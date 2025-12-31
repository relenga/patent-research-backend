# Corpus Model — AUTHORITATIVE BUSINESS RULES

**Authority**: SINGLE AUTHORITY for all corpus business rules and boundaries
**Implementation**: [CorpusEnforcementSpec.md](design/phase-3-specs/CorpusEnforcementSpec.md) (technical enforcement)
**Agent Access Rules**: [AgentResponsibilities.md](AgentResponsibilities.md) (agent-specific corpus permissions)

## Document Authority

This document defines **what corpus boundaries exist and why**, providing the business rules that govern all corpus enforcement. Other documents reference these rules:

- **CorpusEnforcementSpec.md**: HOW to technically implement these business rules
- **AgentResponsibilities.md**: WHICH agents can access which corpora per these rules
- **DatabaseSchemaSpec.md**: Database schema supporting these corpus definitions

This document defines how knowledge is organized into corpora and how each corpus may be used.

---

## Core Rule

**Only the Open Patent Corpus may support claim language.**

All other corpora exist to **constrain, validate, or challenge** claims — never to supply claim text.

---

## Corpus Definitions

### Open Patent Corpus
**Role:** Authoritative claim support  
**May be used for:** Claim drafting  
**May not be overridden**

---

### Adversarial Corpus (Prior Art, OA, IPR)
**Role:** Risk and avoidance  
**Explicitly Forbidden Uses:**
- Supplying claim language
- Introducing limitations

**Explicitly Allowed Uses:**
- Identifying vulnerabilities
- Avoidance reasoning
- Risk scoring

---

### Product Corpus
**Role:** Read-on verification  
**Use:** Evidence mapping only

---

### Drafting Guidance Corpus (Optional)
**Role:** Style and structure guidance  
**Constraint:** Non-substantive

---

## Corpus Access Matrix (AUTHORITATIVE)

| Corpus Type | Claim Drafting | Risk Analysis | Evidence Mapping | Style Guidance |
|-------------|---------------|---------------|------------------|----------------|
| **Open Patent** | ✅ AUTHORIZED | ✅ Allowed | ✅ Allowed | ✅ Allowed |
| **Adversarial** | ❌ FORBIDDEN | ✅ AUTHORIZED | ❌ Forbidden | ❌ Forbidden |
| **Product** | ❌ FORBIDDEN | ✅ Allowed | ✅ AUTHORIZED | ❌ Forbidden |
| **Guidance** | ❌ FORBIDDEN | ❌ Forbidden | ❌ Forbidden | ✅ AUTHORIZED |

**Key**:
- ✅ AUTHORIZED: Primary purpose, full access
- ✅ Allowed: Secondary use permitted
- ❌ FORBIDDEN: Explicitly prohibited, enforcement required

**Implementation**: CorpusEnforcementSpec.md must enforce these access restrictions at storage, retrieval, and agent execution levels.

**Agent Compliance**: AgentResponsibilities.md defines which agents may perform which operations per this matrix.

## Enforcement Rule

If a claim element cannot be traced to the **Open Patent Corpus**, it is invalid.

---

### Prior Art Usage Constraint

Artifacts in the **Adversarial Corpus** (prior art, OA/IPR):
- May be used for **avoidance, risk analysis, and validation**
- May NOT be used as positive support for claim language

The Claim Drafting Agent may reason about prior art only to:
- Avoid overlap
- Identify vulnerabilities
- Adjust claim scope

No claim element may cite adversarial corpus artifacts as support.

---

## Diagrams & Images (AUTHORITATIVE RULES)

### Corpus Inheritance for Diagrams

**Rule**: Diagrams inherit corpus constraints from their parent source document.

- **Open Patent Diagrams**: May support claim drafting when canonicalized
- **Adversarial Corpus Diagrams**: Avoidance analysis only, never claim support
- **Product Corpus Diagrams**: Read-on verification only, never claim support

### Duplicate/Identical/Reused Handling

**Canonical Description Authority**: When identical diagrams appear across documents:
- **First processed diagram** establishes canonical description
- **Subsequent identical diagrams** reference canonical description
- **Corpus access follows MOST RESTRICTIVE** parent document

**Example**: Same diagram in Open Patent (corpus: open) and Prior Art (corpus: adversarial)
- Result: Diagram restricted to adversarial corpus constraints (avoidance only)
- Reason: Most restrictive rule prevents corpus contamination

### IGNORED Diagram Handling

Diagrams marked as **IGNORED**:
- **Stored + Auditable**: Full provenance trail preserved
- **Excluded by Default**: Not retrieved for claim reasoning or evidence
- **Audit Visible**: Remain visible in audit views and lineage reports
- **Human Decision Required**: Only humans may mark diagrams IGNORED
- **Required Rationale**: `ignored_reason` field mandatory

**Common IGNORED reasons**: logos, advertisements, decorative elements, non-technical photos

### Canonical Diagram Reuse Rules

When reusing canonical descriptions across documents:
- **Inherits corpus constraints** of the MOST RESTRICTIVE parent document
- **Lineage tracking** maintains full reuse chain
- **Human approval required** for cross-corpus canonical reuse
- **Audit trail** records all reuse decisions and rationale

---

## Relationship to Other Documents

**CorpusModel.md** governs *where knowledge may be used*  
**PipelineStateMachine.md** governs *how artifacts become usable*

Canonical diagram descriptions inherit the corpus constraints of their parent document. Diagrams linked to Adversarial or Product corpora may never supply claim language.

