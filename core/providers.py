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
    """Deterministic local provider used for PI-001 tests."""

    name = "local"
    model = "echo-v0.1"

    def resource_snapshot(self) -> ResourceSnapshot:
        return ResourceSnapshot(provider=self.name, model=self.model, available=True)

    def generate(self, task: Task) -> Result:
        return Result(
            task_id=task.task_id,
            provider=self.name,
            model=self.model,
            text=f"Echo: {task.prompt}",
            success=True,
        )


class SimulatedCloudProvider(IntelligenceProvider):
    """Deterministic cloud stand-in for routing and quota tests.

    It never contacts a network service and carries no credentials.
    """

    name = "cloud-sim"
    model = "cloud-sim-v0.1"

    def __init__(self, *, available: bool = True, requests_limit=None):
        self._available = available
        self.requests_limit = requests_limit

    def resource_snapshot(self) -> ResourceSnapshot:
        return ResourceSnapshot(
            provider=self.name,
            model=self.model,
            available=self._available,
            requests_limit=self.requests_limit,
        )

    def generate(self, task: Task) -> Result:
        return Result(
            task_id=task.task_id,
            provider=self.name,
            model=self.model,
            text=f"Cloud simulation: {task.prompt}",
            success=True,
        )
