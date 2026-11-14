"""
Grok API client for COGNIFY AI agents.

Async httpx-based client wrapping the xAI Grok chat-completions endpoint
with retry logic, structured JSON output, and proper error handling.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from typing import Any

import httpx

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Custom exception
# ---------------------------------------------------------------------------

class GrokAPIError(Exception):
    """Raised when the Grok API is unreachable or returns an error."""

    def __init__(self, message: str, status_code: int | None = None, raw: str | None = None):
        self.status_code = status_code
        self.raw = raw
        super().__init__(message)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

_GROK_URL = "https://api.x.ai/v1/chat/completions"
_GROK_MODEL = "grok-3-mini-fast"
_GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
_TIMEOUT = 10.0  # seconds
_MAX_RETRIES = 2
_BACKOFF_BASE = 1.0  # first retry after 1 s, then 2 s


def _api_key() -> tuple[str, str]:
    """Returns (provider, api_key) where provider is 'gemini' or 'grok'."""
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    if gemini_key:
        return "gemini", gemini_key
    grok_key = os.getenv("GROK_API_KEY", "")
    if grok_key:
        return "grok", grok_key
    raise GrokAPIError("Neither GEMINI_API_KEY nor GROK_API_KEY environment variable is set")


# ---------------------------------------------------------------------------
# Public async helper
# ---------------------------------------------------------------------------

async def _call_gemini(api_key: str, system_prompt: str, user_prompt: str) -> dict[str, Any]:
    url = f"{_GEMINI_URL}?key={api_key}"
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": f"SYSTEM INSTRUCTIONS:\n{system_prompt}\n\nUSER REQUEST:\n{user_prompt}\n\nCRITICAL: Respond ONLY with valid, raw JSON. Do not add markdown fences or extra explanations."}
                ]
            }
        ],
        "generationConfig": {
            "response_mime_type": "application/json",
            "temperature": 0.2
        }
    }
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        resp = await client.post(url, json=payload)
    if resp.status_code != 200:
        raise GrokAPIError(f"Gemini API returned status {resp.status_code}: {resp.text[:300]}", status_code=resp.status_code)
    data = resp.json()
    text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
    return json.loads(text)


async def _call_grok(api_key: str, system_prompt: str, user_prompt: str, temperature: float, max_tokens: int) -> dict[str, Any]:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": _GROK_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        response = await client.post(_GROK_URL, json=payload, headers=headers)

    if response.status_code != 200:
        raise GrokAPIError(f"Grok API error {response.status_code}: {response.text[:300]}", status_code=response.status_code)
    data = response.json()
    text = data["choices"][0]["message"]["content"].strip()
    if text.startswith("```"):
        first_newline = text.index("\n")
        text = text[first_newline + 1 :]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
    return json.loads(text)


async def grok_chat(
    system_prompt: str,
    user_prompt: str,
    *,
    temperature: float = 0.3,
    max_tokens: int = 4096,
) -> dict[str, Any]:
    """Send a chat completion request to Gemini or Grok and return the parsed JSON dict."""
    provider, api_key = _api_key()

    last_exc: Exception | None = None

    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            if provider == "gemini":
                return await _call_gemini(api_key, system_prompt, user_prompt)
            else:
                return await _call_grok(api_key, system_prompt, user_prompt, temperature, max_tokens)

        except (httpx.HTTPError, httpx.TimeoutException, asyncio.TimeoutError) as exc:
            last_exc = GrokAPIError(f"Network error on attempt {attempt}/{_MAX_RETRIES}: {exc}")
            logger.warning("AI API attempt %d failed: %s", attempt, exc)

        except GrokAPIError as exc:
            last_exc = exc
            logger.warning("AI API attempt %d error: %s", attempt, exc)

        except (json.JSONDecodeError, KeyError, IndexError) as exc:
            last_exc = GrokAPIError(f"Failed to parse AI response: {exc}")
            logger.warning("AI response parse error attempt %d: %s", attempt, exc)

        if attempt < _MAX_RETRIES:
            await asyncio.sleep(1.0)

    raise last_exc  # type: ignore[misc]
