> Reviewed against `hello-arbaaz-khan/DocuMind`, branch `develop`, commit `72d6365f1547d729a5310672477b764efde4a795` (2 November 2026). Re-check source code when routes or implementation change.

## 7. Environment configuration

Use the example files as templates; do not commit real secrets.

  -------------------------------------------------------------------------
  File                                  Used for
  ------------------------------------- -----------------------------------
  `.env.example`                        Local Django/database/Redis/LLM
                                        configuration

  `.env.docker.example`                 Docker Compose Django and service
                                        URLs

  `drive_service/.env.example`          Local Drive service configuration

  `drive_service/.env.docker.example`   Drive service configuration inside
                                        Compose
  -------------------------------------------------------------------------

Important variables include:

-   `SECRET_KEY`, `DEBUG`
-   `GROQ_API_KEY`, `GROQ_MODEL`
-   `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`
-   `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`
-   `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`
-   `FERNET_KEY`, `STATE_SIGNING_SECRET`
-   `DATABASE_URL`, `REDIS_URL`
-   `DJANGO_BASE_URL`, `DRIVE_SERVICE_BASE_URL`, `FRONTEND_BASE_URL`
-   `GOOGLE_REDIRECT_URI` (must match the OAuth redirect URI registered
    in Google Cloud)

For Docker, internal service hostnames must be used. For example, the
Django DB host is `db`, Redis is `redis`, and the Drive service URL is
`http://drive_service:8001`. Do not put `localhost` in a
container-to-container URL unless the target service is in the same
container.
