# bitFlyer Endpoint Priorities

## Public endpoints to implement first

- market list
- board / order book
- ticker
- executions
- board state / health if needed
- funding rate if targeting Crypto CFD

## Private endpoints to implement first

- get API permissions
- get balances
- send child order
- cancel child order
- cancel all child orders
- get child orders
- get executions
- get trading commission

## Advanced or optional private endpoints

- send parent order
- cancel parent order
- get parent orders
- get parent order details
- balance history
- positions
- collateral / margin state
- deposit / withdrawal related endpoints

## Recommended MVP order flow

1. fetch balances
2. send child order
3. poll/query child orders
4. fetch executions
5. reconcile local state
