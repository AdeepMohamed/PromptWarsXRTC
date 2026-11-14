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

_BASE_URL = "https://api.x.ai/v1/chat/completions"
_MODEL = "grok-3-mini-fast"
_TIMEOUT = 30.0  # seconds
_MAX_RETRIES = 3
_BACKOFF_BASE = 1.0  # first retry after 1 s, then 2 s, then 4 s


def _api_key() -> str:
    key = os.getenv("GROK_API_KEY", "")
    if not key:
        raise GrokAPIError("GROK_API_KEY environment variable is not set")
    return key


# ---------------------------------------------------------------------------
# Public async helper
# ---------------------------------------------------------------------------

async def grok_chat(
    system_prompt: str,
    user_prompt: str,
    *,
    temperature: float = 0.3,
    max_tokens: int = 4096,
) -> dict[str, Any]:
    """Send a chat completion request and return the parsed JSON dict.

    The *system_prompt* must instruct the model to reply strictly in JSON.
    The function parses the model's text content as JSON; if parsing fails it
    retries (with the same retry budget as network errors).

    Raises
    ------
    GrokAPIError
        On network failures, HTTP errors, or unparseable responses after all
        retries are exhausted.
    """

    api_key = _api_key()

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": _MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    last_exc: Exception | None = None

    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                response = await client.post(_BASE_URL, json=payload, headers=headers)

            if response.status_code == 429 or response.status_code >= 500:
                # Retriable server / rate-limit error
                raise GrokAPIError(
                    f"Grok API returned {response.status_code}",
                    status_code=response.status_code,
                    raw=response.text,
                )

            if response.status_code != 200:
                raise GrokAPIError(
                    f"Grok API error {response.status_code}: {response.text[:500]}",
                    status_code=response.status_code,
                    raw=response.text,
                )

            data = response.json()
            text = data["choices"][0]["message"]["content"]

            # Strip markdown fences if the model wraps its JSON
            cleaned = text.strip()
            if cleaned.startswith("```"):
                first_newline = cleaned.index("\n")
                cleaned = cleaned[first_newline + 1 :]
                if cleaned.endswith("```"):
                    cleaned = cleaned[: -3]
                cleaned = cleaned.strip()

            return json.loads(cleaned)

        except (httpx.HTTPError, httpx.TimeoutException, asyncio.TimeoutError) as exc:
            last_exc = GrokAPIError(
                f"Network error on attempt {attempt}/{_MAX_RETRIES}: {exc}",
            )
            logger.warning("Grok API attempt %d failed: %s", attempt, exc)

        except GrokAPIError as exc:
            last_exc = exc
            logger.warning("Grok API attempt %d error: %s", attempt, exc)

        except (json.JSONDecodeError, KeyError, IndexError) as exc:
            last_exc = GrokAPIError(f"Failed to parse Grok response: {exc}")
            logger.warning("Grok response parse error attempt %d: %s", attempt, exc)

        # Exponential back-off before next retry
        if attempt < _MAX_RETRIES:
            wait = _BACKOFF_BASE * (2 ** (attempt - 1))
            logger.info("Retrying Grok API in %.1fs …", wait)
            await asyncio.sleep(wait)

    raise last_exc  # type: ignore[misc]
