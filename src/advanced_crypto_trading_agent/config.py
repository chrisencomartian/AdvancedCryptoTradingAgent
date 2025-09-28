"""Configuration models for the Advanced Crypto Trading Agent."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta
from pathlib import Path
from typing import Dict, List, Optional


@dataclass(slots=True)
class BinanceCredentials:
    """Credentials and preferences for accessing the Binance API."""

    api_key: str = ""
    api_secret: str = ""
    testnet: bool = True


@dataclass(slots=True)
class DataConfig:
    """Configuration for market and alternative data collection."""

    trading_pairs: List[str] = field(default_factory=lambda: ["BTCUSDT", "ETHUSDT"])
    klines_interval: str = "1m"
    history_window: int = 500
    cache_dir: Path = Path(".cache")


@dataclass(slots=True)
class TechnicalConfig:
    """Settings for technical indicator calculations."""

    fast_ma: int = 9
    slow_ma: int = 26
    rsi_period: int = 14
    atr_period: int = 14


@dataclass(slots=True)
class FundamentalConfig:
    """Settings for the fundamental score builder."""

    metrics_weights: Dict[str, float] = field(
        default_factory=lambda: {
            "network_growth": 0.4,
            "exchange_inflows": -0.3,
            "developer_activity": 0.3,
        }
    )
    normalize_window: int = 30


@dataclass(slots=True)
class SentimentConfig:
    """Configuration for sentiment aggregation."""

    sources: List[str] = field(
        default_factory=lambda: [
            "twitter",
            "news",
            "onchain_forums",
        ]
    )
    smoothing: float = 0.2


@dataclass(slots=True)
class RiskConfig:
    """Risk management settings."""

    max_position_size: float = 0.15
    max_leverage: int = 5
    max_drawdown: float = 0.03
    take_profit: float = 0.05
    stop_loss: float = 0.02
    cooldown: timedelta = timedelta(minutes=5)


@dataclass(slots=True)
class ExecutionConfig:
    """Configuration for execution and slippage assumptions."""

    order_type: str = "limit"
    max_slippage: float = 0.0005
    order_timeout: timedelta = timedelta(seconds=10)


@dataclass(slots=True)
class AgentConfig:
    """Bundle of configuration values for the trading agent."""

    binance: BinanceCredentials = field(default_factory=BinanceCredentials)
    data: DataConfig = field(default_factory=DataConfig)
    technical: TechnicalConfig = field(default_factory=TechnicalConfig)
    fundamental: FundamentalConfig = field(default_factory=FundamentalConfig)
    sentiment: SentimentConfig = field(default_factory=SentimentConfig)
    risk: RiskConfig = field(default_factory=RiskConfig)
    execution: ExecutionConfig = field(default_factory=ExecutionConfig)
    dry_run: bool = True


DEFAULT_CONFIG = AgentConfig()
