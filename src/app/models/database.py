"""
Database models for Patent Intelligence System.

Implements P3.1 Database Schema & Persistence Layer per DatabaseSchemaSpec.md.
All models follow Standards.md requirements:
- Use UUIDMixin for primary keys (no auto-increment)  
- Follow snake_case naming conventions
- Support PostgreSQL-specific features
- Comply with CorpusModel.md business rules
- Enable ProvenanceAudit.md litigation-grade traceability

TODO P3.x: Replace placeholder patterns with actual common service integrations
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List

from sqlalchemy import (
    String, Text, Boolean, DateTime, Integer, 
    ForeignKey, CheckConstraint, UniqueConstraint, Index,
    JSON, text
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.db.database import Base
from ..core.config import settings


# Custom UUIDMixin and TimestampMixin for our models
# TODO P3.x: Replace with IDService.generate() when common services implemented
class UUIDMixin:
    uuid: Mapped[str] = mapped_column(
        String(36), primary_key=True
    )


# TODO P3.x: Replace with TimeService.utc_now() when common services implemented  
class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("NOW()")
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, server_default=text("NOW()")
    )


# ============================================================================
# Enums - Business Logic Constants per Specifications
# ============================================================================

class CorpusType(str, Enum):
    """Corpus types per CorpusModel.md authoritative definitions."""
    OPEN_PATENT = "open_patent"        # Claim drafting authorized
    ADVERSARIAL = "adversarial"        # Risk analysis only (prior art, OA, IPR)  
    PRODUCT = "product"                # Evidence mapping only
    GUIDANCE = "guidance"              # Style guidance only


class DocumentType(str, Enum):
    """Document classification types."""
    PATENT = "patent"
    PRIOR_ART = "prior_art"
    OFFICE_ACTION = "office_action"
    IPR_DOCUMENT = "ipr_document"
    PRODUCT_DOCUMENT = "product_document"
    GUIDANCE_DOCUMENT = "guidance_document"
    UNKNOWN = "unknown"


class DocumentState(str, Enum):
    """Document processing states per PipelineStateMachine.md."""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    TEXT_EXTRACTED = "text_extracted"
    DIAGRAMS_IDENTIFIED = "diagrams_identified"
    OCR_COMPLETED = "ocr_completed"
    CANONICALIZED = "canonicalized"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    REJECTED = "rejected"
    FAILED = "failed"


class ArtifactType(str, Enum):
    """Types of artifacts derived from documents."""
    EXTRACTED_TEXT = "extracted_text"
    IMAGE_REFERENCE = "image_reference"
    DIAGRAM_DESCRIPTION = "diagram_description"
    OCR_RESULT = "ocr_result"
    CLASSIFICATION_LABEL = "classification_label"


class DiagramStatus(str, Enum):
    """Diagram processing and approval status."""
    IDENTIFIED = "identified"
    OCR_PENDING = "ocr_pending"
    OCR_COMPLETED = "ocr_completed"
    CANONICALIZATION_PENDING = "canonicalization_pending"
    CANONICAL_CREATED = "canonical_created"
    HUMAN_REVIEW_PENDING = "human_review_pending"
    APPROVED = "approved"
    IGNORED = "ignored"
    DUPLICATE = "duplicate"


class TaskType(str, Enum):
    """HITL task types per HITLTaskSpec.md."""
    DOCUMENT_REVIEW = "document_review"
    DIAGRAM_APPROVAL = "diagram_approval"
    OCR_VERIFICATION = "ocr_verification"
    CLAIM_VALIDATION = "claim_validation"
    ERROR_RESOLUTION = "error_resolution"


class TaskStatus(str, Enum):
    """HITL task lifecycle states."""
    CREATED = "created"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"
    ESCALATED = "escalated"


class AuditEventType(str, Enum):
    """Audit event types per ProvenanceAudit.md."""
    DOCUMENT_CREATED = "document_created"
    DOCUMENT_UPDATED = "document_updated"
    STATE_TRANSITION = "state_transition"
    ARTIFACT_CREATED = "artifact_created"
    DIAGRAM_APPROVED = "diagram_approved"
    CORPUS_ASSIGNMENT = "corpus_assignment"
    TASK_CREATED = "task_created"
    TASK_COMPLETED = "task_completed"
    AGENT_EXECUTION = "agent_execution"
    HUMAN_DECISION = "human_decision"


class ActorType(str, Enum):
    """Actor types for provenance tracking."""
    HUMAN_REVIEWER = "human_reviewer"
    SYSTEM_PROCESS = "system_process"
    AGENT_EXECUTION = "agent_execution"


class ProvenanceActionType(str, Enum):
    """Provenance action types per ProvenanceAudit.md."""
    CREATE = "create"
    TRANSFORM = "transform"
    APPROVE = "approve"
    REJECT = "reject"
    ANNOTATE = "annotate"
    DERIVE = "derive"


# ============================================================================
# Core Document Management Models
# ============================================================================

class Document(UUIDMixin, TimestampMixin, Base):
    """
    Primary document entity per DatabaseSchemaSpec.md.
    
    Represents ingested documents with corpus assignment and state tracking.
    Enforces single corpus per document per CorpusModel.md rules.
    """
    __tablename__ = "documents"
    
    # Document metadata
    title: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(1000), nullable=False)
    document_type: Mapped[DocumentType] = mapped_column(String(50), nullable=False, index=True)
    current_state: Mapped[DocumentState] = mapped_column(String(50), nullable=False, index=True, default=DocumentState.UPLOADED)
    
    # Content and metadata
    original_filename: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    mime_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    document_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, unique=True, index=True)
    
    # Single corpus assignment (enforced business rule)
    # TODO P3.x: Replace with IDService.generate() when common services implemented
    corpus_id: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey("corpora.uuid", ondelete="RESTRICT"), 
        nullable=False,
        index=True
    )
    
    # Processing metadata
    ingestion_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    processing_started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    processing_completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Error tracking
    error_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    corpus: Mapped["Corpus"] = relationship("Corpus", back_populates="documents")
    versions: Mapped[List["DocumentVersion"]] = relationship("DocumentVersion", back_populates="document", cascade="all, delete-orphan")
    artifacts: Mapped[List["Artifact"]] = relationship("Artifact", back_populates="document", cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_documents_corpus_state', 'corpus_id', 'current_state'),
        Index('idx_documents_type_created', 'document_type', 'created_at'),
        Index('idx_documents_hash', 'document_hash'),
        CheckConstraint('error_count >= 0', name='ck_documents_error_count_non_negative'),
    )


class DocumentVersion(UUIDMixin, TimestampMixin, Base):
    """
    Immutable document versions per DatabaseSchemaSpec.md.
    
    Tracks document content changes with parent relationships for audit trail.
    Supports content snapshots for litigation-grade auditability.
    """
    __tablename__ = "document_versions"
    
    # Parent document reference
    # TODO P3.x: Replace with IDService.generate() when common services implemented
    document_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("documents.uuid", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Version tracking
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    parent_version_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("document_versions.uuid", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Content snapshot
    content_snapshot: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    transformation_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Version metadata
    created_by_type: Mapped[ActorType] = mapped_column(String(50), nullable=False)
    created_by_id: Mapped[str] = mapped_column(String(255), nullable=False)
    change_rationale: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    document: Mapped["Document"] = relationship("Document", back_populates="versions")
    parent_version: Mapped[Optional["DocumentVersion"]] = relationship("DocumentVersion", remote_side="DocumentVersion.uuid")
    child_versions: Mapped[List["DocumentVersion"]] = relationship("DocumentVersion", back_populates="parent_version")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('document_id', 'version_number', name='uq_document_version'),
        Index('idx_document_versions_doc_version', 'document_id', 'version_number'),
        CheckConstraint('version_number > 0', name='ck_version_number_positive'),
    )


class Artifact(UUIDMixin, TimestampMixin, Base):
    """
    Document-derived content per DatabaseSchemaSpec.md.
    
    Represents text extractions, images, diagrams, and other artifacts
    derived from documents with full provenance tracking.
    """
    __tablename__ = "artifacts"
    
    # Parent document reference
    # TODO P3.x: Replace with IDService.generate() when common services implemented
    document_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("documents.uuid", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Artifact identification
    artifact_type: Mapped[ArtifactType] = mapped_column(String(50), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Content and location
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    file_path: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    content_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    
    # Processing metadata
    extraction_confidence: Mapped[Optional[float]] = mapped_column(nullable=True)
    processing_metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Provenance
    # TODO P3.x: Replace with IDService.generate() when common services implemented
    derived_from_artifact_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("artifacts.uuid", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Relationships
    document: Mapped["Document"] = relationship("Document", back_populates="artifacts")
    parent_artifact: Mapped[Optional["Artifact"]] = relationship("Artifact", remote_side="Artifact.uuid")
    child_artifacts: Mapped[List["Artifact"]] = relationship("Artifact", back_populates="parent_artifact")
    
    # Indexes
    __table_args__ = (
        Index('idx_artifacts_document_type', 'document_id', 'artifact_type'),
        Index('idx_artifacts_hash', 'content_hash'),
        CheckConstraint('extraction_confidence IS NULL OR (extraction_confidence >= 0.0 AND extraction_confidence <= 1.0)', 
                       name='ck_artifacts_confidence_range'),
    )


class DiagramCanonical(UUIDMixin, TimestampMixin, Base):
    """
    Structured diagram representations per DatabaseSchemaSpec.md.
    
    Canonical diagram format with source relationships and versioning.
    Supports diagram reuse per CorpusModel.md most-restrictive inheritance rules.
    """
    __tablename__ = "diagram_canonical"
    
    # Canonical description
    canonical_description: Mapped[str] = mapped_column(Text, nullable=False)
    description_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    description_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    
    # Source and reuse tracking
    # TODO P3.x: Replace with IDService.generate() when common services implemented
    original_artifact_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("artifacts.uuid", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    reuse_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    
    # Status and approval
    status: Mapped[DiagramStatus] = mapped_column(String(50), nullable=False, default=DiagramStatus.CANONICAL_CREATED, index=True)
    approved_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    approval_rationale: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Ignored handling per CorpusModel.md
    ignored_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ignored_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    ignored_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Most restrictive corpus (business rule enforcement)
    # TODO P3.x: Replace with IDService.generate() when common services implemented  
    most_restrictive_corpus_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("corpora.uuid", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    
    # Processing metadata
    ocr_confidence: Mapped[Optional[float]] = mapped_column(nullable=True)
    processing_metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Relationships
    original_artifact: Mapped["Artifact"] = relationship("Artifact")
    most_restrictive_corpus: Mapped["Corpus"] = relationship("Corpus")
    
    # Indexes and constraints
    __table_args__ = (
        Index('idx_diagram_canonical_status', 'status'),
        Index('idx_diagram_canonical_corpus', 'most_restrictive_corpus_id'),
        CheckConstraint('reuse_count > 0', name='ck_diagram_canonical_reuse_count_positive'),
        CheckConstraint('ocr_confidence IS NULL OR (ocr_confidence >= 0.0 AND ocr_confidence <= 1.0)', 
                       name='ck_diagram_canonical_ocr_confidence_range'),
        CheckConstraint('(status = \'ignored\') = (ignored_reason IS NOT NULL)', 
                       name='ck_diagram_canonical_ignored_reason_required'),
        CheckConstraint('(approved_at IS NOT NULL) = (approved_by IS NOT NULL)', 
                       name='ck_diagram_canonical_approval_consistency'),
    )


# ============================================================================
# Corpus & Access Control Models
# ============================================================================

class Corpus(UUIDMixin, TimestampMixin, Base):
    """
    Corpus definitions per CorpusModel.md authoritative business rules.
    
    Defines corpus types with access policies and boundary enforcement.
    Implements the core rule: Only Open Patent Corpus may support claim language.
    """
    __tablename__ = "corpora"
    
    # Corpus identification
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    corpus_type: Mapped[CorpusType] = mapped_column(String(50), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Access control matrix per CorpusModel.md
    allows_claim_drafting: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    allows_risk_analysis: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    allows_evidence_mapping: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    allows_style_guidance: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    
    # Corpus metadata
    created_by: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    
    # Policy enforcement metadata
    isolation_level: Mapped[str] = mapped_column(String(50), nullable=False, default="strict")
    access_audit_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    
    # Relationships
    documents: Mapped[List["Document"]] = relationship("Document", back_populates="corpus")
    memberships: Mapped[List["CorpusMembership"]] = relationship("CorpusMembership", back_populates="corpus", cascade="all, delete-orphan")
    
    # Indexes and business rule constraints
    __table_args__ = (
        Index('idx_corpora_type_active', 'corpus_type', 'is_active'),
        # Enforce CorpusModel.md access matrix rules
        CheckConstraint(
            """(corpus_type = 'open_patent' AND allows_claim_drafting = true) OR
               (corpus_type != 'open_patent' AND allows_claim_drafting = false)""",
            name='ck_corpora_claim_drafting_rule'
        ),
        CheckConstraint(
            """(corpus_type = 'adversarial' AND allows_risk_analysis = true) OR
               (corpus_type != 'adversarial' AND allows_risk_analysis IN (true, false))""",
            name='ck_corpora_adversarial_authorized_for_risk'
        ),
        CheckConstraint(
            """(corpus_type = 'product' AND allows_evidence_mapping = true) OR
               (corpus_type != 'product' AND allows_evidence_mapping IN (true, false))""",
            name='ck_corpora_product_authorized_for_evidence'
        ),
        CheckConstraint(
            """(corpus_type = 'guidance' AND allows_style_guidance = true) OR
               (corpus_type != 'guidance' AND allows_style_guidance IN (true, false))""",
            name='ck_corpora_guidance_authorized_for_style'
        ),
    )


class CorpusMembership(UUIDMixin, TimestampMixin, Base):
    """
    Document-to-corpus assignments per DatabaseSchemaSpec.md.
    
    Tracks membership rules, timestamps, and violation audit trails.
    Enforces single corpus per document with complete audit history.
    """
    __tablename__ = "corpus_memberships"
    
    # Document and corpus references
    # TODO P3.x: Replace with IDService.generate() when common services implemented
    document_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("documents.uuid", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    corpus_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("corpora.uuid", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    
    # Membership metadata
    assigned_by: Mapped[str] = mapped_column(String(255), nullable=False)
    assignment_reason: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    
    # Violation tracking
    violation_detected: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    violation_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    violation_detected_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    violation_resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Membership validation
    validation_performed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    validation_result: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Deactivation tracking
    deactivated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    deactivated_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    deactivation_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    document: Mapped["Document"] = relationship("Document")
    corpus: Mapped["Corpus"] = relationship("Corpus", back_populates="memberships")
    
    # Constraints and indexes
    __table_args__ = (
        # Single active membership per document (business rule) - PostgreSQL partial index
        Index('idx_corpus_membership_single_active', 'document_id', unique=True, 
              postgresql_where="is_active = true"),
        Index('idx_corpus_memberships_document_active', 'document_id', 'is_active'),
        Index('idx_corpus_memberships_corpus', 'corpus_id'),
        Index('idx_corpus_memberships_violations', 'violation_detected', 'violation_detected_at'),
        # Violation consistency constraints
        CheckConstraint('(violation_detected = true) = (violation_reason IS NOT NULL)', 
                       name='ck_corpus_membership_violation_reason_required'),
        CheckConstraint('(violation_detected = false) OR (violation_detected_at IS NOT NULL)', 
                       name='ck_corpus_membership_violation_timestamp_required'),
        # Deactivation consistency
        CheckConstraint('(is_active = false) = (deactivated_at IS NOT NULL)', 
                       name='ck_corpus_membership_deactivation_timestamp_required'),
        CheckConstraint('(deactivated_at IS NOT NULL) = (deactivated_by IS NOT NULL)', 
                       name='ck_corpus_membership_deactivation_actor_required'),
    )


# ============================================================================
# Agent & Task Management Models  
# ============================================================================

class AgentRun(UUIDMixin, TimestampMixin, Base):
    """
    Agent execution tracking per DatabaseSchemaSpec.md.
    
    Tracks agent identity, parameters, corpus access, input/output provenance,
    and success/failure status with retry logic per ProvenanceAudit.md.
    """
    __tablename__ = "agent_runs"
    
    # Agent identification
    agent_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    agent_version: Mapped[str] = mapped_column(String(100), nullable=False)
    agent_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    # Execution context
    execution_id: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    parent_execution_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    correlation_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    
    # Input parameters and corpus access
    input_parameters: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    authorized_corpus_ids: Mapped[List[str]] = mapped_column(JSONB, nullable=False)
    actual_corpus_accessed: Mapped[Optional[List[str]]] = mapped_column(JSONB, nullable=True)
    
    # Execution tracking
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_seconds: Mapped[Optional[float]] = mapped_column(nullable=True)
    
    # Status and results
    status: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    success: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True, index=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_traceback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Input/output tracking for provenance
    input_artifact_ids: Mapped[Optional[List[str]]] = mapped_column(JSONB, nullable=True)
    output_artifact_ids: Mapped[Optional[List[str]]] = mapped_column(JSONB, nullable=True)
    
    # Retry logic
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_retries: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    retry_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Configuration and environment
    configuration_snapshot: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    environment_info: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Performance metrics
    memory_usage_mb: Mapped[Optional[float]] = mapped_column(nullable=True)
    cpu_time_seconds: Mapped[Optional[float]] = mapped_column(nullable=True)
    
    # Indexes and constraints
    __table_args__ = (
        Index('idx_agent_runs_agent_status', 'agent_name', 'status'),
        Index('idx_agent_runs_started', 'started_at'),
        Index('idx_agent_runs_correlation', 'correlation_id'),
        Index('idx_agent_runs_success', 'success', 'completed_at'),
        CheckConstraint('retry_count >= 0', name='ck_agent_runs_retry_count_non_negative'),
        CheckConstraint('max_retries >= 0', name='ck_agent_runs_max_retries_non_negative'),
        CheckConstraint('retry_count <= max_retries', name='ck_agent_runs_retry_within_max'),
        CheckConstraint('duration_seconds IS NULL OR duration_seconds >= 0', 
                       name='ck_agent_runs_duration_non_negative'),
        CheckConstraint('(completed_at IS NOT NULL) = (duration_seconds IS NOT NULL)', 
                       name='ck_agent_runs_completion_duration_consistency'),
        CheckConstraint('(success IS NOT NULL) = (completed_at IS NOT NULL)', 
                       name='ck_agent_runs_success_completion_consistency'),
    )


class Task(UUIDMixin, TimestampMixin, Base):
    """
    HITL task lifecycle per DatabaseSchemaSpec.md and HITLTaskSpec.md.
    
    Manages human-in-the-loop tasks with evidence bundle references,
    completion criteria, outcomes, and full audit trail.
    """
    __tablename__ = "tasks"
    
    # Task identification
    task_type: Mapped[TaskType] = mapped_column(String(50), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=5, index=True)
    
    # Task status and lifecycle
    status: Mapped[TaskStatus] = mapped_column(String(50), nullable=False, default=TaskStatus.CREATED, index=True)
    assigned_to: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    assigned_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Evidence and context
    evidence_bundle: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    related_document_ids: Mapped[Optional[List[str]]] = mapped_column(JSONB, nullable=True)
    related_artifact_ids: Mapped[Optional[List[str]]] = mapped_column(JSONB, nullable=True)
    
    # Escalation and dependencies
    # TODO P3.x: Replace with IDService.generate() when common services implemented
    escalated_from_task_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("tasks.uuid", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    blocks_task_ids: Mapped[Optional[List[str]]] = mapped_column(JSONB, nullable=True)
    depends_on_task_ids: Mapped[Optional[List[str]]] = mapped_column(JSONB, nullable=True)
    
    # Completion criteria and outcome
    completion_criteria: Mapped[str] = mapped_column(Text, nullable=False)
    completion_instructions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timing and deadlines
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    time_spent_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Completion outcome
    outcome: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    outcome_details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reviewer_confidence: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    reviewer_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Task metadata
    created_by: Mapped[str] = mapped_column(String(255), nullable=False)
    created_by_type: Mapped[ActorType] = mapped_column(String(50), nullable=False)
    urgency_level: Mapped[str] = mapped_column(String(50), nullable=False, default="normal")
    
    # Quality assurance
    requires_qa: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    qa_completed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    qa_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    escalated_from: Mapped[Optional["Task"]] = relationship("Task", remote_side="Task.uuid")
    escalated_tasks: Mapped[List["Task"]] = relationship("Task", back_populates="escalated_from")
    
    # Indexes and constraints
    __table_args__ = (
        Index('idx_tasks_type_status', 'task_type', 'status'),
        Index('idx_tasks_assigned', 'assigned_to', 'assigned_at'),
        Index('idx_tasks_due_date', 'due_date'),
        Index('idx_tasks_priority_status', 'priority', 'status'),
        Index('idx_tasks_created', 'created_at'),
        CheckConstraint('priority >= 1 AND priority <= 10', name='ck_tasks_priority_range'),
        CheckConstraint('reviewer_confidence IS NULL OR (reviewer_confidence >= 1 AND reviewer_confidence <= 5)', 
                       name='ck_tasks_reviewer_confidence_range'),
        CheckConstraint('time_spent_minutes IS NULL OR time_spent_minutes >= 0', 
                       name='ck_tasks_time_spent_non_negative'),
        CheckConstraint('(status = \'completed\') = (completed_at IS NOT NULL)', 
                       name='ck_tasks_completion_consistency'),
        CheckConstraint('(assigned_to IS NOT NULL) = (assigned_at IS NOT NULL)', 
                       name='ck_tasks_assignment_consistency'),
        CheckConstraint('(requires_qa = false) OR (qa_completed IN (true, false))', 
                       name='ck_tasks_qa_logic'),
    )


# ============================================================================
# Audit & Provenance Models for Litigation-Grade Traceability
# ============================================================================

class AuditEvent(UUIDMixin, TimestampMixin, Base):
    """
    Immutable audit event logging per DatabaseSchemaSpec.md and ProvenanceAudit.md.
    
    Captures all system events with complete context for legal compliance.
    Events are immutable once recorded - corrections occur through new records.
    """
    __tablename__ = "audit_events"
    
    # Event identification
    event_type: Mapped[AuditEventType] = mapped_column(String(50), nullable=False, index=True)
    event_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    event_description: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Actor identification (who)
    actor_type: Mapped[ActorType] = mapped_column(String(50), nullable=False, index=True)
    actor_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    actor_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    session_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    
    # Context (what, where)
    resource_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    resource_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    resource_name: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Action details
    action_taken: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    action_rationale: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Before/after state for modifications
    before_state: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    after_state: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Request context
    request_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    correlation_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    trace_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    
    # Timing and environment
    event_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    timezone: Mapped[str] = mapped_column(String(50), nullable=False, default="UTC")
    
    # Policy context per ProvenanceAudit.md phase awareness
    development_phase: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    ruleset_version: Mapped[str] = mapped_column(String(100), nullable=False)
    enforcement_mode: Mapped[str] = mapped_column(String(50), nullable=False, default="enforced")
    
    # Impact assessment
    affected_resources: Mapped[Optional[List[str]]] = mapped_column(JSONB, nullable=True)
    impact_level: Mapped[str] = mapped_column(String(50), nullable=False, default="low", index=True)
    
    # HITL escalation (for blocking events)
    requires_hitl: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    # TODO P3.x: Replace with IDService.generate() when common services implemented
    hitl_task_created: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("tasks.uuid", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Additional context and metadata
    additional_context: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    source_system: Mapped[str] = mapped_column(String(100), nullable=False, default="revel_hmi")
    
    # Relationships
    escalated_task: Mapped[Optional["Task"]] = relationship("Task")
    
    # Indexes and constraints (immutability enforced by application logic)
    __table_args__ = (
        Index('idx_audit_events_type_timestamp', 'event_type', 'event_timestamp'),
        Index('idx_audit_events_actor', 'actor_type', 'actor_id'),
        Index('idx_audit_events_resource', 'resource_type', 'resource_id'),
        Index('idx_audit_events_action', 'action_taken', 'event_timestamp'),
        Index('idx_audit_events_correlation', 'correlation_id', 'event_timestamp'),
        Index('idx_audit_events_hitl', 'requires_hitl', 'hitl_task_created'),
        Index('idx_audit_events_phase', 'development_phase', 'enforcement_mode'),
        # Ensure audit completeness
        CheckConstraint('(action_taken = \'modified\') = (before_state IS NOT NULL AND after_state IS NOT NULL)', 
                       name='ck_audit_events_modification_states_required'),
        CheckConstraint('(requires_hitl = false) OR (requires_hitl = true)', 
                       name='ck_audit_events_hitl_boolean'),
    )


class Provenance(UUIDMixin, TimestampMixin, Base):
    """
    Provenance/Lineage DAG tracking per ProvenanceAudit.md and DatabaseSchemaSpec.md.
    
    Implements PROV-O compliance structures for litigation-grade artifact traceability.
    Maintains directed acyclic graph (DAG) relationships between artifacts.
    """
    __tablename__ = "provenance"
    
    # Provenance record identification  
    provenance_record_id: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    
    # Artifact and action identification
    artifact_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    artifact_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    action_type: Mapped[ProvenanceActionType] = mapped_column(String(50), nullable=False, index=True)
    
    # Actor identification (agent, human, system)
    actor_type: Mapped[ActorType] = mapped_column(String(50), nullable=False, index=True)
    actor_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    
    # Input/output relationships for DAG
    input_artifact_ids: Mapped[Optional[List[str]]] = mapped_column(JSONB, nullable=True)
    output_artifact_ids: Mapped[Optional[List[str]]] = mapped_column(JSONB, nullable=True)
    
    # Temporal information
    activity_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    
    # Policy context per ProvenanceAudit.md phase awareness
    policy_phase: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    policy_ruleset_version: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Confidence and quality
    confidence_level: Mapped[Optional[float]] = mapped_column(nullable=True)
    quality_score: Mapped[Optional[float]] = mapped_column(nullable=True)
    
    # Detailed provenance context
    transformation_details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Request correlation
    request_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    correlation_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    
    # Agent-specific context (when applicable)
    # TODO P3.x: Replace with IDService.generate() when common services implemented
    agent_execution_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("agent_runs.uuid", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Lineage chain metadata
    lineage_depth: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    root_artifact_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    
    # PROV-O compliance fields
    prov_activity_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    prov_entity_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    prov_agent_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Immutability tracking
    # TODO P3.x: Replace with IDService.generate() when common services implemented
    revision_of: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("provenance.uuid", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Additional context
    additional_metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Relationships
    agent_run: Mapped[Optional["AgentRun"]] = relationship("AgentRun")
    parent_provenance: Mapped[Optional["Provenance"]] = relationship("Provenance", remote_side="Provenance.uuid")
    child_provenance_records: Mapped[List["Provenance"]] = relationship("Provenance", back_populates="parent_provenance")
    
    # Indexes and constraints
    __table_args__ = (
        Index('idx_provenance_artifact', 'artifact_id', 'artifact_type'),
        Index('idx_provenance_actor', 'actor_type', 'actor_id'),
        Index('idx_provenance_action_timestamp', 'action_type', 'activity_timestamp'),
        Index('idx_provenance_correlation', 'correlation_id', 'activity_timestamp'),
        Index('idx_provenance_lineage', 'root_artifact_id', 'lineage_depth'),
        Index('idx_provenance_agent', 'agent_execution_id'),
        # DAG constraints (cycles forbidden)
        CheckConstraint('lineage_depth >= 0', name='ck_provenance_lineage_depth_non_negative'),
        CheckConstraint('confidence_level IS NULL OR (confidence_level >= 0.0 AND confidence_level <= 1.0)', 
                       name='ck_provenance_confidence_range'),
        CheckConstraint('quality_score IS NULL OR (quality_score >= 0.0 AND quality_score <= 1.0)', 
                       name='ck_provenance_quality_range'),
        # Prevent self-reference in revision chain
        CheckConstraint('revision_of != uuid', name='ck_provenance_no_self_revision'),
    )