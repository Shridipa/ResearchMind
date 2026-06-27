# ResearchMind 2.0 Engineering Quality Gate

This gate applies during development, code review, and release validation. A feature is not done because the UI renders or an endpoint returns 200. It is done only when it is integrated, observable, secure, testable, and maintainable.

## Operating Standard

ResearchMind 2.0 is evaluated as an enterprise research platform, not a feature demo. Every change must improve at least one of:

- Scalability
- Reliability
- Maintainability
- Security
- Performance
- Testability
- Observability
- User experience

If a requested implementation conflicts with these goals, document the risk and propose a safer alternative before merging.

## Required Development Flow

For every meaningful feature or fix:

1. Review existing structure, naming, API conventions, auth flow, services, and reusable components.
2. Identify dependencies, breaking changes, security risk, and integration points.
3. Design the implementation using the existing layered architecture.
4. Implement incrementally and keep business logic out of API routes and UI event handlers.
5. Verify backend, frontend, database, worker, Redis, and WebSocket integration where relevant.
6. Run automated checks and record anything not run.
7. Perform a self-review before requesting review.

## Architecture Gate

Changes must preserve this dependency direction:

```text
Presentation -> API -> Service -> Repository -> Database
```

Infrastructure dependencies such as Redis, Celery, storage, vector search, monitoring, and LLM providers must stay behind service interfaces. Avoid route-level orchestration, duplicated services, and direct database or Redis calls from UI code.

## Backend Gate

Every endpoint must have:

- Input validation
- Authentication unless explicitly public
- Authorization for workspace or role-sensitive actions
- Structured error handling with meaningful status codes
- Logging for important state transitions
- Audit logging for user or admin actions
- Transaction safety for database writes
- Background execution for long-running AI or document operations

Business logic belongs in services. API routes should validate, authorize, call services, and shape responses.

## Frontend Gate

Every screen or workflow must include:

- Consistent dashboard design language
- Loading, empty, success, and error states
- Responsive layouts
- Keyboard-accessible controls
- Clear recovery paths after failures
- No duplicated API clients or duplicated domain components
- No hidden dependency on demo-only data unless explicitly labeled

## Real-Time Gate

Do not fake real-time behavior for production flows. If a feature claims live behavior, verify:

- Celery or async worker emits progress
- Redis Pub/Sub or event bus publishes events
- WebSocket broadcasts updates
- Frontend reconnects and recovers gracefully
- Polling fallback is explicit and bounded

Simulated behavior must be named as demo mode in code and documentation.

## AI Workflow Gate

AI and document operations must not block HTTP requests when they can exceed normal request latency. Required production path:

1. Create job record.
2. Dispatch worker task.
3. Persist progress.
4. Publish progress event.
5. Broadcast WebSocket update.
6. Store result and expose status/result endpoints.

## Security Gate

Before merge, verify:

- No secrets are committed.
- JWT validation and expiry are enforced.
- RBAC checks exist on protected routes.
- Workspace access is scoped.
- File upload type and size are validated.
- User input is sanitized or safely rendered.
- SQL is parameterized.
- Demo or guest bypasses are isolated from production configuration.

## Observability Gate

Important actions should produce:

- Structured logs
- Audit entries
- Metrics
- Health status where applicable
- Worker/queue visibility
- Useful error messages without leaking secrets

## Test Gate

Minimum checks for affected areas:

- Happy path
- Invalid input
- Authentication failure
- Permission failure
- Backend unavailable or dependency unavailable
- Worker failure for async jobs
- Redis/WebSocket unavailable for real-time flows
- Frontend typecheck
- Backend tests or focused compile/import checks

When a check cannot be run, document why and capture residual risk.

## Running Project Checklist

### Complete Enough For Demo

- Landing page routes to dashboard without sign-in friction.
- Dashboard pages render from shared layout.
- Demo data is available for documents, activity, metrics, and jobs.
- Frontend typecheck passes.

### Partial / Needs Hardening

- Enterprise routes rely heavily on JSON demo storage.
- PostgreSQL models exist but are not the primary persistence path for many enterprise endpoints.
- Redis/Celery/WebSocket paths have graceful fallbacks but need integration tests.
- Guest access is useful for demos but must be isolated from production.
- Observability exists at the framework level but lacks full trace coverage per workflow.

### Known Risks

- Port conflicts can make the frontend talk to the wrong backend if `NEXT_PUBLIC_API_BASE_URL` is stale.
- Runtime environments without optional dependencies can fail at import time.
- Demo-mode claims can overstate production readiness unless clearly labeled.
- API keys must remain in local ignored env files or deployment secrets only.

## Definition Of Done

A feature is complete only when:

- Backend implementation is finished.
- Frontend implementation is finished.
- Persistence path is defined and tested.
- API integration is verified.
- Auth and permissions are verified.
- Error handling and logs are implemented.
- Real-time updates are verified if claimed.
- Mobile/responsive behavior is checked.
- Accessibility is reviewed.
- Performance impact is reviewed.
- TypeScript has no errors.
- Backend tests or focused compile/import checks pass.
- Known gaps are documented.
