from sqlalchemy import Column, Integer, Float, Text, create_engine
from sqlalchemy.orm import DeclarativeBase
from crypto_trade_mvp.config import settings


class Base(DeclarativeBase):
    pass


class CandleRow(Base):
    __tablename__ = "candles"
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(Text, nullable=False)
    timeframe = Column(Text, nullable=False)
    timestamp = Column(Integer, nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)


class SignalRow(Base):
    __tablename__ = "signals"
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(Text, nullable=False)
    timeframe = Column(Text, nullable=False)
    timestamp = Column(Integer, nullable=False)
    strategy_name = Column(Text, nullable=False)
    signal = Column(Text, nullable=False)


class OrderRow(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(Integer, nullable=False)
    symbol = Column(Text, nullable=False)
    side = Column(Text, nullable=False)
    order_type = Column(Text, nullable=False)
    price = Column(Float, nullable=False)
    size = Column(Float, nullable=False)
    fee = Column(Float, nullable=False)
    slippage = Column(Float, nullable=False)
    status = Column(Text, nullable=False)


class PositionRow(Base):
    __tablename__ = "positions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(Text, nullable=False)
    size = Column(Float, nullable=False)
    avg_entry_price = Column(Float, nullable=False)
    unrealized_pnl = Column(Float, nullable=False)
    realized_pnl = Column(Float, nullable=False)
    updated_at = Column(Integer, nullable=False)


class PortfolioSnapshotRow(Base):
    __tablename__ = "portfolio_snapshots"
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(Integer, nullable=False)
    cash = Column(Float, nullable=False)
    equity = Column(Float, nullable=False)
    total_position_value = Column(Float, nullable=False)
    realized_pnl = Column(Float, nullable=False)
    unrealized_pnl = Column(Float, nullable=False)


def get_engine():
    db_url = settings.database_url.replace("sqlite:///", "sqlite:///")
    return create_engine(db_url)


def init_db():
    engine = get_engine()
    Base.metadata.create_all(engine)
