from fastapi import APIRouter, Depends, Request
from app.models.request.natural import NaturalQueryRequest
from app.models.response.query import QueryResponse
from app.models.base import QueryMetadata
from app.models.enums import QueryType
from app.graphrag.engine import graphrag_engine
from app.api.dependencies import get_api_key
from app.core.logging import get_logger
from app.middleware.rate_limit import limiter

router = APIRouter()
logger = get_logger(__name__)


@router.post("/natural", response_model=QueryResponse, tags=["Query"])
@limiter.limit("30/minute")
async def execute_natural_query(
        request: Request,
        query_request: NaturalQueryRequest,
        api_key: str = Depends(get_api_key)
):
    """Exécuter une requête en langage naturel"""

    try:
        cypher, results, execution_time, answer = graphrag_engine.process_natural_query(
            query_request.question,
            query_request.context,
            query_request.use_cache
        )

        return QueryResponse(
            success=True,
            data=results,
            metadata=QueryMetadata(
                query_type=QueryType.NATURAL,
                execution_time_ms=execution_time,
                result_count=len(results),
                generated_cypher=cypher if query_request.return_cypher else None,
                used_cache=False  # TODO: déterminer depuis le cache
            ),
            answer=answer
        )

    except Exception as e:
        logger.error(f"Erreur lors de la requête naturelle: {e}")
        raise