"""Provider boundary for cloud and local intelligence backends."""

from abc import ABC, abstractmethod
from .models import ResourceSnapshot, Result, Task


class IntelligenceProvider(ABC):
    name: str
    model: str

    @abstractmethod
    def resource_snapshot(self) -> ResourceSnapshot:
        raise NotImplementedError

    @abstractmethod
    def generate(self, task: Task) -> Result:
        raise NotImplementedError


class EchoProvider(IntelligenceProvider):
    """Deterministic local provider used for PI-001 tests.

    It does not contact a network service and makes no claim to be an LLM.
    """

    name = "local"
    model = "echo-v0.1"

    def resource_snapshot(self) -> ResourceSnapshot:
        return ResourceSnapshot(
            provider=self.name,
            model=self.model,
            available=True,
        )

    def generate(self, task: Task) -> Result:
        return Result(
            task_id=task.task_id,
            provider=self.name,
            model=self.model,
            text=f"Echo: {task.prompt}",
            success=True,
        )
