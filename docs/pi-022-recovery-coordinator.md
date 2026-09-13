# PI-022 — Recovery Coordinator

PI-022 turns recovered work state into an explicit recovery decision. It does not execute the decision.

## Actions

- **resume** — queued work can safely continue.
- **retry** — a failed attempt may be attempted again.
- **reroute** — an alternate provider/path is explicitly available.
- **defer** — work remains preserved but should wait.
- **human_review** — automatic continuation is unsafe or completion is uncertain.

## Recovery Rules

```text
Recovered State
      ↓
Safe to continue?
 ├── yes → Resume / Retry
 └── no
      ↓
Alternate path?
 ├── yes → Reroute
 └── no → Defer / Human Review
```

A particularly important case is a task that was `running` when the process disappeared. The system cannot assume whether an external side effect happened. Unless completion can be established safely, the default is human review; an explicitly available alternate path may produce a reroute decision.

## Separation of Concerns

`SQLiteWorkStateStore` persists state.

`RecoveryCoordinator` decides what should happen next.

The scheduler executes the resulting action.

The PI-019 idempotency layer protects retryable external operations.

This keeps recovery policy separate from execution and provider selection.

## Principle

> Recovery should preserve work first, then make the safest evidence-based decision about what happens next.

## Next Step

PI-023 should connect recovery decisions to the scheduler without allowing recovery logic to bypass permissions, idempotency, or provider eligibility.
