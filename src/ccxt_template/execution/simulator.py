from ccxt_template.models.order import Order, OrderSide, OrderStatus
from ccxt_template.models.position import Position
from ccxt_template.models.portfolio import PortfolioSnapshot
from ccxt_template.execution.fee_model import FeeModel
from ccxt_template.config import settings
from ccxt_template.logger import logger


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

        fee_rate = self._fee_model.fee_bps / 10000
        slippage_rate = self._fee_model.slippage_bps / 10000

        if order_side == OrderSide.BUY:
            exec_price = price * (1 + slippage_rate)
            # size must account for fee so total spend = cash exactly
            # cash = size * exec_price * (1 + fee_rate)
            size = self.cash / (exec_price * (1 + fee_rate))
            notional = size * exec_price
            fee = notional * fee_rate
            slippage = price * slippage_rate
            cash_before = self.cash
            self.cash = 0.0
            self.position.size = size
            self.position.avg_entry_price = exec_price
            logger.info(
                f"BUY  qty={size:.6f} price={price:.0f} exec={exec_price:.0f} "
                f"notional={notional:.2f} fee_rate={fee_rate:.4f} fee={fee:.2f} "
                f"cash_before={cash_before:.2f} cash_after=0.00"
            )
        else:
            exec_price = price * (1 - slippage_rate)
            size = self.position.size
            notional = size * exec_price
            fee = notional * fee_rate
            slippage = price * slippage_rate
            proceeds = notional - fee
            cash_before = self.cash
            self.position.realized_pnl += proceeds - (size * self.position.avg_entry_price)
            self.cash = proceeds
            self.position.size = 0.0
            self.position.avg_entry_price = 0.0
            logger.info(
                f"SELL qty={size:.6f} price={price:.0f} exec={exec_price:.0f} "
                f"notional={notional:.2f} fee_rate={fee_rate:.4f} fee={fee:.2f} "
                f"cash_before={cash_before:.2f} cash_after={self.cash:.2f}"
            )

        order = Order(
            symbol=self.symbol, side=order_side,
            price=exec_price, size=size,
            fee=fee, slippage=slippage * size,
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
