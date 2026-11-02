# Deployment notes

This page is a production-readiness checklist, not a provider-specific
deployment recipe. The reviewed Compose setup is intended for development
and must not be exposed to the public internet unchanged.

## Before deployment

- Choose a hosting provider and define how frontend, Django, FastAPI,
  Celery worker, PostgreSQL, and Redis will run.
- Use production environment variables and strong unique secrets.
- Set `DEBUG=False`; configure `ALLOWED_HOSTS`, CORS, CSRF trusted origins,
  secure cookies, and HTTPS for the real public domains.
- Use a production application server for Django rather than `runserver`.
- Configure reliable email delivery for signup/password OTP flows.
- Configure persistent PostgreSQL storage and persistent uploaded-media
  storage. Define and test backups and restores.
- Ensure the Celery worker and Redis are running and monitored.
- Configure logging, health checks, error monitoring, and resource limits.
- Configure Google OAuth with the exact public HTTPS callback URL.
- Review API authentication, user-level authorization, file validation,
  rate limits, and secret handling before opening the service publicly.

## Release sequence

1. Prepare production environment variables and managed secrets.
2. Provision PostgreSQL with pgvector and Redis.
3. Provision persistent media/object storage and backups.
4. Build and deploy backend services and frontend.
5. Run database migrations as a controlled release step.
6. Start/verify the Celery worker.
7. Configure public HTTPS URLs and Google OAuth redirect URI.
8. Run smoke tests: signup, OTP, login, upload, processing, chat, search,
   Drive connect/sync, and document deletion.
9. Verify logs, backups, and rollback procedure.

## CI is not deployment

The reviewed `.github/workflows/ci.yml` runs tests. It does not publish
container images or deploy the application. Add a CD workflow only after
choosing the hosting provider, image registry, secret strategy, and
deployment/rollback process.
