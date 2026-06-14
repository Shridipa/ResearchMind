# AI Operations Platform

The AI Operations Platform is an enterprise-grade multi-agent orchestration system designed for complex, retrieval-augmented research and operational tasks. It provides a robust, scalable backend for deploying autonomous agents capable of task decomposition, structured reasoning, and audited tool execution.

## System Intent

This project serves as a reference implementation for large-scale AI operations. Instead of relying on single-shot LLM queries, the platform utilizes a multi-agent framework where specialized personas (Planner, Researcher, Reasoner, Summarizer) collaborate through a directed acyclic graph (DAG). This approach significantly reduces hallucination rates, enforces explicit reasoning steps, and ensures all outputs are firmly grounded in retrieved evidence.

The platform is designed with enterprise security and observability in mind, incorporating strict role-based access controls for tool execution and comprehensive distributed tracing for performance monitoring.

## Core Capabilities

*   **Multi-Agent Orchestration**: Agent workflows are managed as state graphs, allowing for conditional routing, error recovery, and complex reasoning pipelines.
*   **Enterprise Tool Registry**: Agents interact with external systems through a dynamic, secure tool registry featuring strict input validation and immutable audit logging.
*   **Model Context Protocol (MCP)**: Native support for JSON-RPC 2.0 MCP server and client architectures, enabling standard integration with third-party tools and platforms.
*   **Provider Agnostic LLM Layer**: The core abstraction supports switching between AWS Bedrock (Claude 3, Titan, Nova), OpenRouter, Gemini, and OpenAI with built-in rate limiting and token tracking.
*   **Hybrid Retrieval (RAG)**: Combines dense vector search (PGVector, FAISS) with sparse keyword retrieval (BM25) for high-accuracy evidence extraction.
*   **Comprehensive Observability**: Integrated OpenTelemetry for distributed tracing across agent executions and API requests.

## Architecture

The system is organized into decoupled layers:
1.  **Frontend**: A Next.js and React application providing user interfaces for workflow initiation, document management, and chat.
2.  **API Gateway**: A FastAPI backend exposing RESTful endpoints, secured by JWT authentication.
3.  **Graph Engine**: The LangGraph-based workflow executor managing state transitions between agents.
4.  **Agent Layer**: Independent LangChain-compatible agents that perform specific cognitive functions.
5.  **Infrastructure**: PostgreSQL for relational data and vector storage, Redis for high-speed caching, and AWS ECS for deployment.

## Technical Stack

### Backend
*   **Framework**: Python 3.12, FastAPI
*   **AI Orchestration**: LangChain, LangGraph
*   **Model Providers**: AWS Bedrock SDK (Boto3), OpenAI, Google Generative AI
*   **Data Storage**: PostgreSQL (asyncpg, SQLAlchemy), PGVector, Redis
*   **Observability**: OpenTelemetry

### Frontend
*   **Framework**: Node.js, Next.js 14, React 18
*   **Styling**: Tailwind CSS, TypeScript

### Infrastructure
*   **Deployment**: Docker, Docker Compose
*   **Infrastructure as Code**: Terraform
*   **Testing**: Pytest

## Getting Started

### Local Development

1.  **Start Infrastructure Services**:
    The system requires PostgreSQL and Redis. Start them using Docker Compose:
    ```bash
    docker-compose up postgres redis -d
    ```

2.  **Configure Environment**:
    Copy `configs/.env.example` to `.env` and configure your LLM provider credentials (e.g., AWS Bedrock or OpenRouter keys).

3.  **Run the Backend**:
    ```bash
    cd backend
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    pip install -r requirements.txt
    uvicorn app.main:app --reload
    ```

4.  **Run the Frontend**:
    ```bash
    cd frontend
    npm install
    npm run dev
    ```

The API documentation will be available at `http://localhost:8000/docs` and the user interface at `http://localhost:3000`.

## Documentation

Detailed architectural decisions and implementation notes are available in the `docs/` directory:
*   `PHASE_1_ARCHITECTURE.md`: Infrastructure and database configurations.
*   `PHASE_2_BEDROCK.md`: AWS Foundation Model integration strategies.
*   `PHASE_3_AGENTS.md`: Multi-agent persona design.
*   `PHASE_4_LANGGRAPH.md`: State graph execution and error handling.
*   `PHASE_5_TOOLS.md`: Tool registry, auditing, and permissions.
*   `PHASE_6_MCP.md`: Model Context Protocol specifications.

## License

This project is licensed under the MIT License.
