# PI-042 — Authorization Decision Receipts

## Purpose

Bind an authorization decision to a specific task, provider, task type, subject, and authorization epoch so a worker can verify it immediately before execution.

## Receipt model

A receipt contains:
- task ID
- subject
- provider
- task type
- authorization epoch
- allow/deny result
- reason
- issuance timestamp

## Final check

Before execution, the receipt guard verifies:

1. The original decision allowed execution.
2. The authorization epoch is still current.
3. No matching revocation exists.

Only when all three checks succeed does the receipt remain executable.

## Architecture

`Authorization Decision → Receipt + Epoch → Queue/Worker → Receipt Guard → Execute`

With revocation:

`Consent Change → Revocation → Epoch/Receipt Check → Existing receipt rejected`

## Why this matters

This creates a compact authorization artifact that can travel with queued work without trusting the worker's memory of an earlier permission state.

The receipt is not a credential and does not grant access by itself. It is evidence that a decision was made and a freshness check that must still succeed.

## Security

Do not put sensitive user payloads, provider secrets, API keys, or authentication tokens into receipts.

## Next step

PI-043 should address **safe cancellation and compensation semantics** for work that has already started or may have produced an external side effect. Revocation can stop future execution; it cannot automatically undo an action that already happened.
