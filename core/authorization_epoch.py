"""PI-041 authorization epochs for stale-decision detection."""

from dataclasses import dataclass
from typing import Dict, Tuple


Scope = Tuple[str, str, str]


@dataclass(frozen=True)
class AuthorizationEpoch:
    subject: str
    provider: str
    task_type: str
    version: int


class AuthorizationEpochRegistry:
    """Monotonic authorization versions shared by decision consumers."""

    def __init__(self) -> None:
        self._versions: Dict[Scope, int] = {}

    def current(self, subject: str, provider: str, task_type: str) -> int:
        return self._versions.get((subject, provider, task_type), 0)

    def advance(self, subject: str, provider: str, task_type: str) -> AuthorizationEpoch:
        scope = (subject, provider, task_type)
        version = self._versions.get(scope, 0) + 1
        self._versions[scope] = version
        return AuthorizationEpoch(subject, provider, task_type, version)

    def is_current(self, record: AuthorizationEpoch) -> bool:
        return record.version == self.current(record.subject, record.provider, record.task_type)


@dataclass(frozen=True)
class EpochCheck:
    current: bool
    reason: str


class AuthorizationEpochGuard:
    def __init__(self, registry: AuthorizationEpochRegistry) -> None:
        self.registry = registry

    def check(self, record: AuthorizationEpoch) -> EpochCheck:
        current = self.registry.is_current(record)
        if current:
            return EpochCheck(True, "authorization epoch is current")
        return EpochCheck(False, "authorization decision is stale")
