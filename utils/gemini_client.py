#utils/gemini_client.py
"""
Shared Gemini API client used by every agent that calls out to Gemini
(hotel, food, tour, flight, transport, booking).

Centralizing this in one place means the model name and API version only
need to be updated in one spot when Google deprecates a model - which they
do frequently. `gemini-pro` on the `v1beta` endpoint (the original,
per-agent-duplicated implementation) was deprecated and returns 404 even
with a valid API key; `v1beta` itself is deprecated for production use in
favor of `v1`.

The model is configurable via the GEMINI_MODEL environment variable so a
future rename doesn't require another code change - just an env var update.
"""
import os
import logging
import requests

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "gemini-2.5-flash"
API_VERSION = "v1"


def call_gemini(text: str, api_key: str = None, model: str = None, timeout: int = 15) -> str:
    """
    Call the Gemini generateContent endpoint with a plain-text prompt and
    return the generated text.

    Raises:
        ValueError: if no API key is available (env var or argument).
        requests.RequestException: on network/HTTP errors.
        (KeyError, IndexError): if the response doesn't have the expected
            candidates[0].content.parts[0].text shape.
    """
    api_key = api_key or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable not set")

    model = model or os.getenv("GEMINI_MODEL", DEFAULT_MODEL)
    url = f"https://generativelanguage.googleapis.com/{API_VERSION}/models/{model}:generateContent"

    resp = requests.post(
        url,
        headers={"x-goog-api-key": api_key, "Content-Type": "application/json"},
        json={"contents": [{"parts": [{"text": text}]}]},
        timeout=timeout,
    )
    resp.raise_for_status()
    data = resp.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]
