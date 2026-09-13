# PI-026 — Scheduler Recovery Integration

PI-026 establishes the boundary between recovery decisions and the work scheduler.

## Flow

```text
Persisted WorkState
       ↓
Recovery Inspection
       ↓
RecoveryDecision
       ↓
SchedulerRecoveryController
       ↓
ENQUEUE / RETRY / REROUTE / DEFER / HUMAN_REVIEW
```

The controller translates decisions into queue operations. It does not execute the task itself.

## Safety boundary

`HUMAN_REVIEW` remains `HUMAN_REVIEW`. It can never silently become retry or execution.

`REROUTE` remains a separate action so provider substitution is visible and can be checked against privacy, resource, and authorization constraints before execution.

`RETRY` is only a scheduling instruction. Actual retry still requires the PI-019 idempotency and retry controls.

## Why this matters

Personal Intelligence can now preserve work through a failure and hand the recovered work back to the scheduling layer without collapsing uncertainty into an automatic action.

Next: connect scheduler recovery to provider/resource eligibility and actual tokenizer-aware resource accounting.
