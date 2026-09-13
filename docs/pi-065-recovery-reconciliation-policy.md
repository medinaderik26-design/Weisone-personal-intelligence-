# PI-065 — Recovery Reconciliation Policy

## Purpose

PI-065 gives Personal Intelligence a controlled response to recovery drift.

PI-064 detects changes. PI-065 classifies those changes without pretending every difference is an error.

## Classifications

### No drift

Snapshots are equivalent.

**Action:** continue.

### Expected progression

Only recovery-narrative fields changed, such as ledger stage or recovery explanation.

**Action:** continue.

### Recoverable divergence

Durable work state changed, such as status, attempt count, or provider.

**Action:** re-inspect the current recovery state before execution.

### Human-review-required divergence

Mixed or identity-sensitive changes appear, especially changes involving execution identity.

**Action:** stop automatic progression and require human review.

## Safety rule

Drift detection describes change. The reconciliation policy decides how cautious the system must become.

A provider change or execution-identity change is not treated as an ordinary progress update.

## Architecture

`Recovery Snapshot → Drift Detector → Reconciliation Policy → Continue / Reinspect / Human Review`

The policy does not execute work and does not grant authorization.

## Next step

PI-066 should connect this policy to the scheduler/recovery controller so classified drift can actually block or requeue work at the execution boundary.
