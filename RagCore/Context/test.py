from RagCore.Context.builder import ContextBuilder
from RagCore.Context.context import ContextConfig
from RagCore.Retrieval.retrieval import RetrievalResult


def make_result(
    chunk_id,
    document_id,
    content,
    chunk_index,
    page_number=None,
    metadata=None,
):
    return RetrievalResult(
        chunk_id=chunk_id,
        document_id=document_id,
        content=content,
        score=0.90,
        page_number=page_number,
        chunk_index=chunk_index,
        metadata=metadata or {},
    )


def test_build_context_from_candidates():
    candidates = [
        make_result(
            "chunk-1",
            "doc-1",
            "First content",
            0,
        ),
        make_result(
            "chunk-2",
            "doc-1",
            "Second content",
            1,
        ),
    ]

    builder = ContextBuilder()

    context = builder.build(candidates)

    assert "[Source 1]" in context.text
    assert "Document ID: doc-1" in context.text
    assert "First content" in context.text
    assert "[Source 2]" in context.text
    assert "Second content" in context.text


def test_build_context_preserves_source_information():
    candidates = [
        make_result(
            "chunk-1",
            "doc-1",
            "First content",
            0,
            page_number=3,
            metadata={
                "filename": "report.pdf",
                "rerank_score": 0.95,
            },
        )
    ]

    builder = ContextBuilder()

    context = builder.build(candidates)

    source = context.sources[0]
    assert source["source_number"] == 1
    assert source["chunk_id"] == "chunk-1"
    assert source["document_id"] == "doc-1"
    assert source["page_number"] == 3
    assert source["chunk_index"] == 0
    assert source["score"] == 0.90
    assert source["rerank_score"] == 0.95
    assert source["metadata"] == {
        "filename": "report.pdf",
        "rerank_score": 0.95,
    }


def test_build_empty_context():
    builder = ContextBuilder()

    context = builder.build([])

    assert context.text == ""
    assert context.sources == []


def test_build_context_respects_max_chunks():
    candidates = [
        make_result(
            "chunk-1",
            "doc-1",
            "Content 1",
            0,
        ),
        make_result(
            "chunk-2",
            "doc-1",
            "Content 2",
            1,
        ),
        make_result(
            "chunk-3",
            "doc-1",
            "Content 3",
            2,
        ),
    ]

    config = ContextConfig(max_chunks=2)

    builder = ContextBuilder(config)

    context = builder.build(candidates)

    assert len(context.sources) == 2
    assert "Content 1" in context.text
    assert "Content 2" in context.text
    assert "Content 3" not in context.text


def test_build_context_preserves_candidate_order():
    candidates = [
        make_result(
            "chunk-2",
            "doc-1",
            "Second",
            1,
        ),
        make_result(
            "chunk-1",
            "doc-1",
            "First",
            0,
        ),
    ]

    builder = ContextBuilder()

    context = builder.build(candidates)

    assert context.text.index("Second") < context.text.index("First")
    assert context.text.index("[Source 1]") < context.text.index("[Source 2]")


def test_context_config_default_max_chunks():
    config = ContextConfig()

    assert config.max_chunks == 5


def test_context_config_rejects_invalid_max_chunks():
    import pytest
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        ContextConfig(max_chunks=0)