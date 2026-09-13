"""PI-065 policy for classifying recovery snapshot drift."""

from dataclasses import dataclass

from .recovery_drift import RecoveryDrift


@dataclass(frozen=True)
class RecoveryPolicyDecision:
    classification: str
    action: str
    reason: str


class RecoveryReconciliationPolicy:
    """Classify drift without silently resolving ambiguous recovery state."""

    def classify(self, drift: RecoveryDrift) -> RecoveryPolicyDecision:
        if not drift.changed:
            return RecoveryPolicyDecision(
                "no_drift", "continue", "recovery snapshots are equivalent"
            )

        changes = set(drift.changes)

        expected = {"ledger_stage", "recovery_action", "recovery_reason"}
        if changes.issubset(expected):
            return RecoveryPolicyDecision(
                "expected_progression",
                "continue",
                "only recovery narrative fields changed",
            )

        recoverable = {"work_status", "attempt_count", "provider"}
        if changes.issubset(recoverable):
            return RecoveryPolicyDecision(
                "recoverable_divergence",
                "reinspect",
                "durable work state changed and requires a fresh recovery inspection",
            )

        return RecoveryPolicyDecision(
            "human_review_required",
            "human_review",
            "recovery snapshots contain mixed or identity-sensitive divergence",
        )
