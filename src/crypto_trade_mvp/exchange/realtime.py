import asyncio
import json
import time
from collections.abc import Callable
from datetime import datetime, timezone

import websockets

from crypto_trade_mvp.exchange.candle_builder import CandleBuilder
from crypto_trade_mvp.logger import logger

WS_URL = "wss://ws.lightstream.bitflyer.com/json-rpc"
PRODUCT_CODE = "BTC_JPY"


async def _fetch_history(exchange, symbol: str, builder: CandleBuilder, target_candles: int) -> None:
    """Page through REST executions to warm up the CandleBuilder with history.

    Feeds trades in chronological order (oldest first) so the builder
    builds candles correctly. Strategy callbacks are suppressed during
    warm-up — the builder's on_candle_closed is replaced temporarily.
    """
    interval_ms = builder._interval_ms
    needed_ms = target_candles * interval_ms
    cutoff_ms = int(time.time() * 1000) - needed_ms

    # Collect all trades first, then feed oldest-first.
    # bitFlyer paginates backwards using the minimum trade id as `before`.
    all_trades: list[dict] = []
    before_id = None

    while True:
        params = {"count": 500}
        if before_id:
            params["before"] = before_id

        trades = exchange.fetch_trades(symbol, params=params)
        if not trades:
            break

        reached_cutoff = False
        for t in trades:
            if t["timestamp"] < cutoff_ms:
                reached_cutoff = True
                break
            all_trades.append(t)

        before_id = min(t["info"]["id"] for t in trades)
        oldest_ts = min(t["timestamp"] for t in trades)
        logger.info(f"History: collected {len(all_trades)} trades, oldest ts={oldest_ts}")

        if reached_cutoff:
            break

        await asyncio.sleep(0.6)  # ~100 req/min, well within 500/5min limit

    # Feed oldest-first with callbacks suppressed
    original_callback = builder._on_candle_closed
    builder._on_candle_closed = lambda c: None

    for t in reversed(all_trades):
        builder.feed(t["price"], t["amount"], t["timestamp"])

    builder._on_candle_closed = original_callback
    logger.info(f"History warm-up done: fed {len(all_trades)} trades, builder ready")


async def stream(
    exchange,
    symbol: str,
    timeframe: str,
    on_candle_closed: Callable,
    history_candles: int = 30,
) -> None:
    """
    1. Warm up with REST history to fill `history_candles` worth of data.
    2. Open WebSocket and stream live executions into the same CandleBuilder.

    `on_candle_closed` is called each time a candle boundary is crossed.
    """
    builder = CandleBuilder(symbol=symbol, timeframe=timeframe, on_candle_closed=on_candle_closed)

    logger.info(f"Warming up history ({history_candles} candles)...")
    await _fetch_history(exchange, symbol, builder, history_candles)

    logger.info("Connecting to bitFlyer Realtime API...")
    async for ws in websockets.connect(WS_URL, ping_interval=20, ping_timeout=10):
        try:
            await ws.send(json.dumps({
                "method": "subscribe",
                "params": {"channel": f"lightning_executions_{PRODUCT_CODE}"},
            }))
            logger.info(f"Subscribed to lightning_executions_{PRODUCT_CODE}")

            async for message in ws:
                data = json.loads(message)
                executions = data.get("params", {}).get("message", [])
                for ex in executions:
                    exec_date = ex.get("exec_date", "")
                    if exec_date:
                        ts_ms = int(datetime.fromisoformat(exec_date.replace("Z", "+00:00")).timestamp() * 1000)
                    else:
                        ts_ms = int(time.time() * 1000)
                    builder.feed(ex["price"], ex["size"], ts_ms)

        except websockets.ConnectionClosed:
            logger.warning("WebSocket disconnected, reconnecting...")
            continue
