from typing import List, Dict, Any
from app.services.llm_service import llm_service
from app.graphrag.prompts.system import SystemPrompts, PromptTemplates
from app.core.logging import get_logger

logger = get_logger(__name__)


def _format_fallback_response(
        results: List[Dict[str, Any]]
) -> str:
    """Réponse de secours si le LLM échoue"""
    if not results:
        return "Aucun résultat trouvé."

    count = len(results)
    sample = results[0] if results else {}

    return f"J'ai trouvé {count} résultat{'s' if count > 1 else ''}. Exemple: {sample}"


class ResponseFormatter:
    """Formateur de réponses"""

    def __init__(self):
        self.llm = llm_service

    def format_natural_response(
            self,
            question: str,
            results: List[Dict[str, Any]]
    ) -> str:
        """
        Générer une réponse en langage naturel

        Args:
            question: Question originale
            results: Résultats de la requête

        Returns:
            Réponse en langage naturel
        """
        if not results:
            return "Aucune information trouvée pour répondre à cette question."

        # Construire le prompt
        system_prompt = SystemPrompts.get_response_generation_prompt()
        user_prompt = PromptTemplates.format_response_prompt(question, results)

        # Générer la réponse
        try:
            response = self.llm.generate_completion(
                prompt=user_prompt,
                system_message=system_prompt
            )
            return response
        except Exception as e:
            logger.error(f"Erreur lors de la génération de réponse: {e}")
            return _format_fallback_response(results)

