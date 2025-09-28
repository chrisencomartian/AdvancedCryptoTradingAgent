# Advanced Crypto Trading Agent

This project provides a modular blueprint for building an advanced crypto
trading agent that combines technical, fundamental, and sentiment analysis to
support high-frequency trading (HFT) workflows on Binance. The implementation
focuses on clarity, extensibility, and testability while keeping third-party
dependencies to a minimum.

## Features

- **Market Data Layer** – Fetches candlestick data from Binance REST endpoints
  with optional local caching for bursty HFT access patterns.
- **Technical Analysis** – Implements core indicators (moving averages, RSI,
  ATR) and fuses them into actionable signals.
- **Fundamental Analysis** – Normalizes and weights alternative datasets to
  capture longer-term crypto fundamentals such as network growth and
  developer activity.
- **Sentiment Analysis** – Aggregates social and news sentiment with exponential
  smoothing to dampen noise.
- **Strategy Engine** – Produces a composite signal targeting 3-5% moves every
  eight hours by balancing technical momentum with fundamental and sentiment
  confirmation.
- **Risk Management** – Enforces position sizing, cooldowns, and stop levels to
  protect against drawdowns.
- **Execution Layer** – Simulates Binance order routing with configurable
  slippage and latency assumptions; ready to be swapped with a live trading
  implementation.

## Getting Started

1. Create and activate a Python virtual environment (Python 3.11+ recommended).
2. Install dependencies if additional libraries are required for live trading.
3. Run the agent in dry-run mode:

   ```bash
   python main.py
   ```

   The example uses mock fundamental and sentiment data to demonstrate the
   pipeline end-to-end without live capital.

## Architecture Overview

```
main.py
└── AdvancedCryptoTradingAgent
    ├── Data Layer (BinanceClient)
    ├── Strategy Context
    │   ├── Technical Analysis
    │   ├── Fundamental Analysis
    │   └── Sentiment Analysis
    ├── Risk Manager
    └── Execution Engine
```

Each module is documented and can be extended with real-time data sources,
portfolio management logic, and connection to Binance's REST or WebSocket APIs.

## Disclaimer

The code is provided for educational and research purposes. High-frequency
crypto trading carries significant risk. Thoroughly test, monitor, and comply
with all exchange rules before deploying in production.
