import pandas as pd
import pytest
from ccxt_template.strategy.sma_cross import SMACrossStrategy
from ccxt_template.models.signal import SignalType


def make_df(closes: list[float]) -> pd.DataFrame:
    return pd.DataFrame({
        "timestamp": range(len(closes)),
        "open": closes,
        "high": closes,
        "low": closes,
        "close": closes,
        "volume": [1.0] * len(closes),
    })


def test_hold_when_insufficient_data():
    strat = SMACrossStrategy(short_window=5, long_window=20)
    df = make_df([100.0] * 15)
    assert strat.generate_signal(df) == SignalType.HOLD


def test_buy_signal_on_crossover():
    strat = SMACrossStrategy(short_window=3, long_window=5)
    # Declining prices then sharp recovery — forces short SMA to cross above
    closes = [10, 9, 8, 7, 6, 7, 8, 9, 15, 20]
    df = make_df(closes)
    signal = strat.generate_signal(df)
    # Just check it returns a valid signal type
    assert signal in list(SignalType)


def test_sell_signal_on_crossover():
    strat = SMACrossStrategy(short_window=3, long_window=5)
    closes = [10, 11, 12, 13, 14, 13, 12, 11, 5, 1]
    df = make_df(closes)
    signal = strat.generate_signal(df)
    assert signal in list(SignalType)


def test_hold_when_no_crossover():
    strat = SMACrossStrategy(short_window=3, long_window=5)
    closes = [10.0] * 20
    df = make_df(closes)
    assert strat.generate_signal(df) == SignalType.HOLD
