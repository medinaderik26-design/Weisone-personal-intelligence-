# PI-033 — Local-First Fallback & Provider Failover

## Purpose

Keep work moving when a preferred provider is unavailable, exhausted, or otherwise excluded, while respecting privacy and explicit user policy.

## Policy

1. High-privacy tasks are local-only.
2. Normal tasks may fall back to local by default.
3. The user can disable local fallback with `allow_local_fallback=False`.
4. If local fallback is unavailable, an alternate eligible provider may be selected.
5. If no safe provider exists, work is deferred or sent to human review.
6. Failover never bypasses the permission boundary.

## Architecture

`Task → Primary Routing → Failure/Quota Event → FailoverPolicy → Local / Alternate / Defer / Human Review`

## Important distinction

Failover is a **decision layer**, not an execution layer. The policy chooses what should happen; normal permissions, idempotency, scheduling, and execution controls still apply before work is actually performed.

## Why this matters

The personal intelligence should not make the user manually switch systems every time a cloud provider reaches a limit. Local intelligence becomes a resilience path rather than a replacement for every provider.

## Security

No credentials, provider keys, personal data, or proprietary model code belong in this policy layer. Provider adapters remain replaceable and permission-bound.

## Next step

PI-034 should establish the **Personal Data Boundary / Data Minimization Policy**, defining exactly what information may cross from the personal intelligence into each provider or tool.
