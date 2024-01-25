import logging

from fastapi import FastAPI
from mangum import Mangum

from app.config import Config
from app.db import db_migrate

logger = logging.getLogger()
logger.setLevel(logging.DEBUG if Config.is_development else logging.INFO)

if Config.migrate_db_on_startup:
    db_migrate()

app = FastAPI(debug=Config.is_development)

lambda_handler = Mangum(app, lifespan="off")
