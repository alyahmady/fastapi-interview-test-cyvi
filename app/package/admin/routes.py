from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, true
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Config
from app.db import get_db
from app.enums import UserRole
from app.models import User
from app.package.admin.schemas import LoginSchema
from app.utils import verify_hashed_password, get_user_jwt

router = APIRouter()

templates = Jinja2Templates(directory=Config.base_directory / "templates")


@router.get("/login/", response_class=HTMLResponse)
async def admin_login(*, request: Request, message: Annotated[str, Query(None)]):
    return templates.TemplateResponse(
        request=request, name="admin/login.html", context={"message": message}
    )


@router.post("/login/", response_class=HTMLResponse)
async def admin_login_form(
    *,
    request: Request,
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
    auth: LoginSchema,
):
    admin: User = await db.scalar(
        select(User).where(
            User.is_active == true(),
            User.role == UserRole.ADMIN,
            User.username == auth.username,
        )
    )
    if not admin:
        return RedirectResponse(
            url=request.url_for("admin_login").include_query_params(
                message="User not found"
            )
        )

    if not verify_hashed_password(auth.password):
        return RedirectResponse(
            url=request.url_for("admin_login").include_query_params(
                message="Password is incorrect"
            )
        )

    response.set_cookie(
        key=Config.cookie_auth_key,
        value=await get_user_jwt(admin.id, admin.role),
        max_age=Config.cookie_auth_max_age,
        samesite=Config.cookie_auth_samesite,
        secure=Config.cookie_auth_secure,
        httponly=Config.cookie_auth_httponly,
    )

    return RedirectResponse(url=request.url_for("home"))
