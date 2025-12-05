from typing import Optional
from app.services.llm_service import llm_service
from app.graphrag.prompts.system import SystemPrompts, PromptTemplates
from app.graphrag.context_builder import ContextBuilder
from app.core.logging import get_logger
from app.core.config import settings
import re

logger = get_logger(__name__)


def _clean_cypher(cypher: str) -> str:
    """Nettoyer le Cypher généré"""
    # Enlever les markdown code blocks
    cypher = re.sub(r'```cypher\n?', '', cypher)
    cypher = re.sub(r'```\n?', '', cypher)

    # Enlever les commentaires
    cypher = re.sub(r'//.*?$', '', cypher, flags=re.MULTILINE)

    # Normaliser les espaces
    cypher = ' '.join(cypher.split())

    return cypher.strip()


class CypherGenerator:
    """Générateur de requêtes Cypher"""

    def __init__(self):
        self.llm = llm_service
        self.context_builder = ContextBuilder(
            max_context_length=settings.graphrag_max_context_length
        )

    def generate(
        self,
        question: str,
        schema: dict,
        context: Optional[str] = None
    ) -> str:
        """
        Générer une requête Cypher à partir d'une question

        Args:
            question: Question en langage naturel
            schema: Schéma de la base
            context: Contexte additionnel

        Returns:
            Requête Cypher générée
        """
        # Construire le prompt système
        system_prompt = SystemPrompts.get_cypher_generation_prompt(schema)

        # Construire le prompt utilisateur
        user_prompt = PromptTemplates.format_cypher_prompt(question, context)

        # Générer le Cypher
        cypher = self.llm.generate_completion(
            prompt=user_prompt,
            system_message=system_prompt
        )

        # Nettoyer le Cypher
        cypher = _clean_cypher(cypher)

        logger.info(f"Cypher généré: {cypher}")

        return cypher

