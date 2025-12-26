"""
Request/Execution Context Service interface.

Provides request correlation, tracing metadata, and lifecycle-safe propagation.
Phase 2: Interface contract only - no implementation.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union
from datetime import datetime


class ExecutionContext:
    """
    Execution context data container.
    
    Holds request correlation data and metadata for the current execution context.
    Thread-safe and lifecycle-aware.
    """
    
    def __init__(
        self,
        request_id: str,
        trace_id: Optional[str] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        correlation_data: Optional[Dict[str, Any]] = None,
        created_at: Optional[datetime] = None
    ):
        """
        Initialize execution context.
        
        Args:
            request_id: Unique request identifier
            trace_id: Distributed tracing identifier
            user_id: Authenticated user identifier
            session_id: Session identifier
            correlation_data: Additional correlation metadata
            created_at: Context creation timestamp
        """
        self.request_id = request_id
        self.trace_id = trace_id
        self.user_id = user_id
        self.session_id = session_id
        self.correlation_data = correlation_data or {}
        self.created_at = created_at
    
    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to correlation data."""
        self.correlation_data[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata from correlation data."""
        return self.correlation_data.get(key, default)


class ContextService(ABC):
    """
    Abstract interface for request/execution context management.
    
    Provides lifecycle-safe context propagation across async boundaries,
    request correlation, and tracing metadata management.
    
    Phase 2: Interface contract only - no implementation.
    Runtime wiring and context storage mechanism deferred to Phase 3.
    """
    
    @abstractmethod
    def create_context(
        self,
        request_id: str,
        trace_id: Optional[str] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        **metadata: Any
    ) -> ExecutionContext:
        """
        Create new execution context.
        
        Args:
            request_id: Unique request identifier
            trace_id: Optional distributed tracing ID
            user_id: Optional authenticated user ID
            session_id: Optional session ID
            **metadata: Additional correlation metadata
            
        Returns:
            New ExecutionContext instance
        """
        pass
    
    @abstractmethod
    def set_current_context(self, context: ExecutionContext) -> None:
        """
        Set the current execution context.
        
        Should be thread-safe and async-aware.
        
        Args:
            context: Context to set as current
        """
        pass
    
    @abstractmethod
    def get_current_context(self) -> Optional[ExecutionContext]:
        """
        Get the current execution context.
        
        Should be thread-safe and async-aware.
        
        Returns:
            Current ExecutionContext or None if no context set
        """
        pass
    
    @abstractmethod
    def clear_context(self) -> None:
        """
        Clear the current execution context.
        
        Should be called at request completion to prevent context leakage.
        """
        pass
    
    @abstractmethod
    def get_request_id(self) -> Optional[str]:
        """
        Get current request ID.
        
        Convenience method for common use case.
        
        Returns:
            Current request ID or None
        """
        pass
    
    @abstractmethod
    def get_trace_id(self) -> Optional[str]:
        """
        Get current trace ID.
        
        Convenience method for distributed tracing.
        
        Returns:
            Current trace ID or None
        """
        pass
    
    @abstractmethod
    def propagate_context(self, target_callable: Any) -> Any:
        """
        Propagate current context to target callable.
        
        Should work with both sync and async callables.
        Implementation may use decorators, context managers, or other mechanisms.
        
        Args:
            target_callable: Function/method to receive context
            
        Returns:
            Wrapped callable with context propagation
        """
        pass