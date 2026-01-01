# Logging and Events Specification

**Status**: APPROVED - Comprehensive Audit + Performance Architecture (Dec 30, 2025)  
**Authority**: Technical implementation guidance for P3.10 Logging and Event System Implementation  
**Logging Standards**: [Standards.md](../Standards.md) - MANDATORY logging service usage, event taxonomy, and audit requirements  
**Cross-References**: [PipelineStateMachine.md](../PipelineStateMachine.md) (state transitions), [CorpusModel.md](../CorpusModel.md) (corpus operations), [AgentResponsibilities.md](../AgentResponsibilities.md) (agent operations), [HITLTaskSpec.md](./HITLTaskSpec.md) (human decision events)

## Authority Relationship

**PipelineStateMachine.md defines EVENTS** (state transition triggers and audit requirements)  
**This specification defines HOW** (technical logging infrastructure and event capture)  
**CorpusModel.md defines BUSINESS EVENTS** (corpus boundary violations and isolation events)  
**BuildPlan.md P3.10 defines EXECUTION** (implementation tasks and acceptance criteria)

## Purpose

Defines technical implementation of comprehensive logging, event capture, audit trails, performance monitoring, and debugging infrastructure for patent intelligence system with strict provenance and compliance requirements.

## Required Content (Minimum Specification)

### Logging Architecture

#### Log Levels & Categories
- **ERROR**: System failures, exceptions, unrecoverable errors
- **WARN**: Business rule violations, fallback scenarios, concerning conditions
- **INFO**: System operations, state changes, normal business events
- **DEBUG**: Detailed execution traces, variable states, control flow
- **TRACE**: Maximum detail for development and troubleshooting

#### Log Destinations
- **File Logging**: Structured log files with rotation and archival
- **Database Logging**: Critical events stored in PostgreSQL for querying
- **Console Logging**: Development and debugging output
- **Structured Logging**: JSON format for automated processing and analysis
- **Performance Logging**: Separate high-frequency performance metrics stream

### Event System Design

#### Event Categories
- **System Events**: Application startup, shutdown, configuration changes
- **Security Events**: Authentication, authorization, access control violations
- **Business Events**: Document processing, corpus operations, agent executions
- **Performance Events**: Response times, resource utilization, bottlenecks
- **Error Events**: Exceptions, failures, recovery attempts

#### Event Structure
- **Timestamp**: Precise UTC timestamp with microsecond resolution
- **Event Type**: Hierarchical event classification (system.startup, business.document.processed)
- **Actor**: User, agent, or system component generating the event
- **Resource**: Document, corpus, task, or system resource involved
- **Context**: Additional metadata, parameters, and contextual information
- **Correlation ID**: Request/transaction correlation across multiple events

## Event Severity Taxonomy

### Fixed Severity Classification

#### Severity Levels (Fixed Hierarchy)
- **DEBUG**: Detailed execution traces, variable states, development information
- **INFO**: Normal system operations, successful state changes, routine business events
- **WARNING**: Concerning conditions, business rule violations, fallback scenarios triggered
- **ERROR**: System failures, exceptions, recoverable errors requiring attention
- **CRITICAL**: Unrecoverable failures, data integrity issues, system-wide problems

#### Severity Assignment Rules
- **Configuration Changes**: INFO level with audit trail enhancement
- **Corpus Boundary Violations**: WARNING level with immediate alerting
- **Document Processing Failures**: ERROR level with retry capability assessment
- **Database Connection Failures**: CRITICAL level with immediate escalation
- **Agent Permission Violations**: WARNING level with security audit enhancement

### Blocking vs Non-Blocking Events

#### Event Impact Classification

| Event Type | Pipeline Impact | HITL Escalation | Continuation |
|------------|----------------|-----------------|--------------|
| **Document Upload Success** | Non-Blocking | No | Continue |
| **OCR Low Confidence** | Blocking | Yes | Human Decision Required |
| **Corpus Access Violation** | Blocking | Yes | Deny + Audit |
| **Configuration Change** | Non-Blocking | No | Continue + Log |
| **Database Connection Lost** | Blocking | Yes | System Recovery Required |
| **Agent Execution Success** | Non-Blocking | No | Continue |
| **Diagram Classification Ambiguous** | Blocking | Yes | Human Classification Required |
| **Similarity Threshold Changed** | Non-Blocking | No | Continue + Audit |
| **Document Hash Collision** | Blocking | Yes | Human Resolution Required |
| **Performance Threshold Exceeded** | Non-Blocking | No | Continue + Alert |

#### Pipeline Progression Rules
- **Blocking Events**: Pipeline state remains unchanged until resolution
- **Non-Blocking Events**: Pipeline progression continues with event logging
- **HITL Escalation Events**: Create structured human tasks per HITLTaskSpec.md
- **Informational Events**: Logged for audit and monitoring, no action required

- **Correlation ID**: Request/transaction correlation across multiple events

### Audit Trail Requirements

#### Complete Provenance Tracking
- **Document Lifecycle**: Every document state change with actor and rationale
- **Corpus Operations**: All corpus creation, modification, access, and isolation events
- **Agent Executions**: Complete agent conversation logs with input/output capture
- **Human Decisions**: All HITL task decisions with rationale and evidence
- **Configuration Changes**: System settings modifications with before/after values

#### Compliance Events
- **Access Control**: Every access attempt with success/failure and authorization context
- **Data Lineage**: Complete chain of document transformations and dependencies
- **Business Rule Enforcement**: Corpus isolation violations, rule exceptions, overrides
- **Quality Control**: Validation failures, data integrity issues, correction events
- **Administrative Actions**: System administration, user management, privilege changes

### Performance Monitoring

#### System Performance Metrics
- **Response Times**: API endpoint performance with percentile distributions
- **Resource Utilization**: CPU, memory, disk, GPU usage patterns
- **Database Performance**: Query performance, connection pooling, transaction times
- **Document Processing**: OCR times, embedding generation, pipeline throughput
- **Agent Performance**: LLM response times, RAG retrieval performance, conversation latency

#### Business Performance Metrics
- **Document Processing Rates**: Ingestion throughput, processing completion rates
- **Quality Metrics**: OCR accuracy, duplicate detection rates, classification performance
- **Human Task Metrics**: HITL task completion times, decision quality, escalation rates
- **Agent Effectiveness**: Successful query resolutions, accuracy metrics, user satisfaction
- **System Reliability**: Uptime, error rates, recovery times, data consistency

### Error Handling & Recovery

#### Error Classification
- **Transient Errors**: Temporary failures with automatic retry strategies
- **Permanent Errors**: Business rule violations, data quality issues, user errors
- **System Errors**: Infrastructure failures, database connectivity, resource exhaustion
- **Data Errors**: Corruption, inconsistency, validation failures, format issues
- **Security Errors**: Unauthorized access, authentication failures, privilege violations

#### Recovery Procedures
- **Automatic Recovery**: Retry logic, fallback strategies, circuit breakers
- **Manual Recovery**: Administrative intervention, data repair, system restoration
- **Recovery Logging**: Complete recovery process documentation with success/failure tracking
- **Data Consistency**: Transaction rollback, compensating actions, consistency verification
- **Notification Systems**: Alert administrators for critical errors requiring intervention

### Development & Debugging Support

#### Debug Information Capture
- **Request Tracing**: Complete request lifecycle with intermediate states
- **Variable State**: Critical variable values at decision points
- **Execution Flow**: Control flow through complex business logic
- **Exception Context**: Stack traces with business context and environmental state
- **Performance Profiling**: Detailed execution time breakdowns for optimization

#### Log Analysis & Search
- **Structured Query**: Search logs by timestamp, actor, event type, resource
- **Correlation Analysis**: Follow request correlation IDs across multiple services
- **Pattern Detection**: Identify recurring errors, performance patterns, unusual behavior
- **Statistical Analysis**: Aggregate metrics, trend analysis, anomaly detection
- **Export Capabilities**: Log export for external analysis tools and compliance reporting

### Privacy & Security

#### Sensitive Data Handling
- **Data Minimization**: Log only necessary information for business and audit purposes
- **Data Redaction**: Automatic redaction of sensitive content in logs
- **Access Control**: Role-based access to different log categories and detail levels
- **Retention Policies**: Automatic log cleanup with compliance retention requirements
- **Encryption**: Log encryption for sensitive audit and security information

#### Audit Log Integrity
- **Tamper Protection**: Cryptographic signatures for audit log integrity
- **Append-Only**: Audit logs cannot be modified or deleted after creation
- **Backup Requirements**: Regular audit log backups with integrity verification
- **Access Auditing**: All audit log access tracked and monitored
- **Compliance Reporting**: Automated compliance report generation from audit logs

### Integration with System Components

#### Pipeline State Machine Integration
- **State Transition Events**: Every state change logged with before/after states
- **Transition Triggers**: Log events that triggered state transitions
- **Failed Transitions**: Document blocked states with complete failure context
- **State Validation**: Log state consistency checks and validation results
- **Recovery Events**: Log state recovery and correction procedures

#### Corpus Model Integration
- **Corpus Boundary Events**: Log all corpus access attempts and violations
- **Isolation Enforcement**: Log corpus isolation rule enforcement and exceptions
- **Cross-Corpus Operations**: Log any operations involving multiple corpora
- **Permission Changes**: Log corpus permission modifications with rationale
- **Audit Queries**: Support compliance queries about corpus access patterns

#### Agent Framework Integration
- **Agent Execution Logs**: Complete agent conversation and decision logs
- **Permission Enforcement**: Log agent-corpus access control decisions
- **Performance Metrics**: Agent response times, accuracy, resource utilization
- **Error Handling**: Agent failure modes, recovery attempts, escalation events
- **Conversation Context**: Maintain complete agent conversation history for audit

## Design Decisions (APPROVED)

### Logging Infrastructure
- [x] **Structured JSON Logging**: Machine-readable logs with consistent schema
- [x] **PostgreSQL Audit Storage**: Critical events stored in database for querying
- [x] **File + Database Hybrid**: Performance logs to files, audit events to database
- [x] **Local Storage Only**: No external logging services or cloud log aggregation

### Event Processing
- [x] **Synchronous Logging**: Critical events logged synchronously for consistency
- [x] **Asynchronous Performance Logs**: High-frequency metrics logged asynchronously
- [x] **Correlation ID Tracking**: Request correlation across all system components
- [x] **Configurable Detail Levels**: Runtime log level configuration without restart

## Implementation Guidance

### Python Logging Integration
- Python standard logging library with structured formatters
- Log rotation and archival with automatic cleanup policies
- Custom log handlers for database integration and correlation ID injection
- Performance-optimized logging for high-frequency events

### Configuration Architecture
- **All tunable values** (log levels, retention periods, alert thresholds) sourced from .env files
- **Loaded via Pydantic BaseSettings** with validation and environment-specific defaults
- **Configuration changes allowed by the single reviewer** through administrative interface
- **Configuration changes must be logged, timestamped, and attributed** as configuration change events
- **No runtime hardcoding of tunable values** - all logging behavior controlled through configuration

### Database Audit Schema
- Audit events table with indexed timestamp, actor, and event type columns
- JSON column for flexible event metadata storage
- Partitioning strategy for large-scale audit log management
- Query optimization for common audit and compliance queries

### FastAPI Integration
- Request/response logging middleware with correlation ID generation
- Exception logging with full request context and stack traces
- Performance timing middleware for all API endpoints
- Security event logging for authentication and authorization

### Configuration Management
- Runtime log level configuration with hot reloading
- Environment-specific logging configurations (development, production)
- Sensitive data redaction rules configurable per environment
- Performance vs audit detail trade-off configuration

## Acceptance Criteria

- [ ] Complete document lifecycle events logged with actor and rationale
- [ ] All corpus operations logged with isolation enforcement audit trail
- [ ] Agent executions logged with input/output and performance metrics
- [ ] HITL task decisions logged with evidence and rationale preservation
- [ ] State machine transitions logged with before/after states and triggers
- [ ] Performance metrics captured for all critical system operations
- [ ] Error events include complete context for debugging and recovery
- [ ] Audit logs support compliance queries and regulatory reporting
- [ ] Log analysis supports troubleshooting and performance optimization
- [ ] Sensitive data automatically redacted in logs with access controls
- [ ] Log integrity protected with tamper-evident audit trails
- [ ] Correlation IDs enable request tracing across all system components

---

**Status**: SPECIFICATION COMPLETE - Ready for P3.10 Implementation  
**Approved**: JSON + PostgreSQL + Local File Architecture (Dec 30, 2025)