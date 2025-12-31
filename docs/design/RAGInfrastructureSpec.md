# RAG Infrastructure Specification

**Status**: APPROVED - PyTorch + Transformers Local-First Architecture (Dec 30, 2025)  
**Authority**: Technical implementation guidance for P3.6 RAG Infrastructure Implementation  
**Cross-References**: [CorpusModel.md](../CorpusModel.md) (corpus isolation requirements), [AgentResponsibilities.md](../AgentResponsibilities.md) (agent-specific retrieval permissions), [DataFlowDiagram.md](../DataFlowDiagram.md) (RAG flow stages), [DatabaseSchemaSpec.md](./DatabaseSchemaSpec.md) (vector storage schema)

## Authority Relationship

**CorpusModel.md defines BUSINESS RULES** (corpus isolation and cross-contamination prevention)  
**This specification defines HOW** (technical RAG infrastructure and vector operations)  
**AgentResponsibilities.md defines ACCESS CONTROL** (agent-specific retrieval permissions)  
**BuildPlan.md P3.6 defines EXECUTION** (implementation tasks and acceptance criteria)

## Purpose

Defines technical implementation of Retrieval-Augmented Generation (RAG) infrastructure including embedding generation, vector storage, similarity search, and corpus-aware retrieval for patent intelligence agents.

## Required Content (Minimum Specification)

### Embedding Model Integration

#### Local Model Management
- **Model Selection**: Sentence-BERT or similar transformer for patent domain
- **Model Configuration**: Config-driven model selection without hardcoding
- **Model Loading**: Lazy loading with memory management for GPU/CPU hybrid
- **Model Caching**: Efficient model reuse across multiple retrieval operations
- **Memory Optimization**: Batch processing for large document collections

#### Embedding Generation
- **Text Preprocessing**: Patent-specific text normalization and cleaning
- **Chunk Strategy**: Semantic chunking for patent claims, descriptions, diagrams
- **Batch Processing**: Efficient batch embedding generation for document ingestion
- **Quality Validation**: Embedding dimension validation and NaN detection
- **Performance Metrics**: Embedding generation speed and resource utilization

#### Embedding Storage & Retrieval
- **Vector Database Integration**: pgvector extension in PostgreSQL for vector storage
- **Index Optimization**: HNSW or IVF indices for fast similarity search
- **Dimension Management**: Consistent embedding dimension handling and validation
- **Batch Operations**: Efficient bulk embedding insertion and updates
- **Storage Efficiency**: Embedding compression and storage optimization

### Corpus-Aware Vector Search

#### Isolation Enforcement
- **Corpus Filtering**: Vector search respects corpus isolation boundaries
- **Permission Validation**: Agent-specific corpus access control at query time
- **Cross-Contamination Prevention**: Strict enforcement of corpus separation rules
- **Audit Logging**: All retrieval operations logged with corpus context
- **Error Handling**: Clear failures when attempting unauthorized corpus access

#### Search Strategy Implementation
- **Similarity Thresholds**: Configurable relevance scoring for result filtering
- **Result Ranking**: Hybrid scoring combining semantic similarity and relevance
- **Result Diversity**: Duplicate content detection and diverse result selection
- **Context Window Management**: Optimal token usage for LLM context limits
- **Performance Optimization**: Fast retrieval for interactive agent operations

### Query Processing Pipeline

#### Query Analysis & Enhancement
- **Intent Recognition**: Agent query type classification for retrieval strategy
- **Query Expansion**: Patent terminology expansion and synonym handling
- **Semantic Parsing**: Technical concept extraction from natural language queries
- **Context Integration**: Previous conversation context for enhanced retrieval
- **Quality Assessment**: Query clarity and specificity evaluation

#### Retrieval Strategy Selection
- **Keyword vs Semantic**: Hybrid retrieval combining exact match and semantic similarity
- **Document Type Filtering**: Target specific document types (claims, specifications, diagrams)
- **Temporal Filtering**: Patent date ranges and timeline-based retrieval
- **Cross-Reference Following**: Following citation networks and related documents
- **Specialized Searches**: Prior art, claim language, technical specification searches

### Vector Index Management

#### Index Creation & Maintenance
- **Index Build Strategy**: Incremental index updates for new document ingestion
- **Index Optimization**: Regular index reorganization for query performance
- **Index Validation**: Embedding quality checks and index integrity verification
- **Index Backup**: Vector index backup and recovery procedures
- **Index Monitoring**: Performance metrics and index health monitoring

#### Similarity Search Optimization
- **Distance Metrics**: Cosine similarity, Euclidean distance selection by use case
- **Search Algorithms**: HNSW, Flat, IVF algorithm selection based on corpus size
- **Result Caching**: Frequently accessed embeddings cached for performance
- **Query Optimization**: Query plan optimization for complex corpus-aware searches
- **Resource Management**: GPU/CPU utilization optimization for embedding operations

### Result Post-Processing

#### Relevance Scoring & Filtering
- **Semantic Similarity**: Primary relevance scoring based on embedding distance
- **Content Quality**: Document quality and completeness scoring
- **Recency Weighting**: Patent date relevance for temporal queries
- **Cross-Reference Scoring**: Citation network importance for ranking
- **Threshold Enforcement**: Configurable minimum relevance thresholds

#### Context Assembly
- **Document Snippets**: Relevant text extraction with context preservation
- **Metadata Integration**: Patent metadata, dates, inventors, assignees
- **Cross-Reference Linking**: Related documents and citation information
- **Provenance Tracking**: Full retrieval path and decision audit trail
- **Format Optimization**: LLM-optimized context formatting and token efficiency

### Agent Integration Framework

#### Permission-Based Retrieval
- **Agent Authentication**: Agent identity verification for corpus access control
- **Corpus Permission Matrix**: Agent-specific allowed/forbidden corpus combinations
- **Runtime Permission Checks**: Real-time access control validation
- **Audit Trail**: Complete agent-corpus access logging
- **Error Responses**: Clear permission denied messages with rationale

#### Query Interface
- **Structured Queries**: Typed query objects with corpus constraints and parameters
- **Natural Language Interface**: Free-text queries with automatic corpus inference
- **Batch Queries**: Efficient multi-query processing for agent workflows
- **Streaming Results**: Incremental result delivery for interactive agents
- **Query Cancellation**: Graceful query termination and resource cleanup

### Performance & Scalability

#### Query Performance Optimization
- **Response Time Targets**: Sub-second response for typical agent queries
- **Concurrent Query Handling**: Multi-agent query processing without interference
- **Resource Utilization**: Optimal GPU/CPU usage for embedding and search operations
- **Memory Management**: Efficient memory usage for large corpus processing
- **Caching Strategy**: Multi-level caching for embeddings, queries, and results

#### Scaling Strategy
- **Horizontal Scaling**: Multiple retrieval worker processes for high load
- **Index Partitioning**: Large corpus partitioning strategies for performance
- **Load Balancing**: Query distribution across available resources
- **Resource Monitoring**: Real-time performance metrics and bottleneck detection
- **Capacity Planning**: Predictive scaling based on corpus growth and query patterns

## Design Decisions (APPROVED)

### Local-First Architecture
- [x] **PyTorch + Transformers**: Direct integration without external services
- [x] **PostgreSQL + pgvector**: Single database for all vector operations
- [x] **GPU-Optimized**: RTX-5090 optimization for embedding generation
- [x] **No External APIs**: No OpenAI, Pinecone, or other external vector services

### Corpus Isolation Architecture
- [x] **Database-Level Isolation**: Vector search respects corpus table constraints
- [x] **Agent Permission Matrix**: Runtime access control for agent-corpus combinations
- [x] **Audit Completeness**: All retrieval operations logged with corpus context
- [x] **Strict Enforcement**: Hard failures for unauthorized cross-corpus access

## Implementation Guidance

### Sentence-BERT Integration
- Sentence-transformers library installation and model management
- GPU acceleration with PyTorch CUDA support
- Model selection and configuration for patent domain optimization
- Batch processing optimization for RTX-5090 hardware capabilities

### Configuration Architecture
- **All tunable values** (similarity thresholds, model selection, batch sizes) sourced from .env files
- **Loaded via Pydantic BaseSettings** with type validation and sensible defaults
- **Configuration changes allowed by the single reviewer** through system configuration interface
- **Configuration changes must be logged, timestamped, and attributed** with complete audit trail
- **No runtime hardcoding of tunable values** - all embedding and retrieval parameters configurable

### pgvector Setup
- PostgreSQL pgvector extension installation and configuration
- HNSW index creation and optimization for patent corpus sizes
- Vector dimension management and storage efficiency optimization
- Query performance tuning for large-scale similarity search

### FastAPI Integration
- RESTful API endpoints for agent retrieval requests
- Request validation and corpus permission enforcement
- Response streaming for large result sets
- Error handling and logging for retrieval failures

## Acceptance Criteria

- [ ] Sentence-BERT embeddings generated locally without external API calls
- [ ] pgvector integration provides fast similarity search with configurable indices
- [ ] Corpus isolation strictly enforced at vector search query level
- [ ] Agent permissions validated for every retrieval operation
- [ ] Sub-second response times for typical patent queries on RTX-5090 hardware
- [ ] Embedding generation handles patent technical terminology accurately
- [ ] Vector storage optimized for PostgreSQL single-database architecture
- [ ] Hybrid search combines semantic similarity with keyword matching
- [ ] Result ranking incorporates patent metadata and cross-reference networks
- [ ] All retrieval operations logged with complete provenance and corpus context
- [ ] Memory management supports large patent corpus processing
- [ ] Concurrent agent queries processed without interference or contamination

---

**Status**: SPECIFICATION COMPLETE - Ready for P3.6 Implementation  
**Approved**: PyTorch + Transformers + pgvector Local Architecture (Dec 30, 2025)