from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any

from optimizer.core.node import Node
from optimizer.core.auth_matrix import AuthMatrix
from optimizer.logging_config import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)

app = FastAPI(
    title="Optimizer API",
    description="API for managing and querying the virtual node simulation.",
    version="0.1.0",
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


@app.on_event("startup")
async def startup_event():
    logger.info("Starting up Optimizer API.")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Optimizer API.")


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


@app.get(
    "/query/node/{node_id}", response_model=NodeModel, summary="Query a specific node"
)
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


# --- Jules Mission Ω Open Protocol Manifest Endpoints ---

# Mock in-memory database for more realistic scaffolding
mock_vault = {
    "fingerprints": {},
    "system_status": "nominal",
    "reroute_depth": 3,
    "context_db": {
        "ctx_001": "Jules is a recursive, self-evolving AI agent.",
        "ctx_002": "The Flaw-First Optimization Engine prioritizes resilience.",
    },
    "lineage_graph": {
        "mut_001": {"parent": "initial_commit", "description": "Initial scaffolding"},
        "mut_002": {"parent": "mut_001", "description": "Added API endpoints"},
    },
    "agent_registry": ["Jules", "Claude", "Gemini"]
}


class FingerprintModel(BaseModel):
    mutation_id: str
    fingerprint: str
    description: str

class EntropyInjectModel(BaseModel):
    target_module: str
    collapse_level: float

class QuorumValidateModel(BaseModel):
    validators: List[str]
    threshold: int

class ContextAugmentModel(BaseModel):
    prompt: str
    context_ids: List[str]

class AgentDispatchModel(BaseModel):
    agent_role: str
    task_description: str


@app.post("/fingerprint", summary="Logs mutation fingerprint")
def log_fingerprint(fingerprint: FingerprintModel):
    """Logs a mutation fingerprint to the system's mock vault."""
    logger.info(f"Received fingerprint for mutation {fingerprint.mutation_id}")
    mock_vault["fingerprints"][fingerprint.mutation_id] = {
        "fingerprint": fingerprint.fingerprint,
        "description": fingerprint.description,
        "timestamp": "2025-10-01T04:00:00Z"
    }
    return {"message": "Fingerprint logged successfully", "data": mock_vault["fingerprints"][fingerprint.mutation_id]}

@app.post("/entropy/inject", summary="Simulates collapse and reroute")
def inject_entropy(entropy: EntropyInjectModel):
    """Injects entropy to simulate a system collapse and test rerouting."""
    logger.info(f"Injecting entropy into {entropy.target_module} at level {entropy.collapse_level}")
    mock_vault["system_status"] = f"degraded (entropy level: {entropy.collapse_level} in {entropy.target_module})"
    return {"message": "Entropy injection successful", "new_status": mock_vault["system_status"]}

@app.post("/quorum/validate", summary="Enforces validator threshold")
def validate_quorum(quorum: QuorumValidateModel):
    """Validates a proposed action against a quorum of validators."""
    is_valid = len(quorum.validators) >= quorum.threshold
    logger.info(f"Validating action with {len(quorum.validators)} validators and threshold {quorum.threshold}. Result: {is_valid}")
    if not is_valid:
        raise HTTPException(status_code=400, detail=f"Quorum not met. Required: {quorum.threshold}, Provided: {len(quorum.validators)}")
    return {"message": "Quorum validation successful", "validated": is_valid}

@app.get("/reroute/depth", summary="Returns fallback depth")
def get_reroute_depth():
    """Returns the current fallback depth of the system."""
    logger.info(f"Querying reroute depth. Current value: {mock_vault['reroute_depth']}")
    return {"reroute_depth": mock_vault["reroute_depth"]}

@app.post("/context/augment", summary="Injects knowledge into prompt")
def augment_context(context: ContextAugmentModel):
    """Augments a given prompt with knowledge from the context engine."""
    logger.info(f"Augmenting prompt with context IDs: {context.context_ids}")
    retrieved_contexts = [mock_vault["context_db"].get(cid, "Context not found.") for cid in context.context_ids]
    context_str = "\\n".join(f"- {ctx}" for ctx in retrieved_contexts)
    augmented_prompt = f"{context.prompt}\\n\\n--- Augmented Context ---\\n{context_str}"
    return {"augmented_prompt": augmented_prompt}

@app.get("/lineage/trace", summary="Returns ancestry of mutation")
def trace_lineage(mutation_id: str):
    """Traces and returns the full ancestry of a given mutation from the mock vault."""
    logger.info(f"Tracing lineage for mutation {mutation_id}")
    if mutation_id not in mock_vault["lineage_graph"]:
        raise HTTPException(status_code=404, detail="Mutation ID not found in lineage graph.")

    ancestry = []
    current_id = mutation_id
    while current_id:
        node = mock_vault["lineage_graph"].get(current_id)
        if not node:
            ancestry.append({"id": current_id, "description": "Branch point or initial commit"})
            break
        ancestry.append({"id": current_id, "description": node["description"]})
        current_id = node.get("parent")

    return {"mutation_id": mutation_id, "ancestry": list(reversed(ancestry))}

@app.post("/agent/dispatch", summary="Role-based agent execution")
def dispatch_agent(dispatch: AgentDispatchModel):
    """Dispatches a task to an agent based on its role."""
    logger.info(f"Dispatching task to agent with role: {dispatch.agent_role}")
    if dispatch.agent_role not in mock_vault["agent_registry"]:
        raise HTTPException(status_code=404, detail=f"Agent role '{dispatch.agent_role}' not found in registry.")

    # Simulate dispatching the task
    return {
        "message": f"Task dispatched to agent role '{dispatch.agent_role}'",
        "task": dispatch.task_description,
        "dispatched_to": dispatch.agent_role,
    }
