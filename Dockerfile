FROM python:3.11-slim-trixie as builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Répertoire de travail
WORKDIR /app

# Copier les fichiers de configuration
COPY pyproject.toml ./
COPY README.md ./
COPY . .

RUN uv lock && uv sync --frozen --no-cache

# Stage final
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

RUN apt-get update && apt-get install -y curl

WORKDIR /app

# Copier l'environnement virtuel depuis le builder
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/app /app/app

# Créer le dossier de logs
RUN mkdir -p logs

# Exposer le port
EXPOSE 8000

# Variable d'environnement pour le path
ENV PATH="/app/.venv/bin:$PATH"

# Commande de démarrage
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]