from fastapi import Request
from fastapi.responses import JSONResponse

from app.exceptions.custom_exception import OpenAIException
from app.clients.logger import logger

async def openai_exception_handler(
    request : Request,
    exc : OpenAIException
):
    logger.exception(exc)

    return JSONResponse(
        status_code = 500,
        content = {
            "success" : False,
            "code" : "OPENAI_ERROR",
            "message" : exc.message
        }
    )