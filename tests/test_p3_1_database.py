"""
Functional tests for P3.1 Database Schema & Persistence Layer.

Tests all 10 database models following AgentRules.md Phase 3 requirements:
- Schema creation and table structure validation
- Model field types and constraints
- Database CRUD operations
- Business rule constraints from CorpusModel.md  
- Relationship functionality between models
- Litigation-grade provenance audit features per ProvenanceAudit.md

Follows existing test patterns from conftest.py and test_user.py.
"""

from datetime import datetime
from unittest.mock import Mock
from uuid import uuid4

import pytest
from sqlalchemy import text, inspect
from sqlalchemy.exc import IntegrityError
from faker import Faker

from src.app.core.db.database import Base
from src.app.models.database import (
    Document, DocumentVersion, Artifact, DiagramCanonical, 
    Corpus, CorpusMembership, AgentRun, Task, AuditEvent, Provenance,
    TaskStatus, AuditAction
)

fake = Faker()


class TestP31DatabaseSchema:
    """Test P3.1 database schema creation and structure."""
    
    def test_database_tables_creation(self, local_session):
        """Test that all P3.1 tables are created successfully."""
        # Create all tables
        Base.metadata.create_all(bind=local_session.bind)
        
        # Verify all tables exist
        inspector = inspect(local_session.bind)
        table_names = inspector.get_table_names()
        
        expected_tables = {
            'documents', 'document_versions', 'artifacts', 'diagram_canonicals',
            'corpus', 'corpus_memberships', 'agent_runs', 'tasks', 
            'audit_events', 'provenance'
        }
        
        for table in expected_tables:
            assert table in table_names, f"Table {table} not created"
    
    def test_table_columns_structure(self, local_session):
        """Test that tables have correct column structure per DatabaseSchemaSpec.md."""
        Base.metadata.create_all(bind=local_session.bind)
        inspector = inspect(local_session.bind)
        
        # Test Document table structure
        doc_columns = {col['name']: col for col in inspector.get_columns('documents')}
        assert 'id' in doc_columns
        assert 'uuid' in doc_columns  
        assert 'title' in doc_columns
        assert 'metadata_json' in doc_columns
        assert doc_columns['uuid']['type'].python_type == str
        assert doc_columns['title']['nullable'] is False
        
        # Test Corpus table structure
        corpus_columns = {col['name']: col for col in inspector.get_columns('corpus')}
        assert 'id' in corpus_columns
        assert 'uuid' in corpus_columns
        assert 'name' in corpus_columns
        assert 'description' in corpus_columns
        assert corpus_columns['name']['nullable'] is False
        
        # Test AgentRun table structure  
        agent_columns = {col['name']: col for col in inspector.get_columns('agent_runs')}
        assert 'id' in agent_columns
        assert 'uuid' in agent_columns
        assert 'corpus_id' in agent_columns
        assert 'configuration_json' in agent_columns
        
    def test_table_constraints(self, local_session):
        """Test that tables have proper constraints and indexes."""
        Base.metadata.create_all(bind=local_session.bind)
        inspector = inspect(local_session.bind)
        
        # Test unique constraints
        doc_constraints = inspector.get_unique_constraints('documents')
        uuid_constraint_exists = any('uuid' in uc['column_names'] for uc in doc_constraints)
        assert uuid_constraint_exists, "Document uuid unique constraint missing"
        
        # Test foreign key constraints
        corpus_membership_fks = inspector.get_foreign_keys('corpus_memberships')
        fk_columns = {fk['constrained_columns'][0] for fk in corpus_membership_fks}
        assert 'corpus_id' in fk_columns
        assert 'document_id' in fk_columns


class TestP31DatabaseModels:
    """Test P3.1 database model validation and field types."""
    
    def test_document_model_creation(self, local_session):
        """Test Document model creation and field validation."""
        Base.metadata.create_all(bind=local_session.bind)
        
        # Test Standards.md compliant field patterns
        document = Document(
            uuid=str(uuid4()),  # TODO P3.x: Replace with IDService.generate_uuid()
            title=fake.sentence(),
            content=fake.text(),
            file_path=fake.file_path(),
            # TODO P3.x: Replace with TimeService.utc_now()
            created_at=f"TimeService.utc_now()",
            updated_at=f"TimeService.utc_now()",
            metadata_json={"source": "test", "format": "pdf"}
        )
        
        local_session.add(document)
        local_session.commit()
        
        # Verify document was created
        retrieved = local_session.query(Document).filter_by(uuid=document.uuid).first()
        assert retrieved is not None
        assert retrieved.title == document.title
        assert retrieved.metadata_json["source"] == "test"
    
    def test_document_version_model(self, local_session):
        """Test DocumentVersion model and relationship to Document."""
        Base.metadata.create_all(bind=local_session.bind)
        
        # Create parent document first
        document = Document(
            uuid=str(uuid4()),
            title=fake.sentence(),
            content=fake.text(),
            created_at=f"TimeService.utc_now()",
            updated_at=f"TimeService.utc_now()"
        )
        local_session.add(document)
        local_session.flush()  # Get document.id
        
        # Create document version
        version = DocumentVersion(
            uuid=str(uuid4()),
            document_id=document.id,
            version_number=1,
            content_hash=fake.sha256(),
            created_at=f"TimeService.utc_now()"
        )
        
        local_session.add(version)
        local_session.commit()
        
        # Test relationship
        retrieved_doc = local_session.query(Document).filter_by(id=document.id).first()
        assert len(retrieved_doc.versions) == 1
        assert retrieved_doc.versions[0].version_number == 1
    
    def test_corpus_model_creation(self, local_session):
        """Test Corpus model creation per CorpusModel.md requirements."""
        Base.metadata.create_all(bind=local_session.bind)
        
        corpus = Corpus(
            uuid=str(uuid4()),
            name=fake.company(),
            description=fake.text(),
            configuration_json={"analysis_type": "patent", "domain": "AI"},
            created_at=f"TimeService.utc_now()",
            updated_at=f"TimeService.utc_now()"
        )
        
        local_session.add(corpus)
        local_session.commit()
        
        retrieved = local_session.query(Corpus).filter_by(uuid=corpus.uuid).first()
        assert retrieved is not None
        assert retrieved.name == corpus.name
        assert retrieved.configuration_json["domain"] == "AI"
    
    def test_agent_run_model(self, local_session):
        """Test AgentRun model with task relationships."""
        Base.metadata.create_all(bind=local_session.bind)
        
        # Create corpus first
        corpus = Corpus(
            uuid=str(uuid4()),
            name=fake.company(),
            description=fake.text(),
            created_at=f"TimeService.utc_now()",
            updated_at=f"TimeService.utc_now()"
        )
        local_session.add(corpus)
        local_session.flush()
        
        # Create agent run
        agent_run = AgentRun(
            uuid=str(uuid4()),
            corpus_id=corpus.id,
            configuration_json={"model": "claude-3", "temperature": 0.7},
            started_at=f"TimeService.utc_now()",
            status="running"
        )
        
        local_session.add(agent_run)
        local_session.commit()
        
        retrieved = local_session.query(AgentRun).filter_by(uuid=agent_run.uuid).first()
        assert retrieved is not None
        assert retrieved.corpus_id == corpus.id
        assert retrieved.configuration_json["model"] == "claude-3"


class TestP31DatabaseOperations:
    """Test CRUD operations for P3.1 database models."""
    
    def test_document_crud_operations(self, local_session):
        """Test Create, Read, Update, Delete operations for Document model."""
        Base.metadata.create_all(bind=local_session.bind)
        
        # CREATE
        document = Document(
            uuid=str(uuid4()),
            title="Test Document",
            content="Original content",
            created_at=f"TimeService.utc_now()",
            updated_at=f"TimeService.utc_now()"
        )
        local_session.add(document)
        local_session.commit()
        doc_id = document.id
        
        # READ
        retrieved = local_session.query(Document).filter_by(id=doc_id).first()
        assert retrieved.title == "Test Document"
        assert retrieved.content == "Original content"
        
        # UPDATE
        retrieved.content = "Updated content"
        retrieved.updated_at = f"TimeService.utc_now()"
        local_session.commit()
        
        updated = local_session.query(Document).filter_by(id=doc_id).first()
        assert updated.content == "Updated content"
        
        # DELETE
        local_session.delete(updated)
        local_session.commit()
        
        deleted = local_session.query(Document).filter_by(id=doc_id).first()
        assert deleted is None
    
    def test_corpus_membership_operations(self, local_session):
        """Test CorpusMembership model operations and relationships."""
        Base.metadata.create_all(bind=local_session.bind)
        
        # Create corpus and document
        corpus = Corpus(
            uuid=str(uuid4()),
            name="Test Corpus",
            description="Test description",
            created_at=f"TimeService.utc_now()",
            updated_at=f"TimeService.utc_now()"
        )
        
        document = Document(
            uuid=str(uuid4()),
            title="Test Document",
            content="Test content",
            created_at=f"TimeService.utc_now()",
            updated_at=f"TimeService.utc_now()"
        )
        
        local_session.add_all([corpus, document])
        local_session.flush()
        
        # Create membership
        membership = CorpusMembership(
            corpus_id=corpus.id,
            document_id=document.id,
            added_at=f"TimeService.utc_now()",
            metadata_json={"relevance_score": 0.95}
        )
        
        local_session.add(membership)
        local_session.commit()
        
        # Test relationship queries
        corpus_docs = local_session.query(Document).join(
            CorpusMembership).filter(
            CorpusMembership.corpus_id == corpus.id).all()
        
        assert len(corpus_docs) == 1
        assert corpus_docs[0].title == "Test Document"
    
    def test_task_status_operations(self, local_session):
        """Test Task model with status enum validation."""
        Base.metadata.create_all(bind=local_session.bind)
        
        # Create corpus and agent run first
        corpus = Corpus(
            uuid=str(uuid4()),
            name="Test Corpus",
            description="Test description",
            created_at=f"TimeService.utc_now()",
            updated_at=f"TimeService.utc_now()"
        )
        local_session.add(corpus)
        local_session.flush()
        
        agent_run = AgentRun(
            uuid=str(uuid4()),
            corpus_id=corpus.id,
            configuration_json={},
            started_at=f"TimeService.utc_now()",
            status="running"
        )
        local_session.add(agent_run)
        local_session.flush()
        
        # Create task with enum status
        task = Task(
            uuid=str(uuid4()),
            agent_run_id=agent_run.id,
            task_type="analysis",
            status=TaskStatus.PENDING,
            created_at=f"TimeService.utc_now()",
            parameters_json={"analysis_type": "patent_analysis"}
        )
        
        local_session.add(task)
        local_session.commit()
        
        retrieved = local_session.query(Task).filter_by(uuid=task.uuid).first()
        assert retrieved.status == TaskStatus.PENDING
        
        # Test status update
        retrieved.status = TaskStatus.RUNNING
        local_session.commit()
        
        updated = local_session.query(Task).filter_by(uuid=task.uuid).first()
        assert updated.status == TaskStatus.RUNNING


class TestP31DatabaseConstraints:
    """Test constraint validation and business rules from CorpusModel.md."""
    
    def test_unique_constraints(self, local_session):
        """Test unique constraint violations."""
        Base.metadata.create_all(bind=local_session.bind)
        
        uuid_val = str(uuid4())
        
        # Create first document
        doc1 = Document(
            uuid=uuid_val,
            title="First Document",
            content="Content 1",
            created_at=f"TimeService.utc_now()",
            updated_at=f"TimeService.utc_now()"
        )
        local_session.add(doc1)
        local_session.commit()
        
        # Try to create second document with same UUID
        doc2 = Document(
            uuid=uuid_val,  # Same UUID should violate unique constraint
            title="Second Document", 
            content="Content 2",
            created_at=f"TimeService.utc_now()",
            updated_at=f"TimeService.utc_now()"
        )
        local_session.add(doc2)
        
        with pytest.raises(IntegrityError):
            local_session.commit()
    
    def test_foreign_key_constraints(self, local_session):
        """Test foreign key constraint validation."""
        Base.metadata.create_all(bind=local_session.bind)
        
        # Try to create document version without valid document_id
        version = DocumentVersion(
            uuid=str(uuid4()),
            document_id=999999,  # Non-existent document_id
            version_number=1,
            content_hash=fake.sha256(),
            created_at=f"TimeService.utc_now()"
        )
        
        local_session.add(version)
        
        with pytest.raises(IntegrityError):
            local_session.commit()
    
    def test_not_null_constraints(self, local_session):
        """Test required field validation."""
        Base.metadata.create_all(bind=local_session.bind)
        
        # Try to create document without required title
        document = Document(
            uuid=str(uuid4()),
            # title=None,  # Required field missing
            content="Test content",
            created_at=f"TimeService.utc_now()",
            updated_at=f"TimeService.utc_now()"
        )
        
        local_session.add(document)
        
        with pytest.raises(IntegrityError):
            local_session.commit()
    
    def test_corpus_membership_unique_constraint(self, local_session):
        """Test CorpusMembership unique constraint per CorpusModel.md."""
        Base.metadata.create_all(bind=local_session.bind)
        
        # Create corpus and document
        corpus = Corpus(
            uuid=str(uuid4()),
            name="Test Corpus",
            description="Test description",
            created_at=f"TimeService.utc_now()",
            updated_at=f"TimeService.utc_now()"
        )
        
        document = Document(
            uuid=str(uuid4()),
            title="Test Document",
            content="Test content", 
            created_at=f"TimeService.utc_now()",
            updated_at=f"TimeService.utc_now()"
        )
        
        local_session.add_all([corpus, document])
        local_session.flush()
        
        # Create first membership
        membership1 = CorpusMembership(
            corpus_id=corpus.id,
            document_id=document.id,
            added_at=f"TimeService.utc_now()"
        )
        local_session.add(membership1)
        local_session.commit()
        
        # Try to create duplicate membership
        membership2 = CorpusMembership(
            corpus_id=corpus.id,
            document_id=document.id,
            added_at=f"TimeService.utc_now()"
        )
        local_session.add(membership2)
        
        with pytest.raises(IntegrityError):
            local_session.commit()


class TestP31AuditProvenance:
    """Test litigation-grade audit and provenance features per ProvenanceAudit.md."""
    
    def test_audit_event_creation(self, local_session):
        """Test AuditEvent model for compliance tracking."""
        Base.metadata.create_all(bind=local_session.bind)
        
        audit_event = AuditEvent(
            uuid=str(uuid4()),
            table_name="documents",
            record_id="1",
            action=AuditAction.CREATE,
            user_id="user123",
            changes_json={"title": "New Document", "content": "Initial content"},
            timestamp=f"TimeService.utc_now()"
        )
        
        local_session.add(audit_event)
        local_session.commit()
        
        retrieved = local_session.query(AuditEvent).filter_by(uuid=audit_event.uuid).first()
        assert retrieved is not None
        assert retrieved.action == AuditAction.CREATE
        assert retrieved.table_name == "documents"
        assert retrieved.changes_json["title"] == "New Document"
    
    def test_provenance_tracking(self, local_session):
        """Test Provenance model for litigation-grade traceability."""
        Base.metadata.create_all(bind=local_session.bind)
        
        # Create source document
        source_doc = Document(
            uuid=str(uuid4()),
            title="Source Document",
            content="Source content",
            created_at=f"TimeService.utc_now()",
            updated_at=f"TimeService.utc_now()"
        )
        
        # Create target artifact
        target_artifact = Artifact(
            uuid=str(uuid4()),
            name="Generated Artifact",
            artifact_type="analysis",
            file_path="/path/to/artifact",
            created_at=f"TimeService.utc_now()",
            metadata_json={"generated_from": "document_analysis"}
        )
        
        local_session.add_all([source_doc, target_artifact])
        local_session.flush()
        
        # Create provenance record
        provenance = Provenance(
            uuid=str(uuid4()),
            source_type="Document",
            source_id=source_doc.id,
            target_type="Artifact", 
            target_id=target_artifact.id,
            transformation_type="document_analysis",
            transformation_config={"model": "claude-3", "parameters": {"temperature": 0.7}},
            created_at=f"TimeService.utc_now()"
        )
        
        local_session.add(provenance)
        local_session.commit()
        
        # Verify provenance tracking
        retrieved = local_session.query(Provenance).filter_by(uuid=provenance.uuid).first()
        assert retrieved is not None
        assert retrieved.source_type == "Document"
        assert retrieved.target_type == "Artifact"
        assert retrieved.transformation_type == "document_analysis"
        assert retrieved.transformation_config["model"] == "claude-3"
    
    def test_audit_action_enum_validation(self, local_session):
        """Test AuditAction enum validation."""
        Base.metadata.create_all(bind=local_session.bind)
        
        # Test all valid enum values
        for action in [AuditAction.CREATE, AuditAction.UPDATE, AuditAction.DELETE]:
            audit_event = AuditEvent(
                uuid=str(uuid4()),
                table_name="test_table",
                record_id="123",
                action=action,
                user_id="user123", 
                changes_json={"field": "value"},
                timestamp=f"TimeService.utc_now()"
            )
            
            local_session.add(audit_event)
            local_session.commit()
            
            retrieved = local_session.query(AuditEvent).filter_by(uuid=audit_event.uuid).first()
            assert retrieved.action == action
            
            local_session.delete(retrieved)
            local_session.commit()


class TestP31RelationshipFunctionality:
    """Test SQLAlchemy relationships between P3.1 models."""
    
    def test_document_to_versions_relationship(self, local_session):
        """Test one-to-many relationship: Document -> DocumentVersion."""
        Base.metadata.create_all(bind=local_session.bind)
        
        # Create document
        document = Document(
            uuid=str(uuid4()),
            title="Test Document",
            content="Original content",
            created_at=f"TimeService.utc_now()",
            updated_at=f"TimeService.utc_now()"
        )
        local_session.add(document)
        local_session.flush()
        
        # Create multiple versions
        version1 = DocumentVersion(
            uuid=str(uuid4()),
            document_id=document.id,
            version_number=1,
            content_hash="hash1",
            created_at=f"TimeService.utc_now()"
        )
        
        version2 = DocumentVersion(
            uuid=str(uuid4()),
            document_id=document.id,
            version_number=2,
            content_hash="hash2",
            created_at=f"TimeService.utc_now()"
        )
        
        local_session.add_all([version1, version2])
        local_session.commit()
        
        # Test relationship navigation
        retrieved_doc = local_session.query(Document).filter_by(id=document.id).first()
        assert len(retrieved_doc.versions) == 2
        
        version_numbers = [v.version_number for v in retrieved_doc.versions]
        assert 1 in version_numbers
        assert 2 in version_numbers
    
    def test_corpus_to_documents_relationship(self, local_session):
        """Test many-to-many relationship: Corpus <-> Document via CorpusMembership."""
        Base.metadata.create_all(bind=local_session.bind)
        
        # Create corpus
        corpus = Corpus(
            uuid=str(uuid4()),
            name="Test Corpus",
            description="Test description",
            created_at=f"TimeService.utc_now()",
            updated_at=f"TimeService.utc_now()"
        )
        
        # Create documents  
        doc1 = Document(
            uuid=str(uuid4()),
            title="Document 1",
            content="Content 1",
            created_at=f"TimeService.utc_now()",
            updated_at=f"TimeService.utc_now()"
        )
        
        doc2 = Document(
            uuid=str(uuid4()),
            title="Document 2", 
            content="Content 2",
            created_at=f"TimeService.utc_now()",
            updated_at=f"TimeService.utc_now()"
        )
        
        local_session.add_all([corpus, doc1, doc2])
        local_session.flush()
        
        # Create memberships
        membership1 = CorpusMembership(
            corpus_id=corpus.id,
            document_id=doc1.id,
            added_at=f"TimeService.utc_now()"
        )
        
        membership2 = CorpusMembership(
            corpus_id=corpus.id,
            document_id=doc2.id,
            added_at=f"TimeService.utc_now()"
        )
        
        local_session.add_all([membership1, membership2])
        local_session.commit()
        
        # Test relationship queries through join
        corpus_documents = local_session.query(Document).join(
            CorpusMembership, Document.id == CorpusMembership.document_id
        ).filter(CorpusMembership.corpus_id == corpus.id).all()
        
        assert len(corpus_documents) == 2
        doc_titles = [d.title for d in corpus_documents]
        assert "Document 1" in doc_titles
        assert "Document 2" in doc_titles
    
    def test_agent_run_to_tasks_relationship(self, local_session):
        """Test one-to-many relationship: AgentRun -> Task."""
        Base.metadata.create_all(bind=local_session.bind)
        
        # Create corpus first
        corpus = Corpus(
            uuid=str(uuid4()),
            name="Test Corpus",
            description="Test description",
            created_at=f"TimeService.utc_now()",
            updated_at=f"TimeService.utc_now()"
        )
        local_session.add(corpus)
        local_session.flush()
        
        # Create agent run
        agent_run = AgentRun(
            uuid=str(uuid4()),
            corpus_id=corpus.id,
            configuration_json={"model": "claude-3"},
            started_at=f"TimeService.utc_now()",
            status="running"
        )
        local_session.add(agent_run)
        local_session.flush()
        
        # Create tasks
        task1 = Task(
            uuid=str(uuid4()),
            agent_run_id=agent_run.id,
            task_type="analysis",
            status=TaskStatus.PENDING,
            created_at=f"TimeService.utc_now()",
            parameters_json={"type": "patent_analysis"}
        )
        
        task2 = Task(
            uuid=str(uuid4()),
            agent_run_id=agent_run.id,
            task_type="generation",
            status=TaskStatus.PENDING,
            created_at=f"TimeService.utc_now()",
            parameters_json={"type": "diagram_generation"}
        )
        
        local_session.add_all([task1, task2])
        local_session.commit()
        
        # Test relationship navigation
        retrieved_run = local_session.query(AgentRun).filter_by(id=agent_run.id).first()
        assert len(retrieved_run.tasks) == 2
        
        task_types = [t.task_type for t in retrieved_run.tasks]
        assert "analysis" in task_types
        assert "generation" in task_types