"""FastAPI application setup."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from optimizer.api.routes import ingest, query
from optimizer.config import get_settings, setup_logging
from optimizer import __version__


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    
    # Setup logging
    setup_logging(
        level=settings.logging.level,
        format_type=settings.logging.format,
        output_file=settings.logging.output_file
    )
    
    app = FastAPI(
        title="Optimizer API",
        description="Virtual node and game engine authentication matrix simulation API",
        version=__version__,
        debug=settings.debug,
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(ingest.router, prefix="/api/v1/ingest", tags=["ingest"])
    app.include_router(query.router, prefix="/api/v1/query", tags=["query"])
    
    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "name": settings.app_name,
            "version": __version__,
            "status": "running"
        }
    
    @app.get("/health")
    async def health():
        """Health check endpoint."""
        return {"status": "healthy"}
    
    return app
