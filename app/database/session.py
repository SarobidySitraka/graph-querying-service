from typing import Generator
from neo4j import Session
from app.database.neo4j import neo4j_connection


def get_db_session() -> Generator[Session, None, None]:
    """Dependency pour récupérer une session Neo4j"""
    with neo4j_connection.get_session() as session:
        yield session