import hashlib
from typing import Protocol

import numpy as np

from app.core.config import settings


class EmbeddingModel(Protocol):
    @property
    def dimension(self) -> int:
        ...

    def encode(self, texts: list[str]) -> np.ndarray:
        ...


class SentenceTransformerEmbedder:
    def __init__(self, model_name: str = settings.embedding_model) -> None:
        from sentence_transformers import SentenceTransformer

        self.model = SentenceTransformer(model_name)

    @property
    def dimension(self) -> int:
        return int(self.model.get_embedding_dimension())

    def encode(self, texts: list[str]) -> np.ndarray:
        vectors = self.model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        return np.asarray(vectors, dtype="float32")


class HashingEmbedder:
    """Deterministic lightweight fallback for tests and offline smoke runs."""

    def __init__(self, dimension: int = 384) -> None:
        self._dimension = dimension

    @property
    def dimension(self) -> int:
        return self._dimension

    def encode(self, texts: list[str]) -> np.ndarray:
        matrix = np.zeros((len(texts), self._dimension), dtype="float32")
        for row, text in enumerate(texts):
            for token in text.lower().split():
                digest = hashlib.sha256(token.encode("utf-8")).digest()
                idx = int.from_bytes(digest[:4], "little") % self._dimension
                matrix[row, idx] += 1.0
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        return matrix / np.clip(norms, 1e-6, None)


def build_embedder() -> EmbeddingModel:
    if settings.environment == "test" or settings.embedding_model == "hashing":
        return HashingEmbedder()
    return SentenceTransformerEmbedder()
