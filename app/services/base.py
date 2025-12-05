from abc import ABC, abstractmethod
from app.core.logging import get_logger


class BaseService(ABC):
    """Service de base"""

    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)

    @abstractmethod
    def health_check(self) -> bool:
        """Vérifier la santé du service"""
        pass