# PI-079 — Durable Lifecycle Projections

PI-079 makes the PI-078 lifecycle projection persistent and versioned.

## Versioning

Each task receives its own monotonically increasing projection versions:

`task-1 → v1 → v2 → v3 ...`

A different task starts independently at v1.

## Why version the projection?

Recovery can change what Weisone knows. A versioned projection preserves the sequence of those observations rather than overwriting the previous picture.

This lets the system reconstruct questions such as:

- What was known before scheduler handoff?
- When did scheduler acceptance become known?
- When did provider acceptance become known?
- Was external completion ever actually confirmed?
- What did the system believe at each recovery point?

## Truth boundary

A projection is a record of known evidence, not a claim that missing stages occurred.

The store does not infer:

`accepted → executing`

or:

`provider_accepted → externally_confirmed`

Those boundaries require their own evidence.

## Storage

SQLite is used for local durable persistence. Projection payloads contain lifecycle metadata only; prompts, credentials, provider secrets, and sensitive payloads do not belong in this store.

## Next step

PI-080 should add comparison between projection versions so the system can explicitly describe what changed between recovery observations without silently treating every change as an error.
