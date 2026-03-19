# Contributing

Contributions are welcome. This project is a template for algorithmic trading bots using CCXT — improvements to exchange adapters, strategy scaffolding, rate limiting, and documentation are all useful.

## Getting started

```bash
git clone https://github.com/ShemYu/ccxt-template.git
cd ccxt-template
uv sync
```

## Making changes

1. Fork the repo and create a branch from `main`
2. Make your changes
3. Run the tests: `uv run pytest`
4. Submit a pull request with a clear description of what you changed and why

## What to contribute

- New exchange adapters under `src/ccxt_template/exchange/`
- New strategy examples under `src/ccxt_template/strategy/`
- Bug fixes, test coverage, and documentation improvements

## Code style

- Python 3.11+
- Keep exchange-specific logic isolated from shared/neutral logic
- No hardcoded credentials — use environment variables
- Add tests for new adapters and strategies

## Reporting issues

Open an issue on GitHub with a clear description and steps to reproduce.
