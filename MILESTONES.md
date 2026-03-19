# Milestones — ccxt-template

## Milestone 1 — Data
- [x] Fetch OHLCV candles from exchange
- [x] Store candles to SQLite
- [x] Print dataframe to console
- [x] Build OHLCV from raw trades (bitFlyer workaround — no native candle endpoint)

## Milestone 2 — Signal
- [x] Implement SMA crossover strategy (SMA5 / SMA20)
- [x] Output BUY / SELL / HOLD signals
- [ ] Store signals to SQLite

## Milestone 3 — Execution
- [x] Simulate market orders based on signals
- [x] Apply fee and slippage
- [x] Track cash, position size, avg entry price
- [x] Calculate unrealized and realized PnL

## Milestone 4 — Loop
- [x] Realtime paper trading via bitFlyer WebSocket (lightning_executions)
- [x] REST history warm-up before WebSocket starts (seed candle window)
- [x] CandleBuilder: accumulate raw trades into K-bars, exchange-transport agnostic
- [x] Single TCP connection for all WebSocket channel subscriptions
- [x] Auto-reconnect on disconnect
- [ ] Structured logging to `logs/` directory

## Milestone 5 — Reporting
- [x] Backtest engine skeleton
- [ ] Full backtest report: total return, win rate, trade count, max drawdown
