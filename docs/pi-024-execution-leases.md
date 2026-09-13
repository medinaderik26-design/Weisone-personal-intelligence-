# PI-024 — Execution Leases & Heartbeats

PI-024 adds a lease mechanism that lets Personal Intelligence distinguish an active worker from abandoned execution.

## Contract

Each lease identifies:

- `task_id` — logical work item
- `owner_id` — worker/process holding execution responsibility
- `acquired_at` — lease start
- `heartbeat_at` — most recent liveness signal
- `expires_at` — automatic expiration boundary

## Lifecycle

```text
Queued
  ↓
Lease acquired
  ↓
Running + heartbeats
  ↓
Completed → release

or

Running
  ↓
Worker disappears
  ↓
Heartbeat stops
  ↓
Lease expires
  ↓
Recovery may inspect the task
```

## Safety rules

- Only one owner may hold an active lease for a task.
- An expired lease may be acquired by another owner.
- A heartbeat must come from the current owner.
- Heartbeats renew the lease for an explicit TTL.
- Lease expiration is evidence that ownership ended; it is **not** proof that external work failed or did not complete.
- External side effects still require the PI-019 idempotency boundary before retry.

## Why this matters

Without a lease, `running` is ambiguous. With a lease, the system can reason about liveness separately from completion.

That distinction becomes important when Personal Intelligence eventually performs long-running work across local models, cloud providers, tools, and external services.

## Current scope

This is an in-memory reference implementation. Durable lease persistence and heartbeat coordination should be added only after the contract is tested. The public repository contains no real credentials or personal execution data.

## Next step

PI-025 should connect leases to persistent work state and recovery, then test simulated worker crashes and safe reassignment.
