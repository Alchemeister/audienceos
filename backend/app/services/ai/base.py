"""Abstract base class for AI providers."""

from abc import ABC, abstractmethod
from typing import Any


class AIProvider(ABC):
    """Abstract base class for AI model providers."""

    @abstractmethod
    async def complete(
        self,
        prompt: str,
        system: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> str:
        """
        Generate a text completion.

        Args:
            prompt: The user prompt to complete
            system: Optional system prompt
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0-1)

        Returns:
            The generated text completion
        """
        ...

    @abstractmethod
    async def complete_json(
        self,
        prompt: str,
        system: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.3,
    ) -> dict[str, Any]:
        """
        Generate a JSON completion.

        Args:
            prompt: The user prompt requesting JSON output
            system: Optional system prompt
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (lower for JSON)

        Returns:
            Parsed JSON response as a dictionary
        """
        ...

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return the name of the model being used."""
        ...

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the name of the provider (e.g., 'anthropic', 'deepseek')."""
        ...
