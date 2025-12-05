from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from app.core.config import settings


def setup_cors(app: FastAPI) -> None:
    """Configurer CORS"""
    if settings.cors_enabled:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_credentials=settings.cors_allow_credentials,
            allow_methods=settings.cors_allow_methods,
            allow_headers=settings.cors_allow_headers,
        )