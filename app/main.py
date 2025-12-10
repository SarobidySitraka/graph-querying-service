from fastapi import FastAPI
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.database.neo4j import neo4j_connection
from app.api.v1.router import api_router

# Middlewares
from app.middleware.cors import setup_cors
from app.middleware.error_handler import setup_error_handlers
from app.middleware.request_logger import setup_request_logging
from app.middleware.rate_limit import setup_rate_limiting
from app.middleware.auth import setup_auth

# Setup logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    """Application life cycle management"""
    # Startup
    logger.info("=" * 60)
    logger.info(f"Start of {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.app_env}")
    logger.info("=" * 60)

    try:
        # Neo4j Connection
        logger.info("Connection to Neo4j...")
        neo4j_connection.connect()
        logger.info("Neo4j connected")

        # Verify schema
        from app.services.neo4j_service import neo4j_service
        schema = neo4j_service.get_schema()
        logger.info(f"Loaded schema: {len(schema.get('node_labels', []))} labels, "
                    f"{len(schema.get('relationship_types', []))} relations")

        # Base information
        info = neo4j_service.get_database_info()
        logger.info(f"Database: {info.get('node_count', 0)} nodes, "
                    f"{info.get('relationship_count', 0)} relationships")

        logger.info("=" * 60)
        logger.info("Application is starting up successfully !")
        logger.info(f"Documentation: http://{settings.app_host}:{settings.app_port}/docs")
        logger.info("=" * 60)

    except Exception as e:
        logger.critical(f"Critical error on startup: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down...")
    try:
        neo4j_connection.close()
        logger.info("Neo4j is unconnected")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

    logger.info("Application stopped")


# Initialize app before using it
app = FastAPI(
    title="graph-querying-service",
    description="Neo4j graph querying service with GraphRAG",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)


app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)
setup_cors(app)
setup_error_handlers(app)
setup_request_logging(app)
setup_rate_limiting(app)
setup_auth(app)

app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["Root"])
async def root():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": settings.app_description,
        "status": "running",
        "environment": settings.app_env,
        "docs": "/docs",
        "health": "/api/v1/health"
    }


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Favicon"""
    return JSONResponse(content={}, status_code=204)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_reload,
        log_level=settings.log_level.lower()
    )