import time
import typer
import pandas as pd
from crypto_trade_mvp.config import settings
from crypto_trade_mvp.logger import logger
from crypto_trade_mvp.data.schema import init_db
from crypto_trade_mvp.data.fetcher import DataFetcher
from crypto_trade_mvp.data.repository import Repository
from crypto_trade_mvp.exchange.bitflyer_adapter import BitflyerAdapter
from crypto_trade_mvp.strategy.sma_cross import SMACrossStrategy
from crypto_trade_mvp.execution.simulator import PaperBroker
from crypto_trade_mvp.portfolio.manager import PortfolioManager
from crypto_trade_mvp.backtest.engine import BacktestEngine
from crypto_trade_mvp.models.signal import SignalType

app = typer.Typer(help="crypto-trade-mvp CLI")

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
    interval: int = typer.Option(60, help="Poll interval in seconds"),
    limit: int = typer.Option(300),
):
    """Run paper trading loop, polling on an interval."""
    init_db()
    adapter = BitflyerAdapter()
    fetcher = DataFetcher(adapter)
    repo = Repository()
    broker = PaperBroker(symbol=symbol)
    pm = PortfolioManager(broker=broker, repo=repo)
    strat = SMACrossStrategy()

    typer.echo(f"Starting paper trading for {symbol} [{timeframe}] every {interval}s")

    while True:
        try:
            candles, df = fetcher.fetch(symbol, timeframe, limit)
            repo.save_candles(candles)

            signal = strat.generate_signal(df)
            current_price = df.iloc[-1]["close"]
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
        except Exception as e:
            logger.error(f"Error in paper trading loop: {e}")

        time.sleep(interval)


@app.command()
def init_db():
    """Initialize the SQLite database schema."""
    from crypto_trade_mvp.data.schema import init_db as _init_db
    _init_db()
    typer.echo("Database initialized.")


if __name__ == "__main__":
    app()
