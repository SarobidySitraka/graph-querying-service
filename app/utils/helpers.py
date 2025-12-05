from typing import Dict, Any
import time
from functools import wraps
from app.core.logging import get_logger

logger = get_logger(__name__)


def timeit(func):
    """Décorateur pour mesurer le temps d'exécution"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = (time.time() - start) * 1000
        logger.debug(f"{func.__name__} executed in {duration:.2f}ms")
        return result
    return wrapper


def safe_execute(func, default=None, log_error=True):
    """Exécuter une fonction de manière sûre"""
    try:
        return func()
    except Exception as e:
        if log_error:
            logger.error(f"Error in {func.__name__}: {e}")
        return default


def truncate_string(s: str, max_length: int = 100) -> str:
    """Tronquer une chaîne"""
    if len(s) <= max_length:
        return s
    return s[:max_length-3] + "..."


def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """Fusionner plusieurs dictionnaires"""
    result = {}
    for d in dicts:
        result.update(d)
    return result