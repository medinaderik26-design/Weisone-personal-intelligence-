# PI-006 Resource-Aware Routing

PI-006 introduces a measured scoring layer without pretending the system already understands model quality.

The router considers only providers that are available and within their recorded resource budget.

Current signals:

- privacy preference
- explicit local preference
- remaining request capacity
- observed latency when low latency is requested

The scoring policy is intentionally small and deterministic.

It does **not** yet score:

- answer quality
- task success rate
- actual compute consumption
- true provider cost unless reported
- tokenizer efficiency
- long-term reliability

Those signals require measurement first.

## Design rule

> Never turn a proxy into a performance claim.

The router should become more intelligent as measured evidence improves, not because more heuristics are added.
