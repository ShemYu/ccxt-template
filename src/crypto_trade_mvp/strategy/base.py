from typing import Protocol
import pandas as pd
from crypto_trade_mvp.models.signal import SignalType


class Strategy(Protocol):
    name: str

    def generate_signal(self, df: pd.DataFrame) -> SignalType: ...
