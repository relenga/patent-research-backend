"""
Test configuration for Phase 3.2A Pipeline Coordination Test Suite

Provides test fixtures, configuration, and utilities for comprehensive
testing of pipeline coordination features.
"""

import pytest
import asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import Mock, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import get_settings
from app.models.base import Base


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async testing."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def test_engine():
    """Create test database engine."""
    # Use in-memory SQLite for fast testing
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False}
    )
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    await engine.dispose()


@pytest.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session


@pytest.fixture
def mock_user():
    """Create mock user for testing."""
    return Mock(
        id=1,
        email="test@example.com",
        is_superuser=True,
        role="admin",
        is_active=True
    )


@pytest.fixture
def mock_settings():
    """Create mock settings for testing."""
    settings = Mock()
    settings.DATABASE_URL = "sqlite+aiosqlite:///:memory:"
    settings.SECRET_KEY = "test_secret_key"
    settings.ALGORITHM = "HS256"
    settings.ACCESS_TOKEN_EXPIRE_MINUTES = 30
    return settings


# Test data factories
class TestDataFactory:
    """Factory for creating test data."""
    
    @staticmethod
    def create_test_document(id: int = 1, **kwargs):
        """Create test document data."""
        defaults = {
            'id': id,
            'filename': f'test_document_{id}.pdf',
            'state': 'uploaded',
            'created_at': '2024-01-01T00:00:00Z',
            'updated_at': '2024-01-01T00:00:00Z'
        }
        defaults.update(kwargs)
        return defaults
    
    @staticmethod
    def create_test_image(id: int = 1, document_id: int = 1, **kwargs):
        """Create test image data."""
        defaults = {
            'id': id,
            'document_id': document_id,
            'state': 'discovered',
            'diagram_type': 'critical',
            'text_content': f'Test diagram {id}',
            'metadata': {}
        }
        defaults.update(kwargs)
        return defaults


# Test markers
pytest_plugins = ["pytest_asyncio"]

# Test configuration
pytestmark = pytest.mark.asyncio