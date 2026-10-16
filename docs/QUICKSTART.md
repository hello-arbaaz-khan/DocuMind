# Quickstart — Rag-Agent (develop)

This guide highlights the most common steps to get Rag-Agent running for backend development or local Docker usage. For full details, see docs/API.md and docs/ARCHITECTURE.md.

Docker (recommended for parity)
1. Copy example Docker env files to active files:
   - cp .env.docker.example .env.docker
   - cp drive_service/.env.docker.example drive_service/.env.docker
2. Build and start the stack:
   - docker compose up --build
3. Services included in compose:
   - db (Postgres with pgvector), redis, web (Django), worker (Celery), drive_service
4. Run migrations (from web container or host configured to talk to the DB):
   - python manage.py migrate
5. Create a superuser:
   - python manage.py createsuperuser

Local development
1. Create a virtualenv and install dependencies:
   - python -m venv .venv && source .venv/bin/activate
   - pip install -r requirements.txt
2. Configure .env using .env.example
3. Ensure Postgres has pgvector enabled (before migrations):
   - psql -U <user> -d <db> -c "CREATE EXTENSION IF NOT EXISTS vector;"
4. Run migrations and start Django and Celery:
   - python manage.py migrate
   - python manage.py runserver
   - celery -A core worker -l info

Database notes
- Default compose publishes Postgres on host port 5433 and Redis on 6380; check docker-compose.yml and the .env.docker.example values to confirm port mapping.
- Enable the pgvector extension in your DB prior to running migrations.

Document processing flow (brief)
1. Upload document via API
2. Celery task extracts text, chunks it, generates embeddings, and stores vectors in Postgres
3. Query flows embed the question and run similarity search to retrieve chunks
4. Chunks are passed to the LLM to generate answers with cited sources

Troubleshooting
- DB connection refused: confirm DB container is running and DB_HOST/DB_PORT match compose or local settings
- Redis connection refused: verify Redis container and the CELERY_BROKER_URL
- Celery tasks not running: ensure Celery worker has started and uses the same broker

If you'd like, I can:
- Open a PR that updates README.md and docs/QUICKSTART.md on `develop`
- Add LICENSE, CONTRIBUTING.md, and GitHub Actions workflows in a follow-up
