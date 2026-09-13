"""PI-071 explicit recovery dispatch acknowledgement states."""

from dataclasses import dataclass
from typing import Literal


AckState = Literal["claimed", "handed_off", "accepted"]


@dataclass(frozen=True)
class DispatchAcknowledgement:
    task_id: str
    dispatch_key: str
    state: AckState
    reason: str

    def validate(self) -> None:
        if not self.task_id:
            raise ValueError("task_id is required")
        if not self.dispatch_key:
            raise ValueError("dispatch_key is required")
        if self.state not in {"claimed", "handed_off", "accepted"}:
            raise ValueError("invalid acknowledgement state")
        if not self.reason:
            raise ValueError("reason is required")


class DispatchAcknowledgementPolicy:
    """Keep dispatch claim, handoff, and scheduler acceptance distinct."""

    _transitions = {
        "claimed": {"handed_off"},
        "handed_off": {"accepted"},
        "accepted": set(),
    }

    def can_transition(self, current: AckState, next_state: AckState) -> bool:
        return next_state in self._transitions.get(current, set())

    def require_transition(self, current: AckState, next_state: AckState) -> None:
        if not self.can_transition(current, next_state):
            raise ValueError(f"invalid dispatch acknowledgement transition: {current} -> {next_state}")
