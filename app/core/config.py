from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator, computed_field
from typing import List, Optional, Dict, Any, Literal
from functools import lru_cache
from pathlib import Path
import secrets


class Settings(BaseSettings):
    """Configuration centralisée complète de l'application"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        validate_default=True
    )

    # ============================================
    # APPLICATION CORE
    # ============================================
    app_name: str = Field(
        default="graph-querying-service",
        description="Nom de l'application"
    )
    app_version: str = Field(
        default="1.0.0",
        description="Version de l'application"
    )
    app_description: str = Field(
        default="Service de requêtage Neo4j avec GraphRAG",
        description="Description de l'application"
    )
    app_env: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Environnement d'exécution"
    )
    app_debug: bool = Field(
        default=False,
        description="Mode debug"
    )
    app_host: str = Field(
        default="0.0.0.0",
        description="Host de l'application"
    )
    app_port: int = Field(
        default=8000,
        ge=1024,
        le=65535,
        description="Port de l'application"
    )
    app_reload: bool = Field(
        default=False,
        description="Auto-reload en développement"
    )
    app_workers: int = Field(
        default=1,
        ge=1,
        le=32,
        description="Nombre de workers"
    )

    # ============================================
    # LOGGING CONFIGURATION
    # ============================================
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Niveau de log"
    )
    log_format: Literal["json", "text", "color"] = Field(
        default="json",
        description="Format des logs"
    )
    log_file: str = Field(
        default="logs/app.log",
        description="Fichier de log"
    )
    log_rotation: str = Field(
        default="500 MB",
        description="Rotation des logs"
    )
    log_retention: str = Field(
        default="30 days",
        description="Rétention des logs"
    )
    log_console: bool = Field(
        default=True,
        description="Logger dans la console"
    )
    log_file_enabled: bool = Field(
        default=True,
        description="Logger dans un fichier"
    )

    # ============================================
    # NEO4J DATABASE
    # ============================================
    neo4j_uri: str = Field(
        ...,
        description="URI for Neo4j connection"
    )
    neo4j_user: str = Field(
        ...,
        description="Neo4j user"
    )
    neo4j_password: str = Field(
        ...,
        description="Neo4j password"
    )
    neo4j_database: str = Field(
        default="neo4j",
        description="Neo4j database name"
    )
    neo4j_max_connection_lifetime: int = Field(
        default=3600,
        ge=60,
        description="Lifetime max for the connection (seconds)"
    )
    neo4j_max_connection_pool_size: int = Field(
        default=50,
        ge=1,
        le=1000,
        description="Pool size connection max"
    )
    neo4j_connection_timeout: int = Field(
        default=30,
        ge=1,
        description="Connection timeout (seconds)"
    )
    neo4j_connection_acquisition_timeout: int = Field(
        default=60,
        ge=1,
        description="Connection acquisition timeout (seconds)"
    )
    neo4j_encrypted: bool = Field(
        default=False,
        description="Use SSL/TLS"
    )
    neo4j_trust: Literal["TRUST_ALL_CERTIFICATES", "TRUST_SYSTEM_CA_SIGNED_CERTIFICATES"] = Field(
        default="TRUST_ALL_CERTIFICATES",
        description="Trust policy SSL"
    )

    # ============================================
    # LLM CONFIGURATION (OpenAI)
    # ============================================
    openai_api_key: str = Field(
        ...,
        description="OpenAI API key"
    )
    openai_organization: Optional[str] = Field(
        default=None,
        description="OpenAI Organisation"
    )
    llm_model: str = Field(
        default="gpt-5-mini",
        description="LLM model to use"
    )
    llm_temperature: float = Field(
        default=0.0,
        ge=0.0,
        le=2.0,
        description="LLM temperature"
    )
    llm_max_tokens: int = Field(
        default=2000,
        ge=100,
        le=32000,
        description="Tokens number max"
    )
    llm_top_p: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Top P sampling"
    )
    llm_frequency_penalty: float = Field(
        default=0.0,
        ge=-2.0,
        le=2.0,
        description="Frequency penality"
    )
    llm_presence_penalty: float = Field(
        default=0.0,
        ge=-2.0,
        le=2.0,
        description="Attendance penalty"
    )
    llm_timeout: int = Field(
        default=60,
        ge=10,
        description="LLM request timeout (seconds)"
    )
    llm_max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Retries number max"
    )

    # ============================================
    # REDIS CACHE
    # ============================================
    redis_enabled: bool = Field(
        default=False,
        description="Activate Redis"
    )
    redis_host: str = Field(
        default="localhost",
        description="Redis Host"
    )
    redis_port: int = Field(
        default=6379,
        ge=1,
        le=65535,
        description="Redis Port"
    )
    redis_db: int = Field(
        default=0,
        ge=0,
        le=15,
        description="Redis Database"
    )
    redis_password: Optional[str] = Field(
        default=None,
        description="Redis password"
    )
    redis_ssl: bool = Field(
        default=False,
        description="Use SSL for Redis"
    )
    redis_max_connections: int = Field(
        default=50,
        ge=1,
        description="Redis connection max number"
    )
    cache_ttl: int = Field(
        default=3600,
        ge=60,
        description="Durée de vie du cache (secondes)"
    )
    cache_prefix: str = Field(
        default="graphrag:",
        description="Préfixe des clés cache"
    )

    # ============================================
    # SECURITY
    # ============================================
    secret_key: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        description="Clé secrète pour JWT"
    )
    algorithm: str = Field(
        default="HS256",
        description="Algorithme de signature JWT"
    )
    access_token_expire_minutes: int = Field(
        default=30,
        ge=1,
        description="Durée de validité des tokens (minutes)"
    )
    refresh_token_expire_days: int = Field(
        default=7,
        ge=1,
        description="Durée de validité des refresh tokens (jours)"
    )

    # API Keys
    api_key_enabled: bool = Field(
        default=True,
        description="Activer l'authentification par API Key"
    )
    api_keys: List[str] = Field(
        default_factory=list,
        description="Liste des API Keys autorisées"
    )
    api_key_header: str = Field(
        default="X-API-Key",
        description="Nom du header pour l'API Key"
    )

    # Password Policy
    password_min_length: int = Field(
        default=8,
        ge=6,
        description="Longueur minimale du mot de passe"
    )
    password_require_uppercase: bool = Field(
        default=True,
        description="Exiger une majuscule"
    )
    password_require_lowercase: bool = Field(
        default=True,
        description="Exiger une minuscule"
    )
    password_require_digit: bool = Field(
        default=True,
        description="Exiger un chiffre"
    )
    password_require_special: bool = Field(
        default=True,
        description="Exiger un caractère spécial"
    )

    # ============================================
    # CORS
    # ============================================
    cors_enabled: bool = Field(
        default=True,
        description="Activer CORS"
    )
    cors_origins: List[str] = Field(
        default_factory=lambda: ["*"],
        description="Origines autorisées"
    )
    cors_allow_credentials: bool = Field(
        default=True,
        description="Autoriser les credentials"
    )
    cors_allow_methods: List[str] = Field(
        default_factory=lambda: ["*"],
        description="Méthodes HTTP autorisées"
    )
    cors_allow_headers: List[str] = Field(
        default_factory=lambda: ["*"],
        description="Headers autorisés"
    )
    cors_expose_headers: List[str] = Field(
        default_factory=list,
        description="Headers exposés"
    )
    cors_max_age: int = Field(
        default=600,
        ge=0,
        description="Durée de cache des préflight (secondes)"
    )

    # ============================================
    # RATE LIMITING
    # ============================================
    rate_limit_enabled: bool = Field(
        default=True,
        description="Activer le rate limiting"
    )
    rate_limit_calls: int = Field(
        default=100,
        ge=1,
        description="Nombre de requêtes autorisées"
    )
    rate_limit_period: int = Field(
        default=60,
        ge=1,
        description="Période de temps (secondes)"
    )
    rate_limit_storage_url: Optional[str] = Field(
        default=None,
        description="URL de stockage pour rate limiting (Redis)"
    )

    # ============================================
    # QUERY CONFIGURATION
    # ============================================
    max_query_results: int = Field(
        default=1000,
        ge=1,
        le=10000,
        description="Nombre maximum de résultats"
    )
    default_query_limit: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="Limite par défaut"
    )
    query_timeout: int = Field(
        default=30,
        ge=1,
        le=300,
        description="Timeout des requêtes (secondes)"
    )
    enable_query_validation: bool = Field(
        default=True,
        description="Activer la validation des requêtes"
    )
    enable_read_only_mode: bool = Field(
        default=True,
        description="Mode lecture seule (bloquer les writes)"
    )
    allowed_cypher_keywords: List[str] = Field(
        default_factory=lambda: ["MATCH", "RETURN", "WHERE", "WITH", "LIMIT", "SKIP",
                                 "ORDER BY", "UNION", "UNWIND", "CASE", "CALL"],
        description="Mots-clés Cypher autorisés"
    )
    blocked_cypher_keywords: List[str] = Field(
        default_factory=lambda: ["CREATE", "DELETE", "REMOVE", "SET", "MERGE",
                                 "DROP", "ALTER", "DETACH"],
        description="Mots-clés Cypher bloqués"
    )

    # ============================================
    # GRAPHRAG CONFIGURATION
    # ============================================
    graphrag_enabled: bool = Field(
        default=True,
        description="Activer GraphRAG"
    )
    graphrag_use_schema_context: bool = Field(
        default=True,
        description="Utiliser le contexte du schéma"
    )
    graphrag_max_context_length: int = Field(
        default=4000,
        ge=1000,
        le=32000,
        description="Longueur max du contexte"
    )
    graphrag_include_examples: bool = Field(
        default=True,
        description="Inclure des exemples dans les prompts"
    )
    graphrag_max_schema_items: int = Field(
        default=50,
        ge=10,
        le=200,
        description="Nombre max d'éléments de schéma à inclure"
    )
    graphrag_enable_query_optimization: bool = Field(
        default=True,
        description="Activer l'optimisation des requêtes"
    )
    graphrag_enable_response_formatting: bool = Field(
        default=True,
        description="Activer le formatage des réponses"
    )
    graphrag_cache_prompts: bool = Field(
        default=True,
        description="Mettre en cache les prompts générés"
    )

    # ============================================
    # MONITORING & METRICS
    # ============================================
    enable_metrics: bool = Field(
        default=True,
        description="Activer les métriques"
    )
    metrics_port: int = Field(
        default=9090,
        ge=1024,
        le=65535,
        description="Port pour les métriques Prometheus"
    )
    enable_tracing: bool = Field(
        default=False,
        description="Activer le tracing"
    )
    tracing_endpoint: Optional[str] = Field(
        default=None,
        description="Endpoint pour le tracing"
    )
    enable_profiling: bool = Field(
        default=False,
        description="Activer le profiling"
    )

    # ============================================
    # HEALTH CHECK
    # ============================================
    health_check_interval: int = Field(
        default=30,
        ge=10,
        description="Intervalle des health checks (secondes)"
    )
    health_check_timeout: int = Field(
        default=10,
        ge=1,
        description="Timeout des health checks (secondes)"
    )

    # ============================================
    # BACKUP & RECOVERY
    # ============================================
    backup_enabled: bool = Field(
        default=False,
        description="Activer les backups automatiques"
    )
    backup_path: Path = Field(
        default=Path("backups"),
        description="Répertoire des backups"
    )
    backup_retention_days: int = Field(
        default=7,
        ge=1,
        description="Durée de rétention des backups (jours)"
    )

    # ============================================
    # VALIDATORS
    # ============================================
    @field_validator("api_keys", mode="before")
    @classmethod
    def parse_api_keys(cls, v):
        """Parser les API keys depuis différents formats"""
        if isinstance(v, str):
            import json
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [k.strip() for k in v.split(",") if k.strip()]
        return v or []

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parser les origines CORS"""
        if isinstance(v, str):
            import json
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [o.strip() for o in v.split(",") if o.strip()]
        return v or ["*"]

    @field_validator("log_file", mode="before")
    @classmethod
    def ensure_log_directory(cls, v):
        """Créer le répertoire de logs si nécessaire"""
        log_path = Path(v)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        return str(log_path)

    # ============================================
    # COMPUTED PROPERTIES
    # ============================================
    @computed_field
    @property
    def is_production(self) -> bool:
        """Vérifier si en production"""
        return self.app_env == "production"

    @computed_field
    @property
    def is_development(self) -> bool:
        """Vérifier si en développement"""
        return self.app_env == "development"

    @computed_field
    @property
    def is_staging(self) -> bool:
        """Vérifier si en staging"""
        return self.app_env == "staging"

    @computed_field
    @property
    def database_url(self) -> str:
        """URL complète de la base de données"""
        return f"{self.neo4j_uri}/{self.neo4j_database}"

    @computed_field
    @property
    def redis_url(self) -> Optional[str]:
        """URL Redis complète"""
        if not self.redis_enabled:
            return None

        auth = f":{self.redis_password}@" if self.redis_password else ""
        protocol = "rediss" if self.redis_ssl else "redis"
        return f"{protocol}://{auth}{self.redis_host}:{self.redis_port}/{self.redis_db}"

    def get_config_dict(self) -> Dict[str, Any]:
        """Obtenir la configuration en dictionnaire (sans secrets)"""
        config = self.model_dump()

        # Masquer les secrets
        sensitive_fields = [
            "neo4j_password", "openai_api_key", "secret_key",
            "redis_password", "api_keys"
        ]

        for field in sensitive_fields:
            if field in config:
                config[field] = "***HIDDEN***"

        return config


@lru_cache()
def get_settings() -> Settings:
    """Récupérer les settings (cached)"""
    return Settings()


# Instance globale
settings = get_settings()