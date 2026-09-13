"""PI-049 bridge between execution intents and idempotency receipts."""

from dataclasses import dataclass
from typing import Optional

from .execution_intent import ExecutionIntent
from .idempotency import ExecutionReceipt, IdempotencyRegistry


@dataclass(frozen=True)
class IntentExecutionCheck:
    executable: bool
    execution_key: str
    reason: str
    receipt: Optional[ExecutionReceipt] = None


class IntentIdempotencyBridge:
    """Use one execution intent as the stable identity for one logical action."""

    def __init__(self, registry: IdempotencyRegistry) -> None:
        self.registry = registry

    def check(self, intent: ExecutionIntent) -> IntentExecutionCheck:
        if not intent.intent_id:
            raise ValueError("intent_id is required")
        if not intent.task_id:
            raise ValueError("task_id is required")

        receipt = self.registry.get(intent.intent_id)
        if receipt is not None:
            if receipt.task_id != intent.task_id:
                raise ValueError("execution intent task does not match receipt task")
            if receipt.success:
                return IntentExecutionCheck(
                    executable=False,
                    execution_key=intent.intent_id,
                    reason="logical action already completed",
                    receipt=receipt,
                )
            return IntentExecutionCheck(
                executable=True,
                execution_key=intent.intent_id,
                reason="prior attempt was not successful; retry may use the same execution identity",
                receipt=receipt,
            )

        return IntentExecutionCheck(
            executable=True,
            execution_key=intent.intent_id,
            reason="no prior execution receipt exists",
        )

    def record(
        self,
        intent: ExecutionIntent,
        *,
        success: bool,
        response: Optional[str] = None,
    ) -> ExecutionReceipt:
        check = self.check(intent)
        if check.receipt is not None and check.receipt.success:
            return check.receipt

        return self.registry.record(
            ExecutionReceipt(
                execution_key=intent.intent_id,
                task_id=intent.task_id,
                success=success,
                response=response,
            )
        )
