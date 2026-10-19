import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from RagCore.Ingestion.pipeline import IngestionPipeline
from RagCore.Chunking.pipeline import ChunkingPipeline
from RagCore.Embeddings.embedding import EmbeddingConfig,EmbeddingResult
from RagCore.Embeddings.pipeline import EmbeddingPipeline
from RagCore.Embeddings.provider import SentenceTransformerProvider
import pytest
from pydantic import ValidationError

from RagCore.Chunking.chunk import Chunk
from RagCore.ErrorsHandle.exceptions import EmbeddingError

FIXTURES_DIR = Path(__file__).parent / "Fixtures"
PDF_DIR = FIXTURES_DIR / "Pdf_samples"
DOCX_DIR = FIXTURES_DIR / "Docx_samples"


def get_pdf_files():
    return sorted(PDF_DIR.glob("*.pdf"))


def get_docx_files():
    return sorted(DOCX_DIR.glob("*.docx"))


@pytest.fixture(scope="module")
def embedding_pipeline():
    config = EmbeddingConfig(
        model="sentence-transformers/all-mpnet-base-v2"
    )
    provider = SentenceTransformerProvider(config)
    return EmbeddingPipeline(provider, config)


@pytest.fixture(scope="module")
def chunks_for_documents():
    ingestion_pipeline = IngestionPipeline()
    chunking_pipeline = ChunkingPipeline()

    def build_chunks(file_path: Path):
        document = ingestion_pipeline.run(
            str(file_path),
            document_id="test-document",
        )

        return chunking_pipeline.process(document)

    return build_chunks


@pytest.mark.parametrize("file_path", get_pdf_files())
def test_real_pdf_embedding(
    file_path,
    chunks_for_documents,
    embedding_pipeline,
):
    chunks = chunks_for_documents(file_path)

    assert chunks

    results = embedding_pipeline.process(chunks)

    assert results
    assert len(results) == len(chunks)


@pytest.mark.parametrize("file_path", get_docx_files())
def test_real_docx_embedding(
    file_path,
    chunks_for_documents,
    embedding_pipeline,
):
    chunks = chunks_for_documents(file_path)

    assert chunks

    results = embedding_pipeline.process(chunks)

    assert results
    assert len(results) == len(chunks)


@pytest.mark.parametrize("file_path", get_pdf_files())
def test_real_pdf_embedding_dimensions(
    file_path,
    chunks_for_documents,
    embedding_pipeline,
):
    chunks = chunks_for_documents(file_path)

    results = embedding_pipeline.process(chunks)

    assert all(result.dimensions == 768 for result in results)
    assert all(len(result.embedding) == 768 for result in results)


@pytest.mark.parametrize("file_path", get_docx_files())
def test_real_docx_embedding_dimensions(
    file_path,
    chunks_for_documents,
    embedding_pipeline,
):
    chunks = chunks_for_documents(file_path)

    results = embedding_pipeline.process(chunks)

    assert all(result.dimensions == 768 for result in results)
    assert all(len(result.embedding) == 768 for result in results)


@pytest.mark.parametrize("file_path", get_pdf_files())
def test_real_pdf_embedding_metadata(
    file_path,
    chunks_for_documents,
    embedding_pipeline,
):
    chunks = chunks_for_documents(file_path)

    results = embedding_pipeline.process(chunks)

    assert all(result.chunk_id for result in results)
    assert all(result.document_id == "test-document" for result in results)
    assert all(result.model == "sentence-transformers/all-mpnet-base-v2" for result in results)


@pytest.mark.parametrize("file_path", get_docx_files())
def test_real_docx_embedding_metadata(
    file_path,
    chunks_for_documents,
    embedding_pipeline,
):
    chunks = chunks_for_documents(file_path)

    results = embedding_pipeline.process(chunks)

    assert all(result.chunk_id for result in results)
    assert all(result.document_id == "test-document" for result in results)
    assert all(result.model == "sentence-transformers/all-mpnet-base-v2" for result in results)


@pytest.mark.parametrize("file_path", get_pdf_files())
def test_real_pdf_embedding_values(
    file_path,
    chunks_for_documents,
    embedding_pipeline,
):
    chunks = chunks_for_documents(file_path)

    results = embedding_pipeline.process(chunks)

    for result in results:
        assert result.embedding
        assert all(isinstance(value, float) for value in result.embedding)


@pytest.mark.parametrize("file_path", get_docx_files())
def test_real_docx_embedding_values(
    file_path,
    chunks_for_documents,
    embedding_pipeline,
):
    chunks = chunks_for_documents(file_path)

    results = embedding_pipeline.process(chunks)

    for result in results:
        assert result.embedding
        assert all(isinstance(value, float) for value in result.embedding)




def make_chunk(
    chunk_id="chunk-1",
    document_id="doc-1",
    content="Python is a programming language",
    chunk_index=0,
):
    return Chunk(
        chunk_id=chunk_id,
        document_id=document_id,
        content=content,
        chunk_index=chunk_index,
    )


def test_embedding_config_defaults():
    config = EmbeddingConfig(model="all-MiniLM-L6-v2")

    assert config.model == "all-MiniLM-L6-v2"
    assert config.batch_size == 32
    assert config.normalize_embeddings is False


def test_embedding_config_custom_values():
    config = EmbeddingConfig(
        model="sentence-transformers/all-MiniLM-L6-v2",
        batch_size=16,
        normalize_embeddings=True,
    )

    assert config.model == "sentence-transformers/all-MiniLM-L6-v2"
    assert config.batch_size == 16
    assert config.normalize_embeddings is True


@pytest.mark.parametrize("batch_size", [0, -1])
def test_embedding_config_rejects_invalid_batch_size(batch_size):
    with pytest.raises(ValidationError):
        EmbeddingConfig(
            model="all-MiniLM-L6-v2",
            batch_size=batch_size,
        )


def test_embedding_result():
    result = EmbeddingResult(
        chunk_id="chunk-1",
        document_id="doc-1",
        embedding=[0.1, 0.2, 0.3],
        model="all-MiniLM-L6-v2",
        dimensions=3,
    )

    assert result.chunk_id == "chunk-1"
    assert result.document_id == "doc-1"
    assert result.embedding == [0.1, 0.2, 0.3]
    assert result.model == "all-MiniLM-L6-v2"
    assert result.dimensions == 3


def test_embedding_result_rejects_invalid_dimensions():
    with pytest.raises(ValidationError):
        EmbeddingResult(
            chunk_id="chunk-1",
            document_id="doc-1",
            embedding=[0.1, 0.2, 0.3],
            model="all-MiniLM-L6-v2",
            dimensions=0,
        )


def test_sentence_transformer_provider_initializes_model():
    config = EmbeddingConfig(
        model="sentence-transformers/all-MiniLM-L6-v2"
    )

    with patch(
        "RagCore.Embeddings.provider.SentenceTransformer"
    ) as mock_model:
        SentenceTransformerProvider(config)

        mock_model.assert_called_once_with(
            "sentence-transformers/all-MiniLM-L6-v2"
        )


def test_sentence_transformer_provider_embed():
    config = EmbeddingConfig(
        model="sentence-transformers/all-MiniLM-L6-v2",
        batch_size=16,
        normalize_embeddings=True,
    )

    with patch(
        "RagCore.Embeddings.provider.SentenceTransformer"
    ) as mock_model:
        mock_model.return_value.encode.return_value = MagicMock(
            tolist=lambda: [
                [0.1, 0.2, 0.3],
                [0.4, 0.5, 0.6],
            ]
        )

        provider = SentenceTransformerProvider(config)

        result = provider.embed(
            [
                "Python is a programming language",
                "Django is a web framework",
            ]
        )

        assert result == [
            [0.1, 0.2, 0.3],
            [0.4, 0.5, 0.6],
        ]

        mock_model.return_value.encode.assert_called_once_with(
            [
                "Python is a programming language",
                "Django is a web framework",
            ],
            batch_size=16,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )


def test_sentence_transformer_provider_empty_input():
    config = EmbeddingConfig(
        model="sentence-transformers/all-MiniLM-L6-v2"
    )

    with patch(
        "RagCore.Embeddings.provider.SentenceTransformer"
    ) as mock_model:
        provider = SentenceTransformerProvider(config)

        result = provider.embed([])

        assert result == []
        mock_model.return_value.encode.assert_not_called()


def test_embedding_pipeline_empty_chunks():
    config = EmbeddingConfig(
        model="sentence-transformers/all-MiniLM-L6-v2"
    )
    provider = MagicMock()
    pipeline = EmbeddingPipeline(provider, config)

    result = pipeline.process([])

    assert result == []
    provider.embed.assert_not_called()


def test_embedding_pipeline_ignores_whitespace_chunks():
    config = EmbeddingConfig(
        model="sentence-transformers/all-MiniLM-L6-v2"
    )
    provider = MagicMock()
    provider.embed.return_value = [[0.1, 0.2, 0.3]]

    pipeline = EmbeddingPipeline(provider, config)

    chunks = [
        make_chunk(
            chunk_id="chunk-1",
            content="Python is a programming language",
        ),
        make_chunk(
            chunk_id="chunk-2",
            content="   ",
        ),
    ]

    result = pipeline.process(chunks)

    assert len(result) == 1
    assert result[0].chunk_id == "chunk-1"
    assert result[0].document_id == "doc-1"
    assert result[0].embedding == [0.1, 0.2, 0.3]
    assert result[0].model == "sentence-transformers/all-MiniLM-L6-v2"
    assert result[0].dimensions == 3

    provider.embed.assert_called_once_with(
        ["Python is a programming language"]
    )


def test_embedding_pipeline_creates_results():
    config = EmbeddingConfig(
        model="sentence-transformers/all-MiniLM-L6-v2"
    )
    provider = MagicMock()
    provider.embed.return_value = [
        [0.1, 0.2, 0.3],
        [0.4, 0.5, 0.6],
    ]

    pipeline = EmbeddingPipeline(provider, config)

    chunks = [
        make_chunk(
            chunk_id="chunk-1",
            document_id="doc-1",
            content="Python is a programming language",
            chunk_index=0,
        ),
        make_chunk(
            chunk_id="chunk-2",
            document_id="doc-1",
            content="Django is a web framework",
            chunk_index=1,
        ),
    ]

    result = pipeline.process(chunks)

    assert len(result) == 2

    assert result[0].chunk_id == "chunk-1"
    assert result[0].document_id == "doc-1"
    assert result[0].embedding == [0.1, 0.2, 0.3]
    assert result[0].model == "sentence-transformers/all-MiniLM-L6-v2"
    assert result[0].dimensions == 3

    assert result[1].chunk_id == "chunk-2"
    assert result[1].document_id == "doc-1"
    assert result[1].embedding == [0.4, 0.5, 0.6]
    assert result[1].model == "sentence-transformers/all-MiniLM-L6-v2"
    assert result[1].dimensions == 3


def test_embedding_pipeline_preserves_chunk_order():
    config = EmbeddingConfig(
        model="sentence-transformers/all-MiniLM-L6-v2"
    )
    provider = MagicMock()
    provider.embed.return_value = [
        [0.1, 0.2],
        [0.3, 0.4],
        [0.5, 0.6],
    ]

    pipeline = EmbeddingPipeline(provider, config)

    chunks = [
        make_chunk(chunk_id="chunk-1", content="First"),
        make_chunk(chunk_id="chunk-2", content="Second"),
        make_chunk(chunk_id="chunk-3", content="Third"),
    ]

    result = pipeline.process(chunks)

    assert [item.chunk_id for item in result] == [
        "chunk-1",
        "chunk-2",
        "chunk-3",
    ]


def test_embedding_pipeline_raises_when_embedding_count_does_not_match():
    config = EmbeddingConfig(
        model="sentence-transformers/all-MiniLM-L6-v2"
    )
    provider = MagicMock()
    provider.embed.return_value = [[0.1, 0.2]]

    pipeline = EmbeddingPipeline(provider, config)

    chunks = [
        make_chunk(chunk_id="chunk-1", content="First"),
        make_chunk(chunk_id="chunk-2", content="Second"),
    ]

    with pytest.raises(EmbeddingError):
        pipeline.process(chunks)


def test_embedding_pipeline_raises_for_empty_embedding():
    config = EmbeddingConfig(
        model="sentence-transformers/all-MiniLM-L6-v2"
    )
    provider = MagicMock()
    provider.embed.return_value = [[]]

    pipeline = EmbeddingPipeline(provider, config)

    chunks = [
        make_chunk(
            chunk_id="chunk-1",
            content="Python is a programming language",
        )
    ]

    with pytest.raises(EmbeddingError):
        pipeline.process(chunks)


def test_embedding_pipeline_raises_for_inconsistent_dimensions():
    config = EmbeddingConfig(
        model="sentence-transformers/all-MiniLM-L6-v2"
    )
    provider = MagicMock()
    provider.embed.return_value = [
        [0.1, 0.2, 0.3],
        [0.4, 0.5],
    ]

    pipeline = EmbeddingPipeline(provider, config)

    chunks = [
        make_chunk(chunk_id="chunk-1", content="First"),
        make_chunk(chunk_id="chunk-2", content="Second"),
    ]

    with pytest.raises(EmbeddingError):
        pipeline.process(chunks)