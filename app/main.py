from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.database.mongodb import (
    connect_to_mongodb,
    close_mongodb_connection,
)
from app.exceptions.handlers import (
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler,
)
from app.routes import admin, auth, course, batch


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongodb()
    try:
        yield
    finally:
        await close_mongodb_connection()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)


# Global Exception Handlers

app.add_exception_handler(
    StarletteHTTPException,
    http_exception_handler,
)

app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler,
)

app.add_exception_handler(
    Exception,
    general_exception_handler,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(course.router)
app.include_router(batch.router)