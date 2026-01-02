# State Machine Coordination Enhancement Proposal

**⚠️ DESIGN PROPOSAL ONLY - NOT APPROVED FOR IMPLEMENTATION ⚠️**

**Status**: PROPOSAL UNDER REVIEW  
**Authority**: NONE - This document has no implementation authority  
**Purpose**: Design proposal for PM and stakeholder review only  
**Implementation**: FORBIDDEN until explicit PM approval received

---

## Executive Summary

This refined proposal addresses critical coordination gaps in the current pipeline state machine design for handling complex documents with 15-20+ diagrams. The solution establishes explicit thresholds, formal classification schemas, and precise implementation details while leveraging referenced image optimization benefits.

## Issues Identified

### Document Completion Logic Ambiguity

- Current completion calculation lacks clear thresholds for determining when documents transition from PARTIALLY_PROCESSED to READY
- No explicit definition of what constitutes "READY" state for documents with mixed image types

### Critical Image Classification Vagueness

- Definition of "title/method diagrams" needs formalization
- Missing diagram classification schema to determine which images must be interpreted vs. referenced

### Near-Duplicate Decision Thresholds

- No defined perceptual hash similarity thresholds for distinguishing duplicates from near-duplicates
- Processing priority for near-duplicates not clearly specified

### Low-Quality Image Handling

- Missing automatic fallback logic for images with very low OCR/vision confidence
- No mechanism to prevent unnecessary HITL for uninterpretable images

### Missing Reprocessing State

- No state for handling documents or images that need reprocessing due to overrides or model updates

### Corpus Isolation Enforcement

- Cross-corpus reference blocking lacks specific implementation details
- No clear mechanism for auditing corpus boundary violations

### Emergency Override Logging

- Override audit records lack required fields for complete traceability
- No mechanism to enforce mandatory override reasons

## Key Recommendations Applied

### Add Clear Completion Thresholds

- Define specific percentage thresholds (e.g., 90% for READY) and timeout conditions
- Clarify document state transition criteria based on image completion status

### Implement Diagram Type Schema

- Add diagram_type field with values like title, method, supporting, decorative
- Define interpretation requirements based on diagram type

### Establish Similarity Thresholds

- Set perceptual hash similarity thresholds (e.g., 95% for duplicates, 80-95% for near-duplicates)
- Define processing priority levels for different similarity categories

### Add Automatic Fallback Logic

- Implement auto-ignore for images with OCR confidence < 20% and vision confidence < 30%
- Prevent unnecessary HITL for uninterpretable content

### Introduce Reprocessing State

- Add REPROCESSING state to handle document/image reprocessing scenarios
- Enable state transitions from READY or BLOCKED based on need

### Strengthen Corpus Enforcement

- Add corpus_id validation for canonical descriptions
- Implement audit logging for cross-corpus reference attempts

### Enhance Override Logging

- Add override_reason field to all audit records
- Enforce mandatory override reason capture for all administrative actions

---

## 1. Document Completion Logic with Explicit Thresholds

### Precise Completion Calculation

Document completion percentage = (READY + DUPLICATE_LINKED + IGNORED) / Total Images

Document state transitions with explicit thresholds:

**READY state requires ALL conditions:**
- TEXT_EXTRACTED = complete
- Image completion ≥ 90% AND critical images = 100% complete
- No BLOCKED images remaining (or explicit override)
- Processing time < maximum timeout for document class

**PARTIALLY_PROCESSED state triggers when:**
- Image completion ≥ 70% AND < 90%
- Critical images = 100% complete
- Non-critical images may remain in processing

**BLOCKED state triggers when:**
- Any critical image in BLOCKED state
- Image completion < 70% after timeout
- Cross-corpus violation detected

### Document Class Timeout Matrix

**Simple documents (≤5 images):**
- Maximum processing time: 2 hours
- PARTIALLY_PROCESSED threshold: 1.5 hours
- Force completion threshold: 4 hours

**Standard documents (6-15 images):**
- Maximum processing time: 8 hours
- PARTIALLY_PROCESSED threshold: 6 hours  
- Force completion threshold: 24 hours

**Complex documents (16+ images):**
- Maximum processing time: 24 hours
- PARTIALLY_PROCESSED threshold: 18 hours
- Force completion threshold: 72 hours

## 2. Formal Diagram Classification Schema

### Diagram Type Enumeration

Add diagram_type field with specific values:

**title**: Document title page diagrams
- interpretation_required: TRUE
- can_be_referenced: FALSE
- completion_weight: 2.0 (counts double toward completion)
- hitl_priority: CRITICAL

**method**: System/process flow diagrams
- interpretation_required: TRUE
- can_be_referenced: TRUE (if exact match)
- completion_weight: 1.5
- hitl_priority: HIGH

**supporting**: Detail/component diagrams
- interpretation_required: TRUE
- can_be_referenced: TRUE
- completion_weight: 1.0
- hitl_priority: STANDARD

**decorative**: Logos, borders, non-technical images
- interpretation_required: FALSE
- can_be_referenced: TRUE
- completion_weight: 0.1
- hitl_priority: LOW

### Classification Rules

**Automatic classification triggers:**
- Images with text "Figure 1", "Fig 1" → supporting
- Images containing "System", "Method", "Process" → method  
- Images on page 1 or containing title text → title
- Images with company logos or standard borders → decorative

**Manual classification override:**
- HITL task created for ambiguous classifications
- Reviewer can reclassify with mandatory rationale
- Reclassification triggers reprocessing if needed

## 3. Precise Similarity Thresholds and Processing Priority

### Perceptual Hash Similarity Matrix

**Exact duplicate (similarity ≥ 98%):**
- Action: Immediate DUPLICATE_LINKED state
- Processing: Skip all OCR/vision processing
- HITL: No human review required
- Audit: Log canonical reference with confidence score

**Near-duplicate (similarity 85-97%):**
- Action: BLOCKED state, create HITL task
- Processing: Suspend until human decision
- HITL: "Approve as duplicate" or "Process as unique"
- Audit: Log similarity score and human rationale

**Possible duplicate (similarity 70-84%):**
- Action: Continue processing, flag for optional review
- Processing: Full OCR/vision processing
- HITL: Optional batch review for similar patterns
- Audit: Log similarity for pattern learning

**Unique (similarity < 70%):**
- Action: Standard processing pipeline
- Processing: Full OCR/vision/interpretation required
- HITL: Standard interpretation review
- Audit: Log as unique with processing results

### Processing Priority Queue

**Priority Level 1 (immediate processing):**
- Exact duplicates (instant linking)
- Title diagrams from high-priority documents
- Critical diagrams blocking document completion

**Priority Level 2 (standard processing):**
- Method diagrams from active documents
- Supporting diagrams with processing capacity
- Reprocessing tasks from administrative overrides

**Priority Level 3 (batch processing):**
- Decorative image classification
- Near-duplicate confirmations
- Pattern learning optimization tasks

## 4. Automatic Fallback Logic for Low-Quality Images

### Quality Confidence Thresholds

**OCR quality assessment:**
- High confidence (≥ 80%): Proceed to interpretation
- Medium confidence (50-79%): Flag for HITL review
- Low confidence (20-49%): Auto-generate warning, proceed with caution
- Very low confidence (< 20%): Auto-ignore with audit trail

**Vision model confidence:**
- High confidence (≥ 70%): Accept interpretation automatically
- Medium confidence (40-69%): Require HITL confirmation  
- Low confidence (< 40%): Auto-ignore or force manual description

### Automatic Ignore Conditions

Images automatically marked IGNORED when ALL conditions met:
- OCR confidence < 20% AND vision confidence < 30%
- File size < 10KB (likely low-resolution)
- Aspect ratio > 10:1 or < 1:10 (likely decorative borders)
- Classified as decorative AND similarity to known decorative > 90%

Automatic ignore generates audit record:
- ignore_reason: "auto_low_quality"
- confidence_scores: [ocr_score, vision_score]
- fallback_applied: TRUE
- reviewer_override_available: TRUE

## 5. Reprocessing State for Updates and Overrides

### New REPROCESSING State

**REPROCESSING state triggers:**
- Administrative override requiring document reanalysis
- Model updates affecting existing interpretations
- Corpus reclassification requiring validation
- Quality improvements necessitating reanalysis

**State transitions to REPROCESSING:**
- From READY: When model updates or overrides require reanalysis
- From BLOCKED: When HITL decisions change processing requirements
- From FAILED: When administrative intervention enables retry

**REPROCESSING workflow:**
1. Preserve original processing results with timestamp
2. Create reprocessing audit record with trigger reason
3. Reset affected images to appropriate processing state
4. Maintain original canonical references unless explicitly changed
5. Generate comparative analysis between old and new results

### Reprocessing Priority Management

**Reprocessing requests prioritized by:**
1. Administrative overrides with urgent flag
2. Corpus violation corrections
3. Model updates affecting legal accuracy
4. Quality improvements for critical documents

**Resource allocation for reprocessing:**
- Maximum 20% of processing capacity reserved for reprocessing
- Reprocessing requests queued with estimated completion time
- Bulk reprocessing scheduled during low-activity periods

## 6. Strengthened Corpus Isolation Enforcement

### Cross-Corpus Reference Validation

**Canonical description corpus validation:**
- Every DUPLICATE_LINKED assignment validates corpus compatibility
- Cross-corpus references blocked with specific error codes
- Audit trail captures attempted violations with full context

**Corpus compatibility matrix:**
- Open Patent ↔ Open Patent: ALLOWED
- Adversarial ↔ Adversarial: ALLOWED  
- Product ↔ Product: ALLOWED
- Cross-corpus references: BLOCKED with audit

### Violation Audit Implementation

**Corpus violation audit record contains:**
- violation_type: "cross_corpus_reference_attempt"
- source_corpus: Original document corpus
- target_corpus: Attempted reference corpus  
- canonical_id: Blocked canonical description ID
- blocking_rule: Specific CorpusModel.md rule violated
- timestamp: Violation attempt timestamp
- resolution_action: "blocked" or "override_approved"

**Administrative override for corpus violations:**
- Requires explicit override_reason
- Must reference specific business justification
- Generates high-priority audit flag
- Requires PM-level approval for cross-corpus exceptions

## 7. Enhanced Override Logging with Mandatory Fields

### Structured Override Audit Schema

All administrative overrides must capture:

**Required Override Fields:**
- override_id: Unique identifier
- override_type: "state_transition", "corpus_exception", "timeout_extension", "processing_bypass"
- override_reason: Mandatory text field (minimum 20 characters)
- business_justification: Reference to business requirement or emergency
- authorized_by: Administrator identity
- impact_assessment: Estimated effect on downstream processing
- rollback_available: Boolean indicating if override can be undone

**Optional Override Fields:**
- related_documents: Documents affected by override
- compliance_risk: Assessment of legal/regulatory risk
- notification_sent: List of stakeholders notified
- follow_up_required: Future actions needed

### Override Reason Validation

**Mandatory override reasons validated against approved categories:**
- "emergency_processing_deadline": Time-critical business requirement
- "corpus_exception_approved": Authorized cross-corpus access
- "quality_override": Manual quality assessment override
- "administrative_correction": Correcting system processing error
- "model_limitation_bypass": Working around current model limitations

**Invalid or generic override reasons rejected:**
- "quick fix", "temporary", "emergency" without specifics
- Reasons shorter than 20 characters
- Identical reasons used repeatedly without justification

### Override Impact Tracking

**Override impact assessment requires:**
- Estimated documents affected by override decision
- Processing time impact (positive or negative)
- Compliance risk level (low/medium/high)
- Rollback complexity and time estimate
- Stakeholder notification requirements

**High-impact overrides (affecting >10 documents or high compliance risk):**
- Require PM approval before execution
- Generate immediate stakeholder notifications  
- Create follow-up tasks for impact validation
- Mandate post-override review within 48 hours

## Implementation Validation Framework

### Acceptance Criteria with Measurable Thresholds

**Document completion accuracy:**
- 95% of documents reach READY state within timeout thresholds
- <2% of documents require administrative override for completion
- Zero documents stuck indefinitely without explicit blocking reason

**Resource utilization efficiency:**
- GPU utilization maintained between 70-85% during processing
- Processing queue depth remains below 50 items during normal operation
- Referenced image processing provides >60% time savings vs full processing

**HITL workflow effectiveness:**
- Average HITL task completion time <4 hours for standard tasks
- Bulk diagram review handles >80% of similar diagrams simultaneously
- Pattern learning reduces HITL load by >30% over 30-day period

**Audit compliance verification:**
- 100% of administrative actions generate complete audit records
- Zero corpus isolation violations in production processing
- All override records contain mandatory fields with valid reasons

### Performance Monitoring Requirements

**Real-time monitoring dashboards:**
- Document processing velocity by complexity class
- Resource utilization by processing type
- HITL queue depth and average resolution time
- Override frequency and impact assessment

**Alert thresholds:**
- Document processing stalled >50% of timeout threshold
- HITL queue depth >40 tasks
- Resource utilization >90% for >15 minutes
- Administrative override rate >5% of total processing

**Weekly performance reports:**
- Processing efficiency trends by document type
- Referenced image optimization effectiveness
- HITL workflow performance and bottlenecks  
- Audit compliance metrics and violation analysis

## Recommendation

This refined proposal provides implementable precision while maintaining the architectural advantages of referenced image optimization. All thresholds, classifications, and procedures are explicitly defined with measurable criteria, enabling confident implementation and ongoing performance validation.

The solution addresses every identified ambiguity while preserving the efficiency gains from duplicate detection and maintaining full compliance with governance, audit, and corpus isolation requirements.

**⚠️ AWAITING PM APPROVAL BEFORE ANY IMPLEMENTATION ⚠️**

---

**Document Status**: PROPOSAL ONLY - NO IMPLEMENTATION AUTHORITY