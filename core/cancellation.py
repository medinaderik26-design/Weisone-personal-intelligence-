"""PI-043 cancellation and compensation contracts for started work."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CancellationDecision:
    task_id: str
    action: str
    reason: str
    compensation: Optional[str] = None


class CancellationPolicy:
    """Decide whether started work may stop safely.

    This layer never performs the cancellation or compensation itself.
    """

    def decide(
        self,
        task_id: str,
        *,
        started: bool,
        cancelable: bool,
        external_side_effect: bool,
        compensation_available: bool = False,
        user_revoked: bool = False,
    ) -> CancellationDecision:
        if not task_id:
            raise ValueError("task_id is required")

        if not started:
            return CancellationDecision(task_id, "cancel_before_start", "work has not started")

        if not user_revoked:
            return CancellationDecision(task_id, "continue", "no cancellation condition is active")

        if cancelable:
            return CancellationDecision(task_id, "cancel", "user authorization was revoked before completion")

        if external_side_effect and compensation_available:
            return CancellationDecision(
                task_id,
                "compensate",
                "work is already committed but a compensation action is available",
                compensation="apply_registered_compensation",
            )

        return CancellationDecision(
            task_id,
            "human_review",
            "work cannot be safely cancelled or automatically compensated",
        )
