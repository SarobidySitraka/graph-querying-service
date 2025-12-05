from neo4j import GraphDatabase, Driver
from typing import Optional
from contextlib import contextmanager
from app.core.config import settings
from app.core.logging import get_logger
from app.core.exceptions import Neo4jConnectionError

logger = get_logger(__name__)


class Neo4jConnection:
    """Neo4j connection management"""

    _instance: Optional['Neo4jConnection'] = None
    _driver: Optional[Driver] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def connect(self) -> None:
        """Establish Neo4j connection"""
        if self._driver is not None:
            logger.warning("Neo4j Driver is already connected")
            return

        try:
            self._driver = GraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_user, settings.neo4j_password),
                max_connection_lifetime=settings.neo4j_max_connection_lifetime,
                max_connection_pool_size=settings.neo4j_max_connection_pool_size,
                connection_timeout=settings.neo4j_connection_timeout
            )

            # Connexion verification
            self._driver.verify_connectivity()
            logger.info("Neo4j connection is established successfully")

        except Exception as e:
            logger.error(f"Neo4j connection error: {e}")
            raise Neo4jConnectionError(f"Impossible to connect to Neo4j: {str(e)}")

    def close(self) -> None:
        if self._driver is not None:
            self._driver.close()
            self._driver = None
            logger.info("Neo4j connection closed")

    def is_connected(self) -> bool:
        """Verify if connected"""
        if self._driver is None:
            return False

        try:
            self._driver.verify_connectivity()
            return True
        except Exception as e:
            logger.error(f"Neo4j connection lost: {e}")
            return False

    @property
    def driver(self) -> Driver:
        if self._driver is None:
            raise Neo4jConnectionError("Neo4j driver not initialised")
        return self._driver

    @contextmanager
    def get_session(self, database: Optional[str] = None):
        """Context manager pour une session"""
        db = database or settings.neo4j_database
        session = self._driver.session(database=db)
        try:
            yield session
        finally:
            session.close()


# Singleton instance
neo4j_connection = Neo4jConnection()