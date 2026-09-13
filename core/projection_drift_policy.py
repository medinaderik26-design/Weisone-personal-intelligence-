"""PI-081 explicit policy classification for lifecycle projection drift."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ProjectionDriftPolicyDecision:
    classification: str
    action: str
    reason: str


class ProjectionDriftPolicy:
    """Classify projection drift without treating every change as failure."""

    def classify(self, drift):
        if not drift.changed:
            return ProjectionDriftPolicyDecision(
                "no_drift", "continue", "projection is unchanged"
            )

        changes = set(drift.changes)

        # Normal forward progress in the lifecycle is not an error.
        if changes.issubset({"stages", "current_stage"}):
            return ProjectionDriftPolicyDecision(
                "expected_progression",
                "continue",
                "only lifecycle stage information changed",
            )

        # Completion evidence changing from false to true is expected when
        # the lifecycle reaches externally_confirmed.
        if changes.issubset({"stages", "current_stage", "evidence_complete"}):
            return ProjectionDriftPolicyDecision(
                "expected_progression",
                "continue",
                "lifecycle progression includes a completion-evidence update",
            )

        # A changing execution intent is identity-sensitive and must be
        # inspected rather than silently accepted.
        if "intent_id" in changes:
            return ProjectionDriftPolicyDecision(
                "identity_divergence",
                "human_review",
                "execution intent changed between projections",
            )

        return ProjectionDriftPolicyDecision(
            "unexpected_divergence",
            "reinspect",
            "projection changed in a way not classified as normal lifecycle progression",
        )
