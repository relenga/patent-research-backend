# ScopeByPhase.md
## Development Phase Scope Summary

---

## Purpose

This document provides a concise **summary view** of what is included in each development phase, extracted from the authoritative BuildPlan.md and PRD.md documents.

**Authority:** This is a **summary only** - BuildPlan.md remains the execution authority for detailed tasks.

This document does not authorize work. All execution must follow BuildPlan.md task definitions.

## Task Management System Status Summary

**Overall Status:** ❌ Not Implemented

- **Phase 1:** ✅ Background task infrastructure deliberately removed (ARQ/Redis)
- **Phase 2:** ✅ HITL contracts and audit models defined as interfaces
- **Phase 3:** ❌ Human-in-the-loop workflow implementation pending (P3.9)

**Key Architecture:** Database-only task persistence, no queue system, state machine integration

---

## Phase 0 — Bootstrap ✅ COMPLETE
**Goal:** Environment verification and toolchain stability

**Scope:**
- Development environment setup
- Tool verification 
- Repository initialization
- No feature development

**Status:** Complete - Tagged `phase-0-complete`

---

## Phase 1 — Prune ✅ COMPLETE  
**Goal:** Simplification and control through removal

**Scope:**
- **Remove unused template features:** Redis, ARQ, admin panels, authentication, JWT, rate limiting, caching
- **Disable external infrastructure:** No Redis connections, no background workers, no admin bootstrapping during startup
- **Simplify configuration:** Safe defaults, no required .env file, minimal settings surface
- **Establish governance:** AgentRules.md consolidating phase discipline and execution rules
- **Prepare structure:** Create empty target folders (`common/`, `pipelines/`, `llm/`, `state/`)

**Out of Scope:** Any new functionality, performance optimization, architectural improvements

**Status:** Complete - Tagged `phase-1-prune-complete`

---

## Phase 2 — Harden ✅ COMPLETE  
**Goal:** Structure, contracts, and enforcement preparation

### Pre-Phase 2 Notes

**Acknowledged clarifications before execution begins:**

• **API Routing Policy** - Trailing slash policy chosen and documented, no enforcement until Phase 3
• **Testing Strategy** - No automated testing in Phase 2, validation is structural not behavioral  
• **Persistence Boundary** - Data models and interfaces only, no storage engines or migrations
• **Observability Scope** - Logging interfaces only, metrics/tracing/alerting deferred
• **Production Concerns** - Docker, CI/CD, deployment explicitly out of scope
• **Enforcement Timing** - Phase 2 documents invariants, Phase 3 enforces them

**Scope:**
- **Common services skeleton:** Request/execution context, time/clock service, ID generation, structured logging (interfaces only)
- **API invariants:** Routing standards, response envelopes, error schemas (documented, not enforced)
- **Document state machine:** State enums, transition rules, validation contracts (no execution logic)
- **Pipeline contracts:** Step interfaces, input/output contracts, composition rules (no implementations)
- **Phase enforcement:** Feature flags structure, phase detection utilities, violation exception types
- **Provenance tracking:** Lineage data models, audit trail schemas (no storage logic)

**Critical Rule:** Contracts and interfaces ONLY - no implementations, no business logic, no external integrations

**Status:** Complete - Tagged `phase-2-harden-complete`

---

## Phase 3 — Build — DESIGN GATE CLOSED
**Goal:** Feature implementation using Phase 2 contracts

### Phase 3 Design Gate — CLOSED (Dec 30, 2025)

**GATE STATUS**: CLOSED - Technical specifications completed and approved

**Human Approval**: All 5 critical technology decisions approved by Project Manager
- PostgreSQL (single-node, local-first) for database
- PyTorch+Transformers (direct integration) for LLM
- FastAPI+HTMX (server-rendered) for UI
- Single reviewer model (no authentication) for actor identity
- OCR+Human correction (no full automation) for diagrams

**Specification Status**: All 7 technical specifications completed, consistent, and cross-referenced

**Implementation Authorization**: Phase 3 is now READY FOR P3.1 EXECUTION upon human authorization

### Functional Scope (Post-Design Gate)

**Planned Implementation Capabilities:**
- Document upload, normalization, and text extraction (manual upload path)
- OCR processing for images and scanned content with quality scoring
- Corpus classification and isolation enforcement (Open Patent, Adversarial, Product, Guidance)
- Agent execution within strict corpus and authority boundaries
- Text chunking, embedding generation, and corpus-aware retrieval
- Human-in-the-loop task generation, review workflows, and audit trails
- Basic web interface for document management and human review tasks
- Comprehensive system logging and event tracking

**Implementation Structure:** P3.1-P3.12 tasks with foundation-first ordering
- **Data Layer (P3.1):** Database schema and persistence layer
- **Pipeline Layer (P3.2):** Pipeline state machine execution engine
- **Ingestion Layer (P3.3-P3.4):** Document ingestion and OCR processing  
- **Corpus Layer (P3.5):** Classification and corpus isolation
- **RAG Layer (P3.6):** Text chunking and retrieval infrastructure
- **Agent Layer (P3.7-P3.8):** Agent execution framework and implementations
- **Interface Layer (P3.9-P3.11):** HITL workflows (not implemented), logging, and minimal UI (not implemented)
- **Verification (P3.12):** End-to-end integration testing and compliance validation

**Critical Enforcement Boundaries:**
- **Corpus Isolation:** Retrieval operations strictly limited to specified corpus
- **Agent Authority:** Each agent limited to defined responsibilities and corpus access
- **HITL Requirements:** Human approval mandatory for all claim outputs
- **Audit Completeness:** All actions logged with immutable provenance tracking
- **Phase Discipline:** No optimization, analytics, or production features

**Explicitly Forbidden in Phase 3:**
- Research agent automation (external API integration)
- Advanced ML model training or fine-tuning
- Performance optimization beyond basic functionality
- Complex user management or role-based access control
- Production deployment configurations
- Business intelligence or analytics features
- Multi-tenancy or customer isolation
- Advanced UI/UX or mobile interfaces

**Planning Approach:**
- Foundation-first implementation order (data → pipeline → agents → UI)
- Detailed task breakdown in BuildPlan.md P3.1-P3.12
- Implementation leverages all Phase 2 contracts and structures
- Comprehensive verification required before phase completion
- Open questions documented in BuildPlan require human decision

**Status:** Planning aligned pending final human design review

---

## Phase Not Defined 🤔

Based on review of the codebase and documentation, the following capabilities are mentioned but not explicitly assigned to phases:

### Production & Operations
- **Deployment strategies:** Docker compose configurations, container orchestration
- **Security hardening:** Production security headers, SSL configuration, secure credential management  
- **Performance optimization:** Database tuning, connection pooling, resource limits
- **Monitoring & observability:** Metrics collection, health checks, alerting, log aggregation
- **Backup & recovery:** Database backups, disaster recovery procedures
- **CI/CD pipelines:** Automated testing, deployment automation

### Testing & Quality Assurance  
- **Test automation:** Unit testing, integration testing, end-to-end testing
- **Performance testing:** Load testing, stress testing, benchmark validation
- **Security testing:** Vulnerability scanning, penetration testing
- **Configuration validation:** Environment-specific validation, startup checks

### Documentation & Maintenance
- **API documentation:** OpenAPI/Swagger documentation maintenance
- **User guides:** End-user documentation, admin guides
- **Operational runbooks:** Troubleshooting guides, maintenance procedures

### Questions for Consideration:
1. Should **Testing & Quality Assurance** be integrated into each phase or treated as a separate phase?
2. Should **Production & Operations** be Phase 4, or distributed across phases?
3. Are **Documentation & Maintenance** ongoing concerns or phase-specific deliverables?

---

## Authority & Cross-References

- **Execution Authority:** [BuildPlan.md](BuildPlan.md) - Detailed tasks and phase requirements
- **Requirements Authority:** [PRD.md](PRD.md) - What must be true for Phase 1
- **Governance Authority:** [AgentRules.md](AgentRules.md) - AI governance, phase rules and agent constraints

---

## One-Line Summary

> **Each phase builds upon the previous, with Phase 1 removing complexity, Phase 2 adding structure, and Phase 3 implementing functionality.**