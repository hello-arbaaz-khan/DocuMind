# Docker setup

## 3. Runtime services and ports

---

Service Container/service Host port Responsibility
name

---

React/Vite `frontend` 3000 Browser UI

Django `django` 8000 Authentication
and Django
project

FastAPI `drive_service` 8001 Documents, chat,
search and Drive
API

PostgreSQL + `db` 5433 Relational data
pgvector and embeddings

Redis `redis` 6380 Celery
broker/result
backend

Celery worker `celery_worker` --- Background jobs

---

Inside Docker, services communicate using Compose service names and
**container ports**: `db:5432`, `redis:6379`, `django:8000`, and
`drive_service:8001`. Host applications use the published ports, such as
PostgreSQL `localhost:5433` and Redis `localhost:6380`.

The Compose file mounts `media-data` for uploaded media and
`postgres-data` for database persistence. It also mounts the Hugging
Face cache to avoid repeatedly downloading model files.

## 8. Run the project locally with Docker

1.  Install Docker Engine and the Docker Compose plugin.
2.  Clone the repository and switch to `develop`.
3.  Create active environment files from the examples:

```bash
cp .env.docker.example .env.docker
cp drive_service/.env.docker.example drive_service/.env.docker
```

4.  Edit the two files and supply real application secrets and API
    credentials. Generate strong unique values for Django secret, Fernet
    key and OAuth state signing secret.
5.  Build and start the services:

```bash
docker compose up --build -d
```

6.  Apply database migrations:

```bash
docker compose exec django python manage.py migrate
```

7.  Create an administrator if required:

```bash
docker compose exec django python manage.py createsuperuser
```

8.  Check service status and logs:

```bash
docker compose ps
docker compose logs -f django drive_service celery_worker
```

9.  Open:
    - Frontend: `http://localhost:3000`
    - Django admin: `http://localhost:8000/admin/`
    - FastAPI Swagger: `http://localhost:8001/docs`
10. Test signup, OTP, login, upload, processing status, chat, search and
    Drive connection separately.

Stop the stack:

```bash
docker compose down
```

Stop and remove local database/media volumes only when you intentionally
want to erase local data:

```bash
docker compose down -v
```
