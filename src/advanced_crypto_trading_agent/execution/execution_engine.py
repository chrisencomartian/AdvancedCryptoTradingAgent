"""Execution engine for routing orders to Binance."""

from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import datetime
from typing import Dict

from ..config import ExecutionConfig
from ..utils.logger import get_logger


@dataclass(slots=True)
class Order:
    """Represents an order to be sent to an exchange."""

    symbol: str
    side: str
    quantity: float
    price: float
    order_type: str
    timestamp: datetime


@dataclass(slots=True)
class ExecutionReport:
    """Represents the result of an order submission."""

    order: Order
    status: str
    executed_quantity: float
    avg_price: float


class ExecutionEngine:
    """Simplified execution engine with simulated fills."""

    def __init__(self, config: ExecutionConfig, dry_run: bool = True) -> None:
        self._config = config
        self._dry_run = dry_run
        self._logger = get_logger(self.__class__.__name__)

    def send_order(self, symbol: str, side: str, quantity: float, price: float) -> ExecutionReport:
        """Send an order and return a simulated execution report."""

        order = Order(
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=price,
            order_type=self._config.order_type,
            timestamp=datetime.utcnow(),
        )
        if self._dry_run:
            executed_qty = quantity * random.uniform(0.9, 1.0)
            slippage = price * random.uniform(-self._config.max_slippage, self._config.max_slippage)
            avg_price = price + slippage
            status = "FILLED" if executed_qty == quantity else "PARTIALLY_FILLED"
        else:  # pragma: no cover - requires live credentials
            self._logger.info("Live trading not implemented; order would be sent here.")
            executed_qty = 0.0
            avg_price = price
            status = "NEW"
        report = ExecutionReport(order=order, status=status, executed_quantity=executed_qty, avg_price=avg_price)
        self._logger.info(
            "Order %s %s %s @ %.2f status=%s qty=%.4f avg_price=%.2f",
            order.side,
            order.quantity,
            order.symbol,
            order.price,
            status,
            executed_qty,
            avg_price,
        )
        return report


__all__ = ["ExecutionEngine", "ExecutionReport", "Order"]
