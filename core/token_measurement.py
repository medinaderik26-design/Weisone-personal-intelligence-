"""PI-027 provider-neutral token measurement boundary.

Token counts must come from an actual tokenizer or a provider-reported usage
record. Character counts and word counts are intentionally not substitutes.
"""

from dataclasses import dataclass
from typing import Callable, Optional


@dataclass(frozen=True)
class TokenMeasurement:
    provider: str
    model: str
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    context_tokens: Optional[int] = None
    source: str = "unknown"

    def validate(self) -> None:
        if not self.provider:
            raise ValueError("provider is required")
        if not self.model:
            raise ValueError("model is required")
        for name in ("input_tokens", "output_tokens", "context_tokens"):
            value = getattr(self, name)
            if value is not None and value < 0:
                raise ValueError(f"{name} cannot be negative")
        if self.source not in {"tokenizer", "provider_reported", "unknown"}:
            raise ValueError("invalid token measurement source")


class TokenMeasurementAdapter:
    """Adapter around a real tokenizer callable.

    The callable receives text and returns the tokenizer's integer token count.
    """

    def __init__(self, tokenizer: Callable[[str], int], provider: str, model: str) -> None:
        self.tokenizer = tokenizer
        self.provider = provider
        self.model = model

    def measure_input(self, text: str) -> TokenMeasurement:
        count = self.tokenizer(text)
        measurement = TokenMeasurement(
            provider=self.provider,
            model=self.model,
            input_tokens=count,
            source="tokenizer",
        )
        measurement.validate()
        return measurement
