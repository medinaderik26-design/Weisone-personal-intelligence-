# PI-088 — Scheduler Acceptance → Execution Start Boundary

## Purpose

PI-088 creates an explicit boundary between scheduler acceptance and actual execution start.

The system must not treat a scheduler saying **accepted** as proof that execution has begun.

## Evidence chain

```text
Policy
  ↓
Dispatch Eligibility
  ↓
Durable Dispatch Claim
  ↓
Scheduler Handoff
  ↓
Scheduler Accepted
  ↓
Execution Started       ← PI-088
  ↓
Provider Accepted
  ↓
Externally Confirmed
```

## Rules

- Execution start requires scheduler acceptance.
- A rejected or unconfirmed scheduler result cannot produce `started=True`.
- Task ID, dispatch key, and execution intent ID must be present.
- Execution start is its own evidence event; it does not prove provider acceptance.
- Execution start does not prove an external side effect completed.
- No token, prompt, credential, or sensitive payload is stored by this boundary.

## Boundary discipline

PI-088 does not call a provider, execute the task, or claim completion. It records the logical transition that execution is permitted to begin after scheduler acceptance.

That distinction matters for crash recovery: a system crash after this boundary means execution may have started, but later evidence is still required to establish provider acceptance or external completion.
