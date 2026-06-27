# ResearchMind 2.0 Enterprise

> **Enterprise AI Research Operating System** — multi-tenant workspaces, distributed document ingestion, event-driven architecture, real-time collaboration, RBAC security, and full observability.

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![License](https://img.shields.io/badge/license-Apache--2.0-green)
![Stack](https://img.shields.io/badge/stack-FastAPI%20%7C%20Next.js%20%7C%20Celery%20%7C%20Redis%20%7C%20PostgreSQL-purple)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     ResearchMind 2.0                         │
├──────────────┬──────────────┬───────────────┬───────────────┤
│   Next.js 14 │   FastAPI    │  Celery Workers│  Redis Pub/Sub│
│   Dashboard  │   REST API   │  (5 queues)    │  + WebSocket  │
├──────────────┴──────────────┴───────────────┴───────────────┤
│              PostgreSQL (metadata + audit)                    │
│              Vector Store  (FAISS embeddings)                 │
│              S3-Compatible Storage (documents)                │
├─────────────────────────────────────────────────────────────┤
│          Prometheus + Grafana (observability)                │
│          OpenTelemetry (distributed tracing)                 │
└─────────────────────────────────────────────────────────────┘
```

## Key Features

| Feature | Description |
|---------|-------------|
| 🏗️ **Multi-tenant Workspaces** | Organizations → Workspaces → Documents/Research |
| 🔄 **Distributed Ingestion** | 5-stage async pipeline: Upload → Chunk → Embed → Index → Ready |
| 📡 **Event-Driven Architecture** | Redis Pub/Sub domain events, WebSocket real-time updates |
| 🔐 **RBAC Security** | JWT + Refresh tokens, 5-level role hierarchy, permission guards |
| 🔍 **Hybrid Search** | BM25 keyword + semantic vector similarity combined |
| 📊 **Observability** | Prometheus metrics, Grafana dashboards, structured logging |
| 🛡️ **Audit System** | Append-only audit log (who, when, what, where) |
| 📋 **Document Versioning** | Full version history, comparison, and rollback |
| ⚡ **Real-time UI** | WebSocket-driven progress updates, notifications |
| 🚀 **Production Ready** | Docker Compose + Kubernetes manifests + GitHub Actions CI/CD |

---

## Quick Start (Local Dev)

### Prerequisites
- Docker & Docker Compose
- Python 3.12+
- Node.js 20+

### 1. Clone and configure
```bash
git clone https://github.com/yourorg/researchmind.git
cd researchmind
cp configs/.env.example configs/.env   # fill in API keys
```

### 2. Start all services
```bash
docker-compose up -d
```

This starts:
- **PostgreSQL** on `:5432`
- **Redis** on `:6379`
- **FastAPI Backend** on `:8000` → [http://localhost:8000/api/docs](http://localhost:8000/api/docs)
- **Celery Workers** (5 queues: documents, embeddings, research, cleanup, notifications)
- **Prometheus** on `:9090`
- **Grafana** on `:3001` (admin/admin)
- **Next.js Frontend** on `:3000`

### 3. Run database migrations
```bash
cd backend
alembic upgrade head
```

### 4. Start frontend (development mode)
```bash
cd frontend
npm install
npm run dev
```

---

## Architecture Details

### Backend Structure
```
backend/app/
├── api/
│   ├── v1/
│   │   ├── enterprise_routes.py   # Auth, Workspaces, Documents, Search, Admin
│   │   ├── routes/                # Existing RAG/Chat/Papers routes
│   │   └── router.py
│   └── websockets.py              # Redis Pub/Sub → WebSocket bridge
├── auth/
│   ├── jwt_handler.py             # JWT creation/verification
│   ├── rbac.py                    # Role/Permission matrix
│   └── dependencies.py            # FastAPI RBAC guards
├── domain/
│   └── models/                    # SQLAlchemy models (User, Workspace, Document, etc.)
├── events/
│   ├── domain_events.py           # Typed domain event dataclasses
│   └── event_bus.py               # Redis-backed async EventBus
├── services/
│   ├── ingestion_service.py       # Upload → Celery dispatch orchestration
│   └── audit_service.py           # Audit log writer
└── workers/
    ├── celery_app.py              # Celery config + queue routing
    ├── document_worker.py         # 5-stage ingestion pipeline
    ├── embedding_worker.py        # GPU-bound embedding tasks
    ├── research_worker.py         # Async AI research sessions
    ├── cleanup_worker.py          # GC for dead jobs/vectors
    └── notification_worker.py     # Email/in-app notifications
```

### Frontend Structure
```
frontend/app/
├── (dashboard)/
│   ├── layout.tsx         # Sidebar + command palette + animated transitions
│   ├── dashboard/         # Metrics, activity charts, ingestion tracker
│   ├── workspace/         # Workspace grid, team members, activity feed
│   ├── documents/         # Upload zone, status table, version history
│   ├── search/            # Hybrid/semantic/keyword search UI
│   └── admin/             # System health, queue monitor, audit logs, users
└── globals.css            # Enterprise design system (glassmorphism, tokens)

frontend/store/
└── appStore.ts            # Zustand: auth, WebSocket, real-time events
```

### RBAC Roles
| Role | Create WS | Delete WS | Upload | Delete Docs | Manage Users | Admin Panel |
|------|-----------|-----------|--------|-------------|--------------|-------------|
| SUPER_ADMIN | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| ORG_ADMIN | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| WORKSPACE_ADMIN | ❌ | ❌ | ✅ | ✅ | ✅ | ❌ |
| RESEARCHER | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| VIEWER | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

### Ingestion Pipeline
```
Document Upload (API)
       ↓
  IngestionService.start_ingestion()
       ↓
  ingestion_jobs (PENDING) → DB
       ↓
  Celery Task → documents queue
       ↓ ─────────────────────────────────────────┐
  PROCESSING  →  CHUNKING  →  EMBEDDING  →  INDEXING  →  COMPLETED
       ↓ (at each step)
  Redis PUBLISH "document_updates" channel
       ↓
  WebSocket pushes to connected browser clients
```

### Redis Pub/Sub Channels
| Channel | Events |
|---------|--------|
| `document_updates` | `DocumentUploadedEvent`, `DocumentProcessedEvent`, `IngestionProgressEvent` |
| `research_updates` | `ResearchGeneratedEvent` |
| `workspace_updates` | `WorkspaceCreatedEvent` |
| `notifications` | General user notifications |

---

## API Reference

Base URL: `http://localhost:8000/api/v1`

Interactive docs: [http://localhost:8000/api/docs](http://localhost:8000/api/docs)

### Auth
| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Get JWT tokens |
| POST | `/auth/refresh` | Refresh access token |

### Workspaces
| Method | Path | Description |
|--------|------|-------------|
| GET | `/workspaces` | List user's workspaces |
| POST | `/workspaces` | Create workspace |
| GET | `/workspaces/{id}` | Get workspace |
| POST | `/workspaces/{id}/members` | Invite member |
| DELETE | `/workspaces/{id}/members/{uid}` | Remove member |

### Documents
| Method | Path | Description |
|--------|------|-------------|
| POST | `/workspaces/{id}/documents` | Upload document (async) |
| GET | `/workspaces/{id}/documents` | List documents |
| DELETE | `/workspaces/{id}/documents/{docId}` | Soft-delete document |
| GET | `/ingestion-jobs/{jobId}` | Poll job status |

### Search & Admin
| Method | Path | Description |
|--------|------|-------------|
| POST | `/search` | Hybrid search |
| GET | `/admin/health` | System health |
| GET | `/admin/queue-stats` | Celery queue stats |
| GET | `/admin/audit-logs` | Paginated audit logs |

### WebSocket
```
ws://localhost:8000/ws/{workspace_id}?token={access_token}
```

---

## Deployment (Kubernetes)

```bash
kubectl apply -f infra/k8s/postgres-deployment.yaml
kubectl apply -f infra/k8s/redis-deployment.yaml
kubectl apply -f infra/k8s/app-deployments.yaml
```

---

## Monitoring

| Service | URL | Credentials |
|---------|-----|-------------|
| Grafana | http://localhost:3001 | admin / admin |
| Prometheus | http://localhost:9090 | — |
| API Metrics | http://localhost:8000/metrics | — |

---

## License

Apache 2.0 — see [LICENSE](LICENSE)
