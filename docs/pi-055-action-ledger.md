# PI-055 — Accountable Action Ledger

## Purpose

Create a durable-style history of consequential Personal Intelligence actions without storing the user's sensitive payload.

## Ledger stages

An action can leave an inspectable trail such as:

`planned → confirmed → authorized → executing → provider_accepted → externally_confirmed`

Failures, cancellation, deferral, retry, and human-review decisions can also be recorded as explicit stages.

## What is recorded

Each ledger entry binds:
- task ID
- execution intent ID
- operation
- target
- stage
- human-readable statement
- timestamp
- optional evidence confidence

The reference ledger intentionally excludes prompts, message bodies, credentials, tokens, and other sensitive payloads.

## Why this matters

The user should eventually be able to ask:

> What did you do?
> Why did you do it?
> What was I approving?
> What actually happened?
> What evidence proves it?
> What remains uncertain?

The ledger provides the chronological spine needed to answer those questions.

## Architecture

`Intent → Authorization → Action Plan → Execution → External Effect → Evidence → Completion Claim → Action Ledger`

## Next step

PI-056 should add **ledger event types and lifecycle validation** so the ledger can detect impossible or contradictory state transitions instead of acting as a passive log.
