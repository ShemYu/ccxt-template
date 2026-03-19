# ccxt-template

A template for building algorithmic trading bots on top of [CCXT](https://github.com/ccxt/ccxt).
Ships with a working bitFlyer integration, SMA strategy, paper trading loop, and SQLite persistence.

Use this as a starting point — swap the exchange, symbol, or strategy to fit your needs.

---

## What's inside

```
src/crypto_trade_mvp/
├── exchange/
│   ├── ccxt_client.py        # Base CCXT wrapper
│   ├── bitflyer_adapter.py   # bitFlyer-specific overrides
│   ├── candle_builder.py     # Builds K-bars from raw trades (exchange-agnostic)
│   └── realtime.py           # WebSocket stream + REST history warm-up
├── strategy/
│   ├── base.py               # Strategy interface
│   └── sma_cross.py          # SMA5/SMA20 crossover
├── execution/
│   └── simulator.py          # Paper broker (fee + slippage simulation)
├── data/
│   ├── fetcher.py            # Candle fetching
│   ├── repository.py         # SQLite read/write
│   └── schema.py             # SQLAlchemy models
├── backtest/
│   └── engine.py             # Backtesting engine
└── cli/main.py               # CLI entry point
```

---

## Quickstart

### 1. Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) — used for all dependency and runtime management

### 2. Install

```bash
git clone https://github.com/ShemYu/ccxt-template.git
cd ccxt-template
uv sync
```

### 3. Configure

```bash
cp .env.example .env
```

Edit `.env`:

```env
EXCHANGE_NAME=bitflyer
API_KEY=your_api_key
API_SECRET=your_api_secret
```

### 4. Initialize the database

```bash
uv run python -m crypto_trade_mvp.cli.main init-db
```

---

## Usage

### Paper trading (realtime)

Streams live BTC/JPY trades from bitFlyer WebSocket, builds 5m candles on the fly,
and runs SMA crossover to generate BUY/SELL/HOLD signals.

```bash
uv run python -m crypto_trade_mvp.cli.main paper-trade --symbol BTC/JPY --timeframe 5m
```

On startup:
1. Fetches recent trade history via REST to seed the candle window (warm-up)
2. Connects to WebSocket and streams live executions
3. Outputs signals and portfolio state each time a candle closes

### Fetch candles manually

```bash
uv run python -m crypto_trade_mvp.cli.main fetch-data --symbol BTC/JPY --timeframe 5m --limit 100
```

### Run strategy on stored candles

```bash
uv run python -m crypto_trade_mvp.cli.main run-strategy --symbol BTC/JPY --timeframe 5m --strategy sma_cross
```

### Backtest

```bash
uv run python -m crypto_trade_mvp.cli.main backtest --symbol BTC/JPY --timeframe 5m --strategy sma_cross
```

---

## How to extend

### Add a new exchange

1. Create `src/crypto_trade_mvp/exchange/<exchange>_adapter.py`
2. Subclass `CCXTClient`, override `fetch_ohlcv` if the exchange lacks a candle endpoint
3. Update `.env` → `EXCHANGE_NAME=<ccxt_exchange_id>`

### Add a new strategy

1. Create `src/crypto_trade_mvp/strategy/<name>.py`
2. Subclass `BaseStrategy`, implement `generate_signal(df) -> SignalType`
3. Register in `cli/main.py` → `STRATEGIES` dict

### Subscribe to additional WebSocket channels

`realtime.stream()` accepts an `extra_channels` dict — all channels share one TCP connection:

```python
await stream(
    exchange=adapter._exchange,
    symbol="BTC/JPY",
    timeframe="5m",
    on_candle_closed=on_candle_closed,
    extra_channels={
        "lightning_ticker_BTC_JPY": handle_ticker,
        "lightning_board_snapshot_BTC_JPY": handle_board,
    },
)
```

---

## Architecture notes

**Why build candles from trades?**
bitFlyer does not expose a native OHLCV endpoint. `CandleBuilder` accumulates
raw executions into K-bars locally. It is transport-agnostic — works with both
REST-fetched history and live WebSocket events.

**Why share one WebSocket connection?**
All channel subscriptions run over a single TCP connection. Adding more channels
(ticker, board, private order events) does not open additional connections —
just send more `subscribe` messages and add handlers to the dispatch map.

**Layer separation**
Data layer (WS/REST) → Strategy layer → Execution layer are kept independent.
This makes it straightforward to swap transports (e.g. replace polling with
event-driven), add message queues, or deploy layers separately on Cloud Run.

---

## Milestones

See [MILESTONES.md](./MILESTONES.md) for current progress.

---

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md).

## License

MIT — see [LICENSE](./LICENSE).
