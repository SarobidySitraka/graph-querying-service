from pydantic import Field
from typing import Optional, List
from app.models.base import BaseResponse, ErrorDetail


class ErrorResponse(BaseResponse):
    """Réponse d'erreur"""

    success: bool = Field(default=False)
    error: ErrorDetail = Field(..., description="Détails de l'erreur")
    recovery_suggestions: Optional[List[str]] = Field(
        None,
        description="Suggestions de récupération"
    )