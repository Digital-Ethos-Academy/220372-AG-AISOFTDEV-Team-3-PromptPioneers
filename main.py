from fastapi import FastAPI, HTTPException, status, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum
from sqlalchemy.orm import Session
from database import get_db, init_db
from models import FileAttachment as FileAttachmentModel


# ============================================================================
# ENUMS
# ============================================================================

class FileTypeEnum(str, Enum):
    """Allowed file types for attachments."""
    txt = "txt"
    md = "md"
    docx = "docx"


class FileAttachmentStatus(str, Enum):
    """Status of file attachment."""
    uploaded = "uploaded"
    processing = "processing"
    processed = "processed"
    failed = "failed"


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class FileAttachmentBase(BaseModel):
    """
    Base model for file attachment with common fields.
    Used as foundation for create and update operations.
    """
    conversation_id: int = Field(..., gt=0, description="ID of the conversation this file belongs to")
    original_filename: str = Field(..., min_length=1, max_length=255, description="Original name of the uploaded file")
    file_type: FileTypeEnum = Field(..., description="Type of the file (txt, md, docx)")
    file_size: int = Field(..., gt=0, description="Size of the file in bytes")
    storage_path: str = Field(..., min_length=1, description="Path where the file is stored")
    extracted_text: Optional[str] = Field(None, description="Text extracted from the file")
    status: FileAttachmentStatus = Field(default=FileAttachmentStatus.uploaded, description="Current status of the file")
    metadata: Optional[str] = Field(None, description="Additional metadata in JSON format")

    @field_validator('file_size')
    @classmethod
    def validate_file_size(cls, v: int) -> int:
        """Validate file size is reasonable (max 50MB)."""
        max_size = 50 * 1024 * 1024  # 50MB
        if v > max_size:
            raise ValueError(f'File size must not exceed {max_size} bytes (50MB)')
        return v


class FileAttachmentCreate(FileAttachmentBase):
    """
    Model for creating a new file attachment.
    Inherits all fields from base model.
    """
    pass


class FileAttachmentUpdate(BaseModel):
    """
    Model for updating an existing file attachment.
    All fields are optional to support partial updates.
    """
    conversation_id: Optional[int] = Field(None, gt=0)
    original_filename: Optional[str] = Field(None, min_length=1, max_length=255)
    file_type: Optional[FileTypeEnum] = None
    file_size: Optional[int] = Field(None, gt=0)
    storage_path: Optional[str] = Field(None, min_length=1)
    extracted_text: Optional[str] = None
    status: Optional[FileAttachmentStatus] = None
    metadata: Optional[str] = None

    @field_validator('file_size')
    @classmethod
    def validate_file_size(cls, v: Optional[int]) -> Optional[int]:
        """Validate file size if provided."""
        if v is not None:
            max_size = 50 * 1024 * 1024  # 50MB
            if v > max_size:
                raise ValueError(f'File size must not exceed {max_size} bytes (50MB)')
        return v


class FileAttachmentResponse(FileAttachmentBase):
    """
    Model for file attachment API responses.
    Includes system-generated fields like id and timestamps.
    """
    id: int = Field(..., description="Unique identifier for the file attachment")
    created_at: datetime = Field(..., description="Timestamp when the file was uploaded")
    updated_at: datetime = Field(..., description="Timestamp when the file was last updated")

    class Config:
        from_attributes = True


# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title="AI-Powered Requirement Analyzer API",
    description="REST API for managing file attachments in the PRD generation system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

# Initialize database tables on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database tables when application starts."""
    init_db()


# ============================================================================
# ROOT & HEALTH ENDPOINTS
# ============================================================================

@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint providing API information.
    Returns basic details about the API and available endpoints.
    """
    return {
        "name": "AI-Powered Requirement Analyzer API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "file_attachments": "/file-attachments/"
        }
    }


@app.get("/health", tags=["Health"])
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint to verify API is operational.
    Returns status and database information.
    """
    try:
        # Test database connection by counting file attachments
        count = db.query(FileAttachmentModel).count()
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": {
                "type": "sqlite",
                "connected": True,
                "file_attachments_count": count
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "database": {
                "type": "sqlite",
                "connected": False,
                "error": str(e)
            }
        }


# ============================================================================
# FILE ATTACHMENT CRUD ENDPOINTS
# ============================================================================

@app.post(
    "/file-attachments/",
    response_model=FileAttachmentResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["File Attachments"]
)
async def create_file_attachment(
    file_attachment: FileAttachmentCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new file attachment.
    
    Accepts file attachment details and returns the created resource
    with generated ID and timestamps.
    """
    # Create new FileAttachment model instance
    db_attachment = FileAttachmentModel(
        **file_attachment.model_dump()
    )
    
    # Add to database and commit
    db.add(db_attachment)
    db.commit()
    db.refresh(db_attachment)
    
    return db_attachment


@app.get(
    "/file-attachments/",
    response_model=List[FileAttachmentResponse],
    tags=["File Attachments"]
)
async def list_file_attachments(
    conversation_id: Optional[int] = Query(None, description="Filter by conversation ID"),
    db: Session = Depends(get_db)
):
    """
    List all file attachments with optional filtering.
    
    Can be filtered by conversation_id to retrieve attachments
    for a specific conversation.
    """
    query = db.query(FileAttachmentModel)
    
    if conversation_id is not None:
        query = query.filter(FileAttachmentModel.conversation_id == conversation_id)
    
    return query.all()


@app.get(
    "/file-attachments/{file_id}",
    response_model=FileAttachmentResponse,
    tags=["File Attachments"]
)
async def get_file_attachment(file_id: int, db: Session = Depends(get_db)):
    """
    Get a specific file attachment by ID.
    
    Returns the file attachment details if found, otherwise raises 404 error.
    """
    attachment = db.query(FileAttachmentModel).filter(
        FileAttachmentModel.id == file_id
    ).first()
    
    if attachment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File attachment with id {file_id} not found"
        )
    
    return attachment


@app.put(
    "/file-attachments/{file_id}",
    response_model=FileAttachmentResponse,
    tags=["File Attachments"]
)
async def update_file_attachment(
    file_id: int,
    file_attachment: FileAttachmentCreate,
    db: Session = Depends(get_db)
):
    """
    Fully update an existing file attachment.
    
    Replaces all fields of the file attachment with the provided values.
    Returns 404 if the file attachment doesn't exist.
    """
    attachment = db.query(FileAttachmentModel).filter(
        FileAttachmentModel.id == file_id
    ).first()
    
    if attachment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File attachment with id {file_id} not found"
        )
    
    # Update all fields
    for key, value in file_attachment.model_dump().items():
        setattr(attachment, key, value)
    
    db.commit()
    db.refresh(attachment)
    
    return attachment


@app.patch(
    "/file-attachments/{file_id}",
    response_model=FileAttachmentResponse,
    tags=["File Attachments"]
)
async def partial_update_file_attachment(
    file_id: int,
    file_attachment: FileAttachmentUpdate,
    db: Session = Depends(get_db)
):
    """
    Partially update an existing file attachment.
    
    Only updates the fields provided in the request body.
    Returns 404 if the file attachment doesn't exist.
    """
    attachment = db.query(FileAttachmentModel).filter(
        FileAttachmentModel.id == file_id
    ).first()
    
    if attachment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File attachment with id {file_id} not found"
        )
    
    # Update only provided fields
    update_data = file_attachment.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(attachment, key, value)
    
    db.commit()
    db.refresh(attachment)
    
    return attachment


@app.delete(
    "/file-attachments/{file_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["File Attachments"]
)
async def delete_file_attachment(file_id: int, db: Session = Depends(get_db)):
    """
    Delete a file attachment.
    
    Removes the file attachment from the database.
    Returns 204 No Content on success, 404 if not found.
    """
    attachment = db.query(FileAttachmentModel).filter(
        FileAttachmentModel.id == file_id
    ).first()
    
    if attachment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File attachment with id {file_id} not found"
        )
    
    db.delete(attachment)
    db.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
