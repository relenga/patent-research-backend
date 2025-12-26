# ScopeByPhase.md
## Development Phase Scope Summary

---

## Purpose

This document provides a concise **summary view** of what is included in each development phase, extracted from the authoritative BuildPlan.md and PRD.md documents.

**Authority:** This is a **summary only** - BuildPlan.md remains the execution authority for detailed tasks.

This document does not authorize work. All execution must follow BuildPlan.md task definitions.

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
- **Establish governance:** AgentRules.md, CopilotRules.md, phase discipline documentation
- **Prepare structure:** Create empty target folders (`common/`, `pipelines/`, `llm/`, `state/`)

**Out of Scope:** Any new functionality, performance optimization, architectural improvements

**Status:** Complete - Tagged `phase-1-prune-complete`

---

## Phase 2 — Harden 🔄 READY  
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

**Status:** Ready to begin

---

## Phase 3 — Build 🔮 FUTURE
**Goal:** Feature implementation using Phase 2 contracts

**Functional Scope:**
- **OCR functionality:** Document processing, text extraction
- **Vectorization:** Document embedding and similarity
- **LLM integration:** Language model interactions, prompt engineering
- **Research agents:** Intelligent document analysis
- **Pipeline orchestration:** End-to-end processing workflows
- **Background task implementations:** Async processing execution
- **Database schema design:** Persistence layer (if needed)

**Planning Approach:**
- Detailed task breakdown deferred until Phase 2 completion
- Implementation order and technical decisions to be determined collaboratively
- Will leverage Phase 2 contracts and structures

**Status:** Future - Cannot begin until Phase 2 tagged complete

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
- **Governance Authority:** [AgentRules.md](AgentRules.md) - Phase rules and AI agent constraints

---

## One-Line Summary

> **Each phase builds upon the previous, with Phase 1 removing complexity, Phase 2 adding structure, and Phase 3 implementing functionality.**