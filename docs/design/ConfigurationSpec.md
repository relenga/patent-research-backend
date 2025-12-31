# Phase 3 Configuration Variables Reference

## Local LLM Configuration
- `LLM_MODEL_NAME`: HuggingFace model identifier for patent intelligence
- `LLM_MODEL_CACHE_DIR`: Local directory for model storage
- `LLM_DEVICE`: Computation device (cuda/cpu)
- `LLM_QUANTIZATION`: Model quantization level (none/4bit/8bit)
- `LLM_MAX_NEW_TOKENS`: Maximum tokens for LLM responses
- `LLM_TEMPERATURE`: Sampling temperature for response generation
- `LLM_BATCH_SIZE`: Batch size for concurrent requests
- `LLM_MAX_MEMORY_GB`: Maximum GPU memory allocation

## RAG Infrastructure
- `EMBEDDING_MODEL_NAME`: Sentence transformer model for embeddings
- `EMBEDDING_DIMENSION`: Vector dimension for similarity search
- `VECTOR_INDEX_TYPE`: Index algorithm (hnsw/ivf/flat)
- `SIMILARITY_THRESHOLD`: Minimum similarity for retrieval
- `MAX_RETRIEVAL_RESULTS`: Maximum documents returned per query
- `EMBEDDING_BATCH_SIZE`: Batch size for embedding generation

## OCR Processing
- `TESSERACT_PATH`: Path to Tesseract OCR executable
- `OCR_LANGUAGE`: OCR language configuration
- `OCR_CONFIDENCE_THRESHOLD`: Minimum confidence for text extraction
- `OCR_MAX_IMAGE_SIZE_MB`: Maximum image size for processing
- `DIAGRAM_HASH_THRESHOLD`: Threshold for identical diagram detection
- `DIAGRAM_SIMILARITY_THRESHOLD`: Threshold for similar diagram detection

## HITL Task Management
- `HITL_TASK_TIMEOUT_HOURS`: Task completion deadline
- `HITL_ESCALATION_THRESHOLD_HOURS`: Escalation trigger time
- `HITL_MAX_RETRY_ATTEMPTS`: Maximum retry attempts for failed tasks
- `HITL_BATCH_SIZE`: Tasks assigned per batch
- `HITL_AUTO_ASSIGN`: Automatic task assignment enabled

## Corpus Management
- `CORPUS_ISOLATION_STRICT`: Strict corpus boundary enforcement
- `CORPUS_MAX_DOCUMENTS`: Maximum documents per corpus
- `CORPUS_ACCESS_LOG_RETENTION_DAYS`: Audit log retention period
- `CORPUS_VIOLATION_ALERT`: Alert on corpus boundary violations

## Logging & Audit
- `LOG_LEVEL`: Application log level (DEBUG/INFO/WARNING/ERROR)
- `LOG_TO_DATABASE`: Store critical logs in database
- `LOG_RETENTION_DAYS`: Application log retention period
- `AUDIT_LOG_RETENTION_DAYS`: Compliance audit log retention
- `PERFORMANCE_LOG_ENABLED`: Performance metrics logging
- `SENSITIVE_DATA_REDACTION`: Automatic PII redaction

## Performance & Resources
- `API_RESPONSE_TIMEOUT_SECONDS`: API request timeout
- `DOCUMENT_PROCESSING_WORKERS`: Concurrent document processing threads
- `CONCURRENT_AGENT_REQUESTS`: Maximum concurrent agent operations
- `MEMORY_MONITOR_THRESHOLD_PERCENT`: Memory usage alert threshold