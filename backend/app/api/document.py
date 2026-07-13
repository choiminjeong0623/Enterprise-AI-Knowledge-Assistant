from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Query,
    UploadFile,
)

from app.dependencies.auth import get_current_user
from app.dependencies.document import get_document_service
from app.schemas.document import (
    DocumentChunkResponse,
    DocumentDeleteResponse,
    DocumentResponse,
    DocumentSearchResponse,
    DocumentUploadResponse,
)
from app.services.document_service import DocumentService
from app.tasks.document_processing_task import (
    process_document,
)

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=202,
)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    document_service: DocumentService = Depends(
        get_document_service
    ),
):
    document = await document_service.upload_document(
        user_id=current_user.id,
        file=file,
    )

    background_tasks.add_task(
        process_document,
        document.id,
    )

    return {
        "id": document.id,
        "user_id": document.user_id,
        "original_filename": document.original_filename,
        "stored_filename": document.stored_filename,
        "content_type": document.content_type,
        "status": document.status,
        "error_message": document.error_message,
        "processed_at": document.processed_at,
        "created_at": document.created_at,
        "chunk_count": 0,
    }


@router.get("", response_model=list[DocumentResponse])
def get_documents(
    current_user=Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service),
):
    return document_service.get_documents(
        user_id=current_user.id,
    )

@router.get("/search", response_model=list[DocumentSearchResponse])
def search_document_chunks(
    query: str = Query(..., min_length=1),
    limit: int = Query(5, ge=1, le=20), ## limit 기본값은 5, 최소값은 1, 최대값은 20
    current_user=Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service),
):
    return document_service.search_document_chunks(
        user_id=current_user.id,
        query=query,
        limit=limit,
    )

@router.get("/{document_id}/chunks", response_model=list[DocumentChunkResponse])
def get_document_chunks(
    document_id: int,
    current_user=Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service),
):
    return document_service.get_document_chunks(
        document_id=document_id,
        user_id=current_user.id,
    )

@router.delete("/{document_id}", response_model=DocumentDeleteResponse)
def delete_document(
    document_id: int,
    current_user=Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service),
):
    return document_service.delete_document(
        document_id=document_id,
        user_id=current_user.id,
    )

