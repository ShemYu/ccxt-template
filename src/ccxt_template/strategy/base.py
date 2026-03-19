from typing import Protocol
import pandas as pd
from ccxt_template.models.signal import SignalType


class Strategy(Protocol):
    name: str

    def generate_signal(self, df: pd.DataFrame) -> SignalType: ...
