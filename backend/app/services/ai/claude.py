"""Claude (Anthropic) AI provider implementation."""

import json
import logging
from typing import Any

import anthropic

from app.core.exceptions import AIServiceError
from app.services.ai.base import AIProvider

logger = logging.getLogger(__name__)


class ClaudeProvider(AIProvider):
    """Claude API provider for expensive/high-quality tasks."""

    def __init__(
        self,
        api_key: str,
        model: str = "claude-sonnet-4-20250514",
    ):
        """
        Initialize Claude provider.

        Args:
            api_key: Anthropic API key
            model: Model to use (default: claude-sonnet-4-20250514)
        """
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        self.model = model

    @property
    def model_name(self) -> str:
        return self.model

    @property
    def provider_name(self) -> str:
        return "anthropic"

    async def complete(
        self,
        prompt: str,
        system: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> str:
        """Generate a text completion using Claude."""
        try:
            message = await self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system or "You are a helpful assistant.",
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
            )

            # Extract text from response
            if message.content and len(message.content) > 0:
                return message.content[0].text

            return ""

        except anthropic.RateLimitError as e:
            logger.warning(f"Claude rate limit hit: {e}")
            raise AIServiceError(
                message="Rate limit exceeded",
                provider="anthropic",
                status_code=429,
            )
        except anthropic.APIError as e:
            logger.error(f"Claude API error: {e}")
            raise AIServiceError(
                message=str(e),
                provider="anthropic",
                status_code=getattr(e, "status_code", None),
            )

    async def complete_json(
        self,
        prompt: str,
        system: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.3,
    ) -> dict[str, Any]:
        """Generate a JSON completion using Claude."""
        # Add JSON instruction to system prompt
        json_system = (system or "") + "\n\nRespond only with valid JSON. No markdown, no explanation, just the JSON object."

        response = await self.complete(
            prompt=prompt,
            system=json_system.strip(),
            max_tokens=max_tokens,
            temperature=temperature,
        )

        # Parse JSON from response
        try:
            # Try to extract JSON if wrapped in markdown code blocks
            text = response.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]

            return json.loads(text.strip())
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Claude JSON response: {e}\nResponse: {response}")
            raise AIServiceError(
                message=f"Invalid JSON response: {e}",
                provider="anthropic",
            )
