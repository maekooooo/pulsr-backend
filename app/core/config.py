from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Pulsr"
    ENV: str = "dev"
    # SQLite file in project root
    DATABASE_URL: str = "sqlite:///./pulsr.db"
    # 5-second pulse duration (can tune later)
    ROUND_DURATION_SEC: int = 5
    # Default market pair
    MARKET_SYMBOL: str = "BTCUSDT"
    # Price provider: "binance" | "kraken"
    PRICE_PROVIDER: str = "kraken"

    class Config:
        env_file = ".env"

settings = Settings()
