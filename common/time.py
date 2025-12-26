"""
Time/Clock Service interface.

Centralized UTC time source with mockable interface.
Prevents direct datetime.now() usage outside this service.
Phase 2: Interface contract only - no implementation.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Optional, Union


class TimeService(ABC):
    """
    Abstract interface for centralized time/clock operations.
    
    Provides mockable time source for testing and consistent UTC time handling.
    All time operations SHOULD go through this service to ensure consistency
    and testability.
    
    Phase 2: Interface contract only - no implementation.
    Runtime implementation deferred to Phase 3.
    
    Future Phase Note: Direct datetime.now() usage will be discouraged
    in favor of this service.
    """
    
    @abstractmethod
    def utc_now(self) -> datetime:
        """
        Get current UTC datetime.
        
        Primary method for getting current time. All implementations
        MUST return timezone-aware datetime in UTC.
        
        Returns:
            Current UTC datetime with timezone info
        """
        pass
    
    @abstractmethod
    def utc_timestamp(self) -> float:
        """
        Get current UTC timestamp as float.
        
        Convenience method for unix timestamp.
        
        Returns:
            UTC timestamp as seconds since epoch
        """
        pass
    
    @abstractmethod
    def iso_utc_now(self) -> str:
        """
        Get current UTC time as ISO format string.
        
        Convenience method for API responses and logging.
        Format: YYYY-MM-DDTHH:MM:SS.fffffZ
        
        Returns:
            ISO format UTC datetime string
        """
        pass
    
    @abstractmethod
    def parse_iso_datetime(self, iso_string: str) -> datetime:
        """
        Parse ISO format datetime string.
        
        Should handle various ISO formats and always return UTC.
        
        Args:
            iso_string: ISO format datetime string
            
        Returns:
            Timezone-aware datetime in UTC
            
        Raises:
            ValueError: If string cannot be parsed
        """
        pass
    
    @abstractmethod
    def to_iso_string(self, dt: datetime) -> str:
        """
        Convert datetime to ISO format string.
        
        Args:
            dt: Datetime to convert (will be converted to UTC if needed)
            
        Returns:
            ISO format string in UTC
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def sleep(self, seconds: Union[int, float]) -> None:
        """
        Sleep for specified seconds.
        
        Mockable sleep function for testing.
        
        Args:
            seconds: Seconds to sleep
        """
        pass
    
    @abstractmethod
    def set_fixed_time(self, fixed_time: Optional[datetime]) -> None:
        """
        Set fixed time for testing.
        
        When set, utc_now() should return this fixed time instead of real time.
        Used for deterministic testing.
        
        Args:
            fixed_time: Fixed time to return, or None to use real time
        """
        pass


class TimeZoneService(ABC):
    """
    Abstract interface for timezone operations.
    
    Separate from TimeService to keep core time operations simple.
    Phase 2: Interface contract only - no implementation.
    """
    
    @abstractmethod
    def convert_to_timezone(self, dt: datetime, timezone_name: str) -> datetime:
        """
        Convert UTC datetime to specific timezone.
        
        Args:
            dt: UTC datetime to convert
            timezone_name: Target timezone (e.g., 'America/New_York')
            
        Returns:
            Datetime in target timezone
            
        Raises:
            ValueError: If timezone is invalid
        """
        pass
    
    @abstractmethod
    def get_supported_timezones(self) -> list[str]:
        """
        Get list of supported timezone names.
        
        Returns:
            List of supported timezone identifiers
        """
        pass
    
    @abstractmethod
    def validate_timezone(self, timezone_name: str) -> bool:
        """
        Validate if timezone name is supported.
        
        Args:
            timezone_name: Timezone name to validate
            
        Returns:
            True if valid, False otherwise
        """
        pass