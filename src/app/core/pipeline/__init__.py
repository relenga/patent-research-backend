"""
Pipeline coordination package for Phase 3.2A implementation.

This package implements the pipeline state machine execution engine with
coordination enhancements for complex document processing per the 
Phase 3.2A development brief.

Key Components:
- state_machine.py: Core state transition executor
- completion_calculator.py: Document completion logic (90%/70% thresholds)
- coordination.py: Diagram classification and similarity handling
- resource_manager.py: GPU/OCR limits and starvation prevention

Standards.md Compliance:
- Uses PostgreSQL persistence service patterns from P3.1
- Follows API response standards with ErrorCode enum
- Implements structured logging format
- Uses environment-based configuration patterns

Authority:
- PipelineStateMachine.md: AUTHORITATIVE state definitions and transition rules
- PipelineExecutionSpec.md: Technical execution mechanics
- Standards.md: Implementation compliance requirements
"""

__version__ = "3.2A.0"
__author__ = "Phase 3.2A Pipeline Coordination Team"