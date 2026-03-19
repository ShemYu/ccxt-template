import pandas as pd
from ccxt_template.exchange.base import ExchangeAdapter
from ccxt_template.models.candle import Candle
from ccxt_template.logger import logger


class DataFetcher:
    def __init__(self, adapter: ExchangeAdapter):
        self._adapter = adapter

    def fetch(self, symbol: str, timeframe: str, limit: int) -> tuple[list[Candle], pd.DataFrame]:
        raw = self._adapter.fetch_ohlcv(symbol, timeframe, limit)
        candles = [
            Candle(
                symbol=symbol, timeframe=timeframe,
                timestamp=row[0], open=row[1], high=row[2],
                low=row[3], close=row[4], volume=row[5],
            )
            for row in raw
        ]
        df = pd.DataFrame(raw, columns=["timestamp", "open", "high", "low", "close", "volume"])
        df["datetime"] = pd.to_datetime(df["timestamp"], unit="ms")
        logger.info(f"Fetched {len(candles)} candles for {symbol} [{timeframe}]")
        return candles, df
