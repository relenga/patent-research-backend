import os
from enum import Enum

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvironmentOption(str, Enum):
    LOCAL = "local"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings(BaseSettings):
    # App metadata
    APP_NAME: str = "Patent Intelligence System"
    APP_DESCRIPTION: str = "AI-Powered Patent Intelligence Backend"
    APP_VERSION: str = "3.0.0"
    LICENSE_NAME: str = "MIT"
    CONTACT_NAME: str | None = None
    CONTACT_EMAIL: str | None = None

    # Environment
    ENVIRONMENT: EnvironmentOption = EnvironmentOption.LOCAL

    # Database (PostgreSQL only)
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "postgres"
    POSTGRES_SYNC_PREFIX: str = "postgresql://"
    POSTGRES_ASYNC_PREFIX: str = "postgresql+asyncpg://"
    POSTGRES_URL: str | None = None

    # Phase 3: Local LLM Configuration
    LLM_MODEL_NAME: str = "microsoft/DialoGPT-large"
    LLM_MODEL_CACHE_DIR: str = "./models"
    LLM_DEVICE: str = "cuda"
    LLM_QUANTIZATION: str = "4bit"  # none, 4bit, 8bit
    LLM_MAX_NEW_TOKENS: int = 512
    LLM_TEMPERATURE: float = 0.7
    LLM_BATCH_SIZE: int = 4
    LLM_MAX_MEMORY_GB: int = 40

    # Phase 3: RAG Infrastructure
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384
    VECTOR_INDEX_TYPE: str = "hnsw"  # hnsw, ivf, flat
    SIMILARITY_THRESHOLD: float = 0.7
    MAX_RETRIEVAL_RESULTS: int = 10
    EMBEDDING_BATCH_SIZE: int = 32

    # Phase 3: OCR Processing
    TESSERACT_PATH: str = "tesseract"
    OCR_LANGUAGE: str = "eng"
    OCR_CONFIDENCE_THRESHOLD: float = 0.6
    OCR_MAX_IMAGE_SIZE_MB: int = 50
    DIAGRAM_HASH_THRESHOLD: float = 0.9
    DIAGRAM_SIMILARITY_THRESHOLD: float = 0.85

    # Phase 3: HITL Task Configuration
    HITL_TASK_TIMEOUT_HOURS: int = 24
    HITL_ESCALATION_THRESHOLD_HOURS: int = 48
    HITL_MAX_RETRY_ATTEMPTS: int = 3
    HITL_BATCH_SIZE: int = 10
    HITL_AUTO_ASSIGN: bool = True

    # Phase 3: Corpus Management
    CORPUS_ISOLATION_STRICT: bool = True
    CORPUS_MAX_DOCUMENTS: int = 10000
    CORPUS_ACCESS_LOG_RETENTION_DAYS: int = 365
    CORPUS_VIOLATION_ALERT: bool = True

    # Phase 3: Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_TO_DATABASE: bool = True
    LOG_RETENTION_DAYS: int = 90
    AUDIT_LOG_RETENTION_DAYS: int = 2555  # 7 years
    PERFORMANCE_LOG_ENABLED: bool = True
    SENSITIVE_DATA_REDACTION: bool = True

    # Phase 3: Performance Settings
    API_RESPONSE_TIMEOUT_SECONDS: int = 30
    DOCUMENT_PROCESSING_WORKERS: int = 4
    CONCURRENT_AGENT_REQUESTS: int = 8
    MEMORY_MONITOR_THRESHOLD_PERCENT: int = 85

    @computed_field  # type: ignore[prop-decorator]
    @property
    def POSTGRES_URI(self) -> str:
        credentials = f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
        location = f"{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        return f"{credentials}@{location}"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def DATABASE_URL(self) -> str:
        """Complete async database URL for SQLAlchemy"""
        return f"{self.POSTGRES_ASYNC_PREFIX}{self.POSTGRES_URI}"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def LLM_DEVICE_MAP(self) -> str:
        """Device mapping for model loading"""
        if self.LLM_DEVICE == "cuda":
            return "auto"
        return self.LLM_DEVICE

    @computed_field  # type: ignore[prop-decorator]
    @property
    def IS_QUANTIZED(self) -> bool:
        """Whether model quantization is enabled"""
        return self.LLM_QUANTIZATION in ["4bit", "8bit"]

    @computed_field  # type: ignore[prop-decorator]
    @property
    def VECTOR_STORE_CONFIG(self) -> dict:
        """Vector store configuration dictionary"""
        return {
            "index_type": self.VECTOR_INDEX_TYPE,
            "dimension": self.EMBEDDING_DIMENSION,
            "similarity_threshold": self.SIMILARITY_THRESHOLD
        }

    # CORS
    CORS_ORIGINS: list[str] = ["*"]
    CORS_METHODS: list[str] = ["*"]
    CORS_HEADERS: list[str] = ["*"]

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()