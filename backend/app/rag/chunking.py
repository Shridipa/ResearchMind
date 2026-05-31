from dataclasses import dataclass

from app.document_processing.types import ParsedDocument


@dataclass(frozen=True)
class DocumentChunk:
    chunk_id: str
    paper_id: str
    title: str
    page: int
    text: str


class AdaptiveChunker:
    def __init__(self, chunk_size: int = 900, overlap: int = 160) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, document: ParsedDocument) -> list[DocumentChunk]:
        chunks: list[DocumentChunk] = []
        for page in document.pages:
            text = " ".join(page.text.split())
            start = 0
            local_index = 0
            while start < len(text):
                end = min(start + self.chunk_size, len(text))
                if end < len(text):
                    sentence_end = max(text.rfind(". ", start, end), text.rfind("? ", start, end))
                    if sentence_end > start + self.chunk_size * 0.55:
                        end = sentence_end + 1
                chunk_text = text[start:end].strip()
                if chunk_text:
                    chunks.append(
                        DocumentChunk(
                            chunk_id=f"{document.paper_id}:p{page.page}:c{local_index}",
                            paper_id=document.paper_id,
                            title=document.title,
                            page=page.page,
                            text=chunk_text,
                        )
                    )
                if end >= len(text):
                    break
                start = max(0, end - self.overlap)
                local_index += 1
        return chunks
