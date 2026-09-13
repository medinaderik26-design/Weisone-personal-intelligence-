"""PI-076 lifecycle validation for scheduler-derived ledger stages."""

from dataclasses import dataclass


@dataclass(frozen=True)
class SchedulerLedgerValidation:
    allowed: bool
    reason: str


class SchedulerLedgerValidator:
    """Ensure scheduler evidence cannot bypass authorization or confirmation."""

    REQUIRED_PREDECESSORS = {
        "handed_off": {"authorized"},
        "accepted": {"handed_off"},
    }

    def validate(self, prior_stages: tuple[str, ...], next_stage: str) -> SchedulerLedgerValidation:
        if next_stage not in self.REQUIRED_PREDECESSORS:
            return SchedulerLedgerValidation(False, "stage is not scheduler-derived")
        required = self.REQUIRED_PREDECESSORS[next_stage]
        if not any(stage in required for stage in prior_stages):
            return SchedulerLedgerValidation(
                False,
                f"scheduler stage '{next_stage}' is missing required predecessor evidence",
            )
        return SchedulerLedgerValidation(True, "required scheduler predecessor evidence exists")

    def require(self, prior_stages: tuple[str, ...], next_stage: str) -> None:
        result = self.validate(prior_stages, next_stage)
        if not result.allowed:
            raise ValueError(result.reason)
