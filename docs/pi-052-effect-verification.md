# PI-052 — External Effect Verification Policies

## Purpose

PI-051 established that provider acceptance is not the same as confirmed external completion. PI-052 defines the policy boundary for deciding what evidence is strong enough to mark an external effect as verified.

## Verification levels

1. **Attempted** — execution was initiated.
2. **Accepted** — the provider reported acceptance.
3. **Confirmed** — the external system or a trusted external observation confirmed the effect.
4. **Failed** — the operation is known to have failed.
5. **Unknown** — available evidence is insufficient to determine completion.

## Policy rule

An operation without a registered verification policy is **not considered verified**.

The system must not infer completion from:
- elapsed time
- a successful local function return
- a provider request being constructed
- a character count
- a guessed response
- absence of an error

## Architecture

`External Effect Receipt → Operation Verification Policy → Verification Result`

A verification policy may eventually use:
- provider-confirmed delivery
- external system acknowledgment
- read-after-write confirmation
- signed webhook/event
- independent observation

The strength of each evidence source should remain explicit.

## Safety

Verification proves an observed state; it does not grant permission. Authorization, consent, scope, confirmation, resource policy, and idempotency remain separate controls.

## Next step

PI-053 should create an **evidence confidence model** so Personal Intelligence can distinguish strong confirmation from weak or indirect confirmation instead of treating all evidence as equal.
