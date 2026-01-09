# Current Corpus Workflow - Functional Description

**Status**: CURRENT IMPLEMENTATION ANALYSIS - Phase 3.2A Complete, P3.2B In Progress  
**Authority**: Describes existing system architecture and workflows  
**Cross-References**: [PipelineStateMachine.md](../../PipelineStateMachine.md), [SystemNarrative.md](../../SystemNarrative.md), [DataFlowDiagram.md](../../DataFlowDiagram.md)

## Executive Summary

This document describes the current corpus workflow implementation based on completed Phase 3.2A infrastructure and planned P3.2B document lifecycle management. The system processes patent documents through a structured pipeline from ingestion to vector indexing, with basic OCR processing and human-in-the-loop validation.

## Functional Workflow Overview

### Document Ingestion to Corpus Assignment

```
Document Upload (Manual/Research Agent)
    ↓
Document Registration → PostgreSQL (documents table)
    ↓
Format Detection & Normalization 
    ↓
Text Extraction → Normalized Text Storage
    ↓
Image Extraction → Image Registry
    ↓
Document Classification → Corpus Assignment
    ↓
OCR Processing → Image Text Extraction
    ↓
Vector Generation → Corpus-Segregated Vector Storage
    ↓
Document State: READY → Available for Agent Analysis
```

## Current Processing Phases

### Phase 1: Document Registration
**Input**: PDF, XML, HTML files or manual upload
**Process**: 
- Document UUID generation using ID service
- Source tracking (manual_upload, research_agent)
- Initial document type detection (patent, prior_art, office_action, product_doc)
- Database record creation with metadata

**Database Operations**:
```sql
INSERT INTO documents (uuid, title, source, document_type, current_state, corpus_id, ingestion_timestamp)
VALUES (generated_uuid, extracted_title, source_file, detected_type, 'INGESTED', target_corpus, now())
```

### Phase 2: Content Normalization
**Input**: Raw document files
**Process**:
- PDF text extraction using PyPDF
- XML/HTML parsing and structure preservation  
- Character encoding normalization (UTF-8)
- Metadata extraction (title, dates, references)

**State Transition**: `INGESTED → NORMALIZED → TEXT_EXTRACTED`

### Phase 3: Image Processing Pipeline
**Input**: Embedded images from documents
**Process**:
- Image extraction to separate storage
- Perceptual hash generation for duplicate detection
- Image metadata tracking (dimensions, format, source page)
- Initial classification (technical vs decorative)

**Database Operations**:
```sql
INSERT INTO images (id, document_id, image_path, perceptual_hash, extracted_at, metadata)
VALUES (image_id, parent_doc_id, storage_path, hash_value, timestamp, json_metadata)
```

### Phase 4: OCR Text Extraction
**Input**: Extracted images
**Process**:
- Tesseract OCR processing
- Confidence score assessment
- Low-confidence flagging for HITL review
- Text storage linked to image records

**Current Limitations**:
- Single OCR engine (Tesseract only)
- Basic confidence scoring without context
- No document-image correlation
- Generic OCR without patent-specific optimization

### Phase 5: Corpus Classification & Assignment
**Input**: Processed documents with extracted content
**Process**:
- Document type classification using classification agent
- Corpus assignment based on CorpusModel.md rules
- Isolation enforcement (document assigned to single corpus)
- Access control setup for corpus boundaries

**Corpus Types**:
- **Open Patent Corpus**: Source specifications for claim generation
- **Adversarial Corpus**: Prior art and OA/IPR materials
- **Product Corpus**: Target product evidence
- **Guidance Corpus**: Treatises, case law, USPTO guidance (optional)

### Phase 6: Vector Indexing & Embedding
**Input**: Normalized text + OCR results
**Process**:
- Text chunking for optimal retrieval
- Vector embedding generation using sentence-transformers
- Corpus-segregated vector storage
- Search index creation with metadata tagging

**Vector Isolation**: Each corpus maintains separate vector indices to prevent cross-corpus contamination

## Image-Document Relationships

### Current Linking Structure

```
Document (documents table)
    ↓ (one-to-many)
Images (images table)
    ↓ (one-to-many) 
OCR Results (stored in images metadata)
    ↓ (contributes to)
Vector Embeddings (corpus-specific indices)
```

### Image Processing Workflow

```
PDF Document → Image Extraction → Image Registry
    ↓
Individual Images → OCR Processing → Text Results
    ↓
Text + Image Metadata → Chunking → Vector Chunks
    ↓
Vector Chunks → Embedding Generation → Corpus Vector Index
```

### Current Vector Database Integration

**Vector Storage Pattern**:
- Separate vector indices per corpus (isolation enforcement)
- Document chunks include image-derived text
- Image descriptions stored as text chunks with image_id references
- Cross-references between document text and image content through chunk metadata

## RDBMS Table Structure (Current Implementation)

### Entity Relationship Diagram (Current System)

```
┌─────────────────┐     ┌─────────────────┐
│     corpus      │     │   documents     │
├─────────────────┤     ├─────────────────┤
│ id (PK)         │◄────│ corpus_id (FK)  │
│ name            │  │  │ uuid (PK)       │
│ description     │  │  │ title           │
│ corpus_type     │  │  │ source          │
│ isolation_level │  │  │ document_type   │
│ created_at      │  │  │ current_state   │
│ updated_at      │  │  │ document_hash   │
└─────────────────┘  │  │ ingestion_time  │
                     │  │ processing_*    │
                     │  │ error_count     │
                     │  │ created_at      │
                     │  │ updated_at      │
                     │  └─────────────────┘
                     │           │
                     │           │ 1:N
                     │           ▼
                     │  ┌─────────────────┐
                     │  │     images      │
                     │  ├─────────────────┤
                     │  │ id (PK)         │
                     │  │ document_id(FK) │
                     │  │ image_path      │
                     │  │ original_file   │
                     │  │ file_size_bytes │
                     │  │ image_format    │
                     │  │ dimensions      │
                     │  │ perceptual_hash │
                     │  │ extracted_at    │
                     │  │ processing_state│
                     │  │ metadata (JSONB)│
                     │  └─────────────────┘
                     │
                     │ 1:N
                     ▼
            ┌─────────────────┐     ┌─────────────────┐
            │    artifacts    │     │document_versions│
            ├─────────────────┤     ├─────────────────┤
            │ id (PK)         │     │ id (PK)         │
            │ document_id(FK) │     │ document_id(FK) │
            │ artifact_type   │     │ version_number  │
            │ name            │     │ content         │
            │ content         │     │ metadata (JSONB)│
            │ binary_data     │     │ created_at      │
            │ metadata (JSONB)│     │ created_by      │
            │ created_at      │     └─────────────────┘
            └─────────────────┘

                                    ┌─────────────────┐
                                    │provenance_records│
                                    ├─────────────────┤
                                    │ id (PK)         │
                                    │ source_art_id   │
                                    │ derived_art_id  │
                                    │ transform_type  │
                                    │ transform_detail│
                                    │ processing_agent│
│ timestamp       │     │ confidence_score│
└─────────────────┘     │ created_at      │
                        └─────────────────┘
```

### Core Document Management

```sql
-- Primary document storage
CREATE TABLE documents (
    uuid UUID PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    source VARCHAR(500) NOT NULL,
    document_type document_type_enum NOT NULL,
    current_state document_state_enum NOT NULL,
    corpus_id UUID REFERENCES corpus(id),
    document_hash VARCHAR(64),
    ingestion_timestamp TIMESTAMP NOT NULL,
    processing_started_at TIMESTAMP,
    processing_completed_at TIMESTAMP,
    error_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Corpus management with isolation
CREATE TABLE corpus (
    id UUID PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    corpus_type corpus_type_enum NOT NULL,
    isolation_level isolation_level_enum DEFAULT 'STRICT',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Image and Asset Management

```sql
-- Image registry with document linking
CREATE TABLE images (
    id UUID PRIMARY KEY,
    document_id UUID REFERENCES documents(uuid) ON DELETE CASCADE,
    image_path VARCHAR(500) NOT NULL,
    original_filename VARCHAR(255),
    file_size_bytes BIGINT,
    image_format VARCHAR(10),
    dimensions JSONB, -- {"width": 800, "height": 600}
    perceptual_hash VARCHAR(32),
    extracted_at TIMESTAMP DEFAULT NOW(),
    processing_state image_state_enum DEFAULT 'EXTRACTED',
    metadata JSONB -- OCR results, classification data
);

-- Document artifacts (text extractions, etc.)
CREATE TABLE artifacts (
    id UUID PRIMARY KEY,
    document_id UUID REFERENCES documents(uuid) ON DELETE CASCADE,
    artifact_type artifact_type_enum NOT NULL,
    name VARCHAR(255) NOT NULL,
    content TEXT,
    binary_data BYTEA,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Pipeline State Management

```sql
-- Document versioning for REPROCESSING state
CREATE TABLE document_versions (
    id UUID PRIMARY KEY,
    document_id UUID REFERENCES documents(uuid) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(100)
);

### Provenance and Lineage Tracking

```sql
-- Complete processing provenance
CREATE TABLE provenance_records (
    id UUID PRIMARY KEY,
    source_artifact_id UUID NOT NULL,
    derived_artifact_id UUID NOT NULL,
    transformation_type VARCHAR(100) NOT NULL,
    transformation_details JSONB,
    processing_agent VARCHAR(100) NOT NULL,
    confidence_score FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Data Flow and Processing Steps

### Document Processing Data Flow

```
┌─────────────────┐
│ Document Upload │
│ (PDF/XML/HTML)  │
└─────────┬───────┘
          ▼
┌─────────────────┐    ┌─────────────────┐
│   Registration  │    │    File Store   │
│   (documents)   │    │  (originals)    │
└─────────┬───────┘    └─────────────────┘
          ▼
┌─────────────────┐
│  Normalization  │
│   (text ext.)   │
└─────────┬───────┘
          ▼
┌─────────────────┐    ┌─────────────────┐
│ Image Extraction│    │  Image Registry │
│   (images)      │────│   (images)      │
└─────────┬───────┘    └─────────────────┘
          ▼
┌─────────────────┐
│  OCR Processing │
│  (Tesseract)    │
└─────────┬───────┘
          ▼
┌─────────────────┐
│ Classification  │
│ (corpus assign) │
└─────────┬───────┘
          ▼
┌─────────────────┐    ┌─────────────────┐
│   Text Chunking │    │ Vector Database │
│   (embedding)   │────│ (corpus-segr.)  │
└─────────────────┘    └─────────────────┘
```

### Vector Generation Process

```
Document Text + Image OCR Results
    ↓
Content Chunking (semantic segments)
    ↓
Embedding Generation (sentence-transformers)
    ↓
Corpus-Specific Storage
    ↓
Search Index Creation
    ↓
Available for RAG Retrieval
```

### Current Processing Coordination

**Resource Management** (Phase 3.2A Complete):
- GPU slot allocation for processing
- OCR slot management (max 10 concurrent)
- Document timeout handling (24-hour limit)
- Priority-based processing queue

**Completion Calculation** (Phase 3.2A Complete):
- Image processing completion tracking
- Document state progression monitoring  
- Threshold-based state transitions (70% partial, 90% ready)
- HITL task generation for blocked items

## Current System Limitations

### OCR and Image Processing
- **Single OCR Engine**: Only Tesseract, no fallback options
- **Generic Processing**: No patent-specific optimization or context
- **Basic Confidence**: Simple confidence scores without document correlation
- **Limited Description Quality**: OCR text extraction only, no semantic understanding

### Document Structure Understanding  
- **Flat Text Processing**: Documents treated as undifferentiated text
- **No Section Awareness**: Abstract, claims, specifications processed identically
- **Limited Metadata**: Basic bibliographic data extraction
- **Generic Chunking**: No section-specific chunking strategies

### Vector Database Management
- **Basic Deletion**: Simple cascade deletes without recovery options
- **No Cleanup Strategy**: Removed documents leave stale vectors
- **Limited Lifecycle**: No soft delete options for vector data
- **Recovery Gaps**: Accidental deletions difficult to restore

## System Performance Characteristics

### Processing Throughput (Current)
- **Document Ingestion**: 5-10 documents/hour (dependent on size)
- **Image Processing**: 2-5 images/minute (OCR-limited)  
- **Vector Generation**: 100-200 chunks/minute
- **Search Query Response**: <500ms for typical queries

### Resource Utilization
- **GPU Usage**: Minimal (embeddings only)
- **OCR Processing**: CPU-intensive, queue-managed
- **Database Operations**: Standard PostgreSQL performance
- **Storage**: Linear growth with document corpus size

### Quality Metrics
- **OCR Accuracy**: Variable (60-95% depending on image quality)
- **Classification Accuracy**: Manual validation required
- **Vector Relevance**: Dependent on chunk quality and size
- **Processing Reliability**: >95% success rate for standard documents

## Integration Points

### Agent Framework Integration
Current pipeline outputs feed directly into agent processing:
- **Document Classification Agent**: Uses processed metadata
- **Prior Art Analysis Agent**: Accesses adversarial corpus vectors
- **Claim Drafting Agent**: Retrieves from open patent corpus
- **Product Mapping Agent**: Searches product corpus

### HITL Task Generation
Automated task creation for:
- Low-confidence OCR results requiring human verification
- Duplicate image detection requiring human judgment  
- Complex technical diagrams needing description validation
- Document classification uncertainties

### Standards.md Compliance
All processing follows established patterns:
- Common services usage (Time, ID, Logging services)
- Configuration management through BaseSettings
- Structured API responses with request tracking
- Comprehensive audit logging and provenance capture

---

**Status**: This represents the current system as implemented in Phase 3.2A with P3.2B document lifecycle management in progress. The system provides a solid foundation for patent document processing with basic intelligence capabilities and comprehensive audit trails.