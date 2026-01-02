"""
Phase 3.2A Pipeline Coordination Integration Module

Main integration point for all pipeline coordination components,
providing unified interface for pipeline state machine execution
with coordination enhancements for complex documents.

This module integrates:
- State machine execution engine
- Document completion calculation with 90%/70% thresholds
- Diagram classification and similarity analysis
- Resource management with GPU/OCR limits and starvation prevention
- Enhanced override logging with audit trails
- Real-time event publishing system
- Comprehensive progress tracking
- Secure manual state transition overrides

Standards.md Compliance: All components follow established patterns
for async operations, logging, error handling, and API design.
"""

import asyncio
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import get_logger
from app.core.config import get_settings

# Import all pipeline coordination components
from .state_machine import PipelineStateExecutor, StateTransition
from .completion_calculator import DocumentCompletionCalculator
from .coordination import PipelineCoordinator
from .resource_manager import ResourceManager, ResourceType, ProcessingPriority
from .override_logging import PipelineOverrideLogger
from .event_publisher import EventPublisher, EventPayloadBuilder, EventPriority
from .progress_tracker import PipelineProgressTracker, TrackingPeriod
from .manual_overrides import ManualOverrideSystem, OverrideRequest


logger = get_logger(__name__)
settings = get_settings()


@dataclass
class PipelineConfiguration:
    """Configuration for pipeline coordination system."""
    max_gpu_slots: int = 4
    max_ocr_slots: int = 8
    starvation_timeout_hours: int = 24
    completion_threshold_primary: float = 90.0
    completion_threshold_secondary: float = 70.0
    enable_event_publishing: bool = True
    enable_progress_tracking: bool = True
    progress_snapshot_interval_minutes: int = 15


class PipelineCoordinationSystem:
    """
    Main pipeline coordination system integrating all Phase 3.2A components.
    
    Provides unified interface for complex document processing with:
    - Intelligent state machine coordination
    - Resource-aware processing decisions
    - Comprehensive monitoring and override capabilities
    - Real-time progress tracking and event publishing
    """
    
    def __init__(self, db: AsyncSession, config: Optional[PipelineConfiguration] = None):
        self.db = db
        self.config = config or PipelineConfiguration()
        
        # Initialize core components
        self.state_executor = PipelineStateExecutor()
        self.completion_calculator = DocumentCompletionCalculator(db)
        self.coordinator = PipelineCoordinator(db)
        self.resource_manager = ResourceManager(
            max_gpu_slots=self.config.max_gpu_slots,
            max_ocr_slots=self.config.max_ocr_slots,
            starvation_timeout_hours=self.config.starvation_timeout_hours
        )
        
        # Initialize monitoring and override systems
        self.override_logger = PipelineOverrideLogger(db)
        self.event_publisher: Optional[EventPublisher] = None
        self.progress_tracker: Optional[PipelineProgressTracker] = None
        self.manual_override_system: Optional[ManualOverrideSystem] = None
        
        # Background tasks
        self._progress_task: Optional[asyncio.Task] = None
        self._starvation_check_task: Optional[asyncio.Task] = None
        
    async def initialize(self) -> None:
        """Initialize the pipeline coordination system."""
        logger.info("Initializing Pipeline Coordination System")
        
        # Initialize event publishing
        if self.config.enable_event_publishing:
            self.event_publisher = EventPublisher(self.db)
            await self.event_publisher.start()
            logger.info("Event publishing system initialized")
        
        # Initialize progress tracking
        if self.config.enable_progress_tracking:
            self.progress_tracker = PipelineProgressTracker(self.db)
            self.progress_tracker.set_resource_manager(self.resource_manager)
            self.progress_tracker.set_completion_calculator(self.completion_calculator)
            logger.info("Progress tracking system initialized")
        
        # Initialize manual override system
        if self.event_publisher:
            self.manual_override_system = ManualOverrideSystem(
                db=self.db,
                state_executor=self.state_executor,
                override_logger=self.override_logger,
                event_publisher=self.event_publisher
            )
            logger.info("Manual override system initialized")
        
        # Start background tasks
        await self._start_background_tasks()
        
        logger.info("Pipeline Coordination System fully initialized")
    
    async def shutdown(self) -> None:
        """Shutdown the pipeline coordination system."""
        logger.info("Shutting down Pipeline Coordination System")
        
        # Stop background tasks
        if self._progress_task:
            self._progress_task.cancel()
            try:
                await self._progress_task
            except asyncio.CancelledError:
                pass
        
        if self._starvation_check_task:
            self._starvation_check_task.cancel()
            try:
                await self._starvation_check_task
            except asyncio.CancelledError:
                pass
        
        # Shutdown event publisher
        if self.event_publisher:
            await self.event_publisher.stop()
        
        logger.info("Pipeline Coordination System shutdown complete")
    
    async def process_document(
        self,
        document_id: int,
        priority: ProcessingPriority = ProcessingPriority.NORMAL
    ) -> bool:
        """
        Process a document through the coordination pipeline.
        
        Args:
            document_id: ID of document to process
            priority: Processing priority level
            
        Returns:
            True if processing started successfully, False otherwise
        """
        try:
            logger.info(f"Starting coordinated processing for document {document_id}")
            
            # 1. Check if document should be processed immediately
            should_process = await self.coordinator.should_process_immediately(
                document_id=document_id
            )
            
            if not should_process:
                logger.info(f"Document {document_id} queued for later processing")
                return True
            
            # 2. Allocate resources
            resource_allocation = await self.resource_manager.allocate_resource(
                resource_type=ResourceType.GPU,
                document_id=document_id,
                priority=priority,
                estimated_duration=1800  # 30 minutes default
            )
            
            if not resource_allocation:
                logger.warning(f"No resources available for document {document_id}")
                return False
            
            # 3. Execute state transition
            transition = StateTransition(
                entity_type="document",
                entity_id=document_id,
                from_state="uploaded",  # Would get actual current state
                to_state="processing",
                trigger="start_coordinated_processing",
                metadata={
                    'priority': priority.value,
                    'resource_allocation_id': str(resource_allocation.allocation_id),
                    'coordination_enabled': True
                }
            )
            
            success = await self.state_executor.execute_transition(transition, self.db)
            
            if not success:
                # Release resources if state transition failed
                await self.resource_manager.release_resource(
                    ResourceType.GPU, 
                    document_id
                )
                logger.error(f"State transition failed for document {document_id}")
                return False
            
            # 4. Publish processing started event
            if self.event_publisher:
                event_payload = EventPayloadBuilder.processing_started(
                    document_id=document_id,
                    priority=EventPriority.NORMAL,
                    metadata={
                        'coordination_enabled': True,
                        'resource_type': ResourceType.GPU.value,
                        'priority': priority.value
                    }
                )
                await self.event_publisher.publish_event(event_payload)
            
            # 5. Track operation start
            if self.progress_tracker:
                self.progress_tracker.track_operation_start(f"document_{document_id}")
            
            logger.info(f"Coordinated processing started for document {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start coordinated processing for document {document_id}: {e}")
            return False
    
    async def check_completion(self, document_id: int) -> Dict[str, Any]:
        """
        Check document completion status using coordination logic.
        
        Args:
            document_id: ID of document to check
            
        Returns:
            Dictionary with completion status and recommendations
        """
        try:
            # Calculate completion metrics
            completion_metrics = await self.completion_calculator.calculate_completion(
                document_id=document_id
            )
            
            # Get state recommendation
            current_state = "processing"  # Would get actual current state
            recommended_state = await self.completion_calculator.recommend_next_state(
                document_id=document_id,
                current_state=current_state
            )
            
            # Check if coordination decisions affect completion
            coordination_decision = await self.coordinator.should_process_immediately(
                document_id=document_id
            )
            
            result = {
                'document_id': document_id,
                'completion_percentage': completion_metrics.completion_percentage,
                'critical_images_processed': completion_metrics.critical_images_processed,
                'total_critical_images': completion_metrics.total_critical_images,
                'meets_primary_threshold': completion_metrics.completion_percentage >= self.config.completion_threshold_primary,
                'meets_secondary_threshold': completion_metrics.completion_percentage >= self.config.completion_threshold_secondary,
                'recommended_state': recommended_state,
                'coordination_decision': coordination_decision,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            # Publish completion change event
            if self.event_publisher:
                event_payload = EventPayloadBuilder.completion_change(
                    document_id=document_id,
                    completion_percentage=completion_metrics.completion_percentage,
                    priority=EventPriority.NORMAL,
                    metadata=result
                )
                await self.event_publisher.publish_event(event_payload)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to check completion for document {document_id}: {e}")
            return {
                'document_id': document_id,
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    async def request_manual_override(self, request: OverrideRequest) -> Optional[str]:
        """
        Request manual state transition override.
        
        Args:
            request: Override request details
            
        Returns:
            Override ID if successful, None otherwise
        """
        if not self.manual_override_system:
            logger.error("Manual override system not available")
            return None
        
        try:
            override_id = await self.manual_override_system.request_override(request)
            logger.info(f"Manual override requested: {override_id}")
            return str(override_id)
            
        except Exception as e:
            logger.error(f"Manual override request failed: {e}")
            return None
    
    async def get_system_status(self) -> Dict[str, Any]:
        """
        Get comprehensive system status.
        
        Returns:
            Dictionary with current system status
        """
        try:
            status = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'system_initialized': True,
                'configuration': {
                    'max_gpu_slots': self.config.max_gpu_slots,
                    'max_ocr_slots': self.config.max_ocr_slots,
                    'completion_thresholds': {
                        'primary': self.config.completion_threshold_primary,
                        'secondary': self.config.completion_threshold_secondary
                    }
                }
            }
            
            # Add resource status
            resource_status = await self.resource_manager.get_resource_status()
            status['resources'] = resource_status
            
            # Add progress tracking status
            if self.progress_tracker:
                recent_snapshots = await self.progress_tracker.get_recent_snapshots(hours=1, limit=5)
                status['recent_progress'] = [
                    {
                        'timestamp': snapshot.timestamp.isoformat(),
                        'completion_percentage': snapshot.completion_percentage,
                        'total_documents': snapshot.total_documents,
                        'completed_documents': snapshot.completed_documents
                    }
                    for snapshot in recent_snapshots
                ]
            
            # Add event publishing status
            if self.event_publisher:
                recent_events = await self.event_publisher.get_event_history(limit=5)
                status['recent_events'] = [
                    {
                        'event_type': event.event_type,
                        'timestamp': event.timestamp.isoformat(),
                        'document_id': event.document_id
                    }
                    for event in recent_events
                ]
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get system status: {e}")
            return {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'system_initialized': False,
                'error': str(e)
            }
    
    async def _start_background_tasks(self) -> None:
        """Start background monitoring and maintenance tasks."""
        # Start progress tracking task
        if self.config.enable_progress_tracking and self.progress_tracker:
            self._progress_task = asyncio.create_task(self._progress_tracking_loop())
            logger.info("Started progress tracking background task")
        
        # Start starvation check task
        self._starvation_check_task = asyncio.create_task(self._starvation_check_loop())
        logger.info("Started starvation check background task")
    
    async def _progress_tracking_loop(self) -> None:
        """Background task for periodic progress tracking."""
        while True:
            try:
                await asyncio.sleep(self.config.progress_snapshot_interval_minutes * 60)
                
                if self.progress_tracker:
                    snapshot_id = await self.progress_tracker.capture_progress_snapshot(
                        period=TrackingPeriod.HOURLY
                    )
                    logger.debug(f"Progress snapshot captured: {snapshot_id}")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Progress tracking loop error: {e}")
                await asyncio.sleep(60)  # Brief pause before retry
    
    async def _starvation_check_loop(self) -> None:
        """Background task for checking resource starvation."""
        while True:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes
                
                starving_requests = await self.resource_manager.check_starvation()
                
                if starving_requests:
                    logger.warning(f"Found {len(starving_requests)} starving resource requests")
                    
                    # Publish starvation events
                    if self.event_publisher:
                        for request in starving_requests:
                            event_payload = EventPayloadBuilder.resource_exhausted(
                                document_id=request.document_id,
                                resource_type=request.resource_type.value,
                                priority=EventPriority.HIGH,
                                metadata={
                                    'starvation_duration': str(
                                        datetime.now(timezone.utc) - request.requested_at
                                    ),
                                    'priority': request.priority.value
                                }
                            )
                            await self.event_publisher.publish_event(event_payload)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Starvation check loop error: {e}")
                await asyncio.sleep(60)


# Context manager for pipeline system lifecycle
class PipelineCoordinationContext:
    """Context manager for pipeline coordination system."""
    
    def __init__(self, db: AsyncSession, config: Optional[PipelineConfiguration] = None):
        self.system = PipelineCoordinationSystem(db, config)
    
    async def __aenter__(self):
        await self.system.initialize()
        return self.system
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.system.shutdown()


# Standards.md compliance: Export main classes and functions
__all__ = [
    "PipelineConfiguration",
    "PipelineCoordinationSystem",
    "PipelineCoordinationContext"
]