import json
from dataclasses import asdict
from pathlib import Path

import faiss
import numpy as np

from app.rag.chunking import DocumentChunk


class FaissVectorStore:
    def __init__(self, dimension: int, index_path: Path, metadata_path: Path) -> None:
        self.dimension = dimension
        self.index_path = index_path
        self.metadata_path = metadata_path
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        self.metadata_path.parent.mkdir(parents=True, exist_ok=True)
        self.index = self._load_or_create_index()
        self.metadata = self._load_metadata()

    def _load_or_create_index(self) -> faiss.Index:
        if self.index_path.exists():
            return faiss.read_index(str(self.index_path))
        return faiss.IndexFlatIP(self.dimension)

    def _load_metadata(self) -> list[dict]:
        if not self.metadata_path.exists():
            return []
        return json.loads(self.metadata_path.read_text(encoding="utf-8"))

    def add(self, chunks: list[DocumentChunk], embeddings: np.ndarray) -> None:
        if len(chunks) == 0:
            return
        self.index.add(embeddings.astype("float32"))
        self.metadata.extend(asdict(chunk) for chunk in chunks)
        self.persist()

    def remove_chunks(self, paper_ids: list[str]) -> None:
        if not paper_ids or not self.metadata:
            return

        remove_indices = [idx for idx, meta in enumerate(self.metadata) if meta.get("paper_id") in paper_ids]
        if not remove_indices:
            return

        self.index.remove_ids(np.array(remove_indices, dtype="int64"))
        self.metadata = [meta for idx, meta in enumerate(self.metadata) if idx not in set(remove_indices)]
        self.persist()

    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int,
        paper_ids: list[str] | None = None,
    ) -> list[tuple[DocumentChunk, float]]:
        if self.index.ntotal == 0:
            return []
        scores, indices = self.index.search(query_embedding.astype("float32"), min(top_k * 4, self.index.ntotal))
        results: list[tuple[DocumentChunk, float]] = []
        allowed = set(paper_ids or [])
        for score, idx in zip(scores[0], indices[0], strict=False):
            if idx < 0:
                continue
            item = self.metadata[idx]
            if allowed and item["paper_id"] not in allowed:
                continue
            results.append((DocumentChunk(**item), float(score)))
            if len(results) >= top_k:
                break
        return results

    def persist(self) -> None:
        faiss.write_index(self.index, str(self.index_path))
        self.metadata_path.write_text(json.dumps(self.metadata, indent=2), encoding="utf-8")
