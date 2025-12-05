from typing import List, Dict, Any, Optional
from app.database.neo4j import neo4j_connection
from app.core.logging import get_logger
from app.core.exceptions import QueryExecutionError
from tenacity import retry, stop_after_attempt, wait_exponential

logger = get_logger(__name__)


class DatabaseManager:
    """Gestionnaire de base de données"""

    def __init__(self):
        self.connection = neo4j_connection

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def execute_query(
        self,
        cypher: str,
        parameters: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Exécuter une requête Cypher

        Args:
            cypher: Requête Cypher
            parameters: Paramètres de la requête
            timeout: Timeout en secondes

        Returns:
            Liste de résultats
        """
        try:
            with self.connection.get_session() as session:
                result = session.run(
                    cypher,
                    parameters or {},
                    timeout=timeout
                )
                return [dict(record.data()) for record in result]

        except Exception as e:
            logger.error(f"Erreur lors de l'exécution de la requête: {e}")
            raise QueryExecutionError(f"Erreur d'exécution: {str(e)}")

    def validate_query(self, cypher: str) -> tuple[bool, Optional[str]]:
        """
        Valider une requête Cypher sans l'exécuter

        Args:
            cypher: Requête à valider

        Returns:
            Tuple (is_valid, error_message)
        """
        try:
            explain_query = f"EXPLAIN {cypher}"

            with self.connection.get_session() as session:
                session.run(explain_query)

            return True, None

        except Exception as e:
            error_msg = str(e)
            logger.warning(f"Requête Cypher invalide: {error_msg}")
            return False, error_msg

    def get_schema(self) -> Dict[str, Any]:
        """
        Récupérer le schéma de la base de données

        Returns:
            Dictionnaire contenant le schéma
        """
        from neo4j.time import DateTime

        def _convert_datetime(obj):
            if isinstance(obj, DateTime):
                return obj.isoformat()
            return obj

        schema = {
            "node_labels": [],
            "relationship_types": [],
            "property_keys": [],
            "constraints": [],
            "indexes": []
        }
        try:
            with self.connection.get_session() as session:
                # Labels
                result = session.run("CALL db.labels()")
                schema["node_labels"] = [record.data().get("label") for record in result]
                # Relations
                result = session.run("CALL db.relationshipTypes()")
                schema["relationship_types"] = [
                    record.data().get("relationshipType") for record in result
                ]

                # Propriétés
                result = session.run("CALL db.propertyKeys()")
                schema["property_keys"] = [
                    record.data().get("propertyKey") for record in result
                ]

                # Contraintes
                result = session.run("SHOW CONSTRAINTS")
                schema["constraints"] = [dict(record.data()) for record in result]

                # Index
                result = session.run("SHOW INDEXES")
                schema["indexes"] = [
                    {k: _convert_datetime(v) for k, v in dict(record.data()).items()}
                    for record in result
                ]

        except Exception as e:
            logger.error(f"Erreur lors de la récupération du schéma: {e}")

        return schema

    def execute_read_transaction(
            self,
            transaction_function,
            **kwargs
    ) -> Any:
        """Exécuter une transaction en lecture"""
        with self.connection.get_session() as session:
            return session.execute_read(transaction_function, **kwargs)

    def execute_write_transaction(
            self,
            transaction_function,
            **kwargs
    ) -> Any:
        """Exécuter une transaction en écriture"""
        with self.connection.get_session() as session:
            return session.execute_write(transaction_function, **kwargs)

    def get_database_info(self) -> Dict[str, Any]:
        """Récupérer les informations de la base"""
        info = {}

        try:
            with self.connection.get_session() as session:
                # Compter les nœuds
                result = session.run("MATCH (n) RETURN count(n) as count")
                info["node_count"] = result.single()["count"]

                # Compter les relations
                result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
                info["relationship_count"] = result.single()["count"]

                # Version Neo4j
                result = session.run("CALL dbms.components()")
                for record in result:
                    if record["name"] == "Neo4j Kernel":
                        info["neo4j_version"] = record["versions"][0]

        except Exception as e:
            logger.error(f"Erreur lors de la récupération des infos: {e}")

        return info


# Instance globale
db_manager = DatabaseManager()