"""
Phase 3.2A Task 3.2A.8: State Change Event Publishing System

Comprehensive event system for pipeline state changes with real-time notifications
and external system integration hooks for monitoring and automation.

Implements event-driven architecture for pipeline state transitions:
- Real-time event publishing for all state changes
- WebSocket notifications for connected clients  
- External webhook integration for third-party systems
- Event history and replay capabilities
- Filtering and subscription management
- High-throughput async event processing
"""

import asyncio
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Callable, Set
from enum import Enum
from dataclasses import dataclass, asdict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
import json
import aiohttp
from pydantic import BaseModel, HttpUrl
from contextlib import asynccontextmanager

from app.core.logger import get_logger
from app.core.config import get_settings
from app.models.base import Base
from .state_machine import PipelineDocumentState, PipelineImageState


logger = get_logger(__name__)
settings = get_settings()


class EventType(str, Enum):
    """Types of pipeline events that can be published."""
    STATE_TRANSITION = "state_transition"
    COMPLETION_CHANGE = "completion_change"
    RESOURCE_ALLOCATION = "resource_allocation"
    ERROR_OCCURRED = "error_occurred"
    OVERRIDE_PERFORMED = "override_performed"
    PROCESSING_STARTED = "processing_started"
    PROCESSING_COMPLETED = "processing_completed"
    BATCH_COMPLETED = "batch_completed"
    RESOURCE_EXHAUSTED = "resource_exhausted"
    MANUAL_INTERVENTION = "manual_intervention"


class EventPriority(str, Enum):
    """Priority levels for event processing and delivery."""
    LOW = "low"
    NORMAL = "normal" 
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class EventPayload:
    """Structured payload for pipeline events."""
    event_id: str
    event_type: EventType
    timestamp: datetime
    priority: EventPriority
    source: str  # Component that generated the event
    
    # Core identifiers
    document_id: Optional[int] = None
    image_id: Optional[int] = None
    batch_id: Optional[str] = None
    user_id: Optional[int] = None
    
    # State information
    previous_state: Optional[str] = None
    current_state: Optional[str] = None
    
    # Processing details
    completion_percentage: Optional[float] = None
    resource_type: Optional[str] = None
    processing_duration: Optional[float] = None
    error_message: Optional[str] = None
    
    # Additional context
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with JSON-serializable values."""
        data = asdict(self)
        # Convert datetime to ISO string
        data['timestamp'] = self.timestamp.isoformat()
        return data


class PipelineEventLog(Base):
    """
    Event log table for pipeline state changes.
    
    Stores all pipeline events for history, debugging, and replay capabilities.
    """
    __tablename__ = "pipeline_event_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, index=True)
    
    # Event metadata
    event_type = Column(String(50), nullable=False, index=True)
    priority = Column(String(20), nullable=False, index=True)
    source = Column(String(100), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Entity references
    document_id = Column(Integer, index=True)
    image_id = Column(Integer, index=True)
    batch_id = Column(String(100), index=True)
    user_id = Column(Integer, index=True)
    
    # Event data
    payload = Column(JSONB, nullable=False)
    
    # Delivery tracking
    delivered = Column(Boolean, default=False)
    delivery_attempts = Column(Integer, default=0)
    last_delivery_attempt = Column(DateTime(timezone=True))
    delivery_errors = Column(JSONB, default=list)


class EventSubscription(BaseModel):
    """Configuration for event subscription."""
    subscription_id: str
    event_types: List[EventType]
    entity_filters: Dict[str, Any] = {}
    webhook_url: Optional[HttpUrl] = None
    active: bool = True
    max_retries: int = 3
    timeout_seconds: int = 30


class EventPublisher:
    """
    High-performance event publishing system for pipeline state changes.
    
    Handles real-time event distribution with multiple delivery mechanisms
    including WebSocket notifications and external webhooks.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._subscribers: Dict[str, EventSubscription] = {}
        self._websocket_clients: Set[Any] = set()
        self._event_queue: asyncio.Queue = asyncio.Queue()
        self._processing_task: Optional[asyncio.Task] = None
        self._http_session: Optional[aiohttp.ClientSession] = None
        
    async def start(self):
        """Start the event processing system."""
        self._http_session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        )
        self._processing_task = asyncio.create_task(self._process_event_queue())
        logger.info("Pipeline event publisher started")
    
    async def stop(self):
        """Stop the event processing system."""
        if self._processing_task:
            self._processing_task.cancel()
            try:
                await self._processing_task
            except asyncio.CancelledError:
                pass
        
        if self._http_session:
            await self._http_session.close()
        
        logger.info("Pipeline event publisher stopped")
    
    @asynccontextmanager
    async def lifespan(self):
        """Context manager for event publisher lifecycle."""
        await self.start()
        try:
            yield self
        finally:
            await self.stop()
    
    async def publish_event(self, payload: EventPayload) -> None:
        """
        Publish a pipeline event asynchronously.
        
        Args:
            payload: Event data to publish
        """
        # Store event in database
        event_log = PipelineEventLog(
            event_id=uuid.UUID(payload.event_id),
            event_type=payload.event_type.value,
            priority=payload.priority.value,
            source=payload.source,
            timestamp=payload.timestamp,
            document_id=payload.document_id,
            image_id=payload.image_id,
            batch_id=payload.batch_id,
            user_id=payload.user_id,
            payload=payload.to_dict()
        )
        
        self.db.add(event_log)
        await self.db.commit()
        
        # Queue for async processing
        await self._event_queue.put(payload)
        
        logger.debug(
            f"Event published: {payload.event_type.value}",
            extra={
                "event_id": payload.event_id,
                "document_id": payload.document_id,
                "priority": payload.priority.value
            }
        )
    
    async def _process_event_queue(self):
        """Process events from the queue continuously."""
        while True:
            try:
                # Get next event with timeout
                payload = await asyncio.wait_for(
                    self._event_queue.get(), 
                    timeout=1.0
                )
                
                # Process event delivery
                await self._deliver_event(payload)
                
            except asyncio.TimeoutError:
                # No events in queue, continue
                continue
            except Exception as e:
                logger.error(f"Error processing event queue: {e}")
                await asyncio.sleep(1)  # Brief pause before retry
    
    async def _deliver_event(self, payload: EventPayload):
        """Deliver event to all appropriate subscribers."""
        delivery_tasks = []
        
        # WebSocket delivery
        if self._websocket_clients:
            delivery_tasks.append(
                self._deliver_to_websockets(payload)
            )
        
        # Webhook delivery
        for subscription in self._subscribers.values():
            if self._should_deliver_to_subscription(payload, subscription):
                delivery_tasks.append(
                    self._deliver_to_webhook(payload, subscription)
                )
        
        # Execute deliveries concurrently
        if delivery_tasks:
            await asyncio.gather(*delivery_tasks, return_exceptions=True)
    
    def _should_deliver_to_subscription(
        self, 
        payload: EventPayload, 
        subscription: EventSubscription
    ) -> bool:
        """Check if event matches subscription criteria."""
        if not subscription.active:
            return False
        
        if payload.event_type not in subscription.event_types:
            return False
        
        # Check entity filters
        for filter_key, filter_value in subscription.entity_filters.items():
            payload_value = getattr(payload, filter_key, None)
            if payload_value != filter_value:
                return False
        
        return True
    
    async def _deliver_to_websockets(self, payload: EventPayload):
        """Deliver event to all connected WebSocket clients."""
        if not self._websocket_clients:
            return
        
        message = json.dumps(payload.to_dict())
        disconnected_clients = set()
        
        for client in self._websocket_clients:
            try:
                await client.send_text(message)
            except Exception as e:
                logger.warning(f"Failed to deliver to WebSocket client: {e}")
                disconnected_clients.add(client)
        
        # Remove disconnected clients
        self._websocket_clients -= disconnected_clients
    
    async def _deliver_to_webhook(
        self, 
        payload: EventPayload, 
        subscription: EventSubscription
    ):
        """Deliver event to webhook endpoint."""
        if not subscription.webhook_url or not self._http_session:
            return
        
        for attempt in range(subscription.max_retries + 1):
            try:
                async with self._http_session.post(
                    str(subscription.webhook_url),
                    json=payload.to_dict(),
                    timeout=subscription.timeout_seconds
                ) as response:
                    if response.status < 400:
                        logger.debug(
                            f"Event delivered to webhook: {subscription.subscription_id}"
                        )
                        return
                    else:
                        logger.warning(
                            f"Webhook delivery failed with status {response.status}: "
                            f"{subscription.subscription_id}"
                        )
            
            except Exception as e:
                logger.warning(
                    f"Webhook delivery attempt {attempt + 1} failed: {e}"
                )
                
                if attempt < subscription.max_retries:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        # Log final failure
        logger.error(
            f"Failed to deliver event to webhook after {subscription.max_retries + 1} attempts: "
            f"{subscription.subscription_id}"
        )
    
    def subscribe(self, subscription: EventSubscription) -> None:
        """Add an event subscription."""
        self._subscribers[subscription.subscription_id] = subscription
        logger.info(f"Added event subscription: {subscription.subscription_id}")
    
    def unsubscribe(self, subscription_id: str) -> bool:
        """Remove an event subscription."""
        if subscription_id in self._subscribers:
            del self._subscribers[subscription_id]
            logger.info(f"Removed event subscription: {subscription_id}")
            return True
        return False
    
    def add_websocket_client(self, client) -> None:
        """Add a WebSocket client for real-time events."""
        self._websocket_clients.add(client)
        logger.debug("WebSocket client connected for events")
    
    def remove_websocket_client(self, client) -> None:
        """Remove a WebSocket client."""
        self._websocket_clients.discard(client)
        logger.debug("WebSocket client disconnected")
    
    async def get_event_history(
        self,
        event_types: Optional[List[EventType]] = None,
        document_id: Optional[int] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[PipelineEventLog]:
        """
        Retrieve event history with filtering options.
        
        Args:
            event_types: Filter by event types
            document_id: Filter by document ID  
            start_time: Filter events after this time
            end_time: Filter events before this time
            limit: Maximum number of events to return
            
        Returns:
            List of event log records
        """
        from sqlalchemy import select, desc, and_
        
        stmt = select(PipelineEventLog).order_by(desc(PipelineEventLog.timestamp))
        
        conditions = []
        
        if event_types:
            conditions.append(
                PipelineEventLog.event_type.in_([et.value for et in event_types])
            )
        
        if document_id:
            conditions.append(PipelineEventLog.document_id == document_id)
        
        if start_time:
            conditions.append(PipelineEventLog.timestamp >= start_time)
        
        if end_time:
            conditions.append(PipelineEventLog.timestamp <= end_time)
        
        if conditions:
            stmt = stmt.where(and_(*conditions))
        
        stmt = stmt.limit(limit)
        
        result = await self.db.execute(stmt)
        return result.scalars().all()


class EventPayloadBuilder:
    """Helper class to build standardized event payloads."""
    
    @staticmethod
    def state_transition(
        document_id: Optional[int] = None,
        image_id: Optional[int] = None,
        previous_state: Optional[str] = None,
        current_state: Optional[str] = None,
        source: str = "state_machine",
        priority: EventPriority = EventPriority.NORMAL,
        user_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> EventPayload:
        """Build payload for state transition event."""
        return EventPayload(
            event_id=str(uuid.uuid4()),
            event_type=EventType.STATE_TRANSITION,
            timestamp=datetime.now(timezone.utc),
            priority=priority,
            source=source,
            document_id=document_id,
            image_id=image_id,
            previous_state=previous_state,
            current_state=current_state,
            user_id=user_id,
            metadata=metadata or {}
        )
    
    @staticmethod
    def processing_completed(
        document_id: Optional[int] = None,
        completion_percentage: Optional[float] = None,
        processing_duration: Optional[float] = None,
        source: str = "processing_engine",
        priority: EventPriority = EventPriority.NORMAL,
        metadata: Optional[Dict[str, Any]] = None
    ) -> EventPayload:
        """Build payload for processing completion event."""
        return EventPayload(
            event_id=str(uuid.uuid4()),
            event_type=EventType.PROCESSING_COMPLETED,
            timestamp=datetime.now(timezone.utc),
            priority=priority,
            source=source,
            document_id=document_id,
            completion_percentage=completion_percentage,
            processing_duration=processing_duration,
            metadata=metadata or {}
        )
    
    @staticmethod
    def error_occurred(
        error_message: str,
        document_id: Optional[int] = None,
        image_id: Optional[int] = None,
        source: str = "pipeline_system",
        priority: EventPriority = EventPriority.HIGH,
        metadata: Optional[Dict[str, Any]] = None
    ) -> EventPayload:
        """Build payload for error event."""
        return EventPayload(
            event_id=str(uuid.uuid4()),
            event_type=EventType.ERROR_OCCURRED,
            timestamp=datetime.now(timezone.utc),
            priority=priority,
            source=source,
            document_id=document_id,
            image_id=image_id,
            error_message=error_message,
            metadata=metadata or {}
        )
    
    @staticmethod
    def manual_intervention(
        document_id: Optional[int] = None,
        user_id: Optional[int] = None,
        previous_state: Optional[str] = None,
        current_state: Optional[str] = None,
        source: str = "admin_override",
        priority: EventPriority = EventPriority.CRITICAL,
        metadata: Optional[Dict[str, Any]] = None
    ) -> EventPayload:
        """Build payload for manual intervention event."""
        return EventPayload(
            event_id=str(uuid.uuid4()),
            event_type=EventType.MANUAL_INTERVENTION,
            timestamp=datetime.now(timezone.utc),
            priority=priority,
            source=source,
            document_id=document_id,
            user_id=user_id,
            previous_state=previous_state,
            current_state=current_state,
            metadata=metadata or {}
        )


# Global event publisher instance
_event_publisher: Optional[EventPublisher] = None

async def get_event_publisher(db: AsyncSession) -> EventPublisher:
    """Get or create the global event publisher instance."""
    global _event_publisher
    if _event_publisher is None:
        _event_publisher = EventPublisher(db)
        await _event_publisher.start()
    return _event_publisher


# Standards.md compliance: Export main classes and functions
__all__ = [
    "EventType",
    "EventPriority", 
    "EventPayload",
    "PipelineEventLog",
    "EventSubscription",
    "EventPublisher",
    "EventPayloadBuilder",
    "get_event_publisher"
]