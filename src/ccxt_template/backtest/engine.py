import pandas as pd
from ccxt_template.strategy.base import Strategy
from ccxt_template.execution.simulator import PaperBroker
from ccxt_template.models.signal import SignalType
from ccxt_template.config import settings
from ccxt_template.logger import logger


class BacktestEngine:
    def __init__(self, strategy: Strategy, symbol: str, initial_capital: float | None = None):
        self.strategy = strategy
        self.symbol = symbol
        self.initial_capital = initial_capital or settings.initial_capital

    def run(self, df: pd.DataFrame) -> dict:
        broker = PaperBroker(symbol=self.symbol, initial_capital=self.initial_capital)
        trades = 0

        for i in range(len(df)):
            window = df.iloc[: i + 1]
            signal = self.strategy.generate_signal(window)
            price = window.iloc[-1]["close"]

            broker.update_unrealized_pnl(price)

            if signal == SignalType.BUY:
                order = broker.place_order("buy", price)
                if order:
                    trades += 1
            elif signal == SignalType.SELL:
                order = broker.place_order("sell", price)
                if order:
                    trades += 1

        final = broker.get_portfolio_state()
        total_return = (final.equity - self.initial_capital) / self.initial_capital * 100

        report = {
            "initial_capital": self.initial_capital,
            "final_equity": round(final.equity, 2),
            "total_return_pct": round(total_return, 4),
            "realized_pnl": round(final.realized_pnl, 2),
            "unrealized_pnl": round(final.unrealized_pnl, 2),
            "total_trades": trades,
        }
        logger.info(f"Backtest complete: {report}")
        return report
