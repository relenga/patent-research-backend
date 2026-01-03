"""
ID Generation Service interface.

Canonical UUID/ULID generation with single interface for ID creation.
Prevents ad-hoc uuid usage in future phases.
Phase 3: Provides working concrete implementation as canonical service.
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


# Concrete implementation embedded to avoid circular imports
import uuid
import random
import string
import re
import time


class ConcreteIDService(IDService):
    """Production implementation of IDService interface."""
    
    def __init__(self):
        """Initialize concrete ID service."""
        self._test_mode = False
        self._test_seed: Optional[int] = None
        self._sequential_counter = 1
    
    def generate_id(self, format: IDFormat = IDFormat.UUID4) -> str:
        """Generate new ID in specified format."""
        if self._test_mode and self._test_seed is not None:
            random.seed(self._test_seed)
            
        if format == IDFormat.UUID4:
            return str(uuid.uuid4())
        elif format == IDFormat.UUID7:
            # UUID7 not in standard library yet, use UUID4 for now
            return str(uuid.uuid4())
        elif format == IDFormat.ULID:
            # Simplified ULID-like implementation
            timestamp = int(time.time() * 1000)
            return f"{timestamp:013x}{uuid.uuid4().hex[:16]}"
        elif format == IDFormat.NANOID:
            # URL-safe alphabet
            alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_-"
            return ''.join(random.choices(alphabet, k=21))
        elif format == IDFormat.SEQUENTIAL:
            result = str(self._sequential_counter)
            self._sequential_counter += 1
            return result
        else:
            raise ValueError(f"Unsupported ID format: {format}")
    
    def generate_request_id(self) -> str:
        """Generate request correlation ID."""
        return f"req_{self.generate_id(IDFormat.UUID4)[:8]}"
    
    def generate_trace_id(self) -> str:
        """Generate distributed trace ID."""
        return f"trace_{self.generate_id(IDFormat.UUID4)[:16]}"
    
    def generate_session_id(self) -> str:
        """Generate session ID."""
        return f"sess_{self.generate_id(IDFormat.UUID4)[:12]}"
    
    def generate_entity_id(self, entity_type: Optional[str] = None) -> str:
        """Generate entity ID for business objects."""
        base_id = self.generate_id(IDFormat.UUID4)
        if entity_type:
            return f"{entity_type}_{base_id}"
        return base_id
    
    def validate_id(self, id_value: str, expected_format: Optional[IDFormat] = None) -> bool:
        """Validate ID format."""
        if not id_value:
            return False
            
        detected_format = self.detect_format(id_value)
        if detected_format is None:
            return False
            
        if expected_format is not None:
            return detected_format == expected_format
            
        return True
    
    def detect_format(self, id_value: str) -> Optional[IDFormat]:
        """Detect ID format from value."""
        if not id_value:
            return None
            
        # UUID4 pattern
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[4][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
        if re.match(uuid_pattern, id_value, re.IGNORECASE):
            return IDFormat.UUID4
            
        # NANOID pattern (URL-safe characters, typically 21 chars)
        nanoid_pattern = r'^[0-9A-Za-z_-]+$'
        if len(id_value) == 21 and re.match(nanoid_pattern, id_value):
            return IDFormat.NANOID
            
        # ULID-like pattern
        if len(id_value) == 29 and all(c in '0123456789abcdef' for c in id_value):
            return IDFormat.ULID
            
        # Sequential (numeric)
        if id_value.isdigit():
            return IDFormat.SEQUENTIAL
            
        return None
    
    def is_sortable_format(self, format: IDFormat) -> bool:
        """Check if ID format is sortable by creation time."""
        return format in [IDFormat.ULID, IDFormat.UUID7, IDFormat.SEQUENTIAL]
    
    def generate_short_id(self, length: int = 8) -> str:
        """Generate short ID for human-readable references."""
        if length < 1 or length > 64:
            raise ValueError(f"Invalid length: {length}")
            
        # Use URL-safe alphabet without ambiguous characters
        alphabet = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"
        return ''.join(random.choices(alphabet, k=length))
    
    def set_test_mode(self, enabled: bool, seed: Optional[int] = None) -> None:
        """Enable deterministic ID generation for testing."""
        self._test_mode = enabled
        self._test_seed = seed
        if enabled and seed is not None:
            random.seed(seed)
            self._sequential_counter = 1


# Create canonical service instance
id_service = ConcreteIDService()

# Make the working instance available as the canonical IDService  
__all__ = ['IDService', 'IDFormat', 'id_service']