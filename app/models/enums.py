from enum import Enum

class QueryType(str, Enum):
    """Type de requête"""
    CYPHER = "cypher"
    NATURAL = "natural"
    HYBRID = "hybrid"


class QueryStatus(str, Enum):
    """Statut de la requête"""
    SUCCESS = "success"
    ERROR = "error"
    PARTIAL = "partial"
    TIMEOUT = "timeout"
    CACHED = "cached"


class ServiceStatus(str, Enum):
    """Statut d'un service"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    STARTING = "starting"
    STOPPING = "stopping"


class LogLevel(str, Enum):
    """Niveaux de log"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class CypherOperation(str, Enum):
    """Types d'opérations Cypher"""
    READ = "read"
    WRITE = "write"
    MIXED = "mixed"
    UNKNOWN = "unknown"


class ErrorCode(str, Enum):
    """Codes d'erreur"""
    VALIDATION_ERROR = "VALIDATION_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    LLM_ERROR = "LLM_ERROR"
    AUTH_ERROR = "AUTH_ERROR"
    RATE_LIMIT_ERROR = "RATE_LIMIT_ERROR"
    NOT_FOUND = "NOT_FOUND"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class CacheStrategy(str, Enum):
    """Stratégies de cache"""
    NONE = "none"
    MEMORY = "memory"
    REDIS = "redis"
    HYBRID = "hybrid"


class ResponseFormat(str, Enum):
    """Formats de réponse"""
    JSON = "json"
    TEXT = "text"
    MARKDOWN = "markdown"
    HTML = "html"