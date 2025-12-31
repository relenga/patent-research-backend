# OCR and Diagram Processing Specification

**Status**: APPROVED - OCR + Human Correction Approach Confirmed (Dec 30, 2025)  
**Authority**: Technical implementation guidance for P3.4 OCR and Image Processing Pipeline  
**Cross-References**: [PipelineStateMachine.md](../PipelineStateMachine.md) (image states), [CorpusModel.md](../CorpusModel.md) (diagram corpus rules), [DataFlowDiagram.md](../DataFlowDiagram.md) (diagram flows), [HITLTaskSpec.md](./HITLTaskSpec.md) (human review integration)

## Authority Relationship

**PipelineStateMachine.md defines WHAT states** (image/diagram lifecycle and transitions)  
**This specification defines HOW** (technical OCR processing and diagram handling)  
**CorpusModel.md defines BUSINESS RULES** (diagram corpus inheritance and IGNORED handling)  
**BuildPlan.md P3.4 defines EXECUTION** (implementation tasks and acceptance criteria)

## Purpose

Defines technical implementation of OCR processing, diagram extraction, canonicalization, duplicate detection, and human-in-the-loop diagram processing for patent intelligence pipeline.

## Required Content (Minimum Specification)

### OCR Processing Pipeline

#### Image Extraction & Preparation
- **Source Detection**: Embedded images, figures, scanned pages identification
- **Format Standardization**: Convert to consistent format for OCR processing
- **Quality Assessment**: Resolution, contrast, clarity evaluation for OCR suitability
- **Preprocessing**: Noise reduction, contrast enhancement, rotation correction
- **Region Detection**: Text regions, diagram regions, decorative elements identification

#### OCR Engine Integration
- **Primary Engine**: Tesseract OCR with language configuration (English + patent-specific)
- **Quality Scoring**: Confidence metrics for extracted text accuracy
- **Alternative Processing**: Fallback OCR strategies for low-confidence results
- **Character Recognition**: Patent-specific terminology and notation handling
- **Layout Preservation**: Spatial relationships between text elements

#### Text Post-Processing
- **Confidence Filtering**: Low-confidence text flagged for human review
- **Patent Terminology**: Specialized vocabulary recognition and correction
- **Reference Extraction**: Figure numbers, claim references, part labels
- **Formatting Cleanup**: Whitespace normalization, line break handling
- **Quality Metrics**: Overall OCR success rate and confidence scoring

### Diagram Extraction & Classification

#### Image Classification
- **Technical Diagrams**: Engineering drawings, flowcharts, system architectures
- **Decorative Elements**: Logos, borders, header/footer graphics
- **Non-Technical Images**: Photos, marketing materials, irrelevant graphics
- **Patent Drawings**: Formal patent figure drawings with reference numerals
- **Classification Confidence**: Automated classification with uncertainty handling

#### Diagram Processing
- **Reference Numeral Extraction**: Identify and catalog part numbers and labels
- **Caption Association**: Link figure captions to corresponding diagrams
- **Spatial Analysis**: Component relationships and layout understanding
- **Technical Content Detection**: Distinguish technical vs decorative content
- **Complexity Assessment**: Diagram complexity for processing strategy selection

### Duplicate Detection & Canonicalization

#### Perceptual Hashing
- **Hash Generation**: Perceptual hashes for duplicate detection (pHash, dHash)
- **Similarity Thresholds**: Configurable thresholds for identical vs similar detection
- **Hash Storage**: Efficient hash storage and comparison infrastructure
- **Performance Optimization**: Fast similarity search across large diagram collections

#### Duplicate Resolution Strategies
- **Identical Matches**: Automatic linking to canonical diagram descriptions
- **Near Duplicates**: HITL escalation for human duplicate determination
- **Unique Diagrams**: New canonical description generation process
- **Cross-Document Duplicates**: Handle diagrams appearing in multiple documents

#### Canonical Description Management
- **Description Authority**: First-processed diagram establishes canonical description
- **Reuse Inheritance**: Subsequent identical diagrams inherit description and corpus constraints
- **Most Restrictive Rule**: Cross-corpus duplicates inherit most restrictive corpus limitations
- **Lineage Tracking**: Full provenance chain for all diagram reuse decisions

### IGNORE Handling (Comprehensive)

#### IGNORE Decision Process
- **Automatic Classification**: Clear decorative/non-technical elements
- **Human Decision Required**: Ambiguous or potentially technical content
- **Required Rationale**: Human justification mandatory for IGNORE decisions
- **Administrative Override**: Project manager authority for IGNORE reclassification

#### IGNORED Diagram Storage
- **Full Preservation**: Complete diagram data and metadata retained
- **Audit Trail**: IGNORE decision with timestamp, rationale, human identity
- **Immutable Decisions**: IGNORE status cannot be silently changed
- **Lineage Maintenance**: IGNORED diagrams remain in provenance chains

#### Retrieval Exclusion Rules
- **Default Exclusion**: IGNORED diagrams excluded from normal retrieval operations
- **Explicit Inclusion**: Special queries may include IGNORED diagrams for audit
- **Evidence Preparation**: IGNORED diagrams never included in claim evidence bundles
- **Audit Visibility**: IGNORED diagrams visible in audit reports and lineage views

## Configurable Similarity Thresholds

### Diagram Similarity Controls

#### Configuration-Driven Thresholds
- **Hash similarity thresholds** are configuration-driven via .env / BaseSettings, not hardcoded
- **Embedding similarity thresholds** are configuration-driven via .env / BaseSettings, not hardcoded
- **All threshold values** sourced from environment variables with validation
- **Runtime Configuration**: Thresholds loaded at application startup from Pydantic BaseSettings

#### Threshold Configuration Variables
- `DIAGRAM_HASH_THRESHOLD`: Perceptual hash similarity for identical detection
- `DIAGRAM_SIMILARITY_THRESHOLD`: Embedding similarity for near-duplicate detection
- `OCR_CONFIDENCE_THRESHOLD`: Minimum OCR confidence for text extraction
- **Default Values**: Reasonable defaults provided in configuration schema

### UI Visibility

#### Threshold Display and Control
- **Similarity threshold values are displayed in the UI** for human reviewer visibility
- **Threshold values are editable by the human reviewer** through configuration interface
- **Threshold changes are logged as configuration change audit events** with timestamp and rationale
- **Real-time Validation**: UI validates threshold changes before application

#### Configuration Change Audit
- **All threshold modifications** logged with human identity and timestamp
- **Rationale Required**: Human justification mandatory for threshold changes
- **Change History**: Complete audit trail of all threshold value changes
- **Rollback Capability**: Previous threshold values preserved for potential rollback

### Enforcement

#### Retroactive Processing Rules
- **Changing thresholds does not retroactively alter prior canonicalization decisions** unless explicitly reprocessed
- **Historical Decisions**: Existing diagram relationships preserved with original threshold values
- **Explicit Reprocessing**: Human can trigger reprocessing with new thresholds if required
- **Audit Trail Preservation**: Original decisions and reprocessing events both logged

### HITL Escalation Framework

#### Escalation Triggers
- **Low OCR Confidence**: Text extraction confidence below threshold
- **Ambiguous Classification**: Uncertain technical vs decorative classification
- **Near Duplicate Uncertainty**: Similar but not identical diagrams requiring human judgment
- **Complex Technical Content**: Diagrams requiring domain expertise for interpretation

#### Evidence Bundle Assembly
- **Diagram Context**: Source document, page location, surrounding text
- **OCR Results**: Extracted text with confidence scores and alternatives
- **Classification Data**: Automated classification results with uncertainty metrics
- **Comparison Data**: Similar diagrams for duplicate determination context

#### Human Decision Integration
- **Task Creation**: Structured HITL tasks per HITLTaskSpec.md requirements
- **Decision Recording**: Human choices with rationale and timestamp
- **Quality Feedback**: Human corrections to improve automated processing
- **Escalation Routing**: Complex decisions to appropriate human reviewers

### State Transition Implementation

#### Automatic Transitions (per PipelineStateMachine.md)
- **IMAGE_EXTRACTED → HASHED**: Automatic perceptual hash generation
- **HASHED → DUPLICATE_CHECKED**: Automatic similarity comparison
- **DUPLICATE_CHECKED → DUPLICATE_LINKED**: Identical match found
- **DUPLICATE_CHECKED → UNIQUE**: No similar diagrams found
- **UNIQUE → NEEDS_INTERPRETATION**: Automatic OCR processing trigger

#### HITL-Dependent Transitions
- **DUPLICATE_CHECKED → BLOCKED**: Near-duplicate requires human judgment
- **NEEDS_INTERPRETATION → BLOCKED**: Low OCR confidence or complex content
- **BLOCKED → INTERPRETED**: Human decision completes processing
- **INTERPRETED → CANONICALIZED**: Human approval of diagram description

#### Terminal States
- **CANONICALIZED → READY**: Diagram available for downstream processing
- **ANY → IGNORED**: Human decision to exclude from processing
- **ANY → FAILED**: Irrecoverable processing errors

## Design Decisions (APPROVED)

### OCR + Human Correction Approach
- [x] **No Full Automation**: All diagram descriptions require human validation
- [x] **OCR Assistance Only**: Automated text extraction supports human review
- [x] **Quality Thresholds**: Configurable confidence thresholds for escalation
- [x] **Human Authority**: Final diagram interpretation decisions are human-made

### Processing Strategy
- [x] **Synchronous OCR**: Direct OCR processing without background queues
- [x] **Database Persistence**: All diagram metadata and decisions in PostgreSQL
- [x] **Local Processing**: No external OCR services or cloud dependencies
- [x] **Audit Completeness**: Every processing step logged with full provenance

## Implementation Guidance

### Tesseract Integration
- Tesseract installation and configuration for patent document processing
- Language model optimization for technical terminology
- Custom configuration for patent figure layouts and formatting
- Error handling for Tesseract processing failures

### Image Processing Pipeline
- PIL/Pillow for image manipulation and format conversion
- OpenCV integration for advanced image preprocessing
- Performance optimization for large diagram collections
- Memory management for high-resolution patent diagrams

### Database Schema Integration
- Diagram metadata tables with hash storage and comparison indices
- IGNORED diagram tracking with rationale and audit fields
- Canonical description linking with corpus constraint inheritance
- Performance indices for similarity search and duplicate detection

## Acceptance Criteria

- [ ] OCR processing extracts text from patent diagrams with quality scoring
- [ ] Perceptual hashing enables accurate duplicate detection across documents
- [ ] IGNORED diagrams stored with audit trail but excluded from retrieval
- [ ] Canonical diagram descriptions inherited correctly across duplicates
- [ ] Most restrictive corpus rule applied to cross-corpus duplicate diagrams
- [ ] HITL tasks generated for low-confidence OCR and near-duplicate resolution
- [ ] Human diagram decisions integrated with pipeline state transitions
- [ ] All diagram processing steps logged with complete provenance
- [ ] No external OCR services or cloud processing dependencies
- [ ] State transitions comply exactly with PipelineStateMachine.md rules

---

**Status**: SPECIFICATION COMPLETE - Ready for P3.4 Implementation  
**Approved**: OCR + Human Correction + Local Processing (Dec 30, 2025)