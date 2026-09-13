"""Continuity abstraction.

PI-001 deliberately uses a simple in-memory implementation. A future Glyphin or Wison
Kernel adapter can implement the same interface without changing the orchestration layer.
"""

from typing import List
from .models import ContinuityEvent


class ContinuityStore:
    def remember(self, event: ContinuityEvent) -> None:
        raise NotImplementedError

    def recall(self, query: str) -> List[ContinuityEvent]:
        raise NotImplementedError


class InMemoryContinuity(ContinuityStore):
    def __init__(self) -> None:
        self.events: List[ContinuityEvent] = []

    def remember(self, event: ContinuityEvent) -> None:
        self.events.append(event)

    def recall(self, query: str) -> List[ContinuityEvent]:
        query_lower = query.lower()
        return [
            event
            for event in self.events
            if query_lower in str(event.payload).lower()
            or query_lower in event.kind.lower()
        ]
