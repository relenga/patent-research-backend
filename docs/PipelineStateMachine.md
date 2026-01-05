# Pipeline State Machine — AUTHORITATIVE STATE DEFINITIONS

**Authority**: SINGLE AUTHORITY for all pipeline state definitions and transition rules
**Execution Implementation**: [PipelineExecutionSpec.md](design/phase-3-specs/PipelineExecutionSpec.md) (execution mechanics)
**Implementation Tasks**: [BuildPlan.md P3.2](BuildPlan.md#p32-pipeline-state-machine-execution) (execution requirements)

## Document Authority

This document defines **what pipeline states exist and when transitions occur**, providing the business logic that governs all pipeline execution. Other documents implement these rules:

- **PipelineExecutionSpec.md**: HOW to technically implement these state transitions  
- **BuildPlan.md P3.2**: WHAT implementation tasks are required
- **HITLTaskSpec.md**: HOW human tasks integrate with pipeline states
- **DatabaseSchemaSpec.md**: Database schema supporting these state definitions

## Purpose

This document defines the **document processing pipeline and state machine** governing how documents, text, images, and diagrams flow through the system.

It specifies:
- Lifecycle states
- Transition rules
- Failure handling
- Human-in-the-Loop (HITL) escalation
- Explicit handling of **images and diagrams as first-class entities**

This document defines **structure and behavior expectations only**.  
Implementation details belong to Phase 3+.

---

## Design Principles

1. **Deterministic Progression**
   - Every entity progresses through explicit states
   - No implicit transitions

2. **Separation of Concerns**
   - Documents, text blocks, images, and diagrams have distinct lifecycles
   - Shared lineage links them

3. **Image/Diagram Elevation**
   - Images are not secondary artifacts
   - Diagrams provide evidence preparation for patent analysis and product mapping

4. **Reuse Over Redundancy**
   - Identical diagrams should share canonical descriptions
   - Duplicate effort is avoided

5. **Human Escalation Where Necessary**
   - OCR and diagram interpretation require HITL
   - Decisions are auditable and repeatable

---

## Entity Types Governed by the Pipeline

| Entity Type | Description |
|------------|------------|
| Document | Source artifact (patent, OA, product doc, legal text) |
| TextBlock | Extracted textual content |
| Image | Raw embedded image (figure, diagram, photo) |
| Diagram | Interpreted technical image with semantic meaning |
| DiagramDescription | Canonical textual explanation of a diagram |
| LineageRecord | Provenance linkage between entities |
| Task | Human review or intervention request |

---

## High-Level Pipeline Stages

1. Acquisition
2. Normalization
3. Extraction
4. Image Isolation
5. Duplicate Detection
6. Interpretation (OCR + Vision)
7. Validation (Automated + HITL)
8. Canonicalization
9. Corpus Assignment
10. Ready for Analysis

Manual uploads and research-agent acquisitions enter the pipeline identically after registration. All downstream processing is uniform and source-agnostic.


---

## Document State Machine

### Document States

| State | Meaning |
|-----|--------|
| INGESTED | Document identified and registered |
| NORMALIZED | Format standardized |
| TEXT_EXTRACTED | Text successfully extracted |
| IMAGES_EXTRACTED | Images isolated |
| PARTIALLY_PROCESSED | Some entities pending review (70-89% completion) |
| READY | All required components complete (≥90% completion) |
| BLOCKED | Awaiting HITL or external decision |
| FAILED | Processing failed irrecoverably |

### Phase 3.2A Document Completion Logic

**Document completion percentage calculation:**
Completion = (READY + DUPLICATE_LINKED + IGNORED) / Total Images

**State transitions with explicit thresholds:**

**READY state requires ALL conditions:**
- TEXT_EXTRACTED = complete
- Image completion ≥ 90% AND critical images = 100% complete
- No BLOCKED images remaining (or explicit override)
- Processing time < 24-hour timeout (simplified)

**PARTIALLY_PROCESSED state triggers when:**
- Image completion ≥ 70% AND < 90%
- Critical images = 100% complete
- Non-critical images may remain in processing

**BLOCKED state triggers when:**
- Any critical image in BLOCKED state
- Image completion < 70% after timeout
- Manual override required for completion

**Manual Override Capability:**
- Project managers can force READY state with mandatory override_reason field
- Override audit includes: timestamp, user, reason, completion_percentage
- Override does not bypass corpus isolation or safety checks

---

## Image / Diagram State Machine (Elevated)

### Image States

| State | Meaning |
|------|--------|
| IMAGE_EXTRACTED | Image isolated from document |
| HASHED | Perceptual/hash fingerprint generated |
| DUPLICATE_CHECKED | Compared against canonical registry |
| DUPLICATE_LINKED | Matched to existing canonical image |
| UNIQUE | No prior match found |
| IGNORED | Explicitly marked as non-semantic |
| NEEDS_INTERPRETATION | Requires OCR / vision analysis |
| INTERPRETED | Textual/structural meaning extracted |
| NEEDS_HITL | Requires human confirmation |
| CANONICALIZED | Approved diagram description exists |
| REPROCESSING | Administrative reanalysis of existing processed entity |
| READY | Eligible for downstream reasoning (corpus constraints apply) |

### Phase 3.2A Diagram Classification System (3-Type)

**diagram_type field values:**

**critical** (title/method diagrams):
- interpretation_required: TRUE
- completion_weight: 2.0 (counts double toward completion)
- hitl_priority: CRITICAL
- Must complete for document READY state

**supporting** (detail diagrams):
- interpretation_required: TRUE  
- completion_weight: 1.0
- hitl_priority: STANDARD
- Standard processing priority

**decorative** (logos, borders):
- interpretation_required: FALSE
- completion_weight: 0.1
- hitl_priority: LOW
- May be auto-ignored

**Automatic Classification Rules:**
- Images with "Figure 1", "Fig 1" → supporting
- Images containing "System", "Method", "Process" → critical
- Images on page 1 or containing title text → critical  
- Images with company logos or standard borders → decorative
- Ambiguous classifications trigger HITL task for manual review

---

## Duplicate & Reuse Handling (Critical)

### Phase 3.2A Similarity Thresholds (3-Level System)

**Duplicate Detection Rules with explicit thresholds:**

Every image produces:
- Perceptual hash
- Structural embedding  
- Comparison against **Diagram Canonical Registry**

**Similarity-based outcomes:**

**Duplicate (≥95% similarity):**
- Action: Immediate DUPLICATE_LINKED state
- Processing: Auto-link to canonical, skip OCR/vision processing
- HITL: No human review required
- Audit: Log canonical reference with confidence score

**Near-duplicate (80-94% similarity):**
- Action: BLOCKED state, create HITL task
- Processing: Suspend until human decision
- HITL: "Approve as duplicate" or "Process as unique"
- Audit: Log similarity score and human rationale

**Unique (<80% similarity):**
- Action: Standard processing pipeline
- Processing: Full OCR/vision/interpretation required
- HITL: Standard interpretation review
- Audit: Log as unique with processing results

### Processing Outcomes

| Similarity Level | Threshold | Action |
|-----------------|-----------|--------|
| Duplicate | ≥95% | Link to existing canonical diagram |
| Near-duplicate | 80-94% | HITL decision required |
| Unique | <80% | New diagram interpretation required |
| Non-semantic | Any | Mark as IGNORED (decorative) |

---

## Ignore Semantics (Required)

Images may be explicitly marked as **IGNORED** for reasons including:

- Logos
- Advertisements
- Decorative images
- Non-technical photos
- Repeated boilerplate figures

Ignored images:
- Remain in lineage
- Are excluded from evidence preparation
- Are auditable decisions

### Ignored Image Handling (Explicit Rules)

Images marked as **IGNORED**:

- Are stored with a required `ignored_reason`
- Remain fully represented in lineage and audit trails
- Are excluded from:
  - RAG retrieval
  - Evidence preparation for claim analysis
  - Diagram-to-claim mapping
- Remain visible in:
  - Provenance reports
  - Diagram registries
  - HITL review history

Ignored images are never deleted and never silently excluded.


---

## Diagram Interpretation Flow

1. OCR (text inside diagram)
2. Vision model structure analysis
3. Caption + reference extraction
4. Semantic description draft
5. Confidence scoring

### Escalation Conditions (HITL)

- Low OCR confidence
- Ambiguous technical meaning
- Potential claim-critical diagram
- Near-duplicate uncertainty

---

## Human-in-the-Loop Tasks

| Task Type | Trigger |
|---------|--------|
| Verify OCR | Low confidence text |
| Approve duplicate | Near-match detected |
| Write diagram description | Complex technical figure |
| Approve canonicalization | Diagram reused across corpus |
| Mark ignore | Non-semantic image |

All HITL actions:
- Create auditable Task records
- Require explicit human decision
- Feed back into pipeline state

---

## State Transition Rules (AUTHORITATIVE)

**Implementation Authority**: PipelineExecutionSpec.md must implement these exact transition rules

### Document State Transitions
- INGESTED → NORMALIZED (automatic)
- NORMALIZED → TEXT_EXTRACTED (automatic)
- TEXT_EXTRACTED → IMAGES_EXTRACTED (automatic)
- IMAGES_EXTRACTED → PARTIALLY_PROCESSED (if images pending)
- IMAGES_EXTRACTED → READY (if no images or all images complete)
- PARTIALLY_PROCESSED → READY (when all dependencies complete)
- ANY → BLOCKED (awaiting HITL)
- ANY → FAILED (fatal error)

### Image/Diagram State Transitions
- IMAGE_EXTRACTED → HASHED (automatic)
- HASHED → DUPLICATE_CHECKED (automatic)
- DUPLICATE_CHECKED → DUPLICATE_LINKED (if identical match)
- DUPLICATE_CHECKED → UNIQUE (if no match)
- DUPLICATE_CHECKED → BLOCKED (if near-duplicate, requires HITL)
- UNIQUE → NEEDS_INTERPRETATION (automatic)
- NEEDS_INTERPRETATION → INTERPRETED (OCR + vision processing)
- INTERPRETED → CANONICALIZED (automatic or HITL approval)
- CANONICALIZED → READY (automatic)
- ANY → IGNORED (human decision)
- ANY → FAILED (fatal error)

**Trigger Types** (implemented by PipelineExecutionSpec.md):
- **Automatic**: Agent completion or business rule evaluation
- **HITL**: Human task completion triggers transition
- **Manual**: Administrative override
- **External**: API calls or system events

## State Transition Rules (Examples)

- IMAGE_EXTRACTED → HASHED
- HASHED → DUPLICATE_CHECKED
- DUPLICATE_CHECKED → DUPLICATE_LINKED
- DUPLICATE_CHECKED → UNIQUE
- UNIQUE → NEEDS_INTERPRETATION
- NEEDS_INTERPRETATION → INTERPRETED
- INTERPRETED → CANONICALIZED
- CANONICALIZED → READY
- ANY → BLOCKED (awaiting HITL)
- ANY → FAILED (fatal error)

---

## Failure & Recovery Semantics

- Failures are localized to entities
- Document may proceed while images block
- Retry allowed only for:
  - OCR
  - Vision interpretation
- Fatal failures require human resolution

---

## REPROCESSING State Specification (Phase 3.2B)

### Authority Approval
**Status**: APPROVED - January 5, 2026  
**Scope**: Single-user system with unified image handling  
**Integration**: Authorized for immediate development

### Entity Scope

**REPROCESSING State applies to:**
- **Documents**: Full document reanalysis (text + images)
- **Images**: Individual image reinterpretation  
- **DiagramDescriptions**: Canonical description updates

**REPROCESSING State does NOT apply to:**
- TextBlocks: Text extraction is deterministic
- LineageRecords: Audit trails are immutable
- Tasks: HITL tasks have their own lifecycle

### Preservation vs Regeneration Logic

**Preserved During Reprocessing:**
- Original artifact files (PDFs, images) - never modified
- Complete audit trail and provenance records
- Existing canonical descriptions (until explicitly replaced)
- Document metadata (title, source, ingestion timestamp)

**Regenerated During Reprocessing:**
- Text extraction output (if document reprocessing)
- Image analysis results (OCR, vision model output)
- Diagram descriptions (if image reprocessing)
- State transition audit events

**Versioning Approach:**
- Original results preserved with _archived suffix
- New results replace current active versions
- Provenance records link original → reprocessed versions

### State Transition Rules

**Valid Entry Paths to REPROCESSING:**
- READY → REPROCESSING (administrative request)
- CANONICALIZED → REPROCESSING (description update)
- DUPLICATE_LINKED → REPROCESSING (canonical reference change)
- BLOCKED → REPROCESSING (after HITL resolution with reprocessing flag)

**Valid Exit Paths from REPROCESSING:**
- REPROCESSING → READY (successful reprocessing completion)
- REPROCESSING → FAILED (reprocessing failed, preserved original)
- REPROCESSING → BLOCKED (reprocessing requires human intervention)

**Forbidden Transitions:**
- REPROCESSING → INGESTED (would lose provenance)
- FAILED → REPROCESSING (use administrative override instead)
- Any state → REPROCESSING without explicit trigger event

### Completion Logic

**Successful Completion (REPROCESSING → READY):**
- All processing stages completed successfully
- New results pass validation checks
- Provenance links established to original versions
- Audit trail shows complete reprocessing workflow

**Timeout and Escalation:**
- REPROCESSING timeout: 24 hours for documents, 4 hours for individual images
- After timeout: Administrative notification, option to extend or abort
- Abort action: Restore original results, mark REPROCESSING → FAILED

### Concurrent Processing Logic

**Resource Allocation:**
- REPROCESSING entities get standard priority (not higher than new content)
- Maximum 20% of processing capacity reserved for reprocessing
- Reprocessing suspended if new document queue > 10 items

**Conflict Resolution:**
- If original entity in REPROCESSING, new duplicates link to archived canonical
- If canonical entity in REPROCESSING, duplicates remain BLOCKED until completion

### Unified Image Handling Integration

**REPROCESSING + Unified Image Approach:**
- All visual content follows same three options: describe/ignore/duplicate
- REPROCESSING respects original classification but allows reclassification
- Reprocessed images can change from IGNORED → CANONICALIZED if analysis improves
- Duplicate relationships preserved but can be updated if canonical changes

**Canonical Registry Integration:**
- REPROCESSING of canonical descriptions updates all linked duplicates
- Duplicate images can be reprocessed to become canonical if original quality poor
- Registry maintains version history for reprocessed canonical descriptions

### Audit Requirements

**Mandatory Audit Events:**
- REPROCESSING trigger with reason and authorization
- Original state preservation with archive timestamp
- Processing stage completions during reprocessing
- Final state transition with success/failure indication

**Provenance Linking:**
- Reprocessed entities maintain derived_from links to original versions
- Original→reprocessed relationship captured in provenance graph
- Human decisions during reprocessing captured with rationale

### Cascade Behavior Specification

**Authority Decision**: Immediate Cascade (Option A) - APPROVED January 5, 2026

**Cascade Timing**: IMMEDIATE

**On REPROCESSING State Entry:**
- Delete all vector embeddings for entity_id
- Remove all search index entries for entity_id  
- Clear RAG retrieval cache for entity_id
- Mark analytics records as under_reprocessing
- Log cascade deletion counts for audit

**On REPROCESSING State Exit:**
- Generate new vector embeddings
- Rebuild search index entries
- Update RAG retrieval availability
- Finalize analytics records with reprocessing flag
- Log cascade rebuild completion for audit

**Vector Database Behavior:**
- Immediate deletion of all embeddings when entering REPROCESSING
- Embedding deletion logged with counts and timestamps
- New embeddings generated during normal processing pipeline
- No storage bloat from accumulated old embeddings

**RAG System Integration:**
- Reprocessing entities NOT AVAILABLE for RAG retrieval during processing
- Query results exclude reprocessing entities completely
- No mixed old/new content in single retrieval context

**Rollback Requirements:**
- If REPROCESSING → FAILED: restore archived embeddings immediately
- All deleted embeddings archived (not permanently destroyed) during cascade
- Rollback completion target: <1 hour for documents, <15 minutes for images

**Performance Targets:**
- Immediate deletion: <30 seconds for documents, <10 seconds for images
- Rebuilding completion: <5 minutes for documents, <2 minutes for images
- Maximum 10% of system resources for cascade operations

---

## Pipeline Guarantees

When an entity reaches **READY**:
- All dependencies are satisfied
- Provenance links exist
- Decisions are auditable
- Reuse is maximized
- No silent assumptions remain

**Important:** Pipeline readiness does not grant claim-support authority. Downstream agents must obey corpus usage rules defined in CorpusModel.md.

---

## Relationship to Other Documents

| Document | Relationship |
|--------|-------------|
| PRD.md | Defines *what* is required |
| SystemNarrative.md | Explains *why* |
| CorpusModel.md | Defines *where knowledge may be used* |
| AgentResponsibilities.md | Defines *who acts* |
| ProvenanceAudit.md | Defines *how decisions are proven* |

---

## Phase Alignment

- Phase 2: State definitions only (this document)
- Phase 3+: Execution logic, storage, enforcement

---

## Summary

This pipeline treats **images and diagrams as legally significant evidence**, not secondary artifacts.

It ensures:
- Diagram reuse across patents
- Explicit ignore decisions
- Human oversight where required
- Strong claim defensibility

This is essential to achieving the system’s litigation and patent strategy goals.
