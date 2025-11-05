from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, UniqueConstraint, Index, event
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""
    pass


class Conversation(Base):
    """
    Represents a conversation session between a user and the AI.
    Each conversation can have multiple messages, file attachments, PRD versions,
    and clarifying questions.
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


class Message(Base):
    """
    Represents a message in a conversation, sent by either the user or AI.
    Messages can be of different types (text, system, file) and can trigger
    PRD generation or clarifying questions.
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


class FileAttachment(Base):
    """
    Represents a file uploaded by the user during a conversation.
    Files can be text, markdown, or Word documents that are processed
    to extract requirements.
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


class ClarifyingQuestion(Base):
    """
    Represents a question asked by the AI to clarify requirements.
    Questions can be answered by users to improve PRD quality and can be
    categorized by type (functional, non-functional, user, etc.).
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


class PRDVersion(Base):
    """
    Represents a version of a Product Requirements Document.
    Each conversation can have multiple PRD versions as requirements
    are refined through clarifying questions and user feedback.
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


class PRDChange(Base):
    """
    Tracks changes between PRD versions, including what was added,
    modified, or removed in each section of the document.
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


class Export(Base):
    """
    Represents an exported version of a PRD in various formats
    (markdown, PDF, Word, JSON). Tracks export history and file locations.
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


# Event listener to automatically update 'updated_at' timestamp
@event.listens_for(Conversation, "before_update")
@event.listens_for(Message, "before_update")
@event.listens_for(FileAttachment, "before_update")
@event.listens_for(ClarifyingQuestion, "before_update")
@event.listens_for(PRDVersion, "before_update")
@event.listens_for(Export, "before_update")
def receive_before_update(mapper, connection, target):
    """Automatically update the updated_at timestamp before any update operation."""
    target.updated_at = datetime.utcnow()
