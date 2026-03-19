from dataclasses import dataclass, field
from enum import Enum
import time


class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"


class OrderStatus(str, Enum):
    FILLED = "filled"
    REJECTED = "rejected"


@dataclass
class Order:
    symbol: str
    side: OrderSide
    price: float
    size: float
    fee: float
    slippage: float
    status: OrderStatus
    order_type: str = "market"
    timestamp: int = field(default_factory=lambda: int(time.time() * 1000))
