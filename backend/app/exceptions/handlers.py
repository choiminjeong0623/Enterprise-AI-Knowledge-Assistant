from fastapi import Request
from fastapi.responses import JSONResponse

from app.clients.logger import logger
from app.exceptions.custom_exception import CustomException


async def custom_exception_handler(
    request: Request,
    exc: CustomException
):

    logger.exception(exc)

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "code": exc.code,
            "message": exc.message
        }
    )