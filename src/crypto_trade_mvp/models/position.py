from dataclasses import dataclass, field
import time


@dataclass
class Position:
    symbol: str
    size: float = 0.0
    avg_entry_price: float = 0.0
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    updated_at: int = field(default_factory=lambda: int(time.time() * 1000))

    def is_open(self) -> bool:
        return self.size > 0
