import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from mangum import Mangum

from app.config import Config
from app.models import init_db

logger = logging.getLogger()
logger.setLevel(logging.DEBUG if Config.is_development else logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(lifespan=lifespan, debug=Config.is_development)

lambda_handler = Mangum(app, lifespan="auto")
