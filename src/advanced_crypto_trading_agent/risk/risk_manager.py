"""Risk management utilities for the trading agent."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict

from ..config import RiskConfig
from ..utils.logger import get_logger


@dataclass(slots=True)
class PositionState:
    """Represents the current position state."""

    size: float = 0.0
    entry_price: float = 0.0
    last_trade_time: datetime = field(default_factory=datetime.utcnow)


class RiskManager:
    """Enforces position sizing, leverage, and drawdown constraints."""

    def __init__(self, config: RiskConfig) -> None:
        self._config = config
        self._position = PositionState()
        self._peak_equity = 1.0
        self._logger = get_logger(self.__class__.__name__)

    def update_equity(self, equity: float) -> None:
        """Update the tracked equity and drawdown state."""

        if equity > self._peak_equity:
            self._peak_equity = equity
        drawdown = 1 - equity / self._peak_equity
        if drawdown > self._config.max_drawdown:
            self._logger.warning("Drawdown exceeded threshold: %.2f%%", drawdown * 100)

    def can_trade(self, now: datetime | None = None) -> bool:
        """Check whether new trades are allowed based on cooldown."""

        now = now or datetime.utcnow()
        elapsed = now - self._position.last_trade_time
        return elapsed >= self._config.cooldown

    def position_size(self, equity: float, signal_strength: float) -> float:
        """Determine position size based on signal strength and constraints."""

        size = min(abs(signal_strength), 1.0) * self._config.max_position_size * equity
        return max(min(size, equity * self._config.max_position_size), 0.0)

    def record_trade(self, size: float, price: float, now: datetime | None = None) -> None:
        """Store last trade information for cooldown enforcement."""

        now = now or datetime.utcnow()
        self._position.size = size
        self._position.entry_price = price
        self._position.last_trade_time = now

    def stop_levels(self, entry_price: float) -> Dict[str, float]:
        """Calculate stop loss and take profit levels."""

        return {
            "take_profit": entry_price * (1 + self._config.take_profit),
            "stop_loss": entry_price * (1 - self._config.stop_loss),
        }


__all__ = ["RiskManager", "PositionState"]
