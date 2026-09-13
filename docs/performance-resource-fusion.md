# PI-016 — Performance + Resource Fusion

PI-016 combines two kinds of measured evidence:

1. **Task performance** — quality and success history for a provider on a task type.
2. **Resource state** — availability and remaining request capacity, plus measured latency when requested.

## Decision hierarchy

Hard constraints come first:

- unavailable providers are excluded
- exhausted providers are excluded
- high-privacy tasks require a local provider when one is available

Only eligible providers are scored.

## Fusion

For sufficiently trusted task-specific evidence, the router can use:

- measured quality
- measured success rate
- measured latency for low-latency tasks
- remaining request capacity

Sparse or unknown quality does not receive a fabricated quality score. Resource values are used only when the provider actually reports them.

## Important boundary

PI-016 is a routing policy, not proof of efficiency.

It does not claim:

- token savings
- lower compute consumption
- lower monetary cost
- superior intelligence
- universal provider rankings

Those claims require controlled measurements.

## Architecture

**Task → Hard Constraints → Performance Confidence + Resource State → Fusion Score → Provider → Execution Evidence → Feedback → Updated History**

The result is an adaptive routing loop that can learn which resource is appropriate for which kind of work while preserving privacy and resource limits as non-negotiable constraints.

## Next step

PI-017 should introduce explicit task requirements and resource budgets so the Personal Intelligence layer can reject, defer, split, or reroute work before consuming scarce AI capacity.
