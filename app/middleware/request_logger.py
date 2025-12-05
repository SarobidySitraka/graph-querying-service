from fastapi import Request, FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging import get_logger
import time
import uuid

logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware pour logger les requêtes"""

    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        start_time = time.time()

        logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "client": request.client.host if request.client else None
            }
        )

        response = await call_next(request)

        process_time = (time.time() - start_time) * 1000

        logger.info(
            f"Request completed: {request.method} {request.url.path} - {response.status_code}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(process_time, 2)
            }
        )

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(round(process_time, 2))

        return response


def setup_request_logging(app: FastAPI) -> None:
    """Configurer le logging des requêtes"""
    app.add_middleware(RequestLoggingMiddleware)