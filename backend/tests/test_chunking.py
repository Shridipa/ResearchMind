from app.document_processing.types import PageText, ParsedDocument
from app.rag.chunking import AdaptiveChunker


def test_chunker_preserves_metadata():
    doc = ParsedDocument(
        paper_id="p1",
        title="Attention Paper",
        pages=[PageText(page=1, text="Transformers use attention. " * 80)],
    )
    chunks = AdaptiveChunker(chunk_size=120, overlap=20).chunk(doc)
    assert chunks
    assert chunks[0].paper_id == "p1"
    assert chunks[0].page == 1
