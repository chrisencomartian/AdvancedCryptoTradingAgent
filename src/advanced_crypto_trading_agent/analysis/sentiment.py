"""Sentiment analysis aggregation for crypto markets."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable


@dataclass(slots=True)
class SentimentReading:
    """Represents a sentiment reading from a particular source."""

    source: str
    score: float


def exponential_smoothing(previous: float, current: float, alpha: float) -> float:
    """Apply exponential smoothing to reduce noise."""

    return alpha * current + (1 - alpha) * previous


def aggregate_sentiment(readings: Iterable[SentimentReading], alpha: float) -> float:
    """Aggregate sentiment readings into a single score."""

    sentiment_by_source: Dict[str, float] = {}
    for reading in readings:
        prev = sentiment_by_source.get(reading.source, 0.0)
        sentiment_by_source[reading.source] = exponential_smoothing(prev, reading.score, alpha)
    if not sentiment_by_source:
        return 0.0
    return sum(sentiment_by_source.values()) / len(sentiment_by_source)


__all__ = ["SentimentReading", "aggregate_sentiment", "exponential_smoothing"]
