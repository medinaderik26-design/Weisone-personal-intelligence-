"""Execution accounting wrapper for Personal Intelligence providers.

This module keeps resource accounting separate from the v0.1 runtime while the
execution contract is stabilized. It can later be folded into runtime.py.
"""

from time import monotonic

from .models import Result, Task
from .providers import IntelligenceProvider
from .resource_manager import ResourceManager


class AccountedExecution:
    """Execute one provider request and record measurable resource signals."""

    def __init__(self, resource_manager: ResourceManager):
        self.resource_manager = resource_manager

    def run(self, provider: IntelligenceProvider, task: Task) -> Result:
        started = monotonic()
        try:
            result = provider.generate(task)
        except Exception:
            latency_ms = (monotonic() - started) * 1000
            self.resource_manager.record_request(
                provider.name,
                latency_ms=latency_ms,
                failed=True,
            )
            raise

        latency_ms = (monotonic() - started) * 1000
        usage = result.usage or {}
        input_tokens = int(usage.get("input_tokens", 0) or 0)
        output_tokens = int(usage.get("output_tokens", 0) or 0)
        estimated_cost = float(usage.get("estimated_cost", 0.0) or 0.0)

        self.resource_manager.record_request(
            provider.name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            estimated_cost=estimated_cost,
            latency_ms=latency_ms,
            failed=not result.success,
        )
        result.latency_ms = latency_ms
        return result
