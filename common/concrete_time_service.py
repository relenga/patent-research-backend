"""
Concrete Time Service Implementation

Production implementation of the abstract TimeService interface
with all required methods for Phase 3.2A pipeline coordination.
"""

from datetime import datetime, timezone, timedelta
import time
from typing import Optional, Union

from common.time import TimeService


class ConcreteTimeService(TimeService):
    """
    Production implementation of TimeService interface.
    
    Provides all required time operations with UTC timezone handling
    and support for deterministic testing via fixed time setting.
    """
    
    def __init__(self):
        """Initialize concrete time service."""
        self._fixed_time: Optional[datetime] = None
    
    def utc_now(self) -> datetime:
        """
        Get current UTC datetime.
        
        Returns fixed time if set (for testing), otherwise real UTC time.
        
        Returns:
            Current UTC datetime with timezone info
        """
        if self._fixed_time is not None:
            return self._fixed_time
        return datetime.now(timezone.utc)
    
    def utc_timestamp(self) -> float:
        """
        Get current UTC timestamp.
        
        Returns:
            UTC timestamp as seconds since epoch
        """
        return self.utc_now().timestamp()
    
    def iso_utc_now(self) -> str:
        """
        Get current UTC time as ISO format string.
        
        Convenience method for API responses and logging.
        Format: YYYY-MM-DDTHH:MM:SS.fffffZ
        
        Returns:
            ISO format UTC datetime string
        """
        return self.utc_now().isoformat()
    
    def parse_iso_datetime(self, iso_string: str) -> datetime:
        """
        Parse ISO format datetime string.
        
        Handles various ISO formats and always returns UTC.
        
        Args:
            iso_string: ISO format datetime string
            
        Returns:
            Timezone-aware datetime in UTC
            
        Raises:
            ValueError: If string cannot be parsed
        """
        try:
            # Handle ISO format with Z suffix
            if iso_string.endswith('Z'):
                dt = datetime.fromisoformat(iso_string[:-1])
                return dt.replace(tzinfo=timezone.utc)
            
            # Handle ISO format with timezone info
            dt = datetime.fromisoformat(iso_string)
            
            # If no timezone info, assume UTC
            if dt.tzinfo is None:
                return dt.replace(tzinfo=timezone.utc)
            
            # Convert to UTC if needed
            return dt.astimezone(timezone.utc)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Cannot parse ISO datetime string '{iso_string}': {e}")
    
    def to_iso_string(self, dt: datetime) -> str:
        """
        Convert datetime to ISO format string.
        
        Args:
            dt: Datetime to convert (will be converted to UTC if needed)
            
        Returns:
            ISO format string in UTC
        """
        # Convert to UTC if needed
        if dt.tzinfo is None:
            # Assume naive datetime is UTC
            dt = dt.replace(tzinfo=timezone.utc)
        elif dt.tzinfo != timezone.utc:
            dt = dt.astimezone(timezone.utc)
        
        return dt.isoformat()
    
    def add_seconds(self, dt: datetime, seconds: Union[int, float]) -> datetime:
        """
        Add seconds to datetime.
        
        Convenience method for time calculations.
        
        Args:
            dt: Base datetime
            seconds: Seconds to add (can be negative)
            
        Returns:
            New datetime with seconds added
        """
        return dt + timedelta(seconds=seconds)
    
    def is_expired(self, dt: datetime, ttl_seconds: Union[int, float]) -> bool:
        """
        Check if datetime is expired based on TTL.
        
        Convenience method for expiration checking.
        
        Args:
            dt: Datetime to check
            ttl_seconds: Time-to-live in seconds
            
        Returns:
            True if expired, False otherwise
        """
        current_time = self.utc_now()
        expiry_time = self.add_seconds(dt, ttl_seconds)
        return current_time >= expiry_time
    
    def sleep(self, seconds: Union[int, float]) -> None:
        """
        Sleep for specified seconds.
        
        Mockable sleep function for testing.
        
        Args:
            seconds: Seconds to sleep
        """
        time.sleep(seconds)
    
    def set_fixed_time(self, fixed_time: Optional[datetime]) -> None:
        """
        Set fixed time for testing.
        
        When set, utc_now() should return this fixed time instead of real time.
        Used for deterministic testing.
        
        Args:
            fixed_time: Fixed time to return, or None to use real time
        """
        self._fixed_time = fixed_time
    
    # Legacy methods for backward compatibility
    def parse_iso(self, iso_string: str) -> datetime:
        """Legacy method - use parse_iso_datetime instead."""
        return self.parse_iso_datetime(iso_string)
    
    def to_iso(self, dt: datetime) -> str:
        """Legacy method - use to_iso_string instead."""
        return self.to_iso_string(dt)


# Global singleton instance for use throughout the application
time_service = ConcreteTimeService()