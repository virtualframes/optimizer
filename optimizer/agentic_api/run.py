from __future__ import annotations
import uvicorn
from fastapi import FastAPI
from optimizer.agentic_api.router import router as agentic

def main():
    app = FastAPI(title="Jules Agentic API")
    app.include_router(agentic)
    uvicorn.run(app, host="0.0.0.0", port=8080)