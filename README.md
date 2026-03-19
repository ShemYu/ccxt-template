# ccxt-template

A template for building algorithmic trading bots using CCXT, with exchange adapters, strategy scaffolding, and rate limiting out of the box.

## Project Goal

Build a working crypto trading MVP — not a perfect platform. The goal is to have something running within a few evenings, then iterate.

## MVP Scope

First version supports only:

- **Exchange**: bitFlyer (or GMO Coin)
- **Symbol**: `BTC/JPY`
- **Timeframe**: `5m`
- **Strategy**: SMA crossover (SMA5 / SMA20)
- **Execution**: paper trading only

**Out of scope for v1:**

- Real order execution
- Multi-exchange arbitrage
- High-frequency trading
- Web dashboard
- Complex strategy search
- Distributed architecture

## Setup

```bash
# 1. Clone and enter the repo
git clone https://github.com/ShemYu/ccxt-template.git
cd ccxt-template

# 2. Install dependencies (using uv)
uv sync

# 3. Copy and fill in your env
cp .env.example .env

# 4. Initialize the database
uv run python -m crypto_trade_mvp.cli.main init-db
```

## Commands

```bash
# Fetch OHLCV candles and store to SQLite
uv run python -m crypto_trade_mvp.cli.main fetch-data --symbol BTC/JPY --timeframe 5m --limit 300

# Run strategy on stored candles and generate signals
uv run python -m crypto_trade_mvp.cli.main run-strategy --symbol BTC/JPY --timeframe 5m --strategy sma_cross

# Run a backtest on historical data
uv run python -m crypto_trade_mvp.cli.main backtest --symbol BTC/JPY --timeframe 5m --strategy sma_cross

# Start paper trading loop (polls every N seconds)
uv run python -m crypto_trade_mvp.cli.main paper-trade --symbol BTC/JPY --timeframe 5m --interval 60
```

## Current Limitations

- Single exchange only (bitFlyer)
- Single symbol only (BTC/JPY)
- Single strategy only (SMA crossover)
- Paper trading only — no real order execution
- No web UI or dashboard
- SQLite only (no cloud DB)
- No multi-timeframe analysis

## Milestones

### Milestone 1 — Data
- Fetch OHLCV candles from exchange
- Store to SQLite
- Print dataframe to console

### Milestone 2 — Signal
- Run SMA crossover strategy
- Output BUY / SELL / HOLD signals

### Milestone 3 — Execution
- Simulate trades based on signals
- Track cash, position, PnL

### Milestone 4 — Loop
- Run paper trading via CLI on a timed interval
- Structured logging to file

### Milestone 5 — Reporting
- Output simple backtest report (total return, win rate, trade count)

## Next Steps (Post-MVP)

- Add more strategies (RSI, Bollinger Bands)
- Add real order execution interface
- Support multiple symbols
- Upgrade storage to PostgreSQL
- Add simple HTML report output
