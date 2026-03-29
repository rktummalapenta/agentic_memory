"""HTTP client for the local LLM gateway."""

from __future__ import annotations

import json
from typing import Any

import httpx


class GatewayClient:
    def __init__(
        self,
        base_url: str,
        chat_completions_path: str,
        model: str,
        fallback_model: str | None = None,
        model_provider: str = "openai",
        timeout_seconds: float = 60.0,
    ) -> None:
        self.url = f"{base_url.rstrip('/')}{chat_completions_path}"
        self.model = model
        self.fallback_model = fallback_model
        self.model_provider = model_provider
        self.timeout_seconds = timeout_seconds
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout_seconds),
            headers={
                "accept": "application/json",
                "Content-Type": "application/json",
            },
        )

    async def generate_sql(self, messages: list[dict[str, str]]) -> str:
        data = await self._request_sql(messages, self.model)
        content = data.get("data", {}).get("content", "")
        if isinstance(content, str) and content.strip():
            return _extract_sql(content)

        if self.fallback_model and self.fallback_model != self.model:
            data = await self._request_sql(messages, self.fallback_model)
            content = data.get("data", {}).get("content", "")

        if not isinstance(content, str) or not content.strip():
            raise RuntimeError(f"LLM gateway returned empty content: {data}")
        return _extract_sql(content)

    async def _request_sql(self, messages: list[dict[str, str]], model: str) -> dict[str, Any]:
        payload = {
            "messages": messages,
            "model_provider": self.model_provider,
            "model": model,
        }
        try:
            response = await self._client.post(self.url, json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            if (
                self.fallback_model
                and model == self.model
                and self.fallback_model != self.model
                and exc.response.status_code in {429, 500, 502, 503, 504}
            ):
                return await self._request_sql(messages, self.fallback_model)
            raise RuntimeError(f"LLM gateway request failed: {exc}") from exc
        except (httpx.HTTPError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"LLM gateway request failed: {exc}") from exc

    async def aclose(self) -> None:
        await self._client.aclose()


def _extract_sql(content: str) -> str:
    text = content.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    if text.lower().startswith("sql\n"):
        text = text[4:].strip()
    return text.rstrip(";") + ";"
