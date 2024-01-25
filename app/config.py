import os
from pathlib import Path
from typing import Literal
from dotenv import load_dotenv

class Config:
    base_directory = Path(__file__).parent
    if (base_directory.parent / ".env").exists():
        load_dotenv(base_directory.parent / ".env", verbose=True, override=True)

    migrate_db_on_startup: bool = os.getenv("MIGRATE_DB_ON_STARTUP", "false") == "true"

    environment: Literal["development", "production"] = os.getenv("ENVIRONMENT")
    is_development: bool = environment == "development"
    is_production: bool = environment == "production"

    access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    # refresh_token_expiration_day = int(os.getenv("REFRESH_TOKEN_EXPIRATION_DAY", 7))

    time_zone = os.getenv("TIME_ZONE", "UTC")

class PostgresConfig:
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    db_name = os.getenv("POSTGRES_DB")
    host = os.getenv("BACKEND_POSTGRES_HOST")
    port = int(os.getenv("POSTGRES_PORT", "5432"))

    max_connections = int(os.getenv("POSTGRES_MAX_DB_CONNECTIONS", "10"))
    concurrent_connections = int(
        os.getenv("POSTGRES_EXPECTED_DB_CONCURRENT_CONNECTIONS", 30)
    )

    database_url = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db_name}"
