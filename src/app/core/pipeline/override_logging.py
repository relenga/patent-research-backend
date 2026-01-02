"""
Phase 3.2A Task 3.2A.7: Enhanced Override Logging System

Mandatory audit trail for all state overrides with administrator identification,
timestamp precision, and justification tracking per Standards.md requirements.

Implements comprehensive logging for manual state transitions with:
- Administrator identification and role verification
- High-precision timestamps with timezone awareness  
- Mandatory justification fields with minimum requirements
- Audit trail persistence and retrieval
- Integration with existing logging infrastructure
"""

import asyncio
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from enum import Enum
from dataclasses import dataclass, asdict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
import json

from app.core.logger import get_logger
from app.core.config import get_settings
from app.models.base import Base
from app.crud.crud_users import crud_user
from .state_machine import PipelineDocumentState, PipelineImageState


logger = get_logger(__name__)
settings = get_settings()


class OverrideAction(str, Enum):
    """Types of override actions that can be performed."""
    STATE_TRANSITION = "state_transition"
    RESOURCE_ALLOCATION = "resource_allocation"
    COMPLETION_THRESHOLD = "completion_threshold"
    PRIORITY_ADJUSTMENT = "priority_adjustment"
    PROCESSING_BYPASS = "processing_bypass"


class OverrideReason(str, Enum):
    """Standardized override reason categories."""
    TECHNICAL_ERROR = "technical_error"
    BUSINESS_REQUIREMENT = "business_requirement"
    DEADLINE_PRESSURE = "deadline_pressure"
    RESOURCE_CONSTRAINT = "resource_constraint"
    DATA_QUALITY_ISSUE = "data_quality_issue"
    SYSTEM_MAINTENANCE = "system_maintenance"
    EMERGENCY_PROCESSING = "emergency_processing"


@dataclass
class OverrideContext:
    """Context information for override operations."""
    document_id: Optional[int] = None
    image_id: Optional[int] = None
    original_state: Optional[str] = None
    target_state: Optional[str] = None
    resource_type: Optional[str] = None
    threshold_change: Optional[Dict[str, Any]] = None
    priority_adjustment: Optional[int] = None


class PipelineOverrideAudit(Base):
    """
    Audit trail table for pipeline state overrides.
    
    Stores comprehensive information about all manual interventions
    in the pipeline state machine for compliance and debugging.
    """
    __tablename__ = "pipeline_override_audits"
    
    id = Column(Integer, primary_key=True, index=True)
    override_id = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, index=True)
    
    # Administrator identification
    administrator_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    administrator_role = Column(String(100), nullable=False)
    administrator_ip = Column(String(45))  # Support IPv6
    
    # Override details
    action = Column(String(50), nullable=False, index=True)
    reason_category = Column(String(50), nullable=False, index=True)
    justification = Column(Text, nullable=False)  # Minimum length enforced in validation
    
    # Timing information
    requested_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    executed_at = Column(DateTime(timezone=True), index=True)
    completed_at = Column(DateTime(timezone=True))
    
    # Context and metadata
    context = Column(JSONB, nullable=False)  # OverrideContext serialized
    additional_metadata = Column(JSONB, default=dict)
    
    # Outcome tracking
    success = Column(String(20), default="pending")  # pending, success, failed
    error_message = Column(Text)
    rollback_performed = Column(String(20), default="no")  # no, partial, full
    
    # Relationships
    administrator = relationship("User", back_populates="pipeline_overrides")


class PipelineOverrideLogger:
    """
    Enhanced logging system for pipeline overrides.
    
    Provides comprehensive audit trail functionality with mandatory
    fields, validation, and integration with Standards.md logging patterns.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._minimum_justification_length = 50
        self._maximum_justification_length = 2000
    
    async def log_override_request(
        self,
        administrator_id: int,
        action: OverrideAction,
        reason: OverrideReason,
        justification: str,
        context: OverrideContext,
        administrator_ip: Optional[str] = None,
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> uuid.UUID:
        """
        Log a new override request with comprehensive validation.
        
        Args:
            administrator_id: ID of user performing override
            action: Type of override action being performed
            reason: Standardized reason category
            justification: Detailed explanation (minimum 50 characters)
            context: Override context with relevant IDs and state info
            administrator_ip: IP address of administrator (optional)
            additional_metadata: Extra context information (optional)
            
        Returns:
            UUID of created audit record
            
        Raises:
            ValueError: If validation fails
            RuntimeError: If database operation fails
        """
        # Validate justification
        if len(justification.strip()) < self._minimum_justification_length:
            raise ValueError(
                f"Justification must be at least {self._minimum_justification_length} characters. "
                f"Current length: {len(justification.strip())}"
            )
        
        if len(justification) > self._maximum_justification_length:
            raise ValueError(
                f"Justification exceeds maximum length of {self._maximum_justification_length} characters"
            )
        
        # Verify administrator exists and get role
        admin_user = await crud_user.get(self.db, id=administrator_id)
        if not admin_user:
            raise ValueError(f"Administrator with ID {administrator_id} not found")
        
        # Create audit record
        audit_record = PipelineOverrideAudit(
            administrator_id=administrator_id,
            administrator_role=admin_user.role or "unknown",
            administrator_ip=administrator_ip,
            action=action.value,
            reason_category=reason.value,
            justification=justification.strip(),
            context=asdict(context),
            additional_metadata=additional_metadata or {}
        )
        
        self.db.add(audit_record)
        await self.db.commit()
        await self.db.refresh(audit_record)
        
        # Log to application logger
        logger.warning(
            "Pipeline override requested",
            extra={
                "override_id": str(audit_record.override_id),
                "administrator_id": administrator_id,
                "administrator_role": admin_user.role,
                "action": action.value,
                "reason": reason.value,
                "context": asdict(context),
                "ip_address": administrator_ip
            }
        )
        
        return audit_record.override_id
    
    async def log_override_execution(
        self,
        override_id: uuid.UUID,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> None:
        """
        Update audit record when override execution begins.
        
        Args:
            override_id: UUID of audit record to update
            success: Whether execution was successful
            error_message: Error details if execution failed
        """
        # Find audit record
        from sqlalchemy import select
        stmt = select(PipelineOverrideAudit).where(
            PipelineOverrideAudit.override_id == override_id
        )
        result = await self.db.execute(stmt)
        audit_record = result.scalar_one_or_none()
        
        if not audit_record:
            logger.error(f"Override audit record not found: {override_id}")
            return
        
        # Update execution status
        audit_record.executed_at = datetime.now(timezone.utc)
        if not success:
            audit_record.success = "failed"
            audit_record.error_message = error_message
        
        await self.db.commit()
        
        # Log execution status
        log_level = logger.info if success else logger.error
        log_level(
            f"Pipeline override execution {'completed' if success else 'failed'}",
            extra={
                "override_id": str(override_id),
                "success": success,
                "error": error_message
            }
        )
    
    async def log_override_completion(
        self,
        override_id: uuid.UUID,
        final_success: bool = True,
        rollback_performed: str = "no"
    ) -> None:
        """
        Mark override as fully completed with final status.
        
        Args:
            override_id: UUID of audit record to update
            final_success: Final success status
            rollback_performed: Level of rollback if any ("no", "partial", "full")
        """
        from sqlalchemy import select
        stmt = select(PipelineOverrideAudit).where(
            PipelineOverrideAudit.override_id == override_id
        )
        result = await self.db.execute(stmt)
        audit_record = result.scalar_one_or_none()
        
        if not audit_record:
            logger.error(f"Override audit record not found: {override_id}")
            return
        
        # Update completion status
        audit_record.completed_at = datetime.now(timezone.utc)
        audit_record.success = "success" if final_success else "failed"
        audit_record.rollback_performed = rollback_performed
        
        await self.db.commit()
        
        # Log completion
        logger.warning(
            f"Pipeline override completed with status: {audit_record.success}",
            extra={
                "override_id": str(override_id),
                "final_success": final_success,
                "rollback_performed": rollback_performed,
                "total_duration_seconds": (
                    audit_record.completed_at - audit_record.requested_at
                ).total_seconds() if audit_record.completed_at else None
            }
        )
    
    async def get_override_history(
        self,
        document_id: Optional[int] = None,
        administrator_id: Optional[int] = None,
        action: Optional[OverrideAction] = None,
        limit: int = 100
    ) -> List[PipelineOverrideAudit]:
        """
        Retrieve override audit history with filtering options.
        
        Args:
            document_id: Filter by document ID
            administrator_id: Filter by administrator
            action: Filter by action type
            limit: Maximum number of records to return
            
        Returns:
            List of audit records matching criteria
        """
        from sqlalchemy import select, desc
        
        stmt = select(PipelineOverrideAudit).order_by(desc(PipelineOverrideAudit.requested_at))
        
        if administrator_id:
            stmt = stmt.where(PipelineOverrideAudit.administrator_id == administrator_id)
        
        if action:
            stmt = stmt.where(PipelineOverrideAudit.action == action.value)
        
        if document_id:
            stmt = stmt.where(
                PipelineOverrideAudit.context['document_id'].astext == str(document_id)
            )
        
        stmt = stmt.limit(limit)
        
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_administrator_override_stats(
        self,
        administrator_id: int,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """
        Get override statistics for a specific administrator.
        
        Args:
            administrator_id: ID of administrator to analyze
            days_back: Number of days to look back
            
        Returns:
            Dictionary with override statistics
        """
        from sqlalchemy import select, func, and_
        from datetime import timedelta
        
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_back)
        
        # Count overrides by action
        stmt = select(
            PipelineOverrideAudit.action,
            func.count(PipelineOverrideAudit.id).label('count')
        ).where(
            and_(
                PipelineOverrideAudit.administrator_id == administrator_id,
                PipelineOverrideAudit.requested_at >= cutoff_date
            )
        ).group_by(PipelineOverrideAudit.action)
        
        result = await self.db.execute(stmt)
        action_counts = {row.action: row.count for row in result}
        
        # Count success vs failure
        stmt = select(
            PipelineOverrideAudit.success,
            func.count(PipelineOverrideAudit.id).label('count')
        ).where(
            and_(
                PipelineOverrideAudit.administrator_id == administrator_id,
                PipelineOverrideAudit.requested_at >= cutoff_date
            )
        ).group_by(PipelineOverrideAudit.success)
        
        result = await self.db.execute(stmt)
        success_counts = {row.success or 'unknown': row.count for row in result}
        
        return {
            'administrator_id': administrator_id,
            'period_days': days_back,
            'total_overrides': sum(action_counts.values()),
            'overrides_by_action': action_counts,
            'success_breakdown': success_counts,
            'success_rate': (
                success_counts.get('success', 0) / max(sum(success_counts.values()), 1) * 100
            )
        }


class OverrideContextBuilder:
    """Helper class to build OverrideContext objects with validation."""
    
    @staticmethod
    def for_state_transition(
        document_id: Optional[int] = None,
        image_id: Optional[int] = None,
        original_state: Optional[str] = None,
        target_state: Optional[str] = None
    ) -> OverrideContext:
        """Build context for state transition override."""
        return OverrideContext(
            document_id=document_id,
            image_id=image_id,
            original_state=original_state,
            target_state=target_state
        )
    
    @staticmethod
    def for_resource_allocation(
        resource_type: str,
        document_id: Optional[int] = None
    ) -> OverrideContext:
        """Build context for resource allocation override."""
        return OverrideContext(
            document_id=document_id,
            resource_type=resource_type
        )
    
    @staticmethod
    def for_completion_threshold(
        document_id: int,
        threshold_change: Dict[str, Any]
    ) -> OverrideContext:
        """Build context for completion threshold override."""
        return OverrideContext(
            document_id=document_id,
            threshold_change=threshold_change
        )


# Standards.md compliance: Export main classes and functions
__all__ = [
    "OverrideAction",
    "OverrideReason", 
    "OverrideContext",
    "PipelineOverrideAudit",
    "PipelineOverrideLogger",
    "OverrideContextBuilder"
]