# UI Specification

**Status**: APPROVED - FastAPI Server-Rendered + HTMX Architecture (Dec 30, 2025)  
**Authority**: Technical implementation guidance for P3.11 User Interface Implementation  
**Cross-References**: [HITLTaskSpec.md](./HITLTaskSpec.md) (human task interfaces), [AgentResponsibilities.md](../AgentResponsibilities.md) (agent interaction interfaces), [CorpusModel.md](../CorpusModel.md) (corpus management interfaces), [PipelineStateMachine.md](../PipelineStateMachine.md) (document state visualization)

## Authority Relationship

**HITLTaskSpec.md defines USER WORKFLOWS** (human-in-the-loop task interfaces)  
**This specification defines HOW** (technical UI implementation and user experience)  
**AgentResponsibilities.md defines AGENT INTERFACES** (agent conversation and control interfaces)  
**BuildPlan.md P3.11 defines EXECUTION** (implementation tasks and acceptance criteria)

## Purpose

Defines technical implementation of user interfaces for document management, human-in-the-loop tasks, agent interactions, system administration, and monitoring using FastAPI server-rendered HTML with HTMX for interactivity.

## Required Content (Minimum Specification)

### Architecture Foundation

#### Core Document Management UI
- **Document Management Interface**: CRUD operations for documents using existing SoftDeleteMixin
- **Version Comparison**: Before/after views for document operations using existing DocumentVersion
- **Image State Management**: Mark images as ignored/duplicate with reason tracking

#### FastAPI + Jinja2 Template Engine
- **Server-Side Rendering**: HTML generated server-side with Jinja2 templates
- **Template Inheritance**: Base templates for consistent layout and styling
- **Template Context**: Dynamic data binding from FastAPI route handlers
- **Static Assets**: CSS, JavaScript, images served through FastAPI static files
- **Form Handling**: Server-side form processing with validation and error display

#### HTMX Integration
- **Partial Page Updates**: HTMX for dynamic content updates without full page reload
- **Form Submissions**: Asynchronous form submission with inline validation
- **Progressive Enhancement**: Functional without JavaScript, enhanced with HTMX
- **WebSocket Integration**: Real-time updates for long-running tasks and notifications
- **URL Management**: Clean URLs with proper browser history and navigation

#### No React/SPA Architecture
- **Simplified Stack**: No Node.js, webpack, or React build pipeline
- **Server-Side State**: Application state managed server-side with session storage
- **Direct Integration**: Direct FastAPI route handlers without API layer separation
- **SEO Friendly**: Server-rendered content fully indexable and accessible
- **Performance**: Reduced client-side complexity and faster initial page loads

## UI Authority Constraints

### UI Role and Limitations

#### UI Authority Boundaries
- **The UI performs no reasoning** - all logic and decisions are server-side
- **The UI cannot bypass pipeline rules** - all pipeline constraints enforced server-side
- **The UI cannot modify corpus access rules** - corpus boundaries are system-enforced
- **The UI cannot override agent boundaries** - agent permissions are system-managed
- **The UI cannot directly write claim text** - all claim generation is agent-performed

#### Allowed UI Functions
- **Viewer**: Display system state, documents, and processing results
- **Task Executor (HITL)**: Execute human-in-the-loop tasks with structured input
- **Configuration Surface**: Modify explicitly allowed configuration values (thresholds, settings)
- **Navigation**: Provide user interface for system navigation and operation

#### Server-Side Validation
- **All actions initiated from the UI are validated server-side** before execution
- **Client-side validation is for user experience only** - never relied upon for security
- **Authorization checks performed on every UI-initiated action**
- **Business rule enforcement occurs at the server layer**
- **UI state changes reflect server-authoritative state only**

### Document Management Interface

#### Document Upload & Ingestion
- **Drag-and-Drop Upload**: Modern file upload interface with progress tracking
- **Batch Upload**: Multiple document upload with individual progress and status
- **Upload Validation**: Client-side and server-side file validation and error display
- **Metadata Entry**: Document classification, source, and initial metadata capture
- **Upload Progress**: Real-time upload progress with cancellation capability

#### Document Library & Search
- **Document Grid**: Responsive card-based document browsing with thumbnails
- **Advanced Search**: Full-text search, metadata filtering, date ranges, corpus filtering
- **Search Results**: Relevance ranking with snippet highlighting and metadata display
- **Document Preview**: In-browser document preview with page navigation
- **Bulk Operations**: Multi-select for batch operations (corpus assignment, deletion)

#### Document Detail Views
- **Metadata Display**: Comprehensive document metadata with edit capabilities
- **Processing Status**: Pipeline state visualization with progress indicators
- **Extracted Content**: OCR results, diagram extractions, and text content display
- **Provenance Chain**: Complete document lineage and processing history
- **Related Documents**: Similar documents, citations, and cross-references

### HITL Task Interface

#### Task Queue & Assignment
- **Task Dashboard**: Personal task queue with priority, type, and age indicators
- **Task Filtering**: Filter by task type, corpus, urgency, and assignment status
- **Task Assignment**: Manual task assignment to specific human reviewers
- **Workload Balancing**: Visual workload distribution across available reviewers
- **Task Escalation**: Interface for escalating complex or blocked tasks

#### Task Execution Interface
- **Context Display**: Complete task context with supporting documents and evidence
- **Side-by-Side Comparison**: Document comparison interface for duplicate detection
- **Annotation Tools**: Text highlighting, note-taking, and markup capabilities
- **Decision Recording**: Structured decision capture with rationale requirements
- **Quality Assurance**: Decision validation and confirmation workflows

#### Task Completion & Review
- **Decision Summary**: Clear summary of decisions made with rationale display
- **Task History**: Complete task execution history with time tracking
- **Quality Metrics**: Task completion quality scoring and feedback
- **Batch Review**: Bulk review and approval for similar task types
- **Training Integration**: Link task decisions to training materials and guidelines

### Agent Interaction Interface

#### Agent Conversation View
- **Chat Interface**: Clean conversation interface with agent and user messages
- **Message Threading**: Conversation organization with thread management
- **Agent Selection**: Interface for selecting and switching between available agents
- **Context Display**: Current agent context, corpus access, and conversation state
- **Conversation Export**: Export conversations for analysis and documentation

#### Agent Management & Configuration
- **Agent Dashboard**: Agent status, performance metrics, and health monitoring
- **Permission Management**: Agent-corpus access control configuration interface
- **Conversation History**: Historical conversation logs with search and filtering
- **Agent Performance**: Response times, accuracy metrics, and usage patterns
- **Agent Configuration**: Agent-specific settings and parameter configuration

### Corpus Management Interface

#### Corpus Creation & Configuration
- **Corpus Wizard**: Guided corpus creation with validation and configuration
- **Access Control Configuration**: Visual interface for corpus permission management
- **Corpus Hierarchy**: Tree view for corpus organization and relationships
- **Isolation Rules**: Interface for configuring and validating isolation requirements
- **Bulk Operations**: Mass corpus assignment and permission updates

#### Corpus Monitoring & Audit
- **Corpus Analytics**: Document counts, processing status, and health metrics
- **Access Audit**: Complete audit trail of corpus access and permission changes
- **Violation Reporting**: Corpus isolation violation detection and reporting
- **Cross-Corpus Analysis**: Tools for analyzing cross-corpus relationships
- **Compliance Dashboard**: Regulatory compliance status and audit preparation

### System Administration Interface

#### System Health & Monitoring
- **System Dashboard**: Overall system health, performance, and status indicators
- **Resource Monitoring**: CPU, memory, disk, GPU utilization with historical trends
- **Pipeline Monitoring**: Document processing pipeline status and throughput metrics
- **Error Monitoring**: System errors, exceptions, and resolution status
- **Performance Analytics**: Response times, query performance, and bottleneck analysis

#### Audit Log Management
- **Audit Log Viewer**: Real-time and historical audit event browsing with filtering
- **Message Filtering**: User-controlled filtering of repetitive/noisy audit messages
  - **Filter This Message**: One-click filtering of specific audit events
  - **Show All Messages**: Toggle to display all messages including filtered ones
  - **Filter Management**: View, edit, and remove existing message filters
  - **Filter Rationale**: Required justification for filtering audit messages
- **Event Search**: Full-text search and advanced filtering of audit events
- **Export Functionality**: Export audit logs for compliance and analysis
- **Correlation Tracking**: Trace related events using correlation and trace IDs

#### User & Permission Management
- **User Administration**: User account creation, modification, and deactivation
- **Role Management**: Role-based access control configuration and assignment
- **Permission Audit**: Complete audit of user permissions and access patterns
- **Session Management**: Active user sessions with forced logout capability
- **Security Monitoring**: Authentication attempts, security violations, and alerts

### Responsive Design & Accessibility

#### Mobile & Tablet Support
- **Responsive Layout**: Adaptive layout for desktop, tablet, and mobile devices
- **Touch Interface**: Touch-optimized controls for tablet and mobile usage
- **Performance Optimization**: Optimized for slower connections and limited bandwidth
- **Offline Capability**: Basic offline functionality for critical operations
- **Progressive Web App**: PWA features for app-like mobile experience

#### Accessibility Compliance
- **WCAG 2.1 AA**: Full compliance with accessibility standards
- **Screen Reader Support**: Proper semantic HTML and ARIA attributes
- **Keyboard Navigation**: Complete keyboard accessibility for all interfaces
- **High Contrast**: Support for high contrast modes and visual accessibility
- **Internationalization**: UTF-8 support and localization framework

### Real-Time Updates & Notifications

#### WebSocket Integration
- **Task Notifications**: Real-time notifications for new tasks and assignments
- **Processing Updates**: Live updates for document processing status
- **System Alerts**: Real-time system alerts and maintenance notifications
- **Agent Status**: Live agent availability and conversation status updates
- **Collaborative Features**: Real-time updates for multi-user task collaboration

#### Notification System
- **In-App Notifications**: Toast notifications for important events and updates
- **Email Notifications**: Configurable email alerts for critical events
- **Notification History**: Historical notification log with read/unread status
- **Notification Preferences**: User-configurable notification settings and channels
- **Alert Escalation**: Automatic escalation for unacknowledged critical alerts

### Performance & User Experience

#### Page Load Optimization
- **Fast Initial Load**: Optimized initial page load with critical CSS inline
- **Lazy Loading**: Progressive loading of non-critical content and images
- **Caching Strategy**: Appropriate browser caching for static assets and templates
- **Compression**: Gzip compression for HTML, CSS, and JavaScript assets
- **CDN Integration**: Optional CDN support for static asset delivery

#### User Experience Patterns
- **Consistent Navigation**: Standard navigation patterns across all interfaces
- **Loading States**: Clear loading indicators for all asynchronous operations
- **Error Handling**: User-friendly error messages with recovery suggestions
- **Confirmation Dialogs**: Appropriate confirmation for destructive operations
- **Keyboard Shortcuts**: Power user keyboard shortcuts for common operations

## Design Decisions (APPROVED)

### Technology Stack
- [x] **FastAPI + Jinja2**: Server-side rendered HTML with template inheritance
- [x] **HTMX for Interactivity**: Progressive enhancement without React complexity
- [x] **No SPA Architecture**: Server-rendered pages with targeted dynamic updates
- [x] **Single Reviewer Model**: No authentication system, direct human reviewer interface

### UI Architecture
- [x] **Local-First**: All UI served from FastAPI application server
- [x] **Database-Driven**: UI state and preferences stored in PostgreSQL
- [x] **Responsive Design**: Mobile-friendly responsive layout
- [x] **Accessibility First**: WCAG 2.1 AA compliance from initial implementation

## Implementation Guidance

### FastAPI Template Setup
- Jinja2 template engine configuration with template inheritance
- Static file serving for CSS, JavaScript, and image assets
- Form handling with Pydantic validation and error display
- Session management for user state and preferences

### HTMX Integration Patterns
- Partial page updates for dynamic content refresh
- Form submission with inline validation and error display
- WebSocket integration for real-time updates and notifications
- Progressive enhancement ensuring functionality without JavaScript

### Bootstrap or Similar CSS Framework
- Responsive grid system for adaptive layout
- Component library for consistent UI elements
- Customizable theme for patent intelligence domain
- Accessibility-compliant components and interactions

### Database-Driven UI State
- User preferences and settings stored in PostgreSQL
- Session state management with database persistence
- UI configuration and customization stored server-side
- Performance optimization for UI data queries

## Acceptance Criteria

- [ ] Document upload interface with drag-and-drop and progress tracking
- [ ] HITL task interface displays context and captures decisions with rationale
- [ ] Agent conversation interface enables natural language interaction
- [ ] Corpus management interface provides access control and monitoring
- [ ] System administration interface shows health, performance, and user management
- [ ] Responsive design works on desktop, tablet, and mobile devices
- [ ] WCAG 2.1 AA accessibility compliance verified with automated testing
- [ ] Real-time updates delivered via WebSocket for task notifications
- [ ] All interfaces render server-side with HTMX progressive enhancement
- [ ] Performance optimized with fast initial load and efficient updates
- [ ] Error handling provides clear user feedback and recovery options
- [ ] No React/SPA complexity, pure FastAPI + Jinja2 + HTMX implementation

---

**Status**: SPECIFICATION COMPLETE - Ready for P3.11 Implementation  
**Approved**: FastAPI + Jinja2 + HTMX Server-Rendered Architecture (Dec 30, 2025)