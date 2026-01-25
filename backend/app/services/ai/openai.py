"""OpenAI provider implementation for GPT-4o-mini (cheap) operations."""

import json
import logging
from typing import Any

import httpx

from app.core.exceptions import AIServiceError
from app.services.ai.base import AIProvider

logger = logging.getLogger(__name__)

OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"


class OpenAIProvider(AIProvider):
    """OpenAI API provider for GPT-4o-mini (cheap tier)."""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        timeout: float = 30.0,
    ):
        """
        Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key
            model: Model to use (default: gpt-4o-mini)
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
        return "openai"

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
        """Generate a text completion using OpenAI."""
        client = await self._get_client()

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        try:
            response = await client.post(
                OPENAI_API_URL,
                json={
                    "model": self.model,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                },
            )

            if response.status_code == 429:
                logger.warning("OpenAI rate limit hit")
                raise AIServiceError(
                    message="Rate limit exceeded",
                    provider="openai",
                    status_code=429,
                )

            if response.status_code != 200:
                logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
                raise AIServiceError(
                    message=f"API error: {response.status_code}",
                    provider="openai",
                    status_code=response.status_code,
                )

            data = response.json()
            return data["choices"][0]["message"]["content"]

        except httpx.HTTPError as e:
            logger.error(f"OpenAI HTTP error: {e}")
            raise AIServiceError(
                message=str(e),
                provider="openai",
            )

    async def complete_json(
        self,
        prompt: str,
        system: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.3,
    ) -> dict[str, Any]:
        """Generate a JSON completion using OpenAI."""
        client = await self._get_client()

        messages = []
        json_system = (system or "") + "\n\nRespond only with valid JSON."
        messages.append({"role": "system", "content": json_system.strip()})
        messages.append({"role": "user", "content": prompt})

        try:
            response = await client.post(
                OPENAI_API_URL,
                json={
                    "model": self.model,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "response_format": {"type": "json_object"},
                },
            )

            if response.status_code == 429:
                logger.warning("OpenAI rate limit hit")
                raise AIServiceError(
                    message="Rate limit exceeded",
                    provider="openai",
                    status_code=429,
                )

            if response.status_code != 200:
                logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
                raise AIServiceError(
                    message=f"API error: {response.status_code}",
                    provider="openai",
                    status_code=response.status_code,
                )

            data = response.json()
            content = data["choices"][0]["message"]["content"]
            return json.loads(content)

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse OpenAI JSON response: {e}")
            raise AIServiceError(
                message=f"Invalid JSON response: {e}",
                provider="openai",
            )
        except httpx.HTTPError as e:
            logger.error(f"OpenAI HTTP error: {e}")
            raise AIServiceError(
                message=str(e),
                provider="openai",
            )

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None
