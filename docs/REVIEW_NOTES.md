## 11. Important implementation notes and review findings

These are observations from reading the code, not assumptions about how
the application behaves in a deployed environment.

1.  **The existing architecture document is stale.** It contains legacy
    references to ChromaDB, SQLite, old endpoint shapes and old security
    status. The current code uses PostgreSQL/pgvector, JWT
    authentication, user-owned records and FastAPI routes. Update
    `docs/ARCHITECTURE.md` to avoid misleading contributors.
2.  **The README title still says "Rag-Agent (DocuMind)".** The
    product-facing name is DocuMind AI; consider making repository
    documentation consistent with the product name.
3.  **Compose is development-oriented.** The Django service starts with
    `runserver`; `DEBUG=True` appears in the Docker example; local
    default database credentials are visible in Compose examples. Do not
    expose this configuration as-is to the public internet.
4.  **Production settings need a deployment pass.** Review
    `ALLOWED_HOSTS`, CORS, CSRF trusted origins, secure cookies, HTTPS,
    email delivery, static/media storage, database credentials, secret
    management and logging for the actual production domain.
5.  **OAuth deployment needs public callback URLs.** The Google OAuth
    redirect URI must exactly match the deployed FastAPI callback URL.
    The frontend redirect URL must also be configured correctly.
    Localhost/container URLs cannot be used as public production
    callbacks.
6.  **Persistent storage is essential.** Back up PostgreSQL and preserve
    uploaded media. A container filesystem alone is not a safe place for
    user documents.
7.  **CI is not CD.** Tests passing does not mean an image has been
    published or a server has been deployed.
8.  **Frontend navigation deserves a small code review.** In
    `frontend/src/router/paths.js`, the `useViewNavigate` switch
    currently has a fall-through from the `chat`/`default` case into the
    `dashboard` case. Verify and correct this before relying on sidebar
    navigation to the new-chat screen.
9.  **Documentation/API drift should be checked when endpoints change.**
    The current chat implementation is conversation-based. Older API
    documentation describes a simpler document-specific chat endpoint.
    Keep route tables aligned with the FastAPI router.
10. **Some root-level Django app modules coexist with the newer FastAPI
    router layer.** When adding endpoints, trace the actual frontend
    call, FastAPI router, workflow/task and model rather than assuming a
    Django view is active just because a Django app exists.

## 13. Suggested next documentation and release tasks

- Replace the stale `docs/ARCHITECTURE.md` with a diagram of the
  current Django + FastAPI + Celery + PostgreSQL/pgvector
  architecture.
- Update `docs/API.md` from the actual FastAPI route definitions,
  especially conversation endpoints.
- Add a dedicated Google OAuth setup guide covering local and deployed
  callback URLs, consent screen status, scopes and per-user
  authorization.
- Add a production deployment guide with environment variables,
  persistent volumes, database migration, HTTPS, worker process and
  rollback steps.
- Add `CONTRIBUTING.md` and a license after choosing the intended
  license.
- Add a CD workflow only after choosing a hosting provider and
  defining image registry, secrets and deployment strategy.
- Fix and test the `useViewNavigate` case fall-through.
