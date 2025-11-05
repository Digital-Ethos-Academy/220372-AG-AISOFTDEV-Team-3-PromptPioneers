"""
SQLAlchemy ORM Models for AI-Powered Requirement Analyzer

This module defines the database schema for managing conversations,
messages, file attachments, PRD versions, and related entities in the
Product Requirements Document generation system.

All models use SQLAlchemy 2.0+ declarative style with proper type hints
and relationship mappings.
"""

from datetime import datetime
from typing import Optional, List, Any

from sqlalchemy import (
    String,
    Text,
    Integer,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    Index,
    event
)
from sqlalchemy.engine import Connection
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Mapper


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy ORM models.
    
    Provides common functionality and type checking for all database models.
    All model classes should inherit from this base class.
    """
    pass


class Conversation(Base):
    """
    Represents a conversation session between a user and the AI.
    
    A conversation is the top-level entity that contains all interactions,
    including messages, file attachments, PRD versions, and clarifying questions.
    Each conversation tracks its current PRD version and overall status.
    
    Attributes:
        id: Primary key, auto-incremented.
        title: Optional human-readable title for the conversation.
        current_prd_version_id: Foreign key to the current PRD version.
        status: Current state (e.g., 'active', 'completed', 'archived').
        metadata: JSON-formatted additional data.
        created_at: Timestamp of conversation creation.
        updated_at: Timestamp of last modification.
    """
    __tablename__ = "conversation"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    current_prd_version_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("prd_version.id", ondelete="SET NULL"),
        nullable=True
    )
    status: Mapped[str] = mapped_column(Text, nullable=False, default="active")
    metadata: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationships
    messages: Mapped[List["Message"]] = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan"
    )
    file_attachments: Mapped[List["FileAttachment"]] = relationship(
        "FileAttachment",
        back_populates="conversation",
        cascade="all, delete-orphan"
    )
    clarifying_questions: Mapped[List["ClarifyingQuestion"]] = relationship(
        "ClarifyingQuestion",
        back_populates="conversation",
        cascade="all, delete-orphan"
    )
    prd_versions: Mapped[List["PRDVersion"]] = relationship(
        "PRDVersion",
        back_populates="conversation",
        foreign_keys="PRDVersion.conversation_id",
        cascade="all, delete-orphan"
    )
    exports: Mapped[List["Export"]] = relationship(
        "Export",
        back_populates="conversation",
        cascade="all, delete-orphan"
    )
    # Self-referential relationship for current PRD version
    current_prd_version: Mapped[Optional["PRDVersion"]] = relationship(
        "PRDVersion",
        foreign_keys=[current_prd_version_id],
        post_update=True
    )
    
    def __repr__(self) -> str:
        """String representation for debugging and logging."""
        return (
            f"<Conversation(id={self.id}, title={self.title!r}, "
            f"status={self.status!r}, created_at={self.created_at})>"
        )
    
    def is_active(self) -> bool:
        """Check if conversation is in active status."""
        return self.status == "active"


class Message(Base):
    """
    Represents a message in a conversation, sent by either the user or AI.
    
    Messages are the fundamental unit of communication in a conversation.
    They can trigger various actions like PRD generation or clarifying questions.
    
    Attributes:
        id: Primary key, auto-incremented.
        conversation_id: Foreign key to parent conversation.
        sender: Message sender ('user' or 'ai').
        message_type: Type of message ('text', 'system', 'file', etc.).
        content: The actual message content.
        metadata: JSON-formatted additional data.
        status: Delivery status (e.g., 'delivered', 'pending', 'failed').
        created_at: Timestamp of message creation.
        updated_at: Timestamp of last modification.
    """
    __tablename__ = "message"
    __table_args__ = (
        Index("idx_message_conversation_id", "conversation_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    conversation_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("conversation.id", ondelete="CASCADE"),
        nullable=False
    )
    sender: Mapped[str] = mapped_column(Text, nullable=False)  # 'user' or 'ai'
    message_type: Mapped[str] = mapped_column(Text, nullable=False)  # 'text', 'system', 'file', etc.
    content: Mapped[str] = mapped_column(Text, nullable=False)
    metadata: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="delivered")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationships
    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="messages")
    prd_versions_generated: Mapped[List["PRDVersion"]] = relationship(
        "PRDVersion",
        back_populates="generated_by_ai_message",
        foreign_keys="PRDVersion.generated_by_ai_message_id"
    )
    clarifying_questions_asked: Mapped[List["ClarifyingQuestion"]] = relationship(
        "ClarifyingQuestion",
        back_populates="ai_message",
        foreign_keys="ClarifyingQuestion.ai_message_id"
    )
    clarifying_questions_answered: Mapped[List["ClarifyingQuestion"]] = relationship(
        "ClarifyingQuestion",
        back_populates="user_message",
        foreign_keys="ClarifyingQuestion.user_message_id"
    )
    
    def __repr__(self) -> str:
        """String representation for debugging and logging."""
        content_preview: str = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return (
            f"<Message(id={self.id}, sender={self.sender!r}, "
            f"type={self.message_type!r}, content={content_preview!r})>"
        )
    
    def is_from_user(self) -> bool:
        """Check if message is from user."""
        return self.sender == "user"
    
    def is_from_ai(self) -> bool:
        """Check if message is from AI."""
        return self.sender == "ai"


class FileAttachment(Base):
    """
    Represents a file uploaded by the user during a conversation.
    
    File attachments are processed to extract text content that feeds into
    the PRD generation process. Supports multiple file formats.
    
    Attributes:
        id: Primary key, auto-incremented.
        conversation_id: Foreign key to parent conversation.
        original_filename: Name of the uploaded file.
        file_type: File extension ('txt', 'md', 'docx').
        file_size: Size in bytes.
        storage_path: Path where file is stored on disk.
        extracted_text: Text content extracted from the file.
        status: Processing status ('uploaded', 'processing', 'processed', 'failed').
        metadata: JSON-formatted additional data.
        created_at: Timestamp of file upload.
        updated_at: Timestamp of last modification.
    """
    __tablename__ = "file_attachment"
    __table_args__ = (
        Index("idx_file_attachment_conversation_id", "conversation_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    conversation_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("conversation.id", ondelete="CASCADE"),
        nullable=False
    )
    original_filename: Mapped[str] = mapped_column(Text, nullable=False)
    file_type: Mapped[str] = mapped_column(Text, nullable=False)  # 'txt', 'md', 'docx'
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_path: Mapped[str] = mapped_column(Text, nullable=False)
    extracted_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="uploaded")
    metadata: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationships
    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="file_attachments")
    
    def __repr__(self) -> str:
        """String representation for debugging and logging."""
        return (
            f"<FileAttachment(id={self.id}, filename={self.original_filename!r}, "
            f"type={self.file_type!r}, size={self.file_size}, status={self.status!r})>"
        )
    
    def is_processed(self) -> bool:
        """Check if file has been successfully processed."""
        return self.status == "processed"
    
    def get_size_in_mb(self) -> float:
        """Get file size in megabytes."""
        return round(self.file_size / (1024 * 1024), 2)


class ClarifyingQuestion(Base):
    """
    Represents a question asked by the AI to clarify requirements.
    
    Clarifying questions help refine and improve PRD quality by gathering
    additional information from users about ambiguous or incomplete requirements.
    
    Attributes:
        id: Primary key, auto-incremented.
        conversation_id: Foreign key to parent conversation.
        prd_version_id: Foreign key to related PRD version.
        question_text: The actual question being asked.
        category: Question category ('functional', 'non-functional', 'user', etc.).
        priority: Question priority (0=low, higher=more important).
        ai_message_id: Message where question was asked.
        user_message_id: Message containing the answer.
        answer: User's response to the question.
        status: Current state ('unanswered', 'answered', 'dismissed').
        metadata: JSON-formatted additional data.
        created_at: Timestamp of question creation.
        updated_at: Timestamp of last modification.
    """
    __tablename__ = "clarifying_question"
    __table_args__ = (
        Index("idx_clarifying_question_conversation_id", "conversation_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    conversation_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("conversation.id", ondelete="CASCADE"),
        nullable=False
    )
    prd_version_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("prd_version.id", ondelete="SET NULL"),
        nullable=True
    )
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    priority: Mapped[int] = mapped_column(Integer, default=0)
    ai_message_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("message.id", ondelete="SET NULL"),
        nullable=True
    )
    user_message_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("message.id", ondelete="SET NULL"),
        nullable=True
    )
    answer: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="unanswered")
    metadata: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationships
    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="clarifying_questions")
    prd_version: Mapped[Optional["PRDVersion"]] = relationship(
        "PRDVersion",
        back_populates="clarifying_questions"
    )
    ai_message: Mapped[Optional["Message"]] = relationship(
        "Message",
        back_populates="clarifying_questions_asked",
        foreign_keys=[ai_message_id]
    )
    user_message: Mapped[Optional["Message"]] = relationship(
        "Message",
        back_populates="clarifying_questions_answered",
        foreign_keys=[user_message_id]
    )
    
    def __repr__(self) -> str:
        """String representation for debugging and logging."""
        question_preview: str = (
            self.question_text[:50] + "..." 
            if len(self.question_text) > 50 
            else self.question_text
        )
        return (
            f"<ClarifyingQuestion(id={self.id}, status={self.status!r}, "
            f"priority={self.priority}, question={question_preview!r})>"
        )
    
    def is_answered(self) -> bool:
        """Check if question has been answered."""
        return self.status == "answered" and self.answer is not None
    
    def is_pending(self) -> bool:
        """Check if question is still waiting for an answer."""
        return self.status == "unanswered"


class PRDVersion(Base):
    """
    Represents a version of a Product Requirements Document.
    
    PRD versions track the evolution of requirements as they are refined
    through user feedback and clarifying questions. Each version is immutable
    and new versions are created for changes.
    
    Attributes:
        id: Primary key, auto-incremented.
        conversation_id: Foreign key to parent conversation.
        version_number: Sequential version number within conversation.
        content: Full PRD content in markdown format.
        change_summary: Description of changes from previous version.
        generated_by_ai_message_id: Message that triggered generation.
        trigger_type: What caused this version ('initial', 'clarification', 'edit', etc.).
        status: Processing status ('draft', 'complete', 'archived').
        metadata: JSON-formatted additional data.
        created_at: Timestamp of version creation.
        updated_at: Timestamp of last modification.
    """
    __tablename__ = "prd_version"
    __table_args__ = (
        UniqueConstraint("conversation_id", "version_number", name="uq_conversation_version"),
        Index("idx_prd_version_conversation_id", "conversation_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    conversation_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("conversation.id", ondelete="CASCADE"),
        nullable=False
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    change_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    generated_by_ai_message_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("message.id", ondelete="SET NULL"),
        nullable=True
    )
    trigger_type: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="complete")
    metadata: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationships
    conversation: Mapped["Conversation"] = relationship(
        "Conversation",
        back_populates="prd_versions",
        foreign_keys=[conversation_id]
    )
    generated_by_ai_message: Mapped[Optional["Message"]] = relationship(
        "Message",
        back_populates="prd_versions_generated"
    )
    clarifying_questions: Mapped[List["ClarifyingQuestion"]] = relationship(
        "ClarifyingQuestion",
        back_populates="prd_version"
    )
    prd_changes: Mapped[List["PRDChange"]] = relationship(
        "PRDChange",
        back_populates="prd_version",
        foreign_keys="PRDChange.prd_version_id",
        cascade="all, delete-orphan"
    )
    previous_prd_changes: Mapped[List["PRDChange"]] = relationship(
        "PRDChange",
        back_populates="previous_prd_version",
        foreign_keys="PRDChange.previous_prd_version_id"
    )
    exports: Mapped[List["Export"]] = relationship(
        "Export",
        back_populates="prd_version",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        """String representation for debugging and logging."""
        return (
            f"<PRDVersion(id={self.id}, conversation_id={self.conversation_id}, "
            f"version={self.version_number}, status={self.status!r})>"
        )
    
    def is_complete(self) -> bool:
        """Check if PRD version is complete and ready to use."""
        return self.status == "complete"
    
    def get_content_length(self) -> int:
        """Get the length of PRD content in characters."""
        return len(self.content) if self.content else 0


class PRDChange(Base):
    """
    Tracks changes between PRD versions, including what was added,
    modified, or removed in each section of the document.
    
    PRD changes provide detailed audit trail of how requirements evolved
    over time, enabling rollback and understanding of decision history.
    
    Attributes:
        id: Primary key, auto-incremented.
        prd_version_id: Foreign key to the new PRD version.
        previous_prd_version_id: Foreign key to the previous version.
        section: Document section that changed (e.g., 'executive_summary').
        change_type: Type of change ('added', 'modified', 'removed').
        old_content: Previous content (for modified/removed).
        new_content: New content (for added/modified).
        reason: Explanation for the change.
        metadata: JSON-formatted additional data.
        created_at: Timestamp of change recording.
    """
    __tablename__ = "prd_change"
    __table_args__ = (
        Index("idx_prd_change_prd_version_id", "prd_version_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    prd_version_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("prd_version.id", ondelete="CASCADE"),
        nullable=False
    )
    previous_prd_version_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("prd_version.id", ondelete="CASCADE"),
        nullable=True
    )
    section: Mapped[str] = mapped_column(Text, nullable=False)
    change_type: Mapped[str] = mapped_column(Text, nullable=False)  # 'added', 'modified', 'removed'
    old_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    new_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    prd_version: Mapped["PRDVersion"] = relationship(
        "PRDVersion",
        back_populates="prd_changes",
        foreign_keys=[prd_version_id]
    )
    previous_prd_version: Mapped[Optional["PRDVersion"]] = relationship(
        "PRDVersion",
        back_populates="previous_prd_changes",
        foreign_keys=[previous_prd_version_id]
    )
    
    def __repr__(self) -> str:
        """String representation for debugging and logging."""
        return (
            f"<PRDChange(id={self.id}, section={self.section!r}, "
            f"type={self.change_type!r}, version={self.prd_version_id})>"
        )
    
    def is_addition(self) -> bool:
        """Check if this change added new content."""
        return self.change_type == "added"
    
    def is_modification(self) -> bool:
        """Check if this change modified existing content."""
        return self.change_type == "modified"
    
    def is_removal(self) -> bool:
        """Check if this change removed content."""
        return self.change_type == "removed"


class Export(Base):
    """
    Represents an exported version of a PRD in various formats.
    
    Exports track when and how PRDs are exported to different formats,
    maintaining a history of generated documents.
    
    Attributes:
        id: Primary key, auto-incremented.
        prd_version_id: Foreign key to the PRD version being exported.
        conversation_id: Foreign key to parent conversation.
        export_format: Output format ('markdown', 'pdf', 'word', 'json').
        file_path: Path to the exported file.
        status: Export status ('pending', 'completed', 'failed').
        metadata: JSON-formatted additional data.
        created_at: Timestamp of export initiation.
        updated_at: Timestamp of last modification.
    """
    __tablename__ = "export"
    __table_args__ = (
        Index("idx_export_prd_version_id", "prd_version_id"),
        Index("idx_export_conversation_id", "conversation_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    prd_version_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("prd_version.id", ondelete="CASCADE"),
        nullable=False
    )
    conversation_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("conversation.id", ondelete="CASCADE"),
        nullable=False
    )
    export_format: Mapped[str] = mapped_column(Text, nullable=False)  # 'markdown', 'pdf', 'word', 'json'
    file_path: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="completed")
    metadata: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationships
    prd_version: Mapped["PRDVersion"] = relationship("PRDVersion", back_populates="exports")
    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="exports")
    
    def __repr__(self) -> str:
        """String representation for debugging and logging."""
        return (
            f"<Export(id={self.id}, format={self.export_format!r}, "
            f"status={self.status!r}, prd_version_id={self.prd_version_id})>"
        )
    
    def is_completed(self) -> bool:
        """Check if export completed successfully."""
        return self.status == "completed"
    
    def is_pdf(self) -> bool:
        """Check if export format is PDF."""
        return self.export_format == "pdf"
    
    def is_markdown(self) -> bool:
        """Check if export format is Markdown."""
        return self.export_format == "markdown"


# ============================================================================
# EVENT LISTENERS
# ============================================================================

@event.listens_for(Conversation, "before_update")
@event.listens_for(Message, "before_update")
@event.listens_for(FileAttachment, "before_update")
@event.listens_for(ClarifyingQuestion, "before_update")
@event.listens_for(PRDVersion, "before_update")
@event.listens_for(Export, "before_update")
def receive_before_update(
    mapper: Mapper,
    connection: Connection,
    target: Any
) -> None:
    """
    Automatically update the updated_at timestamp before any update operation.
    
    This event listener ensures that the 'updated_at' field is always set to
    the current UTC time whenever a record is modified.
    
    Args:
        mapper: The mapper which is the target of the event.
        connection: The database connection being used.
        target: The instance being updated.
    """
    if hasattr(target, 'updated_at'):
        target.updated_at = datetime.utcnow()
