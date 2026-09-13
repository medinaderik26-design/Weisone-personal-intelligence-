"""PI-083 boundary between durable policy decisions and execution."""

from dataclasses import dataclass


@dataclass(frozen=True)
class PolicyBoundaryDecision:
    task_id: str
    action: str
    handoff_allowed: bool
    reason: str


class PolicyExecutionBoundary:
    """Translate policy outcomes into boundary decisions, never authorization."""

    def evaluate(self, policy_decision) -> PolicyBoundaryDecision:
        if not policy_decision.task_id:
            raise ValueError("task_id is required")
        if not policy_decision.action:
            raise ValueError("action is required")

        if policy_decision.action == "continue":
            return PolicyBoundaryDecision(
                policy_decision.task_id,
                policy_decision.action,
                True,
                "policy permits continuation to the next execution boundary",
            )

        if policy_decision.action == "reinspect":
            return PolicyBoundaryDecision(
                policy_decision.task_id,
                policy_decision.action,
                False,
                "policy requires fresh inspection before execution",
            )

        if policy_decision.action == "human_review":
            return PolicyBoundaryDecision(
                policy_decision.task_id,
                policy_decision.action,
                False,
                "policy requires human review before execution",
            )

        return PolicyBoundaryDecision(
            policy_decision.task_id,
            policy_decision.action,
            False,
            "unknown policy action cannot cross the execution boundary",
        )
