# Research Mind

Research Mind is a research paper assistant built to make academic literature easier to understand, search, and compare. It is designed around retrieval-first responses, so answers are based on real paper content instead of model guesses.

## What this project does

Research Mind accepts PDF research papers, extracts their text and metadata, and makes the corpus searchable. Users can ask questions, compare papers, and generate summaries that are grounded in sources.

Key capabilities:
- Upload research paper PDFs and automatically parse metadata
- Index paper content for semantic and keyword retrieval
- Answer questions with evidence from retrieved paper sections
- Compare methodology, results, and conclusions across papers
- Produce abstractive summaries with a local fallback path

## Why it exists

Many AI tools generate plausible-sounding answers without supporting evidence. Research Mind solves that by
- insisting on retrieval-first reasoning,
- validating answers against actual document content,
- and returning "not found" when supporting evidence is missing.

This makes it better suited for academic workflows where accuracy and traceability matter.

## Architecture overview

The project has two main parts:

1. **Frontend**
   - Next.js + React
   - TypeScript
   - Tailwind CSS
   - Provides upload, question, and comparison interfaces

2. **Backend**
   - FastAPI
   - Pydantic validation
   - Document extraction, indexing, retrieval, and answer generation

The backend processes PDFs, creates searchable text chunks, stores embeddings, and combines semantic and keyword search to retrieve relevant evidence.

## Core design principles

- **Evidence grounding**: answers come from retrieved content, not only from model completion.
- **Hybrid retrieval**: semantic search is combined with keyword matching for higher recall.
- **Fallback behavior**: if transformer summarization is unavailable, the system uses extractive summarization.
- **Modularity**: model providers, document processing, and retrieval components are separated cleanly.

## Technical stack

- Python 3.10+
- FastAPI backend
- React 18 + Next.js 14 frontend
- Tailwind CSS
- FAISS vector search
- BM25 keyword retrieval
- HuggingFace Transformers and SentenceTransformers
- Docker support for local deployments

## Project structure

- `backend/` — API, document processing, retrieval, and model integration
- `frontend/` — web UI and user workflow
- `docs/` — architecture, deployment, and implementation notes
- `data/` — sample indexes, paper registry, and cache files
- `tests/` — app-level tests for core functionality

## How to run locally

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pytest
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open the frontend at `http://localhost:3000` and the API docs at `http://localhost:8000/docs`.

### Environment variables

Create a `.env` file with the values you need.

Example for a provider:

```bash
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=your_key
OPENROUTER_MODEL=deepseek/deepseek-v4-flash:free
USE_LOCAL_SUMMARIZATION=true
```

Example for local development without an external LLM:

```bash
LLM_PROVIDER=mock
USE_LOCAL_SUMMARIZATION=true
```

## API highlights

- `POST /api/v1/papers/upload` — upload and index a PDF
- `GET /api/v1/papers` — list all indexed papers
- `DELETE /api/v1/papers/{paper_id}` — delete a paper and update the index
- `POST /api/v1/chat` — ask questions over the paper collection
- `POST /api/v1/compare` — compare multiple papers side-by-side

## Testing

Run tests from the backend folder:

```bash
cd backend
pytest -v
```

## What this project demonstrates

- Full-stack engineering with a modern React frontend and Python backend
- Retrieval-augmented generation tailored for research use cases
- Evidence-aware QA instead of hallucination-prone answers
- Modular document processing and indexing
- Testable model fallback strategies

## Future improvements

- richer paper metadata extraction,
- author/date filtering,
- ranked comparison reports,
- user accounts and persistence,
- citation export and note-taking.

## Documentation available

- `docs/API.md` — API details
- `docs/ARCHITECTURE.md` — design notes
- `docs/DEPLOYMENT.md` — deployment instructions
- `docs/HYBRID_RETRIEVAL.md` — retrieval strategy
- `docs/GROUNDING_VALIDATION.md` — grounding and evidence rules


## License

MIT
