# Standards.md
## Authoritative Technical Standards & Common Services (MANDATORY)

---

## Document Authority & Purpose

**This document is the AUTHORITATIVE REFERENCE for:**
- Common services usage requirements
- API conventions and patterns
- Configuration management standards
- Logging and event semantics
- Versioning rules and policies
- Coding and naming standards

**Document Authority Hierarchy:**
1. **AgentRules.md** (governance and phase control) - HIGHEST AUTHORITY
2. **Standards.md** (technical standards and common services) - THIS DOCUMENT
3. **BuildPlan.md** (execution sequencing and task definitions)
4. **Design specifications** (implementation guidance)
5. **Business logic documents** (context only)

**Compliance Rule**: All development work MUST comply with standards defined in this document. Violations require immediate correction or explicit human approval with documented rationale.

**Authority Date**: December 31, 2025
**Supersedes**: All scattered standards definitions in other documents

---

## Common Services (MANDATORY USAGE)

All components MUST use these standardized services. Direct usage of alternatives is FORBIDDEN unless explicitly documented and approved.

### PostgreSQL Persistence Service
**Name**: Database Session Management  
**Purpose**: Single-node PostgreSQL database for all data persistence  
**Required Usage**: All database operations MUST use `async_get_db()` dependency injection  
**Defined In**: `src/app/core/db/database.py`, `DatabaseSchemaSpec.md`  
**FORBIDDEN**: Manual session creation, direct SQLAlchemy engine access, multiple databases  
**Enforcement**: Phase 3 active - all database access audited

**Phase 3 Database Migration Constraints**:
- **Schema Creation**: Fresh schema creation assumed for Phase 3
- **Migration Tooling**: EXPLICITLY DEFERRED - No Alembic, versioned migrations, or automated schema migration tools in Phase 3
- **Backward Compatibility**: NOT GUARANTEED - Phase 3 assumes clean slate deployment
- **Schema Changes**: Manual schema updates only, no automated migration workflows

**Database Documentation Authority Model**:
- **DatabaseSchemaSpec.md**: IMPLEMENTATION AUTHORITY - definitive table definitions, constraints, indexes, business rules
- **ER Diagrams**: VISUAL AUTHORITY - enhanced visual representation with field lengths, basic constraints, relationships
- **DDL Scripts**: DEPLOYED REALITY - actual implementation deployed to database
- **Authority Hierarchy**: DatabaseSchemaSpec.md → ER Diagrams → DDL Scripts
- **Conflict Resolution**: All conflicts resolved by referring to DatabaseSchemaSpec.md
- **ER Diagram Enhancement**: Include field lengths (varchar(255)), basic constraints (NOT NULL, UNIQUE), relationships

### LoggingService (Structured Logging + Audit)
**Name**: Centralized Logging Service  
**Purpose**: Structured logging with correlation IDs, audit trails, and compliance tracking  
**Required Usage**: All logging MUST use LoggingService interface - no direct Python logging  
**Defined In**: `common/logging.py`, `LoggingAndEventsSpec.md`  
**FORBIDDEN**: Direct `logging.getLogger()`, print statements, ad-hoc logging  
**Enforcement**: Phase 3 active - all log entries require structured format

### Configuration via Pydantic BaseSettings
**Name**: Settings Management Service  
**Purpose**: Type-safe environment variable management with validation  
**Required Usage**: All configuration MUST be accessed via `from app.core.config import settings`  
**Defined In**: `src/app/core/config.py`  
**FORBIDDEN**: Direct `os.environ` access, hardcoded values, runtime configuration files  
**Source**: .env files ONLY - no alternative configuration sources permitted

### IDService (Canonical ID Generation)
**Name**: ID Generation Service  
**Purpose**: Consistent UUID/ULID generation across all components  
**Required Usage**: All ID generation MUST use IDService interface  
**Defined In**: `common/ids.py`  
**FORBIDDEN**: Direct `uuid.uuid4()`, `uuid.uuid7()`, or ad-hoc ID generation  
**Enforcement**: Phase 3 active - prevents ID format inconsistency

### TimeService (UTC Time Management)
**Name**: Centralized Time Service  
**Purpose**: UTC time source, mockable for testing, consistent time handling  
**Required Usage**: All time operations MUST use TimeService interface  
**Defined In**: `common/time.py`  
**FORBIDDEN**: Direct `datetime.now()`, `time.time()`, or manual UTC conversion  
**Enforcement**: Phase 3 active - ensures consistent time handling and testability

### LLM Inference Service (Local PyTorch + Transformers)
**Name**: Local LLM Integration Service  
**Purpose**: Patent intelligence inference using local models on RTX-5090  
**Required Usage**: All AI inference MUST use approved PyTorch + Transformers stack  
**Defined In**: `AgentFrameworkSpec.md`, `RAGInfrastructureSpec.md`  
**FORBIDDEN**: External LLM APIs, cloud services, alternative inference engines  
**Configuration**: Model selection via environment variables only

### OCR / Diagram Processing Service
**Name**: Tesseract OCR + Diagram Canonicalization Service  
**Purpose**: Document OCR, diagram extraction, duplicate detection, human-in-the-loop processing  
**Required Usage**: All document processing MUST use OCR service with HITL workflows  
**Defined In**: `DocumentProcessingPipelineSpec.md`  
**FORBIDDEN**: Alternative OCR engines, fully automated diagram processing  
**Approach**: OCR + Human Correction (approved Phase 3 decision)

### RAG Infrastructure Service
**Name**: Retrieval-Augmented Generation Service  
**Purpose**: Embedding generation, vector search, corpus-aware retrieval  
**Required Usage**: All document retrieval MUST respect corpus isolation boundaries  
**Defined In**: `RAGInfrastructureSpec.md`  
**FORBIDDEN**: Cross-corpus contamination, external vector databases, cloud embedding services  
**Technology**: pgvector + sentence-transformers (local processing only)

---

## API Standards

### URL Structure (MANDATORY)
- **Pattern**: `/api/v1/{resource}` - ALL endpoints MUST follow this structure
- **Versioning**: Path-based versioning (`/api/v1/`, `/api/v2/`) - NO query parameter versioning
- **Trailing Slash Policy**: **NO trailing slashes** - `/api/v1/documents` NOT `/api/v1/documents/`
- **Resource Naming**: Plural nouns for collections (`/documents`), singular for specific operations (`/document/{id}`)

### HTTP Method Conventions (MANDATORY)
- **GET**: Retrieval operations, MUST be idempotent
- **POST**: Creation operations, document ingestion, task creation
- **PUT**: Update operations, state transitions, approval workflows
- **DELETE**: Resource removal (rare - most operations use soft delete)
- **PATCH**: Partial updates (discouraged - prefer PUT with full resource)

### Canonical Response Envelopes (MANDATORY)
**Success Response**: ALL successful responses MUST use `APIResponse[T]` from `common/api.py`
```json
{
  "data": T,
  "message": "optional human-readable message",
  "success": true,
  "request_id": "correlation-uuid",
  "timestamp": "2025-12-31T10:30:00Z",
  "meta": { "pagination": "...", "additional": "..." }
}
```

**Error Response**: ALL error responses MUST use `APIError` with `ErrorCode` enum
```json
{
  "code": "VALIDATION_ERROR",
  "message": "Human-readable error message",
  "details": { "field": "error details" },
  "request_id": "correlation-uuid",
  "timestamp": "2025-12-31T10:30:00Z",
  "trace_id": "optional-trace-uuid"
}
```

### ErrorCode Usage (MANDATORY)
Standard error codes from `common/api.py`:
- **VALIDATION_ERROR**: Input validation failures
- **NOT_FOUND**: Resource not found
- **UNAUTHORIZED**: Authentication required
- **FORBIDDEN**: Access denied (corpus violations)
- **RATE_LIMITED**: Rate limit exceeded
- **INTERNAL_ERROR**: Server-side failures
- **SERVICE_UNAVAILABLE**: Temporary service issues
- **TIMEOUT**: Operation timeout

### Pagination Standards (MANDATORY)
All list endpoints MUST support:
- **page**: Page number (1-based)
- **items_per_page**: Items per page (default: 10, max: 100)
- **Metadata**: Include `total_items`, `total_pages`, `current_page` in response meta

### Correlation IDs and Timestamps (MANDATORY)
- **request_id**: Every request MUST have correlation ID for tracing
- **timestamp**: All responses MUST include ISO 8601 UTC timestamp
- **trace_id**: Optional distributed tracing ID for complex operations

---

## Configuration Standards

### Environment Variable Management (MANDATORY)
- **Source**: ALL configuration MUST come from .env files - NO alternative sources
- **Access**: MUST use `from app.core.config import settings` - NO direct `os.environ`
- **Validation**: ALL configuration MUST use Pydantic BaseSettings with type hints
- **Defaults**: Sensible defaults required for all optional configuration

### Prohibited Configuration Patterns
- **Hardcoded Values**: NO magic numbers or strings in code
- **Runtime Configuration Files**: NO JSON/YAML/INI configuration files
- **Database Configuration**: NO configuration stored in database
- **Command Line Arguments**: NO argparse or CLI configuration

### Configuration Change Authority
- **Who**: Single reviewer model - designated human reviewer ONLY
- **Method**: Direct .env file modification or approved UI configuration interface
- **Validation**: ALL changes MUST be validated before application restart
- **Testing**: Configuration changes MUST be tested in isolation

### Configuration Change Audit (MANDATORY)
- **Logging**: ALL configuration changes MUST be logged with structured event
- **Timestamp**: Precise UTC timestamp required
- **Attribution**: Human identity and rationale required
- **Rollback**: Previous configuration values preserved for rollback capability

### UI-Editable Configuration Constraints
**Permitted**: Threshold values, model selections, timeout values, similarity parameters
**FORBIDDEN**: Database credentials, API keys, system paths, security settings
**Validation**: UI changes MUST be validated server-side before persistence

---

## Logging & Event Standards

### Event Severity Taxonomy (FIXED HIERARCHY)
- **DEBUG**: Detailed execution traces, variable states, development information
- **INFO**: Normal operations, successful state changes, routine business events
- **WARNING**: Concerning conditions, business rule violations, fallback scenarios
- **ERROR**: System failures, exceptions, recoverable errors requiring attention
- **CRITICAL**: Unrecoverable failures, data integrity issues, system-wide problems

### Blocking vs Non-Blocking Events (MANDATORY CLASSIFICATION)
**Blocking Events** (pipeline progression stops):
- OCR confidence below threshold → HITL escalation required
- Corpus boundary violation → Access denied + audit
- Document hash collision → Human resolution required
- Database connection failure → System recovery required

**Non-Blocking Events** (pipeline progression continues):
- Document upload success → Continue processing
- Configuration change → Continue + audit log
- Performance threshold exceeded → Continue + alert
- Agent execution success → Continue processing

### Required Fields for ALL Log Entries (MANDATORY)
- **timestamp**: Precise UTC timestamp with microsecond precision
- **level**: Event severity level from taxonomy
- **message**: Human-readable description
- **request_id**: Correlation ID for request tracing
- **component**: Source component/module name
- **operation**: Specific operation being performed

### Audit Logging Requirements (MANDATORY)
**All audit events MUST include**:
- Human identity (when applicable)
- Resource affected (document, corpus, task, etc.)
- Action taken (created, modified, approved, rejected)
- Rationale (for human decisions)
- Before/after state (for modifications)
- Immutable storage (no audit log modifications permitted)

### Failure Event Capture (MANDATORY)
- **Exception Details**: Full stack trace with business context
- **Recovery Actions**: Attempted recovery steps and results
- **Impact Assessment**: Affected documents, corpora, or operations
- **Escalation Path**: HITL task creation when human intervention required

---

## Versioning Standards

### Prompt Template Versioning (Phase 4+ Requirement)
- **Basic Identification**: Phase 3 templates identified by simple name/timestamp only
- **Phase 4+ Requirements**: Explicit semantic versioning (v1.0, v1.1, etc.)
- **Phase 4+ Immutability**: Templates immutable once used in recorded executions
- **Phase 4+ Version Changes**: Template modifications create new versions
- **Phase 4+ Lineage**: Complete template version chains
- **Phase 4+ Reference Integrity**: Execution logs reference specific template versions

### Diagram Description Versioning (Phase 4+ Requirement)
- **Basic Tracking**: Phase 3 descriptions use simple timestamp/edit tracking
- **Phase 4+ Canonical Versions**: All descriptions versioned with unique identifiers
- **Phase 4+ Reuse References**: Document references specify exact description versions
- **Phase 4+ Non-Destructive Updates**: Updates create new versions, preserve historical
- **Phase 4+ Version Progression**: Parent-child relationships between description versions
- **Phase 4+ Human Approval**: Description version changes require explicit approval

### Agent Output Versioning (Phase 4+ Requirement)
- **Basic Preservation**: Phase 3 agent outputs preserved with timestamps
- **Phase 4+ Artifact Versioning**: All outputs versioned artifacts with unique identifiers
- **Phase 4+ Revision Linkage**: Output revisions linked by lineage chains
- **Phase 4+ No Overwrites**: Original agent outputs preserved permanently
- **Phase 4+ Version Relationships**: Complete audit trail through all revisions
- **Phase 4+ Rationale Capture**: Human changes include rationale and approval

### Lineage Preservation Rules (Phase 4+ Requirement)
- **Basic Tracking**: Phase 3 maintains simple parent-child document relationships
- **Phase 4+ Complete Chains**: Full lineage from original artifact through all versions
- **Phase 4+ Immutable History**: No deletion/modification of historical version records
- **Phase 4+ Cross-Reference Integrity**: Version references remain valid permanently
- **Phase 4+ Audit Completeness**: All version changes logged with complete context

### Phase 3 Essential Versioning (MANDATORY)
- **API Versioning**: Path-based versioning (`/api/v1/`) required for all endpoints
- **Document Lineage**: Basic parent-child relationships for document modifications
- **Timestamp Tracking**: All artifacts timestamped with creation/modification times
- **Simple Preservation**: Original documents and outputs preserved (no overwrites)

---

## Coding & Naming Standards

### Python Conventions (MANDATORY)
- **PEP 8 Compliance**: ALL Python code MUST follow PEP 8 standards
- **Type Hints**: ALL functions and methods MUST include complete type hints
- **Docstrings**: ALL public functions/classes MUST include docstrings
- **Import Organization**: Standard import order (stdlib, third-party, local)
- **Line Length**: 120 character maximum (consistent with AgentRules.md)

### Database Naming Conventions (MANDATORY)
- **Tables**: snake_case naming (e.g., `document_artifacts`, `corpus_permissions`)
- **Columns**: snake_case naming (e.g., `created_timestamp`, `document_hash`)
- **Indexes**: Descriptive names with table prefix (e.g., `idx_documents_created_timestamp`)
- **Foreign Keys**: Consistent naming pattern (e.g., `document_id`, `corpus_id`)
- **Primary Keys**: Use UUIDs via UUIDMixin, avoid integer auto-increment

### API Resource Naming (MANDATORY)
- **Collections**: Plural nouns (e.g., `/documents`, `/corpora`, `/tasks`)
- **Resources**: Singular operations with ID (e.g., `/document/{id}`, `/task/{id}/approve`)
- **Actions**: Verb-based sub-resources (e.g., `/document/{id}/process`, `/task/{id}/escalate`)
- **Relationships**: Clear parent-child structure (e.g., `/corpus/{id}/documents`)

### File & Module Organization (MANDATORY)
- **Module Names**: snake_case for all Python modules
- **Class Names**: PascalCase for all class definitions
- **Function Names**: snake_case for all function definitions
- **Constants**: UPPERCASE for module-level constants
- **Test Files**: MUST be created in `test_files/` directory only

### Variable Naming Domain-Specific Rules
- **IDs**: Suffix with `_id` (e.g., `document_id`, `request_id`)
- **Timestamps**: Suffix with `_timestamp` (e.g., `created_timestamp`, `processed_timestamp`)
- **Flags**: Boolean variables prefixed with `is_` or `has_` (e.g., `is_processed`, `has_errors`)
- **Counts**: Prefix with `num_` or `count_` (e.g., `num_documents`, `count_failures`)

---

## Compliance & Enforcement

### Standards Review Requirements (MANDATORY)
**When Standards Must Be Reviewed**:
- Start of each P3.x task execution
- Before any major code changes
- When introducing new dependencies
- Before production deployment
- During code review process

### Required Compliance Checks Before Task Completion
- [ ] All common services used correctly (no forbidden alternatives)
- [ ] API endpoints follow URL structure and response envelope standards
- [ ] Configuration accessed via Settings class only
- [ ] All logging uses LoggingService interface
- [ ] Versioning rules applied to all artifacts
- [ ] Database naming conventions followed
- [ ] Error handling uses standardized ErrorCode enum

### Relationship to Testing and Verification (P3.12)
- **Standards Validation**: All tests MUST validate standards compliance
- **Integration Tests**: MUST verify common service usage patterns
- **API Tests**: MUST validate response envelope compliance
- **Configuration Tests**: MUST verify Settings class usage
- **Audit Tests**: MUST validate logging and versioning compliance

### Violation Handling Process

**Default Response**: **FATAL - Standards violations STOP implementation by default**

**Exception Process**: Violations may proceed ONLY if ALL conditions met:
1. **Explicit Flag**: Developer explicitly identifies and flags the violation
2. **Written Rationale**: Clear documentation of why violation is necessary  
3. **Human Approval**: Human reviewer approval with documented rationale
4. **Audit Trail**: All exceptions logged with violation details, rationale, and approver

**Prohibited Actions**:
- Silent deviations from standards (automatic failure)
- Auto-fixing standards conflicts without human review
- Implementation proceeding with known violations without approval

### Global Conflict-Handling Rule

**When ANY requirement or design document conflicts with Standards.md**:

**REQUIRED ACTIONS**:
1. **DO NOT auto-fix** - Never automatically resolve conflicts
2. **DO NOT silently override** - No hidden deviations permitted  
3. **FLAG the conflict** - Explicitly identify conflicting requirements
4. **PROVIDE rationale** - Document why conflict exists and implications
5. **PROPOSE options** - Present multiple resolution approaches
6. **AWAIT human decision** - Implementation halts until human resolution

**This conflict-handling rule applies universally and MUST be referenced wherever standards compliance is discussed.**

### Primary Enforcement Audience

**Primary Enforcers**:
- **Copilot Development Agents**: MUST validate standards compliance before proceeding
- **Automated Review Checks**: CI/CD validation where technically feasible  
- **Code Review Process**: Human reviewers verify standards compliance

**Human Override Authority**:
- Humans may review and override standards requirements
- **ALL overrides MUST be explicitly documented with rationale**
- Override decisions become part of permanent project record

### Per-Task Standards Compliance Process

**MANDATORY for every Phase 3 task**:

**Task Documentation Requirements**:
- Task MUST explicitly state: **"Must comply with Standards.md"**
- Task MUST include pre-development reminder: **"Review Standards.md and required common services before implementation"**
- Task MUST include post-development verification: **"Confirm Standards.md compliance checklist completion"**

**Implementation Verification Steps**:
1. **Common Services Usage**: Verify all required common services are properly used
2. **API Standards Compliance**: Confirm response envelopes, error handling, routing patterns
3. **Configuration Standards**: Validate Pydantic BaseSettings usage and environment variable patterns
4. **Logging Standards**: Verify LoggingService interface usage and event taxonomy
5. **ID Generation Standards**: Confirm UUID4 usage for all entity identifiers
6. **Version Management**: Verify semantic versioning compliance
7. **Coding Standards**: Validate naming conventions and structure requirements
8. **Documentation Standards**: Confirm in-code documentation and API documentation

**Checklist Authority**: 
- **Single Source**: This checklist lives ONLY in Standards.md - do not duplicate in individual tasks
- **Reference Pattern**: Tasks reference this checklist, do not copy content
- **Updates**: All checklist modifications happen in Standards.md only

### Enforcement Authority
- **Primary Authority**: Human reviewer has final authority for all standards exceptions
- **Agent Enforcement**: Copilot agents MUST validate standards before proceeding
- **Automated Validation**: CI/CD pipeline SHOULD validate standards where technically possible
- **Code Review**: All code changes MUST be reviewed for standards compliance
- **Documentation**: Standards violations MUST be documented with rationale and approval status
- **Conflict Resolution**: All conflicts with Standards.md MUST follow global conflict-handling rule

---

## Standards Evolution

### Change Process
- Standards changes require human approval with documented rationale
- All changes MUST maintain backward compatibility within Phase 3
- Breaking changes deferred to future phases unless critical
- Change history maintained with complete audit trail

### Version Control
- Standards.md version tracked with semantic versioning
- Major changes require new major version
- Minor clarifications use patch versions
- All changes logged with timestamp and rationale

---

**Status**: AUTHORITATIVE - Ready for Phase 3 Enforcement  
**Authority**: Single Source of Truth for All Technical Standards  
**Last Updated**: January 1, 2026  
**Next Review**: Start of each P3.x task or upon human request