# PI-023 — Recovery Execution Safety Gate

PI-023 places a safety boundary between recovered work and actual execution.

## Purpose

PI-021 made work durable. PI-022 decides what should happen after interruption. PI-023 asks the final question before execution:

> **Is this recovered operation actually allowed to run?**

The gate combines three existing controls:

1. Recovery decision
2. Idempotency check
3. Retry policy

```text
Persisted WorkState
       ↓
RecoveryCoordinator
       ↓
RecoveryDecision
       ↓
Idempotency Check
       ↓
Retry / Execution Policy
       ↓
┌───────────────┐
│ ALLOW EXECUTE │
│ or BLOCK      │
└───────────────┘
```

## Safety behavior

- A successful idempotency receipt blocks duplicate execution.
- Interrupted `running` work with unknown external completion requires review unless explicit rerouting is available.
- Queued work can resume when a provider is available.
- Failed work can retry only when retry policy permits it.
- Rerouting is an explicit recovery action, not an automatic assumption.
- The gate evaluates safety; it does not perform external side effects.

## Why this matters

This is the boundary that will eventually protect real-world operations. Sending an email, modifying a file, pushing code, making a transaction, or calling an external service should not become repeatable merely because the process restarted.

The system must know the difference between:

**work was persisted**

and

**work was safely completed**.

## Next step

PI-024 should introduce execution leases/heartbeats so the system can distinguish an actively running worker from genuinely abandoned work after a crash.
