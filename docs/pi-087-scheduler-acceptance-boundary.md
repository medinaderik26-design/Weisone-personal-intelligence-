# PI-087 — Scheduler Handoff → Scheduler Acceptance Boundary

## Purpose

PI-087 records the point where a scheduler explicitly acknowledges a previously prepared handoff.

It closes the gap between:

`durable claim → handoff request → scheduler acceptance`

without treating acceptance as proof that execution has started or that an external effect occurred.

## Evidence chain

```text
Policy Decision
      ↓
Policy Boundary
      ↓
Dispatch Request
      ↓
Durable Dispatch Claim
      ↓
Scheduler Handoff Request
      ↓
Scheduler Handoff Receipt
      ↓
Scheduler Acceptance Receipt       ← PI-087
      ↓
Execution
      ↓
Provider Accepted
      ↓
Externally Confirmed
```

## Rules

- Acceptance requires a durable `handed_off` receipt first.
- Acceptance is idempotent for the same dispatch identity and intent.
- Task ID, dispatch key, and execution intent identity cannot change.
- An ineligible handoff cannot be accepted.
- The boundary records scheduler acceptance only.
- Scheduler acceptance does not prove execution started.
- Scheduler acceptance does not prove a provider accepted the work.
- Scheduler acceptance does not prove an external side effect occurred.

## Safety boundary

PI-087 performs no provider call and no external side effect. It records evidence supplied by the scheduler boundary.

The next boundary must establish execution state independently rather than inferring it from acceptance.
