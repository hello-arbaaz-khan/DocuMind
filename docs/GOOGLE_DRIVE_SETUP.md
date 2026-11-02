> Reviewed against `hello-arbaaz-khan/DocuMind`, branch `develop`, commit `72d6365f1547d729a5310672477b764efde4a795` (2 November 2026). Re-check source code when routes or implementation change.

### 4.5 Google Drive connection and sync

``` text
React Settings -> Connect Google Drive
        |
        v
GET /api/v1/drive/connect (JWT required)
        |
        v
FastAPI creates OAuth URL and signed one-time state
        |
        v
Google consent screen
        |
        v
GET /api/v1/drive/callback (state/code)
        |
        v
Validate and consume state; exchange OAuth code
        |
        v
Encrypt and save user's Drive tokens
        |
        v
Queue sync_google_drive_task(user_id)
        |
        v
List/download/export supported Drive files
        |
        v
Create/update UploadedDocument records
        |
        v
Queue process_document_task for imported files
        |
        v
Normal ingestion -> chunking -> embeddings -> pgvector
```

Drive authorization is per application user. The Google OAuth client
ID/secret belong to the application configuration; each user authorizes
their own Google account. The code uses Drive read-only scope plus
OpenID/email scopes. Tokens are encrypted before storage. OAuth state is
signed and stored/consumed to protect the callback flow.

Google Docs, Sheets and Slides are exported to supported formats. The
sync implementation skips Google Workspace exports exceeding the Drive
API's 10 MB export limit.

## OAuth configuration checklist

- Create/configure the OAuth client in the Google Cloud project.
- Add the exact callback URL used by the deployed FastAPI service to the
  OAuth client's authorized redirect URIs.
- Configure the matching frontend URL and backend base URLs in the
  environment files.
- Keep the client secret and token-encryption/signing secrets private.
- Each application user must authorize their own Google account.
- During Google OAuth app testing, only configured test users can authorize.
  Publishing/verifying the OAuth app is a separate Google Cloud process.

Do not use Docker service names such as `drive_service` as public Google
redirect URLs. Google must be able to reach the callback over the public
HTTPS URL of the deployed service.
