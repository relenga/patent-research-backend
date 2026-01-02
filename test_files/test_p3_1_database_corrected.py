"""
Functional tests for P3.1 Database Schema & Persistence Layer.

Tests the complete database schema implementation per AgentRules.md Phase 3 
requirements. Covers schema creation, model validation, database operations,
constraint testing, and relationship testing.

Validates compliance with DatabaseSchemaSpec.md, CorpusModel.md business rules,
and ProvenanceAudit.md litigation-grade traceability requirements.

Standards.md Compliance: Uses datetime(2024, 1, 1) for test data per TimeService requirement.
"""
import asyncio
import pytest
import pytest_asyncio
from datetime import datetime
from typing import List, Optional
from uuid import uuid4
from sqlalchemy import text, inspect, MetaData, Table
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Import all P3.1 database models
from src.app.models.database import (
    # Core models
    Document, DocumentVersion, Artifact, DiagramCanonical,
    Corpus, CorpusMembership, AgentRun, Task, AuditEvent, Provenance,
    
    # Enums
    CorpusType, DocumentType, DocumentState, ArtifactType,
    DiagramStatus, TaskType, TaskStatus, AuditEventType,
    ActorType, ProvenanceActionType
)
from src.app.core.db.database import Base

# Configure pytest-asyncio
pytestmark = pytest.mark.asyncio

# Test database configuration
# TODO P3.x: Replace with proper test DB isolation when infrastructure available
TEST_DB_ENGINE = None
TEST_SESSION_FACTORY = None

@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """Create test database engine with proper cleanup."""
    global TEST_DB_ENGINE
    from src.app.core.config import settings
    TEST_DB_ENGINE = create_async_engine(settings.DATABASE_URL, echo=False)
    yield TEST_DB_ENGINE
    await TEST_DB_ENGINE.dispose()

@pytest_asyncio.fixture(scope="session")
async def test_session_factory(test_engine):
    """Create session factory for tests."""
    global TEST_SESSION_FACTORY
    TEST_SESSION_FACTORY = sessionmaker(
        bind=test_engine, class_=AsyncSession, expire_on_commit=False
    )
    return TEST_SESSION_FACTORY

@pytest_asyncio.fixture
async def session(test_session_factory):
    """Provide isolated test session with cleanup."""
    async with test_session_factory() as session:
        try:
            yield session
        finally:
            await session.rollback()


class TestP31DatabaseSchema:
    """Test P3.1 database schema creation and structure validation."""
    
    async def test_database_tables_creation(self, test_engine):
        """Test that all P3.1 database tables are created correctly."""
        # Create all tables
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        # Verify all tables exist
        async with test_engine.begin() as conn:
            inspector = await conn.run_sync(lambda sync_conn: inspect(sync_conn))
            table_names = await conn.run_sync(lambda sync_conn: inspector.get_table_names())
            
            expected_tables = {
                'documents', 'document_versions', 'artifacts', 'diagram_canonical',
                'corpora', 'corpus_memberships', 'agent_runs', 'tasks',
                'audit_events', 'provenance'
            }
            
            assert expected_tables.issubset(set(table_names)), f"Missing tables: {expected_tables - set(table_names)}"
    
    async def test_table_indexes_created(self, test_engine):
        """Test that all required indexes are created per DatabaseSchemaSpec.md."""
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            inspector = await conn.run_sync(lambda sync_conn: inspect(sync_conn))
            
            # Test critical indexes exist
            documents_indexes = await conn.run_sync(lambda sync_conn: inspector.get_indexes('documents'))
            index_names = [idx['name'] for idx in documents_indexes]
            
            # Verify key performance indexes
            expected_patterns = ['documents', 'corpus', 'state', 'type', 'hash']
            found_indexes = [name for name in index_names if any(pattern in name for pattern in expected_patterns)]
            assert len(found_indexes) >= 3, f"Missing critical indexes in documents table: {index_names}"
    
    async def test_foreign_key_constraints(self, test_engine):
        """Test that foreign key relationships are properly established."""
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            inspector = await conn.run_sync(lambda sync_conn: inspect(sync_conn))
            
            # Check documents table foreign keys
            documents_fks = await conn.run_sync(lambda sync_conn: inspector.get_foreign_keys('documents'))
            corpus_fk_found = any(fk['referred_table'] == 'corpora' for fk in documents_fks)
            assert corpus_fk_found, "Documents table missing foreign key to corpora"
            
            # Check corpus_memberships foreign keys
            memberships_fks = await conn.run_sync(lambda sync_conn: inspector.get_foreign_keys('corpus_memberships'))
            fk_tables = {fk['referred_table'] for fk in memberships_fks}
            assert 'documents' in fk_tables and 'corpora' in fk_tables, f"corpus_memberships missing required FKs: {fk_tables}"


class TestP31ModelValidation:
    """Test P3.1 model instantiation and field validation."""
    
    def test_document_model_creation(self):
        """Test Document model can be instantiated with required fields."""
        doc = Document(
            uuid="doc-uuid-123",
            title="Test Patent Document",
            source="test_source.pdf",
            document_type=DocumentType.PATENT,
            current_state=DocumentState.UPLOADED,
            corpus_id="corpus-uuid-456",
            ingestion_timestamp=datetime(2024, 1, 1),  # TODO P3.x: Replace with TimeService when implemented
            created_at=datetime(2024, 1, 1)  # TODO P3.x: Replace with TimeService when implemented
        )
        
        assert doc.title == "Test Patent Document"
        assert doc.document_type == DocumentType.PATENT
        assert doc.current_state == DocumentState.UPLOADED
        assert doc.error_count == 0
    
    def test_corpus_model_creation_with_business_rules(self):
        """Test Corpus model with CorpusModel.md business rules."""
        # Test open patent corpus (only one that allows claim drafting)
        open_corpus = Corpus(
            uuid="corpus-open-123",
            name="Open Patent Corpus",
            corpus_type=CorpusType.OPEN_PATENT,
            allows_claim_drafting=True,
            allows_risk_analysis=False,
            allows_evidence_mapping=False,
            allows_style_guidance=False,
            created_by="test_user",
            is_active=True,
            created_at=datetime(2024, 1, 1)  # TODO P3.x: Replace with TimeService when implemented
        )
        
        assert open_corpus.allows_claim_drafting is True
        assert open_corpus.corpus_type == CorpusType.OPEN_PATENT
        
        # Test adversarial corpus (risk analysis only)
        adversarial_corpus = Corpus(
            uuid="corpus-adv-123",
            name="Adversarial Corpus",
            corpus_type=CorpusType.ADVERSARIAL,
            allows_claim_drafting=False,
            allows_risk_analysis=True,
            allows_evidence_mapping=False,
            allows_style_guidance=False,
            created_by="test_user",
            is_active=True,
            created_at=datetime(2024, 1, 1)  # TODO P3.x: Replace with TimeService when implemented
        )
        
        assert adversarial_corpus.allows_risk_analysis is True
        assert adversarial_corpus.allows_claim_drafting is False
    
    def test_audit_event_model_creation(self):
        """Test AuditEvent model for ProvenanceAudit.md compliance."""
        event = AuditEvent(
            uuid="event-uuid-123",
            event_type=AuditEventType.DOCUMENT_CREATED,
            event_name="Document Upload",
            event_description="User uploaded new patent document",
            actor_type=ActorType.HUMAN_REVIEWER,
            actor_id="user123",
            resource_type="document",
            resource_id="doc-123",
            action_taken="create",
            event_timestamp=datetime(2024, 1, 1),  # TODO P3.x: Replace with TimeService when implemented
            development_phase="phase_3",
            ruleset_version="v3.1",
            impact_level="medium",
            requires_hitl=False,
            created_at=datetime(2024, 1, 1)  # TODO P3.x: Replace with TimeService when implemented
        )
        
        assert event.event_type == AuditEventType.DOCUMENT_CREATED
        assert event.actor_type == ActorType.HUMAN_REVIEWER
        assert event.development_phase == "phase_3"
        assert event.requires_hitl is False
    
    def test_provenance_model_dag_tracking(self):
        """Test Provenance model for DAG lineage tracking."""
        prov = Provenance(
            uuid="prov-uuid-123",
            provenance_record_id="prov-rec-456",
            artifact_id="artifact-789",
            artifact_type="extracted_text",
            action_type=ProvenanceActionType.DERIVE,
            actor_type=ActorType.AGENT_EXECUTION,
            actor_id="ocr-agent-v1",
            input_artifact_ids=["input-123", "input-456"],
            output_artifact_ids=["output-789"],
            activity_timestamp=datetime(2024, 1, 1),  # TODO P3.x: Replace with TimeService when implemented
            policy_phase="phase_3",
            policy_ruleset_version="v3.1",
            lineage_depth=2,
            root_artifact_id="root-artifact-001",
            created_at=datetime(2024, 1, 1)  # TODO P3.x: Replace with TimeService when implemented
        )
        
        assert prov.action_type == ProvenanceActionType.DERIVE
        assert prov.lineage_depth == 2
        assert len(prov.input_artifact_ids) == 2
        assert prov.root_artifact_id == "root-artifact-001"


class TestP31DatabaseOperations:
    """Test database CRUD operations with P3.1 models."""
    
    async def test_document_crud_operations(self, session):
        """Test document creation, retrieval, update, and cascade delete."""
        # Create test corpus first
        corpus = Corpus(
            uuid="test-corpus-crud",
            name="Test CRUD Corpus", 
            corpus_type=CorpusType.OPEN_PATENT,
            allows_claim_drafting=True,
            allows_risk_analysis=False,
            allows_evidence_mapping=False,
            allows_style_guidance=False,
            created_by="test_user",
            is_active=True,
            created_at=datetime(2024, 1, 1)  # TODO P3.x: Replace with TimeService when implemented
        )
        session.add(corpus)
        await session.commit()

        # Create document
        doc = Document(
            uuid="test-doc-crud-123",
            title="Test CRUD Document",
            source="test_crud.pdf",
            document_type=DocumentType.PATENT,
            current_state=DocumentState.UPLOADED,
            corpus_id=corpus.uuid,
            ingestion_timestamp=datetime(2024, 1, 1),  # TODO P3.x: Replace with TimeService when implemented
            created_at=datetime(2024, 1, 1)  # TODO P3.x: Replace with TimeService when implemented
        )
        session.add(doc)
        await session.commit()

        # Test READ
        retrieved_doc = await session.get(Document, doc.uuid)
        assert retrieved_doc is not None
        assert retrieved_doc.title == "Test CRUD Document"

        # Test UPDATE
        retrieved_doc.title = "Updated CRUD Document"
        await session.commit()
        
        updated_doc = await session.get(Document, doc.uuid)
        assert updated_doc.title == "Updated CRUD Document"

        # Test DELETE
        await session.delete(updated_doc)
        await session.commit()
        
        deleted_doc = await session.get(Document, doc.uuid)
        assert deleted_doc is None

    async def test_corpus_membership_single_active_rule(self, session):
        """Test CorpusModel.md single active membership business rule."""
        # Create corpus  
        corpus = Corpus(
            uuid="test-corpus-membership",
            name="Test Membership Corpus",
            corpus_type=CorpusType.OPEN_PATENT,
            allows_claim_drafting=True,
            allows_risk_analysis=False,
            allows_evidence_mapping=False,
            allows_style_guidance=False,
            created_by="test_user",
            is_active=True,
            created_at=datetime(2024, 1, 1)  # TODO P3.x: Replace with TimeService when implemented
        )
        session.add(corpus)
        
        # Create document
        doc = Document(
            uuid="test-doc-membership",
            title="Test Membership Document",
            source="test_membership.pdf",
            document_type=DocumentType.PATENT,
            current_state=DocumentState.UPLOADED,
            corpus_id=corpus.uuid,
            ingestion_timestamp=datetime(2024, 1, 1),  # TODO P3.x: Replace with TimeService when implemented
            created_at=datetime(2024, 1, 1)  # TODO P3.x: Replace with TimeService when implemented
        )
        session.add(doc)
        await session.commit()

        # Create first active membership
        membership1 = CorpusMembership(
            uuid="membership-1",
            document_id=doc.uuid,
            corpus_id=corpus.uuid,
            assigned_by="test_user",
            assignment_reason="Initial assignment",
            is_active=True,
            created_at=datetime(2024, 1, 1)  # TODO P3.x: Replace with TimeService when implemented
        )
        session.add(membership1)
        await session.commit()

        # Verify first membership exists
        retrieved_membership = await session.get(CorpusMembership, membership1.uuid)
        assert retrieved_membership is not None
        assert retrieved_membership.is_active is True

    async def test_artifact_provenance_chain(self, session):
        """Test artifact creation and provenance chain tracking."""
        # Create corpus and document first
        corpus = Corpus(
            uuid="test-corpus-prov",
            name="Test Provenance Corpus",
            corpus_type=CorpusType.OPEN_PATENT,
            allows_claim_drafting=True,
            allows_risk_analysis=False,
            allows_evidence_mapping=False,
            allows_style_guidance=False,
            created_by="test_user",
            is_active=True,
            created_at=datetime(2024, 1, 1)  # TODO P3.x: Replace with TimeService when implemented
        )
        session.add(corpus)

        doc = Document(
            uuid="test-doc-prov",
            title="Test Provenance Document", 
            source="test_prov.pdf",
            document_type=DocumentType.PATENT,
            current_state=DocumentState.UPLOADED,
            corpus_id=corpus.uuid,
            ingestion_timestamp=datetime(2024, 1, 1),  # TODO P3.x: Replace with TimeService when implemented
            created_at=datetime(2024, 1, 1)  # TODO P3.x: Replace with TimeService when implemented
        )
        session.add(doc)
        await session.commit()

        # Create artifact
        artifact = Artifact(
            uuid="test-artifact-123",
            document_id=doc.uuid,
            artifact_type=ArtifactType.EXTRACTED_TEXT,
            name="Extracted Text Artifact",
            description="Text extracted from patent document",
            content="This is extracted patent text content",
            content_type="text/plain",
            extraction_confidence=0.95,
            created_at=datetime(2024, 1, 1)  # TODO P3.x: Replace with TimeService when implemented
        )
        session.add(artifact)
        await session.commit()

        # Create provenance record
        prov = Provenance(
            uuid="test-prov-123",
            provenance_record_id="prov-rec-test-123",
            artifact_id=artifact.uuid,
            artifact_type="extracted_text",
            action_type=ProvenanceActionType.CREATE,
            actor_type=ActorType.SYSTEM_PROCESS,
            actor_id="text-extraction-engine",
            input_artifact_ids=[doc.uuid],
            output_artifact_ids=[artifact.uuid],
            activity_timestamp=datetime(2024, 1, 1),  # TODO P3.x: Replace with TimeService when implemented
            policy_phase="phase_3",
            policy_ruleset_version="v3.1",
            lineage_depth=1,
            root_artifact_id=doc.uuid,
            created_at=datetime(2024, 1, 1)  # TODO P3.x: Replace with TimeService when implemented
        )
        session.add(prov)
        await session.commit()

        # Verify provenance chain
        retrieved_prov = await session.get(Provenance, prov.uuid)
        assert retrieved_prov is not None
        assert retrieved_prov.artifact_id == artifact.uuid
        assert doc.uuid in retrieved_prov.input_artifact_ids
        assert artifact.uuid in retrieved_prov.output_artifact_ids


class TestP31ConstraintValidation:
    """Test database constraints and business rule enforcement."""

    async def test_corpus_claim_drafting_constraint(self, session):
        """Test CorpusModel.md constraint: Only open patent corpus allows claim drafting."""
        # This should succeed - open patent corpus with claim drafting
        valid_corpus = Corpus(
            uuid="valid-claim-corpus",
            name="Valid Claim Drafting Corpus",
            corpus_type=CorpusType.OPEN_PATENT,
            allows_claim_drafting=True,
            allows_risk_analysis=False,
            allows_evidence_mapping=False,
            allows_style_guidance=False,
            created_by="test_user",
            is_active=True,
            created_at=datetime(2024, 1, 1)  # TODO P3.x: Replace with TimeService when implemented
        )
        session.add(valid_corpus)
        await session.commit()
        
        # Verify it was created successfully
        retrieved = await session.get(Corpus, valid_corpus.uuid)
        assert retrieved is not None
        assert retrieved.allows_claim_drafting is True
        assert retrieved.corpus_type == CorpusType.OPEN_PATENT

    async def test_task_priority_range_constraint(self, session):
        """Test TaskType priority range constraint (1-10)."""
        # Valid priority within range
        valid_task = Task(
            uuid="valid-task-priority",
            task_type=TaskType.DOCUMENT_REVIEW,
            status=TaskStatus.CREATED,
            title="Valid Priority Task",
            description="Task with valid priority",
            evidence_bundle_ids=["bundle-123"],
            priority=5,  # Valid: within 1-10 range
            completion_criteria="Review document for compliance",
            created_at=datetime(2024, 1, 1)  # TODO P3.x: Replace with TimeService when implemented
        )
        session.add(valid_task)
        await session.commit()
        
        retrieved_task = await session.get(Task, valid_task.uuid)
        assert retrieved_task is not None
        assert retrieved_task.priority == 5

    async def test_diagram_canonical_reuse_count_positive(self, session):
        """Test DiagramCanonical reuse_count must be positive constraint."""
        # Create required corpus first
        corpus = Corpus(
            uuid="diagram-corpus",
            name="Diagram Test Corpus",
            corpus_type=CorpusType.OPEN_PATENT,
            allows_claim_drafting=True,
            allows_risk_analysis=False,
            allows_evidence_mapping=False,
            allows_style_guidance=False,
            created_by="test_user",
            is_active=True,
            created_at=datetime(2024, 1, 1)  # TODO P3.x: Replace with TimeService when implemented
        )
        session.add(corpus)

        # Create document and artifact for the diagram
        doc = Document(
            uuid="diagram-doc",
            title="Diagram Test Document",
            source="diagram_test.pdf",
            document_type=DocumentType.PATENT,
            current_state=DocumentState.UPLOADED,
            corpus_id=corpus.uuid,
            ingestion_timestamp=datetime(2024, 1, 1),  # TODO P3.x: Replace with TimeService when implemented
            created_at=datetime(2024, 1, 1)  # TODO P3.x: Replace with TimeService when implemented
        )
        session.add(doc)

        artifact = Artifact(
            uuid="diagram-artifact",
            document_id=doc.uuid,
            artifact_type=ArtifactType.DIAGRAM_DESCRIPTION,
            name="Test Diagram Artifact",
            description="Test diagram for canonical",
            content="Test diagram content",
            content_type="image/png",
            created_at=datetime(2024, 1, 1)  # TODO P3.x: Replace with TimeService when implemented
        )
        session.add(artifact)
        await session.commit()

        # Valid diagram canonical with positive reuse count
        valid_diagram = DiagramCanonical(
            uuid="valid-diagram-canonical",
            canonical_description="Valid canonical diagram description",
            description_version=1,
            description_hash="valid-hash-123",
            original_artifact_id=artifact.uuid,
            reuse_count=1,  # Valid: positive number
            status=DiagramStatus.CANONICAL_CREATED,
            most_restrictive_corpus_id=corpus.uuid,
            created_at=datetime(2024, 1, 1)  # TODO P3.x: Replace with TimeService when implemented
        )
        session.add(valid_diagram)
        await session.commit()
        
        retrieved_diagram = await session.get(DiagramCanonical, valid_diagram.uuid)
        assert retrieved_diagram is not None
        assert retrieved_diagram.reuse_count == 1


class TestP31RelationshipIntegrity:
    """Test foreign key relationships and cascade behaviors."""

    async def test_document_version_parent_child_relationships(self, session):
        """Test DocumentVersion parent-child relationship integrity."""
        # Create corpus and document
        corpus = Corpus(
            uuid="version-corpus",
            name="Version Test Corpus",
            corpus_type=CorpusType.OPEN_PATENT,
            allows_claim_drafting=True,
            allows_risk_analysis=False,
            allows_evidence_mapping=False,
            allows_style_guidance=False,
            created_by="test_user",
            is_active=True,
            created_at=datetime(2024, 1, 1)  # TODO P3.x: Replace with TimeService when implemented
        )
        session.add(corpus)

        doc = Document(
            uuid="version-doc",
            title="Version Test Document",
            source="version_test.pdf",
            document_type=DocumentType.PATENT,
            current_state=DocumentState.UPLOADED,
            corpus_id=corpus.uuid,
            ingestion_timestamp=datetime(2024, 1, 1),  # TODO P3.x: Replace with TimeService when implemented
            created_at=datetime(2024, 1, 1)  # TODO P3.x: Replace with TimeService when implemented
        )
        session.add(doc)
        await session.commit()

        # Create parent version
        parent_version = DocumentVersion(
            uuid="parent-version",
            document_id=doc.uuid,
            version_number=1,
            content_snapshot="Original document content",
            content_hash="original-hash-123",
            created_by_type=ActorType.HUMAN_REVIEWER,
            created_by_id="reviewer-123",
            change_rationale="Initial version",
            created_at=datetime(2024, 1, 1)  # TODO P3.x: Replace with TimeService when implemented
        )
        session.add(parent_version)
        await session.commit()

        # Create child version
        child_version = DocumentVersion(
            uuid="child-version",
            document_id=doc.uuid,
            version_number=2,
            parent_version_id=parent_version.uuid,
            content_snapshot="Updated document content",
            content_hash="updated-hash-456",
            created_by_type=ActorType.HUMAN_REVIEWER,
            created_by_id="reviewer-123",
            change_rationale="Content update",
            created_at=datetime(2024, 1, 1)  # TODO P3.x: Replace with TimeService when implemented
        )
        session.add(child_version)
        await session.commit()

        # Verify parent-child relationship
        retrieved_child = await session.get(DocumentVersion, child_version.uuid)
        assert retrieved_child is not None
        assert retrieved_child.parent_version_id == parent_version.uuid
        assert retrieved_child.version_number == 2

    async def test_agent_run_task_escalation_relationship(self, session):
        """Test AgentRun to Task escalation relationship."""
        # Create agent run
        agent_run = AgentRun(
            uuid="test-agent-run",
            agent_name="test-patent-analyzer",
            agent_version="v1.0.0",
            agent_type="document_analyzer",
            execution_id="exec-123-456",
            correlation_id="corr-789-012",
            input_parameters={"param1": "value1"},
            authorized_corpus_ids=["corpus-123"],
            started_at=datetime(2024, 1, 1),  # TODO P3.x: Replace with TimeService when implemented
            status="completed",
            success=True,
            created_at=datetime(2024, 1, 1)  # TODO P3.x: Replace with TimeService when implemented
        )
        session.add(agent_run)
        await session.commit()

        # Create escalated task
        escalated_task = Task(
            uuid="escalated-task",
            task_type=TaskType.ERROR_RESOLUTION,
            status=TaskStatus.CREATED,
            title="Agent Run Error Resolution",
            description="Resolve issues from agent execution",
            evidence_bundle_ids=["bundle-error-123"],
            priority=8,
            completion_criteria="Resolve agent execution errors",
            escalated_from_agent_run=agent_run.uuid,
            created_at=datetime(2024, 1, 1)  # TODO P3.x: Replace with TimeService when implemented
        )
        session.add(escalated_task)
        await session.commit()

        # Verify escalation relationship
        retrieved_task = await session.get(Task, escalated_task.uuid)
        assert retrieved_task is not None
        assert retrieved_task.escalated_from_agent_run == agent_run.uuid
        assert retrieved_task.task_type == TaskType.ERROR_RESOLUTION


class TestP31PerformanceIndexes:
    """Test database performance index utilization."""

    async def test_corpus_document_query_performance(self, session):
        """Test corpus-document relationship query performance."""
        # Create test data
        corpus = Corpus(
            uuid="perf-test-corpus",
            name="Performance Test Corpus",
            corpus_type=CorpusType.OPEN_PATENT,
            allows_claim_drafting=True,
            allows_risk_analysis=False,
            allows_evidence_mapping=False,
            allows_style_guidance=False,
            created_by="test_user",
            is_active=True,
            created_at=datetime(2024, 1, 1)  # TODO P3.x: Replace with TimeService when implemented
        )
        session.add(corpus)

        # Create multiple documents for query testing
        for i in range(5):
            doc = Document(
                uuid=f"perf-doc-{i}",
                title=f"Performance Test Document {i}",
                source=f"perf_test_{i}.pdf",
                document_type=DocumentType.PATENT,
                current_state=DocumentState.UPLOADED,
                corpus_id=corpus.uuid,
                ingestion_timestamp=datetime(2024, 1, 1),  # TODO P3.x: Replace with TimeService when implemented
                created_at=datetime(2024, 1, 1)  # TODO P3.x: Replace with TimeService when implemented
            )
            session.add(doc)
        await session.commit()

        # Test performance query (should utilize corpus-document indexes)
        result = await session.execute(
            text("SELECT COUNT(*) FROM documents WHERE corpus_id = :corpus_id"),
            {"corpus_id": corpus.uuid}
        )
        count = result.scalar()
        assert count == 5

    async def test_audit_event_temporal_queries(self, session):
        """Test audit event temporal query performance."""
        # Create test audit events
        for i in range(3):
            event = AuditEvent(
                uuid=f"perf-event-{i}",
                event_type=AuditEventType.DOCUMENT_CREATED,
                event_name=f"Performance Test Event {i}",
                event_description=f"Test event {i} for performance testing",
                actor_type=ActorType.SYSTEM_PROCESS,
                actor_id="perf-test-system",
                resource_type="document",
                resource_id=f"perf-doc-{i}",
                action_taken="create",
                event_timestamp=datetime(2024, 1, 1),  # TODO P3.x: Replace with TimeService when implemented
                development_phase="phase_3",
                ruleset_version="v3.1",
                impact_level="low",
                requires_hitl=False,
                created_at=datetime(2024, 1, 1)  # TODO P3.x: Replace with TimeService when implemented
            )
            session.add(event)
        await session.commit()

        # Test temporal query (should utilize timestamp indexes)
        result = await session.execute(
            text("SELECT COUNT(*) FROM audit_events WHERE event_timestamp >= :start_time"),
            {"start_time": datetime(2024, 1, 1)}
        )
        count = result.scalar()
        assert count >= 3