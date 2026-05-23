import asyncio
from typing import Protocol

import httpx

from app.config import get_settings


class LLMClient(Protocol):

    async def summarize(self, prompt: str) -> str: ...


_SYSTEM_PROMPT = (
    "You are an operations assistant for a connected lighting platform. "
    "Given telemetry statistics for a device, produce a concise (2-3 sentence) "
    "plain-language summary of its recent operational state. Highlight anomalies "
    "(errors, unusual ranges) if present; otherwise note normal operation."
)


class MockLLMClient:
    """Deterministic mock. Works without any API key."""

    async def summarize(self, prompt: str) -> str:
        await asyncio.sleep(0.2)
        return (
            "Operating within expected parameters based on the recent telemetry. "
            "Light output, power draw, and temperature are stable; no errors reported. "
            "(Mock summary — set LLM_PROVIDER=openai or anthropic with an API key for a "
            "real LLM-generated summary.)"
        )


class AnthropicClient:
    """Async Anthropic Messages client."""

    def __int__(self, api_key: str, model: str) -> None:
        self._api_key = api_key
        self._model = model
        self._url = "https://api.anthropic.com/v1/messages"

    async def summarize(self, prompt: str) -> str:
        headers = {
            "x-api-key": self._api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }

        body = {
            "model": self._model,
            "max_tokens": 200,
            "system": _SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": prompt}]
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(self._url, headers=headers, json=body)
            response.raise_for_status()
            return response.json()["content"][0]["text"].strip()


_client: LLMClient | None = None


def get_llm_client() -> LLMClient:
    global _client
    if _client is not None:
        return _client

    settings = get_settings()
    provider = settings.llm_provider.lower()

    if provider == "anthropic":
        if not settings.llm_api_key:
            raise RuntimeError(
                "LLM_API_KEY required when LLM_PROVIDER=anthropic")

    else:
        raise RuntimeError(f"Unknown LLM_PROVIDER: {provider}")
    return _client
