"""
Concrete ID Service Implementation

Production implementation of the abstract IDService interface
with all required ID generation methods for Phase 3.2A pipeline coordination.
"""

import uuid
import random
import string
from typing import Optional
import re

from common.ids import IDService, IDFormat


class ConcreteIDService(IDService):
    """
    Production implementation of IDService interface.
    
    Provides all required ID generation operations with multiple format support
    and deterministic testing capability.
    """
    
    def __init__(self):
        """Initialize concrete ID service."""
        self._test_mode = False
        self._test_seed: Optional[int] = None
        self._sequential_counter = 1
    
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
        if self._test_mode and self._test_seed is not None:
            random.seed(self._test_seed + self._sequential_counter)
        
        if format == IDFormat.UUID4:
            return str(uuid.uuid4())
        elif format == IDFormat.UUID7:
            # UUID7 not yet in standard library, use UUID4 for now
            return str(uuid.uuid4())
        elif format == IDFormat.ULID:
            # Simplified ULID implementation
            return self._generate_ulid_like()
        elif format == IDFormat.NANOID:
            return self._generate_nanoid()
        elif format == IDFormat.SEQUENTIAL:
            seq_id = str(self._sequential_counter)
            self._sequential_counter += 1
            return seq_id
        else:
            raise ValueError(f"Unsupported ID format: {format}")
    
    def generate_request_id(self) -> str:
        """
        Generate request correlation ID.
        
        Specialized method for request tracing. Should generate
        IDs suitable for correlation across service boundaries.
        
        Returns:
            Request correlation ID
        """
        if self._test_mode:
            return f"req_{self._sequential_counter:08d}"
        return f"req_{str(uuid.uuid4()).replace('-', '')[:16]}"
    
    def generate_trace_id(self) -> str:
        """
        Generate distributed trace ID.
        
        Specialized method for distributed tracing. Should be
        compatible with common tracing systems.
        
        Returns:
            Trace ID suitable for distributed tracing
        """
        if self._test_mode:
            return f"trace_{self._sequential_counter:016d}"
        # Generate 32-character hex string (128-bit)
        return f"trace_{str(uuid.uuid4()).replace('-', '')}"
    
    def generate_session_id(self) -> str:
        """
        Generate session ID.
        
        Specialized method for user sessions. Should generate
        IDs suitable for session management.
        
        Returns:
            Session ID
        """
        if self._test_mode:
            return f"sess_{self._sequential_counter:012d}"
        return f"sess_{str(uuid.uuid4()).replace('-', '')[:20]}"
    
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
        base_id = str(uuid.uuid4())
        if entity_type:
            return f"{entity_type}_{base_id}"
        return base_id
    
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
        if not id_value:
            return False
        
        if expected_format:
            detected = self.detect_format(id_value)
            return detected == expected_format
        
        # General validation - if any format is detected, it's valid
        return self.detect_format(id_value) is not None
    
    def detect_format(self, id_value: str) -> Optional[IDFormat]:
        """
        Detect ID format from value.
        
        Attempt to identify the format of an existing ID.
        
        Args:
            id_value: ID to analyze
            
        Returns:
            Detected format or None if unrecognized
        """
        if not id_value:
            return None
        
        # UUID4 pattern
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
        if re.match(uuid_pattern, id_value.lower()):
            return IDFormat.UUID4
        
        # Sequential (all digits)
        if id_value.isdigit():
            return IDFormat.SEQUENTIAL
        
        # NANOID (URL-safe characters)
        if re.match(r'^[A-Za-z0-9_-]+$', id_value) and len(id_value) >= 8:
            return IDFormat.NANOID
        
        # ULID-like pattern
        if len(id_value) == 26 and re.match(r'^[0-9A-HJKMNP-TV-Z]+$', id_value.upper()):
            return IDFormat.ULID
        
        return None
    
    def is_sortable_format(self, format: IDFormat) -> bool:
        """
        Check if ID format is sortable by creation time.
        
        Some formats (ULID, UUID7) are time-sortable, others are not.
        
        Args:
            format: ID format to check
            
        Returns:
            True if format is time-sortable
        """
        return format in (IDFormat.ULID, IDFormat.UUID7, IDFormat.SEQUENTIAL)
    
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
        if length < 4 or length > 64:
            raise ValueError("Length must be between 4 and 64")
        
        if self._test_mode:
            # Deterministic short ID for testing
            base = f"{self._sequential_counter:010d}"
            return base[:length].zfill(length)
        
        # URL-safe alphabet excluding ambiguous characters
        alphabet = "23456789ABCDEFGHJKMNPQRSTUVWXYZ"
        return ''.join(random.choice(alphabet) for _ in range(length))
    
    def set_test_mode(self, enabled: bool, seed: Optional[int] = None) -> None:
        """
        Enable deterministic ID generation for testing.
        
        When enabled, IDs should be deterministic and predictable.
        Used for reproducible tests.
        
        Args:
            enabled: Whether to enable test mode
            seed: Optional seed for deterministic generation
        """
        self._test_mode = enabled
        self._test_seed = seed
        if enabled:
            self._sequential_counter = 1
            if seed is not None:
                random.seed(seed)
    
    def _generate_ulid_like(self) -> str:
        """Generate ULID-like identifier (simplified implementation)."""
        # Simplified ULID: timestamp + randomness
        import time
        timestamp = int(time.time() * 1000)  # milliseconds
        
        # Crockford Base32 alphabet
        alphabet = "0123456789ABCDEFGHJKMNPQRSTUVWXYZ"
        
        # Encode timestamp (10 chars)
        ts_encoded = ""
        ts = timestamp
        for _ in range(10):
            ts_encoded = alphabet[ts % 32] + ts_encoded
            ts //= 32
        
        # Random part (16 chars)
        random_part = ''.join(random.choice(alphabet) for _ in range(16))
        
        return ts_encoded + random_part
    
    def _generate_nanoid(self, length: int = 21) -> str:
        """Generate NanoID."""
        alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_-"
        return ''.join(random.choice(alphabet) for _ in range(length))


# Global singleton instance for use throughout the application  
id_service = ConcreteIDService()