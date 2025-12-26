"""
Logging Interface for structured logging with correlation.

Structured logging contract with request_id correlation.
Phase 2: Interface contract only - no implementation.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union
from enum import Enum


class LogLevel(Enum):
    """Standard log levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogContext:
    """
    Structured log context data.
    
    Container for structured logging data with correlation fields.
    """
    
    def __init__(
        self,
        request_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        component: Optional[str] = None,
        operation: Optional[str] = None,
        **extra_fields: Any
    ):
        """
        Initialize log context.
        
        Args:
            request_id: Request correlation ID
            trace_id: Distributed trace ID
            user_id: User identifier
            session_id: Session identifier
            component: Component/module name
            operation: Operation/method name
            **extra_fields: Additional structured fields
        """
        self.request_id = request_id
        self.trace_id = trace_id
        self.user_id = user_id
        self.session_id = session_id
        self.component = component
        self.operation = operation
        self.extra_fields = extra_fields
    
    def add_field(self, key: str, value: Any) -> None:
        """Add additional structured field."""
        self.extra_fields[key] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging output."""
        result = {}
        if self.request_id:
            result['request_id'] = self.request_id
        if self.trace_id:
            result['trace_id'] = self.trace_id
        if self.user_id:
            result['user_id'] = self.user_id
        if self.session_id:
            result['session_id'] = self.session_id
        if self.component:
            result['component'] = self.component
        if self.operation:
            result['operation'] = self.operation
        result.update(self.extra_fields)
        return result


class LoggingService(ABC):
    """
    Abstract interface for structured logging operations.
    
    Provides structured logging with automatic correlation field injection.
    Integrates with ContextService for request correlation.
    
    Phase 2: Interface contract only - no implementation.
    Runtime implementation and log output configuration deferred to Phase 3.
    
    Future Phase Note: Direct logging.getLogger() usage should be discouraged
    in favor of this service for consistent structured logging.
    """
    
    @abstractmethod
    def debug(
        self,
        message: str,
        context: Optional[LogContext] = None,
        **extra_fields: Any
    ) -> None:
        """
        Log debug message.
        
        Args:
            message: Log message
            context: Optional log context (will auto-populate from current request context if None)
            **extra_fields: Additional structured fields
        """
        pass
    
    @abstractmethod
    def info(
        self,
        message: str,
        context: Optional[LogContext] = None,
        **extra_fields: Any
    ) -> None:
        """
        Log info message.
        
        Args:
            message: Log message
            context: Optional log context
            **extra_fields: Additional structured fields
        """
        pass
    
    @abstractmethod
    def warning(
        self,
        message: str,
        context: Optional[LogContext] = None,
        **extra_fields: Any
    ) -> None:
        """
        Log warning message.
        
        Args:
            message: Log message
            context: Optional log context
            **extra_fields: Additional structured fields
        """
        pass
    
    @abstractmethod
    def error(
        self,
        message: str,
        exception: Optional[Exception] = None,
        context: Optional[LogContext] = None,
        **extra_fields: Any
    ) -> None:
        """
        Log error message.
        
        Args:
            message: Log message
            exception: Optional exception to include
            context: Optional log context
            **extra_fields: Additional structured fields
        """
        pass
    
    @abstractmethod
    def critical(
        self,
        message: str,
        exception: Optional[Exception] = None,
        context: Optional[LogContext] = None,
        **extra_fields: Any
    ) -> None:
        """
        Log critical message.
        
        Args:
            message: Log message
            exception: Optional exception to include
            context: Optional log context
            **extra_fields: Additional structured fields
        """
        pass
    
    @abstractmethod
    def log(
        self,
        level: Union[LogLevel, str],
        message: str,
        exception: Optional[Exception] = None,
        context: Optional[LogContext] = None,
        **extra_fields: Any
    ) -> None:
        """
        Log message at specified level.
        
        Generic logging method for dynamic level selection.
        
        Args:
            level: Log level
            message: Log message
            exception: Optional exception to include
            context: Optional log context
            **extra_fields: Additional structured fields
        """
        pass
    
    @abstractmethod
    def create_context(
        self,
        component: Optional[str] = None,
        operation: Optional[str] = None,
        **extra_fields: Any
    ) -> LogContext:
        """
        Create log context with current request correlation.
        
        Automatically populates request_id, trace_id from current execution context.
        
        Args:
            component: Component/module name
            operation: Operation/method name
            **extra_fields: Additional fields
            
        Returns:
            LogContext with correlation fields populated
        """
        pass
    
    @abstractmethod
    def set_default_context(self, context: Optional[LogContext]) -> None:
        """
        Set default context for subsequent log calls.
        
        Used to set component-level defaults.
        
        Args:
            context: Default context or None to clear
        """
        pass
    
    @abstractmethod
    def get_logger_for_component(self, component_name: str) -> 'ComponentLogger':
        """
        Get component-specific logger.
        
        Returns logger with component name pre-configured.
        
        Args:
            component_name: Component identifier
            
        Returns:
            Component-specific logger
        """
        pass


class ComponentLogger(ABC):
    """
    Component-specific logger interface.
    
    Pre-configured with component name for consistent structured logging.
    """
    
    @abstractmethod
    def debug(self, message: str, operation: Optional[str] = None, **extra_fields: Any) -> None:
        """Log debug with component context."""
        pass
    
    @abstractmethod
    def info(self, message: str, operation: Optional[str] = None, **extra_fields: Any) -> None:
        """Log info with component context."""
        pass
    
    @abstractmethod
    def warning(self, message: str, operation: Optional[str] = None, **extra_fields: Any) -> None:
        """Log warning with component context."""
        pass
    
    @abstractmethod
    def error(self, message: str, exception: Optional[Exception] = None, operation: Optional[str] = None, **extra_fields: Any) -> None:
        """Log error with component context."""
        pass
    
    @abstractmethod
    def critical(self, message: str, exception: Optional[Exception] = None, operation: Optional[str] = None, **extra_fields: Any) -> None:
        """Log critical with component context."""
        pass