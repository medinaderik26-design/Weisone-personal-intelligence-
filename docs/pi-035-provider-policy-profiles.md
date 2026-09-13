# PI-035 — Provider-Specific Policy Profiles

## Purpose

Give Personal Intelligence an explicit policy contract for every provider it may use.

## Provider policy answers

- What sensitivity classes may this provider receive?
- What task types may it process?
- May it receive high-privacy work?
- May it perform external side effects?
- What additional provider-specific metadata or restrictions apply?

## Architecture

`Task → Provider Candidate → Provider Policy → Data Boundary → Resource/Quota Checks → Execution`

Provider policy is a separate authorization layer from routing. A provider being available or inexpensive does not make it authorized.

## Default-deny behavior

An unregistered provider has no policy and therefore cannot be treated as authorized by the registry.

External side effects are denied by default. A future provider may explicitly receive permission, but that permission must remain separate from ordinary inference access.

## Example policy model

```text
Cloud Provider
  normal data       ✓
  sensitive data    ✗
  high privacy     ✗
  external actions ✗

Local Provider
  normal data       ✓
  sensitive data    ✓
  high privacy     ✓
  external actions conditional
```

These are architectural examples, not default claims about any real provider.

## Security principle

**Capability is not authorization.**

The fact that a model can technically process information does not mean Personal Intelligence should allow it to receive that information.

## Next step

PI-036 should combine provider policy, data-boundary filtering, quota/resource eligibility, and failover into one **pre-execution authorization gate**.
