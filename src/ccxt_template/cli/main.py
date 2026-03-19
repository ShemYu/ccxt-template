import asyncio
import time
import typer
import pandas as pd
from ccxt_template.config import settings
from ccxt_template.logger import logger
from ccxt_template.data.schema import init_db
from ccxt_template.data.fetcher import DataFetcher
from ccxt_template.data.repository import Repository
from ccxt_template.exchange.bitflyer_adapter import BitflyerAdapter
from ccxt_template.exchange.realtime import stream
from ccxt_template.models.candle import Candle
from ccxt_template.strategy.sma_cross import SMACrossStrategy
from ccxt_template.execution.simulator import PaperBroker
from ccxt_template.portfolio.manager import PortfolioManager
from ccxt_template.backtest.engine import BacktestEngine
from ccxt_template.models.signal import SignalType

app = typer.Typer(help="ccxt-template CLI")

STRATEGIES = {
    "sma_cross": SMACrossStrategy(),
}


@app.command()
def init_db_cmd():
    """Initialize the SQLite database."""
    init_db()
    logger.info("Database initialized.")


@app.command()
def fetch_data(
    symbol: str = typer.Option(settings.default_symbol, help="Trading pair"),
    timeframe: str = typer.Option(settings.default_timeframe, help="Candle timeframe"),
    limit: int = typer.Option(300, help="Number of candles to fetch"),
):
    """Fetch OHLCV candles and store to SQLite."""
    init_db()
    adapter = BitflyerAdapter()
    fetcher = DataFetcher(adapter)
    repo = Repository()

    candles, df = fetcher.fetch(symbol, timeframe, limit)
    repo.save_candles(candles)
    typer.echo(df.tail(10).to_string(index=False))
    typer.echo(f"\nStored {len(candles)} candles.")


@app.command()
def run_strategy(
    symbol: str = typer.Option(settings.default_symbol),
    timeframe: str = typer.Option(settings.default_timeframe),
    strategy: str = typer.Option("sma_cross"),
    limit: int = typer.Option(300),
):
    """Run strategy on stored candles and generate a signal."""
    init_db()
    repo = Repository()
    rows = repo.get_candles(symbol, timeframe, limit)
    if not rows:
        typer.echo("No candles found. Run fetch-data first.")
        raise typer.Exit(1)

    df = pd.DataFrame(
        [(r.timestamp, r.open, r.high, r.low, r.close, r.volume) for r in rows],
        columns=["timestamp", "open", "high", "low", "close", "volume"],
    ).sort_values("timestamp").reset_index(drop=True)

    strat = STRATEGIES.get(strategy)
    if not strat:
        typer.echo(f"Unknown strategy: {strategy}")
        raise typer.Exit(1)

    signal = strat.generate_signal(df)
    typer.echo(f"Signal: {signal.value}")


@app.command()
def backtest(
    symbol: str = typer.Option(settings.default_symbol),
    timeframe: str = typer.Option(settings.default_timeframe),
    strategy: str = typer.Option("sma_cross"),
    limit: int = typer.Option(300),
):
    """Backtest strategy on stored candles."""
    init_db()
    repo = Repository()
    rows = repo.get_candles(symbol, timeframe, limit)
    if not rows:
        typer.echo("No candles found. Run fetch-data first.")
        raise typer.Exit(1)

    df = pd.DataFrame(
        [(r.timestamp, r.open, r.high, r.low, r.close, r.volume) for r in rows],
        columns=["timestamp", "open", "high", "low", "close", "volume"],
    ).sort_values("timestamp").reset_index(drop=True)

    strat = STRATEGIES.get(strategy)
    if not strat:
        typer.echo(f"Unknown strategy: {strategy}")
        raise typer.Exit(1)

    engine = BacktestEngine(strategy=strat, symbol=symbol)
    report = engine.run(df)

    typer.echo("\n--- Backtest Report ---")
    for k, v in report.items():
        typer.echo(f"  {k}: {v}")


@app.command()
def paper_trade(
    symbol: str = typer.Option(settings.default_symbol),
    timeframe: str = typer.Option(settings.default_timeframe),
):
    """Run paper trading loop driven by bitFlyer Realtime API."""
    from ccxt_template.data.schema import init_db as _init_db
    _init_db()

    adapter = BitflyerAdapter()
    repo = Repository()
    broker = PaperBroker(symbol=symbol)
    pm = PortfolioManager(broker=broker, repo=repo)
    strat = SMACrossStrategy()
    candle_window: list[Candle] = []

    def on_candle_closed(candle: Candle) -> None:
        repo.save_candles([candle])
        candle_window.append(candle)
        if len(candle_window) > 300:
            candle_window.pop(0)

        if len(candle_window) < 20:
            logger.info(f"Warming up: {len(candle_window)}/20 candles")
            return

        df = pd.DataFrame([
            (c.timestamp, c.open, c.high, c.low, c.close, c.volume)
            for c in candle_window
        ], columns=["timestamp", "open", "high", "low", "close", "volume"])

        signal = strat.generate_signal(df)
        current_price = candle_window[-1].close
        broker.update_unrealized_pnl(current_price)

        if signal == SignalType.BUY:
            order = broker.place_order("buy", current_price)
            if order:
                repo.save_order(order)
        elif signal == SignalType.SELL:
            order = broker.place_order("sell", current_price)
            if order:
                repo.save_order(order)

        pm.snapshot()
        typer.echo(f"[{candle_window[-1].timestamp}] signal={signal.value} price={current_price}")

    typer.echo(f"Starting realtime paper trading for {symbol} [{timeframe}]")
    asyncio.run(stream(
        exchange=adapter._exchange,
        symbol=symbol,
        timeframe=timeframe,
        on_candle_closed=on_candle_closed,
        history_candles=25,
    ))


@app.command()
def init_db():
    """Initialize the SQLite database schema."""
    from ccxt_template.data.schema import init_db as _init_db
    _init_db()
    typer.echo("Database initialized.")


if __name__ == "__main__":
    app()
