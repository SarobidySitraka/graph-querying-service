import re
from typing import Tuple
from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)


def _has_limit(cypher: str) -> bool:
    """Vérifier si la requête a un LIMIT"""
    return bool(re.search(r'\bLIMIT\s+\d+', cypher, re.IGNORECASE))


def _add_limit(cypher: str, limit: int) -> str:
    """Ajouter un LIMIT à la requête"""
    return f"{cypher.rstrip(';')} LIMIT {limit}"


class QueryOptimizer:
    """Optimiseur de requêtes Cypher"""

    DANGEROUS_KEYWORDS = [
        'CREATE', 'DELETE', 'REMOVE', 'SET', 'MERGE',
        'DROP', 'ALTER', 'DETACH DELETE'
    ]

    def __init__(self):
        self.max_results = settings.max_query_results
        self.default_limit = settings.default_query_limit

    def optimize(self, cypher: str) -> str:
        """Optimiser une requête Cypher"""
        # Ajouter LIMIT si absent
        if not _has_limit(cypher):
            cypher = _add_limit(cypher, self.default_limit)

        return cypher

    def is_read_only(self, cypher: str) -> Tuple[bool, str]:
        """
        Vérifier si la requête est en lecture seule

        Returns:
            Tuple (is_read_only, error_message)
        """
        if not settings.enable_read_only_mode:
            return True, ""

        cypher_upper = cypher.upper()

        for keyword in self.DANGEROUS_KEYWORDS:
            if re.search(r'\b' + keyword + r'\b', cypher_upper):
                return False, f"Opération non autorisée: {keyword}"

        return True, ""

