# PI-080 — Lifecycle Projection Drift

PI-080 compares two lifecycle projections and reports exactly what changed.

## Drift dimensions

The detector checks:

- execution intent identity
- ordered lifecycle stages
- current known stage
- external-evidence completion state

## Important boundary

Drift detection is descriptive, not judgmental.

A change from `authorized` to `handed_off` is expected progression. A change in execution intent is an identity-sensitive change. The detector reports the difference but does not automatically label it as safe or unsafe.

## Safety principle

The system should separate three questions:

1. **What changed?** — projection drift.
2. **Is the change expected?** — policy layer.
3. **What should happen next?** — recovery/execution boundary.

PI-080 only answers the first question.

## Next step

PI-081 should classify projection drift using explicit policy, distinguishing expected progression from unexpected or identity-sensitive divergence.
