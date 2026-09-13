# PI-032 — Quota-Aware Scheduling

## Purpose

Turn explicit provider quota facts into safe scheduling decisions instead of repeatedly attempting work against exhausted capacity.

## Decisions

| State | Decision |
|---|---|
| Quota unknown | Eligible; exhaustion is not assumed |
| Quota available | Eligible |
| Exhausted + future reset known | Defer until reset |
| Exhausted + reset passed | Refresh quota |
| Exhausted + reset unknown | Reroute |

## Architecture

`QuotaSource → QuotaAdapter → QuotaRegistry → QuotaAwareScheduler → Queue/Routing`

## Safety

The scheduler does not infer reset times. A timestamp must come from an explicit quota report. Unknown capacity is not treated as zero.

This prevents a common failure mode in multi-provider AI systems: burning retries against a provider that is already known to be exhausted.

## Relationship to PI-030

PI-030 answers **where a task may run** using eligibility, quota, budgets, and measured performance.

PI-032 answers **when a provider should be retried, deferred, refreshed, or abandoned for this execution window**.

Together:

`Task → Eligibility/Budget Routing → Quota Schedule Decision → Provider → Execution`

## Next step

PI-033 should add **local-first fallback and provider failover**, so deferred/exhausted cloud work can continue safely on an authorized local provider when the task permits it.
