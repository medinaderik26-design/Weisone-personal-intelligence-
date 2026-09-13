# PI-064 — Recovery Snapshot Drift Detection

## Purpose

PI-064 compares recovery snapshots across restarts and identifies what changed without assuming which snapshot is correct.

## Detected drift

The detector can identify changes in:
- work status
- attempt count
- provider
- latest ledger stage
- recovery action
- recovery reason
- execution intent

## Architecture

`Snapshot N → Snapshot N+1 → Drift Detector → Explicit Changes`

A drift result is descriptive. It does not silently resolve the conflict.

## Safety

Different task IDs cannot be compared.

Drift does not automatically mean corruption. A task legitimately moving from `provider_accepted` to `externally_confirmed` is expected progression. Conversely, unexpected changes can trigger review before another external action occurs.

## Next step

PI-065 should add a **recovery reconciliation policy** that classifies detected drift as expected progression, recoverable divergence, or human-review-required divergence.
