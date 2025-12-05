from pydantic import Field
from app.models.base import BaseRequest


class ValidateCypherRequest(BaseRequest):
    """Requête de validation Cypher"""

    cypher: str = Field(
        ...,
        min_length=5,
        max_length=10000,
        description="Requête Cypher à valider"
    )
    check_read_only: bool = Field(
        default=True,
        description="Vérifier si la requête est en lecture seule"
    )
    check_syntax: bool = Field(
        default=True,
        description="Vérifier la syntaxe"
    )
    check_performance: bool = Field(
        default=False,
        description="Analyser les performances potentielles"
    )
    suggest_improvements: bool = Field(
        default=False,
        description="Suggérer des améliorations"
    )