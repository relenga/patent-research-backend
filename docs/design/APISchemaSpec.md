# API Schema Specification

**Status**: APPROVED - FastAPI+HTMX UI and PostgreSQL Decisions Confirmed (Dec 30, 2025)  
**Authority**: Implementation guidance for all P3.x tasks requiring API endpoints  
**Implementation Standards**: [Standards.md](../Standards.md) - MANDATORY API conventions, response envelopes, and error handling  
**Cross-References**: [common/api.py](../../../common/api.py), [DatabaseSchemaSpec.md](./DatabaseSchemaSpec.md)

## Purpose

Defines domain-specific API endpoints and request/response schemas for documents, artifacts, diagrams, corpora, tasks, agent runs, and claims using canonical response envelopes.

## Required Content (Minimum Specification)

### Domain Endpoints

#### Document Management APIs
- [ ] **POST /api/v1/documents** - Document upload and ingestion
- [ ] **GET /api/v1/documents/{id}** - Document retrieval with metadata
- [ ] **PUT /api/v1/documents/{id}** - Document metadata updates
- [ ] **GET /api/v1/documents/{id}/versions** - Document version history
- [ ] **POST /api/v1/documents/{id}/transition** - Pipeline state transitions
- [ ] **DELETE /api/v1/documents/{id}** - Soft delete with reason

#### Artifact & Content APIs  
- [ ] **GET /api/v1/documents/{id}/artifacts** - Document artifact listing
- [ ] **POST /api/v1/artifacts** - Artifact creation (text, image, diagram)
- [ ] **GET /api/v1/artifacts/{id}** - Artifact retrieval with content
- [ ] **PUT /api/v1/artifacts/{id}** - Artifact updates and versioning
- [ ] **DELETE /api/v1/artifacts/{id}** - Soft delete artifact with reason (P3.2B.2)
- [ ] **POST /api/v1/artifacts/{id}/restore** - Restore soft-deleted artifact (P3.2B.2)
- [ ] **PUT /api/v1/artifacts/{id}/description** - Edit image description (P3.2B.2)
- [ ] **POST /api/v1/artifacts/{id}/ignore** - Mark image as ignored (P3.2B.2)

#### Diagram Management APIs
- [ ] **POST /api/v1/diagrams/canonical** - Canonical diagram creation
- [ ] **GET /api/v1/diagrams/{id}** - Diagram retrieval with representations
- [ ] **PUT /api/v1/diagrams/{id}/approve** - Diagram approval workflow
- [ ] **GET /api/v1/diagrams/{id}/versions** - Diagram version history

#### Corpus Management APIs
- [ ] **GET /api/v1/corpora** - Available corpora listing
- [ ] **POST /api/v1/corpora/{corpus_id}/assign** - Document corpus assignment
- [ ] **GET /api/v1/corpora/{corpus_id}/documents** - Corpus membership queries
- [ ] **GET /api/v1/corpora/{corpus_id}/statistics** - Corpus analytics

#### Task Management APIs
- [ ] **GET /api/v1/tasks/assigned/{actor_id}** - Tasks for specific user (from session-selected reviewer)
- [ ] **PUT /api/v1/tasks/{id}/complete** - Task completion with session reviewer attribution
- [ ] **GET /api/v1/tasks/{id}/evidence** - Evidence bundle retrieval
- [ ] **POST /api/v1/tasks/{id}/reassign** - Task reassignment (session reviewer performing reassignment)

#### Agent Execution APIs
- [ ] **POST /api/v1/agents/{agent_id}/execute** - Agent execution trigger
- [ ] **GET /api/v1/agent-runs/{id}** - Agent run status and results
- [ ] **GET /api/v1/agent-runs** - Agent execution history
- [ ] **POST /api/v1/agents/{agent_id}/validate** - Agent boundary validation

#### Claim Management APIs
- [ ] **POST /api/v1/claims** - Claim creation and validation
- [ ] **GET /api/v1/claims/{id}** - Claim retrieval with provenance
- [ ] **PUT /api/v1/claims/{id}/review** - Claim review and approval
- [ ] **GET /api/v1/claims** - Claim listing with filtering

### Request/Response Schemas

#### Identity Model Integration
**Simple Identity (No Authentication)**: All API endpoints assume session-based reviewer selection
- **{actor_id}** parameters: User ID from session-selected reviewer (dropdown selection from users table)
- **Attribution Pattern**: Session reviewer ID automatically applied to all created/modified entities
- **LLM Operations**: System processes use distinct userids separate from human reviewer selection
- **Audit Compliance**: All API operations include reviewer attribution for litigation requirements

#### Canonical Response Envelope
**Reference**: [Standards.md](../Standards.md) defines complete envelope specification  
- [ ] **Success Response**: Uses `APIResponse[T]` from common/api.py per standards
- [ ] **Error Response**: Uses `APIError` with ErrorCode enum per standards
- [ ] **Metadata Inclusion**: request_id, timestamp, correlation info per standards
- [ ] **Pagination Support**: Standard pagination metadata per standards

#### Domain-Specific Schemas
```python
# Document schemas
class DocumentCreateRequest(BaseModel):
    title: str
    source_type: str
    corpus_id: str
    file_content: bytes

class DocumentResponse(BaseModel):
    id: str
    title: str
    status: DocumentState
    corpus_id: str
    created_at: datetime
    metadata: Dict[str, Any]

# Agent execution schemas  
class AgentExecuteRequest(BaseModel):
    input_data: Dict[str, Any]
    corpus_scope: List[str]
    parameters: Dict[str, Any]

class AgentRunResponse(BaseModel):
    run_id: str
    agent_id: str
    status: str
    outputs: Dict[str, Any]
    provenance: Dict[str, Any]
```

### Validation Requirements

#### Input Validation
- [ ] **Corpus Boundary Validation**: All requests validate corpus access
- [ ] **Schema Validation**: Pydantic models enforce data integrity
- [ ] **Business Rule Validation**: Domain constraints enforced
- [ ] **Authorization Validation**: Actor permissions verified

#### Output Validation
- [ ] **Response Schema Compliance**: All responses use canonical envelope
- [ ] **Data Consistency**: Cross-entity references validated
- [ ] **Audit Trail Inclusion**: Provenance data included where required
- [ ] **Performance Monitoring**: Response time and size tracking

## Design Decisions (APPROVED)

1. **UI Integration**: **FastAPI server-rendered HTML** (Jinja + HTMX)
   - **Rationale**: Single service architecture; backend controls all state; no separate build system
   - **Constraints**: HTMX for interactivity only; API remains reusable for future needs

2. **Pagination Strategy**: Offset-based pagination with PostgreSQL optimization
3. **File Upload Strategy**: Direct upload with PostgreSQL blob storage
4. **Real-time Updates**: HTMX partial page updates (no WebSocket complexity)
5. **Bulk Operations**: Individual operations only for Phase 3 (batch deferred)

## Implementation Guidance

### FastAPI Integration
- Use existing APIRouter patterns from src/app/api/
- Integrate with dependency injection for database sessions
- Apply rate limiting and request validation middleware
- Implement request/response logging for audit compliance

### Error Handling
```python
# Consistent error response patterns
@app.exception_handler(CorpusViolationError)
async def corpus_violation_handler(request: Request, exc: CorpusViolationError):
    return APIError(
        code=ErrorCode.CORPUS_VIOLATION,
        message="Corpus boundary violation detected",
        details={"violation": exc.details}
    )
```

## Acceptance Criteria

- [ ] All domain endpoints defined with complete schemas
- [ ] Canonical response envelope used consistently per [Standards.md](../Standards.md)
- [ ] Input validation comprehensive and tested
- [ ] Error handling follows patterns per [Standards.md](../Standards.md)
- [ ] Integration with database layer verified
- [ ] Performance requirements met for API responses
- [ ] Human reviewer approval obtained

---

**Status**: SPECIFICATION COMPLETE - Ready for API Implementation
**Approved**: FastAPI+HTMX Integration + PostgreSQL (Dec 30, 2025)