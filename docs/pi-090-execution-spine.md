# PI-090 — First Integrated Execution Spine

## Purpose

PI-090 stops adding isolated boundaries and begins connecting the existing evidence layers into one executable orchestration path.

The spine currently covers the pre-provider portion of the lifecycle:

```text
Task
  ↓
Policy Boundary
  ↓
Dispatch Request
  ↓
Durable Dispatch Claim
  ↓
Execution Start
  ↓
Provider Acceptance
```

External completion remains intentionally outside this spine until its verification boundary is implemented.

## Design rule

The spine coordinates existing boundaries. It does not weaken them.

Each stage retains its own evidence meaning:

- policy eligibility is not authorization
- a dispatch request is not a durable claim
- a durable claim is not scheduler acceptance
- execution start is not provider acceptance
- provider acceptance is not external completion

## Explicit execution identity

PI-090 requires an `intent_id` from the caller rather than deriving one from the task or dispatch claim.

This is deliberate. A task can produce multiple legitimate execution intents over its lifetime, while a durable dispatch claim identifies a specific recovery dispatch.

## Current API shape

`ExecutionSpine.prepare(...)`

Creates the policy dispatch request and attempts the durable claim.

`ExecutionSpine.start_execution(...)`

Requires a successful durable claim and creates explicit execution-start evidence using the caller-provided execution intent.

`ExecutionSpine.record_provider_acceptance(...)`

Requires execution-start evidence and records provider acceptance or rejection.

## Safety behavior

A policy decision that blocks handoff cannot start execution.

A missing durable claim cannot start execution.

Provider acceptance cannot occur before execution-start evidence.

No external provider is called by this spine. No completion is inferred.

## Next integration target

PI-091 should connect the spine to the external-effect verification boundary so the full path can be exercised without treating provider acceptance as proof of real-world completion.
