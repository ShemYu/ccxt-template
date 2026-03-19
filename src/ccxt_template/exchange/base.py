from typing import Protocol


class ExchangeAdapter(Protocol):
    def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int) -> list[list]: ...
