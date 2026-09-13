# PI-008 — Task-Specific Performance Routing

PI-008 changes the routing question from:

> Which provider is best?

to:

> Which available provider has the best measured history for this task type?

The performance registry keys observations by `(provider, task_type)`.

Tracked evidence:

- success/failure count
- success rate
- optional measured quality
- optional measured latency

The performance-aware router preserves hard constraints first:

1. provider availability
2. resource capacity
3. privacy requirements
4. measured task-specific performance
5. latency preference when explicitly requested

An unknown provider/task pair receives no performance bonus. It is not automatically considered bad.

Quality must come from an explicit evaluator or measured outcome. The router does not manufacture a quality score from token counts, character counts, model names, or other proxies.

## Example

A coding task can learn that Provider A has historically produced higher-quality results than Provider B for coding, while a research task can learn a different preference. The same provider may therefore be selected for one task class and not another.

## Current boundary

This is routing infrastructure, not autonomous learning. The system records observations and uses supplied measurements. Future work can add evaluators, confidence thresholds, rolling windows, and cost/quality tradeoffs.
