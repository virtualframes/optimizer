from fastapi import FastAPI

app = FastAPI(
    title="Physixiology API Gateway",
    description="Interface for agentic systems and verification.",
    version="0.1.0",
)

@app.get("/health", status_code=200)
async def health_check():
    """
    Endpoint to verify that the API is running.
    """
    return {"status": "healthy"}