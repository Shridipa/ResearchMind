# ResearchMind AI Architecture

## Design Goals

ResearchMind AI is built around separable research-system layers:

1. ingestion: parse PDFs into typed page spans,
2. chunking: convert raw paper text into retrieval units,
3. embeddings: map chunks to dense vectors,
4. indexing: store vectors and metadata in FAISS,
5. retrieval: find candidate evidence,
6. generation: produce answers with citations,
7. verification: score grounding and confidence,
8. evaluation: measure quality and regressions.

## Backend Modules

- `app.api`: FastAPI routers and request/response schemas.
- `app.core`: settings, logging, errors, dependency wiring.
- `app.document_processing`: PDF readers and citation extraction.
- `app.rag`: chunking, embeddings, vector store, retrieval, answer generation.
- `app.services`: high-level orchestration services.
- `app.evaluation`: metric implementations used by scripts and tests.

## Grounding Policy

Answers should prefer retrieved evidence over parametric memory. Every generated response returns source chunks and a confidence score. If retrieved evidence is weak, the system should say it cannot answer from the uploaded papers.

## Scalability Plan

- Move indexing into background workers.
- Persist metadata in Postgres.
- Store files in S3-compatible object storage.
- Keep FAISS local for prototype; replace with managed vector DB when needed.
- Add Redis caching for embeddings and repeated queries.
