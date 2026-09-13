# PI-053 — Evidence Confidence Model

## Purpose

PI-053 prevents Personal Intelligence from treating every positive signal as equally trustworthy.

## Confidence levels

- **None — 0.0:** no trustworthy confirmation exists.
- **Weak:** indirect evidence may exist, but is not sufficient for a completion claim.
- **Moderate — 0.5:** a provider reports acceptance, but the external outcome is not independently confirmed.
- **Strong — 0.9:** the external system confirms the effect.
- **Strongest — 1.0:** external confirmation is independently corroborated.

The model intentionally keeps evidence strength separate from authorization. A highly confident observation does not grant permission to act.

## Architecture

`External Effect Receipt → Verification Policy → Evidence Confidence → Completion Claim`

This creates a clean distinction between:

`I was allowed to do it`  vs.  `I have evidence that it happened`.

## Safety rule

The system must never upgrade weak evidence into certainty merely because an operation normally succeeds.

Unknown remains unknown until a defined evidence source changes the state.

## Next step

PI-054 should create **completion-claim policy** so the system can decide what it is actually allowed to tell the user based on evidence confidence.
