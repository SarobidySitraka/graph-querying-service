from pydantic import Field, field_validator
from typing import Optional, List, Dict
from app.models.base import BaseRequest
from app.models.enums import ResponseFormat


class NaturalQueryRequest(BaseRequest):
    """Requête en langage naturel"""

    question: str = Field(
        ...,
        min_length=5,
        max_length=1000,
        description="Question en langage naturel",
        examples=["Quels sont les pays fournisseur de E0000167"]
    )
    context: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Contexte additionnel pour la question"
    )
    return_cypher: bool = Field(
        default=False,
        description="Retourner la requête Cypher générée"
    )
    use_cache: bool = Field(
        default=True,
        description="Utiliser le cache si disponible"
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.TEXT,
        description="Format de la réponse"
    )
    max_results: Optional[int] = Field(
        default=None,
        ge=1,
        le=1000,
        description="Nombre maximum de résultats"
    )
    include_explanation: bool = Field(
        default=False,
        description="Inclure une explication du raisonnement"
    )

    @field_validator("question")
    @classmethod
    def validate_question(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("La question ne peut pas être vide")
        # Supprimer les caractères dangereux
        dangerous_chars = ['<', '>', '{', '}']
        for char in dangerous_chars:
            v = v.replace(char, '')
        return v


class ConversationalQueryRequest(NaturalQueryRequest):
    """Requête conversationnelle avec historique"""

    conversation_id: Optional[str] = Field(
        None,
        description="ID de la conversation"
    )
    history: List[Dict[str, str]] = Field(
        default_factory=list,
        max_length=10,
        description="Historique de la conversation"
    )