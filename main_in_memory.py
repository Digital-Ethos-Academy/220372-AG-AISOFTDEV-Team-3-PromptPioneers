from fastapi import FastAPI, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


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
# IN-MEMORY DATABASE
# ============================================================================

# Global counter for ID generation
_file_attachment_id_counter = 1

def generate_id() -> int:
    """Generate a unique ID for a new file attachment."""
    global _file_attachment_id_counter
    new_id = _file_attachment_id_counter
    _file_attachment_id_counter += 1
    return new_id


# In-memory database: list of dictionaries
file_attachments_db: List[dict] = [
    {
        "id": generate_id(),
        "conversation_id": 1,
        "original_filename": "requirements.txt",
        "file_type": "txt",
        "file_size": 2048,
        "storage_path": "/uploads/conv_1/requirements_20251105_120000.txt",
        "extracted_text": "User should be able to upload files\nSystem should process markdown files\nSupport for Word documents required",
        "status": "processed",
        "metadata": '{"upload_source": "web_ui", "user_agent": "Mozilla/5.0"}',
        "created_at": datetime(2025, 11, 5, 12, 0, 0),
        "updated_at": datetime(2025, 11, 5, 12, 5, 0)
    },
    {
        "id": generate_id(),
        "conversation_id": 1,
        "original_filename": "product_spec.md",
        "file_type": "md",
        "file_size": 15360,
        "storage_path": "/uploads/conv_1/product_spec_20251105_130000.md",
        "extracted_text": "# Product Specification\n\n## Overview\nThis document outlines the core features...",
        "status": "processed",
        "metadata": '{"upload_source": "api", "version": "1.0"}',
        "created_at": datetime(2025, 11, 5, 13, 0, 0),
        "updated_at": datetime(2025, 11, 5, 13, 2, 30)
    },
    {
        "id": generate_id(),
        "conversation_id": 2,
        "original_filename": "initial_notes.docx",
        "file_type": "docx",
        "file_size": 45056,
        "storage_path": "/uploads/conv_2/initial_notes_20251105_140000.docx",
        "extracted_text": None,
        "status": "processing",
        "metadata": None,
        "created_at": datetime(2025, 11, 5, 14, 0, 0),
        "updated_at": datetime(2025, 11, 5, 14, 0, 0)
    }
]


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def find_file_attachment_by_id(file_id: int) -> Optional[dict]:
    """Find a file attachment by ID in the in-memory database."""
    return next((item for item in file_attachments_db if item["id"] == file_id), None)


def find_file_attachments_by_conversation(conversation_id: int) -> List[dict]:
    """Find all file attachments for a specific conversation."""
    return [item for item in file_attachments_db if item["conversation_id"] == conversation_id]


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
async def health_check():
    """
    Health check endpoint to verify API is operational.
    Returns status and database information.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": {
            "type": "in-memory",
            "file_attachments_count": len(file_attachments_db)
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
async def create_file_attachment(file_attachment: FileAttachmentCreate):
    """
    Create a new file attachment.
    
    Accepts file attachment details and returns the created resource
    with generated ID and timestamps.
    """
    # Create new record with generated ID and timestamps
    now = datetime.now()
    new_attachment = {
        "id": generate_id(),
        **file_attachment.model_dump(),
        "created_at": now,
        "updated_at": now
    }
    
    # Add to in-memory database
    file_attachments_db.append(new_attachment)
    
    return FileAttachmentResponse(**new_attachment)


@app.get(
    "/file-attachments/",
    response_model=List[FileAttachmentResponse],
    tags=["File Attachments"]
)
async def list_file_attachments(
    conversation_id: Optional[int] = Query(None, description="Filter by conversation ID")
):
    """
    List all file attachments with optional filtering.
    
    Can be filtered by conversation_id to retrieve attachments
    for a specific conversation.
    """
    if conversation_id is not None:
        filtered = find_file_attachments_by_conversation(conversation_id)
        return [FileAttachmentResponse(**item) for item in filtered]
    
    return [FileAttachmentResponse(**item) for item in file_attachments_db]


@app.get(
    "/file-attachments/{file_id}",
    response_model=FileAttachmentResponse,
    tags=["File Attachments"]
)
async def get_file_attachment(file_id: int):
    """
    Get a specific file attachment by ID.
    
    Returns the file attachment details if found, otherwise raises 404 error.
    """
    attachment = find_file_attachment_by_id(file_id)
    
    if attachment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File attachment with id {file_id} not found"
        )
    
    return FileAttachmentResponse(**attachment)


@app.put(
    "/file-attachments/{file_id}",
    response_model=FileAttachmentResponse,
    tags=["File Attachments"]
)
async def update_file_attachment(file_id: int, file_attachment: FileAttachmentCreate):
    """
    Fully update an existing file attachment.
    
    Replaces all fields of the file attachment with the provided values.
    Returns 404 if the file attachment doesn't exist.
    """
    attachment = find_file_attachment_by_id(file_id)
    
    if attachment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File attachment with id {file_id} not found"
        )
    
    # Update all fields except id and created_at
    attachment.update({
        **file_attachment.model_dump(),
        "updated_at": datetime.now()
    })
    
    return FileAttachmentResponse(**attachment)


@app.patch(
    "/file-attachments/{file_id}",
    response_model=FileAttachmentResponse,
    tags=["File Attachments"]
)
async def partial_update_file_attachment(file_id: int, file_attachment: FileAttachmentUpdate):
    """
    Partially update an existing file attachment.
    
    Only updates the fields provided in the request body.
    Returns 404 if the file attachment doesn't exist.
    """
    attachment = find_file_attachment_by_id(file_id)
    
    if attachment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File attachment with id {file_id} not found"
        )
    
    # Update only provided fields
    update_data = file_attachment.model_dump(exclude_unset=True)
    if update_data:
        attachment.update({
            **update_data,
            "updated_at": datetime.now()
        })
    
    return FileAttachmentResponse(**attachment)


@app.delete(
    "/file-attachments/{file_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["File Attachments"]
)
async def delete_file_attachment(file_id: int):
    """
    Delete a file attachment.
    
    Removes the file attachment from the database.
    Returns 204 No Content on success, 404 if not found.
    """
    attachment = find_file_attachment_by_id(file_id)
    
    if attachment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File attachment with id {file_id} not found"
        )
    
    file_attachments_db.remove(attachment)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main_in_memory:app", host="0.0.0.0", port=8000, reload=True)