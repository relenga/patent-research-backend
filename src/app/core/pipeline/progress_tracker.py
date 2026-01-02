"""
Phase 3.2A Task 3.2A.9: Pipeline Progress Tracking System

Detailed progress tracking with percentage completion, resource utilization metrics,
and processing statistics for comprehensive pipeline monitoring and optimization.

Implements comprehensive progress monitoring with:
- Real-time completion percentage calculation
- Resource utilization tracking across GPU/OCR/CPU
- Processing statistics and performance metrics
- Historical trend analysis and forecasting
- Dashboard data aggregation and visualization support
"""

import asyncio
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List, Tuple
from enum import Enum
from dataclasses import dataclass, field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Column, Integer, String, DateTime, Float, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy import func, select, and_, or_
import uuid
import statistics
from collections import defaultdict, deque

from app.core.logger import get_logger
from app.core.config import get_settings
from app.models.base import Base
from .state_machine import PipelineDocumentState, PipelineImageState
from .completion_calculator import DocumentCompletionCalculator, DocumentCompletionMetrics
from .resource_manager import ResourceType, ResourceManager


logger = get_logger(__name__)
settings = get_settings()


class TrackingPeriod(str, Enum):
    """Time periods for progress tracking aggregation."""
    HOURLY = "hourly"
    DAILY = "daily" 
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class PerformanceMetricType(str, Enum):
    """Types of performance metrics tracked."""
    PROCESSING_SPEED = "processing_speed"  # images per hour
    RESOURCE_EFFICIENCY = "resource_efficiency"  # utilization percentage
    ERROR_RATE = "error_rate"  # errors per total operations
    COMPLETION_RATE = "completion_rate"  # documents completed per period
    THROUGHPUT = "throughput"  # total operations per period
    LATENCY = "latency"  # average processing time per operation


@dataclass
class ResourceUtilization:
    """Current resource utilization snapshot."""
    timestamp: datetime
    gpu_slots_used: int
    gpu_slots_total: int
    ocr_slots_used: int
    ocr_slots_total: int
    cpu_utilization: float  # 0.0 to 1.0
    memory_utilization: float  # 0.0 to 1.0
    queue_lengths: Dict[str, int] = field(default_factory=dict)
    
    @property
    def gpu_utilization(self) -> float:
        """Calculate GPU utilization percentage."""
        if self.gpu_slots_total == 0:
            return 0.0
        return self.gpu_slots_used / self.gpu_slots_total
    
    @property 
    def ocr_utilization(self) -> float:
        """Calculate OCR utilization percentage."""
        if self.ocr_slots_total == 0:
            return 0.0
        return self.ocr_slots_used / self.ocr_slots_total
    
    @property
    def overall_utilization(self) -> float:
        """Calculate overall system utilization."""
        utilizations = [
            self.gpu_utilization,
            self.ocr_utilization,
            self.cpu_utilization,
            self.memory_utilization
        ]
        return statistics.mean(utilizations)


@dataclass
class ProcessingStatistics:
    """Processing performance statistics for a time period."""
    period_start: datetime
    period_end: datetime
    
    # Volume metrics
    documents_started: int = 0
    documents_completed: int = 0
    images_processed: int = 0
    total_operations: int = 0
    
    # Performance metrics
    average_document_time: Optional[float] = None  # seconds
    average_image_time: Optional[float] = None  # seconds
    processing_speed: Optional[float] = None  # operations per hour
    
    # Quality metrics
    error_count: int = 0
    retry_count: int = 0
    manual_interventions: int = 0
    
    # Resource metrics
    peak_gpu_utilization: float = 0.0
    average_gpu_utilization: float = 0.0
    peak_ocr_utilization: float = 0.0
    average_ocr_utilization: float = 0.0
    
    @property
    def completion_rate(self) -> float:
        """Calculate completion rate percentage."""
        if self.documents_started == 0:
            return 0.0
        return (self.documents_completed / self.documents_started) * 100
    
    @property
    def error_rate(self) -> float:
        """Calculate error rate percentage."""
        if self.total_operations == 0:
            return 0.0
        return (self.error_count / self.total_operations) * 100
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        return 100.0 - self.error_rate


class PipelineProgressSnapshot(Base):
    """
    Progress tracking table for pipeline processing snapshots.
    
    Stores periodic snapshots of pipeline progress and performance
    for monitoring, analysis, and forecasting capabilities.
    """
    __tablename__ = "pipeline_progress_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    snapshot_id = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, index=True)
    
    # Timing information
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    period = Column(String(20), nullable=False, index=True)  # TrackingPeriod
    
    # Progress metrics
    total_documents = Column(Integer, default=0)
    completed_documents = Column(Integer, default=0)
    in_progress_documents = Column(Integer, default=0)
    failed_documents = Column(Integer, default=0)
    
    total_images = Column(Integer, default=0)
    processed_images = Column(Integer, default=0)
    pending_images = Column(Integer, default=0)
    
    # Resource utilization
    resource_utilization = Column(JSONB, default=dict)  # ResourceUtilization data
    
    # Performance statistics
    processing_stats = Column(JSONB, default=dict)  # ProcessingStatistics data
    
    # Additional metrics
    completion_percentage = Column(Float, default=0.0)
    projected_completion_time = Column(DateTime(timezone=True))
    additional_metrics = Column(JSONB, default=dict)


class PipelineProgressTracker:
    """
    Comprehensive progress tracking system for pipeline operations.
    
    Provides real-time monitoring, historical analysis, and performance
    forecasting for pipeline processing activities.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._resource_manager: Optional[ResourceManager] = None
        self._completion_calculator: Optional[DocumentCompletionCalculator] = None
        
        # In-memory tracking for real-time metrics
        self._recent_utilizations: deque = deque(maxlen=60)  # Last 60 measurements
        self._processing_times: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self._current_operations: Dict[str, datetime] = {}
        
    def set_resource_manager(self, resource_manager: ResourceManager):
        """Set resource manager for utilization tracking."""
        self._resource_manager = resource_manager
    
    def set_completion_calculator(self, completion_calculator: DocumentCompletionCalculator):
        """Set completion calculator for progress metrics."""
        self._completion_calculator = completion_calculator
    
    async def capture_progress_snapshot(
        self,
        period: TrackingPeriod = TrackingPeriod.HOURLY
    ) -> uuid.UUID:
        """
        Capture a comprehensive progress snapshot.
        
        Args:
            period: Time period for snapshot aggregation
            
        Returns:
            UUID of created snapshot record
        """
        # Get current resource utilization
        resource_util = await self._get_current_resource_utilization()
        
        # Calculate document progress
        document_progress = await self._calculate_document_progress()
        
        # Calculate image progress  
        image_progress = await self._calculate_image_progress()
        
        # Generate processing statistics
        processing_stats = await self._calculate_processing_statistics(period)
        
        # Calculate overall completion percentage
        completion_pct = await self._calculate_overall_completion()
        
        # Project completion time
        projected_completion = await self._project_completion_time()
        
        # Create snapshot record
        snapshot = PipelineProgressSnapshot(
            timestamp=datetime.now(timezone.utc),
            period=period.value,
            total_documents=document_progress['total'],
            completed_documents=document_progress['completed'],
            in_progress_documents=document_progress['in_progress'],
            failed_documents=document_progress['failed'],
            total_images=image_progress['total'],
            processed_images=image_progress['processed'],
            pending_images=image_progress['pending'],
            resource_utilization=resource_util.__dict__ if resource_util else {},
            processing_stats=processing_stats.__dict__ if processing_stats else {},
            completion_percentage=completion_pct,
            projected_completion_time=projected_completion
        )
        
        self.db.add(snapshot)
        await self.db.commit()
        await self.db.refresh(snapshot)
        
        logger.info(
            f"Progress snapshot captured: {completion_pct:.1f}% complete",
            extra={
                "snapshot_id": str(snapshot.snapshot_id),
                "period": period.value,
                "completion_percentage": completion_pct,
                "documents_completed": document_progress['completed'],
                "total_documents": document_progress['total']
            }
        )
        
        return snapshot.snapshot_id
    
    async def _get_current_resource_utilization(self) -> Optional[ResourceUtilization]:
        """Get current resource utilization snapshot."""
        if not self._resource_manager:
            return None
        
        try:
            # Get resource status from resource manager
            status = await self._resource_manager.get_resource_status()
            
            # Create utilization snapshot
            resource_util = ResourceUtilization(
                timestamp=datetime.now(timezone.utc),
                gpu_slots_used=status.get('gpu_slots_used', 0),
                gpu_slots_total=status.get('gpu_slots_total', 0),
                ocr_slots_used=status.get('ocr_slots_used', 0), 
                ocr_slots_total=status.get('ocr_slots_total', 0),
                cpu_utilization=status.get('cpu_utilization', 0.0),
                memory_utilization=status.get('memory_utilization', 0.0),
                queue_lengths=status.get('queue_lengths', {})
            )
            
            # Store in recent utilizations for trending
            self._recent_utilizations.append(resource_util)
            
            return resource_util
        
        except Exception as e:
            logger.warning(f"Could not get resource utilization: {e}")
            return None
    
    async def _calculate_document_progress(self) -> Dict[str, int]:
        """Calculate document processing progress."""
        try:
            # Query document states from state machine tables
            from app.models.pipeline import PipelineDocument  # Assumes this exists
            
            stmt = select(
                func.count().label('total'),
                func.sum(
                    func.case(
                        (PipelineDocument.state == PipelineDocumentState.COMPLETED.value, 1),
                        else_=0
                    )
                ).label('completed'),
                func.sum(
                    func.case(
                        (PipelineDocument.state.in_([
                            PipelineDocumentState.PROCESSING.value,
                            PipelineDocumentState.PENDING_IMAGES.value,
                            PipelineDocumentState.ANALYZING_IMAGES.value
                        ]), 1),
                        else_=0
                    )
                ).label('in_progress'),
                func.sum(
                    func.case(
                        (PipelineDocument.state == PipelineDocumentState.FAILED.value, 1),
                        else_=0
                    )
                ).label('failed')
            )
            
            result = await self.db.execute(stmt)
            row = result.first()
            
            return {
                'total': row.total or 0,
                'completed': row.completed or 0,
                'in_progress': row.in_progress or 0,
                'failed': row.failed or 0
            }
            
        except Exception as e:
            logger.warning(f"Could not calculate document progress: {e}")
            return {'total': 0, 'completed': 0, 'in_progress': 0, 'failed': 0}
    
    async def _calculate_image_progress(self) -> Dict[str, int]:
        """Calculate image processing progress."""
        try:
            # Query image states from state machine tables
            from app.models.pipeline import PipelineImage  # Assumes this exists
            
            stmt = select(
                func.count().label('total'),
                func.sum(
                    func.case(
                        (PipelineImage.state.in_([
                            PipelineImageState.PROCESSED.value,
                            PipelineImageState.ANALYZED.value
                        ]), 1),
                        else_=0
                    )
                ).label('processed'),
                func.sum(
                    func.case(
                        (PipelineImage.state.in_([
                            PipelineImageState.DISCOVERED.value,
                            PipelineImageState.QUEUED.value
                        ]), 1),
                        else_=0
                    )
                ).label('pending')
            )
            
            result = await self.db.execute(stmt)
            row = result.first()
            
            return {
                'total': row.total or 0,
                'processed': row.processed or 0,
                'pending': row.pending or 0
            }
            
        except Exception as e:
            logger.warning(f"Could not calculate image progress: {e}")
            return {'total': 0, 'processed': 0, 'pending': 0}
    
    async def _calculate_processing_statistics(
        self,
        period: TrackingPeriod
    ) -> Optional[ProcessingStatistics]:
        """Calculate processing statistics for the given period."""
        try:
            # Determine time window
            now = datetime.now(timezone.utc)
            if period == TrackingPeriod.HOURLY:
                start_time = now - timedelta(hours=1)
            elif period == TrackingPeriod.DAILY:
                start_time = now - timedelta(days=1)
            elif period == TrackingPeriod.WEEKLY:
                start_time = now - timedelta(weeks=1)
            else:  # MONTHLY
                start_time = now - timedelta(days=30)
            
            # Calculate resource utilization averages
            recent_utils = [u for u in self._recent_utilizations if u.timestamp >= start_time]
            
            avg_gpu_util = 0.0
            peak_gpu_util = 0.0
            avg_ocr_util = 0.0
            peak_ocr_util = 0.0
            
            if recent_utils:
                gpu_utils = [u.gpu_utilization for u in recent_utils]
                ocr_utils = [u.ocr_utilization for u in recent_utils]
                
                avg_gpu_util = statistics.mean(gpu_utils)
                peak_gpu_util = max(gpu_utils)
                avg_ocr_util = statistics.mean(ocr_utils)
                peak_ocr_util = max(ocr_utils)
            
            # Create statistics object
            stats = ProcessingStatistics(
                period_start=start_time,
                period_end=now,
                average_gpu_utilization=avg_gpu_util,
                peak_gpu_utilization=peak_gpu_util,
                average_ocr_utilization=avg_ocr_util,
                peak_ocr_utilization=peak_ocr_util
            )
            
            return stats
            
        except Exception as e:
            logger.warning(f"Could not calculate processing statistics: {e}")
            return None
    
    async def _calculate_overall_completion(self) -> float:
        """Calculate overall pipeline completion percentage."""
        try:
            if not self._completion_calculator:
                return 0.0
            
            # Get all active documents and calculate weighted completion
            from app.models.pipeline import PipelineDocument
            
            stmt = select(PipelineDocument).where(
                PipelineDocument.state != PipelineDocumentState.FAILED.value
            )
            result = await self.db.execute(stmt)
            documents = result.scalars().all()
            
            if not documents:
                return 100.0  # No documents means 100% complete
            
            total_completion = 0.0
            for doc in documents:
                doc_metrics = await self._completion_calculator.calculate_completion(
                    document_id=doc.id
                )
                total_completion += doc_metrics.completion_percentage
            
            return total_completion / len(documents)
            
        except Exception as e:
            logger.warning(f"Could not calculate overall completion: {e}")
            return 0.0
    
    async def _project_completion_time(self) -> Optional[datetime]:
        """Project estimated completion time based on current progress."""
        try:
            # Get recent processing rates
            if len(self._recent_utilizations) < 2:
                return None
            
            # Calculate processing velocity (documents completed per hour)
            recent_snapshots = await self.get_recent_snapshots(hours=24, limit=24)
            if len(recent_snapshots) < 2:
                return None
            
            # Calculate completion rate trend
            completion_rates = []
            for i in range(1, len(recent_snapshots)):
                prev = recent_snapshots[i-1]
                curr = recent_snapshots[i]
                time_diff = (curr.timestamp - prev.timestamp).total_seconds() / 3600  # hours
                
                if time_diff > 0:
                    docs_completed = curr.completed_documents - prev.completed_documents
                    rate = docs_completed / time_diff if time_diff > 0 else 0
                    completion_rates.append(max(0, rate))  # Ensure non-negative
            
            if not completion_rates:
                return None
            
            # Use average completion rate
            avg_rate = statistics.mean(completion_rates)
            if avg_rate <= 0:
                return None
            
            # Get current progress
            doc_progress = await self._calculate_document_progress()
            remaining_docs = doc_progress['total'] - doc_progress['completed']
            
            if remaining_docs <= 0:
                return datetime.now(timezone.utc)  # Already complete
            
            # Project completion time
            hours_remaining = remaining_docs / avg_rate
            projected_time = datetime.now(timezone.utc) + timedelta(hours=hours_remaining)
            
            return projected_time
            
        except Exception as e:
            logger.warning(f"Could not project completion time: {e}")
            return None
    
    async def get_recent_snapshots(
        self,
        hours: int = 24,
        limit: int = 100
    ) -> List[PipelineProgressSnapshot]:
        """Get recent progress snapshots."""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        stmt = select(PipelineProgressSnapshot).where(
            PipelineProgressSnapshot.timestamp >= cutoff_time
        ).order_by(PipelineProgressSnapshot.timestamp.desc()).limit(limit)
        
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_performance_trends(
        self,
        metric_type: PerformanceMetricType,
        days: int = 7
    ) -> List[Tuple[datetime, float]]:
        """Get performance trend data for charting."""
        cutoff_time = datetime.now(timezone.utc) - timedelta(days=days)
        
        stmt = select(PipelineProgressSnapshot).where(
            PipelineProgressSnapshot.timestamp >= cutoff_time
        ).order_by(PipelineProgressSnapshot.timestamp)
        
        result = await self.db.execute(stmt)
        snapshots = result.scalars().all()
        
        trends = []
        for snapshot in snapshots:
            value = self._extract_metric_value(snapshot, metric_type)
            if value is not None:
                trends.append((snapshot.timestamp, value))
        
        return trends
    
    def _extract_metric_value(
        self,
        snapshot: PipelineProgressSnapshot,
        metric_type: PerformanceMetricType
    ) -> Optional[float]:
        """Extract specific metric value from snapshot."""
        try:
            if metric_type == PerformanceMetricType.COMPLETION_RATE:
                return snapshot.completion_percentage
            
            elif metric_type == PerformanceMetricType.PROCESSING_SPEED:
                stats = snapshot.processing_stats
                return stats.get('processing_speed') if stats else None
            
            elif metric_type == PerformanceMetricType.RESOURCE_EFFICIENCY:
                resource_util = snapshot.resource_utilization
                if resource_util:
                    return (
                        resource_util.get('gpu_utilization', 0) +
                        resource_util.get('ocr_utilization', 0)
                    ) / 2
            
            elif metric_type == PerformanceMetricType.ERROR_RATE:
                stats = snapshot.processing_stats
                return stats.get('error_rate') if stats else None
            
            # Add other metric extractions as needed
            
        except Exception as e:
            logger.warning(f"Could not extract metric {metric_type}: {e}")
        
        return None
    
    def track_operation_start(self, operation_id: str):
        """Track the start of a processing operation."""
        self._current_operations[operation_id] = datetime.now(timezone.utc)
    
    def track_operation_end(self, operation_id: str, operation_type: str = "generic"):
        """Track the end of a processing operation."""
        if operation_id in self._current_operations:
            start_time = self._current_operations.pop(operation_id)
            duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            self._processing_times[operation_type].append(duration)


# Standards.md compliance: Export main classes and functions
__all__ = [
    "TrackingPeriod",
    "PerformanceMetricType",
    "ResourceUtilization",
    "ProcessingStatistics", 
    "PipelineProgressSnapshot",
    "PipelineProgressTracker"
]