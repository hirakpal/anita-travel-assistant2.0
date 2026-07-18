#utils/cache.py
"""
Lightweight in-memory API response cache with hit/miss efficiency tracking.

This intentionally avoids a hard dependency on Redis (redis is listed as an
optional extra in requirements.txt) so the project works out of the box with
zero external services. If REDIS_URL is set in the environment, callers may
later swap this module's storage backend without changing the public API
(call_api / savings_percent / clear_cache).
"""
import hashlib
import json
import time
from typing import Any, Dict, Optional

# In-memory cache store: {cache_key: (value, expires_at)}
_cache_store: Dict[str, Any] = {}

# Efficiency counters
_stats = {"hits": 0, "misses": 0}

DEFAULT_TTL_SECONDS = 300  # 5 minutes


def _make_key(service: str, params: dict) -> str:
    """Build a stable cache key from a service name + params dict."""
    payload = json.dumps(params, sort_keys=True, default=str)
    digest = hashlib.sha256(f"{service}:{payload}".encode()).hexdigest()
    return f"{service}:{digest}"


def call_api(service: str, params: dict, fetch_fn=None, ttl: int = DEFAULT_TTL_SECONDS) -> Any:
    """
    Cache-wrapped API call.

    - service: logical name of the API/service being called (e.g. "google_maps")
    - params: request parameters, used to build the cache key
    - fetch_fn: optional zero-arg callable that performs the real API call and
      returns a value to cache. If omitted, a deterministic stub response is
      generated from (service, params) - useful for tests and Demo mode where
      no real network call should happen.
    - ttl: seconds the cached value remains valid

    Returns the (possibly cached) response value.
    """
    key = _make_key(service, params)
    now = time.time()

    cached = _cache_store.get(key)
    if cached is not None:
        value, expires_at = cached
        if expires_at > now:
            _stats["hits"] += 1
            return value

    _stats["misses"] += 1
    if fetch_fn is not None:
        value = fetch_fn()
    else:
        # Deterministic stub so repeated calls with the same params are
        # cache-hittable without requiring a real network call.
        value = {"service": service, "params": params, "stub": True}

    _cache_store[key] = (value, now + ttl)
    return value


def savings_percent() -> float:
    """
    Percentage of call_api() invocations that were served from cache instead
    of triggering a fresh fetch. Returns 0.0 if no calls have been made yet.
    """
    total = _stats["hits"] + _stats["misses"]
    if total == 0:
        return 0.0
    return round((_stats["hits"] / total) * 100, 2)


def get_stats() -> Dict[str, int]:
    """Return raw hit/miss counters."""
    return dict(_stats)


def clear_cache() -> None:
    """Clear all cached entries and reset hit/miss counters (mainly for tests)."""
    _cache_store.clear()
    _stats["hits"] = 0
    _stats["misses"] = 0
