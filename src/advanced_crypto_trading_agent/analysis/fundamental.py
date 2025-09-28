"""Fundamental analysis signal generation."""

from __future__ import annotations

from dataclasses import dataclass
from statistics import fmean
from typing import Dict, Iterable


@dataclass(slots=True)
class FundamentalMetric:
    """Represents a single fundamental metric value."""

    name: str
    value: float
    weight: float


def normalize_metric(values: Iterable[float]) -> float:
    """Normalize a metric value into the range [-1, 1]."""

    values = list(values)
    if not values:
        return 0.0
    minimum = min(values)
    maximum = max(values)
    if maximum == minimum:
        return 0.0
    latest = values[-1]
    normalized = 2 * ((latest - minimum) / (maximum - minimum)) - 1
    return normalized


def fundamental_score(history: Dict[str, Iterable[float]], weights: Dict[str, float]) -> float:
    """Generate a weighted score using normalized metrics."""

    metrics: Dict[str, float] = {}
    for name, series in history.items():
        normalized = normalize_metric(series)
        weight = weights.get(name, 0.0)
        metrics[name] = normalized * weight
    return sum(metrics.values())


def build_metric_snapshot(raw_metrics: Dict[str, float], weights: Dict[str, float]) -> Dict[str, FundamentalMetric]:
    """Create a snapshot of weighted metrics for explainability."""

    snapshot = {}
    for name, value in raw_metrics.items():
        weight = weights.get(name, 0.0)
        snapshot[name] = FundamentalMetric(name=name, value=value, weight=weight)
    return snapshot


__all__ = [
    "FundamentalMetric",
    "normalize_metric",
    "fundamental_score",
    "build_metric_snapshot",
]
