"""
Deterministic Pipeline Step Contracts

This module defines pipeline step interfaces and contracts for deterministic
document processing pipelines. All definitions are pure interfaces without
execution logic.

Phase 2: Interface contracts ONLY - no implementations or orchestration.

Pipeline Philosophy:
- Each step is a pure transformation with explicit inputs/outputs
- Steps are composable through well-defined contracts
- Validation occurs at contract boundaries
- No implicit ordering or control flow assumptions
- Deterministic behavior through explicit state management
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Set, TypeVar, Generic, Protocol, TypedDict, Union
from enum import Enum
from dataclasses import dataclass


# Type variables for generic pipeline contracts
InputType = TypeVar('InputType')
OutputType = TypeVar('OutputType')
ConfigType = TypeVar('ConfigType')


class StepStatus(Enum):
    """
    Pipeline step execution status.
    
    Phase 2: Data structure only - no status management logic.
    """
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"


class ValidationSeverity(Enum):
    """
    Validation result severity levels.
    """
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass(frozen=True)
class StepMetadata:
    """
    Pipeline step metadata container.
    
    Pure data structure for step identification and categorization.
    Phase 2: No behavior, just data.
    """
    step_id: str
    step_name: str
    step_version: str
    description: str
    category: str
    tags: Set[str]
    dependencies: Set[str]  # Step IDs this step depends on
    produces: Set[str]      # Data products this step produces
    consumes: Set[str]      # Data products this step consumes


class StepInputContract(TypedDict, total=False):
    """
    Standard input contract for pipeline steps.
    
    Phase 2: Type definition only - no validation logic.
    """
    data: Any                    # Primary input data
    config: Dict[str, Any]       # Step configuration
    context: Dict[str, Any]      # Execution context
    metadata: Dict[str, Any]     # Input metadata
    previous_outputs: Dict[str, Any]  # Outputs from previous steps


class StepOutputContract(TypedDict, total=False):
    """
    Standard output contract for pipeline steps.
    
    Phase 2: Type definition only - no validation logic.
    """
    data: Any                    # Primary output data
    metadata: Dict[str, Any]     # Output metadata
    artifacts: Dict[str, Any]    # Generated artifacts
    metrics: Dict[str, Any]      # Step execution metrics
    validation_results: List['ValidationResult']
    next_step_inputs: Dict[str, Any]  # Prepared inputs for next steps


@dataclass(frozen=True)
class ValidationResult:
    """
    Validation result data structure.
    
    Phase 2: Pure data container - no validation logic.
    """
    validator_id: str
    severity: ValidationSeverity
    message: str
    details: Dict[str, Any]
    field_path: Optional[str] = None
    error_code: Optional[str] = None


class PipelineStepProtocol(Protocol[InputType, OutputType, ConfigType]):
    """
    Protocol defining the contract for pipeline steps.
    
    Phase 2: Protocol definition only - no implementations.
    Defines the interface that all pipeline steps must satisfy.
    """
    
    metadata: StepMetadata
    
    def validate_input(self, input_data: InputType) -> List[ValidationResult]:
        """
        Validate step input data.
        
        Phase 2: Interface only - no validation logic.
        
        Args:
            input_data: Data to validate
            
        Returns:
            List of validation results
        """
        ...
    
    def validate_config(self, config: ConfigType) -> List[ValidationResult]:
        """
        Validate step configuration.
        
        Phase 2: Interface only - no validation logic.
        
        Args:
            config: Configuration to validate
            
        Returns:
            List of validation results
        """
        ...
    
    def get_input_schema(self) -> Dict[str, Any]:
        """
        Get JSON schema for input validation.
        
        Phase 2: Interface only - no schema generation.
        
        Returns:
            JSON schema for input data
        """
        ...
    
    def get_output_schema(self) -> Dict[str, Any]:
        """
        Get JSON schema for output validation.
        
        Phase 2: Interface only - no schema generation.
        
        Returns:
            JSON schema for output data
        """
        ...
    
    def get_config_schema(self) -> Dict[str, Any]:
        """
        Get JSON schema for configuration validation.
        
        Phase 2: Interface only - no schema generation.
        
        Returns:
            JSON schema for configuration
        """
        ...


class AbstractPipelineStep(ABC, Generic[InputType, OutputType, ConfigType]):
    """
    Abstract base class for pipeline steps.
    
    Phase 2: Abstract interface only - no implementations.
    Provides structure for concrete step implementations in Phase 3.
    """
    
    def __init__(self, metadata: StepMetadata):
        """
        Initialize step with metadata.
        
        Phase 2: Constructor interface only.
        
        Args:
            metadata: Step metadata
        """
        self.metadata = metadata
    
    @abstractmethod
    def validate_input(self, input_data: InputType) -> List[ValidationResult]:
        """
        Validate step input data.
        
        Phase 2: Abstract method - no implementation.
        """
        pass
    
    @abstractmethod
    def validate_config(self, config: ConfigType) -> List[ValidationResult]:
        """
        Validate step configuration.
        
        Phase 2: Abstract method - no implementation.
        """
        pass
    
    @abstractmethod
    def get_input_schema(self) -> Dict[str, Any]:
        """
        Get input validation schema.
        
        Phase 2: Abstract method - no implementation.
        """
        pass
    
    @abstractmethod
    def get_output_schema(self) -> Dict[str, Any]:
        """
        Get output validation schema.
        
        Phase 2: Abstract method - no implementation.
        """
        pass
    
    @abstractmethod
    def get_config_schema(self) -> Dict[str, Any]:
        """
        Get configuration validation schema.
        
        Phase 2: Abstract method - no implementation.
        """
        pass


# Document Processing Pipeline Step Categories
# Phase 2: Data structure only - no execution logic

class DocumentValidationStep(AbstractPipelineStep[Dict[str, Any], Dict[str, Any], Dict[str, Any]]):
    """
    Abstract interface for document validation steps.
    
    Validates document structure, content, and metadata.
    Phase 2: Interface only - no validation implementations.
    """
    pass


class DocumentTransformationStep(AbstractPipelineStep[Dict[str, Any], Dict[str, Any], Dict[str, Any]]):
    """
    Abstract interface for document transformation steps.
    
    Transforms document content, format, or structure.
    Phase 2: Interface only - no transformation implementations.
    """
    pass


class DocumentEnrichmentStep(AbstractPipelineStep[Dict[str, Any], Dict[str, Any], Dict[str, Any]]):
    """
    Abstract interface for document enrichment steps.
    
    Adds metadata, tags, classifications, or derived data to documents.
    Phase 2: Interface only - no enrichment implementations.
    """
    pass


class DocumentStorageStep(AbstractPipelineStep[Dict[str, Any], Dict[str, Any], Dict[str, Any]]):
    """
    Abstract interface for document storage steps.
    
    Handles document persistence, indexing, and retrieval preparation.
    Phase 2: Interface only - no storage implementations.
    """
    pass


# Pipeline Composition Contracts
# Phase 2: Structure only - no control flow or orchestration

@dataclass(frozen=True)
class PipelineDefinition:
    """
    Pipeline structure definition.
    
    Phase 2: Pure data structure - no execution logic.
    Defines the structural composition of pipeline steps.
    """
    pipeline_id: str
    pipeline_name: str
    pipeline_version: str
    description: str
    steps: List[StepMetadata]
    step_dependencies: Dict[str, Set[str]]  # step_id -> dependency_step_ids
    data_flow: Dict[str, Dict[str, str]]    # step_id -> {output_name: target_input}
    configuration: Dict[str, Any]
    tags: Set[str]


@dataclass(frozen=True) 
class StepConnection:
    """
    Connection between pipeline steps.
    
    Phase 2: Pure data structure - no connection logic.
    Defines how data flows between steps.
    """
    source_step_id: str
    source_output: str
    target_step_id: str
    target_input: str
    transformation_rules: Optional[Dict[str, Any]] = None


class PipelineCompositionContract(ABC):
    """
    Abstract interface for pipeline composition.
    
    Phase 2: Interface only - no composition implementation.
    Defines how pipelines are structurally composed from steps.
    """
    
    @abstractmethod
    def validate_pipeline_structure(self, pipeline_def: PipelineDefinition) -> List[ValidationResult]:
        """
        Validate pipeline structural integrity.
        
        Phase 2: Interface only - no validation logic.
        
        Args:
            pipeline_def: Pipeline definition to validate
            
        Returns:
            List of validation results
        """
        pass
    
    @abstractmethod
    def validate_data_flow(self, pipeline_def: PipelineDefinition) -> List[ValidationResult]:
        """
        Validate data flow between steps.
        
        Phase 2: Interface only - no validation logic.
        
        Args:
            pipeline_def: Pipeline definition to validate
            
        Returns:
            List of validation results
        """
        pass
    
    @abstractmethod
    def get_execution_order(self, pipeline_def: PipelineDefinition) -> List[List[str]]:
        """
        Get step execution order based on dependencies.
        
        Phase 2: Interface only - no ordering logic.
        Returns steps grouped by execution level (parallel steps in same level).
        
        Args:
            pipeline_def: Pipeline definition
            
        Returns:
            List of step groups ordered by execution level
        """
        pass
    
    @abstractmethod
    def validate_step_compatibility(self, source_step: StepMetadata, target_step: StepMetadata) -> List[ValidationResult]:
        """
        Validate compatibility between connected steps.
        
        Phase 2: Interface only - no compatibility logic.
        
        Args:
            source_step: Source step metadata
            target_step: Target step metadata
            
        Returns:
            List of validation results
        """
        pass


# Step Validation Interface Definitions
# Phase 2: Schema/typing only - no validation implementations

class StepValidationContract(ABC):
    """
    Abstract interface for step validation operations.
    
    Phase 2: Interface only - no validation implementations.
    Defines contracts for validating step inputs, outputs, and configurations.
    """
    
    @abstractmethod
    def validate_step_input_schema(self, step_metadata: StepMetadata, input_schema: Dict[str, Any]) -> List[ValidationResult]:
        """
        Validate step input schema definition.
        
        Phase 2: Interface only - no schema validation logic.
        
        Args:
            step_metadata: Step metadata
            input_schema: Input schema to validate
            
        Returns:
            List of validation results
        """
        pass
    
    @abstractmethod
    def validate_step_output_schema(self, step_metadata: StepMetadata, output_schema: Dict[str, Any]) -> List[ValidationResult]:
        """
        Validate step output schema definition.
        
        Phase 2: Interface only - no schema validation logic.
        
        Args:
            step_metadata: Step metadata  
            output_schema: Output schema to validate
            
        Returns:
            List of validation results
        """
        pass
    
    @abstractmethod
    def validate_step_config_schema(self, step_metadata: StepMetadata, config_schema: Dict[str, Any]) -> List[ValidationResult]:
        """
        Validate step configuration schema definition.
        
        Phase 2: Interface only - no schema validation logic.
        
        Args:
            step_metadata: Step metadata
            config_schema: Configuration schema to validate
            
        Returns:
            List of validation results
        """
        pass
    
    @abstractmethod
    def validate_schema_compatibility(self, source_schema: Dict[str, Any], target_schema: Dict[str, Any]) -> List[ValidationResult]:
        """
        Validate schema compatibility between connected steps.
        
        Phase 2: Interface only - no compatibility logic.
        
        Args:
            source_schema: Output schema from source step
            target_schema: Input schema for target step
            
        Returns:
            List of validation results
        """
        pass


# Pipeline Step Registry Interface
# Phase 2: Interface only - no registry implementation

class PipelineStepRegistry(ABC):
    """
    Abstract interface for pipeline step registration and discovery.
    
    Phase 2: Interface only - no registry implementation.
    Defines how steps are registered and discovered in the system.
    """
    
    @abstractmethod
    def register_step(self, step_class: type, metadata: StepMetadata) -> None:
        """
        Register a pipeline step.
        
        Phase 2: Interface only - no registration logic.
        
        Args:
            step_class: Step implementation class
            metadata: Step metadata
        """
        pass
    
    @abstractmethod
    def get_step_metadata(self, step_id: str) -> Optional[StepMetadata]:
        """
        Get step metadata by ID.
        
        Phase 2: Interface only - no lookup logic.
        
        Args:
            step_id: Step identifier
            
        Returns:
            Step metadata or None if not found
        """
        pass
    
    @abstractmethod
    def list_steps_by_category(self, category: str) -> List[StepMetadata]:
        """
        List steps by category.
        
        Phase 2: Interface only - no listing logic.
        
        Args:
            category: Step category
            
        Returns:
            List of step metadata in category
        """
        pass
    
    @abstractmethod
    def find_compatible_steps(self, output_schema: Dict[str, Any]) -> List[StepMetadata]:
        """
        Find steps compatible with given output schema.
        
        Phase 2: Interface only - no compatibility logic.
        
        Args:
            output_schema: Output schema to match against
            
        Returns:
            List of compatible step metadata
        """
        pass