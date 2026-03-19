from dataclasses import dataclass
from enum import Enum


class SignalType(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


@dataclass
class Signal:
    symbol: str
    timeframe: str
    timestamp: int
    strategy_name: str
    signal: SignalType
