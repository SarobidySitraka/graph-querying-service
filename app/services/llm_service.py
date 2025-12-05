from openai import OpenAI, OpenAIError
from typing import Optional
from app.services.base import BaseService
from app.core.config import settings
from app.core.exceptions import LLMServiceError


class LLMService(BaseService):
    """Service pour le LLM (OpenAI)"""

    def __init__(self):
        super().__init__()
        self.client = OpenAI(
            api_key=settings.openai_api_key,
            timeout=settings.llm_timeout
        )
        self.model = settings.llm_model
        self.temperature = settings.llm_temperature
        self.max_tokens = settings.llm_max_tokens

    def generate_completion(
            self,
            prompt: str,
            system_message: Optional[str] = None,
            temperature: Optional[float] = None,
            max_tokens: Optional[int] = None
    ) -> str:
        """
        Générer une completion

        Args:
            prompt: Le prompt utilisateur
            system_message: Message système
            temperature: Température (override)
            max_tokens: Max tokens (override)

        Returns:
            Réponse du LLM
        """
        messages = []

        if system_message:
            messages.append({"role": "system", "content": system_message})

        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature or self.temperature,
                max_completion_tokens=max_tokens or self.max_tokens
            )

            content = response.choices[0].message.content

            self.logger.info(
                f"LLM completion generated: {response.usage.total_tokens} tokens"
            )

            return content

        except OpenAIError as e:
            self.logger.error(f"OpenAI error: {e}")
            raise LLMServiceError(f"Erreur LLM: {str(e)}")
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            raise LLMServiceError(f"Erreur inattendue: {str(e)}")

    def health_check(self) -> bool:
        """Vérifier la santé"""
        try:
            # Simple test avec un prompt minimal
            self.generate_completion("test", max_tokens=5)
            return True
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False

llm_service = LLMService()