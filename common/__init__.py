"""
Common services and contracts module.

This module provides core service interfaces and contracts for the Revel HMI system.
All services defined here are abstract interfaces only - no implementations provided.

Phase 2 Focus: Structure and contracts without implementation.
"""

from .api import APIRouting, APIResponse, APIError, APIRoutingPolicy, ErrorCode
from .context import ContextService, ExecutionContext
from .time import TimeService, TimeZoneService
from .ids import IDService, IDFormat
from .logging import LoggingService, ComponentLogger, LogContext, LogLevel
from .phase_flags import (
    DevelopmentPhase, FeatureFlag, PhaseConstraint, FeatureFlagDefinition,
    PhaseViolationError, FeatureNotAvailableError, PrematureFeatureUsageError,
    DeprecatedFeatureUsageError, ConflictingFeatureError,
    PhaseDetector, FeatureFlagEvaluator, PhaseBoundaryValidator, FeatureFlagRegistry,
    requires_phase, feature_flag, phase_boundary, deprecated_in_phase
)

__all__ = [
    # API contracts
    "APIRouting",
    "APIResponse", 
    "APIError",
    "APIRoutingPolicy",
    "ErrorCode",
    
    # Context management
    "ContextService",
    "ExecutionContext",
    
    # Time services
    "TimeService",
    "TimeZoneService",
    
    # ID generation
    "IDService",
    "IDFormat",
    
    # Logging
    "LoggingService",
    "ComponentLogger",
    "LogContext",
    "LogLevel",
    
    # Phase flags and enforcement
    "DevelopmentPhase",
    "FeatureFlag", 
    "PhaseConstraint",
    "FeatureFlagDefinition",
    "PhaseViolationError",
    "FeatureNotAvailableError",
    "PrematureFeatureUsageError", 
    "DeprecatedFeatureUsageError",
    "ConflictingFeatureError",
    "PhaseDetector",
    "FeatureFlagEvaluator",
    "PhaseBoundaryValidator",
    "FeatureFlagRegistry",
    "requires_phase",
    "feature_flag",
    "phase_boundary",
    "deprecated_in_phase",
]