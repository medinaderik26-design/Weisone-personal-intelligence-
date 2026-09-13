# PI-084 — Policy Dispatch Bridge

## Purpose

PI-084 binds a durable recovery policy boundary decision to a deterministic scheduler dispatch identity without collapsing the evidence boundaries.

The bridge answers one question:

> Is this policy decision eligible to become a scheduler dispatch request, and what deterministic identity would represent that request?

It does **not** authorize an external action, execute a task, or claim that a scheduler accepted the work.

## Boundary

```text
Recovery Snapshot
      ↓
Projection Drift
      ↓
Policy Classification
      ↓
Durable Policy Decision
      ↓
Policy Execution Boundary
      ↓
Policy Dispatch Bridge       ← PI-084
      ↓
Durable Dispatch Claim       ← PI-070
      ↓
Scheduler Acknowledgement
      ↓
Execution
      ↓
Provider Accepted
      ↓
Externally Confirmed
```

## Rules

- Only an explicit `continue` decision with `handoff_allowed=True` can produce an eligible dispatch request.
- `reinspect` and `human_review` produce blocked requests with no dispatch key.
- Unknown actions fail closed even if an upstream object incorrectly marks them as allowed.
- The dispatch key is deterministic for the same task, classification, and action.
- A dispatch request is **not** a durable dispatch claim. PI-070 remains responsible for the actual SQLite-backed claim.
- A dispatch claim is **not** scheduler acknowledgement.
- Scheduler acknowledgement is **not** proof execution started.
- Provider acceptance is **not** proof of external completion.
- External completion remains the strongest completion boundary and must be independently evidenced.

## Identity

The bridge uses the same deterministic identity shape as the existing PI-070 durable recovery dispatch store:

`SHA-256(task_id | classification | action)`

This keeps the bridge compatible with the durable claim layer without making the bridge itself responsible for persistence.

## Safety boundary

The bridge intentionally contains no authorization grant, provider call, scheduler call, retry, or external side effect.

Its output is a request-shaped fact:

- task identity
- policy classification
- policy action
- deterministic dispatch identity when eligible
- eligibility decision
- reason

The next layer may use the dispatch identity to attempt a durable claim. If the claim already exists, the system can preserve idempotency rather than creating a second logical recovery action.

## Evidence discipline

The system must preserve the distinction between:

**Policy decision → dispatch eligibility → durable claim → scheduler acknowledgement → execution → provider acceptance → external confirmation**

No earlier stage may be promoted into evidence for a later stage.
