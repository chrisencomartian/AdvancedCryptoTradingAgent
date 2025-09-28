"""Main trading agent orchestrating data, analysis, and execution."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Iterable, List

from .analysis.sentiment import SentimentReading
from .config import AgentConfig
from .data.binance_client import BinanceClient
from .execution.execution_engine import ExecutionEngine
from .risk.risk_manager import RiskManager
from .strategy.hft_strategy import StrategyContext, build_strategy_context
from .utils.logger import get_logger


@dataclass(slots=True)
class MarketSnapshot:
    """Represents the latest market data used for decision making."""

    symbol: str
    prices: List[float]
    highs: List[float]
    lows: List[float]
    closes: List[float]


class AdvancedCryptoTradingAgent:
    """High level orchestrator for the trading system."""

    def __init__(self, config: AgentConfig) -> None:
        self._config = config
        self._logger = get_logger(self.__class__.__name__)
        self._client = BinanceClient(config)
        self._risk = RiskManager(config.risk)
        self._execution = ExecutionEngine(config.execution, dry_run=config.dry_run)

    def collect_market_data(self, symbol: str) -> MarketSnapshot:
        """Collect market data for a symbol from Binance."""

        klines = self._client.get_klines(symbol)
        prices = [kline["close"] for kline in klines]
        highs = [kline["high"] for kline in klines]
        lows = [kline["low"] for kline in klines]
        closes = [kline["close"] for kline in klines]
        return MarketSnapshot(symbol=symbol, prices=prices, highs=highs, lows=lows, closes=closes)

    def build_context(
        self,
        snapshot: MarketSnapshot,
        fundamentals: Dict[str, Iterable[float]],
        sentiment_readings: Iterable[SentimentReading],
    ) -> StrategyContext:
        """Build the strategy context for the latest market snapshot."""

        context = build_strategy_context(
            prices=snapshot.prices,
            technical_config=self._config.technical,
            fundamentals=fundamentals,
            fundamental_config=self._config.fundamental,
            sentiment_readings=sentiment_readings,
            sentiment_config=self._config.sentiment,
        )
        return context

    def trade(self, symbol: str, fundamentals: Dict[str, Iterable[float]], sentiment_readings: Iterable[SentimentReading]) -> None:
        """Execute one full decision cycle for a trading symbol."""

        snapshot = self.collect_market_data(symbol)
        context = self.build_context(snapshot, fundamentals, sentiment_readings)
        signal = context.composite_signal
        self._logger.info("Composite signal for %s: %.3f", symbol, signal)

        if not self._risk.can_trade():
            self._logger.info("Cooldown active, skipping trade for %s", symbol)
            return

        equity = 1.0  # Placeholder for total capital tracking
        position_size = self._risk.position_size(equity, signal)
        if position_size == 0.0:
            self._logger.info("Signal too weak, not trading %s", symbol)
            return

        side = "BUY" if signal > 0 else "SELL"
        price = snapshot.prices[-1]
        report = self._execution.send_order(symbol, side, position_size / price, price)
        self._risk.record_trade(size=report.executed_quantity * price, price=report.avg_price)
        stops = self._risk.stop_levels(report.avg_price)
        self._logger.info(
            "Risk controls for %s: stop_loss=%.2f take_profit=%.2f",
            symbol,
            stops["stop_loss"],
            stops["take_profit"],
        )


__all__ = ["AdvancedCryptoTradingAgent", "MarketSnapshot"]
