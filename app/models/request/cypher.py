from pydantic import Field, field_validator
from typing import Optional, Dict, Any, List
from app.models.base import BaseRequest


class CypherQueryRequest(BaseRequest):
    """Requête Cypher directe"""

    cypher: str = Field(
        ...,
        min_length=5,
        max_length=10000,
        description="Requête Cypher à exécuter",
        examples=["MATCH (n:EXPORTER) RETURN n.EXPORTER_NAME LIMIT 10"]
    )
    parameters: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Paramètres de la requête Cypher"
    )
    timeout: Optional[int] = Field(
        default=None,
        ge=1,
        le=300,
        description="Timeout en secondes"
    )
    explain: bool = Field(
        default=False,
        description="Retourner le plan d'exécution"
    )
    profile: bool = Field(
        default=False,
        description="Profiler la requête"
    )

    @field_validator("cypher")
    @classmethod
    def validate_cypher(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("La requête Cypher ne peut pas être vide")
        return v

    @field_validator("parameters")
    @classmethod
    def validate_parameters(cls, v: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if v is not None and not isinstance(v, dict):
            raise ValueError("Les paramètres doivent être un dictionnaire")
        return v


class BatchCypherRequest(BaseRequest):
    """Requêtes Cypher en batch"""

    queries: List[CypherQueryRequest] = Field(
        ...,
        min_length=1,
        max_length=10,
        description="Liste de requêtes à exécuter"
    )
    stop_on_error: bool = Field(
        default=True,
        description="Arrêter si une requête échoue"
    )