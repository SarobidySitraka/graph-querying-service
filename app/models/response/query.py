from pydantic import Field
from typing import List, Dict, Any, Optional
from app.models.base import BaseResponse, QueryMetadata, PagedResponse
from app.models.enums import QueryStatus


class QueryResponse(BaseResponse):
    """Réponse pour les requêtes"""

    status: QueryStatus = Field(default=QueryStatus.SUCCESS, description="Statut")
    data: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Résultats de la requête"
    )
    metadata: QueryMetadata = Field(..., description="Métadonnées de la requête")
    answer: Optional[str] = Field(
        None,
        description="Réponse en langage naturel (pour requêtes naturelles)"
    )
    explanation: Optional[str] = Field(
        None,
        description="Explication du raisonnement"
    )
    warnings: List[str] = Field(
        default_factory=list,
        description="Avertissements éventuels"
    )


class QueryResponsePaged(PagedResponse[Dict[str, Any]]):
    """Réponse de requête paginée"""

    metadata: QueryMetadata = Field(..., description="Métadonnées")


class ValidationResponse(BaseResponse):
    """Réponse de validation"""

    is_valid: bool = Field(..., description="La requête est-elle valide?")
    is_read_only: bool = Field(..., description="La requête est-elle en lecture seule?")
    error_message: Optional[str] = Field(None, description="Message d'erreur")
    warnings: List[str] = Field(default_factory=list, description="Avertissements")
    suggestions: Optional[List[str]] = Field(None, description="Suggestions")
    estimated_complexity: Optional[str] = Field(
        None,
        description="Complexité estimée (low/medium/high)"
    )
    performance_tips: List[str] = Field(
        default_factory=list,
        description="Conseils de performance"
    )


class BatchQueryResponse(BaseResponse):
    """Réponse pour requêtes batch"""

    results: List[QueryResponse] = Field(
        ...,
        description="Résultats de chaque requête"
    )
    total_execution_time_ms: float = Field(
        ...,
        description="Temps total d'exécution"
    )
    success_count: int = Field(..., description="Nombre de succès")
    error_count: int = Field(..., description="Nombre d'erreurs")