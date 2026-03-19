import ccxt
from crypto_trade_mvp.config import settings
from crypto_trade_mvp.logger import logger


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
