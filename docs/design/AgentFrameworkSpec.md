# Agent Framework Specification

**Status**: APPROVED - PyTorch+Transformers Decision Confirmed (Dec 30, 2025)  
**Authority**: Implementation guidance for P3.7 Agent Execution Framework, P3.8 Core Agent Implementations  
**Cross-References**: [AgentResponsibilities.md](../../AgentResponsibilities.md), [DevelopmentEnvironment.md](../../DevelopmentEnvironment.md), [CorpusEnforcementSpec.md](./CorpusEnforcementSpec.md)

## Purpose

Defines LLM provider abstraction, prompt management, schema validation, retry strategies, and agent boundary enforcement for patent intelligence agents.

## Required Content (Minimum Specification)

### LLM Provider Abstraction

#### Local LLM Integration (APPROVED APPROACH)
- [x] **PyTorch/Transformers**: Direct integration for local-only inference
- [x] **Model loading**: Explicit model loading and memory management control
- [x] **GPU resource allocation**: Single-process GPU usage on RTX-5090
- [x] **Memory management**: Optimized for 96GB RAM configuration
- [x] **No service dependencies**: Avoids vLLM or external inference services
- [x] **Compatibility control**: Better debuggability and library compatibility

#### Provider Interface
- [ ] Standard completion API (prompt → response)
- [ ] Embedding generation API (text → vectors)
- [ ] Configuration injection (temperature, max_tokens, etc.)
- [ ] Error handling and timeout management

#### Hardware Optimization
- [ ] RTX-5090 optimization patterns
- [ ] Memory management for 96GB RAM configuration
- [ ] Concurrent agent execution resource sharing
- [ ] Model caching and lazy loading strategies

### Prompt Registry & Versioning

#### Prompt Templates
- [ ] Agent-specific prompt template storage
- [ ] Parameter injection and validation
- [ ] Template versioning and rollback capabilities
- [ ] UI-editable prompt support (Phase 4 preparation)

#### Prompt Assembly Pipeline
- [ ] Context assembly with corpus boundaries
- [ ] Evidence bundle integration
- [ ] Few-shot example injection
- [ ] Token limit management and truncation

## Versioning Policy

### Prompt Templates

#### Template Versioning Rules
- **Prompt templates are versioned explicitly** with semantic version identifiers
- **Prompt templates are immutable once used in a recorded agent execution**
- **Changes to prompt templates result in a new version identifier** (e.g., v1.0 → v1.1)
- **Historical prompt template versions are preserved** for audit and reproduction

#### Version Management
- **Active Version**: Current template version used for new agent executions
- **Historical Versions**: All previous versions retained for lineage tracing
- **Version References**: Agent execution logs reference specific prompt template versions
- **Rollback Capability**: Previous template versions can be reactivated if needed

### Diagram Descriptions

#### Canonical Description Versioning
- **Canonical descriptions are versioned** with unique version identifiers
- **Reuse references a specific version** of the canonical description
- **Updates do not overwrite historical versions** - new versions created instead
- **Version Lineage**: Clear chain from original to current description version

#### Description Evolution
- **Incremental Updates**: Minor corrections create patch versions (v1.0 → v1.0.1)
- **Substantial Changes**: Major revisions create minor versions (v1.0 → v1.1)
- **Human Approval**: All description version changes require human approval
- **Cross-Reference Updates**: Document references specify exact description version

### Agent Outputs

#### Output Versioning Rules
- **All agent outputs are versioned artifacts** with unique identifiers
- **Revisions create new outputs linked by lineage** - no destructive overwrites
- **No destructive overwrites** - all agent outputs preserved permanently
- **Version Relationships**: Clear parent-child relationships between output versions

#### Output Evolution Tracking
- **Original Output**: Initial agent response with v1.0 identifier
- **Revised Outputs**: Human-requested revisions create v1.1, v1.2, etc.
- **Lineage Preservation**: Complete chain from original through all revisions
- **Audit Completeness**: All version changes logged with rationale and human identity

### Schema Validation of Outputs

#### Response Schemas
- [ ] Agent-specific output schema definitions
- [ ] Pydantic validation models
- [ ] Structured output parsing (JSON, XML)
- [ ] Free-form text validation patterns

#### Validation Pipeline
- [ ] Real-time output validation during generation
- [ ] Post-processing validation and cleanup
- [ ] Schema violation handling and retry logic
- [ ] Output quality scoring and filtering

### Retry & Idempotency Strategy

#### Failure Categories
- [ ] Transient failures (network, model loading)
- [ ] Content policy violations
- [ ] Invalid output format errors
- [ ] Timeout and resource exhaustion

#### Retry Logic
- [ ] Exponential backoff strategies
- [ ] Maximum retry attempt limits
- [ ] Circuit breaker patterns for systematic failures
- [ ] Degraded service mode operation

#### Idempotency Controls
- [ ] Request deduplication mechanisms
- [ ] Deterministic output guarantees
- [ ] State consistency during retries
- [ ] Partial completion recovery

### Agent Boundary Enforcement

#### Corpus Access Controls
- [ ] Agent-to-corpus permission matrix
- [ ] Runtime corpus boundary validation
- [ ] Input context corpus consistency checks
- [ ] Output corpus compliance verification

#### Execution Isolation
- [ ] Agent execution sandbox patterns
- [ ] Resource limit enforcement per agent
- [ ] Inter-agent communication prevention
- [ ] State isolation and cleanup procedures

#### Authority Enforcement
- [ ] Agent responsibility scope validation
- [ ] Unauthorized capability prevention
- [ ] Output authority level checking
- [ ] Escalation and review triggers

## Design Decisions (APPROVED)

1. **Local LLM Stack**: **PyTorch + Transformers** (direct integration, no vLLM service)
   - **Rationale**: Preference for local-only inference; avoids service orchestration complexity; better debuggability; fits RTX-5090 + high-RAM workstation; reduces compatibility issues
   - **Constraints**: Single-process GPU usage; explicit model loading/memory control; no hosted/remote inference

2. **Model Selection**: 70B models with quantization support
3. **Prompt Storage**: Database-based with versioning support
4. **Validation Strategy**: Comprehensive output validation with schema enforcement

## Implementation Guidance

### Core Framework Classes
```python
# Abstract interfaces to implement
class LLMProvider:
    async def generate_completion(prompt: str, config: dict) -> str
    async def generate_embeddings(text: str) -> List[float]

class AgentExecutor:
    async def execute_agent(agent_id: str, input_data: dict) -> dict

class PromptRegistry:
    def get_template(agent_id: str, version: str) -> str
    def validate_parameters(template: str, params: dict) -> bool
```

### Integration Points
- FastAPI async endpoint integration
- SQLAlchemy session management for agent runs
- Common services integration (logging, context, provenance)
- Pipeline state machine trigger integration

## Acceptance Criteria

- [ ] Local LLM integration fully functional
- [ ] Prompt registry operational with versioning
- [ ] Output validation comprehensive and reliable
- [ ] Retry strategies tested under failure conditions
- [ ] Agent boundaries enforced at runtime
- [ ] Performance meets hardware capability expectations
- [ ] Human reviewer approval obtained

---

**Status**: SPECIFICATION COMPLETE - Ready for P3.7-P3.8 Implementation
**Approved**: PyTorch + Transformers Direct Integration (Dec 30, 2025)