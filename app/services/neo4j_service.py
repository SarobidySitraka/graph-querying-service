from typing import List, Dict, Any, Optional, Tuple
from app.services.base import BaseService
from app.database.manager import db_manager
from app.core.config import settings
from app.core.exceptions import InvalidCypherQueryError
import time


class Neo4jService(BaseService):
    """Service pour Neo4j"""

    def __init__(self):
        super().__init__()
        self.db = db_manager

    def execute_cypher(
            self,
            cypher: str,
            parameters: Optional[Dict[str, Any]] = None,
            timeout: Optional[int] = None
    ) -> Tuple[List[Dict[str, Any]], float]:
        """
        Exécuter une requête Cypher

        Returns:
            Tuple (résultats, temps_execution_ms)
        """
        start_time = time.time()

        # Valider d'abord
        if settings.enable_query_validation:
            is_valid, error_msg = self.validate_cypher(cypher)
            if not is_valid:
                raise InvalidCypherQueryError(error_msg)

        # Exécuter
        results = self.db.execute_query(
            cypher,
            parameters,
            timeout or settings.query_timeout
        )

        execution_time = (time.time() - start_time) * 1000

        self.logger.info(
            f"Query executed: {len(results)} results in {execution_time:.2f}ms"
        )

        return results, execution_time

    def validate_cypher(self, cypher: str) -> Tuple[bool, Optional[str]]:
        """Valider une requête Cypher"""
        return self.db.validate_query(cypher)

    def get_schema(self) -> Dict[str, Any]:
        """Récupérer le schéma"""
        return self.db.get_schema()

    def get_database_info(self) -> Dict[str, Any]:
        """Récupérer les infos de la base"""
        return self.db.get_database_info()

    def health_check(self) -> bool:
        """Vérifier la santé"""
        try:
            self.db.execute_query("RETURN 1")
            return True
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False

neo4j_service = Neo4jService()