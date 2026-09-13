"""Minimal permission boundary for PI-001.

Default-deny is intentional. Tool/provider adapters must not gain authority merely by
being installed.
"""

from dataclasses import dataclass
from typing import Iterable, Set, Tuple


@dataclass
class PermissionEngine:
    grants: Set[Tuple[str, str]]

    @classmethod
    def deny_all(cls) -> "PermissionEngine":
        return cls(grants=set())

    def grant(self, resource: str, action: str) -> None:
        self.grants.add((resource, action))

    def revoke(self, resource: str, action: str) -> None:
        self.grants.discard((resource, action))

    def allowed(self, resource: str, action: str) -> bool:
        return (resource, action) in self.grants

    def require(self, resource: str, action: str) -> None:
        if not self.allowed(resource, action):
            raise PermissionError(f"Permission denied: {action} on {resource}")
