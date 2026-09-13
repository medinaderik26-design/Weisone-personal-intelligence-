"""PI-025 recovery engine tying durable state to execution leases.

This layer inspects state and liveness. It does not execute recovered work.
"""

from dataclasses import dataclass
from typing import Optional

from .execution_lease import LeaseRegistry
from .persistent_work_state import WorkState
from .recovery_coordinator import RecoveryAction, RecoveryCoordinator, RecoveryDecision


@dataclass(frozen=True)
class RecoveryInspection:
    task_id: str
    state: WorkState
    lease_active: Optional[bool]
    decision: RecoveryDecision


class RecoveryEngine:
    def __init__(self, coordinator: RecoveryCoordinator, leases: LeaseRegistry) -> None:
        self.coordinator = coordinator
        self.leases = leases

    def inspect(self, state: WorkState, *, now=None, reroute_available: bool = False) -> RecoveryInspection:
        state.validate()
        lease = self.leases.get(state.task_id)
        lease_active = None if lease is None else lease.active(now)

        if state.status == "running" and lease_active is True:
            decision = RecoveryDecision(
                state.task_id,
                RecoveryAction.DEFER,
                "execution lease is still active; another worker owns live execution",
                state.provider,
            )
        elif state.status == "running" and lease_active is False:
            decision = self.coordinator.decide(
                state,
                provider_available=True,
                reroute_available=reroute_available,
                external_completion_unknown=True,
            )
        else:
            decision = self.coordinator.decide(
                state,
                provider_available=True,
                reroute_available=reroute_available,
                external_completion_unknown=False,
            )

        return RecoveryInspection(state.task_id, state, lease_active, decision)
