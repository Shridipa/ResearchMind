import io
import asyncio
from pathlib import Path

import numpy as np
import pytest
from starlette.datastructures import UploadFile


def _patch_dependencies(tmp_path, monkeypatch):
    """Patch service dependencies to use lightweight in-memory implementations."""
    from app.core import config
    from app.services import dependencies as deps

    # Redirect settings to temp paths
    config.settings.data_dir = tmp_path / "data"
    config.settings.indexes_path = tmp_path / "data" / "indexes"
    config.settings.summary_cache_path = tmp_path / "data" / "cache" / "summaries"
    config.settings.faiss_index_path = config.settings.indexes_path / "researchmind.faiss"
    config.settings.metadata_path = config.settings.indexes_path / "metadata.json"

    # Simple in-memory embedder
    class MockEmbedder:
        def __init__(self, dim=128):
            self.dimension = dim

        def encode(self, texts):
            return np.zeros((len(texts), self.dimension), dtype="float32")

    # In-memory vector store
    class InMemoryVectorStore:
        def __init__(self):
            self.metadata = []

        def add(self, chunks, embeddings):
            for chunk in chunks:
                self.metadata.append({
                    "chunk_id": chunk.chunk_id,
                    "paper_id": chunk.paper_id,
                    "title": chunk.title,
                    "page": chunk.page,
                    "text": chunk.text,
                })

        def remove_chunks(self, paper_ids):
            self.metadata = [m for m in self.metadata if m.get("paper_id") not in set(paper_ids)]

        def search(self, query_embedding, top_k, paper_ids=None):
            results = []
            allowed = set(paper_ids or [])
            for m in self.metadata:
                if allowed and m["paper_id"] not in allowed:
                    continue
                # simple relevance: contain query word
                score = 1.0 if query_embedding and query_embedding == b"_query_placeholder_" else 0.5
                from app.rag.chunking import DocumentChunk

                results.append((DocumentChunk(**m), float(score)))
                if len(results) >= top_k:
                    break
            return results

    # Simple BM25 stub that mirrors vector store metadata
    class InMemoryBM25:
        def __init__(self, vs: InMemoryVectorStore):
            self.vs = vs

        def add_chunks(self, chunks):
            return

        def remove_chunks(self, paper_ids):
            return

        def search(self, query, top_k=10, paper_ids=None):
            results = []
            allowed = set(paper_ids or [])
            for m in self.vs.metadata:
                if allowed and m["paper_id"] not in allowed:
                    continue
                # simple token match score
                score = 5.0 if query.lower().split()[0] in m.get("text", "").lower() else 1.0
                from app.rag.chunking import DocumentChunk

                results.append((DocumentChunk(**m), float(score)))
                if len(results) >= top_k:
                    break
            return results

    # Simple retriever that returns stored chunks matching requested paper_ids
    class SimpleRetriever:
        def __init__(self, vs: InMemoryVectorStore):
            self.vs = vs

        def retrieve(self, query, top_k, paper_ids=None):
            # Return up to top_k chunks from vector store for given paper_ids
            results = []
            allowed = set(paper_ids or [])
            from app.rag.chunking import DocumentChunk

            for m in self.vs.metadata:
                if allowed and m["paper_id"] not in allowed:
                    continue
                results.append((DocumentChunk(**m), 0.5))
                if len(results) >= top_k:
                    break
            return results

    embedder = MockEmbedder()
    vs = InMemoryVectorStore()
    bm25 = InMemoryBM25(vs)
    retriever = SimpleRetriever(vs)

    # Patch dependency providers
    monkeypatch.setattr(deps, "get_embedder", lambda: embedder)
    monkeypatch.setattr(deps, "get_vector_store", lambda: vs)
    monkeypatch.setattr(deps, "get_bm25_index", lambda: bm25)
    monkeypatch.setattr(deps, "get_retriever", lambda: retriever)
    monkeypatch.setattr(deps, "get_summarizer", lambda: None)

    return vs


@pytest.mark.integration
def test_upload_query_delete(tmp_path, monkeypatch):
    """Full flow: upload → index → search → delete."""
    from app.services.paper_service import paper_service
    from app.services.paper_registry import paper_registry

    vs = _patch_dependencies(tmp_path, monkeypatch)

    sample = Path(__file__).parent.parent.parent / "data" / "papers" / "0891d20b45eb4d0f8c8c8140254a2d95.pdf"
    if not sample.exists():
        pytest.skip("Sample PDF not available")

    data = sample.read_bytes()
    upload = UploadFile(file=io.BytesIO(data), filename="sample.pdf")

    # ingest
    upload_resp = asyncio.run(paper_service.ingest_upload(upload))
    paper_id = upload_resp.paper_id

    assert paper_registry.get(paper_id) is not None
    # vector store should have metadata for this paper
    assert any(m["paper_id"] == paper_id for m in vs.metadata)

    # search via paper_service
    results = paper_service.search_papers("momentum", top_k=5)
    assert any(r.paper_id == paper_id for r in results)

    # delete and verify removal
    paper_service.delete_paper(paper_id)
    assert paper_registry.get(paper_id) is None
    assert not any(m["paper_id"] == paper_id for m in vs.metadata)


@pytest.mark.integration
def test_multi_paper_comparison(tmp_path, monkeypatch):
    """Upload two papers and verify the compare flow returns sources for both."""
    from app.services.paper_service import paper_service
    from app.services.paper_registry import paper_registry

    vs = _patch_dependencies(tmp_path, monkeypatch)

    sample = Path(__file__).parent.parent.parent / "data" / "papers" / "0891d20b45eb4d0f8c8c8140254a2d95.pdf"
    if not sample.exists():
        pytest.skip("Sample PDF not available")

    data = sample.read_bytes()
    upload1 = UploadFile(file=io.BytesIO(data), filename="s1.pdf")
    upload2 = UploadFile(file=io.BytesIO(data), filename="s2.pdf")

    resp1 = asyncio.run(paper_service.ingest_upload(upload1))
    resp2 = asyncio.run(paper_service.ingest_upload(upload2))

    # Compare
    compare_resp = paper_service.compare([resp1.paper_id, resp2.paper_id])
    assert compare_resp.sources
    # sources should reference the paper ids
    found_ids = {s.paper_id for s in compare_resp.sources}
    assert resp1.paper_id in found_ids and resp2.paper_id in found_ids


@pytest.mark.integration
def test_out_of_domain_protection(tmp_path, monkeypatch):
    """Asks an out-of-domain question and expects no evidence returned."""
    from app.services.paper_service import paper_service

    _ = _patch_dependencies(tmp_path, monkeypatch)

    results = paper_service.search_papers("Who won FIFA World Cup 2018?", top_k=5)
    assert results == []
