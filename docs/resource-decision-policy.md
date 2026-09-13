# PI-015 — Resource-Aware Decision Policy

PI-015 introduces the first decision layer above the resource ledger.

## Decision order

The policy separates **hard constraints** from **optimization preferences**.

### Hard constraints

A provider is excluded when:

- it is unavailable
- its resource manager says it cannot accept another request
- the task requires high privacy and the provider is not local

These constraints cannot be overridden by a better score.

### Optimization signals

Among eligible providers, the policy can use measured information such as:

- remaining request capacity
- measured latency when the task requests low latency

Unknown measurements contribute no fabricated advantage or penalty.

## Architecture

**Task → Eligibility Gate → Resource-Aware Ranking → Provider → Execution → Evidence → Feedback → Future Ranking**

This is intentionally conservative. The policy does not yet claim that one provider is intrinsically smarter, cheaper, or more efficient.

## Why this matters

The practical problem is not simply access to more AI. It is coordinating many available intelligence resources while the user encounters limits across systems.

PI-015 gives the Personal Intelligence layer a place to make those decisions without hard-coding a single provider.

## Not yet solved

The policy still needs verified measurements for:

- actual tokenizer-based token usage
- provider-specific cost
- compute/resource consumption
- quality by task type
- reliability over meaningful sample sizes
- quota reset timing
- provider failure behavior
- long-running task allocation

Those measurements must enter through the evidence/telemetry system rather than being inferred from text length or assumptions.

## Next step

PI-016 should combine resource-aware ranking with the existing performance-confidence signals, preserving hard constraints while allowing measured task quality to influence provider choice.
