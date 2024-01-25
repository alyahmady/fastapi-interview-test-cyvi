from functools import lru_cache

from alembic.command import upgrade
from alembic.config import Config as AlembicConfig
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
    AsyncEngine,
)

from app.config import PostgresConfig, Config


@lru_cache
def calculate_pool_parameters(
    max_connections=PostgresConfig.max_connections,
    expected_load=PostgresConfig.concurrent_connections,
    safety_factor=0.1,
) -> tuple[int, int]:
    """
    Calculates the pool_size and max_overflow parameters for SQLAlchemy.

    Args:
        max_connections (int): Maximum number of connections supported by the database.
        expected_load (int): Expected number of concurrent database connections needed.
        safety_factor (float, optional): Safety factor to account for occasional spikes in usage.
                                         Defaults to 0.1 (10% safety margin).

    Returns:
        tuple: A tuple containing the calculated pool_size and max_overflow values.

    """
    db_pool_size = int(expected_load * (1 + safety_factor))
    db_max_overflow = int(max_connections * safety_factor)

    return db_pool_size, db_max_overflow


pool_size, max_overflow = calculate_pool_parameters()

engine: AsyncEngine = create_async_engine(
    PostgresConfig.database_url,
    pool_pre_ping=True,
    pool_size=pool_size,
    max_overflow=max_overflow,
)
# test_engine: AsyncEngine = create_async_engine(
#     PostgresConfig.test_database_url,
#     poolclass=NullPool,
# )

Session: async_sessionmaker[AsyncSession] = async_sessionmaker(
    expire_on_commit=False, autocommit=False, autoflush=False, bind=engine
)


# TestSession: async_sessionmaker[AsyncSession] = async_sessionmaker(
#     expire_on_commit=False, autocommit=False, autoflush=False, bind=test_engine
# )


async def get_db():
    async with Session() as session:
        async with session.begin():
            yield session


def db_migrate():
    config_file = Config.base_directory.parent / "alembic.ini"
    config = AlembicConfig(file_=config_file)
    upgrade(config, "head")
