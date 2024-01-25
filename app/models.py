import datetime

from package.db import engine
from sqlalchemy import (
    Sequence,
    String,
    DateTime,
    func,
    Boolean,
    text,
    BigInteger,
)
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped

from app.enums import UserRole


class Base(AsyncAttrs, DeclarativeBase):
    pass


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


UserPrimaryKeySequence = Sequence(
    "user_manager_user_id_sequence", start=1000000, increment=1
)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        BigInteger,
        UserPrimaryKeySequence,
        server_default=UserPrimaryKeySequence.next_value(),
        primary_key=True,
    )
    email: Mapped[str] = mapped_column(
        String(256), index=True, nullable=False, unique=True
    )
    username: Mapped[str] = mapped_column(String(50), nullable=True, unique=True)
    phone: Mapped[str] = mapped_column(String(15), nullable=True)

    hashed_password: Mapped[str] = mapped_column(String(100), nullable=False)

    first_name: Mapped[str] = mapped_column(String(150), nullable=True)
    last_name: Mapped[str] = mapped_column(String(150), nullable=True)

    role: Mapped[str] = mapped_column(
        ENUM(UserRole, name="UserRoleEnum"),
        nullable=False,
        default=UserRole.CUSTOMER,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("TRUE")
    )

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )
