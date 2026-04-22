from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.exceptions import AppException
from app.utils.logger import logger

async def app_exeception_handler(request: Request, exc: AppException):

    logger.warning(
        f"AppException: {exc.error_code} | {exc.message}"
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.message,
            "error_code": exc.error_code
        }
    )

async def generic_exception_handler(request: Request, exc: Exception):

    logger.error(f"Unhandled Error: {str(exc)}")

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal Server Error",
            "error_code": "INTERNAL_SERVER_ERROR"
        }
    )





