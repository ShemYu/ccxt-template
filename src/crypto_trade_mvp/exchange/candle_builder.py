from dataclasses import dataclass
from crypto_trade_mvp.models.candle import Candle
from crypto_trade_mvp.logger import logger

TIMEFRAME_SECONDS = {
    "1m": 60,
    "5m": 300,
    "15m": 900,
    "30m": 1800,
    "1h": 3600,
}


@dataclass
class _Bar:
    ts: int  # bucket open timestamp in ms
    open: float
    high: float
    low: float
    close: float
    volume: float


class CandleBuilder:
    """Accumulates raw trades into fixed-timeframe candles.

    Call feed(price, size, timestamp_ms) for each incoming trade.
    When a candle boundary is crossed, on_candle_closed is called
    with the completed Candle.

    Keeping this class independent of the data source (REST or WS)
    makes it easy to swap transports later.
    """

    def __init__(self, symbol: str, timeframe: str, on_candle_closed):
        if timeframe not in TIMEFRAME_SECONDS:
            raise ValueError(f"Unsupported timeframe: {timeframe}")
        self._symbol = symbol
        self._timeframe = timeframe
        self._interval_ms = TIMEFRAME_SECONDS[timeframe] * 1000
        self._on_candle_closed = on_candle_closed
        self._bar: _Bar | None = None

    def _bucket(self, ts_ms: int) -> int:
        return (ts_ms // self._interval_ms) * self._interval_ms

    def feed(self, price: float, size: float, ts_ms: int) -> None:
        bucket = self._bucket(ts_ms)

        if self._bar is None:
            self._bar = _Bar(ts=bucket, open=price, high=price, low=price, close=price, volume=size)
            return

        if bucket == self._bar.ts:
            self._bar.high = max(self._bar.high, price)
            self._bar.low = min(self._bar.low, price)
            self._bar.close = price
            self._bar.volume += size
        else:
            self._close_bar()
            self._bar = _Bar(ts=bucket, open=price, high=price, low=price, close=price, volume=size)

    def _close_bar(self) -> None:
        if self._bar is None:
            return
        candle = Candle(
            symbol=self._symbol,
            timeframe=self._timeframe,
            timestamp=self._bar.ts,
            open=self._bar.open,
            high=self._bar.high,
            low=self._bar.low,
            close=self._bar.close,
            volume=self._bar.volume,
        )
        logger.info(f"Candle closed [{self._timeframe}] {self._symbol} ts={self._bar.ts} close={self._bar.close}")
        self._on_candle_closed(candle)
