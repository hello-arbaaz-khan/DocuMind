# DocuMind AI documentation

Welcome to the developer documentation for **DocuMind AI**.

This folder explains the current project architecture, API surface, RAG pipeline,
Google Drive integration, local setup, development workflow, tests, and deployment
considerations.

## Documentation

| File | Purpose |
|---|---|
| [Architecture](ARCHITECTURE.md) | Services, repository layout, responsibilities, and request flow |
| [API reference](API.md) | Django authentication and FastAPI endpoints |
| [Quickstart](QUICKSTART.md) | Start the complete application with Docker |
| [RAG pipeline](RAG_PIPELINE.md) | Upload, indexing, retrieval, and answer generation |
| [Google Drive setup](GOOGLE_DRIVE_SETUP.md) | OAuth, per-user authorization, and synchronization |
| [Environment variables](ENVIRONMENT.md) | Configuration files and important variables |
| [Docker setup](DOCKER_SETUP.md) | Container networking, commands, and troubleshooting basics |
| [Development guide](DEVELOPMENT_GUIDE.md) | Code ownership, local development, and recommended reading order |
| [Testing and CI](TESTING.md) | Run tests and understand GitHub Actions |
| [Deployment notes](DEPLOYMENT.md) | Production-readiness requirements and deployment checklist |
| [Review notes](REVIEW_NOTES.md) | Known documentation/code observations from the reviewed branch |

## Project at a glance

DocuMind AI is a document-grounded assistant. The frontend is React/Vite.
Django handles authentication and shared persistence; FastAPI exposes the
main document, conversation, search, and Drive APIs. Celery/Redis run
background work. PostgreSQL with pgvector stores application data and
document embeddings. `RagCore/` contains reusable RAG components.

## Start here

1. Read [Architecture](ARCHITECTURE.md).
2. Follow [Quickstart](QUICKSTART.md).
3. Read [Development guide](DEVELOPMENT_GUIDE.md).
4. Use [API reference](API.md) and [RAG pipeline](RAG_PIPELINE.md) when
   changing application behavior.

## Documentation maintenance

Update the relevant page whenever an API route, environment variable,
background task, service, or user-facing workflow changes. Keep examples
free of real credentials. These docs describe the reviewed `develop`
branch; they are not a production security certification.
