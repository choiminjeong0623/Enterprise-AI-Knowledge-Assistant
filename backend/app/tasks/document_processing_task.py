from pathlib import Path

from app.clients.logger import logger
from app.clients.openai_client import OpenAIClient
from app.database.database import SessionLocal
from app.repositories.document_chunk_repository import (
    DocumentChunkRepository,
)
from app.repositories.document_repository import (
    DocumentRepository,
)
from app.services.embedding_service import EmbeddingService
from app.services.text_chunking_service import (
    TextChunkingService,
)
from app.services.text_extraction_service import (
    TextExtractionService,
)


def process_document(
    document_id: int,
) -> None:
    ## API 요청의 Sesison을 재사용하면 문제가 생길수도 있으므로
    ## Task 내부에서 독립적으로 생성한다.
    db = SessionLocal()
    ## 새로운 DB 생성
    document_repository = DocumentRepository(
        db=db,
    )

    document_chunk_repository = (
        DocumentChunkRepository(
            db=db,
        )
    )

    text_extraction_service = (
        TextExtractionService()
    )

    text_chunking_service = (
        TextChunkingService()
    )

    openai_client = OpenAIClient()

    embedding_service = EmbeddingService(
        client=openai_client,
    )

    document = None

    try:
        ## id로 Document 조회
        document = (
            document_repository.find_by_id(
                document_id=document_id,
            )
        )

        if document is None:
            logger.error(
                "Background document processing failed. "
                "Document not found. document_id=%s",
                document_id,
            )

            return

        ## PROCESSING으로 변경
        document_repository.mark_as_processing(
            document=document,
        )

        file_path = (
            Path("uploads/documents")
            / document.stored_filename
        )

        ## 저장된 파일 존재 여부 확인
        if not file_path.exists():
            raise FileNotFoundError(
                f"Stored document file not found: "
                f"{file_path}"
            )

        ## 텍스트 추출
        extracted_text = (
            text_extraction_service.extract_text(
                filename=document.original_filename,
                file_path=str(file_path),
            )
        )

        if not extracted_text.strip():
            raise ValueError(
                "No text could be extracted "
                "from the document."
            )

        ## Chunking
        chunks = (
            text_chunking_service.split_text(
                text=extracted_text,
            )
        )

        if not chunks:
            raise ValueError(
                "No chunks could be created "
                "from the document."
            )
        
        ## Batch Embedding 
        embeddings = (
            embedding_service.create_embeddings(
                texts=chunks,
            )
        )

        if len(chunks) != len(embeddings):
            raise ValueError(
                "The number of chunks and "
                "embeddings must be equal."
            )

        ## Chunk 저장
        document_chunk_repository.create_many(
            document_id=document.id,
            chunks=chunks,
            embeddings=embeddings,
        )

        ## COMPLETED로 변경
        document_repository.mark_as_completed(
            document=document,
        )

        logger.info(
            "Background document processing completed. "
            "document_id=%s chunk_count=%s",
            document.id,
            len(chunks),
        )

    except Exception as error:
        db.rollback()

        logger.exception(
            "Background document processing failed. "
            "document_id=%s",
            document_id,
        )

        if document is not None:
            try:
                refreshed_document = (
                    document_repository.find_by_id(
                        document_id=document_id,
                    )
                )

                if refreshed_document is not None:
                    document_repository.mark_as_failed(
                        document=refreshed_document,
                        error_message=(
                            _build_safe_error_message(
                                error=error,
                            )
                        ),
                    )

            except Exception:
                db.rollback()

                logger.exception(
                    "Failed to save document FAILED status. "
                    "document_id=%s",
                    document_id,
                )

    finally:
        db.close()

## 외부 API 오류에는 긴 Stack Trace, 민감정보가 있을 수 있으므로
## 짧은 원인만 저장하고, 자세한 Stack Trace는 서버 로그에 남긴다.
def _build_safe_error_message(
    error: Exception,
) -> str:
    error_message = str(error).strip()

    if not error_message:
        error_message = error.__class__.__name__

    return error_message[:500]