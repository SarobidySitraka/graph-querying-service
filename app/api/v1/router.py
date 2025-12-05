from fastapi import APIRouter
from app.api.v1.endpoints import health, cypher, natural, schema

api_router = APIRouter()

api_router.include_router(health.router, prefix="", tags=["Health"])
api_router.include_router(cypher.router, prefix="/query", tags=["Cypher"])
api_router.include_router(natural.router, prefix="/query", tags=["Natural"])
api_router.include_router(schema.router, prefix="", tags=["Schema"])