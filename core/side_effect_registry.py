"""PI-044 registry for external side-effect safety semantics."""

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class SideEffectProfile:
    operation: str
    cancelable: bool
    reversible: bool
    compensatable: bool
    requires_confirmation: bool = False
    description: str = ""

    def validate(self) -> None:
        if not self.operation:
            raise ValueError("operation is required")
        if not (self.cancelable or self.reversible or self.compensatable) and not self.requires_confirmation:
            raise ValueError("irreversible operations must require confirmation")


class SideEffectRegistry:
    """Explicit registry; unknown operations are not treated as safe."""

    def __init__(self) -> None:
        self._profiles: Dict[str, SideEffectProfile] = {}

    def register(self, profile: SideEffectProfile) -> None:
        profile.validate()
        self._profiles[profile.operation] = profile

    def get(self, operation: str) -> SideEffectProfile:
        profile = self._profiles.get(operation)
        if profile is None:
            raise KeyError(f"unknown side-effect operation: {operation}")
        return profile

    def contains(self, operation: str) -> bool:
        return operation in self._profiles
