# Roadmap

## Phase 0 — Foundation

- [x] Define system boundary
- [x] Define v0.1 core loop
- [ ] Implement typed request/result models
- [ ] Implement provider interface
- [ ] Implement resource manager interface
- [ ] Implement continuity interface
- [ ] Implement permission interface
- [ ] Add unit tests

## Phase 1 — PI-001 Core Loop

```text
Task -> Identity -> Permission -> Resource Check -> Router -> Provider -> Telemetry -> Continuity
```

Success criterion: one controlled request can travel through the entire loop with deterministic telemetry and no provider-specific logic leaking into the core.

## Phase 2 — Local Intelligence

- Add local-model provider adapter.
- Add offline execution path.
- Add local continuity/cache behavior.
- Test operation when cloud providers are unavailable.

## Phase 3 — Multi-Provider Resource Orchestration

- Provider availability tracking.
- Quota/limit awareness.
- Task classification.
- Context-size awareness.
- Latency and cost measurement.
- Provider selection policies.
- Fallback routing.

## Phase 4 — Tool Boundary

Add controlled adapters for tools such as files, GitHub, Notion, email, calendar, browser, and local devices.

No tool receives unrestricted access by default.

## Phase 5 — Advanced Continuity

Evaluate integration with Wison Kernel and Glyphin through explicit adapters and experiments.

Do not merge their identities into the Personal Intelligence core.

## Phase 6 — Personal Intelligence

The system should become capable of maintaining a durable, portable continuity layer across replaceable AI providers and tools.
