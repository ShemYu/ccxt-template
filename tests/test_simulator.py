import pytest
from crypto_trade_mvp.execution.simulator import PaperBroker


def test_initial_state():
    broker = PaperBroker(symbol="BTC/JPY", initial_capital=100000)
    state = broker.get_portfolio_state()
    assert state.cash == 100000
    assert state.equity == 100000
    assert not broker.position.is_open()


def test_buy_opens_position():
    broker = PaperBroker(symbol="BTC/JPY", initial_capital=100000)
    order = broker.place_order("buy", price=5000000.0)
    assert order is not None
    assert broker.position.is_open()
    assert broker.cash == 0.0


def test_sell_closes_position():
    broker = PaperBroker(symbol="BTC/JPY", initial_capital=100000)
    broker.place_order("buy", price=5000000.0)
    order = broker.place_order("sell", price=5100000.0)
    assert order is not None
    assert not broker.position.is_open()
    assert broker.cash > 0


def test_duplicate_buy_ignored():
    broker = PaperBroker(symbol="BTC/JPY", initial_capital=100000)
    broker.place_order("buy", price=5000000.0)
    order = broker.place_order("buy", price=5000000.0)
    assert order is None


def test_sell_without_position_ignored():
    broker = PaperBroker(symbol="BTC/JPY", initial_capital=100000)
    order = broker.place_order("sell", price=5000000.0)
    assert order is None


def test_unrealized_pnl_updates():
    broker = PaperBroker(symbol="BTC/JPY", initial_capital=100000)
    broker.place_order("buy", price=5000000.0)
    broker.update_unrealized_pnl(current_price=5100000.0)
    assert broker.position.unrealized_pnl > 0
