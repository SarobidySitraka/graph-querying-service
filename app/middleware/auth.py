from fastapi import Request, HTTPException, status, FastAPI
from fastapi.security import HTTPBearer
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import settings
from app.core.security import verify_api_key, verify_token
from app.core.logging import get_logger

logger = get_logger(__name__)
security = HTTPBearer(auto_error=False)


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware d'authentification"""

    # Routes publiques (pas d'auth requise)
    PUBLIC_ROUTES = [
        "/",
        "/docs",
        "/openapi.json",
        "/redoc",
        "/api/v1/health"
    ]

    async def dispatch(self, request: Request, call_next):
        # Vérifier si la route est publique
        if request.url.path in self.PUBLIC_ROUTES:
            return await call_next(request)

        if not settings.api_key_enabled:
            return await call_next(request)

        # Vérifier l'API Key
        api_key = request.headers.get("X-API-Key")

        if not api_key:
            # Essayer avec Bearer token
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
                try:
                    payload = verify_token(token)
                    request.state.user = payload
                    return await call_next(request)
                except HTTPException:
                    pass

        if not api_key or not verify_api_key(api_key):
            logger.warning(f"Unauthorized access attempt to {request.url.path}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API Key invalide ou manquante",
                headers={"WWW-Authenticate": "Bearer"}
            )

        request.state.api_key = api_key
        return await call_next(request)


def setup_auth(app: FastAPI) -> None:
    """Configurer l'authentification"""
    if settings.api_key_enabled:
        app.add_middleware(AuthMiddleware)