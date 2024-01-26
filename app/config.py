import os
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv


class Config:
    base_directory = Path(__file__).parent
    if (base_directory.parent / ".env").exists():
        load_dotenv(base_directory.parent / ".env", verbose=True, override=False)

    migrate_db_on_startup: bool = os.getenv("MIGRATE_DB_ON_STARTUP", "false") == "true"

    environment: Literal["development", "production"] = (
        os.getenv("ENVIRONMENT").lower().strip()
    )
    is_development: bool = environment == "development"
    is_production: bool = environment == "production"

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


class AuthConfig:
    secret_key = os.getenv("AUTH_SECRET_KEY")

    unusable_password_prefix = "UNUSABLE_PASSWORD_"

    cookie_auth_key = "jwtauth"
    cookie_auth_secure = bool_env("COOKIE_SECURE", "true")
    cookie_auth_httponly = (
        bool_env("COOKIE_HTTPONLY", "true")
    )
    cookie_auth_samesite: Literal["lax", "strict"] = (
        os.getenv("COOKIE_SAMESITE", "strict").lower().strip()
    )

    jwt_algorithm = "HS256"
    jwt_audience = "TEST"
    jwt_issuer = "TEST"
    jwt_age_seconds = 60 * 60 * 24 * 7  # 7 days

    create_admin_on_startup: bool = (
        os.getenv("CREATE_ADMIN_ON_STARTUP", "false") == "true"
    )
    admin_username: str = os.getenv("ADMIN_USERNAME")
    admin_email: str = os.getenv("ADMIN_EMAIL")
    admin_password: str = os.getenv("ADMIN_PASSWORD")
