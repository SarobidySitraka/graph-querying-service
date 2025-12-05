#FROM python:3.11-slim as builder
#
## Variables d'environnement
#ENV PYTHONUNBUFFERED=1 \
#    PYTHONDONTWRITEBYTECODE=1 \
#    PIP_NO_CACHE_DIR=1 \
#    PIP_DISABLE_PIP_VERSION_CHECK=1
#
## Installer uv
#RUN pip install uv

FROM python:3.11-slim-trixie as builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Répertoire de travail
WORKDIR /app

# Copier les fichiers de configuration
COPY pyproject.toml ./
COPY README.md ./
COPY app ./app

# Créer l'environnement virtuel et installer les dépendances
#RUN uv venv && \
#    . .venv/bin/activate && \
#    uv pip install -e . \

RUN uv lock && uv sync --frozen --no-cache

# Stage final
FROM python:3.11-slim

WORKDIR /app

# Copier l'environnement virtuel depuis le builder
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/app /app/app

# Créer le dossier de logs
RUN mkdir -p logs

# Exposer le port
EXPOSE 8004

# Variable d'environnement pour le path
ENV PATH="/app/.venv/bin:$PATH"

# Commande de démarrage
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8004"]