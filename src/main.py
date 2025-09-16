
"""
Main FastAPI application module.

This module initializes the FastAPI app, configures middleware, exception handlers, and includes routers for authentication, user, and contact management.

:author: DimaKisiv
"""
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from src.configuration.swagger_config import OPENAPI_KWARGS
from src.database.models import Base
from src.database.session import engine

from src.routers import auth, users, contacts

Base.metadata.create_all(bind=engine)

app = FastAPI(**OPENAPI_KWARGS)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    lambda request, exc: JSONResponse(
        status_code=429,
        content={"detail": "Too Many Requests"}
    )
)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://127.0.0.1"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(contacts.router)

# Serve Sphinx HTML docs at /docs

app = FastAPI()

if os.path.isdir("docs/_build/html"):
    app.mount(
        "/docs",
        StaticFiles(directory="docs/_build/html", html=True),
        name="sphinx-docs"
    )
