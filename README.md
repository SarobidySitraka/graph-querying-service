# Graph Querying Service 🚀

Service professionnel de requêtage Neo4j avec GraphRAG et LLM permettant d'interroger une base de données graphe via des requêtes Cypher directes ou en langage naturel.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com)
[![Neo4j](https://img.shields.io/badge/Neo4j-5.0+-red.svg)](https://neo4j.com)

## Fonctionnalités

- ** Requêtes Cypher**: Exécution sécurisée de requêtes Cypher directes
- ** Langage Naturel**: Conversion automatique de questions en français vers Cypher
- ** GraphRAG**: Utilisation intelligente du contexte et du schéma de la base
- ** Validation**: Validation automatique des requêtes avant exécution
- **️ Sécurité**: Authentification API Key, rate limiting, mode lecture seule
- ** Performance**: Cache Redis, optimisation automatique des requêtes
- ** Monitoring**: Logs structurés, métriques, health checks

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    API Layer (FastAPI)                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │  Health  │ │  Cypher  │ │ Natural  │ │  Schema  │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
    ┌────▼────┐           ┌─────▼──────┐
    │ GraphRAG │           │  Neo4j     │
    │  Engine  │◄──────────│  Service   │
    └────┬─────┘           └────────────┘
         │
    ┌────▼─────┐
    │   LLM    │
    │ Service  │
    └──────────┘
```

## Prérequis

- Python 3.10+
- Neo4j 5.0+
- OpenAI API Key (ou autre LLM compatible)
- Redis (optionnel, pour le cache)
- uv (gestionnaire de paquets)

## Installation

### 1. Cloner le projet

```bash
git clone <your-repo>
cd graph-querying-service
```

### 2. Installer uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 3. Setup de l'environnement

```bash
# Créer l'environnement virtuel
uv venv

# Activer l'environnement
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate  # Windows

# Installer les dépendances
uv pip install -e .
```

### 4. Configuration

```bash
# Copier le fichier d'exemple
cp .env.example .env

# Éditer avec vos credentials
nano .env
```

**Variables essentielles à configurer:**

```env
# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=votre_mot_de_passe

# OpenAI
OPENAI_API_KEY=sk-votre-clé-api

# Sécurité
SECRET_KEY=générez-une-clé-secrète-forte
API_KEYS=["key1","key2"]
```

### 5. Démarrer le service

```bash
# Mode développement
uvicorn app.main:app --reload

# Mode production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

L'API sera accessible sur:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Docker

### Démarrage rapide avec Docker Compose

```bash
# Démarrer tous les services
docker-compose up -d

# Voir les logs
docker-compose logs -f api

# Arrêter
docker-compose down
```

### Build manuel

```bash
# Build l'image
docker build -t graph-querying-service .

# Run
docker run -p 8000:8000 --env-file .env graph-querying-service
```

## Utilisation

### 1. Health Check

```bash
curl http://localhost:8000/api/v1/health
```

### 2. Requête Cypher Directe

```bash
curl -X POST "http://localhost:8000/api/v1/query/cypher" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "cypher": "MATCH (p:Person) RETURN p.name, p.age LIMIT 10"
  }'
```

**Réponse:**

```json
{
  "success": true,
  "data": [
    {"p.name": "Alice", "p.age": 30},
    {"p.name": "Bob", "p.age": 25}
  ],
  "metadata": {
    "query_type": "cypher",
    "execution_time_ms": 45.2,
    "result_count": 2,
    "generated_cypher": "MATCH (p:Person) RETURN p.name, p.age LIMIT 10",
    "used_cache": false
  },
  "timestamp": "2024-11-06T10:30:00Z"
}
```

### 3. Requête en Langage Naturel

```bash
curl -X POST "http://localhost:8000/api/v1/query/natural" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "question": "Qui travaille dans l'\''entreprise TechCorp?",
    "return_cypher": true
  }'
```

**Réponse:**

```json
{
  "success": true,
  "data": [
    {"name": "Alice Dupont", "position": "Senior Developer"},
    {"name": "Bob Martin", "position": "Junior Developer"}
  ],
  "metadata": {
    "query_type": "natural",
    "execution_time_ms": 1250.5,
    "result_count": 2,
    "generated_cypher": "MATCH (p:Person)-[:WORKS_AT]->(c:Company {name: 'TechCorp'}) RETURN p.name as name, r.position as position LIMIT 100"
  },
  "answer": "Deux personnes travaillent chez TechCorp: Alice Dupont en tant que Senior Developer et Bob Martin en tant que Junior Developer.",
  "timestamp": "2024-11-06T10:30:00Z"
}
```

### 4. Validation de Requête

```bash
curl -X POST "http://localhost:8000/api/v1/query/validate" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "cypher": "MATCH (n:Person) RETURN n LIMIT 10",
    "check_read_only": true
  }'
```

### 5. Récupérer le Schéma

```bash
curl -X GET "http://localhost:8000/api/v1/schema" \
  -H "X-API-Key: your-api-key"
```

## Sécurité

### Authentification par API Key

Ajoutez l'en-tête `X-API-Key` à toutes vos requêtes:

```bash
-H "X-API-Key: your-api-key"
```

### Configuration des API Keys

Dans `.env`:

```env
API_KEY_ENABLED=true
API_KEYS=["key1","key2","key3"]
```

### Mode Lecture Seule

Par défaut, seules les requêtes en lecture sont autorisées (MATCH, RETURN).
Les opérations d'écriture (CREATE, DELETE, SET, etc.) sont bloquées.

Pour désactiver (non recommandé en production):

```env
ENABLE_READ_ONLY_MODE=false
```

### Rate Limiting

Limites par défaut:
- Requêtes Cypher: 50/minute
- Requêtes naturelles: 30/minute

Configuration dans `.env`:

```env
RATE_LIMIT_ENABLED=true
RATE_LIMIT_CALLS=100
RATE_LIMIT_PERIOD=60
```

## Configuration Avancée

### Cache Redis

Activer le cache pour améliorer les performances:

```env
REDIS_ENABLED=true
REDIS_HOST=localhost
REDIS_PORT=6379
CACHE_TTL=3600
```

### Optimisation des Requêtes

```env
MAX_QUERY_RESULTS=1000
DEFAULT_QUERY_LIMIT=100
QUERY_TIMEOUT=30
```

### GraphRAG

```env
GRAPHRAG_ENABLED=true
GRAPHRAG_USE_SCHEMA_CONTEXT=true
GRAPHRAG_MAX_CONTEXT_LENGTH=4000
GRAPHRAG_INCLUDE_EXAMPLES=true
```

### LLM

```env
LLM_MODEL=gpt-4
LLM_TEMPERATURE=0.0
LLM_MAX_TOKENS=2000
LLM_TIMEOUT=60
```

## Tests

```bash
# Installer les dépendances de test
uv pip install -e ".[dev]"

# Lancer tous les tests
pytest tests/ -v

# Avec couverture
pytest tests/ --cov=app --cov-report=html

# Tests spécifiques
pytest tests/unit/ -v
pytest tests/integration/ -v
```

## Monitoring

### Logs

Les logs sont disponibles dans `logs/app.log` (format JSON par défaut).

```bash
# Suivre les logs
tail -f logs/app.log

# Filtrer les erreurs
grep ERROR logs/app.log
```

### Métriques

Health check endpoint: `/api/v1/health`

Retourne l'état de:
- Neo4j (connectivité, latence)
- LLM (disponibilité)
- Cache (statut)

## Dépannage

### Problème: "Connexion Neo4j échouée"

```bash
# Vérifier que Neo4j est démarré
sudo systemctl status neo4j

# Tester la connexion
cypher-shell -u neo4j -p your_password
```

### Problème: "LLM Service Error"

```bash
# Vérifier la clé API
echo $OPENAI_API_KEY

# Tester l'API OpenAI
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### Problème: "Rate Limit Exceeded"

Augmenter les limites dans `.env`:

```env
RATE_LIMIT_CALLS=200
RATE_LIMIT_PERIOD=60
```

## Documentation API

La documentation interactive complète est disponible sur:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Contribution

1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## Licence

MIT License

## Auteurs
Sarobidy Sitraka

## Remerciements

- FastAPI pour le framework web
- Neo4j pour la base de données graphe
- OpenAI pour le LLM
- La communauté open source

---

**Développé avec passion en utilisant FastAPI, Neo4j et GraphRAG**