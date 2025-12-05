from typing import Optional, Any
import json
import hashlib
from app.services.base import BaseService
from app.core.config import settings
from .llm_service import  LLMService
from .neo4j_service import Neo4jService

try:
    import redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None


class CacheService(BaseService):
    """Service de cache (Redis)"""

    def __init__(self):
        super().__init__()
        self.enabled = settings.redis_enabled and REDIS_AVAILABLE
        self.ttl = settings.cache_ttl
        self.client = None

        if self.enabled:
            try:
                self.client = redis.Redis(
                    host=settings.redis_host,
                    port=settings.redis_port,
                    db=settings.redis_db,
                    password=settings.redis_password,
                    decode_responses=True
                )
                self.client.ping()
                self.logger.info("✅ Cache Redis connecté")
            except Exception as e:
                self.logger.warning(f"Redis non disponible: {e}")
                self.enabled = False

    def _generate_key(self, query: str, params: Optional[dict] = None) -> str:
        """Générer une clé de cache"""
        data = f"{query}:{json.dumps(params or {}, sort_keys=True)}"
        return f"query:{hashlib.sha256(data.encode()).hexdigest()}"

    def get(self, query: str, params: Optional[dict] = None) -> Optional[Any]:
        """Récupérer depuis le cache"""
        if not self.enabled:
            return None

        try:
            key = self._generate_key(query, params)
            data = self.client.get(key)

            if data:
                self.logger.debug(f"Cache hit: {key}")
                return json.loads(data)

            return None
        except Exception as e:
            self.logger.error(f"Cache get error: {e}")
            return None

    def set(
            self,
            query: str,
            value: Any,
            params: Optional[dict] = None,
            ttl: Optional[int] = None
    ) -> bool:
        """Sauvegarder dans le cache"""
        if not self.enabled:
            return False

        try:
            key = self._generate_key(query, params)
            data = json.dumps(value)

            self.client.setex(
                key,
                ttl or self.ttl,
                data
            )

            self.logger.debug(f"Cache set: {key}")
            return True
        except Exception as e:
            self.logger.error(f"Cache set error: {e}")
            return False

    def invalidate(self, pattern: str = "*") -> int:
        """Invalider le cache"""
        if not self.enabled:
            return 0

        try:
            keys = self.client.keys(f"query:{pattern}")
            if keys:
                return self.client.delete(*keys)
            return 0
        except Exception as e:
            self.logger.error(f"Cache invalidate error: {e}")
            return 0

    def health_check(self) -> bool:
        """Vérifier la santé"""
        if not self.enabled:
            return True  # Pas d'erreur si désactivé

        try:
            return self.client.ping()
        except Exception:
            return False


# Instances globales
neo4j_service = Neo4jService()
llm_service = LLMService()
cache_service = CacheService()