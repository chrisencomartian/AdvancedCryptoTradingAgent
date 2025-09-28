"""Binance data client abstraction.

This module intentionally avoids hitting the real Binance API. Instead, it
provides a thin wrapper around HTTP requests and caching that can be swapped
with real network calls when credentials are supplied. The goal is to provide a
high-frequency friendly interface without depending on external libraries.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import urllib.request

from ..config import AgentConfig
from ..utils.logger import get_logger


@dataclass(slots=True)
class CachedResponse:
    """Container for cached API responses."""

    timestamp: float
    payload: Dict


class BinanceClient:
    """Minimal client for fetching market data from Binance REST endpoints."""

    BASE_URL = "https://api.binance.com"

    def __init__(self, config: AgentConfig) -> None:
        self._config = config
        self._cache: Dict[Tuple[str, str], CachedResponse] = {}
        self._logger = get_logger(self.__class__.__name__)
        self._cache_dir = config.data.cache_dir
        self._cache_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def get_klines(self, symbol: str, limit: int | None = None) -> List[Dict]:
        """Return candlestick data for a given trading pair."""

        params = {
            "symbol": symbol,
            "interval": self._config.data.klines_interval,
            "limit": limit or self._config.data.history_window,
        }
        endpoint = "/api/v3/klines"
        response = self._request(endpoint, params)
        klines = [
            {
                "open_time": int(item[0]),
                "open": float(item[1]),
                "high": float(item[2]),
                "low": float(item[3]),
                "close": float(item[4]),
                "volume": float(item[5]),
            }
            for item in response
        ]
        return klines

    # ------------------------------------------------------------------
    # Internal utilities
    # ------------------------------------------------------------------
    def _request(self, endpoint: str, params: Dict[str, str | int]) -> List:
        url = self.BASE_URL + endpoint
        query = "&".join(f"{key}={value}" for key, value in params.items())
        url = f"{url}?{query}"

        cache_key = (endpoint, json.dumps(params, sort_keys=True))
        cached = self._cache.get(cache_key)
        if cached and time.time() - cached.timestamp < 30:
            return cached.payload

        self._logger.debug("Requesting %s", url)
        with urllib.request.urlopen(url, timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))

        self._cache[cache_key] = CachedResponse(time.time(), payload)
        return payload

    def warm_cache(self, symbols: Iterable[str]) -> None:
        """Pre-load cache for multiple symbols to avoid network spikes."""

        for symbol in symbols:
            try:
                self.get_klines(symbol)
            except Exception as exc:  # pragma: no cover - network errors handled gracefully
                self._logger.warning("Failed to warm cache for %s: %s", symbol, exc)


__all__ = ["BinanceClient"]
