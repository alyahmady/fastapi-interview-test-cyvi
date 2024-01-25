import logging

from fastapi import FastAPI
from mangum import Mangum

from app.config import Config

logger = logging.getLogger()
logger.setLevel(logging.DEBUG if Config.is_development else logging.INFO)

app = FastAPI()

lambda_handler = Mangum(app, lifespan="off")
