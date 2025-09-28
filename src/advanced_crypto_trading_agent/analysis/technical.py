"""Technical analysis utilities for high-frequency trading decisions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List


@dataclass(slots=True)
class IndicatorResult:
    """Container for indicator outputs."""

    value: float
    signal: float


def moving_average(values: Iterable[float], period: int) -> List[float]:
    """Calculate a simple moving average."""

    values = list(values)
    if period <= 0:
        raise ValueError("Period must be positive")
    averages: List[float] = []
    for index in range(len(values)):
        if index + 1 < period:
            averages.append(float("nan"))
        else:
            window = values[index + 1 - period : index + 1]
            averages.append(sum(window) / period)
    return averages


def relative_strength_index(values: Iterable[float], period: int = 14) -> List[float]:
    """Compute the Relative Strength Index (RSI)."""

    values = list(values)
    if period <= 0:
        raise ValueError("Period must be positive")
    if len(values) < period + 1:
        raise ValueError("Not enough data for RSI calculation")

    gains: List[float] = [0.0]
    losses: List[float] = [0.0]
    for idx in range(1, len(values)):
        delta = values[idx] - values[idx - 1]
        gains.append(max(delta, 0))
        losses.append(abs(min(delta, 0)))

    avg_gain = sum(gains[1 : period + 1]) / period
    avg_loss = sum(losses[1 : period + 1]) / period
    rsi_values: List[float] = [float("nan")] * len(values)

    def compute_rsi(avg_gain: float, avg_loss: float) -> float:
        if avg_loss == 0:
            return 100.0
        rs = avg_gain / avg_loss
        return 100.0 - (100.0 / (1.0 + rs))

    rsi_values[period] = compute_rsi(avg_gain, avg_loss)

    for idx in range(period + 1, len(values)):
        avg_gain = (avg_gain * (period - 1) + gains[idx]) / period
        avg_loss = (avg_loss * (period - 1) + losses[idx]) / period
        rsi_values[idx] = compute_rsi(avg_gain, avg_loss)

    return rsi_values


def average_true_range(highs: Iterable[float], lows: Iterable[float], closes: Iterable[float], period: int = 14) -> List[float]:
    """Calculate the Average True Range (ATR)."""

    highs = list(highs)
    lows = list(lows)
    closes = list(closes)
    if not (len(highs) == len(lows) == len(closes)):
        raise ValueError("Input arrays must have the same length")
    if period <= 0:
        raise ValueError("Period must be positive")

    true_ranges: List[float] = [highs[0] - lows[0]]
    for idx in range(1, len(highs)):
        tr = max(
            highs[idx] - lows[idx],
            abs(highs[idx] - closes[idx - 1]),
            abs(lows[idx] - closes[idx - 1]),
        )
        true_ranges.append(tr)

    atr_values: List[float] = [float("nan")] * len(highs)
    atr = sum(true_ranges[:period]) / period
    atr_values[period - 1] = atr

    for idx in range(period, len(true_ranges)):
        atr = (atr * (period - 1) + true_ranges[idx]) / period
        atr_values[idx] = atr

    return atr_values


def generate_technical_signal(prices: Iterable[float], config) -> IndicatorResult:
    """Combine multiple indicators into a single signal score."""

    prices = list(prices)
    fast_ma = moving_average(prices, config.fast_ma)
    slow_ma = moving_average(prices, config.slow_ma)
    rsi = relative_strength_index(prices, config.rsi_period)

    latest_idx = len(prices) - 1
    fast = fast_ma[latest_idx]
    slow = slow_ma[latest_idx]
    rsi_value = rsi[latest_idx]

    signal = 0.0
    if fast > slow:
        signal += 0.4
    else:
        signal -= 0.4

    if rsi_value != rsi_value:  # NaN check
        rsi_component = 0.0
    elif rsi_value > 70:
        rsi_component = -0.3
    elif rsi_value < 30:
        rsi_component = 0.3
    else:
        rsi_component = 0.0
    signal += rsi_component

    return IndicatorResult(value=fast - slow, signal=signal)


__all__ = [
    "IndicatorResult",
    "moving_average",
    "relative_strength_index",
    "average_true_range",
    "generate_technical_signal",
]
