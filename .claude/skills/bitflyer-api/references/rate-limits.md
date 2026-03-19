# bitFlyer Rate Limits

Design your client around these documented limits:

- same IP address: 500 requests per 5 minutes
- Private API: 500 requests per 5 minutes
- combined total for:
  - `POST /v1/me/sendchildorder`
  - `POST /v1/me/sendparentorder`
  - `POST /v1/me/cancelallchildorders`
  is 300 requests per 5 minutes

There is also an additional restriction for orders with quantity <= 0.1:
- up to 100 orders per minute across all books
- after hitting the cap, the next hour is limited to 10 orders per minute

## Client design implications

- implement token-bucket or leaky-bucket rate limiting
- separate trading write limits from general private reads
- avoid aggressive polling when websocket can reduce load
- back off immediately on rate-limit or temporary-block behavior
- log local limiter decisions for debugging
