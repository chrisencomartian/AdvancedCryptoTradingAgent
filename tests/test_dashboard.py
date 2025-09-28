from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List

from advanced_crypto_trading_agent.analysis.sentiment import SentimentReading
from advanced_crypto_trading_agent.trader import MarketSnapshot
from advanced_crypto_trading_agent.web.dashboard import RecommendationEngine


@dataclass
class _FakeContext:
    composite_signal: float


class _FakeAgent:
    def __init__(self, signals: Dict[str, float]) -> None:
        self._signals = signals

    def collect_market_data(self, symbol: str) -> MarketSnapshot:
        base = 100.0 + len(symbol)
        prices = [base + offset for offset in range(30)]
        highs = [price + 2 for price in prices]
        lows = [price - 2 for price in prices]
        closes = prices
        return MarketSnapshot(symbol=symbol, prices=prices, highs=highs, lows=lows, closes=closes)

    def build_context(
        self,
        snapshot: MarketSnapshot,
        fundamentals: Dict[str, Iterable[float]],
        sentiment: Iterable[SentimentReading],
    ) -> _FakeContext:
        return _FakeContext(self._signals[snapshot.symbol])


def _fundamentals(_: str) -> Dict[str, List[float]]:
    return {"metric": [1.0] * 30}


def _sentiment(_: str) -> List[SentimentReading]:
    return [SentimentReading(source="test", score=0.0)]


def test_recommendations_sorted_by_probability() -> None:
    agent = _FakeAgent({"BTCUSDT": 0.9, "ETHUSDT": 0.2, "SOLUSDT": -0.7})
    engine = RecommendationEngine(agent, _fundamentals, _sentiment)

    recommendations = engine.refresh(["ETHUSDT", "BTCUSDT", "SOLUSDT"])

    probabilities = [rec.probability for rec in recommendations]
    assert recommendations[0].symbol == "BTCUSDT"
    assert probabilities == sorted(probabilities, reverse=True)
    assert any(rec.symbol == "SOLUSDT" and rec.side == "SHORT" for rec in recommendations)
