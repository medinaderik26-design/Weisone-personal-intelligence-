# PI-018 — Work Queue & Scheduler

## Purpose

Personal Intelligence should not lose work simply because the preferred AI provider is temporarily unavailable or out of capacity.

PI-018 introduces a provider-neutral queue that preserves the task and lets a higher-level execution layer retry it when a legitimate execution path becomes available.

## Behavior

```text
Task
  ↓
Attempt execution
  ↓
Available path?
  ├── Yes → Execute → Evidence
  └── No  → Queue → Retry later
```

The queue also supports task priority so urgent work can move ahead of lower-priority work.

## Safety rules

- A task is identified by its `task_id`.
- Duplicate queued tasks are rejected.
- Successful tasks are removed from the pending queue.
- Retryable capacity failures preserve the task in the queue.
- Unexpected execution failures are recorded separately rather than silently retried.
- The scheduler does not invent provider capacity, quota reset times, token counts, costs, or quality scores.
- The scheduler does not bypass permissions or privacy constraints.

## Important boundary

PI-018 is intentionally not the final execution engine. It is a work-preservation layer.

The eventual architecture is:

```text
Task
 ↓
Permission / Privacy
 ↓
Provider Eligibility
 ↓
Performance + Resource Fusion
 ↓
Scheduler
 ↓
Execution
 ↓
Execution Evidence
 ↓
Continuity + Feedback
```

A future scheduler integration can distinguish among provider failure, quota exhaustion, known reset windows, local fallback, and deferred work without changing the core task contract.

## Why this matters

The practical problem is not merely choosing a model. It is managing a person's work when multiple AI systems impose different capacity limits.

The system must preserve the work even when a resource disappears.

> Capacity pressure should change the execution path, not destroy the work.

## Next step

PI-019 should establish **idempotent execution and retry policy**, so a queued task can be safely retried without accidentally performing the same external action twice.