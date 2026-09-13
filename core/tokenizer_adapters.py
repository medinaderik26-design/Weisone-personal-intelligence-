"""PI-028 concrete tokenizer adapter contracts.

Adapters convert provider/model-specific tokenization into the provider-neutral
PI-027 TokenMeasurement contract. Optional tokenizer libraries are loaded only
when the caller installs them; this core package never guesses token counts.
"""

from dataclasses import dataclass
from typing import Optional, Protocol

from .token_measurement import TokenMeasurement


class Tokenizer(Protocol):
    def count(self, text: str) -> int:
        ...


@dataclass(frozen=True)
class GenericTokenizerAdapter:
    """Wrap any installed tokenizer that exposes a count-like callable."""

    tokenizer: Tokenizer
    provider: str
    model: str

    def measure(self, text: str) -> TokenMeasurement:
        count = self.tokenizer.count(text)
        measurement = TokenMeasurement(
            provider=self.provider,
            model=self.model,
            input_tokens=count,
            source="tokenizer",
        )
        measurement.validate()
        return measurement


class TiktokenAdapter:
    """Optional adapter for OpenAI-compatible tokenization via tiktoken.

    The dependency is intentionally optional. If it is not installed, callers
    receive an explicit error rather than a guessed token count.
    """

    def __init__(self, model: str, provider: str = "openai") -> None:
        try:
            import tiktoken
        except ImportError as exc:
            raise RuntimeError(
                "tiktoken is required for TiktokenAdapter; install it explicitly"
            ) from exc

        try:
            self._encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            self._encoding = tiktoken.get_encoding("o200k_base")
        self.provider = provider
        self.model = model

    def measure(self, text: str) -> TokenMeasurement:
        count = len(self._encoding.encode(text))
        measurement = TokenMeasurement(
            provider=self.provider,
            model=self.model,
            input_tokens=count,
            source="tokenizer",
        )
        measurement.validate()
        return measurement


def provider_reported_measurement(
    *,
    provider: str,
    model: str,
    input_tokens: Optional[int] = None,
    output_tokens: Optional[int] = None,
    context_tokens: Optional[int] = None,
) -> TokenMeasurement:
    """Create a measurement from usage numbers explicitly reported by a provider."""

    measurement = TokenMeasurement(
        provider=provider,
        model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        context_tokens=context_tokens,
        source="provider_reported",
    )
    measurement.validate()
    return measurement
