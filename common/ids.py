"""
ID Generation Service interface.

Canonical UUID/ULID generation with single interface for ID creation.
Prevents ad-hoc uuid usage in future phases.
Phase 2: Interface contract only - no implementation.
"""

from abc import ABC, abstractmethod
from typing import Optional, Union
from enum import Enum


class IDFormat(Enum):
    """Supported ID formats."""
    UUID4 = "uuid4"          # Standard UUID version 4
    UUID7 = "uuid7"          # Time-ordered UUID version 7
    ULID = "ulid"            # Universally Unique Lexicographically Sortable Identifier
    NANOID = "nanoid"        # URL-safe unique string IDs
    SEQUENTIAL = "sequential" # Sequential integers (for testing)


class IDService(ABC):
    """
    Abstract interface for ID generation operations.
    
    Provides canonical ID generation with consistent format policies.
    Prevents ad-hoc UUID usage throughout the application.
    
    Phase 2: Interface contract only - no implementation.
    Runtime implementation deferred to Phase 3.
    
    Future Phase Note: Direct uuid.uuid4() or similar usage will be
    discouraged in favor of this service.
    """
    
    @abstractmethod
    def generate_id(self, format: IDFormat = IDFormat.UUID4) -> str:
        """
        Generate new ID in specified format.
        
        Primary method for ID generation. Default format should be
        suitable for most use cases.
        
        Args:
            format: ID format to generate
            
        Returns:
            Generated ID as string
            
        Raises:
            ValueError: If format is unsupported
        """
        pass
    
    @abstractmethod
    def generate_request_id(self) -> str:
        """
        Generate request correlation ID.
        
        Specialized method for request tracing. Should generate
        IDs suitable for correlation across service boundaries.
        
        Returns:
            Request correlation ID
        """
        pass
    
    @abstractmethod
    def generate_trace_id(self) -> str:
        """
        Generate distributed trace ID.
        
        Specialized method for distributed tracing. Should be
        compatible with common tracing systems.
        
        Returns:
            Trace ID suitable for distributed tracing
        """
        pass
    
    @abstractmethod
    def generate_session_id(self) -> str:
        """
        Generate session ID.
        
        Specialized method for user sessions. Should generate
        IDs suitable for session management.
        
        Returns:
            Session ID
        """
        pass
    
    @abstractmethod
    def generate_entity_id(self, entity_type: Optional[str] = None) -> str:
        """
        Generate entity ID for business objects.
        
        Specialized method for business entity IDs. May include
        entity type prefix or other conventions.
        
        Args:
            entity_type: Optional entity type for ID prefix/format
            
        Returns:
            Entity ID
        """
        pass
    
    @abstractmethod
    def validate_id(self, id_value: str, expected_format: Optional[IDFormat] = None) -> bool:
        """
        Validate ID format.
        
        Check if provided ID matches expected format constraints.
        
        Args:
            id_value: ID to validate
            expected_format: Expected format, or None to detect format
            
        Returns:
            True if valid, False otherwise
        """
        pass
    
    @abstractmethod
    def detect_format(self, id_value: str) -> Optional[IDFormat]:
        """
        Detect ID format from value.
        
        Attempt to identify the format of an existing ID.
        
        Args:
            id_value: ID to analyze
            
        Returns:
            Detected format or None if unrecognized
        """
        pass
    
    @abstractmethod
    def is_sortable_format(self, format: IDFormat) -> bool:
        """
        Check if ID format is sortable by creation time.
        
        Some formats (ULID, UUID7) are time-sortable, others are not.
        
        Args:
            format: ID format to check
            
        Returns:
            True if format is time-sortable
        """
        pass
    
    @abstractmethod
    def generate_short_id(self, length: int = 8) -> str:
        """
        Generate short ID for human-readable references.
        
        For use cases where full UUIDs are too long (URLs, user displays, etc.).
        Should be URL-safe and avoid ambiguous characters.
        
        Args:
            length: Desired length of short ID
            
        Returns:
            Short ID of specified length
            
        Raises:
            ValueError: If length is invalid
        """
        pass
    
    @abstractmethod
    def set_test_mode(self, enabled: bool, seed: Optional[int] = None) -> None:
        """
        Enable deterministic ID generation for testing.
        
        When enabled, IDs should be deterministic and predictable.
        Used for reproducible tests.
        
        Args:
            enabled: Whether to enable test mode
            seed: Optional seed for deterministic generation
        """
        pass