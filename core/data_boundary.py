"""PI-034 personal data boundary and minimization policy."""

from dataclasses import dataclass
from typing import Iterable, List

from .models import Task


@dataclass(frozen=True)
class DataField:
    name: str
    sensitivity: str = "normal"
    purpose: str = "general"


@dataclass(frozen=True)
class BoundaryDecision:
    allowed: bool
    fields: tuple[str, ...]
    denied_fields: tuple[str, ...]
    reason: str


class DataBoundary:
    """Decide which fields may cross a provider boundary.

    This is a policy layer only. It does not transmit data and does not grant
    provider access. Unknown or unnecessary fields remain outside the request.
    """

    def filter(
        self,
        task: Task,
        fields: Iterable[DataField],
        *,
        provider: str,
        authorized_sensitivities: Iterable[str] = ("normal",),
    ) -> BoundaryDecision:
        allowed_sensitivities = set(authorized_sensitivities)
        selected: List[str] = []
        denied: List[str] = []

        for field in fields:
            if field.sensitivity not in allowed_sensitivities:
                denied.append(field.name)
                continue
            if field.purpose != task.task_type and field.purpose != "general":
                denied.append(field.name)
                continue
            selected.append(field.name)

        if task.privacy == "high" and provider != "local":
            return BoundaryDecision(False, (), tuple(field.name for field in fields), "high-privacy data is local-only")

        return BoundaryDecision(
            allowed=True,
            fields=tuple(selected),
            denied_fields=tuple(denied),
            reason="only authorized, purpose-compatible fields selected",
        )
