# PI-003 — Resource-Aware Routing

PI-003 connects the Intelligence Router to the Resource Manager.

## Behavior

The router now considers two gates before selecting a provider:

1. Provider reports that it is available.
2. Resource Manager reports that the provider still has request capacity.

Unknown providers remain unavailable by default.

High-privacy tasks continue to prefer a local provider when one is available.

## Current Limitation

Provider ranking is still deterministic. PI-003 does not yet score:

- quality
- latency
- actual cost
- context utilization
- task capability
- measured provider reliability

Those become inputs to a later routing policy.

## Why This Matters

This creates the first separation between intelligence capability and provider availability. A model may be technically capable of answering a task while the Personal Intelligence layer decides that another provider should handle it because the first provider is unavailable or exhausted.

The Resource Manager remains the source of resource accounting; the Router remains responsible for selection.
