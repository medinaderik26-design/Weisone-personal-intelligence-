# PI-060 — Recovery Reconciliation Records

## Purpose

PI-060 records the reasoning behind recovery decisions after interrupted work.

A recovery decision is not enough by itself. Personal Intelligence should preserve the evidence context that produced it.

## Record fields

Each reconciliation record captures:
- task ID
- execution intent ID when known
- prior durable work status
- latest action-ledger stage when known
- recovery action
- reason
- timestamp

## Example

```text
work status: running
ledger stage: provider_accepted
intent: intent-1
recovery: verify_external_effect
reason: external outcome is unknown
```

This makes the decision inspectable without storing the underlying user payload.

## Architecture

`Durable Work State + Action Ledger → Recovery Decision → Reconciliation Record → Scheduler / Human Review`

## Safety

The record does not claim that a recovery action succeeded. It records the decision that was made and why.

This distinction matters because:

- deciding to retry is not proof that the retry succeeded
- deciding to verify is not proof that verification succeeded
- deciding to complete is only justified when the underlying evidence supports completion

## Next step

PI-061 should make reconciliation records **durable and linked to the Action Ledger**, allowing the entire recovery chain to survive restarts and remain auditable.
