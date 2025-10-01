from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymilvus import connections, Collection
from openai import AsyncOpenAI
import os
import json

# --- Configuration (Mirrors embedding_activities.py) ---
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MILVUS_HOST = os.getenv("MILVUS_HOST", "milvus-proxy.synapse-system.svc.cluster.local")
MILVUS_PORT = "19530"

# High-Fidelity Model
EMBEDDING_MODEL = "text-embedding-3-large"
EMBEDDING_DIM = 3072

# --- FastAPI Application ---
app = FastAPI(
    title="Semantic Search API",
    description="API for querying vectorized data in the Syzygy Synapse knowledge base.",
)


class SearchRequest(BaseModel):
    query: str
    top_k: int = 10
    sources: list[str] = ["notes", "citations"]  # Default to searching all sources


class SearchResultItem(BaseModel):
    id: str
    score: float
    text_preview: str
    metadata: dict


class SearchResponse(BaseModel):
    results: list[SearchResultItem]


from contextlib import asynccontextmanager


# --- Lifespan Manager for Startup/Shutdown ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage startup and shutdown events."""
    # Startup
    print(f"Connecting to Milvus at {MILVUS_HOST}:{MILVUS_PORT}...")
    try:
        connections.connect(alias="default", host=MILVUS_HOST, port=MILVUS_PORT)
        print("Successfully connected to Milvus.")
    except Exception as e:
        print(f"FATAL: Could not connect to Milvus on startup: {e}")
        # In a real scenario, you might raise an exception to stop the app
        # from starting if the DB connection is critical.

    yield

    # Shutdown
    print("Disconnecting from Milvus...")
    connections.disconnect(alias="default")
    print("Disconnected from Milvus.")


# --- FastAPI Application ---
app = FastAPI(
    title="Semantic Search API",
    description="API for querying vectorized data in the Syzygy Synapse knowledge base.",
    lifespan=lifespan,
)


@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """
    Performs a semantic search across specified data sources.
    """
    try:
        # 1. Generate query vector
        response = await client.embeddings.create(
            model=EMBEDDING_MODEL, input=[request.query], dimensions=EMBEDDING_DIM
        )
        query_vector = response.data[0].embedding
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate query embedding: {e}"
        )

    all_hits = []

    # 2. Search each requested source collection
    for source in request.sources:
        collection_name = f"synapse_{source}"
        try:
            if not connections.has_connection("default"):
                connections.connect(alias="default", host=MILVUS_HOST, port=MILVUS_PORT)

            collection = Collection(collection_name)
            collection.load()  # Ensure collection is loaded for searching

            search_params = {"metric_type": "IP", "params": {"nprobe": 128}}

            hits = collection.search(
                data=[query_vector],
                anns_field="embedding",
                param=search_params,
                limit=request.top_k,
                output_fields=["id", "text_preview", "metadata"],
            )

            for hit in hits[0]:  # hits[0] corresponds to the first query vector
                all_hits.append(
                    SearchResultItem(
                        id=hit.entity.get("id"),
                        score=hit.distance,
                        text_preview=hit.entity.get("text_preview"),
                        metadata=json.loads(
                            hit.entity.get("metadata")
                        ),  # Metadata is stored as a JSON string
                    )
                )
        except Exception as e:
            # Log the error but continue to the next source
            print(f"Error searching collection '{collection_name}': {e}")
            continue

    # 3. Sort all results by score (higher is better for IP) and return top_k
    all_hits.sort(key=lambda x: x.score, reverse=True)

    return SearchResponse(results=all_hits[: request.top_k])


# Placeholder for running with uvicorn, e.g., `uvicorn main:app --reload`
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
