# Enhanced Document and Image Lifecycle Management - State Machine Extension

**Status**: PROPOSAL - Comprehensive Enhancement for Phase 3.2B+  
**Authority**: Technical proposal for PipelineStateMachine.md extension  
**Standards Compliance**: [Standards.md](../Standards.md) - MANDATORY common services usage, configuration patterns, and logging requirements  
**Governance Compliance**: [AgentRules.md](../AgentRules.md) - Phase 3 authorized implementation  
**Cross-References**: [PipelineStateMachine.md](../PipelineStateMachine.md) (current state definitions), [Standards.md](../Standards.md) (technical requirements)

## Executive Summary

This proposal defines comprehensive enhancements to the document and image lifecycle management system, introducing advanced state management, soft delete architecture, version preservation, and multi-OCR support. The design addresses critical gaps in document removal, reprocessing workflows, and user control while maintaining full audit compliance and Standards.md adherence.

## Authority Relationship

**PipelineStateMachine.md defines WHAT states** (current document/image lifecycle)  
**This proposal defines ENHANCED WHAT** (extended states and transitions)  
**Future implementation specs define HOW** (technical implementation details)  
**Standards.md defines COMPLIANCE** (mandatory service usage and patterns)

## Background & Requirements

### Current State Gaps Identified
- No permanent document removal capability with cascading deletes
- Missing document replacement workflow during reprocessing  
- No document-level IGNORED state for research workflow management
- Limited user control over reprocessing decisions
- Single OCR engine limitation for complex document extraction

### User Workflow Requirements
- **Single-user research context**: <100 documents, overnight processing acceptable
- **Research-grade quality control**: User approval for all critical content
- **Version preservation**: Never lose approved content during reprocessing
- **Granular control**: Update individual components without full reprocessing
- **Audit compliance**: Complete traceability for research and legal requirements

## Proposed State Machine Extensions

### Enhanced Document States

| Current State | New/Enhanced State | Purpose |
|---------------|-------------------|----------|
| PROCESSING | PROCESSING | No change - current processing logic |
| COMPLETED | COMPLETED | No change - current completion logic |
| BLOCKED | BLOCKED | No change - current blocking logic |
| **NEW** | **REPROCESSING** | User-triggered reprocessing with cascade soft-delete |
| **NEW** | **DOCUMENT_REMOVED** | Soft delete with reason codes and audit trail |
| **NEW** | **DRAFT** | Work-in-progress state without vectorization |

### Enhanced Image States

| Current State | New/Enhanced State | Purpose |
|---------------|-------------------|----------|
| IMAGE_EXTRACTED | IMAGE_EXTRACTED | No change - current extraction logic |
| NEEDS_INTERPRETATION | NEEDS_INTERPRETATION | Enhanced with multi-OCR support |
| INTERPRETED | INTERPRETED | Enhanced with version preservation |
| CANONICALIZED | **COMPLETED** | Renamed for consistency |
| IGNORED | IGNORED | Enhanced with reprocess confirmation |
| **NEW** | **DRAFT** | Work-in-progress descriptions |
| **NEW** | **MARKED_FOR_DELETION** | Soft delete state |
| **NEW** | **FAILED** | OCR processing failures requiring user decision |

## Complete CRUD Operations Matrix

### Document CRUD Operations

| Operation | Trigger | Current State | New State | Side Effects | User Actions | System Actions |
|-----------|---------|---------------|-----------|--------------|--------------|----------------|
| **CREATE** | User Upload (Any Type) | N/A | PROCESSING | Text extraction/OCR + image extraction + image OCR | Upload file (text doc, scanned doc, or image-only with context) | Auto-pipeline: document processing + image processing |
| **CREATE** | Research Agent | N/A | PROCESSING | Text extraction/OCR + image extraction + image OCR | N/A | Agent-triggered upload with full pipeline |
| **READ** | User Review | Any | No change | N/A | View document, search, filter | Query database |
| **UPDATE** | Edit Document Text Only | Any active | No state change | **Document text vector re-indexing only** | Edit main document text in UI | Update document vectors, preserve image vectors |
| **UPDATE** | Edit Single Image Text | Any active | No state change | **Individual image vector re-indexing** | Edit specific image "Official_Description" | Update only that image's vectors |
| **UPDATE** | User Reprocess (Full) | Any active | REPROCESSING | **Full cascade soft-delete** + preserve all approved versions | Click "Reprocess Document" button | Soft-delete all images, re-extract text/images, preserve versions for tabs |
| **UPDATE** | Edit Metadata | Any active | No state change | N/A | Edit title, tags, notes, reason codes | Update database metadata only |
| **SOFT DELETE** | User Remove Document | Any active | DOCUMENT_REMOVED | **Cascade soft-delete all images** + audit trail | Click "Remove Document" + reason selection | Soft delete document + all images, create audit records |
| **UNDELETE** | User Restore Document | DOCUMENT_REMOVED | REPROCESSING | **Cascade restore all images** + restart pipeline | Click "Restore Document" | Restore document + all images, restart full pipeline |
| **PERMANENT DELETE** | System Cleanup | DOCUMENT_REMOVED | PERMANENTLY_DELETED | **Hard delete all data** | N/A | Scheduled cleanup job (configurable retention) |

### Image CRUD Operations

| Operation | Trigger | Current State | New State | Side Effects | User Actions | System Actions |
|-----------|---------|---------------|-----------|--------------|--------------|----------------|
| **CREATE** | Document Processing | N/A | PROCESSING | Multi-OCR extraction initiated | N/A | Auto-extract from document + OCR attempts |
| **CREATE** | Manual Upload (via Document) | N/A | PROCESSING | OCR processing with document context | Create wrapper document + upload image | OCR processing with contextual document text |
| **READ** | User Review (Multi-Tab) | Any | No change | N/A | View image + multi-tab interface | Query database + retrieve all OCR attempts |
| **UPDATE** | Edit Description (Draft) | Any active | DRAFT | **No vector indexing** | Edit "Official_Description" + click "Save Draft" | Store description without vectorization |
| **UPDATE** | Submit Final Description | DRAFT | COMPLETED | **Vector indexing triggered** | Edit description + click "Submit to Vector DB" | Vectorize description and make searchable |
| **UPDATE** | Copy From Source Tab | Any active | DRAFT/COMPLETED | **Vector re-indexing if completed** | Click "Copy ↑" from any source tab | Copy text to Official_Description |
| **UPDATE** | Create Reference (Copy) | Any active | No change | **Copy approved text + reference metadata** | Click "Reference existing" + select source | Copy description + set reference lineage |
| **UPDATE** | Re-run OCR (Same Engine) | Any active | PROCESSING | **New OCR attempt stored** | Click "Re-run [Engine Name]" | Re-execute specific OCR engine, store new result |
| **UPDATE** | Try Different OCR Engine | Any active | PROCESSING | **Additional OCR result stored** | Click "Try Different OCR" + select engine | Run new OCR engine, add tab for results |
| **UPDATE** | Mark Ignored | Any active | IGNORED | **Remove from vector index** + audit trail | Click "Ignore Image" + reason selection | Update status, remove vectors, store reason |
| **UPDATE** | Confirm Ignore (Reprocess) | IGNORED (during reprocess) | IGNORED | **Maintain ignored status** | Confirm "Keep Ignored" during document reprocess | Preserve ignored status + original reason |
| **UPDATE** | Override Ignore (Reprocess) | IGNORED (during reprocess) | PROCESSING | **Re-enter processing pipeline** | Select "Process This Time" during document reprocess | Resume normal processing with new OCR |
| **SOFT DELETE** | Document Cascade | Any | MARKED_FOR_DELETION | **Remove from vector index** + cascade audit | N/A (triggered by document removal) | Soft delete + vector cleanup + audit cascade |
| **UNDELETE** | Document Cascade Restore | MARKED_FOR_DELETION | PROCESSING | **Restore to processing pipeline** | N/A (triggered by document restore) | Cascade restore + reprocess confirmation required |
| **PERMANENT DELETE** | System Cleanup | MARKED_FOR_DELETION | PERMANENTLY_DELETED | **Hard delete files + DB records** | N/A | Scheduled cleanup job + file system cleanup |

## Technical Architecture Requirements

### Soft Delete Implementation

#### Database Schema Extensions
```sql
-- Soft delete columns for documents table
ALTER TABLE documents ADD COLUMN deletion_marked_at TIMESTAMP NULL;
ALTER TABLE documents ADD COLUMN deletion_reason VARCHAR(100);
ALTER TABLE documents ADD COLUMN marked_by_user VARCHAR(100);

-- Soft delete columns for images table  
ALTER TABLE images ADD COLUMN deletion_marked_at TIMESTAMP NULL;
ALTER TABLE images ADD COLUMN deletion_reason VARCHAR(100);
ALTER TABLE images ADD COLUMN marked_by_user VARCHAR(100);

-- Version preservation for reprocessing
ALTER TABLE documents ADD COLUMN previous_approved_text TEXT;
ALTER TABLE images ADD COLUMN previous_approved_description TEXT;
```

#### Reason Code Enumeration
```python
class DocumentRemovalReason(str, Enum):
    DOCUMENT_REPLACE = "document_replace"
    DOCUMENT_NOT_RELEVANT = "document_not_relevant" 
    INCORRECT_DOCUMENT = "incorrect_document"
    DOCUMENT_NOT_PARSABLE = "document_not_parsable"
    USER_REQUEST = "user_request"
```

### Multi-OCR Architecture (Extensible)

#### OCR Abstraction Layer
```python
# Abstract interface for future extensibility
class OCREngine(ABC):
    @abstractmethod
    def extract_text(self, image: bytes) -> OCRResult:
        pass
    
    @abstractmethod
    def get_confidence_score(self, result: OCRResult) -> float:
        pass
    
    @abstractmethod  
    def get_engine_name(self) -> str:
        pass

# Initial implementation
class TesseractOCR(OCREngine):
    # Single engine implementation for Phase 3
    
# Future implementations (Phase 4+)
class AzureOCR(OCREngine):
    pass
    
class GoogleVisionOCR(OCREngine):
    pass
```

#### OCR Results Storage
```sql
-- Support multiple OCR results per image
CREATE TABLE image_ocr_results (
    id UUID PRIMARY KEY,
    image_id UUID REFERENCES images(id),
    ocr_engine VARCHAR(50) NOT NULL,
    extracted_text TEXT,
    confidence_score FLOAT,
    processing_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Reference System with Copy-on-Reference

#### Reference Metadata Schema
```sql
-- Reference lineage tracking
ALTER TABLE images ADD COLUMN referenced_from VARCHAR(100); -- format: "doc-123-img-456"
ALTER TABLE images ADD COLUMN description_copied_at TIMESTAMP;
ALTER TABLE images ADD COLUMN reference_source_description TEXT;
```

#### Copy-on-Reference Implementation
```python
def create_image_reference(source_image_id: str, target_image_id: str):
    """Copy description from source to target, maintain reference lineage."""
    source = get_image(source_image_id)
    target = get_image(target_image_id)
    
    # Copy approved description
    target.official_description = source.official_description
    target.referenced_from = f"{source.document_id}-{source.id}"
    target.description_copied_at = time_service.utc_now()
    
    # Log reference creation for audit
    logger.info("Image reference created", extra={
        "source_image": source_image_id,
        "target_image": target_image_id,
        "description_length": len(source.official_description)
    })
```

## User Interface Requirements

### Multi-Tab Review Interface

#### Document Text Review (Reprocessing)
```
┌─ Official_Document_Text (Editable) ──────────────────┐
│ [Empty - ready for user decision]                   │
└──────────────────────────────────────────────────────┘

┌─ Source Tabs ───────────────────────────────────────┐
│ [New Extraction] [New OCR] [Last Official Version]  │
│                                                      │
│ Last Official Version:                               │
│ "This document describes the assembly process..."    │
│ [Copy ↑]                                            │
└──────────────────────────────────────────────────────┘

[Submit to Vector DB] [Save as Draft]
```

#### Image Description Review (Multi-OCR)
```
┌─ Official_Description (Editable) ────────────────────┐
│ [Empty or current description]                      │
└──────────────────────────────────────────────────────┘

┌─ Source Tabs ───────────────────────────────────────┐
│ [Tesseract] [Manual Entry] [Last Version] [Reference] │
│                                                      │
│ ┌─ Tesseract Tab ─────────────────────────────────────┐│
│ │ Status: ✅ Completed (confidence: 87%)            ││
│ │ Text: "Assembly diagram showing widget..."          ││
│ │ [Copy ↑] [Re-run Tesseract] [Try Different OCR]    ││
│ └─────────────────────────────────────────────────────┘│
└────────────────────────────────────────────────────────┘

[Submit to Vector DB] [Save as Draft] [Ignore Image + Reason]
```

### State Transition Controls

#### Document Controls
- **Reprocess Document**: Full pipeline restart with version preservation
- **Remove Document**: Soft delete with reason code selection
- **Restore Document**: Recover from DOCUMENT_REMOVED state

#### Image Controls  
- **Try Different OCR**: Launch alternative OCR engine
- **Reference Existing**: Link to existing image with description copy
- **Ignore Image**: Move to IGNORED state with reason
- **Un-ignore**: Return IGNORED image to processing

## Standards.md Compliance

### Mandatory Common Services Usage

#### Database Operations
```python
# REQUIRED: Use async_get_db() dependency injection
async def update_document_state(
    document_id: str, 
    new_state: DocumentState,
    db: AsyncSession = Depends(async_get_db)
):
    # Implementation using Standards.md required patterns
```

#### Logging Integration
```python
# REQUIRED: Use LoggingService for all operations
from common.logging import logger

logger.info("Document reprocessing initiated", extra={
    "document_id": document_id,
    "previous_state": old_state,
    "new_state": new_state,
    "user_id": user_id,
    "reason": reason_code
})
```

#### ID Generation
```python
# REQUIRED: Use IDService for all ID generation
from common.ids import id_service

audit_record_id = id_service.generate_id()
```

#### Time Management
```python
# REQUIRED: Use TimeService for all time operations  
from common.time import time_service

deletion_timestamp = time_service.utc_now()
```

### Configuration Requirements

#### New Configuration Variables
```python
# Add to src/app/core/config.py per Standards.md patterns
class Settings(BaseSettings):
    # Soft delete retention
    SOFT_DELETE_RETENTION_DAYS: int = 30
    
    # OCR configuration (extensible)
    PRIMARY_OCR_ENGINE: str = "tesseract"
    OCR_ENGINES_AVAILABLE: List[str] = ["tesseract"]
    
    # Reprocessing behavior
    PRESERVE_APPROVED_VERSIONS: bool = True
    REQUIRE_IGNORE_CONFIRMATION: bool = True
```

### API Response Compliance

#### Standard API Responses
```python
# Document removal API response
return APIResponse[DocumentRemovalResult](
    data=DocumentRemovalResult(
        document_id=document_id,
        removal_reason=reason,
        images_affected=len(cascade_deletes),
        audit_record_id=audit_id
    ),
    message="Document successfully marked for deletion",
    request_id=request_id,
    timestamp=time_service.utc_now()
)
```

## Implementation Phases

### Phase 3.2B: Foundation Enhancement
- **Soft delete architecture**: Database schema updates and basic implementation
- **REPROCESSING state**: Basic reprocessing workflow with version preservation
- **Enhanced UI controls**: Document and image management interfaces
- **Standards compliance**: Full integration with mandatory common services

### Phase 3.2C: Advanced Features  
- **Multi-OCR abstraction**: OCR engine interface with Tesseract implementation
- **Reference system**: Copy-on-reference implementation with lineage tracking
- **Draft system**: Work-in-progress state management
- **Advanced UI**: Multi-tab interfaces and comparison tools

### Phase 3.3+: Future Enhancements
- **Additional OCR engines**: Azure, Google, AWS integration
- **Bulk operations**: Multi-document processing workflows  
- **Advanced analytics**: Processing quality metrics and optimization
- **Enterprise features**: Advanced audit reporting and compliance tools

## Risk Assessment & Mitigations

### Implementation Risks
- **Database schema changes**: Mitigated by Phase 3 fresh schema assumption per Standards.md
- **Performance impact**: Mitigated by single-user context and overnight processing windows
- **User interface complexity**: Mitigated by progressive enhancement and intuitive design patterns

### Data Safety Measures
- **Soft delete protection**: No permanent data loss during normal operations
- **Version preservation**: All approved content maintained during reprocessing
- **Audit trails**: Complete traceability for all user actions
- **Rollback capability**: Restore functionality for accidental deletions

## Success Metrics

### User Experience Metrics
- **Document processing time**: <24 hours for complex documents (overnight processing)
- **User control granularity**: Individual image/document text editing without full reprocessing
- **Version preservation rate**: 100% preservation of approved content during reprocessing

### Technical Metrics  
- **Standards compliance**: 100% usage of mandatory common services
- **Audit completeness**: Complete traceability for all state transitions
- **OCR extensibility**: Clean addition of new OCR engines without refactoring
- **Performance impact**: <10% overhead for soft delete vs hard delete operations

## Conclusion

This proposal provides comprehensive enhancement to document and image lifecycle management while maintaining strict compliance with Standards.md requirements and AgentRules.md governance. The design addresses critical workflow gaps identified during Phase 3.2B architecture review and provides a scalable foundation for future enhancements.

The soft delete architecture with full audit trails ensures enterprise-grade data safety, while the multi-OCR abstraction layer provides flexibility for future quality improvements. The user interface enhancements enable research-grade quality control with complete version preservation and granular update control.

Implementation follows established patterns from Phase 3.2A embedded service success and integrates seamlessly with existing common services and configuration management frameworks.

**Next Steps**: Technical specification development for specific implementation phases, database migration planning, and UI mockup creation per BuildPlan.md task authorization process.