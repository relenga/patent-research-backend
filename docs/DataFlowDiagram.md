# Data Flow Diagram — AUTHORITATIVE VISUAL FLOW REFERENCE

**Authority**: SINGLE AUTHORITY for visualizing end-to-end data movement across pipeline states and corpus boundaries  
**Purpose**: Data flow visualization for correctness, auditability, and legal defensibility validation  
**Related Documents**: [SystemNarrative.md](SystemNarrative.md) (system intent), [PipelineStateMachine.md](PipelineStateMachine.md) (state definitions), [CorpusModel.md](CorpusModel.md) (corpus rules), [ProvenanceAudit.md](ProvenanceAudit.md) (audit requirements)

## Document Authority

This document defines **HOW DATA MOVES** through the system, not what the system means or why. It shows:
- Data transformation stages with explicit failure paths
- Corpus isolation enforcement points 
- Provenance capture triggers
- HITL task creation and resolution flows
- Terminal state destinations

Other documents define system intent and requirements; this document visualizes their data flow implications.

---

## End-to-End Data Flow Stages

### Stage 1: Document Acquisition & Registration

**Manual Upload Path:**
```
Human User → Upload Interface → Document Validation → Raw Artifact Store
    ↓
Document Registration (source_type=manual_upload, doc_type=assigned) → Relational DB
    ↓
Provenance Record: Manual Upload Event → Audit/Lineage Graph
```

**Research Agent Path:**
```
Research Agent → Automated Retrieval → Source Validation → Raw Artifact Store
    ↓
Document Registration (source_type=research_agent, doc_type=detected) → Relational DB
    ↓
Provenance Record: Research Agent Acquisition → Audit/Lineage Graph
```

**Failure Paths:**
- Invalid format → PROCESSING_FAILED state
- Network timeout → Retry queue → Manual escalation after 3 attempts
- Duplicate detection → Link to existing document, skip processing

---

### Stage 2: Document Normalization & Text Extraction

```
Raw Artifact Store → Format Detection → Normalization Pipeline
    ↓
PDF/XML/HTML Parser → Normalized Text + Metadata → Normalized Store
    ↓
Document State: INGESTED → NORMALIZED → TEXT_EXTRACTED
    ↓
Provenance Record: Text Extraction Completion → Audit/Lineage Graph
```

**Parallel Branch: Image/Diagram Extraction**
```
Raw Artifact Store → Image Detection → Figure Extractor
    ↓
Image Assets → Figure Registry (figure_id, fingerprint, document_link)
    ↓
Document State: TEXT_EXTRACTED → IMAGES_EXTRACTED
```

**Failure Paths:**
- Corrupted PDF → OCR fallback → HITL validation required
- Parsing failure → PROCESSING_FAILED state → Manual intervention queue
- Character encoding errors → Best-effort recovery + validation flag

---

### Stage 3: Diagram Processing & Canonicalization

**OCR Processing:**
```
Figure Registry → OCR/Caption Pipeline → Extracted Text + Regions
    ↓
Quality Score Analysis → [High Quality: Automatic] OR [Low Quality: HITL Task]
    ↓
Provenance Record: OCR Processing + Quality Score → Audit/Lineage Graph
```

**Duplicate Detection & Reuse:**
```
Figure Registry → Perceptual Hash Comparison → Duplicate Analysis
    ↓
[Identical Match: Link to Canonical] OR [Similar: HITL Review] OR [Unique: Process]
    ↓
Duplicate Decision Provenance → Audit/Lineage Graph
```

**HITL Diagram Description:**
```
Figure + OCR Text → HITL Task Creation → Human Review Queue
    ↓
Human Approval/Revision → Figure Description Artifact → Normalized Store
    ↓
[APPROVED: Canonical Description] OR [IGNORED: Archive with Audit]
    ↓
Provenance Record: Human Diagram Decision + Rationale → Audit/Lineage Graph
```

**Failure Paths:**
- OCR failure → BLOCKED state → HITL task for manual description
- Ambiguous similarity → BLOCKED state → Human duplicate determination
- Human rejection → IGNORED state → Audit trail preserved

---

### Stage 4: Corpus Assignment & Isolation Enforcement

**Corpus Classification:**
```
Document Registration Data → Document Type Analysis → Corpus Assignment
    ↓
[Patent: Open Patent Corpus] OR [Prior Art: Adversarial Corpus] OR [Product: Product Corpus]
    ↓
Corpus Enforcement Gates Applied → Access Control Rules Set
    ↓
Provenance Record: Corpus Assignment + Justification → Audit/Lineage Graph
```

**Isolation Boundaries Applied:**
- **Open Patent Corpus**: May support claim drafting ✅
- **Adversarial Corpus**: Avoidance only, never claim support ❌
- **Product Corpus**: Read-on verification only ❌

**Cross-Corpus Validation:**
```
Multi-Corpus Query Request → Corpus Rule Validation → [Allowed: Process] OR [Blocked: Audit + Error]
    ↓
All cross-corpus operations logged → Provenance Record → Audit/Lineage Graph
```

---

### Stage 5: Chunking & Embedding Pipeline

```
Normalized Store + Figure Descriptions → Content Segmentation → Chunking Pipeline
    ↓
Text Chunks + Figure-Description Chunks → Chunk Store
    ↓
Embedding Generation (per-corpus isolation) → Vector Index (corpus-segregated)
    ↓
Document State: IMAGES_EXTRACTED → READY
    ↓
Provenance Record: Processing Complete + Chunk Count → Audit/Lineage Graph
```

**Corpus-Segregated Storage:**
- Separate vector indices per corpus to enforce isolation
- Cross-corpus contamination technically impossible
- Embedding models applied consistently within corpus boundaries

---

### Stage 6: Agent Execution Stages

**Research Agent Execution:**
```
Claim Drafting Request → Context Retrieval (Open Patent Corpus ONLY) → Research Agent
    ↓
Evidence Collection + Citation Links → Draft Generation → Validation Queue
    ↓
Provenance Record: Agent Execution + Source Citations → Audit/Lineage Graph
```

**Drafting Agent Execution:**
```
Research Context + Claim Requirements → Drafting Agent → Candidate Claims
    ↓
Corpus Compliance Validation → [Valid: Continue] OR [Invalid: Block + Alert]
    ↓
Provenance Record: Claim Generation + Source Lineage → Audit/Lineage Graph
```

**Validation Agent Execution:**
```
Draft Claims + All Corpora (segregated access) → Validation Agent
    ↓
[Open Patent: Support Validation] + [Adversarial: Avoidance Check] + [Product: Read-on Check]
    ↓
Validation Report + Risk Assessment → HITL Review Queue
    ↓
Provenance Record: Multi-Corpus Validation Results → Audit/Lineage Graph
```

---

### Stage 7: HITL Task Creation & Resolution

**Task Generation:**
```
Agent Output + Validation Flags → HITL Task Generator → Structured Task Definition
    ↓
Task Metadata (type, priority, context, validation requirements) → HITL Queue
    ↓
Human Assignment + Interface Presentation → Review Interface
```

**Human Resolution:**
```
Human Review + Decision → [APPROVE] OR [REJECT] OR [REVISE] → Task Resolution
    ↓
Resolution Rationale + Evidence → Task Results → System Integration
    ↓
Provenance Record: Human Decision + Timestamp + Rationale → Audit/Lineage Graph
```

**Reintegration Flow:**
```
HITL Approval → Agent Pipeline Continuation → Next Stage Processing
HITL Rejection → Revision Loop OR Terminal Rejection State
HITL Revision → Modified Input → Agent Re-execution
```

---

### Stage 8: Claim Processing & Decision Loops

**Claim Acceptance Path:**
```
Validated Claims + Human Approval → Final Claim Set → Legal Review Ready
    ↓
Complete Provenance Package → Audit/Lineage Graph → Legal Defensibility Archive
    ↓
TERMINAL STATE: CLAIM_APPROVED
```

**Claim Rejection Path:**
```
Validation Failure OR Human Rejection → Rejection Documentation → Archive
    ↓
Rejection Rationale + Evidence → Audit/Lineage Graph → Lessons Learned Database  
    ↓
TERMINAL STATE: CLAIM_REJECTED
```

**Claim Revision Loop:**
```
Human/Agent Revision Request → Modified Requirements → Agent Re-execution Pipeline
    ↓
Iterative Processing → Convergence OR Max Iterations Reached
    ↓
[Converged: Acceptance Path] OR [Max Iterations: Rejection Path]
    ↓
TERMINAL STATE: CLAIM_REVISED_AND_RESUBMITTED OR CLAIM_REJECTED
```

---

### Stage 9: Failure Paths & Recovery

**OCR Failure Recovery:**
```
OCR Quality Check FAIL → BLOCKED state → HITL Manual Description Task
    ↓
Human Intervention → [Success: Continue] OR [Skip: IGNORED state with audit]
```

**Agent Validation Failure:**
```
Corpus Rule Violation → VALIDATION_FAILED state → Alert + Block
    ↓
Administrative Review → [Override with Justification] OR [Reject]
```

**HITL Rejection Recovery:**
```
Human Rejection → Revision Requirements Analysis → [Revise] OR [Abandon]
    ↓
Revision: Return to appropriate pipeline stage
    ↓
Abandonment: TERMINAL STATE: ARTIFACT_ARCHIVED
```

**System Failure Recovery:**
```
Processing Exception → ERROR_INVESTIGATION state → Diagnostic Capture
    ↓
Root Cause Analysis → [Retry] OR [Manual Escalation] OR [Skip with Documentation]
```

---

## Corpus Isolation Boundaries (Visual)

```
┌─────────────────────────────────────────────────────────────┐
│ OPEN PATENT CORPUS                                          │
│ ✅ Claim Support | ✅ Evidence | ✅ Language Source         │
│                                                             │
│ [Patent Text] → [Embedding Store] → [Agent Access: FULL]   │
└─────────────────────────────────────────────────────────────┘
                           │
                    [ISOLATION BOUNDARY]
                           │
┌─────────────────────────────────────────────────────────────┐
│ ADVERSARIAL CORPUS                                          │
│ ❌ Claim Support | ✅ Avoidance | ❌ Language Source        │
│                                                             │
│ [Prior Art/OA/IPR] → [Embedding Store] → [Agent: AVOID]    │
└─────────────────────────────────────────────────────────────┘
                           │
                    [ISOLATION BOUNDARY]  
                           │
┌─────────────────────────────────────────────────────────────┐
│ PRODUCT CORPUS                                              │
│ ❌ Claim Support | ✅ Read-on Check | ❌ Language Source    │
│                                                             │
│ [Product Docs] → [Embedding Store] → [Agent: READ-ON]      │
└─────────────────────────────────────────────────────────────┘
```

---

## Provenance Capture Points (Mandatory)

1. **Document Acquisition**: Source, method, timestamp, validation status
2. **Agent Outputs**: Input context, processing version, output artifacts, confidence scores
3. **Human Approvals**: Decision, rationale, timestamp, reviewer identity
4. **Diagram Decisions**: Reuse vs. unique determination, quality assessment, description approval
5. **Corpus Assignments**: Classification logic, access rules applied, compliance validation
6. **Claim Acceptance**: Final approval, supporting evidence chain, legal review completion
7. **Failure Events**: Error type, recovery action, resolution method, lessons learned

All provenance records include: timestamp, triggering event, decision rationale, audit trail linkage.

---

## Terminal States (Clearly Labeled)

### Successful Outcomes:
- **CLAIM_APPROVED**: Claims pass all validation, human approval, legal review complete
- **CLAIM_REVISED_AND_RESUBMITTED**: Claims improved through iteration, resubmitted for new cycle

### Rejection Outcomes:  
- **CLAIM_REJECTED**: Claims fail validation, human rejection, or legal review
- **ARTIFACT_ARCHIVED**: Processing abandoned, materials preserved for audit/reference

### Administrative Outcomes:
- **PROCESSING_SUSPENDED**: Temporary halt pending external input or resource availability
- **CORPUS_QUARANTINE**: Isolation violation detected, materials quarantined pending review

---

## Data Flow Validation Checkpoints

Each stage includes validation checkpoints ensuring:
- **Correctness**: Data transformations preserve integrity and meet quality standards
- **Auditability**: All decisions and transformations have complete provenance trails  
- **Legal Defensibility**: Corpus isolation maintained, human oversight documented, evidence chains complete

This visual flow serves as the authoritative reference for system validation and legal compliance verification.