from fastapi import APIRouter, Depends
from app.models.response.health import SchemaResponse
from app.services.neo4j_service import neo4j_service
from app.api.dependencies import get_api_key
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/schema", response_model=SchemaResponse, tags=["Schema"])
async def get_database_schema(api_key: str = Depends(get_api_key)):
    """Récupérer le schéma de la base de données"""

    schema = neo4j_service.get_schema()

    return SchemaResponse(
        success=True,
        node_labels=schema.get("node_labels", []),
        relationship_types=schema.get("relationship_types", []),
        property_keys=schema.get("property_keys", []),
        constraints=schema.get("constraints", []),
        indexes=schema.get("indexes", [])
    )


@router.get("/info", tags=["Schema"])
async def get_database_info(api_key: str = Depends(get_api_key)):
    """Récupérer les informations de la base"""

    info = neo4j_service.get_database_info()
    return {"success": True, "data": info}