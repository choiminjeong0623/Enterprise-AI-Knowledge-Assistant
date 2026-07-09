import os   ## 폴더 생성, 경로 처리 등에 쓰이는 파이썬 표준 라이브러리이다.
from pathlib import Path    ## 파일 확장자를 얻기 위함.
from uuid import uuid4  ## 고유한 파일명을 만들기 위해 사용한다. uuid4() : 랜덤한 32비트 문자열 생성

from fastapi import HTTPException, UploadFile

from app.repositories.document_chunk_repository import DocumentChunkRepository
from app.repositories.document_repository import DocumentRepository
from app.services.text_chunking_service import TextChunkingService
from app.services.text_extraction_service import TextExtractionService

## 문서 업로드의 전체 비즈니스 로직을 담당한다.
## 파일 업로드
## → 확장자 검사
## → 서버에 파일 저장
## → 텍스트 추출
## → chunk 분할
## → documents 테이블 저장
## → document_chunks 테이블 저장
## → 결과 반환
class DocumentService:
    def __init__(
        self,
        document_repository: DocumentRepository,
        document_chunk_repository: DocumentChunkRepository,
        text_extraction_service: TextExtractionService,
        text_chunking_service: TextChunkingService,
    ):
        ## DocumentService는 아래 객체들을 주입받아서 사용한다.
        self.document_repository = document_repository  ## documents 테이블 저장/조회
        self.document_chunk_repository = document_chunk_repository  ## document_chunks 테이블/저장 조회
        self.text_extraction_service = text_extraction_service  ## PDF/TXT에서 텍스트 추출
        self.text_chunking_service = text_chunking_service  ## 긴 텍스트를 chunk로 분할

    ## 문서를 업로드하는 핵심 함수이다.
    ## async def인 이유는 FastAPI의 UploadFile.read()가 비동기 방식이기 때문이다.
    async def upload_document(
        self,
        user_id: int,
        file: UploadFile,
    ):
        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="Filename is required.",
            )

        suffix = Path(file.filename).suffix.lower() ## 파일 확장자를 구한다.

        if suffix not in [".pdf", ".txt"]:
            raise HTTPException(
                status_code=400,
                detail="Only PDF and TXT files are supported.",
            )

        upload_dir = "uploads/documents"
        os.makedirs(upload_dir, exist_ok=True)  ## 폴더가 없으면 생성한다.
                                                ## exist_ok=True 이미 폴더가 있어도 에러를 내지 말라는 뜻.

        stored_filename = f"{uuid4()}{suffix}"  ## 서버에 저장할 파일명을 만든다.
                                                ## 원본 파일명 : report.pdf
                                                ## 저장 파일명 : 32ㅂ트 랜덤한 문자열.확장자
        ## 폴더 경로와 파일명을 합쳐 전체 저장 경로를 만든다.
        ## 전체 경로 : uploads/documents/stored_filename
        file_path = os.path.join(upload_dir, stored_filename)

        ## 업로드된 파일의 실제 내용을 읽는다.
        content = await file.read()

        ## 읽은 파일 내용을 서버 디스크에 저장한다.
        ## w(write) : 쓰기 모드
        ## b(binary) : 바이너리 모드
        ## PDF, TXT의 텍스트를 원본 바이트 그래도 저장하기 위해서이다.
        with open(file_path, "wb") as saved_file:
            saved_file.write(content)

        ## 저장된 파일에서 텍스트를 추출한다.
        ## text_extraction_service.extract_text()를 사용한다.
        ## PDF면 _extract_pdf(), _extract_txt()가 실행된다.
        extracted_text = self.text_extraction_service.extract_text(
            file=file,
            file_path=file_path,
        )

        ## 추출된 텍스트가 비어 있는지 확인한다.
        if not extracted_text.strip():
            raise HTTPException(
                status_code=400,
                detail="No text could be extracted from the document.",
            )

        ## 추출한 텍스트를 여러 chunk로 나눈다.
        ## text_chunking_service.split_text()를 사용한다.
        chunks = self.text_chunking_service.split_text(
            text=extracted_text,
        )

        if not chunks:
            raise HTTPException(
                status_code=400,
                detail="No chunks could be created from the document.",
            )

        ## 문서 메타데이터를 documents 테이블에 저장한다.
        ## document_repository.create()를 사용한다.
        document = self.document_repository.create(
            user_id=user_id,    ## 업로드한 사용자 ID
            original_filename=file.filename,    ## 사용자가 업로드한 원래 파일명
            stored_filename=stored_filename,    ## 서버에 저장된 고유 파일명
            content_type=file.content_type,     ## 파일 MIME 타입
        )

        ## 분할된 chunk들을 document_chunks 테이블에 저장한다.
        ## document_chunk_repository.create_many()를 사용한다.
        document_chunks = self.document_chunk_repository.create_many(
            document_id=document.id,
            chunks=chunks,
        )

        return {
            "document": document,
            "chunk_count": len(document_chunks),
        }
    ## 사용자가 업로드한 문서 목록을 조회한다.
    ## document_repository.find_by_user_id()를 사용한다.
    ## 이를 "Repository에 조회를 위임한다."라고 한다.
    ## 즉, Service가 직접 SQLAlchemy query를 쓰지 않는다.
    def get_documents(
        self,
        user_id: int,
    ):
        return self.document_repository.find_by_user_id(
            user_id=user_id,
        )
    ## 특정 문서의 chunk 목록을 조회한다.
    ## 단, 아무 문서나 조회하면 안 되고, 현재 로그인한 사용자의 문서인지 확인해야 한다.
    def get_document_chunks(
        self,
        document_id: int,
        user_id: int,
    ):
        document = self.document_repository.find_by_id_and_user_id(
            document_id=document_id,
            user_id=user_id,
        )

        if document is None:
            raise HTTPException(
                status_code=404,
                detail="Document not found.",
            )

        ## 문서가 현재 사용자 소유임이 확인되면 chunk 목록을 반환한다.
        return self.document_chunk_repository.find_by_document_id(
            document_id=document_id,
        )

    ## API에서 받은 검색어를 검증하고, Repository에 실제 검색을 요청한다.
    def search_document_chunks(
        self,
        user_id: int,
        query: str,
        limit: int = 5,
    ):
        cleaned_query = query.strip()   ## 검색어 앞뒤의 공백을 제거

        if not cleaned_query:
            raise HTTPException(
                status_code=400,
                detail="Search query is required.",
            )

        if limit < 1:
            raise HTTPException(
                status_code=400,
                detail="Limit must be greater than 0.",
            )

        if limit > 20:
            limit = 20
        
        search_results = self.document_chunk_repository.search_by_keyword(
            user_id=user_id,
            query=cleaned_query,
            limit=limit,
        )

        results = []

        for chunk, document in search_results:
            results.append(
                {
                    "id": chunk.id,
                    "document_id": chunk.document_id,
                    "document_filename": document.original_filename,    ## 20260709 original filename 추가
                    "chunk_index": chunk.chunk_index,
                    "content": chunk.content,
                    "created_at": chunk.created_at,
                }
            )

        return results

    ## 검색된 chunks를 아래와 같은 형태로 바꾼다.(향후 GPT Prompt에 사용)
    ## [Context 1]
    ## Document ID: 1
    ## Chunk Index: 0
    ## Content:
    ## 문서 내용...
    def build_context_from_chunks(
        self,
        user_id: int,
        query: str,
        limit: int = 5,
    ) -> str:
        chunks = self.search_document_chunks(
            user_id=user_id,
            query=query,
            limit=limit,
        )

        if not chunks:
            return {
                "context": "",
                "sources": [],
            }

        context_lines = []
        sources = []

        for index, chunk in enumerate(chunks, start=1):
            context_lines.append(
                f"[Context {index}]\n"
                f"Document ID: {chunk['document_id']}\n"
                f"Filename: {chunk['document_filename']}\n"
                f"Chunk Index: {chunk['chunk_index']}\n"
                f"Content:\n{chunk['content']}"
            )

            sources.append(
                {
                    "document_id": chunk["document_id"],
                    "document_filename": chunk["document_filename"],
                    "chunk_index": chunk["chunk_index"],
                    "content": chunk["content"],
                }
            )

        return {
            "context": "\n\n".join(context_lines),
            "sources": sources,
        }