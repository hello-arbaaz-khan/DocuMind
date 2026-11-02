### 4.2 Manual document upload and indexing

```text
React upload component
        |
        v
POST /api/v1/documents
        |
        v
FastAPI documents router
  - validates extension and size
  - calculates SHA-256
  - checks duplicate for this user
  - saves UploadedDocument through Django ORM
        |
        v
Celery process_document_task.delay(document_id)
        |
        v
Workflow.documents.DocumentProcessingWorkflow
        |
        +--> RagCore IngestionPipeline
        |
        +--> RagCore ChunkingPipeline
        |
        +--> RagCore EmbeddingPipeline
        |
        v
Workflow.documents.ChunkPersistenceService
        |
        v
PostgreSQL UploadedDocument + DocumemtsChunk rows
        |
        v
is_processed = True
```

Important implementation details:

- The upload route is `POST /api/v1/documents` and returns
  `202 Accepted` when the task is queued.
- The upload size limit in the FastAPI document router is 50 MB.
- A SHA-256 hash is used for per-user duplicate detection.
- The document task retries exceptions with exponential backoff and up
  to three retries.
- Processing status and errors are stored on `UploadedDocument`.
- `ChunkPersistenceService` checks that chunk and embedding counts
  match and that embeddings have 384 dimensions.
- Reprocessing deletes the document's previous chunk rows and replaces
  them inside a database transaction.
- The embedding configuration uses
  `sentence-transformers/all-MiniLM-L6-v2`.

### 4.3 Asking a question in a conversation

```text
React ChatArea
    |
    v
POST /api/v1/chat/conversations/{id}/messages
    |
    v
FastAPI chat router
  - validates conversation ownership
  - checks attached documents belong to the user
  - checks documents are processed
    |
    v
ChatQueryWorkflow
    |
    v
RagCore Agent
  1. Planner: decide one or multiple searches
  2. Executor: run document search tool(s)
  3. Query pipeline: normalize query
  4. Embedding provider: embed the query
  5. Retrieval: vector + lexical/hybrid retrieval
  6. Reranking: score and select best candidates
  7. ContextBuilder: assemble evidence
  8. GenerationPipeline: call configured LLM
    |
    v
Persist user and assistant ChatMessage rows
    |
    v
Return answer to React
```

The agent defaults shown in `RagCore/Agent/agent.py` are retrieval top-k
20, reranking top-k 5, maximum steps 5 and maximum subqueries 5. The
planner avoids unnecessary multi-query planning for simple questions and
can use conversation context to resolve follow-up references.

The generation prompt instructs the model to ground factual answers in
retrieved document evidence, acknowledge insufficient evidence, and
treat document text as evidence rather than instructions.

### 4.4 Search

`GET /api/v1/search` supports two modes:

- **Metadata browse:** filters the authenticated user's documents by
  upload date and file type, with ordering and pagination.
- **Content search:** uses the document search service. The current
  implementation combines embedding/vector retrieval with PostgreSQL
  full-text search and includes exact filename handling. It returns
  document results, relevance information and snippets where
  available; it does not generate a chat answer.
