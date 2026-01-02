"""
Document Completion Calculator - Task 3.2A.2

Implements document completion logic per Phase 3.2A development brief:
- 90% completion threshold for READY state  
- 70% completion threshold for PARTIALLY_PROCESSED state
- Critical image completion must be 100% regardless of overall percentage
- Completion calculation: (READY + DUPLICATE_LINKED + IGNORED) / Total Images

Standards.md Compliance:
- Uses PostgreSQL persistence service patterns from P3.1
- Follows API response standards with ErrorCode enum
- Implements structured logging format
- Uses environment-based configuration patterns

Authority: PipelineStateMachine.md defines completion thresholds and state transitions
"""

import logging
from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, func, and_, or_

from .state_machine import PipelineDocumentState, PipelineImageState
from ...core.logger import get_logger
from ...core.db.database import async_engine


class DiagramType(str, Enum):
    """3-type diagram classification per Phase 3.2A brief."""
    CRITICAL = "critical"          # Title/method diagrams - completion_weight: 2.0
    SUPPORTING = "supporting"      # Detail diagrams - completion_weight: 1.0  
    DECORATIVE = "decorative"      # Logos, borders - completion_weight: 0.1


@dataclass
class ImageCompletionStatus:
    """Represents completion status of a single image."""
    image_id: str
    state: PipelineImageState
    diagram_type: DiagramType
    completion_weight: float
    is_complete: bool
    processing_started: Optional[str] = None
    last_updated: Optional[str] = None


@dataclass 
class DocumentCompletionMetrics:
    """Comprehensive document completion metrics."""
    document_id: str
    total_images: int
    completed_images: int
    completion_percentage: float
    critical_images_total: int
    critical_images_complete: int
    critical_completion_percentage: float
    weighted_completion: float
    blocked_images: int
    processing_time_hours: float
    recommended_state: PipelineDocumentState
    completion_details: Dict[str, Any]


class CompletionThresholdError(Exception):
    """Raised when completion calculation fails."""
    def __init__(self, message: str, error_code: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.error_code = error_code
        self.context = context or {}


class DocumentCompletionCalculator:
    """
    Calculates document completion status with coordination enhancements.
    
    Implements completion logic per PipelineStateMachine.md and Phase 3.2A brief:
    - 90% completion threshold for READY state
    - 70% completion threshold for PARTIALLY_PROCESSED state  
    - Critical images must be 100% complete regardless of overall percentage
    - Handles complex documents with 15-20+ diagrams
    """
    
    # Completion thresholds per Phase 3.2A requirements
    READY_THRESHOLD = 90.0
    PARTIALLY_PROCESSED_THRESHOLD = 70.0
    CRITICAL_COMPLETION_REQUIRED = 100.0
    
    # Diagram type weights per Phase 3.2A brief
    DIAGRAM_WEIGHTS = {
        DiagramType.CRITICAL: 2.0,      # Title/method diagrams count double
        DiagramType.SUPPORTING: 1.0,    # Standard weight
        DiagramType.DECORATIVE: 0.1     # Minimal weight
    }
    
    # Image states considered "complete" per PipelineStateMachine.md
    COMPLETE_STATES = {
        PipelineImageState.READY,
        PipelineImageState.DUPLICATE_LINKED,
        PipelineImageState.IGNORED,
        PipelineImageState.CANONICALIZED
    }
    
    # States that block document completion  
    BLOCKING_STATES = {
        PipelineImageState.NEEDS_HITL,
        PipelineImageState.BLOCKED
    }

    def __init__(self):
        self.logger = get_logger(__name__)
        self.session_factory = sessionmaker(
            bind=async_engine, class_=AsyncSession, expire_on_commit=False
        )

    async def calculate_completion(self, document_id: str) -> DocumentCompletionMetrics:
        """
        Calculate comprehensive document completion metrics.
        
        Args:
            document_id: Document UUID to analyze
            
        Returns:
            DocumentCompletionMetrics with completion status and recommendations
            
        Raises:
            CompletionThresholdError: If calculation fails or data is invalid
        """
        try:
            async with self.session_factory() as session:
                # Get image completion status for document
                images = await self._get_document_images(session, document_id)
                
                if not images:
                    # Document with no images is considered complete
                    return self._create_no_images_metrics(document_id)
                
                # Calculate completion metrics
                metrics = await self._calculate_metrics(document_id, images)
                
                # Determine recommended state per PipelineStateMachine.md
                metrics.recommended_state = self._determine_document_state(metrics)
                
                self.logger.info(
                    "Document completion calculated",
                    extra={
                        "document_id": document_id,
                        "completion_percentage": metrics.completion_percentage,
                        "critical_completion": metrics.critical_completion_percentage,
                        "recommended_state": metrics.recommended_state,
                        "total_images": metrics.total_images,
                        "blocked_images": metrics.blocked_images
                    }
                )
                
                return metrics
                
        except Exception as e:
            self.logger.error(
                f"Document completion calculation failed: {str(e)}",
                extra={
                    "document_id": document_id,
                    "error": str(e)
                }
            )
            raise CompletionThresholdError(
                f"Completion calculation failed for document {document_id}: {str(e)}",
                "CALCULATION_ERROR",
                {"document_id": document_id, "error": str(e)}
            )

    async def _get_document_images(
        self, 
        session: AsyncSession, 
        document_id: str
    ) -> List[ImageCompletionStatus]:
        """Get all images for document with completion status."""
        # TODO: Query actual image data from database when schema is ready
        # For now, return mock data for testing
        
        # This would be the actual query:
        # query = select(...).where(Image.document_id == document_id)
        # results = await session.execute(query)
        
        # Mock data for Phase 3.2A development
        mock_images = [
            ImageCompletionStatus(
                image_id=f"{document_id}_img_1",
                state=PipelineImageState.READY,
                diagram_type=DiagramType.CRITICAL,
                completion_weight=2.0,
                is_complete=True
            ),
            ImageCompletionStatus(
                image_id=f"{document_id}_img_2", 
                state=PipelineImageState.DUPLICATE_LINKED,
                diagram_type=DiagramType.SUPPORTING,
                completion_weight=1.0,
                is_complete=True
            ),
            ImageCompletionStatus(
                image_id=f"{document_id}_img_3",
                state=PipelineImageState.NEEDS_HITL,
                diagram_type=DiagramType.SUPPORTING,
                completion_weight=1.0,
                is_complete=False
            ),
            ImageCompletionStatus(
                image_id=f"{document_id}_img_4",
                state=PipelineImageState.IGNORED,
                diagram_type=DiagramType.DECORATIVE,
                completion_weight=0.1,
                is_complete=True
            )
        ]
        
        return mock_images

    async def _calculate_metrics(
        self, 
        document_id: str, 
        images: List[ImageCompletionStatus]
    ) -> DocumentCompletionMetrics:
        """Calculate comprehensive completion metrics."""
        
        total_images = len(images)
        completed_images = sum(1 for img in images if img.is_complete)
        
        # Critical image analysis
        critical_images = [img for img in images if img.diagram_type == DiagramType.CRITICAL]
        critical_total = len(critical_images)
        critical_complete = sum(1 for img in critical_images if img.is_complete)
        
        # Calculate completion percentages
        completion_percentage = (completed_images / total_images * 100) if total_images > 0 else 100.0
        critical_completion_percentage = (
            (critical_complete / critical_total * 100) if critical_total > 0 else 100.0
        )
        
        # Calculate weighted completion (accounts for diagram importance)
        total_weight = sum(img.completion_weight for img in images)
        completed_weight = sum(
            img.completion_weight for img in images if img.is_complete
        )
        weighted_completion = (
            (completed_weight / total_weight * 100) if total_weight > 0 else 100.0
        )
        
        # Count blocking images
        blocked_images = sum(
            1 for img in images if img.state in self.BLOCKING_STATES
        )
        
        # Calculate processing time (mock for now)
        processing_time_hours = 2.5  # TODO: Calculate from actual timestamps
        
        return DocumentCompletionMetrics(
            document_id=document_id,
            total_images=total_images,
            completed_images=completed_images,
            completion_percentage=completion_percentage,
            critical_images_total=critical_total,
            critical_images_complete=critical_complete,
            critical_completion_percentage=critical_completion_percentage,
            weighted_completion=weighted_completion,
            blocked_images=blocked_images,
            processing_time_hours=processing_time_hours,
            recommended_state=PipelineDocumentState.IMAGES_EXTRACTED,  # Will be determined
            completion_details={
                "images_by_type": self._categorize_images_by_type(images),
                "images_by_state": self._categorize_images_by_state(images),
                "blocking_reasons": self._identify_blocking_reasons(images)
            }
        )

    def _determine_document_state(self, metrics: DocumentCompletionMetrics) -> PipelineDocumentState:
        """
        Determine recommended document state per PipelineStateMachine.md thresholds.
        
        READY state requires ALL conditions per authoritative definition:
        - TEXT_EXTRACTED = complete  
        - Image completion ≥ 90% AND critical images = 100% complete
        - No BLOCKED images remaining (or explicit override)
        - Processing time < 24-hour timeout
        
        PARTIALLY_PROCESSED state triggers when:
        - Image completion ≥ 70% AND < 90%
        - Critical images = 100% complete
        - Non-critical images may remain in processing
        """
        
        # Check for blocking conditions first
        if metrics.blocked_images > 0:
            return PipelineDocumentState.BLOCKED
            
        # Check 24-hour timeout (simplified for Phase 3.2A)
        if metrics.processing_time_hours >= 24.0:
            return PipelineDocumentState.BLOCKED
            
        # Check READY state conditions
        if (metrics.completion_percentage >= self.READY_THRESHOLD and
            metrics.critical_completion_percentage >= self.CRITICAL_COMPLETION_REQUIRED):
            return PipelineDocumentState.READY
            
        # Check PARTIALLY_PROCESSED state conditions  
        if (metrics.completion_percentage >= self.PARTIALLY_PROCESSED_THRESHOLD and
            metrics.critical_completion_percentage >= self.CRITICAL_COMPLETION_REQUIRED):
            return PipelineDocumentState.PARTIALLY_PROCESSED
            
        # Still processing
        return PipelineDocumentState.IMAGES_EXTRACTED

    def _create_no_images_metrics(self, document_id: str) -> DocumentCompletionMetrics:
        """Create metrics for document with no images."""
        return DocumentCompletionMetrics(
            document_id=document_id,
            total_images=0,
            completed_images=0,
            completion_percentage=100.0,
            critical_images_total=0,
            critical_images_complete=0,
            critical_completion_percentage=100.0,
            weighted_completion=100.0,
            blocked_images=0,
            processing_time_hours=0.0,
            recommended_state=PipelineDocumentState.READY,
            completion_details={
                "images_by_type": {},
                "images_by_state": {},
                "blocking_reasons": []
            }
        )

    def _categorize_images_by_type(self, images: List[ImageCompletionStatus]) -> Dict[str, int]:
        """Categorize images by diagram type."""
        categories = {}
        for img in images:
            categories[img.diagram_type] = categories.get(img.diagram_type, 0) + 1
        return categories

    def _categorize_images_by_state(self, images: List[ImageCompletionStatus]) -> Dict[str, int]:
        """Categorize images by processing state."""
        categories = {}
        for img in images:
            categories[img.state] = categories.get(img.state, 0) + 1
        return categories

    def _identify_blocking_reasons(self, images: List[ImageCompletionStatus]) -> List[str]:
        """Identify reasons why document completion is blocked."""
        reasons = []
        
        blocked_count = sum(1 for img in images if img.state in self.BLOCKING_STATES)
        if blocked_count > 0:
            reasons.append(f"{blocked_count} images require human intervention")
            
        critical_incomplete = [
            img for img in images 
            if img.diagram_type == DiagramType.CRITICAL and not img.is_complete
        ]
        if critical_incomplete:
            reasons.append(f"{len(critical_incomplete)} critical images incomplete")
            
        return reasons

    async def check_completion_threshold(
        self, 
        document_id: str, 
        target_state: PipelineDocumentState
    ) -> Tuple[bool, DocumentCompletionMetrics]:
        """
        Check if document meets completion threshold for target state.
        
        Args:
            document_id: Document to check
            target_state: Desired target state
            
        Returns:
            Tuple of (threshold_met, completion_metrics)
        """
        metrics = await self.calculate_completion(document_id)
        threshold_met = (metrics.recommended_state == target_state or 
                        self._state_priority(metrics.recommended_state) >= self._state_priority(target_state))
        
        return threshold_met, metrics

    def _state_priority(self, state: PipelineDocumentState) -> int:
        """Get numeric priority for state comparison."""
        priorities = {
            PipelineDocumentState.INGESTED: 1,
            PipelineDocumentState.NORMALIZED: 2,
            PipelineDocumentState.TEXT_EXTRACTED: 3,
            PipelineDocumentState.IMAGES_EXTRACTED: 4,
            PipelineDocumentState.PARTIALLY_PROCESSED: 5,
            PipelineDocumentState.READY: 6,
            PipelineDocumentState.BLOCKED: 0,  # Special case - can happen at any level
            PipelineDocumentState.FAILED: 0   # Special case - terminal state
        }
        return priorities.get(state, 0)


# Export classes for use in other pipeline modules
__all__ = [
    "DiagramType",
    "ImageCompletionStatus", 
    "DocumentCompletionMetrics",
    "CompletionThresholdError",
    "DocumentCompletionCalculator"
]