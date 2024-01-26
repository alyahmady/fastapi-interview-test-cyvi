import logging

from fastapi import FastAPI
from mangum import Mangum

from app.auth import Admin
from app.config import Config, AuthConfig
from app.db import db_migrate
from app.package.admin.routes import router as admin_router
from app.package.base.routes import router as base_router
from app.package.customers.routes import router as customers_router

logger = logging.getLogger()
logger.setLevel(logging.DEBUG if Config.is_development else logging.INFO)

if Config.migrate_db_on_startup:
    db_migrate()

if AuthConfig.create_admin_on_startup:
    Admin.create()

app = FastAPI(debug=Config.is_development)
# app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(base_router, prefix="")
app.include_router(admin_router, prefix="/admin")
app.include_router(customers_router, prefix="/customers")

lambda_handler = Mangum(app, lifespan="off")
