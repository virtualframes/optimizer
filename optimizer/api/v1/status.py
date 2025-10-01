from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any

router = APIRouter()


class HealthResponse(BaseModel):
    status: str


class StatusResponse(BaseModel):
    status: str
    version: str
    timestamp: str
    services: Dict[str, Any]
    system: Dict[str, float]


@router.get("/health", response_model=HealthResponse, summary="Get API health status")
def get_health():
    """
    Returns the health status of the API.
    """
    return {"status": "healthy"}


@router.get("/status", response_model=StatusResponse, summary="Get detailed API status")
def get_status():
    """
    Returns a detailed status of the API and its services.
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": "2025-10-01T09:37:38Z",
        "services": {
            "neo4j": "connected",
            "redis": "connected",
            "vector_db": "connected",
            "mcp_servers": 3,
        },
        "system": {
            "cpu_usage": 15.2,
            "memory_usage": 45.8,
            "disk_usage": 23.1,
        },
    }