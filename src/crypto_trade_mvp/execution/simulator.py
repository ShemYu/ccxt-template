from crypto_trade_mvp.models.order import Order, OrderSide, OrderStatus
from crypto_trade_mvp.models.position import Position
from crypto_trade_mvp.models.portfolio import PortfolioSnapshot
from crypto_trade_mvp.execution.fee_model import FeeModel
from crypto_trade_mvp.config import settings
from crypto_trade_mvp.logger import logger


class PaperBroker:
    def __init__(self, symbol: str, initial_capital: float | None = None):
        self.symbol = symbol
        self.cash = initial_capital if initial_capital is not None else settings.initial_capital
        self.position = Position(symbol=symbol)
        self._fee_model = FeeModel()
        self._orders: list[Order] = []

    def place_order(self, side: str, price: float) -> Order | None:
        order_side = OrderSide(side)

        if order_side == OrderSide.BUY and self.position.is_open():
            logger.warning("BUY ignored: position already open")
            return None
        if order_side == OrderSide.SELL and not self.position.is_open():
            logger.warning("SELL ignored: no open position")
            return None

        exec_price, fee, slippage = self._fee_model.apply(price, side)

        if order_side == OrderSide.BUY:
            size = self.cash / exec_price
            cost = self.cash
            self.cash = 0.0
            self.position.size = size
            self.position.avg_entry_price = exec_price
            logger.info(f"BUY {size:.6f} @ {exec_price:.2f} | fee={fee:.2f}")
        else:
            size = self.position.size
            proceeds = size * exec_price - fee
            self.position.realized_pnl += proceeds - (size * self.position.avg_entry_price)
            self.cash = proceeds
            self.position.size = 0.0
            self.position.avg_entry_price = 0.0
            logger.info(f"SELL {size:.6f} @ {exec_price:.2f} | fee={fee:.2f}")

        order = Order(
            symbol=self.symbol, side=order_side,
            price=exec_price, size=size,
            fee=fee, slippage=slippage,
            status=OrderStatus.FILLED,
        )
        self._orders.append(order)
        return order

    def update_unrealized_pnl(self, current_price: float) -> None:
        if self.position.is_open():
            self.position.unrealized_pnl = (
                (current_price - self.position.avg_entry_price) * self.position.size
            )

    def get_portfolio_state(self) -> PortfolioSnapshot:
        position_value = self.position.size * self.position.avg_entry_price
        equity = self.cash + position_value + self.position.unrealized_pnl
        return PortfolioSnapshot(
            cash=self.cash,
            equity=equity,
            total_position_value=position_value,
            realized_pnl=self.position.realized_pnl,
            unrealized_pnl=self.position.unrealized_pnl,
        )
