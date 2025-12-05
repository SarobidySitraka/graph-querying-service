from fastapi import Header, HTTPException, status
from typing import Optional
from app.core.config import settings
from app.core.security import verify_api_key


async def get_api_key(x_api_key: Optional[str] = Header(None)) -> str:
    """Dépendance pour vérifier l'API key"""
    if not settings.api_key_enabled:
        return "public"

    if not x_api_key or not verify_api_key(x_api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key invalide ou manquante"
        )

    return x_api_key