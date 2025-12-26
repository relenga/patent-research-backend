"""
API routing invariants and response schemas.

Defines canonical API structure, routing policies, and response envelopes.
Phase 2: Contract definition only - no enforcement logic.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union, Generic, TypeVar
from enum import Enum


class APIRoutingPolicy:
    """
    API routing invariants and policies.
    
    Phase 2 Note: These are documentation contracts only.
    Enforcement deferred to Phase 3.
    """
    
    # Trailing slash policy - MUST be chosen and documented
    # Current Phase 1 behavior: inconsistent (some with, some without)
    # Phase 2 Decision: Standardize on NO trailing slashes
    TRAILING_SLASH_POLICY = "no_trailing_slash"
    
    # API prefix policy
    API_PREFIX = "/api/v1"
    
    # Versioning strategy
    VERSIONING_STRATEGY = "path_based"  # /api/v1/, /api/v2/, etc.
    
    # Content negotiation
    DEFAULT_CONTENT_TYPE = "application/json"
    SUPPORTED_CONTENT_TYPES = ["application/json"]


T = TypeVar('T')


class APIResponse(Generic[T]):
    """
    Canonical API response envelope.
    
    All API responses SHOULD follow this structure for consistency.
    Phase 2: Schema definition only - no enforcement.
    """
    
    def __init__(
        self,
        data: Optional[T] = None,
        message: Optional[str] = None,
        success: bool = True,
        request_id: Optional[str] = None,
        timestamp: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize API response envelope.
        
        Args:
            data: The response payload
            message: Human-readable message
            success: Whether the operation succeeded
            request_id: Request correlation ID
            timestamp: Response timestamp (ISO format)
            meta: Additional metadata (pagination, etc.)
        """
        self.data = data
        self.message = message
        self.success = success
        self.request_id = request_id
        self.timestamp = timestamp
        self.meta = meta or {}


class ErrorCode(Enum):
    """Standard error codes for API responses."""
    
    # Client errors (4xx)
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    RATE_LIMITED = "RATE_LIMITED"
    
    # Server errors (5xx)
    INTERNAL_ERROR = "INTERNAL_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    TIMEOUT = "TIMEOUT"


class APIError:
    """
    Canonical API error response structure.
    
    All API errors SHOULD follow this structure for consistency.
    Phase 2: Schema definition only - no enforcement.
    """
    
    def __init__(
        self,
        code: Union[ErrorCode, str],
        message: str,
        details: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
        timestamp: Optional[str] = None,
        trace_id: Optional[str] = None
    ):
        """
        Initialize API error response.
        
        Args:
            code: Error code (enum or string)
            message: Human-readable error message
            details: Additional error details/context
            request_id: Request correlation ID
            timestamp: Error timestamp (ISO format)
            trace_id: Distributed tracing ID
        """
        self.code = code.value if isinstance(code, ErrorCode) else code
        self.message = message
        self.details = details or {}
        self.request_id = request_id
        self.timestamp = timestamp
        self.trace_id = trace_id


class APIRouting(ABC):
    """
    Abstract interface for API routing policies.
    
    Phase 2: Interface contract only - no implementation.
    Runtime wiring deferred to Phase 3.
    """
    
    @abstractmethod
    def normalize_path(self, path: str) -> str:
        """
        Normalize API path according to routing policies.
        
        Args:
            path: Raw path to normalize
            
        Returns:
            Normalized path following routing invariants
        """
        pass
    
    @abstractmethod
    def validate_route_structure(self, route: str) -> bool:
        """
        Validate route follows structural conventions.
        
        Args:
            route: Route to validate
            
        Returns:
            True if route is valid, False otherwise
        """
        pass
    
    @abstractmethod
    def get_versioned_path(self, path: str, version: str = "v1") -> str:
        """
        Generate versioned API path.
        
        Args:
            path: Base path
            version: API version
            
        Returns:
            Versioned path
        """
        pass