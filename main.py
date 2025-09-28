"""Entry point for running the Advanced Crypto Trading Agent."""

from __future__ import annotations

import random
from typing import Dict, Iterable, List

from src.advanced_crypto_trading_agent.analysis.sentiment import SentimentReading
from src.advanced_crypto_trading_agent.config import AgentConfig, DEFAULT_CONFIG
from src.advanced_crypto_trading_agent.trader import AdvancedCryptoTradingAgent


def generate_mock_fundamentals(symbol: str) -> Dict[str, List[float]]:
    """Generate mock fundamental data for demonstration purposes."""

    random.seed(symbol)
    return {
        "network_growth": [random.uniform(0.8, 1.2) for _ in range(30)],
        "exchange_inflows": [random.uniform(-1.0, 1.0) for _ in range(30)],
        "developer_activity": [random.uniform(0.0, 2.0) for _ in range(30)],
    }


def generate_mock_sentiment(sources: Iterable[str]) -> List[SentimentReading]:
    """Generate mock sentiment readings."""

    return [SentimentReading(source=source, score=random.uniform(-1, 1)) for source in sources]


def run_agent(config: AgentConfig = DEFAULT_CONFIG) -> None:
    """Run the trading agent for the configured trading pairs."""

    agent = AdvancedCryptoTradingAgent(config)
    for symbol in config.data.trading_pairs:
        fundamentals = generate_mock_fundamentals(symbol)
        sentiment = generate_mock_sentiment(config.sentiment.sources)
        agent.trade(symbol, fundamentals, sentiment)


if __name__ == "__main__":
    run_agent()
