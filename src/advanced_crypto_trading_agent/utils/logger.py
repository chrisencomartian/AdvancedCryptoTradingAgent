"""Central logging utilities for the trading agent."""

from __future__ import annotations

import logging
from logging import Logger
from typing import Optional


def get_logger(name: str, level: int = logging.INFO) -> Logger:
    """Return a configured logger instance.

    Parameters
    ----------
    name:
        The name for the logger.
    level:
        Logging level to use.
    """

    logger = logging.getLogger(name)
    if not logger.handlers:
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(level)
    logger.propagate = False
    return logger
