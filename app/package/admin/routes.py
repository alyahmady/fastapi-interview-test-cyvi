from typing import Annotated

from fastapi import APIRouter, Depends, Query, Form, status
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, true
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import Password, JWT
from app.config import Config, AuthConfig
from app.db import get_db
from app.enums import UserRole
from app.models import User

router = APIRouter()

templates = Jinja2Templates(directory=Config.base_directory / "templates")


@router.get("/login/", response_class=HTMLResponse)
async def admin_login(*, request: Request, message: Annotated[str, Query] = None):
    return templates.TemplateResponse(
        request=request, name="admin/login.html", context={"message": message}
    )


@router.post("/login/", response_class=HTMLResponse)
async def admin_login_form(
    *,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    username: Annotated[str, Form(max_length=50)],
    password: Annotated[str, Form(min_length=8)],
):
    admin: User = await db.scalar(
        select(User).where(
            User.is_active == true(),
            User.role == UserRole.ADMIN,
            User.username == username,
        )
    )
    if not admin:
        return RedirectResponse(
            url=request.url_for("admin_login").include_query_params(
                message="User not found"
            ),
            status_code=status.HTTP_302_FOUND
        )

    if not await Password.verify_hashed(
        raw_password=password, hashed_password=admin.hashed_password
    ):
        return RedirectResponse(
            url=request.url_for("admin_login").include_query_params(
                message="Password is incorrect"
            ),
            status_code=status.HTTP_302_FOUND
        )


    response = RedirectResponse(
        url=request.url_for("home_page").include_query_params(
            message="Logged in successfully"
        ),
        status_code=status.HTTP_302_FOUND
    )
    response.set_cookie(
        key=AuthConfig.cookie_auth_key,
        value=await JWT.for_user(user_id=admin.id, user_role=admin.role),
        max_age=AuthConfig.jwt_age_seconds,
        samesite=AuthConfig.cookie_auth_samesite,
        secure=AuthConfig.cookie_auth_secure,
        httponly=AuthConfig.cookie_auth_httponly,
    )
    return response


@router.post("/logout/", response_class=HTMLResponse)
async def admin_logout(*, request: Request, response: Response):
    response = RedirectResponse(
        url=request.url_for("home_page").include_query_params(message="Logged out successfully"), status_code=status.HTTP_302_FOUND
    )
    response.delete_cookie(AuthConfig.cookie_auth_key)
    return response
