import ccxt
import pandas as pd
from ccxt_template.config import settings
from ccxt_template.logger import logger

TIMEFRAME_TO_PANDAS = {
    "1m": "1min",
    "5m": "5min",
    "15m": "15min",
    "30m": "30min",
    "1h": "1h",
    "4h": "4h",
    "1d": "1D",
}


class CCXTClient:
    def __init__(self):
        exchange_class = getattr(ccxt, settings.exchange_name)
        self._exchange = exchange_class({
            "apiKey": settings.api_key,
            "secret": settings.api_secret,
        })
        logger.info(f"Initialized exchange: {settings.exchange_name}")

    def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int) -> list[list]:
        logger.info(f"Fetching {limit} candles for {symbol} [{timeframe}]")
        return self._exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)

    def build_ohlcv_from_trades(self, symbol: str, timeframe: str, limit: int) -> list[list]:
        """Fetch raw trades and resample into OHLCV candles. Use for exchanges that lack fetchOHLCV."""
        pandas_freq = TIMEFRAME_TO_PANDAS.get(timeframe)
        if not pandas_freq:
            raise ValueError(f"Unsupported timeframe: {timeframe}")

        # Fetch enough trades to fill `limit` candles. Each candle needs at least one trade,
        # so we over-fetch by a factor of 10 to ensure coverage.
        fetch_count = min(limit * 10, 500)
        logger.info(f"Fetching {fetch_count} trades to build {limit} {timeframe} candles for {symbol}")
        trades = self._exchange.fetch_trades(symbol, limit=fetch_count)

        if not trades:
            return []

        df = pd.DataFrame([
            {"timestamp": t["timestamp"], "price": t["price"], "amount": t["amount"]}
            for t in trades
        ])
        df["datetime"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
        df = df.set_index("datetime").sort_index()

        ohlcv = df["price"].resample(pandas_freq).ohlc()
        ohlcv["volume"] = df["amount"].resample(pandas_freq).sum()
        ohlcv = ohlcv.dropna().tail(limit)

        result = []
        for dt, row in ohlcv.iterrows():
            ts = int(dt.timestamp() * 1000)
            result.append([ts, row["open"], row["high"], row["low"], row["close"], row["volume"]])

        return result
