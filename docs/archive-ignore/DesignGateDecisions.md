# Phase 3 Design Gate — Decision History

**Status**: ARCHIVED - Historical Record (Dec 30, 2025)  
**Purpose**: Documents approved technology decisions that closed Phase 3 Design Gate  
**Location**: Archived from active specifications - decisions are implemented  

## APPROVED DECISIONS (Dec 30, 2025)

**All 5 Critical Decisions Resolved**:

1. **Database Technology**: PostgreSQL (single-node, local-first) ✅
2. **Local LLM Integration**: PyTorch + Transformers (direct integration, no vLLM) ✅  
3. **UI Technology Stack**: FastAPI server-rendered HTML (Jinja + HTMX, no React SPA) ✅
4. **Actor Identity Model**: Single reviewer model (no authentication) ✅
5. **Diagram Automation Scope**: OCR + Human Correction (no full automation) ✅

**Specifications Updated**: All 7 technical specifications updated with approved decisions and rationale.

**Cross-References Verified**: Design document consistency confirmed across BuildPlan.md, ScopeByPhase.md, and all Phase 3 specifications.

---

## ORIGINAL REQUIREMENTS (For Reference)

The following technical decisions must be resolved to complete Phase 3 specifications and authorize implementation:

### 1. Database Technology Choice
**Specification Impact**: DatabaseSchemaSpec.md, PipelineExecutionSpec.md  
**Decision Required**: 
- **PostgreSQL**: Full production database with advanced features
- **SQLite**: Development simplicity with potential production limitations

**Considerations**:
- PostgreSQL: Complex setup, production-ready, advanced indexing
- SQLite: Simple deployment, file-based, limited concurrent access

### 2. UI Technology Stack 
**Specification Impact**: HITLTaskSpec.md, APISchemaSpec.md  
**Decision Required**:
- **FastAPI Templates**: Server-rendered HTML with minimal complexity
- **React SPA**: Client-side application with API backend
- **Hybrid Approach**: Critical HITL flows server-rendered, advanced features SPA

**Considerations**:
- FastAPI Templates: Faster development, simpler deployment
- React SPA: Better user experience, more complex development
- Hybrid: Balanced approach, increased architectural complexity

### 3. Local LLM Integration Pattern
**Specification Impact**: AgentFrameworkSpec.md  
**Decision Required**:
- **PyTorch + Transformers**: Direct integration with model management
- **vLLM Server**: High-performance inference server with API
- **Hybrid Approach**: vLLM for production, PyTorch for development

**Considerations**:
- PyTorch Direct: Simple integration, full control, memory management complexity
- vLLM Server: Performance optimized, additional service dependency
- RTX-5090 hardware supports either approach effectively

### 4. Diagram Automation Scope
**Specification Impact**: DatabaseSchemaSpec.md, APISchemaSpec.md  
**Decision Required**:
- **Manual Upload Only**: Human-provided diagrams, no automation
- **OCR + Manual Correction**: Automated extraction with human review
- **Full Automation Deferred**: Phase 4 feature, minimal Phase 3 support

**Considerations**:
- Manual Only: Simplest implementation, limited functionality
- OCR Integration: Complex diagram parsing, quality validation required
- Deferred Automation: Focuses Phase 3 scope, defers complexity

### 5. Actor Identity Model Scope
**Specification Impact**: DatabaseSchemaSpec.md, HITLTaskSpec.md  
**Decision Required**:
- **Session-Based**: Minimal identity for HITL task continuity
- **User Accounts**: Simple user system without full authentication
- **External Integration**: Integrate with existing identity provider

**Considerations**:
- Session-Based: Meets HITL requirements, minimal complexity
- User Accounts: Better audit trails, moderate complexity
- External: Production-ready, high complexity for Phase 3

## Impact Analysis

### High-Impact Decisions (Block Multiple Specs)
1. **Database Choice**: Affects 5+ specifications significantly
2. **LLM Integration**: Affects agent framework and performance expectations

### Medium-Impact Decisions (Block 1-2 Specs)  
3. **UI Technology**: Affects HITL and API design patterns
4. **Actor Identity**: Affects database schema and task management

### Low-Impact Decisions (Implementation Details)
5. **Diagram Scope**: Can be scoped down without architectural impact

## Recommended Decision Timeline

### Immediate (Required for Design Gate Closure)
- **Database Technology**: Must be resolved for DatabaseSchemaSpec.md completion
- **LLM Integration Pattern**: Must be resolved for AgentFrameworkSpec.md completion

### Near-Term (Required for Implementation Start)
- **UI Technology Stack**: Must be resolved before P3.9 HITL implementation
- **Actor Identity Scope**: Must be resolved before P3.1 database schema

### Can Be Deferred (Scope Reductions Possible)
- **Diagram Automation**: Can scope to manual-only for Phase 3

## Human Reviewer Action Required

**Next Step**: Project Manager must review and decide on the 4 critical technology choices above.

**Documentation Required**: Once decisions are made, update each affected specification with:
- Chosen technology and rationale
- Implementation guidance specific to chosen approach
- Integration patterns with existing system components

**Design Gate Closure**: After decisions documented and specifications updated, explicit human authorization required to begin P3.1 implementation.

---

**BLOCKING STATUS**: Phase 3 implementation cannot begin until these decisions are made and specifications updated accordingly.