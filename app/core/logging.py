import logging
import sys
import json
from datetime import datetime, timezone
from typing import Any, Dict
from pathlib import Path
from logging.handlers import RotatingFileHandler

from app.core.config import settings


class JSONFormatter(logging.Formatter):
    """Formatter JSON pour logs structurés"""

    def format(self, record: logging.LogRecord) -> str:
        """Formater un log record en JSON"""
        log_data: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "thread": record.thread,
            "thread_name": record.threadName,
        }

        # Ajouter les informations d'exception
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info)
            }

        # Ajouter les extras
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id

        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id

        if hasattr(record, "api_key"):
            log_data["api_key"] = record.api_key[:8] + "..."  # Masquer

        if hasattr(record, "execution_time"):
            log_data["execution_time_ms"] = record.execution_time

        if hasattr(record, "query_type"):
            log_data["query_type"] = record.query_type

        # Ajouter les extra fields personnalisés
        for key, value in record.__dict__.items():
            if key not in ["name", "msg", "args", "created", "filename", "funcName",
                           "levelname", "levelno", "lineno", "module", "msecs",
                           "message", "pathname", "process", "processName",
                           "relativeCreated", "thread", "threadName", "exc_info",
                           "exc_text", "stack_info", "request_id", "user_id",
                           "api_key", "execution_time", "query_type"]:
                if isinstance(value, datetime):
                    log_data[key] = value.isoformat() + "Z"
                else:
                    log_data[key] = value

        return json.dumps(log_data, ensure_ascii=False, default=str)


class ColoredFormatter(logging.Formatter):
    """Formatter avec couleurs pour la console"""

    # Codes couleurs ANSI
    COLORS = {
        'DEBUG': '\033[36m',  # Cyan
        'INFO': '\033[32m',  # Vert
        'WARNING': '\033[33m',  # Jaune
        'ERROR': '\033[31m',  # Rouge
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'
    }

    def format(self, record: logging.LogRecord) -> str:
        """Formater avec couleurs"""
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']

        # Format de base
        formatted = f"{color}[{record.levelname}]{reset} "
        formatted += f"{datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')} "
        formatted += f"- {record.name} - {record.getMessage()}"

        # Ajouter l'exception si présente
        if record.exc_info:
            formatted += f"\n{self.formatException(record.exc_info)}"

        return formatted


class StandardFormatter(logging.Formatter):
    """Formatter standard pour fichiers"""

    def __init__(self):
        super().__init__(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )


class LoggerManager:
    """Gestionnaire de logging centralisé"""

    _configured = False

    @classmethod
    def setup(cls) -> None:
        """Configurer le système de logging"""
        if cls._configured:
            return

        # Créer le répertoire de logs
        log_path = Path(settings.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        # Logger root
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, settings.log_level.upper()))

        # Supprimer les handlers existants
        root_logger.handlers.clear()

        # Handler console
        if settings.log_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(
                logging.DEBUG if settings.app_debug else logging.INFO
            )

            # Choisir le formatter
            if settings.log_format == "json":
                console_handler.setFormatter(JSONFormatter())
            elif settings.log_format == "color":
                console_handler.setFormatter(ColoredFormatter())
            else:
                console_handler.setFormatter(StandardFormatter())

            root_logger.addHandler(console_handler)

        # Handler fichier
        if settings.log_file_enabled:
            # Utiliser RotatingFileHandler
            file_handler = RotatingFileHandler(
                settings.log_file,
                maxBytes=500_000_000,  # 500 MB
                backupCount=10,
                encoding="utf-8"
            )
            file_handler.setLevel(logging.DEBUG)

            # Toujours JSON pour les fichiers
            file_handler.setFormatter(JSONFormatter())

            root_logger.addHandler(file_handler)

        # Configurer les loggers de bibliothèques tierces
        cls._configure_third_party_loggers()

        cls._configured = True

        # Log de confirmation
        logger = logging.getLogger(__name__)
        logger.info(
            "Logging configuré",
            extra={
                "level": settings.log_level,
                "format": settings.log_format,
                "file": settings.log_file,
                "console": settings.log_console
            }
        )

    @staticmethod
    def _configure_third_party_loggers():
        """Configurer les loggers des bibliothèques tierces"""
        # Réduire le niveau pour certaines bibliothèques bruyantes
        logging.getLogger("uvicorn").setLevel(logging.WARNING)
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
        logging.getLogger("uvicorn.error").setLevel(logging.INFO)
        logging.getLogger("fastapi").setLevel(logging.WARNING)
        logging.getLogger("neo4j").setLevel(logging.WARNING)
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("httpcore").setLevel(logging.WARNING)
        logging.getLogger("openai").setLevel(logging.WARNING)


def setup_logging() -> None:
    """Setup public du logging"""
    LoggerManager.setup()


def get_logger(name: str) -> logging.Logger:
    """
    Obtenir un logger

    Args:
        name: Nom du logger (généralement __name__)

    Returns:
        Logger configuré
    """
    return logging.getLogger(name)


class LoggerAdapter(logging.LoggerAdapter):
    """Adaptateur pour ajouter du contexte aux logs"""

    def process(self, msg, kwargs):
        """Ajouter le contexte extra"""
        if 'extra' not in kwargs:
            kwargs['extra'] = {}
        kwargs['extra'].update(self.extra)
        return msg, kwargs


def get_contextual_logger(name: str, **context) -> LoggerAdapter:
    """
    Obtenir un logger avec contexte

    Args:
        name: Nom du logger
        **context: Contexte à ajouter à chaque log

    Returns:
        Logger avec contexte
    """
    logger = get_logger(name)
    return LoggerAdapter(logger, context)