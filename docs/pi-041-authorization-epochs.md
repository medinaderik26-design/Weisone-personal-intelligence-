# PI-041 — Authorization Epochs / Versioning

## Purpose

Prevent workers from executing with an authorization decision that was valid when created but has since become stale.

## Model

Each authorization scope has a monotonic version, or **epoch**:

`(subject, provider, task_type) → epoch`

A decision captures the epoch that existed when it was authorized.

If the registry advances that scope, older decisions are stale.

## Example

```text
Epoch 7 → authorization granted
Worker receives decision: epoch 7

User changes/revokes permission
Epoch advances to 8

Worker checks epoch 7
        ↓
STALE → do not execute
```

## Architecture

`Consent / Policy Change → Advance Epoch → Workers Check Epoch → Execute only if current`

This complements PI-040:
- **Revocation registry** records that permission was revoked.
- **Epochs** let distributed workers detect that an authorization decision itself is outdated.

## Safety

Epochs do not grant permission. They only establish freshness. A current epoch still has to pass the complete authorization boundary.

## Next step

PI-042 should add **authorization decision receipts**, binding an authorization record to its epoch so a worker can verify the complete decision is both valid and current before execution.
