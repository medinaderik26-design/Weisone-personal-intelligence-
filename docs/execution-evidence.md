# PI-014 — Unified Execution Evidence

PI-014 establishes one evidence object that binds execution telemetry to resource accounting.

## Why this layer exists

Personal Intelligence needs to make decisions from measured outcomes rather than disconnected signals. A latency measurement in one subsystem and a token count in another are not enough unless they can be proven to belong to the same execution.

`ExecutionEvidence` therefore combines:

- standardized execution telemetry
- resource outcome accounting

The record is accepted only when the task ID and provider agree across both records.

## Architecture

**Task → Router → Provider → Execution → ExecutionTelemetry + ResourceOutcome → ExecutionEvidence → Feedback / Resource History → Future Routing**

This creates a clean evidence boundary between what happened and what the system may later decide.

## Evidence rules

1. Measurements are provider-neutral.
2. Unknown values remain unknown.
3. Actual token counts are preferred; character counts are not substituted.
4. Cost is recorded only when supplied by a defensible source.
5. Quality requires provenance through the telemetry layer.
6. A record from one provider cannot be paired with resource data from another provider.
7. A record from one task cannot be paired with another task's measurements.

## What PI-014 does not do

It does not change the runtime, select providers, infer quality, estimate token usage, or claim cost savings. It creates the evidence object those later decisions can consume.

## Next step

PI-015 should use unified evidence to build a resource-aware decision policy for quotas, latency, cost, privacy, and measured task performance while keeping hard safety and permission constraints ahead of optimization.
