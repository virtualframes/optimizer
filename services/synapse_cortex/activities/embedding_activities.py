from temporalio import activity
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility
from openai import AsyncOpenAI
import os
import psycopg2
import json

# Configuration
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MILVUS_HOST = os.getenv("MILVUS_HOST", "milvus-proxy.synapse-system.svc.cluster.local")
DB_CONN_STRING = os.getenv("DB_CONN_STRING")

# High-Fidelity Model
EMBEDDING_MODEL = "text-embedding-3-large"
EMBEDDING_DIM = 3072

@activity.defn
async def generate_embeddings(items: list[dict]) -> list[dict]:
    """Generates embeddings for a list of items."""
    if not items:
        return []

    activity.logger.info(f"Generating embeddings for {len(items)} items using {EMBEDDING_MODEL}.")

    # Extract text for embedding
    texts_to_embed = [item['text'] for item in items]

    response = await client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts_to_embed,
        dimensions=EMBEDDING_DIM
    )

    results = []
    for i, item in enumerate(items):
        new_item = item.copy()
        new_item['embedding'] = response.data[i].embedding
        results.append(new_item)

    return results

@activity.defn
async def index_to_milvus(source: str, embeddings: list[dict]) -> int:
    """Indexes a list of embeddings into the specified Milvus collection."""
    if not embeddings:
        return 0

    activity.logger.info(f"Connecting to Milvus at {MILVUS_HOST} to index {len(embeddings)} embeddings for source '{source}'.")
    connections.connect(alias="default", host=MILVUS_HOST, port="19530")

    collection_name = f"synapse_{source}"

    if not utility.has_collection(collection_name, using="default"):
        _create_collection(collection_name)

    collection = Collection(collection_name, using="default")

    # Prepare data in columnar format for Milvus
    data = [
        [e['id'] for e in embeddings],
        [e['embedding'] for e in embeddings],
        [e['text_preview'] for e in embeddings],
        [json.dumps(e['metadata']) for e in embeddings] # Milvus expects JSON strings
    ]

    activity.logger.info(f"Inserting {len(embeddings)} vectors into '{collection_name}'.")
    collection.insert(data)
    collection.flush()
    activity.logger.info("Flush complete.")

    return len(embeddings)

def _create_collection(name: str):
    """Creates a Milvus collection with a predefined schema."""
    activity.logger.info(f"Collection '{name}' not found. Creating new collection.")
    fields = [
        FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=128),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=EMBEDDING_DIM),
        FieldSchema(name="text_preview", dtype=DataType.VARCHAR, max_length=1024),
        FieldSchema(name="metadata", dtype=DataType.JSON)
    ]
    schema = CollectionSchema(fields, description=f"Collection for {name}")
    collection = Collection(name, schema, using="default")

    index_params = {
        "metric_type": "IP",
        "index_type": "IVF_SQ8",
        "params": {"nlist": 2048}
    }
    collection.create_index("embedding", index_params)
    activity.logger.info(f"Index 'IVF_SQ8' created for collection '{name}'. Loading collection into memory.")
    collection.load()
    return collection

@activity.defn
async def fetch_note_points(since_timestamp: str) -> list[dict]:
    """Fetches note points from the database since the given timestamp."""
    activity.logger.info(f"Fetching note points modified since {since_timestamp}.")
    if not DB_CONN_STRING:
        activity.logger.error("DB_CONN_STRING is not set. Cannot fetch note points.")
        return []

    conn = psycopg2.connect(DB_CONN_STRING)
    results = []
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, content, metadata, updated_at
                FROM psi_control.note_pages
                WHERE updated_at > %s
            """, (since_timestamp,))

            rows = cur.fetchall()
            activity.logger.info(f"Fetched {len(rows)} note points from the database.")

            for row_id, content, metadata_json, updated_at in rows:
                results.append({
                    "id": str(row_id),
                    "text": content or "",
                    "text_preview": (content or "")[:512],
                    "metadata": {**(metadata_json or {}), "source": "note_point", "updated_at": updated_at.isoformat()}
                })
    except Exception as e:
        activity.logger.error(f"Database error in fetch_note_points: {e}", exc_info=True)
        raise
    finally:
        conn.close()
    return results

@activity.defn
async def fetch_citations(since_timestamp: str) -> list[dict]:
    """Fetches citations from the database since the given timestamp."""
    activity.logger.info(f"Fetching citations created since {since_timestamp}.")
    if not DB_CONN_STRING:
        activity.logger.error("DB_CONN_STRING is not set. Cannot fetch citations.")
        return []

    conn = psycopg2.connect(DB_CONN_STRING)
    results = []
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, text, context, created_at
                FROM public.citations
                WHERE created_at > %s
            """, (since_timestamp,))

            rows = cur.fetchall()
            activity.logger.info(f"Fetched {len(rows)} citations from the database.")

            for row_id, text, context, created_at in rows:
                results.append({
                    "id": f"citation-{row_id}",
                    "text": text or "",
                    "text_preview": (text or "")[:512],
                    "metadata": {**(context or {}), "source": "citation", "created_at": created_at.isoformat()}
                })
    except Exception as e:
        activity.logger.error(f"Database error in fetch_citations: {e}", exc_info=True)
        raise
    finally:
        conn.close()
    return results