import asyncio
import json
import ssl
import time
from collections.abc import Callable
from datetime import datetime, timezone

import websockets

# bitFlyer's WS endpoint has a self-signed cert in the chain
_SSL_CTX = ssl.create_default_context()
_SSL_CTX.check_hostname = False
_SSL_CTX.verify_mode = ssl.CERT_NONE

from crypto_trade_mvp.exchange.candle_builder import CandleBuilder
from crypto_trade_mvp.logger import logger

WS_URL = "wss://ws.lightstream.bitflyer.com/json-rpc"


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
    history_candles: int = 25,
    extra_channels: dict[str, Callable] | None = None,
) -> None:
    """Stream bitFlyer Realtime API over a single WebSocket connection.

    All channel subscriptions share one TCP connection. `extra_channels`
    maps channel name -> handler callable for any additional subscriptions
    (e.g. ticker, board). The executions channel for `symbol` is always
    included and drives the CandleBuilder.

    Workflow:
    1. Warm up with REST history to fill `history_candles` worth of candles.
    2. Open one WebSocket, subscribe to all channels in a single session.
    3. Dispatch incoming messages by channel name to the correct handler.
    """
    product_code = symbol.replace("/", "_")
    executions_channel = f"lightning_executions_{product_code}"

    builder = CandleBuilder(symbol=symbol, timeframe=timeframe, on_candle_closed=on_candle_closed)

    logger.info(f"Warming up history ({history_candles} candles)...")
    await _fetch_history(exchange, symbol, builder, history_candles)

    # Build the full channel -> handler map
    handlers: dict[str, Callable] = {executions_channel: _make_executions_handler(builder)}
    if extra_channels:
        handlers.update(extra_channels)

    logger.info(f"Connecting to bitFlyer Realtime API (channels: {list(handlers)})...")

    async for ws in websockets.connect(WS_URL, ping_interval=20, ping_timeout=10, ssl=_SSL_CTX):
        try:
            # Send all subscribe messages over the same connection
            for channel in handlers:
                await ws.send(json.dumps({
                    "method": "subscribe",
                    "params": {"channel": channel},
                }))
                logger.info(f"Subscribed to {channel}")

            async for message in ws:
                data = json.loads(message)
                channel = data.get("params", {}).get("channel", "")
                handler = handlers.get(channel)
                if handler:
                    handler(data.get("params", {}).get("message", []))

        except websockets.ConnectionClosed:
            logger.warning("WebSocket disconnected, reconnecting...")
            continue


def _make_executions_handler(builder: CandleBuilder) -> Callable:
    """Return a handler that feeds execution events into the CandleBuilder."""
    def handle(executions: list[dict]) -> None:
        for ex in executions:
            exec_date = ex.get("exec_date", "")
            if exec_date:
                ts_ms = int(datetime.fromisoformat(exec_date.replace("Z", "+00:00")).timestamp() * 1000)
            else:
                ts_ms = int(time.time() * 1000)
            builder.feed(ex["price"], ex["size"], ts_ms)
    return handle
