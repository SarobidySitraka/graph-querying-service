from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Any, Dict, List, Generic, TypeVar
from datetime import datetime, timezone
from app.models.enums import QueryType

T = TypeVar('T')


class BaseResponse(BaseModel):
    """Modèle de base pour les réponses"""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        json_encoders={
          datetime: lambda v: v.isoformat() if v else None
        },
        json_schema_extra={
            "example": {
                "success": True,
                "timestamp": "2024-01-01T00:00:00Z"
            }
        }
    )

    success: bool = Field(..., description="Indique si la requête a réussi")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp de la réponse"
    )
    request_id: Optional[str] = Field(None, description="ID de la requête")

    def model_dump(self, **kwargs):
        """Override pour gérer la serialization datetime"""
        data = super().model_dump(**kwargs)
        # Convertir datetime en ISO string
        if 'timestamp' in data and isinstance(data['timestamp'], datetime):
            data['timestamp'] = data['timestamp'].isoformat() + 'Z'
        return data

class BaseRequest(BaseModel):
    """Modèle de base pour les requêtes"""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True
    )


class PaginationParams(BaseModel):
    """Paramètres de pagination"""

    skip: int = Field(
        default=0,
        ge=0,
        description="Nombre d'éléments à ignorer"
    )
    limit: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="Nombre max de résultats"
    )

    @property
    def offset(self) -> int:
        """Alias pour skip"""
        return self.skip

    @property
    def slice(self) -> tuple[int, int]:
        """Retourner le slice (start, end)"""
        return self.skip, self.skip + self.limit


class SortParams(BaseModel):
    """Paramètres de tri"""

    sort_by: str = Field(..., description="Champ de tri")
    order: str = Field(
        default="asc",
        pattern="^(asc|desc)$",
        description="Ordre de tri (asc/desc)"
    )


class FilterParams(BaseModel):
    """Paramètres de filtrage"""

    field: str = Field(..., description="Champ à filtrer")
    operator: str = Field(
        ...,
        pattern="^(eq|ne|gt|gte|lt|lte|in|contains)$",
        description="Opérateur de comparaison"
    )
    value: Any = Field(..., description="Valeur de filtrage")


class QueryMetadata(BaseModel):
    """Métadonnées d'une requête"""

    query_type: QueryType = Field(..., description="Type de requête")
    execution_time_ms: float = Field(..., ge=0, description="Temps d'exécution en ms")
    result_count: int = Field(..., ge=0, description="Nombre de résultats")
    generated_cypher: Optional[str] = Field(None, description="Requête Cypher générée")
    used_cache: bool = Field(default=False, description="Si le cache a été utilisé")
    cache_key: Optional[str] = Field(None, description="Clé de cache utilisée")
    llm_tokens_used: Optional[int] = Field(None, description="Tokens LLM utilisés")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def execution_time_sec(self) -> float:
        """Temps d'exécution en secondes"""
        return self.execution_time_ms / 1000


class ErrorDetail(BaseModel):
    """Détails d'une erreur"""
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        }
    )

    error_code: str = Field(..., description="Code d'erreur")
    message: str = Field(..., description="Message d'erreur")
    details: Optional[Dict[str, Any]] = Field(
        None,
        description="Détails supplémentaires"
    )
    timestamp: Optional[str] = Field(default_factory=lambda: str(datetime.now(timezone.utc)))
    traceback: Optional[str] = Field(None, description="Stacktrace (dev seulement)")

    def model_dump(self, **kwargs):
        """Override pour gérer la serialization datetime"""
        data = super().model_dump(**kwargs)
        if 'timestamp' in data and isinstance(data['timestamp'], datetime):
            data['timestamp'] = data['timestamp'].isoformat() + 'Z'
        return data


class PagedResponse(BaseResponse, Generic[T]):
    """Réponse paginée générique"""

    items: List[T] = Field(default_factory=list, description="Éléments de la page")
    total: int = Field(..., ge=0, description="Nombre total d'éléments")
    page: int = Field(..., ge=1, description="Numéro de page")
    page_size: int = Field(..., ge=1, description="Taille de la page")
    total_pages: int = Field(..., ge=0, description="Nombre total de pages")

    @property
    def has_next(self) -> bool:
        """Y a-t-il une page suivante?"""
        return self.page < self.total_pages

    @property
    def has_previous(self) -> bool:
        """Y a-t-il une page précédente?"""
        return self.page > 1