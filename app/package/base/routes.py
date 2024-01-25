from fastapi import APIRouter
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.config import Config

router = APIRouter()

templates = Jinja2Templates(directory=Config.base_directory / "templates")


@router.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    return templates.TemplateResponse(request=request, name="home.html")
