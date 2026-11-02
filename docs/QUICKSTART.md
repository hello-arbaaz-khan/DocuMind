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
