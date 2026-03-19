from dataclasses import dataclass


@dataclass
class Candle:
    symbol: str
    timeframe: str
    timestamp: int  # unix ms
    open: float
    high: float
    low: float
    close: float
    volume: float
