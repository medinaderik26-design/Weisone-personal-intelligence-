"""PI-090 first integrated execution spine.

This is a deliberately small orchestration boundary. It coordinates existing
PI layers without collapsing their evidence semantics.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Optional

from .execution_start import ExecutionStartBoundary, ExecutionStartRecord
from .models import Task
from .policy_dispatch_bridge import PolicyDispatchBridge, PolicyDispatchRequest
from .policy_dispatch_claim import PolicyDispatchClaimAdapter, PolicyDispatchClaimResult
from .provider_acceptance import ProviderAcceptanceBoundary, ProviderAcceptanceResult


@dataclass(frozen=True)
class SpineResult:
    task_id: str
    dispatch: PolicyDispatchRequest
    claim: PolicyDispatchClaimResult
    execution_start: Optional[ExecutionStartRecord]
    provider_acceptance: Optional[ProviderAcceptanceResult]


class ExecutionSpine:
    """Coordinate the pre-provider execution path without hiding evidence gaps."""

    def __init__(
        self,
        claim_adapter: PolicyDispatchClaimAdapter,
        *,
        dispatch_bridge: Optional[PolicyDispatchBridge] = None,
        execution_start: Optional[ExecutionStartBoundary] = None,
        provider_acceptance: Optional[ProviderAcceptanceBoundary] = None,
    ) -> None:
        self.claim_adapter = claim_adapter
        self.dispatch_bridge = dispatch_bridge or PolicyDispatchBridge()
        self.execution_start_boundary = execution_start or ExecutionStartBoundary()
        self.provider_acceptance_boundary = provider_acceptance or ProviderAcceptanceBoundary()

    def prepare(self, task: Task, boundary_decision: Any, classification: str) -> SpineResult:
        if not task.task_id:
            raise ValueError("task_id is required")
        if boundary_decision.task_id != task.task_id:
            raise ValueError("task and boundary decision task IDs do not match")

        dispatch = self.dispatch_bridge.build(boundary_decision, classification)
        claim = self.claim_adapter.claim(dispatch)

        return SpineResult(
            task_id=task.task_id,
            dispatch=dispatch,
            claim=claim,
            execution_start=None,
            provider_acceptance=None,
        )

    def start_execution(self, result: SpineResult, now=None) -> SpineResult:
        if not result.claim.claimed or result.claim.claim is None:
            raise RuntimeError("execution cannot start without a durable dispatch claim")

        accepted = type("Acceptance", (), {
            "task_id": result.task_id,
            "dispatch_key": result.claim.dispatch_key,
            "intent_id": result.claim.claim.task_id,
            "accepted": True,
        })()
        started = self.execution_start_boundary.start(accepted, now=now)
        return SpineResult(
            task_id=result.task_id,
            dispatch=result.dispatch,
            claim=result.claim,
            execution_start=started,
            provider_acceptance=None,
        )

    def record_provider_acceptance(
        self,
        result: SpineResult,
        *,
        provider: str,
        accepted: bool,
        now=None,
    ) -> SpineResult:
        if result.execution_start is None:
            raise RuntimeError("execution must start before provider acceptance")
        provider_result = self.provider_acceptance_boundary.accept(
            result.execution_start,
            provider=provider,
            accepted=accepted,
            now=now,
        )
        return SpineResult(
            task_id=result.task_id,
            dispatch=result.dispatch,
            claim=result.claim,
            execution_start=result.execution_start,
            provider_acceptance=provider_result,
        )
