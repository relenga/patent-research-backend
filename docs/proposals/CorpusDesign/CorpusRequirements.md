# Corpus Requirements and System Architecture

**Status**: COMPREHENSIVE REQUIREMENTS - Based on Design Analysis and Enhancement Discussions  
**Authority**: Technical requirements specification for patent document corpus management system  
**Cross-References**: [CurrentCorpusWorkFlow.md](./CurrentCorpusWorkFlow.md), [ProposedEnhancedCorpusWorkFlow.md](./ProposedEnhancedCorpusWorkFlow.md), [2026-01-06PipelineEnhancements.md](../2026-01-06PipelineEnhancements.md)

## Executive Summary

This document defines comprehensive requirements for a patent intelligence corpus management system, covering document ingestion, processing, storage, and lifecycle management. Requirements are categorized by priority to support strategic development planning and resource allocation decisions.

---

## Requirements Analysis

### Document Upload and Ingestion Requirements

#### **HARD Requirements (Essential)**
1. **Multiple Format Support**: PDF, XML, HTML document upload with format validation
2. **Source Attribution**: Track manual upload vs research agent acquisition with audit trails
3. **Document Registration**: UUID-based document identification with PostgreSQL persistence
4. **Duplicate Detection**: Content hash-based duplicate prevention with user override capability
5. **File Integrity**: Document hash verification and corruption detection during upload
6. **Error Handling**: Graceful upload failure handling with user notification and retry capability
7. **Storage Management**: Secure file storage with original document preservation
8. **Metadata Extraction**: Basic document metadata (title, dates, file properties) extraction

#### **NICE TO HAVE Requirements**
1. **Batch Upload**: Multiple document upload with progress tracking and batch status reporting
2. **Upload Validation**: Advanced format validation with detailed error reporting for unsupported formats
3. **Storage Optimization**: Document compression and storage optimization for large patent collections
4. **Upload Resume**: Interrupted upload resumption capability for large files

### Document Parsing and Structure Recognition Requirements

#### **HARD Requirements (Essential)**
1. **Text Extraction**: PDF text extraction using PyPDF with encoding normalization (UTF-8)
2. **Basic Structure Recognition**: Document type detection (patent, prior_art, office_action, product_doc)
3. **Content Normalization**: Whitespace normalization, paragraph boundaries, character cleaning
4. **Image Extraction**: Embedded image identification and extraction to separate storage
5. **Corpus Assignment**: Document classification and corpus assignment with isolation enforcement

#### **NICE TO HAVE Requirements**
1. **Section-Aware Parsing**: Patent document section detection (Abstract, Claims, Description) with JSON markup
2. **Hierarchical Structure**: Claim dependencies, subsection numbering, cross-reference resolution
3. **Bibliographic Extraction**: Structured patent metadata (numbers, inventors, assignees, dates) as JSON
4. **Classification Integration**: Patent classification codes (IPC, CPC, US) extraction and categorization
5. **Reference Resolution**: Figure references to text, claim references to specifications linking
6. **Technical Vocabulary**: Domain-specific term extraction and technical concept identification

### Image Processing and OCR Requirements

#### **HARD Requirements (Essential)**
1. **Image Registry**: Extracted images catalogued with document linkage and metadata tracking
2. **Basic OCR**: Tesseract OCR processing with confidence scoring and text extraction
3. **Duplicate Detection**: Perceptual hash-based image duplicate identification and flagging
4. **Processing State**: Image processing state tracking through pipeline stages
5. **Error Handling**: OCR failure handling with human-in-the-loop escalation for poor quality results
6. **Metadata Storage**: Image properties (dimensions, format, source page) with processing results

#### **NICE TO HAVE Requirements**
1. **Multimodal Analysis**: OCR + Vision analysis + Document context correlation for enhanced descriptions
2. **Multi-OCR Support**: Multiple OCR engines (Tesseract, Azure, Google) with fallback strategies
3. **Context Enhancement**: Document text correlation for improved OCR accuracy using reference numerals
4. **Iterative Refinement**: Quality-driven processing improvement loops with confidence-based triggers
5. **Vision Analysis**: PyTorch/OpenCV structural analysis for diagram understanding
6. **LLM Integration**: Multimodal description synthesis combining visual and textual information

### Vector Database and Embedding Requirements

#### **HARD Requirements (Essential)**
1. **Vector Generation**: Text chunking with sentence-transformers embedding generation
2. **Corpus Isolation**: Separate vector indices per corpus preventing cross-corpus contamination
3. **Metadata Tagging**: Vector chunks with document, image, and corpus metadata for retrieval
4. **Search Performance**: Sub-500ms query response times for typical patent searches
5. **Consistency**: Reliable vector-document synchronization with processing state coordination
6. **Storage Management**: Vector storage with performance indices and query optimization

#### **NICE TO HAVE Requirements**
1. **Section-Aware Vectors**: Section-specific vector generation with targeted retrieval capabilities
2. **Advanced Chunking**: Section-aware chunking strategies (claims vs specifications vs background)
3. **Quality Metrics**: Embedding confidence scoring and relevance assessment
4. **Hybrid Search**: Combined keyword and semantic search capabilities with ranking fusion
5. **Vector Lifecycle**: Comprehensive vector cleanup with recovery options for deleted documents
6. **Performance Optimization**: Advanced indexing and query optimization for large patent collections

### Document Lifecycle Management Requirements

#### **HARD Requirements (Essential)**
1. **State Tracking**: Document processing state progression through pipeline stages
2. **Version Control**: Document versioning for REPROCESSING state with audit trails
3. **Basic Deletion**: Document removal with cascade delete to dependent entities
4. **Processing Coordination**: Resource management with timeout handling and queue management
5. **Audit Logging**: Complete processing history with provenance tracking
6. **Recovery Mechanisms**: Error recovery and reprocessing capabilities for failed documents

#### **NICE TO HAVE Requirements**
1. **Three-Tier Deletion**: Soft delete with vector retention, soft delete with cleanup, hard delete options
2. **Restoration Capabilities**: Deleted document recovery with vector restoration for accidental deletions
3. **Batch Operations**: Bulk document management with progress tracking and status reporting
4. **Advanced Analytics**: Processing performance metrics and optimization insights
5. **Cleanup Automation**: Scheduled cleanup jobs with configurable retention policies
6. **Quality Assurance**: Stale vector detection and maintenance for data consistency

---

## Proposed System Architecture

### Standardized Audit Fields

All tables in the enhanced system follow consistent audit field conventions for data governance and compliance:

#### **Standard Audit Fields (All Tables)**
- `created_timestamp`: Datetime when record was created (NOT NULL, DEFAULT CURRENT_TIMESTAMP)
- `updated_timestamp`: Datetime when record was last modified (NULL allowed, updated via trigger)
- `created_by`: User/system identifier who created the record (VARCHAR, NOT NULL)
- `updated_by`: User/system identifier who last modified the record (VARCHAR, NULL allowed)

#### **Deletion Audit Fields (Where Applicable)**
- `marked_deleted`: Boolean flag for soft delete functionality (BOOLEAN, DEFAULT FALSE)
- `deleted_timestamp`: Datetime when record was marked for deletion (TIMESTAMP, NULL)
- `deleted_by`: User/system identifier who deleted the record (VARCHAR, NULL)
- `deletion_reason`: Categorized reason for deletion (ENUM, NULL)

#### **Document-Specific Upload Tracking**
- `uploaded_by`: Identifies upload source (ENUM: 'user', 'research_agent', 'system')
- `upload_source_info`: Additional upload metadata (JSONB, includes user_id, agent_id, upload_method, etc.)

#### **Processing-Specific Fields**
- `created_by` values for automated processes:
  - 'ocr_pipeline_tesseract': Tesseract OCR processing
  - 'vision_pipeline_pytorch': PyTorch vision analysis  
  - 'multimodal_llm_synthesis': LLM description generation
  - 'vector_cleanup_system': Automated vector cleanup
  - 'reprocessing_pipeline': Document reprocessing system
- `created_by` values for user actions:
  - User UUID for manual uploads/changes
  - 'research_agent_[id]' for agent-initiated actions

### Entity Relationship Diagram

```
┌─────────────────┐     ┌────────────────────────────────────────┐
│     corpus      │     │        documents (enhanced)           │
├─────────────────┤     ├────────────────────────────────────────┤
│ corpus_id (PK)  │◄────│ corpus_id (FK)                         │
│ name            │  │  │ document_uuid (PK)                     │
│ description     │  │  │ title, source, document_type           │
│ corpus_type     │  │  │ current_state, document_hash           │
│ isolation_level │  │  │ document_structure (JSONB) ← NEW       │
│ created_timestamp│ │  │ bibliographic_data (JSONB) ← NEW       │
│ updated_timestamp│ │  │ deletion_strategy ← NEW                │
│ created_by      │  │  │ vector_cleanup_status ← NEW            │
│ updated_by      │  │  │ ingestion_timestamp, processing_*      │
└─────────────────┘  │  │ error_count                            │
                     │  │ uploaded_by (user|research_agent) ← NEW│
                     │  │ upload_source_info (JSONB) ← NEW       │
                     │  │ created_timestamp, updated_timestamp ← AUDIT│
                     │  │ created_by, updated_by ← AUDIT         │
                     │  └────────────────────────────────────────┘
                     │           │
                     │           │ 1:N
                     │           ▼
                     │  ┌──────────────────────────────────────────┐
                     │  │         images (enhanced)                │
                     │  ├──────────────────────────────────────────┤
                     │  │ image_id (PK)                            │
                     │  │ document_uuid (FK)                       │
                     │  │ image_path, original_filename            │
                     │  │ file_size_bytes, image_format            │
                     │  │ dimensions, perceptual_hash              │
                     │  │ extracted_at, processing_state           │
                     │  │ vision_analysis_result (JSONB) ← NEW     │
                     │  │ document_context (JSONB) ← NEW           │
                     │  │ multimodal_description ← NEW             │
                     │  │ generation_confidence ← NEW              │
                     │  │ ocr_attempts, vision_attempts            │
                     │  │ human_validated, metadata                │
                     │  │ marked_deleted, deleted_timestamp ← DELETE│
                     │  │ deletion_reason, deleted_by ← DELETE     │
                     │  │ created_timestamp, updated_timestamp ← AUDIT│
                     │  │ created_by, updated_by ← AUDIT           │
                     │  └──────────────────────────────────────────┘
                     │           │ 1:N        │ 1:N
                     │           ▼            ▼
                     │  ┌─────────────────┐ ┌─────────────────┐
                     │  │image_ocr_results│ │image_vision_anal│
                     │  │← NEW TABLE      │ │← NEW TABLE      │
                     │  ├─────────────────┤ ├─────────────────┤
                     │  │ ocr_result_id(PK)│ │vision_analysis  │
                     │  │ image_id (FK)   │ │_id (PK)         │
                     │  │ ocr_engine      │ │ image_id (FK)   │
                     │  │ extracted_text  │ │ detected_objects│
                     │  │ confidence_score│ │ spatial_relations│
                     │  │ processing_time │ │ layout_class    │
                     │  │ created_timestamp│ │ analysis_conf   │
                     │  │ created_by      │ │ processing_model│
                     │  └─────────────────┘ │ created_timestamp│
                     │                      │ created_by      │
                     │                      └─────────────────┘
                     │
                     │ 1:N
                     ▼
            ┌─────────────────┐     ┌─────────────────┐
            │    artifacts    │     │document_versions│
            │  (enhanced)     │◄────│  (enhanced)     │
            ├─────────────────┤     ├─────────────────┤
            │ artifact_id(PK) │     │ version_id (PK) │
            │document_uuid(FK)│     │document_uuid(FK)│
            │ artifact_type   │     │ version_number  │
            │ name, content   │     │ content         │
            │ binary_data     │     │ metadata (JSONB)│
            │ metadata (JSONB)│     │ version_reason  │
            │ marked_deleted  │◄NEW │ marked_deleted  │◄NEW
            │ deleted_timestamp│←NEW │ deleted_timestamp│←NEW
            │ deletion_reason │←NEW │ deletion_reason │←NEW
            │ deleted_by      │←NEW │ deleted_by      │←NEW
            │ created_timestamp│    │ created_timestamp│
            │ created_by      │     │ created_by      │
            └─────────────────┘     │ updated_timestamp│
                                    │ updated_by      │
                                    └─────────────────┘

┌────────────── Vector Lifecycle Management ───────────────┐
│
▼
┌─────────────────┐     ┌─────────────────┐
│vector_cleanup   │     │vector_restoration│
│_audit ← NEW     │     │_cache ← NEW     │
├─────────────────┤     ├─────────────────┤
│cleanup_audit_id │     │restoration_cache│
│(PK)             │     │_id (PK)         │
│document_uuid(FK)│     │document_uuid(FK)│
│ cleanup_strategy│     │ cached_vectors  │
│ vectors_deleted │     │ cached_sections │
│ sections_affected│    │ cache_timestamp │
│ cleanup_time    │     │ expiry_timestamp│
│ cleanup_reason  │     │ restoration_cnt │
│ restoration_ok  │     │ created_timestamp│
│ audit_trail     │     │ created_by      │
│ created_timestamp│    │ updated_timestamp│
│ created_by      │     │ updated_by      │
└─────────────────┘     └─────────────────┘

                        ┌─────────────────┐
                        │provenance_records│
                        │  (enhanced)     │
                        ├─────────────────┤
                        │ provenance_     │
                        │ record_id (PK)  │
                        │ source_art_id   │
                        │ derived_art_id  │
                        │ transform_type  │
                        │ transform_detail│
                        │ processing_agent│
                        │ confidence_score│
└─────────────────┘     │ created_timestamp│
                        └─────────────────┘

┌──────────────── System Logging & Audit Tables ────────────────┐
│                                                               │
▼                                                               │
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  audit_events   │     │pipeline_event   │     │pipeline_override│
│  (existing)     │     │_logs (UPDATED)  │     │_audits (existing│
├─────────────────┤     ├─────────────────┤     ├─────────────────┤
│ audit_event_id  │◄────│ event_log_id    │  ┌──│ override_audit  │
│ (PK - uuid)     │  │  │ (PK)            │  │  │ _id (PK)        │
│ event_type      │  │  │ event_id (uuid) │  │  │ override_id     │
│ event_name      │  │  │ event_type      │  │  │ (uuid)          │
│ event_descript  │  │  │ priority        │  │  │ administrator_id│◄─┐
│ actor_type      │  │  │ source          │  │  │ (FK users)      │  │
│ actor_id        │  │  │ event_timestamp │◄FIX│ admin_role      │  │
│ actor_name      │  │  │ document_id     │  │  │ admin_ip        │  │
│ session_id      │  │  │ image_id        │  │  │ action          │  │
│ resource_type   │  │  │ batch_id        │  │  │ reason_category │  │
│ resource_id     │  │  │ user_id         │  │  │ justification   │  │
│ resource_name   │  │  │ payload (JSONB) │  │  │ requested_at    │  │
│ action_taken    │  │  │ delivered       │  │  │ executed_at     │  │
│ action_rationale│  │  │ delivery_attempt│  │  │ completed_at    │  │
│ before_state    │  │  │ last_delivery   │  │  │ context (JSONB) │  │
│ after_state     │  │  │ delivery_errors │  │  │ metadata (JSONB)│  │
│ request_id      │  │  │ audit_event_id  │◄─┘  │ success         │  │
│ correlation_id  │  │  │ (FK audit_events│     │ error_message   │  │
│ trace_id        │  │  │ created_timestmp│◄FIX │ rollback_done   │  │
│ event_timestamp │  │  │ created_by      │◄NEW │ audit_event_id  │◄─┘
│ timezone        │  │  └─────────────────┘     │ (FK audit_events│◄NEW
│ dev_phase       │  │                          │ created_timestamp│  │
│ ruleset_version │  │                          │ created_by      │  │
│ enforcement_mode│  │                          │ updated_timestamp│  │
│ affected_res    │  │                          │ updated_by      │  │
│ impact_level    │  │                          └─────────────────┘  │
│ requires_hitl   │  │                                               │
│ hitl_task_id(FK)│  │          ┌─────────────────┐                  │
│ additional_ctx  │  │          │     users       │                  │
│ source_system   │  │          │   (enhanced)    │                  │
│ created_timestamp│ │          ├─────────────────┤                  │
│ created_by      │  │          │ user_id (PK)    │──────────────────┘
│ updated_timestamp│ │          │ username        │
│ updated_by      │  │          │ email           │
└─────────────────┘  │          │ is_llm_agent    │
                     │          │ agent_type      │
    ┌────────────────┘          │ agent_version   │
    │ NEW RELATIONSHIPS:       │ capabilities    │
    │ • Pipeline override audits link to users table (administrator_id FK)
    │ • Pipeline override audits link to audit_events (comprehensive audit trail)
    │ • Pipeline event logs link to audit_events (operational + business audit correlation)
    └─► Complete audit ecosystem with cross-table traceability

                     │          │ created_timestamp│
                     │          │ updated_timestamp│
                     │          └─────────────────┘
```

**Enhanced User Table Fields:**
- `is_llm_agent` (BOOLEAN): Distinguishes between human users (FALSE) and automated agents (TRUE)
- `agent_type` (VARCHAR): For agents, specifies the type: 'research_agent', 'ocr_agent', 'vision_agent', 'synthesis_agent', 'pipeline_agent', etc.
- `agent_version` (VARCHAR): Agent version for capability tracking and audit correlation
- `capabilities` (JSONB): Agent-specific capability configuration for audit context

This enhancement ensures complete audit accountability by distinguishing between:
- **Human Users**: Researchers, administrators, domain experts
- **Research Agents**: Patent analysis and corpus navigation
- **OCR Agents**: Document text extraction and processing
- **Vision Agents**: Diagram/image analysis and interpretation  
- **Synthesis Agents**: Multi-modal content integration
- **Pipeline Agents**: Automated workflow execution

---

## Data Flow Diagrams

### Document Processing Data Flow

```
┌─────────────────┐
│ Document Upload │
│ (PDF/XML/HTML)  │
└─────────┬───────┘
          ▼
┌─────────────────┐    ┌─────────────────┐
│   Registration  │    │    File Store   │
│   + Metadata    │    │  (originals)    │
└─────────┬───────┘    └─────────────────┘
          ▼
┌─────────────────┐    ┌─────────────────┐
│ Content Extract │────│ Structure Parse │
│ + Normalization │    │ + JSON Markup   │
└─────────┬───────┘    └─────────┬───────┘
          ▼                      ▼
┌─────────────────────────────────────────┐
│        Image Extraction                 │
│     + Document Context Build            │
└─────────┬───────────────────────────────┘
          ▼
┌─────────────────────────────────────────┐
│        Multimodal Processing            │
│  OCR + Vision + LLM + Context Fusion    │
└─────────┬───────────────────────────────┘
          ▼
┌─────────────────┐    ┌─────────────────┐
│ Classification  │    │ Corpus          │
│ (corpus assign) │    │ Isolation       │
└─────────┬───────┘    └─────────┬───────┘
          ▼                      ▼
┌─────────────────────────────────────────┐
│      Section-Aware Chunking             │
│   + Vector Generation + Metadata        │
└─────────┬───────────────────────────────┘
          ▼
┌─────────────────────────────────────────┐
│    Vector Database Storage              │
│  Corpus-Segregated + Lifecycle Mgmt     │
└─────────────────────────────────────────┘
```

### Multimodal Image Processing Flow

```
Patent Document → Image Extraction → Figure Registry
    ↓
Individual Images + Document Context
    ↓ ↙ ↘
OCR Processing    Vision Analysis    Context Extraction
(Multi-Engine)    (PyTorch/OpenCV)   (Section References)
    ↓                 ↓                   ↓
Text Elements    Visual Structure    Reference Mapping
"606, 604"       "rectangles+arrows"  "606=database"
    ↓ ↘               ↓ ↙                ↓ ↗
          LLM Agent Synthesis
    (Combine Visual + Text + Context)
                ↓
    Enhanced Technical Description
"Figure 6 shows database server 606 receiving 
requests from user interface 604..."
                ↓
    Vector Chunks with Enhanced Metadata
```

### Vector Lifecycle Management Flow

```
Document Deletion Request
    ↓
┌─────────────────────────────────┐
│    Strategy Selection           │
│ ┌─────────┬─────────┬─────────┐ │
│ │Soft+Keep│Soft+Del │Hard Del │ │
│ └─────────┴─────────┴─────────┘ │
└─────────────────────────────────┘
    ↓        ↓        ↓
Strategy 1:  Strategy 2:  Strategy 3:
    ↓        ↓        ↓
Mark Deleted Delete    Delete All
Keep Vectors Vectors   + Records
Filter Search Audit    Physical
    ↓        ↓        ↓
Recovery     Recovery  No Recovery
Immediate    Reprocess Possible
```

---

## Audit Tables Review and Gap Analysis

### **Current Audit Infrastructure Assessment**

After reviewing the pipeline requirements, Standards.md mandates, and existing audit table implementations, here's the comprehensive analysis:

#### **✅ STRENGTHS - Requirements Met**

1. **Comprehensive Event Coverage**: `audit_events` table captures all required MANDATORY fields per Standards.md:
   - ✅ Human identity (`actor_type`, `actor_id`, `actor_name`) 
   - ✅ Resource affected (`resource_type`, `resource_id`, `resource_name`)
   - ✅ Action taken (`action_taken`)
   - ✅ Rationale (`action_rationale`)
   - ✅ Before/after state (`before_state`, `after_state` JSONB)
   - ✅ Immutable storage (enforced by application logic)

2. **Pipeline State Transitions**: All document/image state changes can be logged with:
   - ✅ State transition validation logging
   - ✅ Timeout handling audit trail
   - ✅ Error/exception capture with context
   - ✅ HITL escalation tracking (`requires_hitl`, `hitl_task_created`)

3. **Standards Compliance**: Full compliance with Standards.md audit requirements:
   - ✅ Correlation ID tracking (`correlation_id`, `request_id`, `trace_id`)
   - ✅ Development phase awareness (`development_phase`, `ruleset_version`)
   - ✅ Impact assessment (`affected_resources`, `impact_level`)

4. **Vector Lifecycle Management**: Custom tables support deletion strategies:
   - ✅ `vector_cleanup_audit` tracks what vectors were deleted and why
   - ✅ `vector_restoration_cache` enables recovery workflows
   - ✅ Complete audit trail for compliance

#### **⚠️ GAPS IDENTIFIED - Enhancements Needed**

1. **Pipeline Event Logs Audit Field Inconsistency**:
   ```
   ISSUE: pipeline_event_logs uses old naming convention
   CURRENT: created_at, timestamp  
   REQUIRED: created_timestamp, event_timestamp
   IMPACT: Standards.md non-compliance
   ```

2. **Missing Pipeline State Audit Integration**:
   ```
   GAP: No direct relationship between pipeline_event_logs and audit_events
   NEED: Cross-reference capability for complete audit trail
   SOLUTION: Add audit_event_id FK to pipeline_event_logs
   ```

3. **Multimodal Processing Audit Coverage**:
   ```
   GAP: OCR/Vision analysis results lack comprehensive audit tracking
   NEED: image_ocr_results and image_vision_analysis integration with audit_events
   ENHANCEMENT: Add audit triggers for multimodal processing failures/corrections
   ```

4. **Agent Output Versioning Audit** (Standards.md requirement):
   ```
   GAP: Agent outputs not systematically tracked in audit_events
   NEED: Automatic audit logging for all agent-generated artifacts
   REQUIREMENT: Rationale capture for human-requested changes
   ```

#### **🔧 RECOMMENDED ENHANCEMENTS**

### **Enhancement 1: Pipeline Event Log Standards Compliance**

**Issue**: Current `pipeline_event_logs` table doesn't follow Standards.md naming:
- Uses `timestamp` instead of `event_timestamp`  
- Missing standard audit fields

**Solution**: Update pipeline event logs structure:
```sql
-- Add to pipeline_event_logs
ALTER TABLE pipeline_event_logs 
ADD COLUMN created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN created_by VARCHAR(255) NOT NULL DEFAULT 'pipeline_system',
ADD COLUMN audit_event_id UUID REFERENCES audit_events(uuid);

-- Update existing timestamp column name for consistency
ALTER TABLE pipeline_event_logs 
RENAME COLUMN timestamp TO event_timestamp;
```

### **Enhancement 2: Multimodal Processing Audit Integration**

**Gap**: Image processing results need comprehensive audit coverage

**Solution**: Add audit triggers for multimodal processing:
- OCR confidence below threshold → audit_events entry
- Vision analysis failures → audit_events entry  
- Human corrections to descriptions → audit_events with rationale
- Multimodal LLM synthesis failures → audit_events with context

### **Enhancement 3: Complete Pipeline State Audit Chain**

**Need**: Link all pipeline events to central audit system

**Implementation**:
```sql
-- Enhance pipeline_override_audits with better audit integration
ALTER TABLE pipeline_override_audits
ADD COLUMN parent_audit_event_id UUID REFERENCES audit_events(uuid),
ADD COLUMN child_audit_events JSONB; -- Array of related audit event IDs

-- Add pipeline state transition audit trigger
-- Every document state change → automatic audit_events entry
```

#### **✅ CONCLUSION - MOSTLY COMPLIANT WITH TARGETED IMPROVEMENTS**

**Overall Assessment**: The current audit infrastructure is **85% compliant** with requirements:

- **Excellent Foundation**: `audit_events` table meets all Standards.md MANDATORY requirements
- **Strong Coverage**: Pipeline overrides, vector lifecycle management fully audited  
- **Targeted Gaps**: Pipeline event logs need standards alignment, multimodal processing needs enhanced audit integration

**Priority Actions**:
1. **HIGH**: Fix pipeline_event_logs naming convention (Standards.md compliance)
2. **MEDIUM**: Add audit event integration to multimodal processing failures
3. **LOW**: Enhance cross-table audit event relationships for complete traceability

The audit infrastructure strongly supports our patent intelligence corpus requirements with only minor enhancements needed for complete compliance.

### **MEDIUM Priority Enhancement: Multimodal Processing Audit Integration**

**Implementation Requirement**: Comprehensive audit coverage for advanced image processing pipeline

#### **OCR Processing Audit Requirements**
- **Confidence Threshold Events**: Automatic `audit_events` entry when OCR confidence < 0.7 threshold
  - `event_type`: 'ocr_low_confidence'
  - `action_taken`: 'escalate_to_hitl'
  - `before_state`: Original image metadata and OCR attempts
  - `after_state`: HITL task creation details
  - `action_rationale`: Confidence score and threshold comparison

- **Multi-Engine Failure Tracking**: Audit trail when multiple OCR engines fail
  - `event_type`: 'ocr_engine_failure'
  - `affected_resources`: Array of failed engine names and error codes
  - `impact_level`: 'high' for complete OCR failure scenarios

- **Processing Timeout Audits**: Log OCR timeouts with recovery actions
  - `event_type`: 'ocr_processing_timeout'
  - `additional_context`: Processing duration, timeout threshold, recovery strategy

#### **Vision Analysis Audit Requirements**
- **PyTorch Model Failures**: Audit vision processing errors
  - `event_type`: 'vision_analysis_failure'
  - `resource_type`: 'image'
  - `action_taken`: 'fallback_to_ocr_only'
  - `before_state`: Image properties and processing parameters
  - `after_state`: Error details and fallback decisions

- **Low-Confidence Vision Results**: Track uncertain spatial/layout analysis
  - `event_type`: 'vision_low_confidence'
  - `impact_level`: 'medium' for degraded multimodal descriptions
  - `requires_hitl`: TRUE for human review of complex diagrams

#### **Human Correction Audit Requirements**
- **OCR Override Events**: Mandatory rationale capture for text corrections
  - `event_type`: 'human_ocr_correction'
  - `actor_type`: 'human_reviewer'
  - `action_rationale`: Required field - reason for OCR correction
  - `before_state`: Original OCR extracted text
  - `after_state`: Human-corrected text

- **Description Modification Audits**: Track multimodal description changes
  - `event_type`: 'multimodal_description_modified'
  - `action_rationale`: Required - why AI description was insufficient
  - `correlation_id`: Links to original LLM synthesis process

#### **LLM Synthesis Failure Tracking**
- **Context Correlation Failures**: Audit when OCR/Vision/Document context fails to synthesize
  - `event_type`: 'multimodal_synthesis_failure'
  - `resource_type`: 'image'
  - `additional_context`: OCR confidence, vision confidence, context correlation score
  - `requires_hitl`: TRUE for complex technical diagrams

- **Generation Quality Issues**: Track low-quality multimodal descriptions
  - `event_type`: 'description_quality_concern'
  - `impact_level`: 'medium' for descriptions requiring human validation

#### **Database Integration Requirements**
```sql
-- Enhance image_ocr_results table
ALTER TABLE image_ocr_results 
ADD COLUMN audit_event_id UUID REFERENCES audit_events(uuid);

-- Enhance image_vision_analysis table  
ALTER TABLE image_vision_analysis
ADD COLUMN audit_event_id UUID REFERENCES audit_events(uuid);

-- Add audit triggers for multimodal processing
CREATE OR REPLACE FUNCTION audit_multimodal_processing() 
RETURNS TRIGGER AS $$
BEGIN
    -- Create audit event for low confidence results
    IF NEW.confidence_score < 0.7 THEN
        INSERT INTO audit_events (...) VALUES (...);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

#### **Business Value and Compliance Impact**
- **Legal Defensibility**: Complete traceability of patent image analysis decisions
- **Quality Improvement**: Data-driven optimization of multimodal processing algorithms  
- **Compliance**: Meets Standards.md requirements for immutable audit trails
- **HITL Integration**: Systematic escalation of low-confidence processing results
- **Performance Analytics**: Historical data for processing pipeline optimization

---

## Pipeline States and Transition Rules

### Document State Machine

| Current State | Next State | Trigger | Conditions | Actions |
|---------------|------------|---------|------------|---------|
| **INGESTED** | NORMALIZED | Automatic | Format validation passed | Begin content extraction |
| **NORMALIZED** | TEXT_EXTRACTED | Automatic | Text extraction completed | Extract embedded images |
| **TEXT_EXTRACTED** | IMAGES_EXTRACTED | Automatic | Image extraction completed | Begin OCR processing |
| **IMAGES_EXTRACTED** | PARTIALLY_PROCESSED | Threshold Met | 70-89% image completion | Generate partial vectors |
| **IMAGES_EXTRACTED** | READY | Threshold Met | ≥90% image completion | Generate complete vectors |
| **PARTIALLY_PROCESSED** | READY | Completion | Remaining images processed | Finalize vector generation |
| **Any Active** | BLOCKED | Error/HITL | Low confidence/Human needed | Queue HITL task |
| **Any Active** | FAILED | Fatal Error | Unrecoverable processing error | Error logging and notification |
| **Any Active** | REPROCESSING | User Request | Manual reprocessing triggered | Preserve versions, cascade cleanup |
| **READY** | DOCUMENT_REMOVED | User Action | Soft delete requested | Apply deletion strategy |
| **DOCUMENT_REMOVED** | REPROCESSING | User Action | Restore document requested | Restore + restart pipeline |
| **DOCUMENT_REMOVED** | PERMANENTLY_DELETED | System Cleanup | Retention period expired | Hard delete all data |

### Image State Machine

| Current State | Next State | Trigger | Conditions | Actions |
|---------------|------------|---------|------------|---------|
| **IMAGE_EXTRACTED** | PROCESSING | Automatic | OCR/Vision queued | Begin multimodal analysis |
| **PROCESSING** | NEEDS_INTERPRETATION | Low Confidence | OCR confidence < threshold | Queue HITL task |
| **PROCESSING** | COMPLETED | High Confidence | Processing successful | Store results, generate vectors |
| **NEEDS_INTERPRETATION** | COMPLETED | Human Approval | HITL task completed | Apply human corrections |
| **NEEDS_INTERPRETATION** | IGNORED | Human Decision | Human marks irrelevant | Flag as ignored, exclude from vectors |
| **Any Active** | DRAFT | User Edit | Manual description editing | Work-in-progress state |
| **DRAFT** | COMPLETED | User Submit | Submit to vector database | Generate vectors from description |
| **COMPLETED** | PROCESSING | User Reprocess | Re-run OCR/Vision requested | Restart multimodal processing |
| **Any Active** | MARKED_FOR_DELETION | Document Cascade | Parent document removed | Soft delete with parent |
| **MARKED_FOR_DELETION** | PROCESSING | Restore Cascade | Parent document restored | Restart processing pipeline |

### Transition Rules and Validation

#### **State Transition Validation**
- All state transitions must be valid according to state machine rules
- Invalid transitions logged as errors and rejected
- State rollback capabilities for critical transition failures
- Audit trail generation for all state changes

#### **Completion Thresholds**
- **PARTIALLY_PROCESSED**: 70% image completion + 100% critical images
- **READY**: 90% image completion + 100% critical images + no blocking errors
- **Image Criticality**: Determined by classification algorithm (title diagrams, technical schematics)

#### **Timeout Handling**
- **Document Timeout**: 24-hour maximum processing time
- **Image Timeout**: Configurable per processing type (OCR: 5min, Vision: 10min)
- **HITL Timeout**: 48-hour human review deadline with escalation
- **Starvation Prevention**: Priority boosting for long-waiting tasks

---

## Metadata Schemas

### Document Types and Metadata

#### **Patent Documents**
```json
{
  "document_structure": {
    "sections": [
      {
        "type": "abstract",
        "title": "Abstract",
        "start_pos": 0,
        "end_pos": 450,
        "text": "This patent describes..."
      },
      {
        "type": "claims",
        "title": "Claims", 
        "start_pos": 2500,
        "end_pos": 4200,
        "text": "1. A method comprising...",
        "claim_count": 15,
        "independent_claims": [1, 8, 14],
        "dependent_claims": [[2,3,4,5,6,7], [9,10,11,12,13], [15]]
      },
      {
        "type": "detailed_description",
        "title": "Detailed Description",
        "start_pos": 4200,
        "end_pos": 12000, 
        "text": "Referring to Figure 1...",
        "figure_references": ["Figure 1", "Figure 2", "Figure 6"],
        "reference_numerals": ["606", "604", "602", "610"]
      }
    ]
  },
  "bibliographic_data": {
    "patent_number": "US7123456",
    "application_number": "16/123456",
    "filing_date": "2024-01-15",
    "publication_date": "2025-07-15",
    "inventors": [
      {"name": "John Smith", "location": "San Francisco, CA"},
      {"name": "Jane Doe", "location": "New York, NY"}
    ],
    "assignee": "Example Corp",
    "ipc_classifications": ["G06F 16/35", "G06F 40/20"],
    "cpc_classifications": ["G06F16/35", "G06F40/20"],
    "us_classifications": ["707/736", "715/234"],
    "priority_claims": [
      {"number": "63/123456", "date": "2023-01-15", "country": "US"}
    ],
    "family_relationships": {
      "parent_applications": [],
      "continuation_applications": [],
      "related_patents": ["US7000001", "US7000002"]
    }
  }
}
```

#### **Prior Art Documents**  
```json
{
  "document_structure": {
    "sections": [
      {
        "type": "full_text",
        "title": "Prior Art Document",
        "start_pos": 0,
        "end_pos": 5000,
        "text": "Prior art document content..."
      }
    ]
  },
  "bibliographic_data": {
    "publication_number": "US20200123456",
    "publication_date": "2020-04-16",
    "inventors": ["Author Name"],
    "title": "Prior Art System and Method",
    "relevance_score": 0.85,
    "citation_context": "Cited in office action dated 2024-03-15"
  }
}
```

#### **Office Action Documents**
```json
{
  "document_structure": {
    "sections": [
      {
        "type": "examiner_rejections",
        "title": "Rejections",
        "start_pos": 500,
        "end_pos": 2000,
        "text": "Claims 1-5 are rejected...",
        "rejected_claims": [1, 2, 3, 4, 5],
        "rejection_basis": ["102", "103"]
      },
      {
        "type": "cited_references",
        "title": "References Cited",
        "start_pos": 2000,
        "end_pos": 2500,
        "references": [
          {"number": "US7000001", "relevance": "Claims 1-3"},
          {"number": "US7000002", "relevance": "Claims 4-5"}
        ]
      }
    ]
  },
  "bibliographic_data": {
    "application_number": "16/123456",
    "office_action_date": "2024-03-15",
    "examiner_name": "Jane Examiner",
    "response_deadline": "2024-06-15",
    "action_type": "Non-Final Rejection"
  }
}
```

#### **Product Documents**
```json
{
  "document_structure": {
    "sections": [
      {
        "type": "technical_specifications",
        "title": "Technical Specifications",
        "start_pos": 0,
        "end_pos": 3000,
        "text": "Product technical details...",
        "features": ["Feature A", "Feature B", "Feature C"]
      }
    ]
  },
  "bibliographic_data": {
    "product_name": "Example Product v2.0",
    "manufacturer": "Target Company",
    "release_date": "2024-01-01",
    "version": "2.0",
    "evidence_type": "technical_documentation",
    "infringement_potential": "high"
  }
}
```

### Image Processing Metadata

#### **OCR Results Schema**
```json
{
  "ocr_engine": "tesseract",
  "extracted_text": "Figure 6 shows database server 606...",
  "confidence_score": 0.87,
  "processing_time_ms": 2340,
  "language": "eng",
  "processing_timestamp": "2026-01-07T10:30:00Z",
  "engine_version": "5.2.0",
  "preprocessing_applied": ["contrast_enhancement", "noise_reduction"]
}
```

#### **Vision Analysis Schema**
```json
{
  "detected_objects": [
    {"type": "rectangle", "bbox": [100, 150, 200, 250], "confidence": 0.92},
    {"type": "arrow", "bbox": [250, 200, 300, 220], "confidence": 0.85},
    {"type": "text_region", "bbox": [120, 160, 180, 180], "text": "606"}
  ],
  "spatial_relationships": [
    {"from": "rectangle_1", "to": "rectangle_2", "relationship": "connected_by_arrow"},
    {"from": "text_606", "to": "rectangle_1", "relationship": "labels"}
  ],
  "layout_classification": "flowchart",
  "analysis_confidence": 0.78,
  "processing_model": "pytorch_vision_v1.2",
  "processing_timestamp": "2026-01-07T10:31:00Z"
}
```

#### **Multimodal Description Schema**
```json
{
  "multimodal_description": "Figure 6 illustrates a system architecture where database server 606 receives requests from user interface 604 and processes data through processing engine 602, showing the complete data flow for user request handling.",
  "generation_confidence": 0.91,
  "context_correlation_score": 0.88,
  "sources_used": ["ocr_tesseract", "vision_pytorch", "document_context"],
  "reference_numerals_correlated": ["606", "604", "602"],
  "figure_type": "system_architecture",
  "technical_complexity": "medium",
  "human_validated": false,
  "generation_timestamp": "2026-01-07T10:32:00Z",
  "llm_model_used": "local_patent_llm_v1"
}
```

---

## Document Deletion Rules and Lifecycle Management

### When Document Deletion is Possible

#### **Deletion Triggers**
1. **User Initiated**: Manual document removal through UI with reason selection
2. **System Cleanup**: Scheduled cleanup after retention period expiration  
3. **Data Quality**: Corrupted or unparseable documents flagged for removal
4. **Policy Compliance**: Documents violating corpus policies or access restrictions
5. **Storage Management**: Archive old documents to manage storage capacity

#### **Deletion Restrictions**
1. **Processing State**: Cannot delete documents in PROCESSING state (must wait or force-stop)
2. **Agent Dependencies**: Cannot delete if actively referenced by running agents
3. **HITL Tasks**: Cannot delete documents with pending human review tasks
4. **Version Control**: Cannot delete if referenced by other document versions
5. **Audit Requirements**: Cannot delete if within mandatory audit retention period

### Three-Tier Deletion Strategy

#### **Strategy 1: Soft Delete with Vector Retention**
**Use Cases**: 
- Document temporarily irrelevant but may be restored
- Uncertain deletion decisions requiring easy recovery
- Testing scenarios where document removal is experimental

**Process**:
```
User Request → Confirm Deletion → Mark documents.deletion_strategy = 'soft_keep'
    ↓
Set documents.vector_cleanup_status = 'deleted_filtered'
    ↓
Vectors remain in database but excluded from search queries
    ↓
Recovery: Immediate restoration without reprocessing
```

**Database Changes**:
- `documents.vector_cleanup_status = 'deleted_filtered'`
- `documents.deletion_strategy = 'soft_keep'`
- Search filters automatically exclude deleted documents
- All data preserved for instant recovery

#### **Strategy 2: Soft Delete with Vector Cleanup** 
**Use Cases**:
- Document definitively not relevant for analysis
- Need to clean up search space and remove stale vectors
- Standard deletion for most document removal scenarios

**Process**:
```
User Request → Confirm Deletion → Mark documents.deletion_strategy = 'soft_remove'
    ↓
Cascade delete all vector embeddings (follows REPROCESSING pattern)
    ↓
Remove search index entries and clear RAG cache
    ↓
Document data preserved but vectors cleaned
    ↓
Recovery: Restore possible but requires full reprocessing
```

**Database Changes**:
- `documents.vector_cleanup_status = 'vectors_deleted'` 
- `documents.deletion_strategy = 'soft_remove'`
- Vector embeddings deleted immediately
- Document content preserved for potential recovery
- Audit trail logs vector deletion counts and timestamps

#### **Strategy 3: Hard Delete with Complete Cleanup**
**Use Cases**:
- Permanent removal after retention period expiration
- Confidential documents requiring complete elimination
- Storage optimization requiring physical data removal

**Process**:
```
System Scheduled Job → Check retention period → Permanent deletion eligible
    ↓
Delete all vector embeddings and search indices
    ↓
Delete all related database records (images, artifacts, versions)
    ↓
Delete physical files from storage
    ↓
Recovery: Impossible - complete data elimination
```

**Database Changes**:
- Complete record deletion from all tables
- Physical file removal from storage
- Audit logs preserved showing deletion occurred
- No recovery possible

### Deletion Workflow and User Interface

#### **Deletion Confirmation Process**
1. **Strategy Selection**: User chooses deletion strategy with explanation of consequences
2. **Impact Assessment**: System shows affected documents, images, vectors, and dependencies  
3. **Reason Capture**: Mandatory deletion reason from predefined categories
4. **Confirmation**: Double-confirmation for hard delete operations
5. **Progress Tracking**: Real-time deletion progress with cancellation option (before completion)

#### **Deletion Reason Categories**
```json
{
  "deletion_reasons": [
    "document_replaced_by_newer_version",
    "document_not_relevant_to_analysis", 
    "incorrect_document_uploaded",
    "document_corrupted_or_unparseable",
    "confidential_content_removal_required",
    "duplicate_document_cleanup",
    "corpus_policy_violation",
    "user_request_for_removal",
    "storage_optimization_cleanup",
    "scheduled_retention_policy_cleanup"
  ]
}
```

### Post-Deletion Actions and Recovery

#### **Immediate Post-Deletion Actions**
1. **Audit Log Creation**: Complete deletion audit with strategy, reason, affected entities
2. **Dependent Entity Cleanup**: Cascade cleanup of images, artifacts, versions per strategy
3. **Search Index Updates**: Remove or mark deleted entities in search systems
4. **Agent Notification**: Notify running agents of document unavailability
5. **HITL Task Updates**: Cancel pending tasks for deleted documents
6. **Cache Invalidation**: Clear relevant caches and temporary data

#### **Recovery Procedures**

**Soft Delete Recovery (Strategy 1)**:
```
User Request → Locate deleted document → Verify recovery permissions
    ↓
Set vector_cleanup_status = 'active' and deletion_strategy = NULL
    ↓
Document immediately available in search and processing
    ↓
Audit log recovery action with timestamp and user
```

**Soft Delete with Vector Recovery (Strategy 2)**:
```
User Request → Locate deleted document → Verify recovery permissions
    ↓
Restore document metadata and set status to REPROCESSING
    ↓
Restart full processing pipeline (text + images + vectors)
    ↓
Document available after processing completion
    ↓
Audit log recovery action with reprocessing timeline
```

**Hard Delete Recovery**:
- **Not Possible**: Complete data elimination prevents any recovery
- **Alternative**: Re-upload original document if available externally
- **Audit Trail**: Deletion audit logs provide record of what was removed

#### **Recovery Limitations and Considerations**
1. **Time Limits**: Soft deleted documents have configurable retention before hard cleanup
2. **Storage Costs**: Soft delete strategies require additional storage for retained data
3. **Performance Impact**: Large numbers of soft deleted documents may impact query performance
4. **Audit Compliance**: All recovery actions must be logged for compliance requirements
5. **User Permissions**: Recovery operations may require elevated permissions or approval workflows

---

**Status**: This comprehensive requirements specification provides the foundation for strategic development planning and technical implementation of the patent intelligence corpus management system.