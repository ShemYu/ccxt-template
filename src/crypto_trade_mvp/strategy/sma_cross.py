import pandas as pd
from crypto_trade_mvp.models.signal import SignalType
from crypto_trade_mvp.logger import logger


class SMACrossStrategy:
    name = "sma_cross"

    def __init__(self, short_window: int = 5, long_window: int = 20):
        self.short_window = short_window
        self.long_window = long_window

    def generate_signal(self, df: pd.DataFrame) -> SignalType:
        if len(df) < self.long_window:
            logger.warning(f"Not enough candles ({len(df)}) for long_window={self.long_window}")
            return SignalType.HOLD

        df = df.copy()
        df["sma_short"] = df["close"].rolling(self.short_window).mean()
        df["sma_long"] = df["close"].rolling(self.long_window).mean()

        prev = df.iloc[-2]
        curr = df.iloc[-1]

        prev_above = prev["sma_short"] > prev["sma_long"]
        curr_above = curr["sma_short"] > curr["sma_long"]

        if not prev_above and curr_above:
            logger.info("Signal: BUY (short SMA crossed above long SMA)")
            return SignalType.BUY
        elif prev_above and not curr_above:
            logger.info("Signal: SELL (short SMA crossed below long SMA)")
            return SignalType.SELL
        else:
            return SignalType.HOLD
