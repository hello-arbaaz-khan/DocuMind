DocuMind AI
DocuMind AI is a document assistant that lets users upload documents or connect their Google Drive, ask questions about their files, and get answers based on the document content.

The application uses React for the frontend, Django for authentication and user data, FastAPI for document and chat APIs, and a RAG pipeline to find useful information from documents.

This README explains the project, its main folders, and how to run it locally. For more details, see the docs/ directory.
Main features

- Upload PDF, DOCX, DOC, and TXT documents
- Connect a personal Google Drive account
- Extract text and split documents into smaller chunks
- Generate embeddings using Sentence Transformers
- Store document data and embeddings in PostgreSQL with pgvector
- Ask questions about documents in conversations
- Get answers with source information from retrieved document content
- Search documents by content and metadata
- Process documents in the background using Celery and Redis
- Sign up and log in using JWT authentication and OTP verification
- Use light and dark themes in the frontend
  How the project works

1. A user signs up or logs in from the React frontend.
2. Django handles authentication and creates access tokens.
3. The user uploads documents or connects Google Drive.
4. FastAPI receives document and chat requests.
5. Celery processes documents in the background.
6. The RAG pipeline extracts text, creates chunks, and generates embeddings.
7. Document chunks and embeddings are stored in PostgreSQL with pgvector.
8. When the user asks a question, the system searches the selected documents and sends the retrieved context to the configured LLM.
9. The frontend displays the answer and its source information.
   Repository structure
   DocuMind/
   ├── apps/
   │ ├── auth_manager/ # Signup, login, OTP, JWT and user accounts
   │ ├── chat/ # Conversations and chat messages
   │ ├── documents/ # Documents, chunks, search and background tasks
   │ ├── drive/ # Google Drive related database support
   │ ├── integrations/ # Integration support
   │ └── shared/ # Shared helpers
   ├── core/ # Django settings, URLs and Celery setup
   ├── RagCore/ # RAG, ingestion, embeddings, retrieval and generation
   ├── Workflow/ # Document processing and chat workflows
   ├── drive_service/ # FastAPI APIs and Google Drive integration
   ├── frontend/ # React and Vite application
   ├── db-image/ # PostgreSQL image with pgvector
   ├── db-init/ # Database initialization files
   ├── docs/ # Project documentation
   ├── .github/workflows/ # GitHub Actions CI workflow
   ├── docker-compose.yml # Local services
   ├── Dockerfile # Django and Celery image
   ├── manage.py
   ├── requirements.txt
   └── pytest.ini
   Main technologies

- Python 3.12
- Django and Django REST Framework
- FastAPI
- React and Vite
- PostgreSQL and pgvector
- Celery and Redis
- Sentence Transformers
- Google Drive API
- Groq or another configured LLM provider
- Docker and Docker Compose
- pytest and GitHub Actions
  Requirements
  To run the complete project locally, you need:
- Docker Engine and Docker Compose plugin
- Git
- Google OAuth credentials for Google Drive features
- An LLM API key for AI answer generation
  For running services without Docker, you also need Python 3.12, Node.js/npm, PostgreSQL with pgvector, and Redis.
  Quickstart with Docker

1. Clone the repository
   git clone https://github.com/hello-arbaaz-khan/DocuMind.git
   cd DocuMind
   git checkout develop
2. Create environment files
   cp .env.docker.example .env.docker
   cp drive_service/.env.docker.example drive_service/.env.docker
   Open both files and add the required values. Configure your database, Redis, LLM API key, Google OAuth credentials, and application secrets.

Do not commit real passwords, API keys, OAuth secrets, or encryption keys to GitHub. 3. Build and start the services
docker compose up --build -d 4. Run database migrations
docker compose exec django python manage.py migrate 5. Create an admin account (optional)
docker compose exec django python manage.py createsuperuser 6. Check running services
docker compose ps
To view logs:
docker compose logs -f django drive_service celery_worker 7. Open the application

- Frontend: http://localhost:3000
- Django admin: http://localhost:8000/admin/
- FastAPI documentation: http://localhost:8001/docs
  Docker Compose starts the frontend, Django, FastAPI, PostgreSQL, Redis, and Celery worker services.
  Run without Docker
  You need Python 3.12, Node.js/npm, PostgreSQL with pgvector, and Redis installed and running.

1. Create a Python environment
   python -m venv .venv
   source .venv/bin/activate
2. Install Python dependencies
   pip install -r requirements.txt
   pip install -r drive_service/requirements.txt
3. Configure environment files
   Create .env and drive_service/.env using the matching example files. Set the database and Redis connection details for your local services.
4. Run database migrations
   python manage.py migrate
5. Start Django
   python manage.py runserver 0.0.0.0:8000
6. Start the Celery worker
   Open another terminal, activate the same virtual environment, and run:
   celery -A core worker -l info
7. Start the FastAPI service
   Open another terminal:
   cd drive_service
   PYTHONPATH=.. uvicorn main:app --host 0.0.0.0 --port 8001
8. Start the frontend
   Open another terminal:
   cd frontend
   npm install
   npm run dev
   Open http://localhost:3000 in your browser.
   API services
   The project has two backend services:

- Django: authentication, OTP, JWT tokens, and Django application data.
- FastAPI: document upload, conversations, chat, search, and Google Drive APIs.
  Useful local URLs:
- Django API base: http://localhost:8000
- FastAPI API base: http://localhost:8001
- FastAPI Swagger UI: http://localhost:8001/docs
  Protected FastAPI endpoints use the access token issued by Django.
  Google Drive setup
  Google Drive connection uses Google OAuth. The application has its own OAuth client credentials, but each user connects and authorizes their own Google account.

For local development:

1. Create or select a project in Google Cloud Console.
2. Configure the OAuth consent screen.
3. Add your Google account as a test user while the app is in Testing mode.
4. Create OAuth credentials and set the client ID and secret in the environment files.
5. Set the redirect URI to the callback URL used by your local Drive service.
   For deployment, configure the public HTTPS callback URL in both the application settings and Google Cloud Console. The redirect URI must match exactly.

See docs/GOOGLE_DRIVE_SETUP.md for more details.
Environment files
Use the example files as templates:

- .env.example — local Django and shared application settings
- .env.docker.example — Docker Compose settings
- drive_service/.env.example — local FastAPI/Drive service settings
- drive_service/.env.docker.example — Docker Drive service settings
  The application needs values for Django secrets, database and Redis connections, the LLM provider, Google OAuth, and token encryption/signing.

Use Docker service names such as db and redis for connections between containers. Do not use localhost for another container.
Testing
Run the project tests with:
PYTHONPATH=. python -m pytest
Run Django system checks with:
python manage.py check
The GitHub Actions workflow is in .github/workflows/ci.yml. It runs tests for pushes and pull requests targeting main and develop.
Documentation
More project guides are available in the docs/ directory:

- docs/README.md — documentation index
- docs/ARCHITECTURE.md — project architecture and services
- docs/API.md — API routes
- docs/QUICKSTART.md — Docker quickstart
- docs/RAG_PIPELINE.md — document processing and question-answer flow
- docs/GOOGLE_DRIVE_SETUP.md — Google Drive OAuth and sync
- docs/ENVIRONMENT.md — environment variables
- docs/DOCKER_SETUP.md — Docker setup
- docs/DEVELOPMENT_GUIDE.md — development guide
- docs/TESTING.md — tests and CI
- docs/DEPLOYMENT.md — deployment checklist
- docs/REVIEW_NOTES.md — implementation review notes
  Contributing
  Contributions are welcome.

1. Fork the repository.
2. Create a new branch:
   git checkout -b feature/your-feature
3. Make your changes and run the tests.
4. Commit your changes with a clear message.
5. Open a Pull Request.
   License
   This repository currently does not include a LICENSE file. Add a license file if you want to define the terms for using and contributing to this project.
   Author
   Arbaz Khan — https://github.com/hello-arbaaz-khan
