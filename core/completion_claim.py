"""PI-054 truthful completion-claim policy."""

from dataclasses import dataclass
from typing import Literal

from .evidence_confidence import EvidenceConfidence

ClaimLevel = Literal["not_completed", "provider_accepted", "externally_confirmed"]


@dataclass(frozen=True)
class CompletionClaim:
    level: ClaimLevel
    statement: str
    confidence: float


class CompletionClaimPolicy:
    """Convert measured evidence into a bounded user-facing completion claim."""

    def claim(self, confidence: EvidenceConfidence) -> CompletionClaim:
        confidence.validate()

        if confidence.level == "none":
            return CompletionClaim(
                "not_completed",
                "The system cannot confirm that the external action completed.",
                confidence.score,
            )

        if confidence.level == "moderate":
            return CompletionClaim(
                "provider_accepted",
                "The provider accepted the action, but external completion is not independently confirmed.",
                confidence.score,
            )

        return CompletionClaim(
            "externally_confirmed",
            "The external action is confirmed by the available evidence.",
            confidence.score,
        )
