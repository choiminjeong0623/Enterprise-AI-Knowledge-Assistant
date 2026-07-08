from fastapi import APIRouter, Depends, UploadFile, File

from app.dependencies.auth import get_current_user
from app.dependencies.document import get_document_service
from app.schemas.document import (
    DocumentChunkResponse,
    DocumentResponse,
    DocumentUploadResponse,
)
from app.services.document_service import DocumentService

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service),
):
    return await document_service.upload_document(
        user_id=current_user.id,
        file=file,
    )


@router.get("", response_model=list[DocumentResponse])
def get_documents(
    current_user=Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service),
):
    return document_service.get_documents(
        user_id=current_user.id,
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