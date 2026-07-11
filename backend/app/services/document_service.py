import os   ## 폴더 생성, 경로 처리 등에 쓰이는 파이썬 표준 라이브러리이다.
from pathlib import Path    ## 파일 확장자를 얻기 위함.
from uuid import uuid4  ## 고유한 파일명을 만들기 위해 사용한다. uuid4() : 랜덤한 32비트 문자열 생성

from fastapi import HTTPException, UploadFile

from app.clients.config import settings
from app.repositories.document_chunk_repository import DocumentChunkRepository
from app.repositories.document_repository import DocumentRepository
from app.services.text_chunking_service import TextChunkingService
from app.services.text_extraction_service import TextExtractionService
from app.services.embedding_service import EmbeddingService

import json
import math

## 문서 업로드의 전체 비즈니스 로직을 담당한다.
## 파일 업로드
## → 확장자 검사
## → 서버에 파일 저장
## → 텍스트 추출
## → chunk 분할
## → Embedding 생성(20260710 추가)
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
        embedding_service : EmbeddingService
    ):
        ## DocumentService는 아래 객체들을 주입받아서 사용한다.
        self.document_repository = document_repository  ## documents 테이블 저장/조회
        self.document_chunk_repository = document_chunk_repository  ## document_chunks 테이블/저장 조회
        self.text_extraction_service = text_extraction_service  ## PDF/TXT에서 텍스트 추출
        self.text_chunking_service = text_chunking_service  ## 긴 텍스트를 chunk로 분할
        self.embedding_service=embedding_service    

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

        suffix = Path(file.filename).suffix.lower() ## 파일 확장자를 소문자로 구한다.

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
                                                ## 저장 파일명 : 랜덤 UUID.pdf
        ## 폴더 경로와 파일명을 합쳐 전체 저장 경로를 만든다.
        ## 전체 경로 : uploads/documents/stored_filename
        file_path = os.path.join(upload_dir, stored_filename)

        ## 업로드된 파일의 실제 바이트 데이터를 읽는다.
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
        ## 모든 Chunk 문자열을 Embedding Vector로 변환한다.
        ## chunks:
        ## list[str]
        ## embeddings:
        ## list[list[float]]
        embeddings = (
            self.embedding_service.create_embeddings(
                texts=chunks,
            )
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
        ## chunks와 embeddings를 함께 저장한다.
        ## document_chunk_repository.create_many()를 사용한다.
        document_chunks = self.document_chunk_repository.create_many(
            document_id=document.id,
            chunks=chunks,
            embeddings=embeddings
        )

        return {
            "document": document,
            "chunk_count": len(document_chunks),
        }
    ## 사용자가 업로드한 문서 목록을 조회한다.
    ## document_repository.find_with_chunk_count_by_user_id()를 사용한다.
    ## 이를 "Repository에 조회를 위임한다."라고 한다.
    ## 즉, Service가 직접 SQLAlchemy query를 쓰지 않는다.
    def get_documents(
        self,
        user_id: int,
    ):
        document_rows = (
            self.document_repository
            .find_with_chunk_count_by_user_id(
                user_id=user_id,
            )
        )

        documents = []

        for document, chunk_count in document_rows:
            documents.append(
                {
                    "id": document.id,
                    "user_id": document.user_id,
                    "original_filename": (
                        document.original_filename
                    ),
                    "stored_filename": (
                        document.stored_filename
                    ),
                    "content_type": (
                        document.content_type
                    ),
                    "chunk_count": (
                        chunk_count
                    ),
                    "created_at": (
                        document.created_at
                    ),
                }
            )

        return documents
    
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
        cleaned_query = query.strip()

        if not cleaned_query:
            raise HTTPException(
                status_code=400,
                detail="Search query is required.",
            )

        if limit < 1:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Limit must be greater than 0."
                ),
            )

        if limit > 20:
            limit = 20

        ## similarity_threshold 설정            
        similarity_threshold = (
            settings.VECTOR_SEARCH_SIMILARITY_THRESHOLD
        )

        ## 사용자가 입력한검색어나 채팅 질문을 Embedding으로 반환
        query_embedding = (
            self.embedding_service.create_embedding(
                text=cleaned_query,
            )
        )

        ## 사용자ID로 저장된 Chunk를 조회한다.
        stored_chunks = (
            self.document_chunk_repository
            .find_all_with_embeddings_by_user_id(
                user_id=user_id,
            )
        )

        scored_results = []

        for chunk, document in stored_chunks:
            try:
                ## SQLite Text 컬럼에 저장된 임베딩 문자열을 Python 리스트로 복원한다.
                chunk_embedding = json.loads(
                    chunk.embedding
                )
            except (
                ## embedding이 올바른 문자열이 아님
                ## JSON 형식이 깨져있음
                ## NULL 또는 잘못된 타입임
                TypeError,
                json.JSONDecodeError,
            ):
                continue

            ## chunk_embedding가 list 타입이 아닌 경우 반복 중단
            if not isinstance(
                chunk_embedding,
                list,
            ):
                continue

            try:
                similarity = (
                    self.calculate_cosine_similarity(
                        vector_a=query_embedding,
                        vector_b=chunk_embedding,
                    )
                )
            except (
                TypeError,
                ValueError,
            ):
                continue
            
            ## Threshold 미만 제거
            if similarity < similarity_threshold:
                continue

            scored_results.append(
                {
                    "id": chunk.id,
                    "document_id": chunk.document_id,
                    "document_filename": (
                        document.original_filename
                    ),
                    "chunk_index": chunk.chunk_index,
                    "content": chunk.content,
                    "similarity": similarity,       ## 유사도 점수 저장
                    "created_at": chunk.created_at,
                }
            )


        scored_results.sort(
            key=lambda result: result["similarity"],    ## 정렬 기준을 지정한다.
            reverse=True,   ## 큰 값부터 작은 값 순서로 정렬한다.
        )

        for result in scored_results:
            print(
                "VECTOR SEARCH:",
                result["chunk_index"],
                round(result["similarity"], 4),
                result["content"][:50],
            )
        return scored_results[:limit]   ## limit 개수만큼 반환

    # 검색된 Chunk를 GPT Prompt의 Context와
    # Source 목록으로 변환한다.
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
                # f"Similarity: "
                # f"{chunk['similarity']:.4f}\n"
                f"Content:\n{chunk['content']}"
            )

            sources.append(
                {
                    "document_id": chunk["document_id"],
                    "document_filename": chunk["document_filename"],
                    "chunk_index": chunk["chunk_index"],
                    "similarity" : chunk["similarity"],
                    "content": chunk["content"],
                }
            )

        return {
            "context": "\n\n".join(context_lines),
            "sources": sources,
        }
    
    ## 코사인 유사도 함수
    ## 두 임베딩 벡터가 의미상 얼마나 유사한지 계산한다.
    ## 1에 가까울수록 유사하다.
    ## 0에 가까울수록 관련성이 낮다
    ## 음수일 경우 반대방향이다.
    def calculate_cosine_similarity(
        self,
        vector_a: list[float],
        vector_b: list[float],
    ) -> float:
        ## 두 벡터의 길이는 같아야 한다.
        ## 길이가 다르면 각 좌표를 대응시킬 수 없으므로 계산하지 않는다.
        ## 같은 모델을 사용했다면 정상적으로 길이가 동일하다.
        if len(vector_a) != len(vector_b):
            raise ValueError(
                "Embedding vector dimensions must be equal."
            )

        if not vector_a or not vector_b:
            return 0.0

        ## 내적 계산
        dot_product = sum(
            value_a * value_b
            for value_a, value_b in zip(    ## zip(): 두 리스트의 동일한 위치 값을 한 쌍으로 묶는다.
                vector_a,
                vector_b,
            )
        )

        ## 벡터 크기 계산
        magnitude_a = math.sqrt(
            sum(
                value * value
                for value in vector_a
            )
        )

        magnitude_b = math.sqrt(
            sum(
                value * value
                for value in vector_b
            )
        )

        if magnitude_a == 0 or magnitude_b == 0:
            return 0.0

        ## 최종 유사도 반환 = 두 벡터의 내적 ÷ 두 벡터 크기의 곱
        return dot_product / (
            magnitude_a * magnitude_b
        )

    def delete_document(
        self,
        document_id: int,
        user_id: int,
    ):
        document = (
            self.document_repository.find_by_id_and_user_id(
                document_id=document_id,
                user_id=user_id,
            )
        )

        if document is None:    ## 문서가 없거나 다른 사용자 소유이면 404 에러 발생
            raise HTTPException(
                status_code=404,
                detail="Document not found.",
            )

        ## 실제 파일 경로 생성
        file_path = Path(
            "uploads/documents"
        ) / document.stored_filename

        try:
            if file_path.exists():
                file_path.unlink()  ## 파일이 존재할 때만 삭제
        except OSError as error:
            raise HTTPException(
                status_code=500,
                detail=(
                    "Failed to delete the stored "
                    "document file."
                ),
            ) from error

        ## DB 삭제
        self.document_repository.delete(
            document=document,
        )

        return {
            "message": "Document deleted successfully.",
            "document_id": document_id,
        }