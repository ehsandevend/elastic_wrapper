from __future__ import annotations as _annotations

import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi_pagination import add_pagination

from config.settings.integrations_config import BaseConfig
from config.settings.services.elk import es_manager
from config.settings.services.middlewares import add_trusted_host_middleware, add_cors_middleware
from config.settings.services.prometheus import setup_prometheus
from config.settings.services.register_apps import register_apps
from config.settings.services.sentry import setup_sentry


@asynccontextmanager
async def lifespan(app: FastAPI):

    await es_manager.initialize()
    yield
    await es_manager.close()


app = FastAPI(
    lifespan=lifespan,
    max_request_size=100*1024*1024,
    debug=BaseConfig.DEBUG,
    docs_url="/docs",  # Explicitly set docs URL
    redoc_url="/redoc",  # Explicitly set redoc URL
    openapi_url="/openapi.json"
)

setup_prometheus(app)
setup_sentry()
add_trusted_host_middleware(app)
add_cors_middleware(app)

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.abspath(os.path.join(parent_dir, "apps")))

add_pagination(app)
register_apps(app)
