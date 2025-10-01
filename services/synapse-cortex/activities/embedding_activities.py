# services/synapse-cortex/activities/embedding_activities.py
import os
from datetime import datetime

import psycopg2
from openai import OpenAI
from pymilvus import Collection, CollectionSchema, DataType, FieldSchema, connections
from temporalio import activity

# Initialize OpenAI client. It will use the OPENAI_API_KEY environment variable.
client = OpenAI()


def _get_db_connection():
    """Establishes a database connection using credentials from environment variables."""
    try:
        return psycopg2.connect(
            host=os.getenv("DB_HOST", "cockroachdb-public.syzygy.svc.cluster.local"),
            port=os.getenv("DB_PORT", "26257"),
            database=os.getenv("DB_NAME", "synapse"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD"),
        )
    except Exception as e:
        activity.logger.error(f"Failed to connect to the database: {e}")
        raise


def _create_milvus_collection(name: str) -> Collection:
    """Creates a Milvus collection with an optimized schema and index."""
    fields = [
        FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=100),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1536),
        FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=1000),
        FieldSchema(name="timestamp", dtype=DataType.VARCHAR, max_length=50),
    ]
    schema = CollectionSchema(fields, description=f"Synapse {name} vectors")
    collection = Collection(name, schema)

    index_params = {
        "metric_type": "IP",  # Inner Product is good for OpenAI embeddings
        "index_type": "IVF_FLAT",
        "params": {"nlist": 1024},
    }
    collection.create_index("embedding", index_params)
    collection.load()
    activity.logger.info(f"Created Milvus collection: {name}")
    return collection


@activity.defn
async def generate_embeddings(items: list[dict]) -> list[dict]:
    """Batch generate embeddings using OpenAI."""
    activity.logger.info(f"Generating embeddings for {len(items)} items.")
    texts = [item['text'] for item in items]

    response = await client.embeddings.create(
        model="text-embedding-3-small", input=texts, dimensions=1536
    )

    return [
        {
            'id': items[i]['id'],
            'text': items[i]['text'],
            'embedding': response.data[i].embedding,
            'metadata': items[i]['metadata'],
            'timestamp': datetime.utcnow().isoformat(),
        }
        for i in range(len(items))
    ]


@activity.defn
async def index_to_milvus(source: str, embeddings: list[dict]) -> int:
    """Insert embeddings into the appropriate Milvus collection."""
    activity.logger.info(f"Indexing {len(embeddings)} embeddings into source: {source}")
    connections.connect(
        alias="default",
        host=os.getenv("MILVUS_HOST", "milvus.synapse-system.svc.cluster.local"),
        port=os.getenv("MILVUS_PORT", "19530"),
    )

    collection_name = f"synapse_{source}"
    if not Collection.exists(collection_name):
        _create_milvus_collection(collection_name)

    collection = Collection(collection_name)
    ids = [e['id'] for e in embeddings]
    vectors = [e['embedding'] for e in embeddings]
    texts = [e['text'][:500] for e in embeddings]  # Truncate for storage
    timestamps = [e['timestamp'] for e in embeddings]

    collection.insert([ids, vectors, texts, timestamps])
    collection.flush()
    activity.logger.info(f"Successfully indexed {len(embeddings)} embeddings.")
    return len(embeddings)


@activity.defn
async def fetch_note_points(since: str) -> list[dict]:
    """Fetch OneNote pages modified since the given timestamp."""
    activity.logger.info(f"Fetching note points modified since {since}.")
    conn = _get_db_connection()
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT page_id, title, content, metadata
            FROM psi_control.note_pages
            WHERE last_modified > %s
            LIMIT 10000
            """,
            (since,),
        )
        rows = cur.fetchall()
    conn.close()

    activity.logger.info(f"Fetched {len(rows)} note points.")
    return [
        {
            'id': f"note:{row[0]}",
            'text': f"{row[1]}\n\n{row[2][:2000]}",
            'metadata': {'type': 'note', **(row[3] or {})},
        }
        for row in rows
    ]


@activity.defn
async def fetch_citations(since: str) -> list[dict]:
    """Fetch citations added since the given timestamp."""
    activity.logger.info(f"Fetching citations added since {since}.")
    conn = _get_db_connection()
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT ref, title, summary, ts
            FROM citations.entries
            WHERE ts > %s
            LIMIT 5000
            """,
            (since,),
        )
        rows = cur.fetchall()
    conn.close()

    activity.logger.info(f"Fetched {len(rows)} citations.")
    return [
        {
            'id': f"cite:{row[0]}",
            'text': f"{row[1]}\n{row[2]}",
            'metadata': {'type': 'citation', 'url': row[0], 'ts': str(row[3])},
        }
        for row in rows
    ]


@activity.defn
async def fetch_audit_events(since: str) -> list[dict]:
    """Fetch audit events created since the given timestamp."""
    activity.logger.info(f"Fetching audit events created since {since}.")
    conn = _get_db_connection()
    try:
        with conn.cursor() as cur:
            # This is a hypothetical table structure.
            cur.execute(
                """
                SELECT event_id, actor, action, details, created_at
                FROM audit.events
                WHERE created_at > %s
                LIMIT 5000
                """,
                (since,),
            )
            rows = cur.fetchall()
        activity.logger.info(f"Fetched {len(rows)} audit events.")
        return [
            {
                'id': f"audit:{row[0]}",
                'text': f"Actor: {row[1]}, Action: {row[2]}, Details: {row[3]}",
                'metadata': {
                    'type': 'audit',
                    'actor': row[1],
                    'action': row[2],
                    'ts': str(row[4]),
                },
            }
            for row in rows
        ]
    except psycopg2.errors.UndefinedTable:
        activity.logger.warning("audit.events table not found. Skipping audit events.")
        return []
    finally:
        conn.close()


@activity.defn
async def prune_stale_vectors():
    """
    Prune vectors for items that have been deleted from the source systems.

    This is a complex placeholder. A robust implementation would require:
    1. A reliable way to get a list of deleted IDs from each source system
       (e.g., a "tombstone" table, event sourcing).
    2. A mechanism to periodically run this activity and delete the corresponding
       vectors from Milvus using their IDs.
    3. Careful handling of race conditions where an item is deleted and then
       quickly re-created.
    """
    activity.logger.info("Pruning stale vectors (placeholder - not implemented).")
    # Example of what the Milvus deletion logic would look like:
    # collection.delete("id in ['id1', 'id2', ...]")
    pass


@activity.defn
async def publish_metrics(metrics: dict):
    """Publish workflow metrics to a logging system."""
    activity.logger.info(f"Publishing metrics: {metrics}")
    # In a real system, this would send data to Prometheus, Datadog, or another
    # monitoring service.
    pass