# Resource Model

## Purpose

The Resource Manager gives Personal Intelligence a measurable view of the resources available to each intelligence provider.

v0.1 does not attempt to reverse-engineer provider quotas or billing systems. It records facts supplied by the provider adapter or local runtime.

## Tracked Signals

- request count
- request limit, when known
- input tokens, when known
- output tokens, when known
- estimated cost, when known
- failures

## Decision Rule

A provider that is unknown to the Resource Manager is unavailable by default.

A provider with a known request limit cannot be selected after its recorded budget is exhausted.

## Future Signals

- context-window utilization
- latency
- rate-limit events
- retry-after information
- local CPU/GPU/RAM usage
- queue depth
- provider health
- task quality
- cost per useful operation
- actual tokenizer measurements

These must be measured rather than inferred from proxy metrics.
