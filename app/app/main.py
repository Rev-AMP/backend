import logging
import sys

import sentry_sdk
from fastapi import FastAPI
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from starlette.middleware.cors import CORSMiddleware

from app.api.api_v1.api import api_router
from app.core.config import settings

logging.basicConfig(
    format="[%(levelname)s] (%(asctime)s) %(module)s:%(pathname)s:%(funcName)s:%(lineno)s:: %(message)s",
    level=logging.INFO,
    datefmt="%d-%m-%y %H:%M:%S",
    stream=sys.stdout,
)

app = FastAPI(title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json")

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if settings.SENTRY_DSN:
    sentry_sdk.init(dsn=settings.SENTRY_DSN)
    app.add_middleware(SentryAsgiMiddleware)

app.include_router(api_router, prefix=settings.API_V1_STR)

logging.info("Starting application")
