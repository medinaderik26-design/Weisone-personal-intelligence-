"""PI-019 idempotency primitives for safe execution and retries."""

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass(frozen=True)
class ExecutionReceipt:
    """Stable record proving whether an execution key has completed."""

    execution_key: str
    task_id: str
    success: bool
    response: Optional[str] = None


class IdempotencyRegistry:
    """Prevent accidental duplicate execution for the same logical operation."""

    def __init__(self) -> None:
        self._receipts: Dict[str, ExecutionReceipt] = {}

    def get(self, execution_key: str) -> Optional[ExecutionReceipt]:
        return self._receipts.get(execution_key)

    def record(self, receipt: ExecutionReceipt) -> ExecutionReceipt:
        if not receipt.execution_key:
            raise ValueError("execution_key is required")
        if not receipt.task_id:
            raise ValueError("task_id is required")

        existing = self._receipts.get(receipt.execution_key)
        if existing is not None:
            if existing.task_id != receipt.task_id:
                raise ValueError("execution_key already belongs to another task")
            return existing

        self._receipts[receipt.execution_key] = receipt
        return receipt

    def completed(self, execution_key: str) -> bool:
        receipt = self.get(execution_key)
        return receipt is not None and receipt.success
