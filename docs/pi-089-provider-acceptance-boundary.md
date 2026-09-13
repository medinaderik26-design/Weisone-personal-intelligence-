# PI-089 — Execution Start → Provider Acceptance Boundary

## Purpose

PI-089 creates an explicit evidence boundary between execution beginning and the provider accepting the execution request.

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
Execution Started
  ↓
Provider Accepted       ← PI-089
  ↓
Externally Confirmed
```

## Rules

- Provider acceptance requires execution-start evidence.
- A provider rejection remains a recorded non-acceptance; it is not completion evidence.
- Provider acceptance is provider-side evidence only.
- Provider acceptance does not prove the external action completed.
- The task ID, dispatch key, execution intent ID, and provider identity remain attached to the evidence.
- No credentials, prompts, provider secrets, or sensitive payloads are stored here.

## Why this boundary matters

A request can be accepted by a scheduler and execution can begin without the provider successfully accepting the request. Conversely, provider acceptance can occur without the intended external side effect completing.

Therefore Weisone keeps these states distinct:

**scheduler acceptance ≠ execution start ≠ provider acceptance ≠ external completion**

PI-089 records only the provider-acceptance boundary. External completion requires its own verification evidence at a later stage.
