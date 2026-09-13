# PI-009 — Performance Confidence

PI-009 adds an evidence gate between measurement and routing decisions.

The system should not change provider preference because of one unusually good or bad result. Task-specific performance becomes a routing signal only after it crosses a configurable evidence threshold.

Default policy:

- minimum total samples: 3
- minimum quality samples: 3
- minimum success rate: 0.0

Quality is required before a quality-based preference is considered reliable.

## Principle

**Sparse evidence informs observation; sufficient evidence informs routing.**

Unknown evidence is neutral. It is not treated as failure.

## Routing hierarchy

1. Availability
2. Resource capacity
3. Privacy constraints
4. Confidence gate
5. Measured task-specific quality
6. Explicit latency preference

This prevents the personal intelligence from overfitting to isolated outcomes while still allowing it to adapt as real evidence accumulates.

## Future work

- confidence intervals
- rolling windows
- recency weighting
- task-family inheritance
- evaluator agreement
- cost/quality tradeoff confidence
- automatic exploration of under-tested providers
