import logging

from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


async def http_exception_handler(_request: Request, exc: HTTPException) -> JSONResponse:
    d = exc.detail
    if isinstance(d, dict) and "code" in d and "detail" in d:
        return JSONResponse(status_code=exc.status_code, content=d)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(d), "code": "HTTP_ERROR"},
    )


async def validation_exception_handler(_request: Request, exc: RequestValidationError) -> JSONResponse:
    errs = exc.errors()
    msg = errs[0].get("msg", "validation error") if errs else "validation error"
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": msg, "code": "VALIDATION_ERROR"},
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception(
        "unhandled_exception",
        extra={"path": request.url.path, "exc_type": type(exc).__name__},
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error", "code": "INTERNAL_ERROR"},
    )
