"""DeepSeek AI provider implementation for cheap/bulk processing."""

import json
import logging
from typing import Any

import httpx

from app.core.exceptions import AIServiceError
from app.services.ai.base import AIProvider

logger = logging.getLogger(__name__)

# DeepSeek API endpoint (OpenAI-compatible)
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"


class DeepSeekProvider(AIProvider):
    """DeepSeek API provider for cheap bulk processing tasks."""

    def __init__(
        self,
        api_key: str,
        model: str = "deepseek-chat",
        timeout: float = 30.0,
    ):
        """
        Initialize DeepSeek provider.

        Args:
            api_key: DeepSeek API key
            model: Model to use (default: deepseek-chat)
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self._client: httpx.AsyncClient | None = None

    @property
    def model_name(self) -> str:
        return self.model

    @property
    def provider_name(self) -> str:
        return "deepseek"

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
            )
        return self._client

    async def complete(
        self,
        prompt: str,
        system: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> str:
        """Generate a text completion using DeepSeek."""
        client = await self._get_client()

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        try:
            response = await client.post(
                DEEPSEEK_API_URL,
                json={
                    "model": self.model,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                },
            )

            if response.status_code == 429:
                logger.warning("DeepSeek rate limit hit")
                raise AIServiceError(
                    message="Rate limit exceeded",
                    provider="deepseek",
                    status_code=429,
                )

            if response.status_code != 200:
                logger.error(f"DeepSeek API error: {response.status_code} - {response.text}")
                raise AIServiceError(
                    message=f"API error: {response.status_code}",
                    provider="deepseek",
                    status_code=response.status_code,
                )

            data = response.json()
            return data["choices"][0]["message"]["content"]

        except httpx.HTTPError as e:
            logger.error(f"DeepSeek HTTP error: {e}")
            raise AIServiceError(
                message=str(e),
                provider="deepseek",
            )

    async def complete_json(
        self,
        prompt: str,
        system: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.3,
    ) -> dict[str, Any]:
        """Generate a JSON completion using DeepSeek."""
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
            logger.error(f"Failed to parse DeepSeek JSON response: {e}\nResponse: {response}")
            raise AIServiceError(
                message=f"Invalid JSON response: {e}",
                provider="deepseek",
            )

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None
