from fastapi import APIRouter
from optimizer.api.v1 import status

# Create a new APIRouter for the v1 API
api_router = APIRouter()

# Include the status router
api_router.include_router(status.router, tags=["Status"])