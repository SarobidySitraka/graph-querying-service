"""
Modèles de réponse de base
Tous les autres response models héritent de ceux-ci
"""
from pydantic import Field
from typing import Optional, List, Dict, Any
from app.models.base import BaseResponse, ErrorDetail


class SuccessResponse(BaseResponse):
    """Réponse de succès simple"""

    success: bool = Field(default=True)
    message: str = Field(..., description="Message de succès")
    data: Optional[Dict[str, Any]] = Field(
        None,
        description="Données additionnelles"
    )


class ErrorResponse(BaseResponse):
    """
    Réponse d'erreur standardisée
    Utilisée par tous les error handlers
    """

    success: bool = Field(default=False)
    error: ErrorDetail = Field(..., description="Détails de l'erreur")
    recovery_suggestions: Optional[List[str]] = Field(
        None,
        description="Suggestions pour résoudre l'erreur"
    )
    related_errors: Optional[List[ErrorDetail]] = Field(
        None,
        description="Erreurs liées ou en cascade"
    )

    @classmethod
    def from_exception(
            cls,
            exception: Exception,
            error_code: str = "INTERNAL_ERROR",
            suggestions: Optional[List[str]] = None
    ) -> "ErrorResponse":
        """
        Créer une ErrorResponse depuis une exception

        Args:
            exception: Exception à convertir
            error_code: Code d'erreur
            suggestions: Suggestions de récupération

        Returns:
            ErrorResponse
        """
        return cls(
            error=ErrorDetail(
                error_code=error_code,
                message=str(exception),
                details={"exception_type": type(exception).__name__}
            ),
            recovery_suggestions=suggestions
        )


class MessageResponse(BaseResponse):
    """Réponse avec un simple message"""

    success: bool = Field(default=True)
    message: str = Field(..., description="Message à afficher")
    level: str = Field(
        default="info",
        pattern="^(info|success|warning|error)$",
        description="Niveau du message"
    )


class StatusResponse(BaseResponse):
    """Réponse de statut"""

    success: bool = Field(default=True)
    status: str = Field(..., description="Statut actuel")
    details: Optional[Dict[str, Any]] = Field(
        None,
        description="Détails du statut"
    )


class EmptyResponse(BaseResponse):
    """Réponse vide (204 No Content)"""

    success: bool = Field(default=True)