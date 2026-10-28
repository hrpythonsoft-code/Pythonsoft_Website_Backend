from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
):
    if isinstance(exc.detail, str):
        message = exc.detail
    else:
        message = "An error occurred"

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": message,
        },
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    errors = []

    for error in exc.errors():
        field = ".".join(str(location) for location in error["loc"])

        errors.append(
            {
                "field": field,
                "message": error["msg"],
            }
        )

    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "Validation error",
            "errors": errors,
        },
    )


async def general_exception_handler(
    request: Request,
    exc: Exception,
):
    print(f"Unhandled server error: {exc}")

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error. Please try again later.",
        },
    )