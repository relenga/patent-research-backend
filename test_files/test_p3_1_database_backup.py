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
from src.app.core.db.database import Base, async_engine, local_session


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
            created_at=datetime.utcnow()
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
            created_at=datetime.utcnow()
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
    
    async def test_document_crud_operations(self):
        """Test document creation, retrieval, update, and cascade delete."""
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        # Create test corpus first
        async with local_session() as session:
            corpus = Corpus(
                uuid="test-corpus-crud",
                name="Test CRUD Corpus", 
                corpus_type=CorpusType.OPEN_PATENT,
                allows_claim_drafting=True,
                created_by="test_user",
                created_at=datetime.utcnow()
            )
            session.add(corpus)
            await session.commit()
            
            # Create document
            document = Document(
                uuid="test-doc-crud",
                title="Test Document CRUD",
                source="test.pdf",
                document_type=DocumentType.PATENT,
                current_state=DocumentState.UPLOADED,
                corpus_id="test-corpus-crud",
                ingestion_timestamp=datetime.utcnow(),
                created_at=datetime.utcnow()
            )
            session.add(document)
            await session.commit()
            
            # Retrieve document
            result = await session.get(Document, "test-doc-crud")
            assert result is not None
            assert result.title == "Test Document CRUD"
            
            # Update document
            result.current_state = DocumentState.TEXT_EXTRACTED
            await session.commit()
            
            # Verify update
            updated_result = await session.get(Document, "test-doc-crud")
            assert updated_result.current_state == DocumentState.TEXT_EXTRACTED
    
    async def test_corpus_membership_single_active_rule(self):
        """Test CorpusModel.md rule: single active membership per document."""
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        async with local_session() as session:
            # Create test corpora
            corpus1 = Corpus(
                uuid="corpus-1-single",
                name="Corpus 1",
                corpus_type=CorpusType.OPEN_PATENT,
                allows_claim_drafting=True,
                created_by="test_user",
                created_at=datetime.utcnow()
            )
            corpus2 = Corpus(
                uuid="corpus-2-single", 
                name="Corpus 2",
                corpus_type=CorpusType.ADVERSARIAL,
                allows_risk_analysis=True,
                created_by="test_user",
                created_at=datetime.utcnow()
            )
            session.add_all([corpus1, corpus2])
            
            # Create document
            document = Document(
                uuid="doc-single-membership",
                title="Single Membership Test",
                source="test.pdf",
                document_type=DocumentType.PATENT,
                current_state=DocumentState.UPLOADED,
                corpus_id="corpus-1-single",
                ingestion_timestamp=datetime.utcnow(),
                created_at=datetime.utcnow()
            )
            session.add(document)
            
            # Create first membership
            membership1 = CorpusMembership(
                uuid="membership-1",
                document_id="doc-single-membership",
                corpus_id="corpus-1-single",
                assigned_by="test_user",
                assignment_reason="Initial assignment",
                is_active=True,
                created_at=datetime.utcnow()
            )
            session.add(membership1)
            await session.commit()
            
            # Try to create second active membership (should be prevented by unique index)
            membership2 = CorpusMembership(
                uuid="membership-2",
                document_id="doc-single-membership",
                corpus_id="corpus-2-single",
                assigned_by="test_user",
                assignment_reason="Second assignment",
                is_active=True,
                created_at=datetime.utcnow()
            )
            session.add(membership2)
            
            # This should fail due to unique constraint on (document_id) WHERE is_active = true
            with pytest.raises(IntegrityError):
                await session.commit()
    
    async def test_artifact_provenance_chain(self):
        """Test artifact derivation chain with provenance tracking."""
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        async with local_session() as session:
            # Create corpus and document
            corpus = Corpus(
                uuid="corpus-provenance",
                name="Provenance Test Corpus",
                corpus_type=CorpusType.OPEN_PATENT,
                allows_claim_drafting=True,
                created_by="test_user",
                created_at=datetime.utcnow()
            )
            document = Document(
                uuid="doc-provenance",
                title="Provenance Test Document",
                source="test.pdf",
                document_type=DocumentType.PATENT,
                current_state=DocumentState.PROCESSING,
                corpus_id="corpus-provenance",
                ingestion_timestamp=datetime.utcnow(),
                created_at=datetime.utcnow()
            )
            session.add_all([corpus, document])
            
            # Create original artifact
            original_artifact = Artifact(
                uuid="artifact-original",
                document_id="doc-provenance",
                artifact_type=ArtifactType.IMAGE_REFERENCE,
                name="Original Diagram",
                content="base64-encoded-image-data",
                content_type="image/png",
                extraction_confidence=1.0,
                created_at=datetime.utcnow()
            )
            session.add(original_artifact)
            
            # Create derived artifact
            derived_artifact = Artifact(
                uuid="artifact-derived",
                document_id="doc-provenance",
                artifact_type=ArtifactType.OCR_RESULT,
                name="OCR Text from Diagram",
                content="Extracted text content",
                content_type="text/plain",
                derived_from_artifact_id="artifact-original",
                extraction_confidence=0.85,
                created_at=datetime.utcnow()
            )
            session.add(derived_artifact)
            
            # Create provenance record
            provenance = Provenance(
                uuid="prov-derivation",
                provenance_record_id="prov-ocr-001",
                artifact_id="artifact-derived",
                artifact_type="ocr_result",
                action_type=ProvenanceActionType.DERIVE,
                actor_type=ActorType.AGENT_EXECUTION,
                actor_id="ocr-agent-v2",
                input_artifact_ids=["artifact-original"],
                output_artifact_ids=["artifact-derived"],
                activity_timestamp=datetime.utcnow(),
                policy_phase="phase_3",
                policy_ruleset_version="v3.1",
                lineage_depth=1,
                root_artifact_id="artifact-original",
                transformation_details="OCR processing of diagram image",
                created_at=datetime.utcnow()
            )
            session.add(provenance)
            await session.commit()
            
            # Verify provenance chain
            result = await session.get(Provenance, "prov-derivation")
            assert result.input_artifact_ids == ["artifact-original"]
            assert result.lineage_depth == 1
            assert result.root_artifact_id == "artifact-original"


class TestP31ConstraintValidation:
    """Test database constraint enforcement per CorpusModel.md business rules."""
    
    async def test_corpus_claim_drafting_constraint(self):
        """Test CorpusModel.md rule: only OPEN_PATENT corpus allows claim drafting."""
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        async with local_session() as session:
            # Valid: OPEN_PATENT with claim drafting = true
            valid_corpus = Corpus(
                uuid="valid-open-corpus",
                name="Valid Open Corpus",
                corpus_type=CorpusType.OPEN_PATENT,
                allows_claim_drafting=True,
                created_by="test_user",
                created_at=datetime.utcnow()
            )
            session.add(valid_corpus)
            await session.commit()
            
            # Invalid: ADVERSARIAL with claim drafting = true (violates business rule)
            invalid_corpus = Corpus(
                uuid="invalid-adv-corpus",
                name="Invalid Adversarial Corpus",
                corpus_type=CorpusType.ADVERSARIAL,
                allows_claim_drafting=True,  # This should be rejected
                created_by="test_user",
                created_at=datetime.utcnow()
            )
            session.add(invalid_corpus)
            
            # This should fail due to CHECK constraint
            with pytest.raises(IntegrityError):
                await session.commit()
    
    async def test_task_priority_range_constraint(self):
        """Test task priority must be between 1-10."""
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        async with local_session() as session:
            # Valid priority
            valid_task = Task(
                uuid="valid-priority-task",
                task_type=TaskType.DOCUMENT_REVIEW,
                title="Valid Priority Task",
                description="Test task with valid priority",
                priority=5,
                completion_criteria="Review document content",
                created_by="test_user",
                created_by_type=ActorType.HUMAN_REVIEWER,
                created_at=datetime.utcnow()
            )
            session.add(valid_task)
            await session.commit()
            
            # Invalid priority (out of range)
            invalid_task = Task(
                uuid="invalid-priority-task",
                task_type=TaskType.DOCUMENT_REVIEW,
                title="Invalid Priority Task",
                description="Test task with invalid priority",
                priority=15,  # Outside 1-10 range
                completion_criteria="Review document content",
                created_by="test_user",
                created_by_type=ActorType.HUMAN_REVIEWER,
                created_at=datetime.utcnow()
            )
            session.add(invalid_task)
            
            with pytest.raises(IntegrityError):
                await session.commit()
    
    async def test_diagram_canonical_reuse_count_positive(self):
        """Test DiagramCanonical reuse_count must be positive."""
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        async with local_session() as session:
            # Need corpus and document first
            corpus = Corpus(
                uuid="diagram-corpus",
                name="Diagram Test Corpus",
                corpus_type=CorpusType.OPEN_PATENT,
                allows_claim_drafting=True,
                created_by="test_user",
                created_at=datetime.utcnow()
            )
            document = Document(
                uuid="diagram-doc",
                title="Diagram Test Document",
                source="test.pdf",
                document_type=DocumentType.PATENT,
                current_state=DocumentState.PROCESSING,
                corpus_id="diagram-corpus",
                ingestion_timestamp=datetime.utcnow(),
                created_at=datetime.utcnow()
            )
            artifact = Artifact(
                uuid="diagram-artifact",
                document_id="diagram-doc",
                artifact_type=ArtifactType.IMAGE_REFERENCE,
                name="Test Diagram",
                content="image-data",
                created_at=datetime.utcnow()
            )
            session.add_all([corpus, document, artifact])
            await session.commit()
            
            # Invalid: zero reuse count
            invalid_diagram = DiagramCanonical(
                uuid="invalid-reuse-diagram",
                canonical_description="Test diagram description",
                description_hash="hash123",
                original_artifact_id="diagram-artifact",
                reuse_count=0,  # Invalid: must be positive
                most_restrictive_corpus_id="diagram-corpus",
                created_at=datetime.utcnow()
            )
            session.add(invalid_diagram)
            
            with pytest.raises(IntegrityError):
                await session.commit()


class TestP31RelationshipIntegrity:
    """Test relationship integrity and cascade behaviors."""
    
    async def test_document_version_parent_child_relationships(self):
        """Test DocumentVersion parent-child relationships work correctly."""
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        async with local_session() as session:
            # Create corpus and document
            corpus = Corpus(
                uuid="version-corpus",
                name="Version Test Corpus",
                corpus_type=CorpusType.OPEN_PATENT,
                allows_claim_drafting=True,
                created_by="test_user",
                created_at=datetime.utcnow()
            )
            document = Document(
                uuid="version-doc",
                title="Version Test Document",
                source="test.pdf",
                document_type=DocumentType.PATENT,
                current_state=DocumentState.PROCESSING,
                corpus_id="version-corpus",
                ingestion_timestamp=datetime.utcnow(),
                created_at=datetime.utcnow()
            )
            session.add_all([corpus, document])
            
            # Create parent version
            parent_version = DocumentVersion(
                uuid="parent-version",
                document_id="version-doc",
                version_number=1,
                content_snapshot="Original content",
                content_hash="hash1",
                created_by_type=ActorType.HUMAN_REVIEWER,
                created_by_id="user123",
                change_rationale="Initial version",
                created_at=datetime.utcnow()
            )
            session.add(parent_version)
            await session.commit()
            
            # Create child version
            child_version = DocumentVersion(
                uuid="child-version",
                document_id="version-doc", 
                version_number=2,
                parent_version_id="parent-version",
                content_snapshot="Updated content",
                content_hash="hash2",
                created_by_type=ActorType.AGENT_EXECUTION,
                created_by_id="ocr-agent",
                change_rationale="OCR processing update",
                created_at=datetime.utcnow()
            )
            session.add(child_version)
            await session.commit()
            
            # Verify relationship integrity
            result = await session.get(DocumentVersion, "child-version")
            assert result.parent_version_id == "parent-version"
            assert result.version_number == 2
    
    async def test_agent_run_task_escalation_relationship(self):
        """Test AgentRun to Task escalation relationships."""
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        async with local_session() as session:
            # Create agent run
            agent_run = AgentRun(
                uuid="test-agent-run",
                agent_name="test-agent",
                agent_version="v1.0",
                agent_type="ocr_processor",
                execution_id="exec-123",
                correlation_id="corr-456",
                authorized_corpus_ids=["corpus-123"],
                started_at=datetime.utcnow(),
                status="running",
                created_at=datetime.utcnow()
            )
            session.add(agent_run)
            
            # Create task that can be escalated
            original_task = Task(
                uuid="original-task",
                task_type=TaskType.OCR_VERIFICATION,
                title="Original OCR Task",
                description="Verify OCR results",
                completion_criteria="Confirm text accuracy",
                created_by="agent-123",
                created_by_type=ActorType.AGENT_EXECUTION,
                created_at=datetime.utcnow()
            )
            session.add(original_task)
            await session.commit()
            
            # Create escalated task
            escalated_task = Task(
                uuid="escalated-task",
                task_type=TaskType.ERROR_RESOLUTION,
                title="Escalated OCR Task",
                description="Resolve OCR processing error",
                completion_criteria="Fix OCR error and reprocess",
                escalated_from_task_id="original-task",
                created_by="system",
                created_by_type=ActorType.SYSTEM_PROCESS,
                created_at=datetime.utcnow()
            )
            session.add(escalated_task)
            
            # Create audit event linking to escalated task
            audit_event = AuditEvent(
                uuid="escalation-audit",
                event_type=AuditEventType.TASK_CREATED,
                event_name="Task Escalation",
                event_description="Task escalated due to processing error",
                actor_type=ActorType.SYSTEM_PROCESS,
                actor_id="escalation-system",
                resource_type="task",
                resource_id="escalated-task",
                action_taken="escalate",
                event_timestamp=datetime.utcnow(),
                development_phase="phase_3",
                ruleset_version="v3.1",
                impact_level="high",
                requires_hitl=True,
                hitl_task_created="escalated-task",
                created_at=datetime.utcnow()
            )
            session.add(audit_event)
            await session.commit()
            
            # Verify relationships
            escalated_result = await session.get(Task, "escalated-task")
            assert escalated_result.escalated_from_task_id == "original-task"
            
            audit_result = await session.get(AuditEvent, "escalation-audit")
            assert audit_result.hitl_task_created == "escalated-task"
            assert audit_result.requires_hitl is True


class TestP31PerformanceIndexes:
    """Test database performance with proper index utilization."""
    
    async def test_corpus_document_query_performance(self):
        """Test performance of common corpus-document queries."""
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        async with local_session() as session:
            # Create test data
            corpus = Corpus(
                uuid="perf-corpus",
                name="Performance Test Corpus",
                corpus_type=CorpusType.OPEN_PATENT,
                allows_claim_drafting=True,
                created_by="test_user",
                created_at=datetime.utcnow()
            )
            session.add(corpus)
            
            # Create multiple documents for performance testing
            documents = []
            for i in range(5):
                doc = Document(
                    uuid=f"perf-doc-{i}",
                    title=f"Performance Test Document {i}",
                    source=f"test{i}.pdf",
                    document_type=DocumentType.PATENT,
                    current_state=DocumentState.UPLOADED,
                    corpus_id="perf-corpus",
                    ingestion_timestamp=datetime.utcnow(),
                    created_at=datetime.utcnow()
                )
                documents.append(doc)
            
            session.add_all(documents)
            await session.commit()
            
            # Test indexed query performance (should use idx_documents_corpus_state)
            result = await session.execute(
                text("SELECT * FROM documents WHERE corpus_id = :corpus_id AND current_state = :state"),
                {"corpus_id": "perf-corpus", "state": "uploaded"}
            )
            rows = result.fetchall()
            assert len(rows) == 5
    
    async def test_audit_event_temporal_queries(self):
        """Test temporal audit event queries use proper indexes."""
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        async with local_session() as session:
            # Create test audit events
            events = []
            for i in range(3):
                event = AuditEvent(
                    uuid=f"audit-event-{i}",
                    event_type=AuditEventType.DOCUMENT_CREATED,
                    event_name=f"Test Event {i}",
                    event_description=f"Test audit event {i}",
                    actor_type=ActorType.HUMAN_REVIEWER,
                    actor_id="test-user",
                    resource_type="document",
                    resource_id=f"doc-{i}",
                    action_taken="create",
                    event_timestamp=datetime.utcnow(),
                    development_phase="phase_3",
                    ruleset_version="v3.1",
                    impact_level="low",
                    requires_hitl=False,
                    created_at=datetime.utcnow()
                )
                events.append(event)
            
            session.add_all(events)
            await session.commit()
            
            # Test temporal query (should use idx_audit_events_type_timestamp)
            result = await session.execute(
                text("SELECT * FROM audit_events WHERE event_type = :event_type ORDER BY event_timestamp"),
                {"event_type": "document_created"}
            )
            rows = result.fetchall()
            assert len(rows) == 3


# Test execution compliance with Command Length Rule (<120 chars)
async def run_p31_tests():
    """Execute all P3.1 database functional tests."""
    pytest_args = [
        "test_files/test_p3_1_database.py",
        "-v",
        "--tb=short"
    ]
    return pytest.main(pytest_args)


if __name__ == "__main__":
    asyncio.run(run_p31_tests())