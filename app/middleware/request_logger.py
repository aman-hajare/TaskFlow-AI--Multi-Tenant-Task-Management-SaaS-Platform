from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
import time

from app.utils.logger import logger


class RequestLogginMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):

        start_time = time.time()

        response = await call_next(request)

        process_time = time.time() - start_time

        logger.info(
            f"{request.method} {request.url.path} "
            f"status={response.status_code} "
            f"time={process_time:.4f}s"
        )

        return response
    
# INFO | GET /tasks status=200 time=0.0312s