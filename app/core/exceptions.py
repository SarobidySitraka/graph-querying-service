from fastapi import HTTPException, status
from typing import Any, Optional, Dict


class BaseAPIException(HTTPException):
    """
    Exception de base pour l'API

    Toutes les exceptions custom doivent hériter de celle-ci
    """

    def __init__(
            self,
            status_code: int,
            detail: str,
            headers: Optional[Dict[str, str]] = None,
            error_code: Optional[str] = None,
            extra: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code or self.__class__.__name__
        self.extra = extra or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convertir l'exception en dictionnaire"""
        return {
            "error_code": self.error_code,
            "message": self.detail,
            "status_code": self.status_code,
            "extra": self.extra
        }


# ============================================
# DATABASE EXCEPTIONS
# ============================================

class DatabaseError(BaseAPIException):
    """Erreur de base de données"""

    def __init__(self, detail: str = "Erreur de base de données", **kwargs):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code="DATABASE_ERROR",
            **kwargs
        )


class Neo4jConnectionError(DatabaseError):
    """Erreur de connexion Neo4j"""

    def __init__(self, detail: str = "Impossible de se connecter à Neo4j", **kwargs):
        super().__init__(detail=detail, **kwargs)
        self.error_code = "NEO4J_CONNECTION_ERROR"


class Neo4jQueryError(DatabaseError):
    """Erreur lors d'une requête Neo4j"""

    def __init__(self, detail: str = "Erreur lors de l'exécution de la requête Neo4j", **kwargs):
        super().__init__(detail=detail, **kwargs)
        self.error_code = "NEO4J_QUERY_ERROR"


class DatabaseTimeoutError(DatabaseError):
    """Timeout de base de données"""

    def __init__(self, detail: str = "Timeout de la base de données", **kwargs):
        super().__init__(detail=detail, **kwargs)
        self.error_code = "DATABASE_TIMEOUT"


# ============================================
# QUERY EXCEPTIONS
# ============================================

class QueryError(BaseAPIException):
    """Erreur de requête"""

    def __init__(self, detail: str = "Erreur de requête", **kwargs):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code="QUERY_ERROR",
            **kwargs
        )


class InvalidCypherQueryError(QueryError):
    """Requête Cypher invalide"""

    def __init__(self, detail: str = "Requête Cypher invalide", **kwargs):
        super().__init__(detail=detail, **kwargs)
        self.error_code = "INVALID_CYPHER_QUERY"


class CypherSyntaxError(InvalidCypherQueryError):
    """Erreur de syntaxe Cypher"""

    def __init__(self, detail: str = "Erreur de syntaxe dans la requête Cypher", **kwargs):
        super().__init__(detail=detail, **kwargs)
        self.error_code = "CYPHER_SYNTAX_ERROR"


class QueryExecutionError(BaseAPIException):
    """Erreur lors de l'exécution de la requête"""

    def __init__(self, detail: str = "Erreur lors de l'exécution de la requête", **kwargs):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code="QUERY_EXECUTION_ERROR",
            **kwargs
        )


class QueryTimeoutError(BaseAPIException):
    """Timeout de requête"""

    def __init__(self, detail: str = "La requête a expiré", **kwargs):
        super().__init__(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            detail=detail,
            error_code="QUERY_TIMEOUT",
            **kwargs
        )


class ForbiddenQueryError(BaseAPIException):
    """Requête interdite"""

    def __init__(self, detail: str = "Type de requête non autorisé", **kwargs):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code="FORBIDDEN_QUERY",
            **kwargs
        )


class QueryResultTooLargeError(BaseAPIException):
    """Résultat de requête trop grand"""

    def __init__(self, detail: str = "Le résultat de la requête est trop grand", **kwargs):
        super().__init__(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=detail,
            error_code="QUERY_RESULT_TOO_LARGE",
            **kwargs
        )


# ============================================
# LLM EXCEPTIONS
# ============================================

class LLMError(BaseAPIException):
    """Erreur du service LLM"""

    def __init__(self, detail: str = "Erreur du service LLM", **kwargs):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
            error_code="LLM_ERROR",
            **kwargs
        )


class LLMServiceError(LLMError):
    """Erreur de service LLM"""

    def __init__(self, detail: str = "Le service LLM est indisponible", **kwargs):
        super().__init__(detail=detail, **kwargs)
        self.error_code = "LLM_SERVICE_ERROR"


class LLMTimeoutError(LLMError):
    """Timeout LLM"""

    def __init__(self, detail: str = "Timeout du service LLM", **kwargs):
        super().__init__(detail=detail, **kwargs)
        self.error_code = "LLM_TIMEOUT"


class LLMRateLimitError(LLMError):
    """Rate limit LLM dépassé"""

    def __init__(self, detail: str = "Limite de taux LLM dépassée", **kwargs):
        super().__init__(detail=detail, **kwargs)
        self.error_code = "LLM_RATE_LIMIT"


class LLMTokenLimitError(LLMError):
    """Limite de tokens dépassée"""

    def __init__(self, detail: str = "Limite de tokens dépassée", **kwargs):
        super().__init__(detail=detail, **kwargs)
        self.error_code = "LLM_TOKEN_LIMIT"


class InvalidLLMResponseError(LLMError):
    """Réponse LLM invalide"""

    def __init__(self, detail: str = "Réponse du LLM invalide", **kwargs):
        super().__init__(detail=detail, **kwargs)
        self.error_code = "INVALID_LLM_RESPONSE"


# ============================================
# AUTHENTICATION & AUTHORIZATION EXCEPTIONS
# ============================================

class AuthenticationError(BaseAPIException):
    """Erreur d'authentification"""

    def __init__(self, detail: str = "Erreur d'authentification", **kwargs):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
            error_code="AUTHENTICATION_ERROR",
            **kwargs
        )


class UnauthorizedError(AuthenticationError):
    """Non autorisé"""

    def __init__(self, detail: str = "Non autorisé", **kwargs):
        super().__init__(detail=detail, **kwargs)
        self.error_code = "UNAUTHORIZED"


class InvalidCredentialsError(AuthenticationError):
    """Credentials invalides"""

    def __init__(self, detail: str = "Identifiants invalides", **kwargs):
        super().__init__(detail=detail, **kwargs)
        self.error_code = "INVALID_CREDENTIALS"


class TokenExpiredError(AuthenticationError):
    """Token expiré"""

    def __init__(self, detail: str = "Token expiré", **kwargs):
        super().__init__(detail=detail, **kwargs)
        self.error_code = "TOKEN_EXPIRED"


class InvalidTokenError(AuthenticationError):
    """Token invalide"""

    def __init__(self, detail: str = "Token invalide", **kwargs):
        super().__init__(detail=detail, **kwargs)
        self.error_code = "INVALID_TOKEN"


class InvalidAPIKeyError(AuthenticationError):
    """API Key invalide"""

    def __init__(self, detail: str = "API Key invalide ou manquante", **kwargs):
        super().__init__(detail=detail, **kwargs)
        self.error_code = "INVALID_API_KEY"


class ForbiddenError(BaseAPIException):
    """Accès interdit"""

    def __init__(self, detail: str = "Accès interdit", **kwargs):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code="FORBIDDEN",
            **kwargs
        )


class InsufficientPermissionsError(ForbiddenError):
    """Permissions insuffisantes"""

    def __init__(self, detail: str = "Permissions insuffisantes", **kwargs):
        super().__init__(detail=detail, **kwargs)
        self.error_code = "INSUFFICIENT_PERMISSIONS"


# ============================================
# VALIDATION EXCEPTIONS
# ============================================

class ValidationError(BaseAPIException):
    """Erreur de validation"""

    def __init__(self, detail: str = "Erreur de validation", **kwargs):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code="VALIDATION_ERROR",
            **kwargs
        )


class InvalidInputError(ValidationError):
    """Input invalide"""

    def __init__(self, detail: str = "Données d'entrée invalides", **kwargs):
        super().__init__(detail=detail, **kwargs)
        self.error_code = "INVALID_INPUT"


class MissingParameterError(ValidationError):
    """Paramètre manquant"""

    def __init__(self, parameter: str, **kwargs):
        super().__init__(
            detail=f"Paramètre manquant: {parameter}",
            **kwargs
        )
        self.error_code = "MISSING_PARAMETER"


class InvalidParameterError(ValidationError):
    """Paramètre invalide"""

    def __init__(self, parameter: str, reason: str = "", **kwargs):
        detail = f"Paramètre invalide: {parameter}"
        if reason:
            detail += f" - {reason}"
        super().__init__(detail=detail, **kwargs)
        self.error_code = "INVALID_PARAMETER"


# ============================================
# RATE LIMITING EXCEPTIONS
# ============================================

class RateLimitError(BaseAPIException):
    """Erreur de rate limiting"""

    def __init__(self, detail: str = "Limite de taux dépassée", **kwargs):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            error_code="RATE_LIMIT_ERROR",
            **kwargs
        )


class RateLimitExceededError(RateLimitError):
    """Rate limit dépassé"""

    def __init__(self, detail: str = "Trop de requêtes, veuillez réessayer plus tard", **kwargs):
        super().__init__(detail=detail, **kwargs)
        self.error_code = "RATE_LIMIT_EXCEEDED"


# ============================================
# RESOURCE EXCEPTIONS
# ============================================

class ResourceError(BaseAPIException):
    """Erreur de ressource"""

    def __init__(self, detail: str = "Erreur de ressource", **kwargs):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code="RESOURCE_ERROR",
            **kwargs
        )


class ResourceNotFoundError(ResourceError):
    """Ressource non trouvée"""

    def __init__(self, resource: str = "Ressource", **kwargs):
        super().__init__(detail=f"{resource} non trouvée", **kwargs)
        self.error_code = "RESOURCE_NOT_FOUND"


class ResourceAlreadyExistsError(BaseAPIException):
    """Ressource déjà existante"""

    def __init__(self, resource: str = "Ressource", **kwargs):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{resource} existe déjà",
            error_code="RESOURCE_ALREADY_EXISTS",
            **kwargs
        )


# ============================================
# CACHE EXCEPTIONS
# ============================================

class CacheError(BaseAPIException):
    """Erreur de cache"""

    def __init__(self, detail: str = "Erreur de cache", **kwargs):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
            error_code="CACHE_ERROR",
            **kwargs
        )


class CacheConnectionError(CacheError):
    """Erreur de connexion au cache"""

    def __init__(self, detail: str = "Impossible de se connecter au cache", **kwargs):
        super().__init__(detail=detail, **kwargs)
        self.error_code = "CACHE_CONNECTION_ERROR"


# ============================================
# GRAPHRAG EXCEPTIONS
# ============================================

class GraphRAGError(BaseAPIException):
    """Erreur GraphRAG"""

    def __init__(self, detail: str = "Erreur GraphRAG", **kwargs):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code="GRAPHRAG_ERROR",
            **kwargs
        )


class CypherGenerationError(GraphRAGError):
    """Erreur de génération Cypher"""

    def __init__(self, detail: str = "Erreur lors de la génération de la requête Cypher", **kwargs):
        super().__init__(detail=detail, **kwargs)
        self.error_code = "CYPHER_GENERATION_ERROR"


class ResponseFormattingError(GraphRAGError):
    """Erreur de formatage de réponse"""

    def __init__(self, detail: str = "Erreur lors du formatage de la réponse", **kwargs):
        super().__init__(detail=detail, **kwargs)
        self.error_code = "RESPONSE_FORMATTING_ERROR"


class ContextBuildingError(GraphRAGError):
    """Erreur de construction de contexte"""

    def __init__(self, detail: str = "Erreur lors de la construction du contexte", **kwargs):
        super().__init__(detail=detail, **kwargs)
        self.error_code = "CONTEXT_BUILDING_ERROR"


# ============================================
# CONFIGURATION EXCEPTIONS
# ============================================

class ConfigurationError(BaseAPIException):
    """Erreur de configuration"""

    def __init__(self, detail: str = "Erreur de configuration", **kwargs):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code="CONFIGURATION_ERROR",
            **kwargs
        )


class MissingConfigError(ConfigurationError):
    """Configuration manquante"""

    def __init__(self, config_key: str, **kwargs):
        super().__init__(
            detail=f"Configuration manquante: {config_key}",
            **kwargs
        )
        self.error_code = "MISSING_CONFIG"


# ============================================
# SECURITY EXCEPTIONS
# ============================================

class SecurityError(BaseAPIException):
    """Erreur de sécurité"""

    def __init__(self, detail: str = "Erreur de sécurité", **kwargs):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code="SECURITY_ERROR",
            **kwargs
        )


class WeakPasswordError(SecurityError):
    """Mot de passe faible"""

    def __init__(self, requirements: list[str], **kwargs):
        detail = "Mot de passe trop faible. Exigences: " + ", ".join(requirements)
        super().__init__(detail=detail, **kwargs)
        self.error_code = "WEAK_PASSWORD"


class PasswordPolicyError(SecurityError):
    """Erreur de politique de mot de passe"""

    def __init__(self, detail: str = "Le mot de passe ne respecte pas la politique", **kwargs):
        super().__init__(detail=detail, **kwargs)
        self.error_code = "PASSWORD_POLICY_ERROR"


# ============================================
# GENERAL EXCEPTIONS
# ============================================

class InternalServerError(BaseAPIException):
    """Erreur interne du serveur"""

    def __init__(self, detail: str = "Erreur interne du serveur", **kwargs):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code="INTERNAL_SERVER_ERROR",
            **kwargs
        )


class ServiceUnavailableError(BaseAPIException):
    """Service indisponible"""

    def __init__(self, detail: str = "Service temporairement indisponible", **kwargs):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
            error_code="SERVICE_UNAVAILABLE",
            **kwargs
        )


class BadRequestError(BaseAPIException):
    """Requête invalide"""

    def __init__(self, detail: str = "Requête invalide", **kwargs):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code="BAD_REQUEST",
            **kwargs
        )


class NotImplementedError(BaseAPIException):
    """Fonctionnalité non implémentée"""

    def __init__(self, detail: str = "Fonctionnalité non implémentée", **kwargs):
        super().__init__(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=detail,
            error_code="NOT_IMPLEMENTED",
            **kwargs
        )