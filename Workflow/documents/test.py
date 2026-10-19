from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.files import File
from django.test import TestCase

from apps.documents.models import DocumemtsChunk, UploadedDocument
from RagCore.ErrorsHandle.exceptions import IntegrationError
from Workflow.documents.document_processing import DocumentProcessingWorkflow


User = get_user_model()

# Project layout:
# /app/
#   Workflow/documents/test.py
#   RagCore/Fixtures/
FIXTURES_DIR = (
    Path(__file__).resolve().parents[2]
    / "RagCore"
    / "Fixtures"
)

PDF_FIXTURE = FIXTURES_DIR / "Pdf_samples" / "sample.pdf"

TWO_PAGE_PDF_FIXTURE = (
    FIXTURES_DIR
    / "Pdf_samples"
    / "sample_two_pages.pdf"
)

DOCX_FIXTURE = (
    FIXTURES_DIR
    / "Docx_samples"
    / "sample.docx"
)


class DocumentProcessingWorkflowIntegrationTests(TestCase):
    """
    Real integration tests for the complete document-processing workflow.

    These tests do not mock RagCore components.

    UploadedDocument
        -> DocumentProcessingWorkflow
        -> IngestionPipeline
        -> ChunkingPipeline
        -> EmbeddingPipeline
        -> ChunkPersistenceService
        -> Django PostgreSQL / pgvector
    """

    def setUp(self):
        self.user = self._create_test_user()
        self.workflow = DocumentProcessingWorkflow()

    def _create_test_user(self):
        if User.USERNAME_FIELD == "email":
            return User.objects.create_user(
                email="workflow-real-test@example.com",
                password="test-password",
            )

        username_field = User._meta.get_field(User.USERNAME_FIELD)

        return User.objects.create_user(
            **{
                username_field.name: "workflow-real-test",
                "password": "test-password",
            }
        )

    def _create_document(
        self,
        fixture_path: Path,
        file_type: str,
    ) -> UploadedDocument:
        self.assertTrue(
            fixture_path.is_file(),
            f"Real fixture does not exist: {fixture_path}",
        )

        with fixture_path.open("rb") as file_handle:
            django_file = File(
                file_handle,
                name=fixture_path.name,
            )

            return UploadedDocument.objects.create(
                user=self.user,
                name=fixture_path.name,
                file=django_file,
                file_type=file_type,
                file_size=fixture_path.stat().st_size,
            )

    def _assert_successful_processing(
        self,
        document: UploadedDocument,
    ):
        document.refresh_from_db()

        self.assertTrue(
            document.is_processed,
            "Document should be marked as processed.",
        )
        self.assertFalse(
            document.processing_error,
            "Successful processing must not contain an error.",
        )
        self.assertIsNotNone(
            document.processing_started_at,
            "Processing timestamp should be recorded.",
        )

        chunks = list(
            DocumemtsChunk.objects.filter(
                document=document
            ).order_by("chunks_index")
        )

        self.assertGreater(
            len(chunks),
            0,
            "Real document processing must create at least one chunk.",
        )

        return chunks

    def _assert_valid_chunks(self, chunks):
        for expected_index, chunk in enumerate(chunks):
            self.assertEqual(
                chunk.chunks_index,
                expected_index,
            )
            self.assertTrue(
                chunk.chunks_text,
                "Persisted chunk text must not be empty.",
            )
            self.assertIsNotNone(
                chunk.embedding,
                "Every persisted chunk must have an embedding.",
            )
            self.assertEqual(
                len(chunk.embedding),
                384,
                "Every embedding must contain exactly 384 dimensions.",
            )

    def test_real_pdf_is_processed_and_persisted(self):
        """Verify the complete real PDF processing pipeline."""
        document = self._create_document(
            fixture_path=PDF_FIXTURE,
            file_type="pdf",
        )

        result = self.workflow.process(document.pk)

        self.assertEqual(result.pk, document.pk)

        chunks = self._assert_successful_processing(document)
        self._assert_valid_chunks(chunks)

    def test_real_two_page_pdf_is_processed(self):
        """Verify multi-page PDF extraction, chunking and persistence."""
        document = self._create_document(
            fixture_path=TWO_PAGE_PDF_FIXTURE,
            file_type="pdf",
        )

        self.workflow.process(document.pk)

        chunks = self._assert_successful_processing(document)
        self._assert_valid_chunks(chunks)

        page_numbers = {
            chunk.page_number
            for chunk in chunks
            if chunk.page_number is not None
        }

        self.assertGreaterEqual(
            len(page_numbers),
            1,
            "Expected persisted chunks to include page metadata.",
        )

    def test_real_docx_is_processed_and_persisted(self):
        """Verify the complete real DOCX processing pipeline."""
        document = self._create_document(
            fixture_path=DOCX_FIXTURE,
            file_type="docx",
        )

        result = self.workflow.process(document.pk)

        self.assertEqual(result.pk, document.pk)

        chunks = self._assert_successful_processing(document)
        self._assert_valid_chunks(chunks)

    def test_real_processing_persists_correct_chunk_count(self):
        """Verify that processing persists chunks with embeddings."""
        document = self._create_document(
            fixture_path=PDF_FIXTURE,
            file_type="pdf",
        )

        self.workflow.process(document.pk)

        chunks = list(
            DocumemtsChunk.objects.filter(
                document=document
            ).order_by("chunks_index")
        )

        self.assertGreater(len(chunks), 0)
        self._assert_valid_chunks(chunks)

    def test_real_reprocessing_replaces_existing_chunks(self):
        """Verify that reprocessing does not leave stale chunks."""
        document = self._create_document(
            fixture_path=PDF_FIXTURE,
            file_type="pdf",
        )

        self.workflow.process(document.pk)

        first_chunks = list(
            DocumemtsChunk.objects.filter(
                document=document
            ).order_by("chunks_index")
        )

        self.assertGreater(len(first_chunks), 0)
        first_count = len(first_chunks)

        self.workflow.process(document.pk)

        second_chunks = list(
            DocumemtsChunk.objects.filter(
                document=document
            ).order_by("chunks_index")
        )

        self.assertGreater(len(second_chunks), 0)
        self.assertEqual(len(second_chunks), first_count)
        self._assert_valid_chunks(second_chunks)

    def test_missing_real_file_fails_without_persisting_chunks(self):
        """
        Verify the missing-file error path using a real document record.
        """
        document = self._create_document(
            fixture_path=PDF_FIXTURE,
            file_type="pdf",
        )

        file_path = Path(document.file.path)
        self.assertTrue(file_path.is_file())

        file_path.unlink()

        with self.assertRaises(IntegrationError):
            self.workflow.process(document.pk)

        document.refresh_from_db()

        self.assertFalse(document.is_processed)
        self.assertTrue(document.processing_error)
        self.assertEqual(
            DocumemtsChunk.objects.filter(
                document=document
            ).count(),
            0,
        )

    def test_real_embeddings_are_384_dimensions(self):
        """Verify real embedding vectors match the 384-dimension schema."""
        document = self._create_document(
            fixture_path=PDF_FIXTURE,
            file_type="pdf",
        )

        self.workflow.process(document.pk)

        chunks = list(
            DocumemtsChunk.objects.filter(
                document=document
            ).order_by("chunks_index")
        )

        self.assertGreater(len(chunks), 0)

        for chunk in chunks:
            self.assertIsNotNone(chunk.embedding)
            self.assertEqual(len(chunk.embedding), 384)