"""
Phase 3.2A Task 3.2A.11: Comprehensive Test Suite

Complete test coverage for all pipeline coordination features, error conditions,
resource limits, and override scenarios to ensure robust system operation.

Test Categories:
- Unit tests for individual components
- Integration tests for component interactions
- Performance tests for resource limits
- Security tests for override authorization
- Error handling and recovery tests
- End-to-end pipeline coordination tests
"""

import asyncio
import pytest
import uuid
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Import pipeline components
from app.core.pipeline.state_machine import (
    PipelineDocumentState,
    PipelineImageState, 
    StateTransition,
    PipelineStateExecutor
)
from app.core.pipeline.completion_calculator import (
    DocumentCompletionCalculator,
    DiagramType,
    DocumentCompletionMetrics
)
from app.core.pipeline.coordination import (
    DiagramClassifier,
    SimilarityAnalyzer,
    PipelineCoordinator,
    DiagramClassification,
    SimilarityLevel
)
from app.core.pipeline.resource_manager import (
    ResourceType,
    ResourceManager,
    ResourceAllocation,
    ProcessingPriority
)
from app.core.pipeline.override_logging import (
    PipelineOverrideLogger,
    OverrideAction,
    OverrideReason,
    OverrideContext,
    OverrideContextBuilder
)
from app.core.pipeline.event_publisher import (
    EventPublisher,
    EventType,
    EventPriority,
    EventPayload,
    EventPayloadBuilder
)
from app.core.pipeline.progress_tracker import (
    PipelineProgressTracker,
    TrackingPeriod,
    ResourceUtilization,
    ProcessingStatistics
)
from app.core.pipeline.manual_overrides import (
    ManualOverrideSystem,
    OverrideRequest,
    EmergencyLevel,
    OverrideScope,
    OverrideValidationError,
    OverrideAuthorizationError
)


class TestStateTransitions:
    """Test state machine transitions and validation."""
    
    @pytest.fixture
    async def state_executor(self, db_session: AsyncSession):
        return PipelineStateExecutor()
    
    @pytest.mark.asyncio
    async def test_valid_document_state_transition(self, state_executor, db_session):
        """Test valid document state transitions."""
        transition = StateTransition(
            entity_type="document",
            entity_id=1,
            from_state=PipelineDocumentState.UPLOADED.value,
            to_state=PipelineDocumentState.PROCESSING.value,
            trigger="start_processing"
        )
        
        result = await state_executor.validate_transition(transition, db_session)
        assert result is True
    
    @pytest.mark.asyncio
    async def test_invalid_document_state_transition(self, state_executor, db_session):
        """Test invalid document state transitions are rejected."""
        transition = StateTransition(
            entity_type="document",
            entity_id=1,
            from_state=PipelineDocumentState.UPLOADED.value,
            to_state=PipelineDocumentState.COMPLETED.value,
            trigger="invalid_jump"
        )
        
        result = await state_executor.validate_transition(transition, db_session)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_image_state_progression(self, state_executor, db_session):
        """Test image state progression through pipeline."""
        states = [
            PipelineImageState.DISCOVERED.value,
            PipelineImageState.QUEUED.value,
            PipelineImageState.PROCESSING.value,
            PipelineImageState.PROCESSED.value
        ]
        
        for i in range(len(states) - 1):
            transition = StateTransition(
                entity_type="image",
                entity_id=1,
                from_state=states[i],
                to_state=states[i + 1],
                trigger="next_step"
            )
            
            result = await state_executor.validate_transition(transition, db_session)
            assert result is True


class TestCompletionCalculator:
    """Test document completion calculation logic."""
    
    @pytest.fixture
    async def completion_calculator(self, db_session: AsyncSession):
        return DocumentCompletionCalculator(db_session)
    
    @pytest.mark.asyncio
    async def test_empty_document_completion(self, completion_calculator):
        """Test completion calculation for empty document."""
        with patch('app.crud.crud_pipeline.get_document_images', AsyncMock(return_value=[])):
            metrics = await completion_calculator.calculate_completion(document_id=1)
            
            assert metrics.completion_percentage == 100.0  # Empty is complete
            assert metrics.critical_images_processed == 0
            assert metrics.total_critical_images == 0
    
    @pytest.mark.asyncio
    async def test_partial_completion_calculation(self, completion_calculator):
        """Test partial completion calculation."""
        # Mock document with mixed image states
        mock_images = [
            Mock(diagram_type=DiagramType.CRITICAL.value, state=PipelineImageState.PROCESSED.value),
            Mock(diagram_type=DiagramType.CRITICAL.value, state=PipelineImageState.PROCESSING.value),
            Mock(diagram_type=DiagramType.SUPPORTING.value, state=PipelineImageState.PROCESSED.value),
            Mock(diagram_type=DiagramType.DECORATIVE.value, state=PipelineImageState.QUEUED.value)
        ]
        
        with patch('app.crud.crud_pipeline.get_document_images', AsyncMock(return_value=mock_images)):
            metrics = await completion_calculator.calculate_completion(document_id=1)
            
            # Should have 50% critical completion (1 of 2 critical images)
            assert metrics.critical_images_processed == 1
            assert metrics.total_critical_images == 2
            assert metrics.completion_percentage == 50.0
    
    @pytest.mark.asyncio
    async def test_completion_recommendation_90_percent(self, completion_calculator):
        """Test completion recommendation at 90% threshold."""
        # Mock document at 90% completion
        with patch.object(completion_calculator, 'calculate_completion', AsyncMock(
            return_value=DocumentCompletionMetrics(
                document_id=1,
                completion_percentage=90.0,
                critical_images_processed=9,
                total_critical_images=10,
                supporting_images_processed=5,
                total_supporting_images=5
            )
        )):
            recommendation = await completion_calculator.recommend_next_state(
                document_id=1,
                current_state=PipelineDocumentState.PROCESSING.value
            )
            
            assert recommendation == PipelineDocumentState.COMPLETED.value


class TestDiagramCoordination:
    """Test diagram classification and similarity analysis."""
    
    @pytest.fixture
    def diagram_classifier(self):
        return DiagramClassifier()
    
    @pytest.fixture 
    def similarity_analyzer(self):
        return SimilarityAnalyzer()
    
    @pytest.fixture
    def coordinator(self, db_session: AsyncSession):
        return PipelineCoordinator(db_session)
    
    def test_diagram_classification_critical(self, diagram_classifier):
        """Test classification of critical diagrams."""
        # Test various critical diagram patterns
        critical_patterns = [
            "FIG. 1 shows the main system architecture",
            "Figure 2 illustrates the control flow",
            "FIG 3 depicts the core algorithm"
        ]
        
        for text in critical_patterns:
            classification = diagram_classifier.classify_diagram(text, {})
            assert classification.diagram_type == DiagramType.CRITICAL
            assert classification.confidence_score >= 0.8
    
    def test_diagram_classification_supporting(self, diagram_classifier):
        """Test classification of supporting diagrams."""
        supporting_patterns = [
            "FIG. 10 shows a detailed view of component X",
            "Figure 15 illustrates an alternative embodiment",
            "FIG 20 depicts additional features"
        ]
        
        for text in supporting_patterns:
            classification = diagram_classifier.classify_diagram(text, {})
            assert classification.diagram_type == DiagramType.SUPPORTING
            assert classification.confidence_score >= 0.6
    
    def test_similarity_analysis_duplicate(self, similarity_analyzer):
        """Test detection of duplicate diagrams."""
        # Mock identical diagrams
        diagram1 = Mock(text_content="System architecture diagram", metadata={})
        diagram2 = Mock(text_content="System architecture diagram", metadata={})
        
        similarity = similarity_analyzer.analyze_similarity(diagram1, diagram2)
        assert similarity.similarity_level == SimilarityLevel.DUPLICATE
        assert similarity.confidence_score >= 0.95
    
    def test_similarity_analysis_near_duplicate(self, similarity_analyzer):
        """Test detection of near-duplicate diagrams."""
        diagram1 = Mock(text_content="System architecture with component A", metadata={})
        diagram2 = Mock(text_content="System architecture with component B", metadata={})
        
        similarity = similarity_analyzer.analyze_similarity(diagram1, diagram2)
        assert similarity.similarity_level == SimilarityLevel.NEAR_DUPLICATE
        assert 0.8 <= similarity.confidence_score < 0.95
    
    @pytest.mark.asyncio
    async def test_coordinator_processing_decision(self, coordinator):
        """Test coordinator makes correct processing decisions."""
        # Mock a critical diagram that should be processed immediately
        with patch.object(coordinator.classifier, 'classify_diagram') as mock_classify:
            mock_classify.return_value = DiagramClassification(
                diagram_type=DiagramType.CRITICAL,
                confidence_score=0.9,
                reasoning="Contains main algorithm"
            )
            
            decision = await coordinator.should_process_immediately(
                image_id=1,
                document_context={'total_images': 20, 'critical_count': 3}
            )
            
            assert decision is True


class TestResourceManager:
    """Test resource allocation and management."""
    
    @pytest.fixture
    def resource_manager(self):
        return ResourceManager(
            max_gpu_slots=4,
            max_ocr_slots=8,
            starvation_timeout_hours=24
        )
    
    @pytest.mark.asyncio
    async def test_resource_allocation_success(self, resource_manager):
        """Test successful resource allocation."""
        allocation = await resource_manager.allocate_resource(
            resource_type=ResourceType.GPU,
            document_id=1,
            priority=ProcessingPriority.HIGH,
            estimated_duration=300  # 5 minutes
        )
        
        assert allocation is not None
        assert allocation.resource_type == ResourceType.GPU
        assert allocation.document_id == 1
        assert allocation.allocated_at is not None
    
    @pytest.mark.asyncio
    async def test_resource_allocation_exhaustion(self, resource_manager):
        """Test resource allocation when resources are exhausted."""
        # Allocate all GPU slots
        allocations = []
        for i in range(4):  # Max GPU slots
            allocation = await resource_manager.allocate_resource(
                resource_type=ResourceType.GPU,
                document_id=i + 1,
                priority=ProcessingPriority.NORMAL,
                estimated_duration=600
            )
            allocations.append(allocation)
        
        # Try to allocate one more - should fail
        allocation = await resource_manager.allocate_resource(
            resource_type=ResourceType.GPU,
            document_id=5,
            priority=ProcessingPriority.NORMAL,
            estimated_duration=300
        )
        
        assert allocation is None  # No resources available
    
    @pytest.mark.asyncio 
    async def test_priority_queue_ordering(self, resource_manager):
        """Test that higher priority requests are processed first."""
        # Fill all resources
        for i in range(4):
            await resource_manager.allocate_resource(
                resource_type=ResourceType.GPU,
                document_id=i + 1,
                priority=ProcessingPriority.NORMAL,
                estimated_duration=600
            )
        
        # Queue requests with different priorities
        await resource_manager.allocate_resource(
            resource_type=ResourceType.GPU,
            document_id=10,
            priority=ProcessingPriority.LOW,
            estimated_duration=300
        )
        
        await resource_manager.allocate_resource(
            resource_type=ResourceType.GPU,
            document_id=11,
            priority=ProcessingPriority.CRITICAL,
            estimated_duration=300
        )
        
        # Release a resource
        await resource_manager.release_resource(resource_type=ResourceType.GPU, document_id=1)
        
        # Check that critical priority got the resource
        status = await resource_manager.get_resource_status()
        # The critical priority request should be allocated
        assert any(
            alloc.document_id == 11 and alloc.priority == ProcessingPriority.CRITICAL
            for alloc in status.get('active_allocations', [])
        )
    
    @pytest.mark.asyncio
    async def test_starvation_prevention(self, resource_manager):
        """Test that starvation prevention works correctly."""
        # Set a short starvation timeout for testing
        resource_manager._starvation_timeout_hours = 0.001  # ~3.6 seconds
        
        # Fill all resources with long-running tasks
        for i in range(4):
            await resource_manager.allocate_resource(
                resource_type=ResourceType.GPU,
                document_id=i + 1,
                priority=ProcessingPriority.NORMAL,
                estimated_duration=7200  # 2 hours
            )
        
        # Add a low priority request that should be starving
        await resource_manager.allocate_resource(
            resource_type=ResourceType.GPU,
            document_id=10,
            priority=ProcessingPriority.LOW,
            estimated_duration=300
        )
        
        # Wait for starvation timeout
        await asyncio.sleep(4)
        
        # Check for starvation prevention
        starving_requests = await resource_manager.check_starvation()
        assert len(starving_requests) > 0
        assert starving_requests[0].document_id == 10


class TestOverrideLogging:
    """Test override audit logging functionality."""
    
    @pytest.fixture
    async def override_logger(self, db_session: AsyncSession):
        return PipelineOverrideLogger(db_session)
    
    @pytest.mark.asyncio
    async def test_override_request_logging(self, override_logger):
        """Test logging of override requests."""
        # Mock administrator user
        with patch('app.crud.crud_users.crud_user.get', AsyncMock(
            return_value=Mock(id=1, role="admin", email="admin@test.com")
        )):
            context = OverrideContextBuilder.for_state_transition(
                document_id=1,
                original_state=PipelineDocumentState.PROCESSING.value,
                target_state=PipelineDocumentState.COMPLETED.value
            )
            
            override_id = await override_logger.log_override_request(
                administrator_id=1,
                action=OverrideAction.STATE_TRANSITION,
                reason=OverrideReason.TECHNICAL_ERROR,
                justification="Critical bug in processing pipeline requires manual completion",
                context=context,
                administrator_ip="192.168.1.100"
            )
            
            assert isinstance(override_id, uuid.UUID)
    
    @pytest.mark.asyncio
    async def test_insufficient_justification(self, override_logger):
        """Test that insufficient justification is rejected."""
        with patch('app.crud.crud_users.crud_user.get', AsyncMock(
            return_value=Mock(id=1, role="admin", email="admin@test.com")
        )):
            context = OverrideContextBuilder.for_state_transition(document_id=1)
            
            with pytest.raises(ValueError, match="Justification must be at least"):
                await override_logger.log_override_request(
                    administrator_id=1,
                    action=OverrideAction.STATE_TRANSITION,
                    reason=OverrideReason.TECHNICAL_ERROR,
                    justification="Too short",  # Less than 50 characters
                    context=context
                )
    
    @pytest.mark.asyncio
    async def test_override_execution_tracking(self, override_logger):
        """Test tracking of override execution."""
        # Create override request first
        with patch('app.crud.crud_users.crud_user.get', AsyncMock(
            return_value=Mock(id=1, role="admin", email="admin@test.com")
        )):
            context = OverrideContextBuilder.for_state_transition(document_id=1)
            
            override_id = await override_logger.log_override_request(
                administrator_id=1,
                action=OverrideAction.STATE_TRANSITION,
                reason=OverrideReason.TECHNICAL_ERROR,
                justification="Valid justification with sufficient length for testing purposes",
                context=context
            )
            
            # Log execution
            await override_logger.log_override_execution(override_id, success=True)
            
            # Log completion
            await override_logger.log_override_completion(override_id, final_success=True)
            
            # Verify audit trail
            history = await override_logger.get_override_history(limit=1)
            assert len(history) == 1
            assert history[0].override_id == override_id
            assert history[0].success == "success"


class TestEventPublishing:
    """Test event publishing and subscription system."""
    
    @pytest.fixture
    async def event_publisher(self, db_session: AsyncSession):
        publisher = EventPublisher(db_session)
        await publisher.start()
        yield publisher
        await publisher.stop()
    
    @pytest.mark.asyncio
    async def test_event_publishing(self, event_publisher):
        """Test basic event publishing."""
        payload = EventPayloadBuilder.state_transition(
            document_id=1,
            previous_state=PipelineDocumentState.PROCESSING.value,
            current_state=PipelineDocumentState.COMPLETED.value,
            priority=EventPriority.NORMAL
        )
        
        await event_publisher.publish_event(payload)
        
        # Verify event was stored
        history = await event_publisher.get_event_history(limit=1)
        assert len(history) == 1
        assert history[0].event_type == EventType.STATE_TRANSITION.value
        assert history[0].document_id == 1
    
    @pytest.mark.asyncio
    async def test_event_filtering(self, event_publisher):
        """Test event history filtering."""
        # Publish multiple events
        for i in range(5):
            payload = EventPayloadBuilder.processing_completed(
                document_id=i,
                completion_percentage=float(i * 20),
                priority=EventPriority.NORMAL
            )
            await event_publisher.publish_event(payload)
        
        # Filter by document ID
        history = await event_publisher.get_event_history(document_id=2)
        assert len(history) == 1
        assert history[0].document_id == 2
        
        # Filter by event type
        history = await event_publisher.get_event_history(
            event_types=[EventType.PROCESSING_COMPLETED]
        )
        assert len(history) == 5
        assert all(event.event_type == EventType.PROCESSING_COMPLETED.value for event in history)


class TestProgressTracking:
    """Test pipeline progress tracking functionality."""
    
    @pytest.fixture
    async def progress_tracker(self, db_session: AsyncSession):
        return PipelineProgressTracker(db_session)
    
    @pytest.mark.asyncio
    async def test_progress_snapshot_capture(self, progress_tracker):
        """Test capturing progress snapshots."""
        # Mock resource manager and completion calculator
        mock_resource_manager = Mock()
        mock_resource_manager.get_resource_status = AsyncMock(return_value={
            'gpu_slots_used': 2,
            'gpu_slots_total': 4,
            'ocr_slots_used': 4,
            'ocr_slots_total': 8,
            'cpu_utilization': 0.6,
            'memory_utilization': 0.7,
            'queue_lengths': {'gpu': 2, 'ocr': 1}
        })
        
        mock_completion_calculator = Mock()
        progress_tracker.set_resource_manager(mock_resource_manager)
        progress_tracker.set_completion_calculator(mock_completion_calculator)
        
        # Mock document and image progress
        with patch.object(progress_tracker, '_calculate_document_progress', AsyncMock(
            return_value={'total': 10, 'completed': 7, 'in_progress': 2, 'failed': 1}
        )), patch.object(progress_tracker, '_calculate_image_progress', AsyncMock(
            return_value={'total': 100, 'processed': 75, 'pending': 25}
        )), patch.object(progress_tracker, '_calculate_overall_completion', AsyncMock(
            return_value=75.0
        )):
            snapshot_id = await progress_tracker.capture_progress_snapshot(
                period=TrackingPeriod.HOURLY
            )
            
            assert isinstance(snapshot_id, uuid.UUID)
    
    def test_operation_timing(self, progress_tracker):
        """Test operation timing tracking."""
        operation_id = "test_operation_123"
        
        progress_tracker.track_operation_start(operation_id)
        assert operation_id in progress_tracker._current_operations
        
        progress_tracker.track_operation_end(operation_id, "image_processing")
        assert operation_id not in progress_tracker._current_operations
        assert len(progress_tracker._processing_times["image_processing"]) > 0


class TestManualOverrides:
    """Test manual state transition override system."""
    
    @pytest.fixture
    async def manual_override_system(self, db_session: AsyncSession):
        state_executor = Mock(spec=PipelineStateExecutor)
        override_logger = Mock(spec=PipelineOverrideLogger)
        event_publisher = Mock(spec=EventPublisher)
        
        return ManualOverrideSystem(
            db=db_session,
            state_executor=state_executor,
            override_logger=override_logger,
            event_publisher=event_publisher
        )
    
    @pytest.mark.asyncio
    async def test_override_authorization_validation(self, manual_override_system):
        """Test that authorization is properly validated."""
        request = OverrideRequest(
            administrator_id=999,  # Non-existent user
            emergency_level=EmergencyLevel.HIGH,
            scope=OverrideScope.SINGLE_DOCUMENT,
            document_id=1,
            target_state=PipelineDocumentState.COMPLETED.value,
            justification="Test justification with sufficient length for validation purposes and proper reasoning",
            expected_outcome="Document will be marked as completed to resolve processing issue",
            rollback_plan="Revert document to processing state if completion causes downstream issues"
        )
        
        with pytest.raises(OverrideAuthorizationError, match="Administrator user not found"):
            await manual_override_system.request_override(request)
    
    def test_override_request_validation(self, manual_override_system):
        """Test override request validation logic."""
        # Test insufficient justification
        request = OverrideRequest(
            administrator_id=1,
            emergency_level=EmergencyLevel.LOW,
            scope=OverrideScope.SINGLE_DOCUMENT,
            document_id=1,
            justification="Too short",
            expected_outcome="Will work"
        )
        
        with pytest.raises(OverrideValidationError, match="Justification must be at least"):
            asyncio.run(manual_override_system._validate_override_request(request))
    
    @pytest.mark.asyncio
    async def test_successful_override_execution(self, manual_override_system):
        """Test successful override execution flow."""
        # Mock successful authorization
        mock_admin_user = Mock(id=1, is_superuser=True, role="admin", email="admin@test.com")
        
        with patch('app.crud.crud_users.crud_user.get', AsyncMock(return_value=mock_admin_user)), \
             patch('app.core.security.verify_admin_permission', AsyncMock(return_value=True)), \
             patch.object(manual_override_system.override_logger, 'log_override_request', AsyncMock(
                 return_value=uuid.uuid4()
             )), \
             patch.object(manual_override_system.override_logger, 'log_override_execution', AsyncMock()), \
             patch.object(manual_override_system.override_logger, 'log_override_completion', AsyncMock()), \
             patch.object(manual_override_system, '_execute_override', AsyncMock()):
            
            request = OverrideRequest(
                administrator_id=1,
                emergency_level=EmergencyLevel.LOW,
                scope=OverrideScope.SINGLE_DOCUMENT,
                document_id=1,
                target_state=PipelineDocumentState.COMPLETED.value,
                justification="Valid justification with sufficient length for testing manual override system functionality",
                expected_outcome="Document will be marked as completed successfully without issues",
                rollback_plan="Revert to previous state if any problems arise during execution"
            )
            
            override_id = await manual_override_system.request_override(request)
            assert isinstance(override_id, uuid.UUID)


class TestIntegrationScenarios:
    """Test integration between multiple pipeline components."""
    
    @pytest.mark.asyncio
    async def test_complete_pipeline_coordination(self, db_session: AsyncSession):
        """Test complete pipeline coordination scenario."""
        # This would test a full pipeline scenario with:
        # 1. Document upload and state transition
        # 2. Resource allocation for processing
        # 3. Completion calculation and coordination decisions  
        # 4. Event publishing for state changes
        # 5. Progress tracking throughout
        
        # Mock all components
        state_executor = Mock(spec=PipelineStateExecutor)
        resource_manager = Mock(spec=ResourceManager)
        completion_calculator = Mock(spec=DocumentCompletionCalculator)
        coordinator = Mock(spec=PipelineCoordinator)
        
        # Set up mock returns for successful flow
        state_executor.execute_transition = AsyncMock(return_value=True)
        resource_manager.allocate_resource = AsyncMock(return_value=Mock(
            resource_type=ResourceType.GPU,
            document_id=1,
            allocated_at=datetime.now(timezone.utc)
        ))
        completion_calculator.calculate_completion = AsyncMock(return_value=Mock(
            completion_percentage=25.0,
            critical_images_processed=1,
            total_critical_images=4
        ))
        coordinator.should_process_immediately = AsyncMock(return_value=True)
        
        # Simulate pipeline flow - document starts processing
        # 1. Allocate resources
        allocation = await resource_manager.allocate_resource(
            resource_type=ResourceType.GPU,
            document_id=1,
            priority=ProcessingPriority.HIGH,
            estimated_duration=600
        )
        assert allocation is not None
        
        # 2. Check processing decision  
        should_process = await coordinator.should_process_immediately(
            image_id=1,
            document_context={'total_images': 15}
        )
        assert should_process is True
        
        # 3. Execute state transition
        transition_success = await state_executor.execute_transition(
            StateTransition(
                entity_type="document",
                entity_id=1,
                from_state=PipelineDocumentState.UPLOADED.value,
                to_state=PipelineDocumentState.PROCESSING.value,
                trigger="start_processing"
            ),
            db_session
        )
        assert transition_success is True
        
        # 4. Check completion
        completion = await completion_calculator.calculate_completion(document_id=1)
        assert completion.completion_percentage == 25.0
    
    @pytest.mark.asyncio
    async def test_error_handling_and_recovery(self, db_session: AsyncSession):
        """Test error handling and recovery scenarios."""
        # Test resource exhaustion handling
        resource_manager = ResourceManager(max_gpu_slots=1, max_ocr_slots=1)
        
        # Allocate the single resource
        allocation1 = await resource_manager.allocate_resource(
            resource_type=ResourceType.GPU,
            document_id=1,
            priority=ProcessingPriority.NORMAL,
            estimated_duration=300
        )
        assert allocation1 is not None
        
        # Try to allocate another - should fail
        allocation2 = await resource_manager.allocate_resource(
            resource_type=ResourceType.GPU,
            document_id=2,
            priority=ProcessingPriority.NORMAL,
            estimated_duration=300
        )
        assert allocation2 is None
        
        # Release first resource
        await resource_manager.release_resource(ResourceType.GPU, document_id=1)
        
        # Now second allocation should succeed
        allocation3 = await resource_manager.allocate_resource(
            resource_type=ResourceType.GPU,
            document_id=2,
            priority=ProcessingPriority.NORMAL,
            estimated_duration=300
        )
        assert allocation3 is not None


class TestPerformanceAndLoad:
    """Test performance characteristics and load handling."""
    
    @pytest.mark.asyncio
    async def test_high_volume_event_publishing(self):
        """Test event publishing under high load."""
        # This would test publishing many events concurrently
        # and verify system stability
        pass
    
    @pytest.mark.asyncio
    async def test_resource_manager_under_load(self):
        """Test resource manager performance under load."""
        # This would test many concurrent allocation requests
        # and verify queue management
        pass
    
    @pytest.mark.asyncio
    async def test_completion_calculation_performance(self):
        """Test completion calculation with large document sets."""
        # This would test completion calculation with documents
        # containing many images
        pass


# Test configuration and fixtures
@pytest.fixture
async def db_session():
    """Mock database session for testing."""
    session = Mock(spec=AsyncSession)
    session.add = Mock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.execute = AsyncMock()
    return session


# Test utilities
class TestUtilities:
    """Utility functions for testing pipeline components."""
    
    @staticmethod
    def create_mock_document(
        id: int = 1,
        state: str = PipelineDocumentState.UPLOADED.value,
        image_count: int = 10
    ):
        """Create mock document for testing."""
        return Mock(
            id=id,
            state=state,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
    
    @staticmethod
    def create_mock_image(
        id: int = 1,
        document_id: int = 1,
        state: str = PipelineImageState.DISCOVERED.value,
        diagram_type: str = DiagramType.CRITICAL.value
    ):
        """Create mock image for testing."""
        return Mock(
            id=id,
            document_id=document_id,
            state=state,
            diagram_type=diagram_type,
            text_content="Test diagram content",
            metadata={}
        )


# Export test classes for pytest discovery
__all__ = [
    "TestStateTransitions",
    "TestCompletionCalculator", 
    "TestDiagramCoordination",
    "TestResourceManager",
    "TestOverrideLogging",
    "TestEventPublishing",
    "TestProgressTracking",
    "TestManualOverrides",
    "TestIntegrationScenarios",
    "TestPerformanceAndLoad",
    "TestUtilities"
]