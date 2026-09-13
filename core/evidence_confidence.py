"""PI-053 confidence scoring for external-effect evidence."""

from dataclasses import dataclass
from typing import Optional

from .effect_verification import VerificationResult
from .external_effect import ExternalEffectReceipt


@dataclass(frozen=True)
class EvidenceConfidence:
    score: float
    level: str
    reason: str

    def validate(self) -> None:
        if not 0.0 <= self.score <= 1.0:
            raise ValueError("confidence score must be between 0 and 1")
        if self.level not in {"none", "weak", "moderate", "strong"}:
            raise ValueError("invalid confidence level")


class EvidenceConfidenceModel:
    """Classify evidence strength without turning weak evidence into certainty."""

    def evaluate(
        self,
        receipt: ExternalEffectReceipt,
        verification: VerificationResult,
        *,
        independent_confirmation: bool = False,
    ) -> EvidenceConfidence:
        receipt.validate()

        if not verification.verified:
            result = EvidenceConfidence(0.0, "none", verification.reason)
            result.validate()
            return result

        if receipt.evidence_source == "external_confirmed" and independent_confirmation:
            result = EvidenceConfidence(1.0, "strong", "external effect has independent confirmation")
        elif receipt.evidence_source == "external_confirmed":
            result = EvidenceConfidence(0.9, "strong", "external system confirmed the effect")
        elif receipt.evidence_source == "provider_reported":
            result = EvidenceConfidence(0.5, "moderate", "provider reported acceptance but external completion is not independently confirmed")
        else:
            result = EvidenceConfidence(0.0, "none", "evidence source is unknown")

        result.validate()
        return result
