# bitFlyer API Overview

bitFlyer exposes two API surfaces:

1. HTTP API
   - Base URL: `https://api.bitflyer.com/v1/`
   - Includes:
     - Public API
     - Private API

2. Realtime API
   - Used for streaming market and account-related events

Private API requires API keys generated from the developer page.

The API documentation indicates compatibility for bitFlyer Crypto CFD with the former Lightning FX API semantics, including continued use of:
- `market_type = FX`
- `product_code = FX_BTC_JPY`

Use a symbol/product-code mapping layer in your implementation.
