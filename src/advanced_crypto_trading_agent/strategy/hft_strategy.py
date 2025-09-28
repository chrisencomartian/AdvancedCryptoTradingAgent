"""High-frequency trading strategy combining multiple signals."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable

from ..analysis.fundamental import fundamental_score
from ..analysis.sentiment import SentimentReading, aggregate_sentiment
from ..analysis.technical import IndicatorResult, generate_technical_signal
from ..config import FundamentalConfig, SentimentConfig, TechnicalConfig


@dataclass(slots=True)
class StrategyContext:
    """Aggregated signal context used for decision making."""

    technical: IndicatorResult
    fundamental: float
    sentiment: float

    @property
    def composite_signal(self) -> float:
        """Return a weighted composite signal between -1 and 1."""

        return max(min(self.technical.signal * 0.5 + self.fundamental * 0.3 + self.sentiment * 0.2, 1.0), -1.0)


def build_strategy_context(
    prices: Iterable[float],
    technical_config: TechnicalConfig,
    fundamentals: Dict[str, Iterable[float]],
    fundamental_config: FundamentalConfig,
    sentiment_readings: Iterable[SentimentReading],
    sentiment_config: SentimentConfig,
) -> StrategyContext:
    """Build the strategy context by combining multiple signal sources."""

    technical = generate_technical_signal(prices, technical_config)
    fundamental = fundamental_score(fundamentals, fundamental_config.metrics_weights)
    sentiment = aggregate_sentiment(sentiment_readings, sentiment_config.smoothing)
    return StrategyContext(technical=technical, fundamental=fundamental, sentiment=sentiment)


__all__ = ["StrategyContext", "build_strategy_context"]
