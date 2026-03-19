import pandas as pd
import pytest
from crypto_trade_mvp.backtest.engine import BacktestEngine
from crypto_trade_mvp.strategy.sma_cross import SMACrossStrategy


def make_df(closes: list[float]) -> pd.DataFrame:
    return pd.DataFrame({
        "timestamp": range(len(closes)),
        "open": closes,
        "high": closes,
        "low": closes,
        "close": closes,
        "volume": [1.0] * len(closes),
    })


def test_backtest_returns_report_keys():
    strat = SMACrossStrategy(short_window=3, long_window=5)
    engine = BacktestEngine(strategy=strat, symbol="BTC/JPY", initial_capital=100000)
    closes = [100, 101, 102, 103, 104, 110, 115, 120, 100, 90, 80]
    report = engine.run(make_df(closes))

    assert "initial_capital" in report
    assert "final_equity" in report
    assert "total_return_pct" in report
    assert "total_trades" in report


def test_backtest_no_trades_on_flat_data():
    strat = SMACrossStrategy(short_window=3, long_window=5)
    engine = BacktestEngine(strategy=strat, symbol="BTC/JPY", initial_capital=100000)
    closes = [100.0] * 30
    report = engine.run(make_df(closes))
    assert report["total_trades"] == 0
    assert report["final_equity"] == 100000.0
