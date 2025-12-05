from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.exceptions import BaseAPIException
from app.core.logging import get_logger
from app.models.response.base import ErrorResponse
from app.models.base import ErrorDetail
import traceback

logger = get_logger(__name__)


def setup_error_handlers(app: FastAPI) -> None:
    """Configurer les gestionnaires d'erreurs"""

    @app.exception_handler(BaseAPIException)
    async def api_exception_handler(request: Request, exc: BaseAPIException):
        logger.error(f"API Exception: {exc.detail}", extra={
            "error_code": exc.error_code,
            "path": request.url.path
        })

        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error=ErrorDetail(
                    error_code=exc.error_code or "API_ERROR",
                    message=exc.detail
                )
            ).model_dump()
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.warning(f"Validation error: {exc.errors()}")

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=ErrorResponse(
                error=ErrorDetail(
                    error_code="VALIDATION_ERROR",
                    message="Erreur de validation des données",
                    details={"errors": exc.errors()}
                )
            ).model_dump()
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error=ErrorDetail(
                    error_code="HTTP_ERROR",
                    message=exc.detail
                )
            ).model_dump()
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.critical(f"Unhandled exception: {str(exc)}\n{traceback.format_exc()}")

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                error=ErrorDetail(
                    error_code="INTERNAL_ERROR",
                    message="Erreur interne du serveur"
                )
            ).model_dump()
        )