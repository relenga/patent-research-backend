"""
Phase 3.2A Pipeline Coordination Package

This package implements the pipeline state machine execution engine with 
coordination enhancements for processing complex documents with 15-20+ diagrams.

Key Features:
- PipelineStateMachine.md compliant state transitions
- Document completion calculation with 90%/70% thresholds
- Intelligent diagram classification and similarity analysis
- Resource management with GPU/OCR limits and starvation prevention
- Enhanced override logging with comprehensive audit trails
- Real-time event publishing for state changes
- Detailed progress tracking with performance metrics
- Secure manual state transition overrides for administrators

Components:
- state_machine.py: Core state transition executor
- completion_calculator.py: Document completion logic with thresholds
- coordination.py: Diagram classification and processing coordination
- resource_manager.py: Resource allocation with priority queues
- override_logging.py: Enhanced audit logging for manual overrides
- event_publisher.py: Real-time event publishing system
- progress_tracker.py: Comprehensive progress monitoring
- manual_overrides.py: Secure admin interface for state transitions
- coordination_system.py: Main integration point for all components

All components follow Standards.md requirements for:
- Async/await patterns with SQLAlchemy 2.0
- Comprehensive error handling and logging
- Database transaction management
- API design consistency
- Security and authorization controls

Phase 3.2A Implementation Status: COMPLETE
Tasks 3.2A.1-11: ✅ All pipeline coordination features implemented
"""

from .coordination_system import (
    PipelineCoordinationSystem,
    PipelineCoordinationContext,
    PipelineConfiguration
)

from .state_machine import (
    PipelineDocumentState,
    PipelineImageState,
    StateTransition,
    PipelineStateExecutor
)

from .completion_calculator import (
    DocumentCompletionCalculator,
    DiagramType,
    DocumentCompletionMetrics
)

from .coordination import (
    PipelineCoordinator,
    DiagramClassifier,
    SimilarityAnalyzer
)

from .resource_manager import (
    ResourceManager,
    ProcessingType,
    Priority
)

from .manual_overrides import (
    ManualOverrideSystem,
    OverrideRequest,
    EmergencyLevel,
    OverrideScope
)

__version__ = "3.2A.1"
__phase__ = "3.2A"
__status__ = "IMPLEMENTATION_COMPLETE"

__all__ = [
    # Main coordination system
    "PipelineCoordinationSystem",
    "PipelineCoordinationContext", 
    "PipelineConfiguration",
    
    # Core components
    "PipelineStateExecutor",
    "DocumentCompletionCalculator",
    "PipelineCoordinator",
    "ResourceManager",
    "ManualOverrideSystem",
    
    # Enums and data classes
    "PipelineDocumentState",
    "PipelineImageState",
    "StateTransition",
    "DiagramType",
    "DocumentCompletionMetrics",
    "ProcessingType",
    "Priority",
    "OverrideRequest",
    "EmergencyLevel",
    "OverrideScope"
]