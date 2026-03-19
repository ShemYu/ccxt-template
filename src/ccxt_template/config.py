from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    exchange_name: str = "bitflyer"
    api_key: str = ""
    api_secret: str = ""
    database_url: str = "sqlite:///data/app.db"
    default_symbol: str = "BTC/JPY"
    default_timeframe: str = "5m"
    initial_capital: float = 100000.0
    trading_fee_bps: int = 10
    slippage_bps: int = 5


settings = Settings()
