import textwrap
import pytest
from RagCore.Chunking.parser import MarkdownParser
from RagCore.Chunking.chunk import Chunk

from RagCore.Chunking.parser import StructuralUnit
from RagCore.Chunking.splitter import (
    ChunkSplitter,
    SplitterConfig,
)

from RagCore.Chunking.pipeline import ChunkingPipeline
from RagCore.Ingestion.document import (
    DocumentPage,
    InternalDocument,
)


def test_empty_content():
    # Empty content se empty result milna chahiye.

    parser = MarkdownParser()

    assert parser.parse("") == []


def test_whitespace_only_content():
    # Sirf spaces/newlines bhi empty treat hone chahiye.

    parser = MarkdownParser()

    assert parser.parse("   \n\n   ") == []


def test_paragraph():
    # Normal paragraph correctly detect hona chahiye.

    parser = MarkdownParser()

    units = parser.parse("This is a paragraph.")

    assert len(units) == 1
    assert units[0].unit_type == "paragraph"
    assert units[0].content == "This is a paragraph."


def test_multiple_paragraphs():
    # Multiple paragraphs separate structural units honi chahiye.

    parser = MarkdownParser()

    units = parser.parse(
        textwrap.dedent(
            """
            First paragraph.

            Second paragraph.

            Third paragraph.
            """
        )
    )

    assert len(units) == 3

    assert [unit.unit_type for unit in units] == [
        "paragraph",
        "paragraph",
        "paragraph",
    ]


def test_heading():
    # Heading detect aur level preserve hona chahiye.

    parser = MarkdownParser()

    units = parser.parse("# Introduction")

    assert len(units) == 1
    assert units[0].unit_type == "heading"
    assert units[0].content == "Introduction"
    assert units[0].level == 1


def test_multiple_heading_levels():
    # H1/H2/H3 ke levels correctly preserve hone chahiye.

    parser = MarkdownParser()

    units = parser.parse(
        textwrap.dedent(
            """
            # Main

            ## Section

            ### Subsection
            """
        )
    )

    assert [unit.level for unit in units] == [1, 2, 3]


def test_heading_with_inline_markdown():
    # Heading ke andar bold/italic Markdown hone par text preserve hona chahiye.

    parser = MarkdownParser()

    units = parser.parse("# **Important** Section")

    assert len(units) == 1
    assert units[0].unit_type == "heading"
    assert "Important" in units[0].content
    assert "Section" in units[0].content


def test_bullet_list():
    # Bullet list ko ek list structural unit banana chahiye.

    parser = MarkdownParser()

    units = parser.parse(
        textwrap.dedent(
            """
            - First item
            - Second item
            - Third item
            """
        )
    )

    assert len(units) == 1
    assert units[0].unit_type == "list"
    assert "First item" in units[0].content
    assert "Second item" in units[0].content
    assert "Third item" in units[0].content


def test_ordered_list():
    # Numbered list bhi list structural unit honi chahiye.

    parser = MarkdownParser()

    units = parser.parse(
        textwrap.dedent(
            """
            1. First
            2. Second
            3. Third
            """
        )
    )

    assert len(units) == 1
    assert units[0].unit_type == "list"
    assert "First" in units[0].content
    assert "Second" in units[0].content


def test_nested_list():
    # Nested list completely lose nahi honi chahiye.

    parser = MarkdownParser()

    units = parser.parse(
        textwrap.dedent(
            """
            - Parent
              - Child
              - Another child
            """
        )
    )

    assert len(units) == 1
    assert units[0].unit_type == "list"
    assert "Parent" in units[0].content
    assert "Child" in units[0].content


def test_fenced_code():
    # Fenced code ko code unit banana chahiye.

    parser = MarkdownParser()

    units = parser.parse(
        textwrap.dedent(
            """
            ```python
            def hello():
                return "world"
            ```
            """
        )
    )

    assert len(units) == 1
    assert units[0].unit_type == "code"
    assert "def hello()" in units[0].content
    assert units[0].language == "python"


def test_code_without_language():
    # Language missing ho to parser crash nahi hona chahiye.

    parser = MarkdownParser()

    units = parser.parse(
        textwrap.dedent(
            """
            ```
            print("hello")
            ```
            """
        )
    )

    assert len(units) == 1
    assert units[0].unit_type == "code"
    assert units[0].language is None


def test_indented_code():
    # Indented code block bhi detect hona chahiye.

    parser = MarkdownParser()

    units = parser.parse(
        "    print(\"hello\")\n    print(\"world\")"
    )

    assert any(unit.unit_type == "code" for unit in units)


def test_table():
    # Markdown table ko table unit banana chahiye.

    parser = MarkdownParser()

    units = parser.parse(
        textwrap.dedent(
            """
            | Name | Age |
            | --- | --- |
            | Ali | 20 |
            | Ahmed | 25 |
            """
        )
    )

    assert len(units) == 1
    assert units[0].unit_type == "table"
    assert "Name" in units[0].content
    assert "Ali" in units[0].content
    assert "Ahmed" in units[0].content


def test_mixed_document():
    # Realistic document mein different structures preserve honi chahiye.

    parser = MarkdownParser()

    units = parser.parse(
        textwrap.dedent(
            """
            # Introduction

            This is a paragraph.

            - First
            - Second

            | A | B |
            | --- | --- |
            | 1 | 2 |

            ```python
            print("hello")
            ```
            """
        )
    )

    assert [unit.unit_type for unit in units] == [
        "heading",
        "paragraph",
        "list",
        "table",
        "code",
    ]


def test_deterministic_parser_output():
    # Same input ko baar baar parse karne par same result hona chahiye.

    parser = MarkdownParser()

    content = textwrap.dedent(
        """
        # Test

        Some paragraph.

        - Item
        """
    )

    first = parser.parse(content)
    second = parser.parse(content)

    assert first == second




def test_chunk_creation():

    chunk = Chunk(
        chunk_id="doc-1:0",
        document_id="doc-1",
        content="Hello world",
        page_number=1,
        chunk_index=0,
    )

    assert chunk.chunk_id == "doc-1:0"

    assert chunk.document_id == "doc-1"

    assert chunk.content == "Hello world"

    assert chunk.page_number == 1

    assert chunk.chunk_index == 0


def test_chunk_default_values():

    chunk = Chunk(
        chunk_id="doc-1:0",
        document_id="doc-1",
        content="Text",
        chunk_index=0,
    )

    assert chunk.parent_id is None

    assert chunk.page_number is None

    assert chunk.metadata == {}


def test_chunk_metadata():

    chunk = Chunk(
        chunk_id="doc-1:0",
        document_id="doc-1",
        content="Text",
        chunk_index=0,
        metadata={
            "structure_types": ["heading", "paragraph"],
        },
    )

    assert chunk.metadata["structure_types"] == [
        "heading",
        "paragraph",
    ]


def test_negative_chunk_index_rejected():

    with pytest.raises(ValueError):
        Chunk(
            chunk_id="doc-1:-1",
            document_id="doc-1",
            content="Text",
            chunk_index=-1,
        )




def unit(content: str, unit_type: str = "paragraph") -> StructuralUnit:
    # Tests mein StructuralUnit quickly create karne ke liye helper.

    return StructuralUnit(
        unit_type=unit_type,
        content=content,
    )


def test_default_configuration():
    # Default configuration verify karte hain.

    splitter = ChunkSplitter()

    assert splitter.config.chunk_size == 1000
    assert splitter.config.chunk_overlap == 100


def test_custom_configuration():
    # Custom size/overlap accept hone chahiye.

    splitter = ChunkSplitter(
        SplitterConfig(
            chunk_size=500,
            chunk_overlap=50,
        )
    )

    assert splitter.config.chunk_size == 500
    assert splitter.config.chunk_overlap == 50


def test_invalid_chunk_size():
    # Zero/negative chunk size reject honi chahiye.

    with pytest.raises(ValueError):
        ChunkSplitter(
            SplitterConfig(
                chunk_size=0,
                chunk_overlap=0,
            )
        )

    with pytest.raises(ValueError):
        ChunkSplitter(
            SplitterConfig(
                chunk_size=-1,
                chunk_overlap=0,
            )
        )


def test_negative_overlap():
    # Negative overlap invalid hai.

    with pytest.raises(ValueError):
        ChunkSplitter(
            SplitterConfig(
                chunk_size=100,
                chunk_overlap=-1,
            )
        )


def test_overlap_equal_to_size():
    # Overlap chunk size ke equal nahi ho sakta.

    with pytest.raises(ValueError):
        ChunkSplitter(
            SplitterConfig(
                chunk_size=100,
                chunk_overlap=100,
            )
        )


def test_overlap_greater_than_size():
    # Overlap chunk size se bara bhi invalid hai.

    with pytest.raises(ValueError):
        ChunkSplitter(
            SplitterConfig(
                chunk_size=100,
                chunk_overlap=150,
            )
        )


def test_empty_units():
    # Empty input se empty result milna chahiye.

    splitter = ChunkSplitter()

    assert splitter.split([]) == []


def test_whitespace_units():
    # Whitespace-only units ignore honi chahiye.

    splitter = ChunkSplitter()

    units = [
        unit("   "),
        unit("\n\n"),
        unit("Real content"),
    ]

    chunks = splitter.split(units)

    assert chunks == ["Real content"]


def test_units_fit_single_chunk():
    # Small units ek hi chunk mein group honi chahiye.

    splitter = ChunkSplitter(
        SplitterConfig(
            chunk_size=100,
            chunk_overlap=0,
        )
    )

    chunks = splitter.split(
        [
            unit("First paragraph"),
            unit("Second paragraph"),
        ]
    )

    assert len(chunks) == 1
    assert "First paragraph" in chunks[0]
    assert "Second paragraph" in chunks[0]


def test_chunk_size_creates_multiple_chunks():
    # Size limit cross hone par new chunk create hona chahiye.

    splitter = ChunkSplitter(
        SplitterConfig(
            chunk_size=25,
            chunk_overlap=0,
        )
    )

    chunks = splitter.split(
        [
            unit("1234567890"),
            unit("abcdefghij"),
            unit("ABCDEFGHIJ"),
        ]
    )

    assert len(chunks) == 2


def test_zero_overlap():
    # Zero overlap mein previous content repeat nahi hona chahiye.

    splitter = ChunkSplitter(
        SplitterConfig(
            chunk_size=15,
            chunk_overlap=0,
        )
    )

    chunks = splitter.split(
        [
            unit("1234567890"),
            unit("abcdefghij"),
        ]
    )

    assert len(chunks) == 2
    assert chunks[0] == "1234567890"
    assert chunks[1] == "abcdefghij"


def test_overlap():
    # Configured overlap next chunk mein appear hona chahiye.

    splitter = ChunkSplitter(
        SplitterConfig(
            chunk_size=20,
            chunk_overlap=5,
        )
    )

    chunks = splitter.split(
        [
            unit("1234567890"),
            unit("abcdefghij"),
        ]
    )

    assert len(chunks) == 2
    assert "67890" in chunks[1]


def test_large_single_unit():
    # Single unit chunk_size se bara ho to split hona chahiye.

    splitter = ChunkSplitter(
        SplitterConfig(
            chunk_size=10,
            chunk_overlap=2,
        )
    )

    content = "abcdefghijklmnopqrstuvwxyz"

    chunks = splitter.split([unit(content)])

    assert len(chunks) > 1

    for chunk in chunks:
        # Har generated piece inspect karte hain.

        assert len(chunk) <= 10


def test_large_unit_preserves_content():
    # Large unit split hone ke baad original content completely lose nahi hona chahiye.

    splitter = ChunkSplitter(
        SplitterConfig(
            chunk_size=10,
            chunk_overlap=2,
        )
    )

    content = "abcdefghijklmnopqrstuvwxyz"

    chunks = splitter.split([unit(content)])

    combined = "".join(chunks)

    for character in content:
        # Har original character kisi na kisi chunk mein hona chahiye.

        assert character in combined


def test_structural_units_preserve_order():
    # Structural unit ka order change nahi hona chahiye.

    splitter = ChunkSplitter(
        SplitterConfig(
            chunk_size=100,
            chunk_overlap=0,
        )
    )

    chunks = splitter.split(
        [
            unit("FIRST"),
            unit("SECOND"),
            unit("THIRD"),
        ]
    )

    assert chunks == ["FIRST\n\nSECOND\n\nTHIRD"]


def test_deterministic_splitter():
    # Same input se same chunks generate hone chahiye.

    splitter = ChunkSplitter(
        SplitterConfig(
            chunk_size=30,
            chunk_overlap=5,
        )
    )

    units = [
        unit("First"),
        unit("Second"),
        unit("Third"),
        unit("Fourth"),
    ]

    first = splitter.split(units)
    second = splitter.split(units)

    assert first == second




def test_pipeline_single_page():
    # Ek normal page ko complete Chunking pipeline se pass karte hain.

    document = InternalDocument(
        document_id="doc-1",
        pages=[
            DocumentPage(
                page_number=1,
                content=textwrap.dedent(
                    """
                    # Introduction

                    This is the first paragraph.

                    This is the second paragraph.
                    """
                ),
            )
        ],
        metadata={
            "file_name": "test.pdf",
            "page_count": 1,
        },
    )

    pipeline = ChunkingPipeline()

    chunks = pipeline.process(document)

    assert len(chunks) >= 1

    assert chunks[0].document_id == "doc-1"

    assert chunks[0].page_number == 1

    assert chunks[0].chunk_index == 0

    assert chunks[0].chunk_id == "doc-1:0"

    assert chunks[0].content


def test_pipeline_multiple_pages():
    # Multiple pages independently process honi chahiye.

    document = InternalDocument(
        document_id="doc-2",
        pages=[
            DocumentPage(
                page_number=1,
                content="Page one content.",
            ),
            DocumentPage(
                page_number=2,
                content="Page two content.",
            ),
        ],
        metadata={
            "file_name": "multi-page.pdf",
            "page_count": 2,
        },
    )

    pipeline = ChunkingPipeline()

    chunks = pipeline.process(document)

    assert len(chunks) >= 2

    assert chunks[0].page_number == 1
    assert chunks[1].page_number == 2


def test_pipeline_empty_page():
    # Empty page crash nahi karni chahiye.

    document = InternalDocument(
        document_id="doc-3",
        pages=[
            DocumentPage(
                page_number=1,
                content="",
            ),
            DocumentPage(
                page_number=2,
                content="Real content.",
            ),
        ],
        metadata={
            "file_name": "empty-page.pdf",
            "page_count": 2,
        },
    )

    pipeline = ChunkingPipeline()

    chunks = pipeline.process(document)

    assert len(chunks) >= 1

    assert all(chunk.content.strip() for chunk in chunks)


def test_pipeline_preserves_chunk_order():
    # Chunk indexes sequential hone chahiye.

    document = InternalDocument(
        document_id="doc-4",
        pages=[
            DocumentPage(
                page_number=1,
                content="First page.",
            ),
            DocumentPage(
                page_number=2,
                content="Second page.",
            ),
            DocumentPage(
                page_number=3,
                content="Third page.",
            ),
        ],
        metadata={
            "file_name": "ordered.pdf",
            "page_count": 3,
        },
    )

    pipeline = ChunkingPipeline()

    chunks = pipeline.process(document)

    assert [chunk.chunk_index for chunk in chunks] == list(
        range(len(chunks))
    )


def test_pipeline_deterministic():
    # Same document ko do baar process karne par same chunks hone chahiye.

    document = InternalDocument(
        document_id="doc-5",
        pages=[
            DocumentPage(
                page_number=1,
                content=textwrap.dedent(
                    """
                    # Test

                    Some content here.

                    - One
                    - Two
                    """
                ),
            )
        ],
        metadata={
            "file_name": "deterministic.pdf",
            "page_count": 1,
        },
    )

    pipeline = ChunkingPipeline()

    first = pipeline.process(document)
    second = pipeline.process(document)

    assert first == second


def test_pipeline_preserves_structure_metadata():
    # Heading/paragraph ki structural information metadata mein honi chahiye.

    document = InternalDocument(
        document_id="doc-6",
        pages=[
            DocumentPage(
                page_number=1,
                content=textwrap.dedent(
                    """
                    # Introduction

                    Important information.
                    """
                ),
            )
        ],
        metadata={
            "file_name": "metadata.pdf",
            "page_count": 1,
        },
    )

    pipeline = ChunkingPipeline()

    chunks = pipeline.process(document)

    assert chunks

    assert "structure_types" in chunks[0].metadata
    assert "heading" in chunks[0].metadata["structure_types"]