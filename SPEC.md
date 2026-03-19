# Specification — crypto-trade-mvp

## Tech Stack

| Layer | Choice |
|---|---|
| Language | Python 3.11+ |
| Package manager | `uv` |
| Exchange API | `ccxt` |
| Data processing | `pandas`, `numpy` |
| Config | `pydantic-settings` + `.env` |
| Logging | `loguru` |
| Storage | SQLite (upgradeable to PostgreSQL) |
| Testing | `pytest` |

---

## Project Structure

```
crypto-trade-mvp/
├── README.md
├── SPEC.md
├── pyproject.toml
├── .env.example
├── config/
│   └── settings.yaml
├── data/
│   └── app.db
├── logs/
├── scripts/
│   ├── run_fetch.py
│   ├── run_strategy.py
│   ├── run_backtest.py
│   └── run_paper.py
├── src/
│   └── crypto_trade_mvp/
│       ├── __init__.py
│       ├── config.py
│       ├── logger.py
│       ├── models/
│       │   ├── candle.py
│       │   ├── signal.py
│       │   ├── order.py
│       │   ├── position.py
│       │   └── portfolio.py
│       ├── exchange/
│       │   ├── base.py
│       │   ├── ccxt_client.py
│       │   └── bitflyer_adapter.py
│       ├── data/
│       │   ├── fetcher.py
│       │   ├── repository.py
│       │   └── schema.py
│       ├── strategy/
│       │   ├── base.py
│       │   └── sma_cross.py
│       ├── execution/
│       │   ├── simulator.py
│       │   └── fee_model.py
│       ├── portfolio/
│       │   └── manager.py
│       ├── backtest/
│       │   └── engine.py
│       └── cli/
│           └── main.py
└── tests/
    ├── test_strategy.py
    ├── test_simulator.py
    └── test_backtest.py
```

---

## Core Interfaces

### ExchangeAdapter

```python
class ExchangeAdapter(Protocol):
    def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int) -> list: ...
```

### Strategy

```python
class Strategy(Protocol):
    def generate_signal(self, df: pd.DataFrame) -> str: ...
```

Signals: `BUY` | `SELL` | `HOLD`

### PaperBroker

```python
class PaperBroker:
    def place_order(self, side: str, price: float, size: float) -> None: ...
    def get_portfolio_state(self) -> dict: ...
```

---

## Database Schema (SQLite)

### `candles`
| Column | Type |
|---|---|
| id | INTEGER PK |
| symbol | TEXT |
| timeframe | TEXT |
| timestamp | INTEGER (unix ms) |
| open | REAL |
| high | REAL |
| low | REAL |
| close | REAL |
| volume | REAL |

### `signals`
| Column | Type |
|---|---|
| id | INTEGER PK |
| symbol | TEXT |
| timeframe | TEXT |
| timestamp | INTEGER |
| strategy_name | TEXT |
| signal | TEXT (BUY/SELL/HOLD) |

### `orders`
| Column | Type |
|---|---|
| id | INTEGER PK |
| timestamp | INTEGER |
| symbol | TEXT |
| side | TEXT (buy/sell) |
| order_type | TEXT (market) |
| price | REAL |
| size | REAL |
| fee | REAL |
| slippage | REAL |
| status | TEXT |

### `positions`
| Column | Type |
|---|---|
| id | INTEGER PK |
| symbol | TEXT |
| size | REAL |
| avg_entry_price | REAL |
| unrealized_pnl | REAL |
| realized_pnl | REAL |
| updated_at | INTEGER |

### `portfolio_snapshots`
| Column | Type |
|---|---|
| id | INTEGER PK |
| timestamp | INTEGER |
| cash | REAL |
| equity | REAL |
| total_position_value | REAL |
| realized_pnl | REAL |
| unrealized_pnl | REAL |

---

## Strategy: SMA Crossover

**Parameters**
- `short_window = 5`
- `long_window = 20`

**Signal Rules**
- short SMA crosses above long SMA → `BUY`
- short SMA crosses below long SMA → `SELL`
- otherwise → `HOLD`

**Position Guards**
- If already holding a position, ignore `BUY`
- If no position, ignore `SELL`
- No duplicate orders in the same direction

---

## Execution Simulation

- Market orders only
- Fee: configurable in bps (default `10 bps`)
- Slippage: configurable in bps (default `5 bps`)

---

## CLI Commands

```bash
python -m crypto_trade_mvp.cli.main fetch-data \
  --symbol BTC/JPY --timeframe 5m --limit 300

python -m crypto_trade_mvp.cli.main run-strategy \
  --symbol BTC/JPY --timeframe 5m --strategy sma_cross

python -m crypto_trade_mvp.cli.main backtest \
  --symbol BTC/JPY --timeframe 5m --strategy sma_cross

python -m crypto_trade_mvp.cli.main paper-trade \
  --symbol BTC/JPY --timeframe 5m --interval 60
```

---

## Non-Functional Requirements

- Every module must be independently testable
- Strategy is decoupled from exchange adapter
- No hardcoded config in source code
- API keys via `.env` only
- Exchange adapter interface must support future swap to live trading
