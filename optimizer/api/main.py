from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any

from optimizer.core.node import Node
from optimizer.core.auth_matrix import AuthMatrix
from optimizer.logging_config import setup_logging, get_logger
from optimizer.config.settings import load_config, Settings

logger = get_logger(__name__)

from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager to handle startup and shutdown events.
    """
    # Load configuration and setup logging
    settings = load_config()
    setup_logging(settings)
    app.state.settings = settings
    logger.info("Starting up Optimizer API.")
    yield
    logger.info("Shutting down Optimizer API.")


app = FastAPI(
    title="Optimizer API",
    description="API for managing and querying the virtual node simulation.",
    version="0.1.0",
    lifespan=lifespan,
)

# In-memory storage (for demonstration purposes)
nodes: Dict[str, Node] = {}
auth_matrix = AuthMatrix()


class NodeModel(BaseModel):
    node_id: str
    position: tuple
    metadata: Dict[str, Any] = {}


class CredentialModel(BaseModel):
    source_node_id: str
    target_node_id: str

@app.post("/ingest/node", status_code=201, summary="Ingest a new node")
def ingest_node(node_model: NodeModel):
    """
    Ingests a single node into the simulation.
    """
    if node_model.node_id in nodes:
        raise HTTPException(status_code=409, detail="Node already exists")

    node = Node(
        node_id=node_model.node_id,
        position=node_model.position,
        metadata=node_model.metadata,
    )
    nodes[node.node_id] = node
    logger.info(f"Ingested node: {node.node_id}")
    return {"message": "Node ingested successfully", "node_id": node.node_id}

@app.post("/ingest/credential", status_code=201, summary="Ingest a new credential")
def ingest_credential(credential_model: CredentialModel):
    """
    Ingests a credential, establishing a link in the authentication matrix.
    """
    auth_matrix.add_credential(
        source_node_id=credential_model.source_node_id,
        target_node_id=credential_model.target_node_id,
    )
    return {"message": "Credential ingested successfully"}

@app.get("/query/node/{node_id}", response_model=NodeModel, summary="Query a specific node")
def query_node(node_id: str):
    """
    Retrieves information about a specific node.
    """
    if node_id not in nodes:
        raise HTTPException(status_code=404, detail="Node not found")

    node = nodes[node_id]
    return node.to_dict()

@app.get("/query/auth_matrix", summary="Query the entire authentication matrix")
def query_auth_matrix():
    """
    Retrieves the entire authentication matrix as a dictionary.
    """
    return auth_matrix.to_dict()

@app.get("/", summary="Health check")
def health_check():
    return {"status": "ok"}