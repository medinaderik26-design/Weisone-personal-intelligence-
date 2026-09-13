# PI-021 — Durable Local Storage

PI-020 established the provider-neutral `WorkState` contract. PI-021 adds a SQLite-backed local adapter so unfinished work can survive process termination and machine restarts.

## Why local first

Personal Intelligence is intended to remain useful when cloud services are unavailable. A local work-state store avoids making recovery dependent on the same network or provider that may have failed.

## Recovery model

```text
Task
 ↓
WorkState persisted
 ↓
Execute
 ↓
Process/network/provider failure
 ↓
Restart / recovery
 ↓
Load queued + running states
 ↓
Idempotency check
 ↓
Resume / reroute / retry / human intervention
```

## Important boundary

SQLite persistence records what the Personal Intelligence system knew about a task. It does not prove that an external side effect occurred.

A recovered `running` task therefore requires the PI-019 idempotency policy before it is executed again.

## Design rules

- Stable `task_id` is the recovery key.
- State writes use an atomic SQLite transaction.
- `queued` and `running` states are recoverable.
- Completed work is not returned as unfinished work.
- Unknown external completion remains unknown.
- The storage layer does not make provider, quality, cost, or token claims.
- The adapter can later be replaced by another authorized local or encrypted store without changing the work-state contract.

## Security direction

The current adapter is a development foundation. Production use should add encryption-at-rest where appropriate, file permissions, backup policy, retention controls, corruption handling, and protection for any sensitive metadata before personal data is persisted.

## Next step

PI-022 should add a recovery coordinator that converts recovered states into explicit actions: resume, retry, reroute, defer, or require human review.
