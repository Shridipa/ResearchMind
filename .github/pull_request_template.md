## Summary

- 

## Architecture Review

- [ ] Reuses existing services, API clients, stores, and components
- [ ] Preserves Presentation -> API -> Service -> Repository -> Database layering
- [ ] Keeps Redis, Celery, storage, vector search, and LLM providers behind service boundaries
- [ ] Avoids route-level business logic and duplicated abstractions

## Backend Quality

- [ ] Inputs are validated
- [ ] Authentication and authorization are enforced where required
- [ ] Workspace/RBAC boundaries are preserved
- [ ] Errors return meaningful HTTP status codes
- [ ] Important state transitions emit structured logs and/or audit entries
- [ ] Long-running AI/document operations run asynchronously

## Frontend Quality

- [ ] Loading, empty, error, and success states are handled
- [ ] UI follows the shared dashboard design language
- [ ] Keyboard and responsive behavior were checked
- [ ] No new duplicate API clients/components were introduced

## Real-Time And AI Workflow

- [ ] Worker progress is persisted
- [ ] Redis/event bus publication is verified or the fallback is documented
- [ ] WebSocket updates are verified or the fallback is documented
- [ ] Simulated/demo behavior is clearly labeled

## Security

- [ ] No secrets, tokens, logs, or local env files are committed
- [ ] File uploads and user input are constrained safely
- [ ] Demo/guest access cannot leak into production accidentally

## Evaluation

- [ ] Backend tests pass
- [ ] Frontend typecheck/build pass
- [ ] Dependency-unavailable path tested or documented
- [ ] Benchmark impact recorded, if retrieval behavior changed

## Grounding and Safety

- [ ] Answers remain source-grounded
- [ ] Confidence behavior is documented for new features

## Residual Risk

- 
