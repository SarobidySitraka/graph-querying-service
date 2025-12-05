from typing import Dict, Any
from app.core.logging import get_logger

logger = get_logger(__name__)


class ContextBuilder:
    """Constructeur de contexte pour GraphRAG"""

    def __init__(self, max_context_length: int = 4000):
        self.max_context_length = max_context_length

    def build_schema_context(self, schema: Dict[str, Any]) -> str:
        """Construire le contexte du schéma"""
        context_parts = []

        # Labels
        if schema.get("node_labels"):
            labels = ", ".join(schema["node_labels"][:30])
            context_parts.append(f"Labels disponibles: {labels}")

        # Relations
        if schema.get("relationship_types"):
            rels = ", ".join(schema["relationship_types"][:30])
            context_parts.append(f"Relations disponibles: {rels}")

        # Propriétés
        if schema.get("property_keys"):
            props = ", ".join(schema["property_keys"][:50])
            context_parts.append(f"Propriétés disponibles: {props}")

        context = "\n".join(context_parts)

        # Tronquer si trop long
        if len(context) > self.max_context_length:
            context = context[:self.max_context_length] + "..."

        return context

    def build_examples_context(self) -> str:
        """Construire un contexte avec des exemples"""
        examples = [
            "MATCH (p:Person) RETURN p.name LIMIT 10",
            "MATCH (p:Person)-[:WORKS_AT]->(c:Company) RETURN p.name, c.name",
            "MATCH (p:Person) WHERE p.age > 30 RETURN count(p)",
        ]

        return "Exemples de requêtes:\n" + "\n".join(f"- {ex}" for ex in examples)