"""
AI-Powered Requirement Analyzer - Main API Module

This module provides REST API endpoints for managing file attachments
in the Product Requirements Document generation system.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

from fastapi import FastAPI, HTTPException, status, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from database import get_db, init_db
from models import FileAttachment as FileAttachmentModel
from install_dependencies import install_langgraph_dependencies

# Import RAG System
try:
    from rag_system import process_user_input_for_prd
    RAG_SYSTEM_AVAILABLE = True
    print("✓ RAG system imported successfully")
except ImportError as e:
    print(f"⚠ Warning: RAG system not available: {e}")
    RAG_SYSTEM_AVAILABLE = False


# ============================================================================
# ENUMS
# ============================================================================

class FileTypeEnum(str, Enum):
    """Enumeration of supported file types for document attachments."""
    TXT = "txt"
    MD = "md"
    DOCX = "docx"
    
    @classmethod
    def is_valid(cls, value: str) -> bool:
        """Check if a file type value is valid."""
        return value in cls._value2member_map_


class FileAttachmentStatus(str, Enum):
    """Enumeration of file attachment processing states."""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"
    
    @classmethod
    def is_valid(cls, value: str) -> bool:
        """Check if a status value is valid."""
        return value in cls._value2member_map_


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
    status: FileAttachmentStatus = Field(default=FileAttachmentStatus.UPLOADED, description="Current status of the file")
    additional_metadata: Optional[str] = Field(None, description="Additional metadata in JSON format")

    @field_validator('file_size')
    @classmethod
    def validate_file_size(cls, v: int) -> int:
        """Validate file size is within acceptable limits (max 50MB)."""
        MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB in bytes
        MIN_FILE_SIZE: int = 1  # Minimum 1 byte
        
        if v < MIN_FILE_SIZE:
            raise ValueError(f'File size must be at least {MIN_FILE_SIZE} byte')
        if v > MAX_FILE_SIZE:
            raise ValueError(
                f'File size must not exceed {MAX_FILE_SIZE:,} bytes '
                f'({MAX_FILE_SIZE // (1024 * 1024)}MB)'
            )
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
    additional_metadata: Optional[str] = None

    @field_validator('file_size')
    @classmethod
    def validate_file_size(cls, v: Optional[int]) -> Optional[int]:
        """Validate file size if provided (max 50MB)."""
        if v is not None:
            MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB in bytes
            MIN_FILE_SIZE: int = 1  # Minimum 1 byte
            
            if v < MIN_FILE_SIZE:
                raise ValueError(f'File size must be at least {MIN_FILE_SIZE} byte')
            if v > MAX_FILE_SIZE:
                raise ValueError(
                    f'File size must not exceed {MAX_FILE_SIZE:,} bytes '
                    f'({MAX_FILE_SIZE // (1024 * 1024)}MB)'
                )
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
# RAG SYSTEM MODELS
# ============================================================================

class PRDRequest(BaseModel):
    """Request model for PRD processing."""
    user_input: str = Field(..., min_length=1, max_length=5000, description="User's product idea description")
    conversation_history: Optional[List[Dict[str, str]]] = Field(default=[], description="Previous conversation messages")

class PRDResponse(BaseModel):
    """Response model for PRD processing."""
    success: bool = Field(..., description="Whether the processing was successful")
    prd_content: Dict[str, Any] = Field(..., description="Generated PRD content matching React app structure")
    clarifying_questions: List[str] = Field(..., description="Questions to improve the PRD")
    analysis: Dict[str, Any] = Field(..., description="Analysis of the user input")
    error_message: str = Field(default="", description="Error message if processing failed")
    processing_stage: str = Field(..., description="Current processing stage")


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
    """
    Initialize application on startup.
    
    1. Install required LangGraph dependencies
    2. Initialize database tables
    """
    print("\n" + "=" * 60)
    print("🚀 Starting AI-Powered Requirement Analyzer API")
    print("=" * 60)
    
    # Install LangGraph dependencies if missing
    try:
        install_langgraph_dependencies()
    except Exception as e:
        print(f"⚠ Warning: Failed to install some dependencies: {e}")
        print("The API will continue, but agent features may not work.")
    
    # Initialize database
    print("\n📊 Initializing database...")
    init_db()
    print("✓ Database initialized successfully")
    
    print("=" * 60)
    print("✓ Application startup complete!")
    print("=" * 60 + "\n")


# ============================================================================
# ROOT & HEALTH ENDPOINTS
# ============================================================================

@app.get("/", tags=["Root"])
async def root() -> dict[str, str | dict[str, str]]:
    """
    Root endpoint providing API information.
    
    Returns:
        Dictionary containing API name, version, status, and available endpoints.
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
async def health_check(
    db: Session = Depends(get_db)
) -> dict[str, str | dict[str, str | bool | int]]:
    """
    Health check endpoint to verify API and database operational status.
    
    Args:
        db: Database session injected via dependency.
        
    Returns:
        Dictionary containing health status, timestamp, and database information.
    """
    current_timestamp: str = datetime.now().isoformat()
    
    try:
        # Test database connection by counting file attachments
        count: int = db.query(FileAttachmentModel).count()
        return {
            "status": "healthy",
            "timestamp": current_timestamp,
            "database": {
                "type": "sqlite",
                "connected": True,
                "file_attachments_count": count
            }
        }
    except SQLAlchemyError as e:
        # Log the error for debugging (in production, use proper logging)
        return {
            "status": "unhealthy",
            "timestamp": current_timestamp,
            "database": {
                "type": "sqlite",
                "connected": False,
                "error": str(e)
            }
        }


# ============================================================================
# RAG SYSTEM ENDPOINTS
# ============================================================================

@app.post(
    "/api/process-prd",
    response_model=PRDResponse,
    tags=["RAG System"]
)
async def process_prd_input(request: PRDRequest) -> PRDResponse:
    """
    Process user input and generate PRD content using RAG system.
    
    This endpoint takes user product ideas and generates structured PRD content
    that matches the React frontend's expected data structure.
    
    Args:
        request: PRD request containing user input and conversation history
        
    Returns:
        PRDResponse with generated content, questions, and analysis
        
    Raises:
        HTTPException: If RAG system is not available or processing fails
    """
    if not RAG_SYSTEM_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="RAG system is not available. Please check server configuration."
        )
    
    try:
        # Process the user input using the RAG system
        result = process_user_input_for_prd(
            user_input=request.user_input,
            conversation_history=request.conversation_history
        )
        
        return PRDResponse(**result)
        
    except Exception as e:
        # Log the error for debugging (in production, use proper logging)
        print(f"Error processing PRD request: {str(e)}")
        
        return PRDResponse(
            success=False,
            prd_content={},
            clarifying_questions=[],
            analysis={},
            error_message=f"Processing failed: {str(e)}",
            processing_stage="error"
        )


@app.get(
    "/api/rag-status",
    tags=["RAG System"]
)
async def get_rag_status() -> dict[str, bool | str]:
    """
    Check if RAG system is available and ready.
    
    Returns:
        Dictionary containing RAG system status
    """
    return {
        "rag_available": RAG_SYSTEM_AVAILABLE,
        "status": "ready" if RAG_SYSTEM_AVAILABLE else "unavailable",
        "message": "RAG system is ready for PRD processing" if RAG_SYSTEM_AVAILABLE else "RAG system dependencies not found"
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
) -> FileAttachmentModel:
    """
    Create a new file attachment record in the database.
    
    Args:
        file_attachment: File attachment data to create.
        db: Database session injected via dependency.
        
    Returns:
        Created file attachment with generated ID and timestamps.
        
    Raises:
        HTTPException: If database operation fails.
    """
    try:
        # Create new FileAttachment model instance from validated data
        db_attachment: FileAttachmentModel = FileAttachmentModel(
            **file_attachment.model_dump()
        )
        
        # Persist to database
        db.add(db_attachment)
        db.commit()
        db.refresh(db_attachment)
        
        return db_attachment
        
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: Failed to create file attachment"
        ) from e


@app.get(
    "/file-attachments/",
    response_model=List[FileAttachmentResponse],
    tags=["File Attachments"]
)
async def list_file_attachments(
    conversation_id: Optional[int] = Query(None, ge=1, description="Filter by conversation ID"),
    db: Session = Depends(get_db)
) -> List[FileAttachmentModel]:
    """
    Retrieve all file attachments with optional conversation filtering.
    
    Args:
        conversation_id: Optional conversation ID to filter results.
        db: Database session injected via dependency.
        
    Returns:
        List of file attachments matching the filter criteria.
        
    Raises:
        HTTPException: If database query fails.
    """
    try:
        query = db.query(FileAttachmentModel)
        
        # Apply conversation filter if provided
        if conversation_id is not None:
            query = query.filter(
                FileAttachmentModel.conversation_id == conversation_id
            )
        
        return query.all()
        
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error: Failed to retrieve file attachments"
        ) from e


@app.get(
    "/file-attachments/{file_id}",
    response_model=FileAttachmentResponse,
    tags=["File Attachments"]
)
async def get_file_attachment(
    file_id: int,
    db: Session = Depends(get_db)
) -> FileAttachmentModel:
    """
    Retrieve a specific file attachment by its unique identifier.
    
    Args:
        file_id: Unique identifier of the file attachment.
        db: Database session injected via dependency.
        
    Returns:
        File attachment with the specified ID.
        
    Raises:
        HTTPException: 404 if file attachment not found, 500 if database error.
    """
    # Validate file_id is positive
    if file_id < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File ID must be a positive integer"
        )
    
    try:
        attachment: Optional[FileAttachmentModel] = db.query(
            FileAttachmentModel
        ).filter(
            FileAttachmentModel.id == file_id
        ).first()
        
        if attachment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File attachment with ID {file_id} not found"
            )
        
        return attachment
        
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error: Failed to retrieve file attachment"
        ) from e


@app.put(
    "/file-attachments/{file_id}",
    response_model=FileAttachmentResponse,
    tags=["File Attachments"]
)
async def update_file_attachment(
    file_id: int,
    file_attachment: FileAttachmentCreate,
    db: Session = Depends(get_db)
) -> FileAttachmentModel:
    """
    Perform a full update of an existing file attachment.
    
    Args:
        file_id: Unique identifier of the file attachment to update.
        file_attachment: New file attachment data.
        db: Database session injected via dependency.
        
    Returns:
        Updated file attachment with refreshed data.
        
    Raises:
        HTTPException: 400 for invalid ID, 404 if not found, 500 if database error.
    """
    # Validate file_id is positive
    if file_id < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File ID must be a positive integer"
        )
    
    try:
        attachment: Optional[FileAttachmentModel] = db.query(
            FileAttachmentModel
        ).filter(
            FileAttachmentModel.id == file_id
        ).first()
        
        if attachment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File attachment with ID {file_id} not found"
            )
        
        # Update all fields from validated input
        update_data: dict = file_attachment.model_dump()
        for key, value in update_data.items():
            setattr(attachment, key, value)
        
        db.commit()
        db.refresh(attachment)
        
        return attachment
        
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error: Failed to update file attachment"
        ) from e


@app.patch(
    "/file-attachments/{file_id}",
    response_model=FileAttachmentResponse,
    tags=["File Attachments"]
)
async def partial_update_file_attachment(
    file_id: int,
    file_attachment: FileAttachmentUpdate,
    db: Session = Depends(get_db)
) -> FileAttachmentModel:
    """
    Perform a partial update of an existing file attachment.
    
    Only the fields provided in the request body will be updated.
    
    Args:
        file_id: Unique identifier of the file attachment to update.
        file_attachment: Partial file attachment data with fields to update.
        db: Database session injected via dependency.
        
    Returns:
        Updated file attachment with refreshed data.
        
    Raises:
        HTTPException: 400 for invalid ID or empty update, 404 if not found, 
                      500 if database error.
    """
    # Validate file_id is positive
    if file_id < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File ID must be a positive integer"
        )
    
    try:
        attachment: Optional[FileAttachmentModel] = db.query(
            FileAttachmentModel
        ).filter(
            FileAttachmentModel.id == file_id
        ).first()
        
        if attachment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File attachment with ID {file_id} not found"
            )
        
        # Extract only the fields that were explicitly set
        update_data: dict = file_attachment.model_dump(exclude_unset=True)
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields provided for update"
            )
        
        # Apply partial update
        for key, value in update_data.items():
            setattr(attachment, key, value)
        
        db.commit()
        db.refresh(attachment)
        
        return attachment
        
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error: Failed to update file attachment"
        ) from e


@app.delete(
    "/file-attachments/{file_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["File Attachments"]
)
async def delete_file_attachment(
    file_id: int,
    db: Session = Depends(get_db)
) -> Response:
    """
    Delete a file attachment from the database.
    
    Args:
        file_id: Unique identifier of the file attachment to delete.
        db: Database session injected via dependency.
        
    Returns:
        Response with 204 No Content status on successful deletion.
        
    Raises:
        HTTPException: 400 for invalid ID, 404 if not found, 500 if database error.
    """
    # Validate file_id is positive
    if file_id < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File ID must be a positive integer"
        )
    
    try:
        attachment: Optional[FileAttachmentModel] = db.query(
            FileAttachmentModel
        ).filter(
            FileAttachmentModel.id == file_id
        ).first()
        
        if attachment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File attachment with ID {file_id} not found"
            )
        
        # Delete the record
        db.delete(attachment)
        db.commit()
        
        return Response(status_code=status.HTTP_204_NO_CONTENT)
        
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error: Failed to delete file attachment"
        ) from e


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
