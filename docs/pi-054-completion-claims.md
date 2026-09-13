# PI-054 — Truthful Completion Claims

## Purpose

Turn evidence confidence into bounded user-facing language. Personal Intelligence should never report stronger completion than its evidence supports.

## Claim levels

- **Not completed / unknown:** evidence is insufficient to confirm external completion.
- **Provider accepted:** the provider accepted the request, but external completion remains unconfirmed.
- **Externally confirmed:** the available evidence confirms the external effect.

## Core rule

**The claim must never be stronger than the evidence.**

A successful API call is not automatically a completed external action.

## Architecture

`Execution → External Effect Receipt → Verification → Evidence Confidence → Completion Claim → User`

This is the user-facing truth boundary.

## Safety

The claim layer does not grant permission, retry work, or alter evidence. It only translates existing evidence into a bounded statement.

The user should be able to distinguish:
- what PI attempted
- what a provider accepted
- what was externally confirmed
- what remains unknown

## Next step

PI-055 should build a **user-facing action ledger** so every consequential action has a durable, inspectable history from intent through evidence and final claim.
