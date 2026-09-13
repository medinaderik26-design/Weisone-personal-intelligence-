# PI-078 — Durable End-to-End Lifecycle Projection

PI-078 adds a projection layer that reconstructs the evidence Weisone currently has for a task.

## Projection

The projection reports:

- task ID
- execution intent ID
- ordered ledger stages
- current known stage
- whether external completion evidence exists

Example chain:

`authorized → handed_off → accepted → executing → provider_accepted → externally_confirmed`

## Truth boundary

The projection does not fill gaps. If the ledger ends at `accepted`, it does not infer `executing`. If it ends at `provider_accepted`, it does not infer external completion.

`evidence_complete` is true only when the known ledger state reaches `externally_confirmed`.

## Identity protection

A task projection rejects multiple execution intent IDs for the same task. This prevents the reconstructed history from silently combining unrelated execution attempts.

## Architectural role

The projection is read-only. It does not authorize, execute, retry, reroute, or verify external effects.

It is the observability layer for the evidence chain.

## Next step

PI-079 should make the projection durable/versioned so Weisone can reconstruct the lifecycle as it appeared at different recovery points across restarts.
