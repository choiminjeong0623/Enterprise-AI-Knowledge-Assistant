from fastapi import FastAPI
from app.api.chat import router as chat_router
from app.database.database import Base
from app.database.database import engine
from app.models.conversation import Conversation
from app.exceptions.custom_exception import OpenAIException
from app.exceptions.handlers import (
    openai_exception_handler,
    OpenAIException
)
from app.middleware.logging import LoggingMiddleware

Base.metadata.create_all(bind=engine)

# ------------------------------------------------
# 프로젝트 생성
# Spring => @SpringBootApplication
# ------------------------------------------------
app = FastAPI(
    title="Enterprise AI Knowledge Assistant",
    version="1.0.0"
)
## Custom Exception Handler
app.add_exception_handler(
    OpenAIException,
    openai_exception_handler
)

## Middleware Exception Handler
app.add_middleware(
    LoggingMiddleware
)
# ------------------------------------------------
# include_router : Router 등록
# Spring에서는 Controller가 자동 등록
# ------------------------------------------------
app.include_router(chat_router)

# ------------------------------------------------
# API 생성
# Spring => @GetMapping
# ------------------------------------------------
@app.get("/")
def root():
    return {
        "message" : "Enterprise AI Knowledge Assistant API"
    }

# ------------------------------------------------
# 서버 상태 확인
# ------------------------------------------------
@app.get("/health")
def health():
    return {
        "status" : "OK"
    }