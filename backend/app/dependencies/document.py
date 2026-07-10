from fastapi import Depends
from sqlalchemy.orm import Session

from app.clients.openai_client import OpenAIClient
from app.dependencies.database import get_db
from app.repositories.document_chunk_repository import DocumentChunkRepository
from app.repositories.document_repository import DocumentRepository
from app.services.document_service import DocumentService
from app.services.embedding_service import EmbeddingService
from app.services.text_chunking_service import TextChunkingService
from app.services.text_extraction_service import TextExtractionService

## Document 관련 객체들을 생성해서 FastAPI에 주입해주는 역할을 한다.
## API에서 DocumentService가 필요함
## → dependencies/document.py가 필요한 객체들을 조립한다.
## → 완성된 DocumentService를 API에 전달한다.
## API 함수 안에서 직접 Service를 만들지 않고 의존성 생성 코드를 따로 분리한 것이다.

## DocumentRepository 객체를 만든다. 
def get_document_repository(
    db: Session = Depends(get_db),  ## FastAPI가 get_db()를 실행해서 DB 세션을 넣어준다.
):
    return DocumentRepository(db)

## DocumentRepository 객체를 생성한다.
## 이 Repository는 document_chunks 테이블에 접근한다.
def get_document_chunk_repository(
    db: Session = Depends(get_db),
):
    return DocumentChunkRepository(db)

## 텍스트 추출 서비스를 생성한다.
def get_text_extraction_service():
    return TextExtractionService()

## 텍스트 chunk 분할 서비스를 생성한다.
def get_text_chunking_service():
    return TextChunkingService()

# OpenAIClient 객체를 생성한다.
def get_openai_client():
    return OpenAIClient()


# EmbeddingService 객체를 생성한다.
def get_embedding_service(
    client: OpenAIClient = Depends(get_openai_client),
):
    return EmbeddingService(
        client=client,
    )

## 이 함수는 최종적으로 DocumentService를 만든다.
## 그런데, DocumentService는 여러 객체가 필요하다.
## FastAPI는 내부적으로 아래와 같이 실행한다.
## 1. get_document_service()를 실행해야 함
## 2. get_document_service()에 필요한 의존성을 확인
## 3. document_repository()를 실행
## 4. get_document_chunk_repository() 실행
## 5. get_text_extraction_service() 실행
## 6. get_text_chunking_service() 실행
## 7. 4개 객체를 DocumentService는에 주입한다.
## 8. 완성된 DocumentService는를 API 함수에 전달한다.'

## 20260710 Embedding Service 추가
## get_openai_client()
## ↓
## OpenAIClient 생성
## ↓
## get_embedding_service()
## ↓
## EmbeddingService 생성
## ↓
## get_document_service()
## ↓
## DocumentService에 EmbeddingService 주입
def get_document_service(
    document_repository: DocumentRepository = Depends(
        get_document_repository
    ),
    document_chunk_repository: DocumentChunkRepository = Depends(
        get_document_chunk_repository
    ),
    text_extraction_service: TextExtractionService = Depends(
        get_text_extraction_service
    ),
    text_chunking_service: TextChunkingService = Depends(
        get_text_chunking_service
    ),
    ## 20260710 embedding service 추가
    embedding_service: EmbeddingService = Depends(
        get_embedding_service
    ),
):
    return DocumentService(
        document_repository=document_repository,
        document_chunk_repository=document_chunk_repository,
        text_extraction_service=text_extraction_service,
        text_chunking_service=text_chunking_service,
        embedding_service=embedding_service,
    )