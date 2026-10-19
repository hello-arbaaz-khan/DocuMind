
import pytest
from pydantic import ValidationError

from RagCore.Context.context import Context
from RagCore.Generation.generation import GenerationConfig
from RagCore.Generation.pipeline import GenerationPipeline
from RagCore.Query.query import Query


class RecordingGenerationProvider:
    def __init__(self, response="A concise answer."):
        self.response = response
        self.calls = []

    def generate(self, system_prompt, user_prompt):
        self.calls.append((system_prompt, user_prompt))
        return self.response


def make_query(text="What is RAG?"):
    return Query(text=text)


def make_context(
    text="RAG combines retrieval with generation.",
    sources=None,
):
    return Context(
        text=text,
        sources=[] if sources is None else sources,
    )


def test_generation_config_defaults():
    config = GenerationConfig()

    assert config.model == "openai/gpt-oss-20b"
    assert config.temperature == 0.2
    assert config.max_tokens == 1024


def test_generation_config_rejects_invalid_temperature():
    with pytest.raises(ValidationError):
        GenerationConfig(temperature=-1)


def test_generation_config_rejects_invalid_max_tokens():
    with pytest.raises(ValidationError):
        GenerationConfig(max_tokens=0)


def test_generation_returns_provider_response():
    provider = RecordingGenerationProvider(
        response="RAG retrieves relevant information before generation."
    )
    pipeline = GenerationPipeline(provider)

    answer = pipeline.generate(make_query(), make_context())

    assert answer == (
        "RAG retrieves relevant information before generation."
    )
    assert len(provider.calls) == 1


def test_generation_builds_prompt_from_query_and_context():
    provider = RecordingGenerationProvider()
    pipeline = GenerationPipeline(provider)

    pipeline.generate(
        Query(text="What is the main finding?"),
        Context(
            text=(
                "[Source 1]\n"
                "Document: Report.pdf\n"
                "Page: 2\n"
                "Content:\n"
                "The report identifies a 12% increase."
            ),
            sources=[],
        ),
    )

    system_prompt, user_prompt = provider.calls[0]

    assert "What is the main finding?" in user_prompt
    assert "Report.pdf" in user_prompt
    assert "12% increase" in user_prompt
    assert "document-grounded AI assistant" in system_prompt
    assert "retrieved document evidence" in system_prompt


def test_simple_question_uses_direct_answer_instructions():
    provider = RecordingGenerationProvider()
    pipeline = GenerationPipeline(provider)

    pipeline.generate(
        Query(text="What is the main finding?"),
        Context(
            text=(
                "[Source 1]\n"
                "Document: Report.pdf\n"
                "Page: 2\n"
                "Content:\n"
                "The report identifies a 12% increase."
            ),
            sources=[],
        ),
    )

    system_prompt, user_prompt = provider.calls[0]

    assert "What is the main finding?" in user_prompt
    assert "12% increase" in user_prompt
    assert "document-grounded AI assistant" in system_prompt
    assert "retrieved document evidence" in system_prompt
    assert "document-grounded AI assistant" in system_prompt
    assert "directly and naturally" in system_prompt


def test_summary_instructions_support_structured_markdown():
    provider = RecordingGenerationProvider()
    pipeline = GenerationPipeline(provider)

    answer = pipeline.generate(
        Query(text="Write a professional summary of the report."),
        Context(
            text=(
                "[Source 1]\n"
                "Document: Report.pdf\n"
                "Page: 1\n"
                "Content:\n"
                "The report describes three findings."
            ),
            sources=[],
        ),
    )

    system_prompt, user_prompt = provider.calls[0]

    assert answer == "A concise answer."
    assert "numbered sections" in system_prompt
    assert "bullet points" in system_prompt
    assert "bold" in system_prompt
    assert "conclusion" in system_prompt
    assert "professional summary" in user_prompt
    assert "three findings" in user_prompt


def test_generation_includes_conversation_history_for_follow_up():
    provider = RecordingGenerationProvider()
    pipeline = GenerationPipeline(provider)

    pipeline.generate(
        make_query("What about its limitations?"),
        make_context(),
        conversation_context=(
            "User: Summarize the study.\n"
            "Assistant: The study investigates a new method."
        ),
    )

    system_prompt, user_prompt = provider.calls[0]

    assert "What about its limitations?" in user_prompt
    assert "Summarize the study." in user_prompt
    assert "investigates a new method" in user_prompt
    assert "not document evidence" in user_prompt
    assert "document-grounded AI assistant" in system_prompt


def test_multi_document_prompt_includes_both_sources():
    provider = RecordingGenerationProvider()
    pipeline = GenerationPipeline(provider)

    evidence = (
        "[Source 1]\nDocument: Report-A.pdf\nPage: 2\n"
        "Content:\nFinding A.\n\n---\n\n"
        "[Source 2]\nDocument: Report-B.pdf\nPage: 5\n"
        "Content:\nFinding B."
    )

    pipeline.generate(
        Query(text="Compare the two reports."),
        Context(text=evidence, sources=[]),
    )

    system_prompt, user_prompt = provider.calls[0]

    assert "MULTI-DOCUMENT QUESTIONS" in system_prompt
    assert "Report-A.pdf" in user_prompt
    assert "Report-B.pdf" in user_prompt
    assert "Page: 2" in user_prompt
    assert "Page: 5" in user_prompt
    assert "Finding A." in user_prompt
    assert "Finding B." in user_prompt


def test_follow_up_history_reaches_generation():
    provider = RecordingGenerationProvider()
    pipeline = GenerationPipeline(provider)

    pipeline.generate(
        Query(text="What about its limitations?"),
        Context(
            text=(
                "[Source 1]\n"
                "Document: Study.pdf\n"
                "Page: 4\n"
                "Content:\n"
                "The study reports a small sample size."
            ),
            sources=[],
        ),
        conversation_context=(
            "User: Summarize the study.\n"
            "Assistant: The study investigates a new method."
        ),
    )

    _, user_prompt = provider.calls[0]

    assert "What about its limitations?" in user_prompt
    assert "Summarize the study" in user_prompt
    assert "new method" in user_prompt


def test_empty_context_returns_insufficient_evidence_answer():
    provider = RecordingGenerationProvider()
    pipeline = GenerationPipeline(provider)

    answer = pipeline.generate(
        Query(text="What happened in the report?"),
        Context(text="", sources=[]),
    )

    assert "not contain enough information" in answer
    assert provider.calls == []


def test_provider_response_is_returned_without_reformatting():
    expected = (
        "# Summary\n\n"
        "## Findings\n\n"
        "- **Finding:** Supported by the source.\n"
    )
    pipeline = GenerationPipeline(
        RecordingGenerationProvider(response=expected)
    )

    answer = pipeline.generate(
        Query(text="Summarize the findings."),
        Context(text="Supported evidence.", sources=[]),
    )

    assert answer == expected.strip()