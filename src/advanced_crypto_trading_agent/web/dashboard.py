"""Lightweight web dashboard for entry/exit recommendations."""

from __future__ import annotations

import json
import threading
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Callable, Dict, Iterable, List, Sequence

from ..analysis.sentiment import SentimentReading
from ..analysis.technical import average_true_range
from ..trader import AdvancedCryptoTradingAgent

FundamentalProvider = Callable[[str], Dict[str, Iterable[float]]]
SentimentProvider = Callable[[str], Iterable[SentimentReading]]


@dataclass(slots=True)
class Recommendation:
    """Represents a single trading recommendation."""

    symbol: str
    side: str
    entry_price: float
    exit_price: float
    probability: float
    statistics: Dict[str, float]
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_row(self) -> List[str]:
        """Return formatted strings for HTML table rows."""

        stats = ", ".join(f"{key}: {value:.2f}" for key, value in self.statistics.items())
        return [
            self.symbol,
            self.side,
            f"{self.entry_price:.2f}",
            f"{self.exit_price:.2f}",
            f"{self.probability * 100:.1f}%",
            stats,
            self.updated_at.strftime("%Y-%m-%d %H:%M:%S UTC"),
        ]


class RecommendationEngine:
    """Builds recommendations using the trading agent."""

    def __init__(
        self,
        agent: AdvancedCryptoTradingAgent,
        fundamental_provider: FundamentalProvider,
        sentiment_provider: SentimentProvider,
    ) -> None:
        self._agent = agent
        self._fundamental_provider = fundamental_provider
        self._sentiment_provider = sentiment_provider

    def build_recommendation(self, symbol: str) -> Recommendation:
        """Generate a recommendation for a trading symbol."""

        snapshot = self._agent.collect_market_data(symbol)
        context = self._agent.build_context(
            snapshot,
            self._fundamental_provider(symbol),
            self._sentiment_provider(symbol),
        )
        signal = context.composite_signal
        price = snapshot.prices[-1]
        side = "LONG" if signal >= 0 else "SHORT"

        probability = max(min(abs(signal), 1.0), 0.0)
        expected_return = probability * 0.05  # assume up to 5% move for strong signals
        if side == "LONG":
            entry_price = price
            exit_price = price * (1 + expected_return)
        else:
            entry_price = price
            exit_price = price * (1 - expected_return)

        try:
            atr_values = average_true_range(snapshot.highs, snapshot.lows, snapshot.closes)
            atr = atr_values[-1] if atr_values else float("nan")
        except ValueError:
            atr = float("nan")

        statistics = {
            "signal_strength": signal,
            "expected_return_pct": expected_return * 100,
        }
        if atr == atr:
            statistics["atr"] = atr

        return Recommendation(
            symbol=symbol,
            side=side,
            entry_price=entry_price,
            exit_price=exit_price,
            probability=probability,
            statistics=statistics,
        )

    def refresh(self, symbols: Sequence[str]) -> List[Recommendation]:
        """Return recommendations ordered by probability descending."""

        recommendations = [self.build_recommendation(symbol) for symbol in symbols]
        return sorted(recommendations, key=lambda item: item.probability, reverse=True)


class _DashboardHTTPRequestHandler(BaseHTTPRequestHandler):
    """Renders dashboard pages for the recommendation server."""

    server: "RecommendationDashboardServer"  # type: ignore[assignment]

    def do_GET(self) -> None:  # pragma: no cover - exercised via integration
        if self.path in {"/", "/index.html"}:
            self._handle_index()
        elif self.path == "/recommendations.json":
            self._handle_json()
        else:
            self.send_error(HTTPStatus.NOT_FOUND)

    def log_message(self, format: str, *args) -> None:  # pragma: no cover - noise in tests
        return

    def _handle_index(self) -> None:
        html = self.server.dashboard.render_html()
        encoded = html.encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _handle_json(self) -> None:
        payload = []
        for rec in self.server.dashboard.recommendations:
            item = asdict(rec)
            item["updated_at"] = rec.updated_at.isoformat()
            payload.append(item)
        encoded = json.dumps(payload).encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


class RecommendationDashboardServer(ThreadingHTTPServer):
    """Threading HTTP server that exposes dashboard state."""

    def __init__(self, host: str, port: int, dashboard: "RecommendationDashboard") -> None:
        super().__init__((host, port), _DashboardHTTPRequestHandler)
        self.dashboard = dashboard


class RecommendationDashboard:
    """Maintains refreshed recommendations and serves them via HTTP."""

    def __init__(
        self,
        engine: RecommendationEngine,
        symbols: Sequence[str],
        update_interval: int = 300,
    ) -> None:
        self._engine = engine
        self._symbols = list(symbols)
        self._interval = update_interval
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._recommendations: List[Recommendation] = []
        self._thread = threading.Thread(target=self._refresh_loop, daemon=True)
        self._server: RecommendationDashboardServer | None = None

    @property
    def recommendations(self) -> List[Recommendation]:
        with self._lock:
            return list(self._recommendations)

    def render_html(self) -> str:
        rows = "\n".join(
            "<tr>" + "".join(f"<td>{cell}</td>" for cell in rec.to_row()) + "</tr>"
            for rec in self.recommendations
        )
        return f"""
<!DOCTYPE html>
<html lang=\"en\">
<head>
    <meta charset=\"utf-8\" />
    <title>HFT Entry & Exit Recommendations</title>
    <meta http-equiv=\"refresh\" content=\"300\" />
    <style>
        body {{ font-family: Arial, sans-serif; margin: 2rem; background: #10151c; color: #f5f7fa; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 1.5rem; }}
        th, td {{ padding: 0.75rem; border-bottom: 1px solid #2a3a4b; text-align: left; }}
        th {{ background: #18202b; }}
        tr:nth-child(even) {{ background: #141b24; }}
    </style>
</head>
<body>
    <h1>Entry & Exit Recommendations</h1>
    <p>Recommendations refresh automatically every 5 minutes. Sorted by highest probability.</p>
    <table>
        <thead>
            <tr>
                <th>Symbol</th>
                <th>Bias</th>
                <th>Entry</th>
                <th>Exit</th>
                <th>Probability</th>
                <th>Statistics</th>
                <th>Last Updated</th>
            </tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
    </table>
</body>
</html>
"""

    def start(self, host: str = "0.0.0.0", port: int = 8000) -> None:
        if not self._thread.is_alive():
            self._thread.start()
        self._server = RecommendationDashboardServer(host, port, self)
        try:
            self._server.serve_forever()
        finally:
            self.stop()

    def stop(self) -> None:
        self._stop.set()
        if self._server:
            self._server.shutdown()
            self._server.server_close()
        if self._thread.is_alive():
            self._thread.join(timeout=1.0)

    def _refresh_loop(self) -> None:
        while not self._stop.is_set():
            recommendations = self._engine.refresh(self._symbols)
            with self._lock:
                self._recommendations = recommendations
            self._stop.wait(self._interval)


def run_dashboard(
    agent: AdvancedCryptoTradingAgent,
    fundamental_provider: FundamentalProvider,
    sentiment_provider: SentimentProvider,
    symbols: Sequence[str],
    interval_seconds: int = 300,
    host: str = "0.0.0.0",
    port: int = 8000,
) -> None:
    """Convenience helper to launch the dashboard."""

    engine = RecommendationEngine(agent, fundamental_provider, sentiment_provider)
    dashboard = RecommendationDashboard(engine, symbols, update_interval=interval_seconds)
    dashboard.start(host, port)


__all__ = [
    "Recommendation",
    "RecommendationEngine",
    "RecommendationDashboard",
    "run_dashboard",
]


if __name__ == "__main__":  # pragma: no cover - manual integration entry point
    import random

    from ..config import DEFAULT_CONFIG

    config = DEFAULT_CONFIG
    agent = AdvancedCryptoTradingAgent(config)

    def _demo_fundamentals(symbol: str) -> Dict[str, List[float]]:
        random.seed(symbol)
        return {
            "network_growth": [random.uniform(0.8, 1.2) for _ in range(30)],
            "exchange_inflows": [random.uniform(-1.0, 1.0) for _ in range(30)],
            "developer_activity": [random.uniform(0.0, 2.0) for _ in range(30)],
        }

    def _demo_sentiment(symbol: str) -> List[SentimentReading]:
        random.seed(f"sentiment-{symbol}")
        return [SentimentReading(source="demo", score=random.uniform(-1, 1))]

    run_dashboard(
        agent,
        _demo_fundamentals,
        _demo_sentiment,
        config.data.trading_pairs,
    )
