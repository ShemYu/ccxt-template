from dataclasses import dataclass, field
import time


@dataclass
class PortfolioSnapshot:
    cash: float
    equity: float
    total_position_value: float
    realized_pnl: float
    unrealized_pnl: float
    timestamp: int = field(default_factory=lambda: int(time.time() * 1000))
