## Backend Architecture

API
 ↓
Service
 ↓
Repository
 ↓
Storage

### Repository

- ConversationRepository
- JSON Storage (Current)

Future

- SQLAlchemy
- SQLite
- Snowflake

## Logging

Application Logger

- INFO
- WARNING
- ERROR
- EXCEPTION

## Exception Handling

- Global Exception Handler
- Custom Exception
- OpenAI Exception

## 프로젝트 구조
backend
    /app
        /api             # FastAPI Router
        /services        # 비즈니스 로직(Service Layer)
        /repositories    # DB 접근
        /clients         # 외부 시스템(OpenAPI 등)
        /parsers         # GPT 응답 파싱
        /conversation    # 대화 관련 기능
        /models          # SQLAlchemy Model
        /schemas         # Pydantic DTO
        /database        # DB 연결
        /dependencies    # Depends()
        /exceptions      # Global Exception
        /core            # config, logger, prompt
        /utils           # 공통 유틸

## Enterprise AI Knowledge Assistant

- FastAPI
- SQLAlchemy
- OpenAI API
- Repository Pattern
- Dependency Injection
- Middleware
- Logging
- Exception Handling