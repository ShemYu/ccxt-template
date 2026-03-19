from ccxt_template.exchange.ccxt_client import CCXTClient


class BitflyerAdapter(CCXTClient):
    """bitFlyer-specific adapter. bitFlyer does not support fetchOHLCV,
    so candles are built by resampling raw trade executions."""

    def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int) -> list[list]:
        return self.build_ohlcv_from_trades(symbol, timeframe, limit)
