"""
Audit Trail Data Models

Defines audit trail and tracking event models for comprehensive
system activity monitoring and compliance tracking.

Phase 2: Pure data structures ONLY - no audit processing or storage logic.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Union
import json


class TrackingEventType(Enum):
    """
    Types of tracking events in the system.
    
    Phase 2: Enumeration only - no event processing logic.
    """
    # User actions
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_ACCESS = "user_access"
    USER_PERMISSION_CHANGE = "user_permission_change"
    
    # Document lifecycle
    DOCUMENT_CREATED = "document_created"
    DOCUMENT_UPDATED = "document_updated"
    DOCUMENT_DELETED = "document_deleted"
    DOCUMENT_RESTORED = "document_restored"
    DOCUMENT_STATE_CHANGE = "document_state_change"
    
    # Data operations
    DATA_IMPORTED = "data_imported"
    DATA_EXPORTED = "data_exported"
    DATA_TRANSFORMED = "data_transformed"
    DATA_VALIDATED = "data_validated"
    DATA_ENRICHED = "data_enriched"
    
    # System operations
    SYSTEM_STARTUP = "system_startup"
    SYSTEM_SHUTDOWN = "system_shutdown"
    SYSTEM_ERROR = "system_error"
    SYSTEM_MAINTENANCE = "system_maintenance"
    
    # Security events
    AUTHENTICATION_FAILURE = "authentication_failure"
    AUTHORIZATION_FAILURE = "authorization_failure"
    SECURITY_VIOLATION = "security_violation"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    
    # API operations
    API_REQUEST = "api_request"
    API_RESPONSE = "api_response"
    API_ERROR = "api_error"
    API_RATE_LIMIT = "api_rate_limit"
    
    # Pipeline operations
    PIPELINE_STARTED = "pipeline_started"
    PIPELINE_COMPLETED = "pipeline_completed"
    PIPELINE_FAILED = "pipeline_failed"
    PIPELINE_STEP_EXECUTED = "pipeline_step_executed"


class AuditSeverityLevel(Enum):
    """
    Severity levels for audit events.
    
    Phase 2: Enumeration only - no severity processing logic.
    """
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AuditOutcome(Enum):
    """
    Outcomes for audit events.
    
    Phase 2: Enumeration only - no outcome processing logic.
    """
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class AuditContext:
    """
    Context information for audit events.
    
    Phase 2: Pure data structure - no context processing logic.
    """
    request_id: Optional[str]
    trace_id: Optional[str]
    session_id: Optional[str]
    user_id: Optional[str]
    client_ip: Optional[str]
    user_agent: Optional[str]
    client_id: Optional[str]
    api_version: Optional[str]
    correlation_data: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AuditMetadata:
    """
    Metadata for audit entries.
    
    Phase 2: Pure data structure - no metadata processing logic.
    """
    source_system: str
    source_component: str
    source_version: str
    environment: str
    tags: Set[str]
    custom_fields: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TrackingEvent:
    """
    Individual tracking event with complete information.
    
    Phase 2: Pure data structure - no event processing logic.
    """
    event_id: str
    event_type: TrackingEventType
    event_name: str
    timestamp: datetime
    severity: AuditSeverityLevel
    outcome: AuditOutcome
    message: str
    details: Dict[str, Any]
    context: AuditContext
    metadata: AuditMetadata
    before_state: Optional[Dict[str, Any]] = None
    after_state: Optional[Dict[str, Any]] = None
    error_info: Optional[Dict[str, Any]] = None
    performance_metrics: Optional[Dict[str, Any]] = None


@dataclass(frozen=True)
class AuditEntry:
    """
    Single audit entry representing a tracked operation.
    
    Phase 2: Pure data structure - no audit processing logic.
    """
    audit_id: str
    timestamp: datetime
    event_type: TrackingEventType
    severity: AuditSeverityLevel
    outcome: AuditOutcome
    actor_id: str
    actor_type: str
    resource_id: Optional[str]
    resource_type: Optional[str]
    action: str
    description: str
    context: AuditContext
    metadata: AuditMetadata
    data_before: Optional[Dict[str, Any]] = None
    data_after: Optional[Dict[str, Any]] = None
    changes: Optional[List[Dict[str, Any]]] = None
    risk_score: Optional[float] = None
    compliance_tags: Set[str] = field(default_factory=set)


@dataclass(frozen=True)
class AuditEvent:
    """
    High-level audit event that may contain multiple entries.
    
    Phase 2: Pure data structure - no event processing logic.
    """
    event_id: str
    event_name: str
    event_type: TrackingEventType
    started_at: datetime
    ended_at: Optional[datetime]
    duration_ms: Optional[int]
    outcome: AuditOutcome
    primary_actor_id: str
    affected_resources: Set[str]
    entries: List[AuditEntry]
    context: AuditContext
    metadata: AuditMetadata
    parent_event_id: Optional[str] = None
    related_event_ids: Set[str] = field(default_factory=set)


@dataclass
class AuditTrail:
    """
    Collection of audit events forming a complete audit trail.
    
    Phase 2: Pure data container - no trail processing logic.
    """
    trail_id: str
    name: str
    description: str
    created_at: datetime
    created_by: str
    events: List[AuditEvent] = field(default_factory=list)
    entries: List[AuditEntry] = field(default_factory=list)
    metadata: AuditMetadata
    filters: Dict[str, Any] = field(default_factory=dict)
    
    def add_event(self, event: AuditEvent) -> None:
        """Add event to trail. Phase 2: Simple data operation."""
        self.events.append(event)
    
    def add_entry(self, entry: AuditEntry) -> None:
        """Add entry to trail. Phase 2: Simple data operation."""
        self.entries.append(entry)
    
    def get_event_count(self) -> int:
        """Get event count. Phase 2: Simple data access."""
        return len(self.events)
    
    def get_entry_count(self) -> int:
        """Get entry count. Phase 2: Simple data access."""
        return len(self.entries)


# Tracking Event Schema Definitions
# Phase 2: Schema structures ONLY - no schema validation logic

@dataclass(frozen=True)
class TrackingEventSchema:
    """
    Schema definition for tracking events.
    
    Phase 2: Pure data structure - no schema validation logic.
    """
    event_type: TrackingEventType
    schema_version: str
    required_fields: Set[str]
    optional_fields: Set[str]
    field_types: Dict[str, str]
    field_constraints: Dict[str, Dict[str, Any]]
    example_event: Dict[str, Any]
    description: str


# Pre-defined Event Schemas
# Phase 2: Data structures ONLY - no schema processing logic

USER_LOGIN_SCHEMA = TrackingEventSchema(
    event_type=TrackingEventType.USER_LOGIN,
    schema_version="1.0",
    required_fields={"user_id", "timestamp", "client_ip", "outcome"},
    optional_fields={"user_agent", "client_id", "authentication_method", "mfa_used"},
    field_types={
        "user_id": "string",
        "timestamp": "datetime",
        "client_ip": "ipaddress",
        "outcome": "enum",
        "user_agent": "string",
        "client_id": "string",
        "authentication_method": "string",
        "mfa_used": "boolean"
    },
    field_constraints={
        "outcome": {"enum_values": ["success", "failure"]},
        "client_ip": {"format": "ipv4_or_ipv6"},
        "user_id": {"min_length": 1, "max_length": 255}
    },
    example_event={
        "user_id": "user123",
        "timestamp": "2025-12-26T10:30:00Z",
        "client_ip": "192.168.1.100",
        "outcome": "success",
        "user_agent": "Mozilla/5.0...",
        "authentication_method": "password"
    },
    description="User login event schema"
)

DOCUMENT_STATE_CHANGE_SCHEMA = TrackingEventSchema(
    event_type=TrackingEventType.DOCUMENT_STATE_CHANGE,
    schema_version="1.0",
    required_fields={"document_id", "user_id", "old_state", "new_state", "timestamp"},
    optional_fields={"reason", "reviewer_id", "approval_details", "rejection_reason"},
    field_types={
        "document_id": "string",
        "user_id": "string", 
        "old_state": "enum",
        "new_state": "enum",
        "timestamp": "datetime",
        "reason": "string",
        "reviewer_id": "string",
        "approval_details": "object",
        "rejection_reason": "string"
    },
    field_constraints={
        "old_state": {"enum_values": ["draft", "pending_review", "in_review", "approved", "rejected", "published", "archived"]},
        "new_state": {"enum_values": ["draft", "pending_review", "in_review", "approved", "rejected", "published", "archived"]},
        "document_id": {"min_length": 1, "max_length": 255}
    },
    example_event={
        "document_id": "doc456",
        "user_id": "reviewer789",
        "old_state": "in_review",
        "new_state": "approved",
        "timestamp": "2025-12-26T10:30:00Z",
        "reason": "Content meets approval criteria"
    },
    description="Document state change event schema"
)

API_REQUEST_SCHEMA = TrackingEventSchema(
    event_type=TrackingEventType.API_REQUEST,
    schema_version="1.0",
    required_fields={"request_id", "method", "endpoint", "status_code", "timestamp", "client_ip"},
    optional_fields={"user_id", "user_agent", "request_size", "response_size", "duration_ms", "error_details"},
    field_types={
        "request_id": "string",
        "method": "enum",
        "endpoint": "string",
        "status_code": "integer",
        "timestamp": "datetime",
        "client_ip": "ipaddress",
        "user_id": "string",
        "user_agent": "string",
        "request_size": "integer",
        "response_size": "integer", 
        "duration_ms": "integer",
        "error_details": "object"
    },
    field_constraints={
        "method": {"enum_values": ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]},
        "status_code": {"min": 100, "max": 599},
        "request_size": {"min": 0},
        "response_size": {"min": 0},
        "duration_ms": {"min": 0}
    },
    example_event={
        "request_id": "req123",
        "method": "POST",
        "endpoint": "/api/v1/documents",
        "status_code": 201,
        "timestamp": "2025-12-26T10:30:00Z",
        "client_ip": "192.168.1.100",
        "user_id": "user123",
        "duration_ms": 150
    },
    description="API request event schema"
)

# Event Schema Registry
# Phase 2: Data structure ONLY - no registry implementation
EVENT_SCHEMAS: Dict[TrackingEventType, TrackingEventSchema] = {
    TrackingEventType.USER_LOGIN: USER_LOGIN_SCHEMA,
    TrackingEventType.DOCUMENT_STATE_CHANGE: DOCUMENT_STATE_CHANGE_SCHEMA,
    TrackingEventType.API_REQUEST: API_REQUEST_SCHEMA,
}


# Audit Trail Interface Contracts
# Phase 2: Interface definitions ONLY - no audit implementations

class AuditTrailManager(ABC):
    """
    Abstract interface for audit trail management operations.
    
    Phase 2: Interface contract only - no audit implementation.
    Defines how audit trails are created, maintained, and queried.
    """
    
    @abstractmethod
    def create_audit_trail(self, trail_id: str, name: str, created_by: str) -> AuditTrail:
        """
        Create new audit trail.
        
        Phase 2: Interface only - no trail creation logic.
        
        Args:
            trail_id: Unique trail identifier
            name: Trail display name
            created_by: Creator identifier
            
        Returns:
            New audit trail instance
        """
        pass
    
    @abstractmethod
    def add_audit_entry(
        self,
        trail: AuditTrail,
        event_type: TrackingEventType,
        actor_id: str,
        action: str,
        context: AuditContext
    ) -> AuditEntry:
        """
        Add audit entry to trail.
        
        Phase 2: Interface only - no entry addition logic.
        
        Args:
            trail: Target audit trail
            event_type: Type of event
            actor_id: Actor performing action
            action: Action description
            context: Audit context
            
        Returns:
            Created audit entry
        """
        pass
    
    @abstractmethod
    def create_tracking_event(
        self,
        event_type: TrackingEventType,
        event_name: str,
        context: AuditContext,
        details: Dict[str, Any]
    ) -> TrackingEvent:
        """
        Create tracking event.
        
        Phase 2: Interface only - no event creation logic.
        
        Args:
            event_type: Type of tracking event
            event_name: Event display name
            context: Event context
            details: Event details
            
        Returns:
            Created tracking event
        """
        pass
    
    @abstractmethod
    def get_audit_trail(self, trail_id: str) -> Optional[AuditTrail]:
        """
        Get audit trail by ID.
        
        Phase 2: Interface only - no retrieval logic.
        
        Args:
            trail_id: Trail identifier
            
        Returns:
            Audit trail or None if not found
        """
        pass
    
    @abstractmethod
    def query_audit_entries(
        self,
        filters: Dict[str, Any],
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[AuditEntry]:
        """
        Query audit entries with filters.
        
        Phase 2: Interface only - no query logic.
        
        Args:
            filters: Query filters
            start_time: Optional start time filter
            end_time: Optional end time filter
            
        Returns:
            List of matching audit entries
        """
        pass