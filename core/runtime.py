"""PI-001 execution loop."""

from .continuity import ContinuityStore
from .models import ContinuityEvent, ExecutionRecord, Identity, Task
from .permissions import PermissionEngine
from .router import IntelligenceRouter


class PersonalIntelligence:
    def __init__(
        self,
        identity: Identity,
        permissions: PermissionEngine,
        router: IntelligenceRouter,
        continuity: ContinuityStore,
    ) -> None:
        self.identity = identity
        self.permissions = permissions
        self.router = router
        self.continuity = continuity

    def execute(self, task: Task) -> ExecutionRecord:
        # Provider invocation is an intelligence action. Keep this explicit so future
        # policy can distinguish model calls from tool calls.
        self.permissions.require("intelligence", "execute")

        provider = self.router.select(task)
        result = provider.generate(task)

        self.continuity.remember(
            ContinuityEvent(
                task_id=task.task_id,
                kind="execution",
                payload={
                    "prompt": task.prompt,
                    "provider": result.provider,
                    "model": result.model,
                    "success": result.success,
                    "response": result.text,
                },
            )
        )

        return ExecutionRecord(
            task=task,
            result=result,
            continuity_updated=True,
        )
