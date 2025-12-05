from fastapi import FastAPI, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.core.config import settings


def get_rate_limit_key(request: Request) -> str:
    """Clé pour le rate limiting"""
    # Utiliser l'API key si présente, sinon l'IP
    api_key = request.headers.get("X-API-Key")
    if api_key:
        return f"api_key:{api_key}"
    return get_remote_address(request)


limiter = Limiter(
    key_func=get_rate_limit_key,
    default_limits=[f"{settings.rate_limit_calls}/{settings.rate_limit_period}second"]
    if settings.rate_limit_enabled else []
)


def setup_rate_limiting(app: FastAPI) -> None:
    """Configurer le rate limiting"""
    if settings.rate_limit_enabled:
        app.state.limiter = limiter
        app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)