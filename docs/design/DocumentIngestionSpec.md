# Document Ingestion Specification

**Status**: APPROVED - PostgreSQL Local-First and Manual Upload Priority (Dec 30, 2025)  
**Authority**: Technical implementation guidance for P3.3 Document Ingestion Implementation  
**Cross-References**: [SystemNarrative.md](../SystemNarrative.md) (business context), [DataFlowDiagram.md](../DataFlowDiagram.md) (flow visualization), [PipelineStateMachine.md](../PipelineStateMachine.md) (state transitions), [DatabaseSchemaSpec.md](./DatabaseSchemaSpec.md) (persistence)

## Authority Relationship

**SystemNarrative.md defines WHAT** (document acquisition requirements and sources)  
**This specification defines HOW** (technical implementation of document intake)  
**BuildPlan.md P3.3 defines WHEN** (execution requirements and acceptance criteria)

## Purpose

Defines technical implementation of document acquisition, normalization, and artifact generation for patent intelligence pipeline, covering both manual uploads and research agent acquisition paths.

## Required Content (Minimum Specification)

### Document Intake Paths

#### Manual Upload Path
- **File Upload Interface**: HTML form with FastAPI backend
- **Supported Formats**: PDF, XML, HTML, images (PNG, JPG, TIFF)
- **File Validation**: Format verification, size limits, content integrity checks
- **Metadata Capture**: Source attribution, upload timestamp, user context
- **Error Handling**: Invalid formats, oversized files, corrupted uploads

#### Research Agent Path (Phase 3 Scope)
- **Manual Trigger Only**: No automated scheduling or background processing
- **Source Types**: USPTO database, Google Patents (API keys required)
- **Document Types**: Patents, Office Actions, IPR decisions, prior art references
- **Validation Logic**: Source authenticity verification, duplicate detection
- **Rate Limiting**: API usage throttling to prevent service disruption

### Document Registration & Versioning

#### Registration Process
- **Document ID Generation**: UUID v4 for document identity
- **Source Type Assignment**: manual_upload | research_agent
- **Document Type Detection**: patent | office_action | ipr_decision | prior_art | product_doc
- **Initial State Assignment**: INGESTED per PipelineStateMachine.md
- **Corpus Assignment**: Deferred to P3.5 Corpus Classification

#### Version Management
- **Immutable Storage**: Original document bytes preserved exactly
- **Version Tracking**: Sequential version numbers for document updates
- **Lineage Recording**: Parent-child relationships for document revisions
- **Audit Trail**: All registration events with timestamp and source attribution

### Normalization Pipeline

#### Content Extraction
- **PDF Processing**: Text extraction via PyPDF library, preserve original formatting
- **XML Processing**: Structure preservation, namespace handling, validation
- **HTML Processing**: Clean HTML parsing, link and reference extraction
- **Metadata Extraction**: Title, author, publication date, reference numbers

#### Text Normalization
- **Encoding Standardization**: UTF-8 conversion with fallback handling
- **Whitespace Normalization**: Consistent line breaks, paragraph boundaries
- **Character Cleaning**: Remove control characters, preserve patent-specific formatting
- **Structure Preservation**: Section headers, claim numbering, figure references

#### Asset Extraction
- **Image Detection**: Embedded images, figures, diagrams identification
- **Asset Storage**: Separate storage for binary assets with document linkage
- **Reference Mapping**: Figure numbers to image assets, caption extraction
- **Format Conversion**: Standardize image formats for downstream processing

### Artifact Generation

#### Normalized Document Artifacts
- **Clean Text**: Structured text with preserved patent-specific formatting
- **Metadata Record**: Structured document attributes and references
- **Section Map**: Hierarchical document structure with section boundaries
- **Reference Index**: Internal and external reference catalog

#### Asset Artifacts  
- **Image Registry**: Catalogued images with perceptual hashes
- **Figure Descriptions**: Placeholder descriptions for downstream OCR processing
- **Caption Mapping**: Figure captions linked to image assets
- **Reference Links**: Figure references within document text

### Failure Handling & Recovery

#### Validation Failures
- **Format Rejection**: Unsupported or corrupted document formats
- **Size Limits**: Documents exceeding storage or processing limits
- **Content Validation**: Malformed or incomplete document content
- **Recovery Actions**: User notification, retry mechanisms, manual intervention

#### Processing Failures
- **Extraction Errors**: Text or metadata extraction failures
- **Normalization Issues**: Character encoding or formatting problems
- **Asset Failures**: Image extraction or processing errors
- **Graceful Degradation**: Partial processing with flagged failures

#### State Transition Rules
- **Success Path**: INGESTED → NORMALIZED → TEXT_EXTRACTED per PipelineStateMachine.md
- **Failure Path**: Any state → FAILED with error logging
- **Recovery Path**: FAILED → INGESTED for retry processing
- **Manual Override**: Administrative state transitions with audit logging

### Provenance Integration

#### Document Lineage
- **Source Attribution**: Complete source metadata and acquisition method
- **Processing History**: All normalization and extraction steps recorded
- **Asset Lineage**: Image extraction and processing provenance
- **Error Lineage**: Failed processing attempts with error details

#### Audit Events
- **Registration Events**: Document intake with source and metadata
- **Processing Events**: Normalization steps with success/failure status
- **State Transitions**: All pipeline state changes with triggers
- **Access Events**: Document retrieval and viewing events

## Design Decisions (APPROVED)

### Storage Architecture
- [x] **PostgreSQL Persistence**: All document metadata in relational database
- [x] **Binary Storage**: Original documents in filesystem with database references
- [x] **Asset Management**: Images stored separately with document linkage
- [x] **No External Services**: Local-only processing without external dependencies

### Processing Approach
- [x] **Synchronous Processing**: Direct processing without background queues
- [x] **Error Transparency**: All failures visible with clear error messages
- [x] **Manual Intervention**: Human oversight for failed processing
- [x] **Idempotent Operations**: Safe to retry processing without side effects

## Idempotency & Partial Failure Handling

### Idempotency

#### Document Duplicate Prevention
- **Document ingestion MUST be idempotent** - identical documents create single records
- **Identical document hashes resolve to the same document record** without duplication
- **Re-ingestion of identical documents does not create duplicates** but may update metadata

#### Hash Input Specification
- **Binary Content Hash**: SHA-256 of complete file binary content
- **Metadata Normalization**: Filename lowercased, whitespace normalized, timestamps excluded
- **Hash Input Formula**: `hash(binary_content + normalized_filename + file_size)`
- **Hash Collision Handling**: Secondary content comparison for hash matches

### Partial Ingestion Behavior

#### Mixed Success/Failure Scenarios
- **Text Extraction Success + Image Processing Failure**: Document persisted in PARTIAL state
- **Some Images Processed + Some Failed**: Successful artifacts preserved, failed flagged for retry
- **Metadata Success + Content Failure**: Basic document record created, content processing flagged

#### Partial State Management
- **PARTIAL State Documents**: Preserved with successful artifacts intact
- **Failed Artifact Tracking**: Individual artifact failures logged with retry capability
- **Progressive Completion**: Additional processing attempts build on existing successful artifacts
- **No Artifact Invalidation**: Partial failure does NOT invalidate previously successful artifacts

#### Recovery Strategies
- **Incremental Retry**: Retry only failed artifacts, preserve successful ones
- **HITL Escalation**: Complex partial failures escalated for human decision
- **State Progression**: PARTIAL documents can progress to READY when all artifacts complete
- **Audit Completeness**: All partial failure events logged with complete artifact inventory

## Implementation Guidance

### FastAPI Integration
- Document upload endpoints with multipart/form-data support
- Validation middleware for file type and size checking
- Progress tracking for large document processing
- Error response formatting with user-friendly messages

### Configuration Architecture
- **All tunable values** (file size limits, timeout thresholds, retry counts) sourced from .env files
- **Loaded via Pydantic BaseSettings** with type validation and defaults
- **Configuration changes allowed by the single reviewer** through UI configuration interface
- **Configuration changes must be logged, timestamped, and attributed** per audit requirements
- **No runtime hardcoding of tunable values** - all limits and thresholds configurable

### Database Integration
- Document table with metadata fields and binary reference
- Asset table for image and figure storage references
- Processing history table for audit and troubleshooting
- Transaction boundaries for atomic document registration

### Error Handling Patterns
- Exception hierarchy for different failure types
- Logging integration with structured error information
- User notification system for processing failures
- Administrative interface for failed document recovery

## Acceptance Criteria

- [ ] Manual document upload through web interface functional
- [ ] Research agent document acquisition operational (manual trigger)
- [ ] PDF, XML, HTML document formats processed correctly
- [ ] Text extraction and normalization produce clean, structured output
- [ ] Images extracted and catalogued with document linkage
- [ ] Processing failures handled gracefully with user notification
- [ ] All document registration events logged with complete provenance
- [ ] Document versioning and lineage tracking operational
- [ ] State transitions comply with PipelineStateMachine.md rules
- [ ] No background processing or external service dependencies

---

**Status**: SPECIFICATION COMPLETE - Ready for P3.3 Implementation  
**Approved**: Manual Upload Priority + PostgreSQL Storage (Dec 30, 2025)