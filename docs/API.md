## 5. API route reference

Base URLs in local development:

- Django authentication: `http://localhost:8000`
- FastAPI application API: `http://localhost:8001`
- FastAPI interactive docs: `http://localhost:8001/docs`

### Authentication --- Django

---

Method Route Purpose

---

POST `/api/auth/signup/` Create pending account
and send OTP

POST `/api/auth/signup/verify-otp/` Verify signup OTP and
activate account

POST `/api/auth/signup/resend-otp/` Resend signup OTP

POST `/api/auth/login/` Sign in and issue
tokens

POST `/api/auth/password/forgot/` Start password reset

POST `/api/auth/password/reset/` Reset password

POST `/api/auth/password/change/` Change password

POST `/api/auth/verify-otp/` Generic OTP
verification

POST `/api/auth/token/refresh/` Refresh access token

---

### Documents --- FastAPI

---

Method Route Purpose

---

POST `/api/v1/documents` Upload and queue
indexing

GET `/api/v1/documents` List current user's
documents

GET `/api/v1/documents/{document_id}` Get document and
processing status

DELETE `/api/v1/documents/{document_id}` Delete an owned
document

---

### Conversations and chat --- FastAPI

---

Method Route Purpose

---

POST `/api/v1/chat/conversations` Create conversation;
may attach document IDs

GET `/api/v1/chat/conversations` List current user's
conversations

GET `/api/v1/chat/conversations/{conversation_id}` Get conversation and
attached documents

POST `/api/v1/chat/conversations/{conversation_id}/documents` Attach existing
documents

POST `/api/v1/chat/conversations/{conversation_id}/documents/upload` Upload documents into a
conversation

POST `/api/v1/chat/conversations/{conversation_id}/messages` Send a question and
receive an answer

GET `/api/v1/chat/conversations/{conversation_id}/messages` Read conversation
messages

DELETE `/api/v1/chat/conversations/{conversation_id}` Delete a conversation
(confirm exact behavior
in current router
before client
integration)

---

### Search --- FastAPI

---

Method Route Purpose

---

GET `/api/v1/search` Browse/filter documents
or search their content

---

Typical query parameters include `query`, `uploaded_after`,
`uploaded_before`, `file_type`, `order_by`, `order`, `limit` and
`offset`.

### Google Drive --- FastAPI

---

Method Route Purpose

---

GET `/api/v1/drive/connect` Generate Google
authorization URL

GET `/api/v1/drive/status` Check current user's
Drive connection

GET `/api/v1/drive/callback` OAuth callback

DELETE `/api/v1/drive/disconnect` Disconnect account

POST `/api/v1/drive/sync` Queue Drive
synchronization

GET `/api/v1/drive/files` List Drive files

GET `/api/v1/drive/files/{file_id}/download` Download file content

---

All protected FastAPI endpoints require the Django-issued bearer access
token. The OAuth callback is validated using its signed state rather
than a normal logged-in browser request.
