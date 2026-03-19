---
name: bitflyer-api
description: Build and maintain bitFlyer exchange integrations. Use this skill when implementing or modifying bitFlyer REST clients, Realtime API clients, authentication/signing, rate limiting, order submission, balance retrieval, or exchange-specific adapters for trading bots and data pipelines. Trigger this skill whenever the user mentions bitFlyer, bitFlyer Lightning API, bitFlyer Crypto CFD API, product codes like BTC_JPY or FX_BTC_JPY, or any task involving bitFlyer API keys, signing, order execution, or market data from bitFlyer — even if they don't explicitly say "use bitflyer-api skill".
---

# bitFlyer API Integration Skill

This skill helps you implement robust bitFlyer integrations for:
- HTTP Public API
- HTTP Private API
- Realtime API (market data and account/order event streams)
- Exchange adapters for quant trading systems
- Signing, rate limiting, retries, and local persistence

Use this skill when:
- The task mentions bitFlyer, bitFlyer Lightning API, bitFlyer Crypto CFD API, or product codes like `BTC_JPY` / `FX_BTC_JPY`
- The user wants to create an exchange adapter, market data collector, order executor, or WebSocket stream consumer
- The task involves API key signing, order creation, order cancellation, balance retrieval, executions, or rate limit handling

## What this skill assumes

- bitFlyer provides:
  - HTTP API at `https://api.bitflyer.com/v1/`
  - Realtime API in addition to HTTP API
- Private API calls require API key auth with:
  - `ACCESS-KEY`
  - `ACCESS-TIMESTAMP`
  - `ACCESS-SIGN`
- API keys are issued from the bitFlyer developer page
- The integration may target either spot or Crypto CFD-compatible endpoints

When implementing code, treat bitFlyer as an exchange-specific adapter.
Do not leak secrets, do not hardcode API keys, and do not commit credentials.

## Operating principles

1. Separate exchange-neutral logic from bitFlyer-specific logic.
2. Keep product codes configurable.
3. Build public and private clients separately.
4. Add a signing utility with deterministic tests.
5. Centralize rate limiting and retry behavior.
6. Prefer typed request/response models when possible.
7. Preserve raw exchange payloads for debugging.
8. Make idempotency and reconciliation explicit in order workflows.

## Recommended local file layout

For a Python project:

```text
src/
  exchanges/
    bitflyer/
      __init__.py
      client.py
      public_api.py
      private_api.py
      realtime.py
      auth.py
      models.py
      rate_limit.py
      adapter.py
tests/
  exchanges/
    bitflyer/
      test_auth.py
      test_public_api.py
      test_private_api.py
      test_realtime.py
```

## Minimum capabilities to implement first

Implement in this order:

### Phase 1: market data

* get markets
* get ticker
* get executions
* get board/order book
* normalize symbols and product codes

### Phase 2: auth + account

* signing helper
* get permissions
* get balances
* get trading commission

### Phase 3: trading

* send child order
* cancel child order
* get child orders
* get executions
* optional: cancel all child orders

### Phase 4: realtime

* public channels:

  * ticker
  * executions
  * board snapshot / board diff
* private channels:

  * child order events
  * parent order events if needed

Multiple subscriptions must share a single WebSocket connection (TCP).
Do not open one connection per channel — send all `subscribe` messages
over the same `websockets.connect()` session and dispatch incoming
messages by channel name in a single read loop.

## Exchange-specific implementation notes

### 1. Product code handling

bitFlyer uses exchange-specific `product_code` values rather than generic `BTC/JPY` style symbols.
Create a mapping layer such as:

* internal `BTC/JPY` -> exchange `BTC_JPY`
* internal `BTC-CFD/JPY` -> exchange `FX_BTC_JPY`

Do not scatter product-code translation across the codebase.
Centralize it in one module.

### 2. Private auth signing

For Private API requests:

* generate Unix timestamp as string
* concatenate:

  * timestamp
  * HTTP method
  * request path
  * request body (empty string if no body)
* compute HMAC-SHA256 using API secret
* set request headers:

  * `ACCESS-KEY`
  * `ACCESS-TIMESTAMP`
  * `ACCESS-SIGN`

Always test signing with fixed fixtures.

### 3. Rate limiting

Use a dedicated limiter that accounts for:

* same-IP limit
* private API limit
* stricter limits for certain trading endpoints
* special restrictions for very small orders

Do not embed sleep logic inline inside endpoint methods.
Use a reusable limiter abstraction.

### 4. Order model

bitFlyer exposes exchange-specific order semantics such as:

* child orders
* parent orders (special orders)

For MVPs, implement child orders first:

* create order
* cancel order
* query order list
* query executions

Only implement parent orders if strategy requirements justify them.

### 5. Error handling

Handle these classes of errors distinctly:

* authentication/signature failure
* authorization/permission failure
* validation errors (invalid product code, bad size, missing params)
* rate limit / temporary block
* network / timeout / reconnect
* exchange-side temporary service degradation

Create exchange-specific exceptions or at least map them to stable internal error types.

### 6. Reconciliation

Never trust only local order state.
Implement reconciliation by periodically refreshing:

* active orders
* recent executions
* balances / positions if relevant

On startup:

* reload unresolved orders from local persistence
* query exchange state
* reconcile diffs before resuming trading

### 7. Realtime: single TCP connection for all subscriptions

bitFlyer Realtime API uses JSON-RPC over WebSocket.
All channel subscriptions must share one persistent connection:

```python
# Correct — one connection, multiple subscribe messages
async with websockets.connect(WS_URL) as ws:
    for channel in channels:
        await ws.send(json.dumps({"method": "subscribe", "params": {"channel": channel}}))
    async for message in ws:
        data = json.loads(message)
        channel = data.get("params", {}).get("channel", "")
        dispatch(channel, data)

# Wrong — one connection per channel
for channel in channels:
    asyncio.create_task(open_separate_connection(channel))  # don't do this
```

Dispatch by `params.channel` to the correct handler.
This keeps resource usage flat regardless of how many channels you add.

## Coding rules for Claude

When asked to generate code for bitFlyer:

* produce production-oriented code, not toy snippets
* include request/response type hints
* isolate credentials in environment variables
* include structured logging
* include retry/backoff only for retry-safe calls
* avoid retrying non-idempotent create-order calls blindly
* write at least one auth unit test and one integration-style client test stub
* keep public and private clients separate

## Default implementation targets

When the user does not specify otherwise, generate:

* Python 3.11+
* `httpx` for REST
* `websockets` or equivalent for WS
* `pydantic` models if useful
* `pytest` tests
* environment variables:

  * `BITFLYER_API_KEY`
  * `BITFLYER_API_SECRET`
  * `BITFLYER_BASE_URL`
  * `BITFLYER_WS_URL`

## Suggested adapter interface

Use an internal interface similar to:

```python
class ExchangeAdapter(Protocol):
    async def fetch_ticker(self, symbol: str) -> Ticker: ...
    async def fetch_orderbook(self, symbol: str) -> OrderBook: ...
    async def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int) -> list[Candle]: ...
    async def fetch_balances(self) -> list[Balance]: ...
    async def create_order(self, symbol: str, side: str, order_type: str, size: float, price: float | None = None) -> OrderResult: ...
    async def cancel_order(self, symbol: str, order_id: str) -> None: ...
    async def fetch_open_orders(self, symbol: str) -> list[Order]: ...
    async def fetch_my_trades(self, symbol: str, limit: int = 100) -> list[Trade]: ...
```

Then implement bitFlyer-specific translation underneath.

## What to read next

Read these local references before implementing details:

* `references/overview.md`
* `references/auth-signing.md`
* `references/endpoints.md`
* `references/rate-limits.md`

## Output expectations

When using this skill, prefer one of these deliverables:

1. exchange adapter code
2. auth/signing utility
3. rate limiter
4. realtime consumer
5. endpoint reference table
6. test scaffolding
7. reconciliation workflow
8. integration checklist

If the user asks for "the bitFlyer client", generate:

* public REST client
* private REST client
* signer
* typed models
* minimal tests
* usage example
