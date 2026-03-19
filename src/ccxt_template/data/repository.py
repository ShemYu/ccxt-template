from sqlalchemy.orm import Session
from ccxt_template.data.schema import (
    CandleRow, SignalRow, OrderRow, PositionRow, PortfolioSnapshotRow, get_engine
)
from ccxt_template.models.candle import Candle
from ccxt_template.models.signal import Signal
from ccxt_template.models.order import Order
from ccxt_template.models.position import Position
from ccxt_template.models.portfolio import PortfolioSnapshot


class Repository:
    def __init__(self):
        self._engine = get_engine()

    def save_candles(self, candles: list[Candle]) -> None:
        with Session(self._engine) as session:
            rows = [
                CandleRow(
                    symbol=c.symbol, timeframe=c.timeframe, timestamp=c.timestamp,
                    open=c.open, high=c.high, low=c.low, close=c.close, volume=c.volume,
                )
                for c in candles
            ]
            session.add_all(rows)
            session.commit()

    def save_signal(self, signal: Signal) -> None:
        with Session(self._engine) as session:
            row = SignalRow(
                symbol=signal.symbol, timeframe=signal.timeframe,
                timestamp=signal.timestamp, strategy_name=signal.strategy_name,
                signal=signal.signal.value,
            )
            session.add(row)
            session.commit()

    def save_order(self, order: Order) -> None:
        with Session(self._engine) as session:
            row = OrderRow(
                timestamp=order.timestamp, symbol=order.symbol,
                side=order.side.value, order_type=order.order_type,
                price=order.price, size=order.size,
                fee=order.fee, slippage=order.slippage, status=order.status.value,
            )
            session.add(row)
            session.commit()

    def save_position(self, position: Position) -> None:
        with Session(self._engine) as session:
            row = PositionRow(
                symbol=position.symbol, size=position.size,
                avg_entry_price=position.avg_entry_price,
                unrealized_pnl=position.unrealized_pnl,
                realized_pnl=position.realized_pnl,
                updated_at=position.updated_at,
            )
            session.add(row)
            session.commit()

    def save_portfolio_snapshot(self, snapshot: PortfolioSnapshot) -> None:
        with Session(self._engine) as session:
            row = PortfolioSnapshotRow(
                timestamp=snapshot.timestamp, cash=snapshot.cash,
                equity=snapshot.equity, total_position_value=snapshot.total_position_value,
                realized_pnl=snapshot.realized_pnl, unrealized_pnl=snapshot.unrealized_pnl,
            )
            session.add(row)
            session.commit()

    def get_candles(self, symbol: str, timeframe: str, limit: int) -> list[CandleRow]:
        with Session(self._engine) as session:
            return (
                session.query(CandleRow)
                .filter_by(symbol=symbol, timeframe=timeframe)
                .order_by(CandleRow.timestamp.desc())
                .limit(limit)
                .all()
            )
