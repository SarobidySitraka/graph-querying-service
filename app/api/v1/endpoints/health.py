from fastapi import APIRouter
from app.models.response.health import HealthResponse, ComponentHealth
from app.models.enums import ServiceStatus
from app.services.neo4j_service import neo4j_service
from app.services.llm_service import llm_service
from app.services.cache_service import cache_service
from app.core.config import settings
import time

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Vérifier la santé du service"""

    components = {}

    # Neo4j
    start = time.time()
    neo4j_healthy = neo4j_service.health_check()
    neo4j_latency = (time.time() - start) * 1000

    components["neo4j"] = ComponentHealth(
        success=True,
        status=ServiceStatus.HEALTHY if neo4j_healthy else ServiceStatus.UNAVAILABLE,
        message="Connecté" if neo4j_healthy else "Déconnecté",
        latency_ms=neo4j_latency
    )

    # LLM
    start = time.time()
    llm_healthy = llm_service.health_check()
    llm_latency = (time.time() - start) * 1000

    components["llm"] = ComponentHealth(
        success=True,
        status=ServiceStatus.HEALTHY if llm_healthy else ServiceStatus.UNAVAILABLE,
        message="Disponible" if llm_healthy else "Indisponible",
    latency_ms = llm_latency
    )

    # Cache
    cache_healthy = cache_service.health_check()

    components["cache"] = ComponentHealth(
        success=True,
        status=ServiceStatus.HEALTHY if cache_healthy else ServiceStatus.DEGRADED,
        message="Activé" if cache_service.enabled else "Désactivé"
    )

    # Statut global
    if neo4j_healthy and llm_healthy:
        global_status = ServiceStatus.HEALTHY
    elif neo4j_healthy or llm_healthy:
        global_status = ServiceStatus.DEGRADED
    else:
        global_status = ServiceStatus.UNAVAILABLE

    return HealthResponse(
        success=True,
        status=global_status,
        version=settings.app_version,
        components=components,
        environment=settings.app_env,
        uptime_seconds=time.time() - start
    )