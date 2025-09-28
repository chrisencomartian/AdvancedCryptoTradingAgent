from advanced_crypto_trading_agent.analysis.technical import (
    average_true_range,
    moving_average,
    relative_strength_index,
)


def test_moving_average_basic():
    prices = [1, 2, 3, 4, 5]
    ma = moving_average(prices, 3)
    assert ma[-1] == 4


def test_rsi_bounds():
    prices = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    rsi = relative_strength_index(prices, 14)
    assert 0 <= rsi[-1] <= 100


def test_average_true_range_len_match():
    highs = [2, 3, 4]
    lows = [1, 2, 3]
    closes = [1.5, 2.5, 3.5]
    atr = average_true_range(highs, lows, closes, 2)
    assert len(atr) == len(highs)
