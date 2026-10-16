# Rag-Agent (DocuMind)

Rag-Agent (DocuMind) is a Retrieval-Augmented Generation (RAG) document assistant focused on backend services that let users upload documents (PDF, DOCX, DOC, TXT), extract and chunk text, produce embeddings, store vectors in PostgreSQL + pgvector, and answer queries with context-aware responses and source citations.

This README reflects the current state of the project on the `develop` branch. For more detailed guides, see the docs directory.

Key backend features
- Upload and process PDF, DOCX, DOC, and TXT files via API
- Asynchronous background processing with Celery + Redis
- Text extraction (PyMuPDF, python-docx) and overlapping chunking with metadata
- Embedding generation using Sentence Transformers (all-MiniLM-L6-v2)
- Vector storage and similarity search using PostgreSQL + pgvector
- Context-aware chat endpoints that return answers with source citations (LLM: Groq or configurable)
- Google Drive integration via a separate FastAPI microservice (drive_service)
- JWT authentication with refresh tokens and optional OTP

Repository layout (important folders)
- apps/ — Django apps (including auth_manager, rag)
- core/ — Django project settings, Celery configuration
- drive_service/ — FastAPI microservice for Google Drive sync
- db-init/, db-image/ — helpers for Postgres + pgvector
- docs/ — detailed architecture, API, and quickstart instructions

Quick links
- Docs: docs/QUICKSTART.md, docs/API.md, docs/ARCHITECTURE.md
- Docker compose: docker-compose.yml
- Env examples: .env.example, .env.docker.example, drive_service/.env.example

Minimum requirements
- Python 3.11+ (project tested on 3.12)
- PostgreSQL 13+ with pgvector extension
- Redis for Celery broker

Quickstart (Docker)
1. Copy Docker env files:
   - cp .env.docker.example .env.docker
   - cp drive_service/.env.docker.example drive_service/.env.docker
2. Start services with Docker Compose:
   - docker compose up --build
3. Apply migrations and create a superuser (from the Django container or locally pointing to the DB):
   - python manage.py migrate
   - python manage.py createsuperuser
4. Ensure the Celery worker is running so document tasks are processed. Docker Compose includes a worker service in this repo.

Quickstart (Local development)
1. Create and activate a virtualenv; install dependencies:
   - python -m venv .venv && source .venv/bin/activate
   - pip install -r requirements.txt
2. Configure env files (.env.example is a starting point). For local DB/Redis, set DB_HOST=127.0.0.1 and REDIS_URL=redis://127.0.0.1:6379/0
3. Ensure pgvector extension is enabled in your Postgres database:
   - psql -U <user> -d <db> -c "CREATE EXTENSION IF NOT EXISTS vector;"
4. Run migrations and start services:
   - python manage.py migrate
   - python manage.py runserver
   - Start a Celery worker: celery -A core worker -l info

Database and pgvector
- Create the database and user, then enable pgvector before running migrations:
  psql -U postgres
  CREATE DATABASE ragdb;
  CREATE USER raguser WITH PASSWORD 'ragpassword';
  GRANT ALL PRIVILEGES ON DATABASE ragdb TO raguser;
  \q
  psql -U raguser -d ragdb -c "CREATE EXTENSION IF NOT EXISTS vector;"

API examples
- Upload document (multipart/form-data):
  curl -X POST "http://localhost:8000/api/documents/" \
    -H "Authorization: Bearer <access_token>" \
    -F "file=@/path/to/file.pdf"

- Chat with a document (LLM answer + citations):
  curl -X POST "http://localhost:8000/api/documents/{id}/chat/" \
    -H "Authorization: Bearer <access_token>" \
    -H "Content-Type: application/json" \
    -d '{"message":"Summarize the key points from the uploaded document."}'

Testing
- Run Django tests:
  python manage.py test
- Run app-specific tests:
  python manage.py test apps.rag

Production checklist (short)
- Set DEBUG=False and configure ALLOWED_HOSTS
- Use a secrets manager for API keys and credentials
- Configure HTTPS and a reverse proxy (nginx)
- Run Gunicorn (or similar) behind nginx
- Add monitoring (Sentry/Prometheus) and structured logs
- Ensure pgvector extension exists on production DB
- Enable backups and retention for data volumes

Contributing
Contributions are welcome. Workflow:
1. Fork the repository
2. Create a branch: git checkout -b feature/your-feature
3. Commit with clear messages and open a Pull Request

License
- This repository currently does not include a LICENSE file. Add one (e.g., MIT) to clarify usage and contributions.

Author
- Arbaz Khan — https://github.com/hello-arbaaz-khan

---

For full setup and API details, see docs/QUICKSTART.md and docs/API.md.
