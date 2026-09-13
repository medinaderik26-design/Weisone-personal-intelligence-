"""PI-056 lifecycle validation for the accountable action ledger."""

from dataclasses import dataclass
from typing import Dict


DEFAULT_TRANSITIONS: Dict[str, frozenset[str]] = {
    "planned": frozenset({"confirmed", "cancelled", "deferred"}),
    "confirmed": frozenset({"authorized", "cancelled", "deferred"}),
    "authorized": frozenset({"executing", "cancelled", "deferred"}),
    "executing": frozenset({"provider_accepted", "failed", "cancelled", "human_review"}),
    "provider_accepted": frozenset({"externally_confirmed", "failed", "human_review"}),
    "externally_confirmed": frozenset(),
    "failed": frozenset({"retrying", "rerouted", "human_review"}),
    "retrying": frozenset({"executing", "failed", "human_review"}),
    "rerouted": frozenset({"executing", "failed", "human_review"}),
    "cancelled": frozenset(),
    "deferred": frozenset({"planned", "human_review"}),
    "human_review": frozenset({"planned", "cancelled", "deferred"}),
}


@dataclass(frozen=True)
class LifecycleCheck:
    allowed: bool
    reason: str


class LedgerLifecycleValidator:
    """Reject impossible ledger transitions before they become history."""

    def __init__(self, transitions: Dict[str, frozenset[str]] | None = None) -> None:
        self.transitions = transitions or DEFAULT_TRANSITIONS

    def check(self, current_stage: str, next_stage: str) -> LifecycleCheck:
        if current_stage not in self.transitions:
            return LifecycleCheck(False, "unknown current lifecycle stage")
        if next_stage not in self.transitions:
            return LifecycleCheck(False, "unknown next lifecycle stage")
        if next_stage not in self.transitions[current_stage]:
            return LifecycleCheck(False, f"invalid transition: {current_stage} → {next_stage}")
        return LifecycleCheck(True, "lifecycle transition is valid")

    def require(self, current_stage: str, next_stage: str) -> None:
        result = self.check(current_stage, next_stage)
        if not result.allowed:
            raise ValueError(result.reason)
