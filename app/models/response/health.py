from pydantic import Field, ConfigDict
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.models.base import BaseResponse
from app.models.enums import ServiceStatus


class ComponentHealth(BaseResponse):
    """Santé d'un composant"""
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        }
    )

    status: ServiceStatus = Field(..., description="Statut du composant")
    message: Optional[str] = Field(None, description="Message de statut")
    latency_ms: Optional[float] = Field(None, description="Latence en ms")
    details: Dict[str, Any] = Field(
        default_factory=dict,
        description="Détails supplémentaires"
    )


class HealthResponse(BaseResponse):
    """Réponse de santé globale"""
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        }
    )

    status: ServiceStatus = Field(..., description="Statut global")
    version: str = Field(..., description="Version de l'application")
    environment: str = Field(..., description="Environnement")
    uptime_seconds: Optional[float] = Field(..., description="Uptime en secondes")
    components: Dict[str, ComponentHealth] = Field(
        ...,
        description="Statut des composants"
    )


class SchemaResponse(BaseResponse):
    """Réponse du schéma Neo4j"""

    node_labels: List[str] = Field(
        default_factory=list,
        description="Labels de nœuds"
    )
    relationship_types: List[str] = Field(
        default_factory=list,
        description="Types de relations"
    )
    property_keys: List[str] = Field(
        default_factory=list,
        description="Clés de propriétés"
    )
    constraints: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Contraintes"
    )
    indexes: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Index"
    )
    statistics: Dict[str, Any] = Field(
        default_factory=dict,
        description="Statistiques de la base"
    )


class MetricsResponse(BaseResponse):
    """Réponse des métriques"""

    total_queries: int = Field(..., description="Nombre total de requêtes")
    successful_queries: int = Field(..., description="Requêtes réussies")
    failed_queries: int = Field(..., description="Requêtes échouées")
    average_execution_time_ms: float = Field(
        ...,
        description="Temps moyen d'exécution"
    )
    cache_hit_rate: float = Field(..., description="Taux de hit du cache")
    uptime_seconds: float = Field(..., description="Uptime")