# bitFlyer Private API Authentication

Private API requests require these headers:

- `ACCESS-KEY`
- `ACCESS-TIMESTAMP`
- `ACCESS-SIGN`

## Signature algorithm

Construct the signing payload as:

```text
timestamp + method + path + body
```

Then compute:

```text
HMAC-SHA256(secret, payload)
```

## Implementation notes

* `timestamp` should be a Unix timestamp string
* `method` must match the actual HTTP verb exactly
* `path` should be the request path, e.g. `/v1/me/getbalance`
* `body` should be the exact serialized request body string, or empty string for GETs without body

## Safety rules

* never commit keys
* never print secrets in logs
* redact headers in debug output
* write deterministic unit tests for the signer
