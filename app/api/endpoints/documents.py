from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.db.models.knowledge_document import KnowledgeDocument
from app.db.session import get_db
from app.schemas.knowledge_document import (
    KnowledgeDocumentResponse,
    KnowledgeDocumentUpdate,
)


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


STORAGE_DIR = Path("data/storage")
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".docx"}


@router.post(
    "",
    response_model=KnowledgeDocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_document(
    title: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    extension = Path(file.filename or "").suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF, TXT, and DOCX files are allowed",
        )

    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File name is required",
        )

    file_path = STORAGE_DIR / file.filename

    if file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A file with this name already exists",
        )

    with file_path.open("wb") as destination:
        destination.write(file.file.read())

    document = KnowledgeDocument(
        title=title,
        file_name=file.filename,
        file_path=str(file_path),
        is_approved=False,
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return document


@router.get(
    "",
    response_model=list[KnowledgeDocumentResponse],
)
def list_documents(
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    documents = db.scalars(
        select(KnowledgeDocument).order_by(KnowledgeDocument.id)
    ).all()

    return documents


@router.get(
    "/{document_id}",
    response_model=KnowledgeDocumentResponse,
)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    document = db.get(KnowledgeDocument, document_id)

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    return document


@router.patch(
    "/{document_id}",
    response_model=KnowledgeDocumentResponse,
)
def update_document(
    document_id: int,
    data: KnowledgeDocumentUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    document = db.get(KnowledgeDocument, document_id)

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    update_data = data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(document, field, value)

    db.commit()
    db.refresh(document)

    return document


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    document = db.get(KnowledgeDocument, document_id)

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    file_path = Path(document.file_path)

    if file_path.exists():
        file_path.unlink()

    db.delete(document)
    db.commit()

    return None