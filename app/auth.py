import asyncio
import datetime
import json
import secrets
import string
import sys
from typing import Annotated

import jwt
from fastapi import HTTPException, status, Depends
from fastapi.requests import Request
from fastapi.security import HTTPBearer
from passlib.context import CryptContext
from sqlalchemy.dialects.postgresql import insert as postgresql_insert

from app.config import AuthConfig
from app.db import Session
from app.enums import UserRole
from app.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

not_authenticated_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
)
permission_exception = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied"
)


class BearerTokenCookie(HTTPBearer):
    async def __call__(self, request: Request) -> str | None:
        token = request.cookies.get(AuthConfig.cookie_auth_key)

        if not token:
            if self.auto_error:
                raise not_authenticated_exception
            else:
                return None

        return token


class Password:
    @classmethod
    async def get_unusable(cls) -> str:
        allowed_chars = string.ascii_letters + string.digits
        random_string = "".join(secrets.choice(allowed_chars) for _ in range(8))
        return AuthConfig.unusable_password_prefix + random_string

    @classmethod
    async def is_unusable(cls, hashed_password: str) -> bool:
        return hashed_password.startswith(AuthConfig.unusable_password_prefix)

    @classmethod
    async def get_hashed(cls, raw_password: str) -> str:
        return pwd_context.hash(raw_password)

    @classmethod
    async def verify_hashed(cls, raw_password: str, hashed_password: str) -> bool:
        if await cls.is_unusable(hashed_password):
            return False

        return pwd_context.verify(raw_password, hashed_password)


class JWT:
    @classmethod
    async def for_user(cls, user_id: int, user_role: UserRole) -> str:
        expires = datetime.datetime.utcnow() + datetime.timedelta(
            seconds=AuthConfig.jwt_age_seconds
        )
        return jwt.encode(
            payload={
                "sub": user_id,
                "scopes": [user_role],
                "exp": expires,
                "iss": AuthConfig.jwt_issuer,
                "aud": AuthConfig.jwt_audience,
            },
            key=AuthConfig.secret_key,
            algorithm=AuthConfig.jwt_algorithm,
        )

    @classmethod
    async def verify(
        cls, token: str, role: UserRole | None = None, user_id: int | None = None
    ) -> dict:
        payload = jwt.decode(
            jwt=token,
            key=AuthConfig.secret_key,
            algorithms=[AuthConfig.jwt_algorithm],
            issuer=AuthConfig.jwt_issuer,
            audience=AuthConfig.jwt_audience,
            options={
                "require": ["exp", "iss", "aud", "sub", "scopes"],
                "verify_signature": True,
                "verify_exp": True,
                "verify_iss": True,
                "verify_aud": True,
            },
        )

        if role is not None and role not in payload["scopes"]:
            raise PermissionError("Invalid role")

        if user_id is not None and user_id != payload["sub"]:
            raise PermissionError("Invalid user")

        return payload


class Admin:
    @classmethod
    async def get_user_id(
        cls, token: Annotated[str | None, Depends(BearerTokenCookie(auto_error=False))]
    ) -> int | None:
        if not token:
            return None

        try:
            jwt_payload: dict = await JWT.verify(token, role=UserRole.ADMIN)
        except (jwt.PyJWTError, json.JSONDecodeError, PermissionError):
            return None

        user_id = jwt_payload["sub"]
        return user_id

    @classmethod
    async def required(
        cls, token: Annotated[str | None, Depends(BearerTokenCookie(auto_error=True))]
    ):
        try:
            await JWT.verify(token, role=UserRole.ADMIN)
        except (jwt.PyJWTError, json.JSONDecodeError):
            raise not_authenticated_exception
        except PermissionError:
            raise permission_exception

    @classmethod
    async def create_async(cls):
        async with Session() as session:
            async with session.begin():
                await session.execute(
                    postgresql_insert(User)
                    .values(
                        email=AuthConfig.admin_email,
                        username=AuthConfig.admin_username,
                        hashed_password=await Password.get_hashed(
                            AuthConfig.admin_password
                        ),
                        role=UserRole.ADMIN,
                        is_active=True,
                    )
                    .on_conflict_do_update(
                        index_elements=[User.email],
                        set_=dict(
                            hashed_password=await Password.get_hashed(
                                AuthConfig.admin_password
                            ),
                            username=AuthConfig.admin_username,
                        ),
                    )
                )

    @classmethod
    def create(cls):
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(cls.create_async())
