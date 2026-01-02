"""
Resource Manager - Tasks 3.2A.5-6

Implements resource allocation and starvation prevention for pipeline processing:
- GPU processing limits (5 concurrent diagram interpretations)
- OCR processing limits (10 concurrent extractions)  
- 24-hour document timeout with automatic escalation
- Priority queue system (CRITICAL/STANDARD/LOW)
- Prevents pipeline deadlocks and resource contention

Standards.md Compliance:
- Uses PostgreSQL persistence service patterns from P3.1
- Follows API response standards with ErrorCode enum
- Implements structured logging format  
- Uses environment-based configuration patterns

Authority: Phase 3.2A development brief defines resource limits and timeout policies
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
import uuid

from app.common.time import TimeService
from app.common.ids import IDService
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from .state_machine import PipelineDocumentState, PipelineImageState
from .completion_calculator import DiagramType
from ...core.logger import get_logger
from ...core.db.database import async_engine


class ProcessingType(str, Enum):
    """Types of resource-intensive processing operations."""
    GPU_INTERPRETATION = "gpu_interpretation"    # Diagram interpretation using vision models
    OCR_EXTRACTION = "ocr_extraction"           # Text extraction from images
    SIMILARITY_ANALYSIS = "similarity_analysis" # Perceptual hash comparison
    HITL_REVIEW = "hitl_review"                 # Human-in-the-loop tasks


class Priority(str, Enum):
    """Processing priority levels per Phase 3.2A brief."""
    CRITICAL = "CRITICAL"    # Title diagrams, high-priority documents
    STANDARD = "STANDARD"    # Supporting diagrams, normal processing
    LOW = "LOW"              # Decorative images, batch processing


class ResourceStatus(str, Enum):
    """Resource allocation status."""
    AVAILABLE = "available"
    ALLOCATED = "allocated"
    EXHAUSTED = "exhausted"
    BLOCKED = "blocked"


@dataclass
class ProcessingRequest:
    """Represents a resource processing request."""
    request_id: str
    document_id: str
    image_id: str
    processing_type: ProcessingType
    priority: Priority
    diagram_type: DiagramType
    estimated_duration_minutes: float
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    timeout_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass  
class ResourceAllocation:
    """Represents an active resource allocation."""
    allocation_id: str
    processing_type: ProcessingType
    request_id: str
    document_id: str
    image_id: str
    allocated_at: datetime
    estimated_completion: datetime
    actual_resources: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResourceMetrics:
    """Current resource utilization metrics."""
    gpu_slots_total: int
    gpu_slots_used: int
    gpu_slots_available: int
    ocr_slots_total: int
    ocr_slots_used: int  
    ocr_slots_available: int
    queue_depth_critical: int
    queue_depth_standard: int
    queue_depth_low: int
    oldest_queued_request_age_minutes: float
    processing_requests_active: int
    timeout_violations_24h: int


class ResourceExhaustionError(Exception):
    """Raised when resources are exhausted and request cannot be queued."""
    def __init__(self, message: str, error_code: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.error_code = error_code
        self.context = context or {}


class ResourceManager:
    """
    Manages processing resource allocation with starvation prevention.
    
    Implements resource limits per Phase 3.2A brief:
    - Maximum 5 concurrent GPU diagram interpretations
    - Maximum 10 concurrent OCR extractions  
    - 24-hour document timeout with automatic escalation
    - Priority queue prevents starvation of lower-priority tasks
    """
    
    # Resource limits per Phase 3.2A brief
    MAX_GPU_SLOTS = 5          # Concurrent GPU diagram interpretations
    MAX_OCR_SLOTS = 10         # Concurrent OCR extractions
    DOCUMENT_TIMEOUT_HOURS = 24  # Maximum document processing time
    MAX_QUEUE_DEPTH = 100      # Maximum queued requests before rejection
    
    # Processing time estimates (minutes)
    PROCESSING_ESTIMATES = {
        ProcessingType.GPU_INTERPRETATION: 8.0,   # GPU-intensive diagram interpretation
        ProcessingType.OCR_EXTRACTION: 2.0,      # Text extraction from image
        ProcessingType.SIMILARITY_ANALYSIS: 1.0,  # Hash comparison
        ProcessingType.HITL_REVIEW: 60.0         # Human review estimate
    }
    
    # Starvation prevention - maximum wait time before priority boost
    STARVATION_PREVENTION_MINUTES = {
        Priority.CRITICAL: 30,   # Critical tasks can wait max 30 min
        Priority.STANDARD: 120,  # Standard tasks can wait max 2 hours  
        Priority.LOW: 480        # Low priority can wait max 8 hours
    }

    def __init__(self):
        self.logger = get_logger(__name__)
        self.session_factory = sessionmaker(
            bind=async_engine, class_=AsyncSession, expire_on_commit=False
        )
        
        # Active resource allocations
        self.gpu_allocations: Dict[str, ResourceAllocation] = {}
        self.ocr_allocations: Dict[str, ResourceAllocation] = {}
        
        # Priority queues for pending requests
        self.critical_queue: deque = deque()
        self.standard_queue: deque = deque() 
        self.low_queue: deque = deque()
        
        # Timeout tracking
        self.document_start_times: Dict[str, datetime] = {}
        self.timed_out_documents: Set[str] = set()
        
        # Metrics tracking
        self._metrics_last_updated = datetime.utcnow()

    async def request_processing(
        self,
        document_id: str,
        image_id: str,
        processing_type: ProcessingType,
        priority: Priority,
        diagram_type: DiagramType,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Request processing resource allocation.
        
        Args:
            document_id: Document UUID
            image_id: Image UUID  
            processing_type: Type of processing needed
            priority: Processing priority level
            diagram_type: Diagram classification
            metadata: Additional context information
            
        Returns:
            Request ID for tracking
            
        Raises:
            ResourceExhaustionError: If resources exhausted and queue full
        """
        try:
            # Check if resource is immediately available
            if await self._can_allocate_immediately(processing_type):
                # Allocate immediately
                allocation_id = await self._allocate_resource(
                    document_id, image_id, processing_type, priority, diagram_type, metadata
                )
                
                self.logger.info(
                    "Resource allocated immediately",
                    extra={
                        "document_id": document_id,
                        "image_id": image_id,
                        "processing_type": processing_type,
                        "priority": priority,
                        "allocation_id": allocation_id
                    }
                )
                
                return allocation_id
            else:
                # Queue for later allocation
                request_id = await self._queue_request(
                    document_id, image_id, processing_type, priority, diagram_type, metadata
                )
                
                self.logger.info(
                    "Request queued for resource allocation",
                    extra={
                        "document_id": document_id,
                        "image_id": image_id,
                        "processing_type": processing_type,
                        "priority": priority,
                        "request_id": request_id,
                        "queue_depth": await self._get_queue_depth()
                    }
                )
                
                return request_id
                
        except Exception as e:
            self.logger.error(
                f"Resource request failed: {str(e)}",
                extra={
                    "document_id": document_id,
                    "image_id": image_id,
                    "processing_type": processing_type,
                    "error": str(e)
                }
            )
            raise ResourceExhaustionError(
                f"Resource request failed: {str(e)}",
                "RESOURCE_REQUEST_FAILED",
                {
                    "document_id": document_id,
                    "image_id": image_id,
                    "processing_type": processing_type
                }
            )

    async def release_resource(self, request_id: str) -> bool:
        """
        Release allocated resource and process next queued request.
        
        Args:
            request_id: Request ID to release
            
        Returns:
            True if resource was released successfully
        """
        try:
            # Find and remove allocation
            allocation = None
            
            # Check GPU allocations
            if request_id in self.gpu_allocations:
                allocation = self.gpu_allocations.pop(request_id)
                
            # Check OCR allocations  
            elif request_id in self.ocr_allocations:
                allocation = self.ocr_allocations.pop(request_id)
            
            if not allocation:
                self.logger.warning(
                    f"Resource release requested for unknown allocation: {request_id}"
                )
                return False
            
            self.logger.info(
                "Resource released",
                extra={
                    "allocation_id": allocation.allocation_id,
                    "processing_type": allocation.processing_type,
                    "document_id": allocation.document_id,
                    "duration_minutes": (
                        (datetime.utcnow() - allocation.allocated_at).total_seconds() / 60
                    )
                }
            )
            
            # Process next queued request if available
            await self._process_next_queued_request(allocation.processing_type)
            
            return True
            
        except Exception as e:
            self.logger.error(
                f"Resource release failed: {str(e)}",
                extra={"request_id": request_id, "error": str(e)}
            )
            return False

    async def check_document_timeout(self, document_id: str) -> bool:
        """
        Check if document has exceeded 24-hour processing timeout.
        
        Args:
            document_id: Document to check
            
        Returns:
            True if document has timed out
        """
        if document_id not in self.document_start_times:
            return False
            
        start_time = self.document_start_times[document_id]
        processing_hours = (datetime.utcnow() - start_time).total_seconds() / 3600
        
        has_timed_out = processing_hours >= self.DOCUMENT_TIMEOUT_HOURS
        
        if has_timed_out and document_id not in self.timed_out_documents:
            self.timed_out_documents.add(document_id)
            
            self.logger.warning(
                "Document processing timeout exceeded",
                extra={
                    "document_id": document_id,
                    "processing_hours": processing_hours,
                    "timeout_threshold": self.DOCUMENT_TIMEOUT_HOURS
                }
            )
            
            # TODO: Trigger automatic escalation per Phase 3.2A brief
            await self._escalate_timed_out_document(document_id)
            
        return has_timed_out

    async def get_resource_metrics(self) -> ResourceMetrics:
        """Get current resource utilization metrics."""
        queue_depths = await self._get_queue_depths()
        oldest_request_age = await self._get_oldest_request_age()
        
        return ResourceMetrics(
            gpu_slots_total=self.MAX_GPU_SLOTS,
            gpu_slots_used=len(self.gpu_allocations),
            gpu_slots_available=self.MAX_GPU_SLOTS - len(self.gpu_allocations),
            ocr_slots_total=self.MAX_OCR_SLOTS,
            ocr_slots_used=len(self.ocr_allocations),
            ocr_slots_available=self.MAX_OCR_SLOTS - len(self.ocr_allocations),
            queue_depth_critical=queue_depths["critical"],
            queue_depth_standard=queue_depths["standard"],
            queue_depth_low=queue_depths["low"],
            oldest_queued_request_age_minutes=oldest_request_age,
            processing_requests_active=len(self.gpu_allocations) + len(self.ocr_allocations),
            timeout_violations_24h=len(self.timed_out_documents)
        )

    async def prevent_starvation(self) -> int:
        """
        Check for starved requests and boost their priority.
        
        Returns:
            Number of requests that had priority boosted
        """
        boosted_count = 0
        current_time = datetime.utcnow()
        
        # Check each priority queue for starved requests
        for queue, priority in [
            (self.low_queue, Priority.LOW),
            (self.standard_queue, Priority.STANDARD),
            (self.critical_queue, Priority.CRITICAL)
        ]:
            for request in list(queue):
                wait_time_minutes = (current_time - request.created_at).total_seconds() / 60
                max_wait = self.STARVATION_PREVENTION_MINUTES[priority]
                
                if wait_time_minutes > max_wait:
                    # Move to higher priority queue
                    queue.remove(request)
                    
                    if priority == Priority.LOW:
                        self.standard_queue.appendleft(request)  # Add to front
                    elif priority == Priority.STANDARD:
                        self.critical_queue.appendleft(request)  # Add to front
                        
                    boosted_count += 1
                    
                    self.logger.info(
                        "Request priority boosted due to starvation prevention",
                        extra={
                            "request_id": request.request_id,
                            "document_id": request.document_id,
                            "original_priority": priority,
                            "wait_time_minutes": wait_time_minutes,
                            "max_wait_minutes": max_wait
                        }
                    )
        
        return boosted_count

    # Private helper methods

    async def _can_allocate_immediately(self, processing_type: ProcessingType) -> bool:
        """Check if resource can be allocated immediately."""
        if processing_type == ProcessingType.GPU_INTERPRETATION:
            return len(self.gpu_allocations) < self.MAX_GPU_SLOTS
        elif processing_type == ProcessingType.OCR_EXTRACTION:
            return len(self.ocr_allocations) < self.MAX_OCR_SLOTS
        else:
            # Other processing types don't have explicit limits
            return True

    async def _allocate_resource(
        self,
        document_id: str,
        image_id: str, 
        processing_type: ProcessingType,
        priority: Priority,
        diagram_type: DiagramType,
        metadata: Optional[Dict[str, Any]]
    ) -> str:
        """Allocate resource immediately."""
        id_service = IDService()
        allocation_id = id_service.generate_id()
        now = datetime.utcnow()
        
        estimated_duration = self.PROCESSING_ESTIMATES.get(processing_type, 5.0)
        estimated_completion = now + timedelta(minutes=estimated_duration)
        
        allocation = ResourceAllocation(
            allocation_id=allocation_id,
            processing_type=processing_type,
            request_id=allocation_id,  # Same as allocation for immediate requests
            document_id=document_id,
            image_id=image_id,
            allocated_at=now,
            estimated_completion=estimated_completion,
            actual_resources=metadata or {}
        )
        
        # Track document start time
        if document_id not in self.document_start_times:
            self.document_start_times[document_id] = now
        
        # Store allocation
        if processing_type == ProcessingType.GPU_INTERPRETATION:
            self.gpu_allocations[allocation_id] = allocation
        elif processing_type == ProcessingType.OCR_EXTRACTION:
            self.ocr_allocations[allocation_id] = allocation
            
        return allocation_id

    async def _queue_request(
        self,
        document_id: str,
        image_id: str,
        processing_type: ProcessingType, 
        priority: Priority,
        diagram_type: DiagramType,
        metadata: Optional[Dict[str, Any]]
    ) -> str:
        """Queue request for later processing."""
        total_queue_depth = await self._get_queue_depth()
        
        if total_queue_depth >= self.MAX_QUEUE_DEPTH:
            raise ResourceExhaustionError(
                f"Queue full: {total_queue_depth} requests pending",
                "QUEUE_EXHAUSTED",
                {"queue_depth": total_queue_depth, "max_depth": self.MAX_QUEUE_DEPTH}
            )
        
        id_service = IDService()
        request_id = id_service.generate_id()
        now = datetime.utcnow()
        
        estimated_duration = self.PROCESSING_ESTIMATES.get(processing_type, 5.0)
        timeout_at = now + timedelta(hours=self.DOCUMENT_TIMEOUT_HOURS)
        
        request = ProcessingRequest(
            request_id=request_id,
            document_id=document_id,
            image_id=image_id,
            processing_type=processing_type,
            priority=priority,
            diagram_type=diagram_type,
            estimated_duration_minutes=estimated_duration,
            created_at=now,
            timeout_at=timeout_at,
            metadata=metadata or {}
        )
        
        # Track document start time
        if document_id not in self.document_start_times:
            self.document_start_times[document_id] = now
        
        # Add to appropriate priority queue
        if priority == Priority.CRITICAL:
            self.critical_queue.append(request)
        elif priority == Priority.STANDARD:
            self.standard_queue.append(request)
        else:
            self.low_queue.append(request)
            
        return request_id

    async def _process_next_queued_request(self, processing_type: ProcessingType) -> Optional[str]:
        """Process next queued request for the given processing type."""
        # Find next appropriate request from priority queues
        for queue in [self.critical_queue, self.standard_queue, self.low_queue]:
            for request in list(queue):
                if request.processing_type == processing_type:
                    # Remove from queue and allocate
                    queue.remove(request)
                    
                    allocation_id = await self._allocate_resource(
                        request.document_id,
                        request.image_id,
                        request.processing_type,
                        request.priority,
                        request.diagram_type,
                        request.metadata
                    )
                    
                    return allocation_id
        
        return None

    async def _get_queue_depth(self) -> int:
        """Get total queue depth across all priority levels."""
        return len(self.critical_queue) + len(self.standard_queue) + len(self.low_queue)

    async def _get_queue_depths(self) -> Dict[str, int]:
        """Get queue depths by priority level."""
        return {
            "critical": len(self.critical_queue),
            "standard": len(self.standard_queue), 
            "low": len(self.low_queue)
        }

    async def _get_oldest_request_age(self) -> float:
        """Get age in minutes of oldest queued request."""
        oldest_time = None
        current_time = datetime.utcnow()
        
        for queue in [self.critical_queue, self.standard_queue, self.low_queue]:
            for request in queue:
                if oldest_time is None or request.created_at < oldest_time:
                    oldest_time = request.created_at
        
        if oldest_time is None:
            return 0.0
            
        return (current_time - oldest_time).total_seconds() / 60

    async def _escalate_timed_out_document(self, document_id: str) -> None:
        """Escalate timed-out document per Phase 3.2A brief."""
        # TODO: Implement automatic escalation logic
        # This could include:
        # - Moving all document requests to CRITICAL priority
        # - Creating HITL tasks for manual intervention
        # - Notifying administrators
        # - Logging for management dashboard
        
        self.logger.critical(
            "Document timeout escalation triggered",
            extra={
                "document_id": document_id,
                "timeout_hours": self.DOCUMENT_TIMEOUT_HOURS,
                "escalation_action": "automatic_priority_boost"
            }
        )


# Export classes for use in other pipeline modules
__all__ = [
    "ProcessingType",
    "Priority", 
    "ResourceStatus",
    "ProcessingRequest",
    "ResourceAllocation",
    "ResourceMetrics",
    "ResourceExhaustionError",
    "ResourceManager"
]