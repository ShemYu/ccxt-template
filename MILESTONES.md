# Milestones — crypto-trade-mvp

## Milestone 1 — Data
- [ ] Fetch OHLCV candles via ccxt
- [ ] Store candles to SQLite
- [ ] Print dataframe to console

## Milestone 2 — Signal
- [ ] Implement SMA crossover strategy
- [ ] Output BUY / SELL / HOLD signals
- [ ] Store signals to SQLite

## Milestone 3 — Execution
- [ ] Simulate market orders based on signals
- [ ] Apply fee and slippage
- [ ] Track cash, position size, avg entry price
- [ ] Calculate unrealized and realized PnL

## Milestone 4 — Loop
- [ ] Run paper trading via CLI on a timed interval
- [ ] Structured logging to `logs/` directory

## Milestone 5 — Reporting
- [ ] Backtest on historical candle data
- [ ] Output summary: total return, win rate, trade count, max drawdown
