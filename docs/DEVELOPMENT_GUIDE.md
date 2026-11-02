## 9. Local development without Docker

This mode requires Python 3.12, Node.js/npm, PostgreSQL with pgvector,
Redis and the external credentials used by the features being tested.

1.  Create a Python virtual environment and install root and Drive
    service dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r drive_service/requirements.txt
```

2.  Create and configure `.env` and `drive_service/.env` from their
    example files. Use local host addresses and ensure both services
    point to the same database and Redis instance.
3.  Enable pgvector in the target database if it is not already enabled.
4.  Apply migrations and start Django:

```bash
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

5.  Start the Celery worker in another terminal:

```bash
celery -A core worker -l info
```

6.  Start FastAPI from the `drive_service` directory in another
    terminal, with the project root available on `PYTHONPATH`:

```bash
cd drive_service
PYTHONPATH=.. uvicorn main:app --host 0.0.0.0 --port 8001
```

7.  Install and run the frontend:

```bash
cd frontend
npm install
npm run dev
```

The Vite proxy defaults to Django at `http://localhost:8000` and FastAPI
at `http://localhost:8001`.

## 12. Recommended way to understand and extend the code

For a new developer, read the repository in this order:

1.  `docker-compose.yml` --- understand the running services and
    networking.
2.  `core/settings.py` and `core/celery.py` --- understand Django,
    database and task configuration.
3.  `apps/auth_manager/` --- understand user creation, OTP and JWT
    issuance.
4.  `drive_service/main.py` and `drive_service/app/Apis/routers/` ---
    understand the active API surface.
5.  `apps/documents/models.py` and `apps/chat/models.py` --- understand
    persistent data and ownership.
6.  `apps/documents/tasks.py` --- understand background job entry
    points.
7.  `Workflow/documents/` and `Workflow/chat/` --- understand
    orchestration.
8.  `RagCore/` --- understand the reusable AI/RAG pipeline.
9.  `drive_service/app/services/drive_sync.py` --- understand Drive
    import.
10. `frontend/src/services/`, `frontend/src/router/` and
    `frontend/src/components/` --- connect UI actions to API calls.
11. `.github/workflows/ci.yml` and tests --- understand the quality
    gate.

When implementing a feature, follow the existing ownership boundaries:
keep HTTP validation in the router/schema, application orchestration in
`Workflow/`, reusable retrieval/AI logic in `RagCore/`, persistence in
Django models/services, and UI state in React components/context.
