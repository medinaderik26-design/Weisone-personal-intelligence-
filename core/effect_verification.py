"""PI-052 verification policies for external effects."""

from dataclasses import dataclass
from typing import Optional, Protocol

from .external_effect import ExternalEffectReceipt


@dataclass(frozen=True)
class VerificationResult:
    verified: bool
    reason: str


class EffectVerifier(Protocol):
    def verify(self, receipt: ExternalEffectReceipt) -> VerificationResult:
        ...


class ExplicitConfirmationVerifier:
    """Verifier for integrations that can explicitly confirm an external effect."""

    def __init__(self, confirmed_effects: Optional[set[str]] = None) -> None:
        self.confirmed_effects = confirmed_effects or set()

    def verify(self, receipt: ExternalEffectReceipt) -> VerificationResult:
        if receipt.effect_id in self.confirmed_effects:
            return VerificationResult(True, "external effect was explicitly confirmed")
        return VerificationResult(False, "external effect has not been explicitly confirmed")


class EffectVerificationRegistry:
    """Map operation types to explicit verification strategies."""

    def __init__(self) -> None:
        self._verifiers: dict[str, EffectVerifier] = {}

    def register(self, operation: str, verifier: EffectVerifier) -> None:
        if not operation:
            raise ValueError("operation is required")
        self._verifiers[operation] = verifier

    def verify(self, operation: str, receipt: ExternalEffectReceipt) -> VerificationResult:
        verifier = self._verifiers.get(operation)
        if verifier is None:
            return VerificationResult(False, "no verification policy exists for this operation")
        return verifier.verify(receipt)
