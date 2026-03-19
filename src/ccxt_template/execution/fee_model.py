from ccxt_template.config import settings


class FeeModel:
    def __init__(self, fee_bps: int | None = None, slippage_bps: int | None = None):
        self.fee_bps = fee_bps if fee_bps is not None else settings.trading_fee_bps
        self.slippage_bps = slippage_bps if slippage_bps is not None else settings.slippage_bps

    def apply(self, price: float, side: str) -> tuple[float, float, float]:
        """Returns (execution_price, fee_amount, slippage_amount)."""
        slippage_amount = price * (self.slippage_bps / 10000)
        if side == "buy":
            exec_price = price + slippage_amount
        else:
            exec_price = price - slippage_amount

        fee_amount = exec_price * (self.fee_bps / 10000)
        return exec_price, fee_amount, slippage_amount
