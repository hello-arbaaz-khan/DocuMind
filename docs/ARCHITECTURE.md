## 1. What DocuMind does

DocuMind is a document-grounded AI assistant. A user can create an
account, upload documents or connect a Google Drive account, organize
documents into conversations, ask questions about selected documents,
search document metadata and content, and receive answers generated from
retrieved document passages.

The application is composed of several cooperating services:

- **React + Vite:** browser interface.
- **Django + Django REST Framework:** user accounts, OTP/email flows,
  JWT issuance, Django ORM models and database ownership.
- **FastAPI:** main API for documents, conversations/chat, search and
  Google Drive.
- **Celery + Redis:** asynchronous document processing and Drive
  synchronization.
- **PostgreSQL + pgvector:** application data, document chunks and
  vector embeddings.
- **RagCore:** reusable ingestion, chunking, embedding, retrieval,
  reranking, context and answer-generation components.
- **Google Drive API:** per-user Drive authorization, listing,
  download/export and synchronization.
- **Groq / configured LLM provider:** answer generation; model and key
  are configured through environment variables.

## 2. Repository structure

```text
DocuMind/
├── .github/
│   └── workflows/
│       └── ci.yml                 # GitHub Actions test workflow
├── apps/
│   ├── auth_manager/               # Custom user, signup, OTP, JWT, password flows
│   ├── chat/                       # Conversation, document links, chat messages
│   ├── documents/                  # UploadedDocument, chunks, tasks, search
│   ├── drive/                      # Drive-related Django persistence/API support
│   ├── integrations/               # Integration models and views
│   ├── rag/                        # Earlier/other RAG service modules and commands
│   └── shared/                     # Shared response helpers
├── core/
│   ├── settings.py                 # Django settings and database/JWT/Celery config
│   ├── urls.py                     # Django URL routing
│   ├── celery.py                   # Celery application
│   ├── asgi.py
│   └── wsgi.py
├── RagCore/
│   ├── Agent/                      # Planner, executor, state and agent orchestration
│   ├── Chunking/                   # Chunk data, parsing and splitting
│   ├── Context/                    # Retrieved-context construction
│   ├── Embeddings/                 # Embedding config, providers and pipeline
│   ├── ErrorsHandle/               # Domain/integration exceptions
│   ├── Evaluation/                 # Evaluation datasets, judges and reports
│   ├── Generation/                 # LLM generation pipeline/providers
│   ├── Ingestion/                  # File extraction and ingestion pipeline
│   ├── Query/                      # Query normalization and pipeline
│   ├── Reranking/                  # Candidate scoring and reranking
│   └── Retrieval/                  # Vector, lexical and hybrid retrieval
├── Workflow/
│   ├── documents/                  # Coordinates ingestion through persistence
│   └── chat/                       # Connects conversations to RagCore Agent
├── drive_service/
│   ├── app/
│   │   ├── Apis/routers/            # FastAPI documents/chat/drive/search routes
│   │   ├── Apis/schemas/            # Pydantic request/response schemas
│   │   ├── Apis/services/           # API-level workflow construction
│   │   ├── core/                    # JWT, encryption and OAuth state helpers
│   │   ├── db/                      # SQLAlchemy session
│   │   ├── models/                  # Google Drive account model
│   │   └── services/                # Google Drive client and sync logic
│   ├── main.py                     # FastAPI application entry point
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/              # Auth, chat, documents, Drive, search, sidebar
│   │   ├── context/                 # Auth, app and theme state
│   │   ├── hooks/                   # Drive and polling hooks
│   │   ├── router/                  # Protected routes and page mapping
│   │   └── services/                # Axios API clients
│   ├── public/icons/
│   ├── package.json
│   ├── vite.config.js
│   └── Dockerfile
├── db-image/                        # PostgreSQL + pgvector image
├── db-init/                         # Database initialization SQL
├── docs/                            # Project documentation and diagrams
├── Dockerfile                       # Django/Celery Python image
├── docker-compose.yml               # Local multi-service stack
├── manage.py
├── requirements.txt
└── pytest.ini
```

### Architectural ownership

A useful way to understand the code is to follow the boundaries:

- `apps/` owns Django persistence, user ownership, API-facing
  application data and Celery tasks.
- `RagCore/` contains the reusable RAG/AI logic. It should not need to
  know about Django HTTP views.
- `Workflow/` is the integration layer: it connects Django models and
  tasks to RagCore pipelines.
- `drive_service/` exposes FastAPI endpoints and Google Drive
  integration. It imports the Django project/models and therefore runs
  with the shared project code and settings.
- `frontend/` calls the two backend URL namespaces through Vite's
  development proxy.

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

## 6. Frontend structure and navigation

The React app entry points are `frontend/src/main.jsx`, `Root.jsx` and
`App.jsx`.

- `Root.jsx` defines public-only authentication routes and protected
  application routes.
- `router/pages.jsx` maps routes to Dashboard, ChatArea,
  DocumentsView, AdvancedSearch and Settings screens.
- `context/AuthContext.jsx` manages authentication state.
- `context/AppContext.jsx` manages application-level state.
- `context/ThemeContext.jsx` manages light/dark theme state.
- `services/authApi.js` calls Django authentication endpoints.
- `services/api.js` calls FastAPI `/api/v1/` endpoints and attaches
  the access token.
- `vite.config.js` proxies `/api/auth` to Django and `/api/v1` to
  FastAPI.

Main application routes include `/dashboard`, `/new`,
`/chat/:conversationId`, `/documents`, `/search` and `/settings`.
Authentication routes include `/login`, `/signup`, `/verify-otp`,
`/forgot-password` and `/reset-password`. `/drive/callback` handles the
Drive OAuth redirect.
