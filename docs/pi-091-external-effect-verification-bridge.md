# PI-091 — Provider Acceptance → External-Effect Verification

## Purpose

PI-091 creates the boundary between a provider confirming acceptance and Weisone attempting to verify that the intended external effect actually occurred.

## Evidence chain

```text
Policy
  ↓
Dispatch Claim
  ↓
Scheduler Handoff
  ↓
Scheduler Accepted
  ↓
Execution Started
  ↓
Provider Accepted
  ↓
Verification Request       ← PI-091
  ↓
External Effect Verified
```

## Rules

- Provider acceptance is required before an external-effect verification request can become eligible.
- Provider rejection blocks verification.
- A verification request is not verification evidence.
- The bridge does not call an external service.
- The bridge does not infer completion from provider acceptance.
- The bridge carries task, dispatch, intent, provider, operation, and target identity so verification can be tied to the intended action.
- External confirmation remains a separate evidence boundary.

## Why this matters

A provider can accept a request while the intended real-world effect later fails, is delayed, is partially completed, or becomes ambiguous. Weisone therefore treats external completion as something that must be independently observed rather than inferred.

The next layer should consume the verification request and produce an explicit verification result with an evidence source. Unknown remains unknown.
