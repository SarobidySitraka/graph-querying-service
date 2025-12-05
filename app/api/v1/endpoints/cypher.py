from fastapi import APIRouter, Depends, Request

from app.models.request.cypher import CypherQueryRequest
from app.models.request.validation import ValidateCypherRequest
from app.models.response.query import QueryResponse, ValidationResponse
from app.models.base import QueryMetadata
from app.models.enums import QueryType
from app.graphrag.engine import graphrag_engine
from app.api.dependencies import get_api_key
from app.core.logging import get_logger
from app.middleware.rate_limit import limiter

router = APIRouter()
logger = get_logger(__name__)


@router.post("/cypher", response_model=QueryResponse, tags=["Query"])
@limiter.limit("50/minute")
async def execute_cypher_query(
        request: Request,
        query_request: CypherQueryRequest,
        api_key: str = Depends(get_api_key)
):
    """Exécuter une requête Cypher directe"""

    try:
        results, execution_time = graphrag_engine.process_cypher_query(
            query_request.cypher,
            query_request.parameters,
            query_request.timeout
        )

        return QueryResponse(
            success=True,
            data=results,
            metadata=QueryMetadata(
                query_type=QueryType.CYPHER,
                execution_time_ms=execution_time,
                result_count=len(results),
                generated_cypher=query_request.cypher,
                used_cache=False
            )
        )

    except Exception as e:
        logger.error(f"Erreur lors de l'exécution Cypher: {e}")
        raise


@router.post("/validate", response_model=ValidationResponse, tags=["Query"])
async def validate_cypher_query(
        validation_request: ValidateCypherRequest,
        api_key: str = Depends(get_api_key)
):
    """Valider une requête Cypher"""

    is_valid, is_read_only, error_msg, warnings = graphrag_engine.validate_query(
        validation_request.cypher,
        validation_request.check_read_only
    )

    return ValidationResponse(
        success=True,
        is_valid=is_valid,
        is_read_only=is_read_only,
        error_message=error_msg,
        warnings=warnings
    )