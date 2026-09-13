# PI-051 — External Effect Receipts

## Purpose

Separate an internal execution result from evidence that an external system actually accepted or confirmed the intended effect.

## Status model

- `attempted` — PI initiated the operation.
- `accepted` — the provider reported accepting the request.
- `confirmed` — the external effect was independently confirmed.
- `failed` — the operation was explicitly reported as failed.
- `unknown` — completion cannot currently be established.

These states are intentionally not collapsed into a single boolean success flag.

## Evidence provenance

`provider_reported` means the provider reported the event.

`external_confirmed` means the external system or an independent observation confirmed the effect.

`unknown` means the evidence is insufficient.

The system must not upgrade `accepted` to `confirmed` without explicit evidence.

## Architecture

`Human Confirmation → Execution Intent → Idempotency → Provider Execution → External Effect Receipt → Execution Evidence`

## Safety rule

An internal provider success receipt is not automatically proof that an external side effect occurred.

For consequential actions, Personal Intelligence should remain capable of saying:

> Attempted, but external completion is not confirmed.

That prevents the system from falsely telling the person that an email was delivered, a transaction completed, a file was changed, or another external action occurred when the evidence only proves an attempt or provider acceptance.

## Public-repository boundary

This module contains only generic contracts. Real provider credentials, personal data, private targets, and provider-specific secrets must remain outside this public repository.

## Next step

PI-052 should define **effect verification policies**: how different operation classes obtain trustworthy confirmation without assuming every provider has the same evidence model.
