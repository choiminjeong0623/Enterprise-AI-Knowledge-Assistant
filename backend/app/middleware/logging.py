import time
from starlette.middleware.base import BaseHTTPMiddleware
from app.clients.logger import logger

# ------------------------------------------------
# BaseHTTPMiddleware
# Spring => Filter, HandlerInterceptor
# ------------------------------------------------
class LoggingMiddleware(BaseHTTPMiddleware):

    async def dispatch(
        self,
        request,
        call_next
    ):

        start_time = time.time()

        logger.info(
            f"[REQUEST] {request.method} {request.url.path}"
        )

        ## 실제 Router를 수행
        response = await call_next(request)
        ## 실행 시간 계산
        elapsed = time.time() - start_time

        logger.info(
            f"[RESPONSE] {response.status_code}"
        )

        logger.info(
            f"[TIME] {elapsed:.3f} sec"
        )

        return response