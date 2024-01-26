from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.auth import Admin
from app.config import Config

router = APIRouter()

templates = Jinja2Templates(directory=Config.base_directory / "templates")


@router.get("/", response_class=HTMLResponse)
async def home_page(
    *, request: Request, user_id: Annotated[int, Depends(Admin.get_user_id)]
):
    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={"is_admin_logged_in": user_id is not None},
    )
