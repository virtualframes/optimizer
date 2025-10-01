# services/semantic-search-api/main.py
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from openai import AsyncOpenAI
from pydantic import BaseModel
from pymilvus import Collection, connections
from temporalio.client import Client

from services.synapse_cortex.activities import send_prompt_to_jules

# Use an async client for a FastAPI app
client = AsyncOpenAI()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Connect to Milvus on startup
    connections.connect(
        "default",
        host=os.getenv("MILVUS_HOST", "milvus.synapse-system.svc.cluster.local"),
        port=os.getenv("MILVUS_PORT", "19530"),
    )
    print("Connected to Milvus.")
    yield
    # Disconnect from Milvus on shutdown
    connections.disconnect("default")
    print("Disconnected from Milvus.")


app = FastAPI(title="Synapse Semantic Search API", lifespan=lifespan)


class SearchRequest(BaseModel):
    query: str
    sources: list[str] = ["notes", "citations", "audit"]
    limit: int = 10


class SearchResult(BaseModel):
    id: str
    text: str
    score: float
    metadata: dict


@app.post("/search", response_model=list[SearchResult])
async def semantic_search(req: SearchRequest):
    # 1. Generate query embedding
    response = await client.embeddings.create(
        model="text-embedding-3-small", input=req.query, dimensions=1536
    )
    query_vector = response.data[0].embedding

    # 2. Search each source collection in Milvus
    results = []
    for source in req.sources:
        collection_name = f"synapse_{source}"
        if Collection.exists(collection_name):
            collection = Collection(collection_name)
            collection.load()

            search_results = collection.search(
                data=[query_vector],
                anns_field="embedding",
                param={"metric_type": "IP", "params": {"nprobe": 16}},
                limit=req.limit,
                output_fields=["text", "timestamp"],
            )

            for hit in search_results[0]:
                results.append(
                    SearchResult(
                        id=hit.id,
                        text=hit.entity.get("text"),
                        score=hit.score,
                        metadata={
                            "source": source,
                            "ts": hit.entity.get("timestamp"),
                        },
                    )
                )

    # 3. Sort results by score and return the top N
    results.sort(key=lambda x: x.score, reverse=True)
    return results[: req.limit]


@app.get("/health")
async def health():
    # Basic health check to confirm the API is running.
    # A more robust check could verify the connection to Milvus.
    return {"status": "ok"}


class PromptPayload(BaseModel):
    taskid: str
    context: str
    instructions: str


@app.post("/receive")
async def receive_prompt(payload: PromptPayload):
    """
    Receives a prompt, dispatches it to a Jules agent via Temporal,
    and returns a confirmation.
    """
    try:
        # 1. Connect to Temporal
        temporal_client = await Client.connect(
            os.getenv("TEMPORAL_HOST", "temporal-frontend.synapse-system.svc.cluster.local:7233")
        )

        # 2. Execute the activity
        result = await temporal_client.execute_activity(
            send_prompt_to_jules,
            payload.dict(),
            task_queue="synapse-cortex-task-queue",
            start_to_close_timeout=60,
        )

        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
