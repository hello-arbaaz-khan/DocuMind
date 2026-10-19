
import pytest

from RagCore.Context.builder import ContextBuilder
from RagCore.Context.context import ContextConfig
from RagCore.Retrieval.retrieval import RetrievalResult


def make_result(
    chunk_id,
    document_id,
    content,
    *,
    page_number=None,
    chunk_index=0,
    metadata=None,
    score=0.9,
):
    return RetrievalResult(
        chunk_id=chunk_id,
        document_id=document_id,
        content=content,
        score=score,
        page_number=page_number,
        chunk_index=chunk_index,
        metadata=metadata or {},
    )


def test_context_includes_evidence_from_multiple_documents():
    builder = ContextBuilder(ContextConfig(max_chunks=5))

    candidates = [
        make_result(
            "a1",
            "doc-a",
            "Document A discusses a trade agreement.",
            page_number=2,
            metadata={"filename": "Report-A.pdf"},
        ),
        make_result(
            "b1",
            "doc-b",
            "Document B discusses a different agreement.",
            page_number=5,
            metadata={"filename": "Report-B.pdf"},
        ),
    ]

    context = builder.build(candidates)

    assert "[Source 1]" in context.text
    assert "[Source 2]" in context.text
    assert "Report-A.pdf" in context.text
    assert "Report-B.pdf" in context.text
    assert "Page: 2" in context.text
    assert "Page: 5" in context.text
    assert "Document A discusses a trade agreement." in context.text
    assert "Document B discusses a different agreement." in context.text
    assert len(context.sources) == 2


def test_build_context_preserves_source_information():
    builder = ContextBuilder()

    candidates = [
        make_result(
            "chunk-1",
            "doc-1",
            "First content",
            page_number=3,
            chunk_index=0,
            metadata={
                "filename": "report.pdf",
                "rerank_score": 0.95,
            },
        )
    ]

    context = builder.build(candidates)

    assert len(context.sources) == 1

    source = context.sources[0]
    assert source["source_number"] == 1
    assert source["chunk_id"] == "chunk-1"
    assert source["document_id"] == "doc-1"
    assert source["document_name"] == "report.pdf"
    assert source["page_number"] == 3
    assert source["chunk_index"] == 0
    assert source["score"] == pytest.approx(0.90)
    assert source["rerank_score"] == pytest.approx(0.95)
    assert source["metadata"] == {
        "filename": "report.pdf",
        "rerank_score": 0.95,
    }


def test_build_empty_context():
    context = ContextBuilder().build([])

    assert context.text == ""
    assert context.sources == []


def test_context_represents_each_document_before_extra_chunks():
    builder = ContextBuilder(ContextConfig(max_chunks=3))

    candidates = [
        make_result("a1", "doc-a", "A first excerpt."),
        make_result("a2", "doc-a", "A second excerpt."),
        make_result("a3", "doc-a", "A third excerpt."),
        make_result("b1", "doc-b", "B first excerpt."),
    ]

    context = builder.build(candidates)

    document_ids = {
        source["document_id"] for source in context.sources
    }

    assert document_ids == {"doc-a", "doc-b"}
    assert len(context.sources) == 3


def test_context_deduplicates_identical_content():
    builder = ContextBuilder()

    context = builder.build(
        [
            make_result("a1", "doc-a", "Same content."),
            make_result("b1", "doc-b", "  SAME   CONTENT. "),
        ]
    )

    assert len(context.sources) == 1
    assert "Same content." in context.text


def test_context_uses_document_id_when_name_is_unavailable():
    context = ContextBuilder().build(
        [
            make_result(
                "a1",
                "doc-a",
                "Evidence without a document title.",
                page_number=7,
            )
        ]
    )

    assert "Document: doc-a" in context.text
    assert "Document ID: doc-a" in context.text
    assert "Page: 7" in context.text


def test_context_respects_maximum_chunk_count():
    context = ContextBuilder(
        ContextConfig(max_chunks=2)
    ).build(
        [
            make_result("a1", "doc-a", "First excerpt."),
            make_result("b1", "doc-b", "Second excerpt."),
            make_result("c1", "doc-c", "Third excerpt."),
        ]
    )

    assert len(context.sources) == 2
    assert "Third excerpt." not in context.text


def test_empty_candidates_produce_empty_context():
    context = ContextBuilder().build([])

    assert context.text == ""
    assert context.sources == []