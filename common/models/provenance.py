"""
Provenance Data Models

Defines provenance tracking models following PROV-O ontology concepts
for tracking the origin, processing, and derivation of data entities.

Phase 2: Pure data structures ONLY - no provenance collection or storage logic.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Union


class ProvenanceEntityType(Enum):
    """
    Types of provenance entities.
    
    Phase 2: Enumeration only - no entity processing logic.
    """
    DOCUMENT = "document"
    DATASET = "dataset"
    CONFIGURATION = "configuration"
    MODEL = "model"
    REPORT = "report"
    ARTIFACT = "artifact"
    INTERMEDIATE_RESULT = "intermediate_result"
    FINAL_OUTPUT = "final_output"


class ProvenanceActivityType(Enum):
    """
    Types of provenance activities.
    
    Phase 2: Enumeration only - no activity tracking logic.
    """
    CREATION = "creation"
    TRANSFORMATION = "transformation"
    VALIDATION = "validation"
    ENRICHMENT = "enrichment"
    ANALYSIS = "analysis"
    AGGREGATION = "aggregation"
    FILTERING = "filtering"
    MERGING = "merging"
    SPLITTING = "splitting"
    STORAGE = "storage"
    RETRIEVAL = "retrieval"
    DELETION = "deletion"


class ProvenanceAgentType(Enum):
    """
    Types of provenance agents.
    
    Phase 2: Enumeration only - no agent tracking logic.
    """
    HUMAN_USER = "human_user"
    SYSTEM_PROCESS = "system_process"
    AUTOMATED_SERVICE = "automated_service"
    EXTERNAL_SYSTEM = "external_system"
    API_CLIENT = "api_client"
    PIPELINE_STEP = "pipeline_step"
    VALIDATION_RULE = "validation_rule"
    TRANSFORMATION_RULE = "transformation_rule"


@dataclass(frozen=True)
class ProvenanceEntity:
    """
    Entity in provenance model representing data, documents, or artifacts.
    
    Phase 2: Pure data structure - no entity behavior logic.
    Based on PROV-O Entity concept.
    """
    entity_id: str
    entity_type: ProvenanceEntityType
    name: str
    description: str
    created_at: datetime
    attributes: Dict[str, Any]
    location: Optional[str] = None
    format: Optional[str] = None
    size: Optional[int] = None
    checksum: Optional[str] = None
    version: Optional[str] = None
    parent_entity_id: Optional[str] = None
    tags: Set[str] = field(default_factory=set)


@dataclass(frozen=True)
class ProvenanceActivity:
    """
    Activity in provenance model representing operations on entities.
    
    Phase 2: Pure data structure - no activity execution logic.
    Based on PROV-O Activity concept.
    """
    activity_id: str
    activity_type: ProvenanceActivityType
    name: str
    description: str
    started_at: datetime
    ended_at: Optional[datetime]
    parameters: Dict[str, Any]
    configuration: Dict[str, Any]
    status: str
    error_info: Optional[Dict[str, Any]] = None
    performance_metrics: Optional[Dict[str, Any]] = None
    tags: Set[str] = field(default_factory=set)


@dataclass(frozen=True)
class ProvenanceAgent:
    """
    Agent in provenance model representing who/what performed activities.
    
    Phase 2: Pure data structure - no agent behavior logic.
    Based on PROV-O Agent concept.
    """
    agent_id: str
    agent_type: ProvenanceAgentType
    name: str
    description: str
    created_at: datetime
    attributes: Dict[str, Any]
    version: Optional[str] = None
    contact_info: Optional[Dict[str, Any]] = None
    capabilities: Set[str] = field(default_factory=set)
    tags: Set[str] = field(default_factory=set)


@dataclass(frozen=True)
class ProvenanceAssociation:
    """
    Association between activity and agent (who performed the activity).
    
    Phase 2: Pure data structure - no association logic.
    Based on PROV-O Association concept.
    """
    association_id: str
    activity_id: str
    agent_id: str
    role: str
    started_at: datetime
    plan_id: Optional[str] = None
    ended_at: Optional[datetime] = None
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ProvenanceAttribution:
    """
    Attribution between entity and agent (who was responsible for entity).
    
    Phase 2: Pure data structure - no attribution logic.
    Based on PROV-O Attribution concept.
    """
    attribution_id: str
    entity_id: str
    agent_id: str
    role: str
    attributed_at: datetime
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ProvenanceDerivation:
    """
    Derivation between entities (how one entity was derived from another).
    
    Phase 2: Pure data structure - no derivation logic.
    Based on PROV-O Derivation concept.
    """
    derivation_id: str
    derived_entity_id: str
    source_entity_id: str
    activity_id: Optional[str]
    derivation_type: str
    derived_at: datetime
    transformation_rules: Optional[Dict[str, Any]] = None
    quality_impact: Optional[Dict[str, Any]] = None
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ProvenanceUsage:
    """
    Usage of entity by activity (what data was used in the activity).
    
    Phase 2: Pure data structure - no usage tracking logic.
    Based on PROV-O Usage concept.
    """
    usage_id: str
    activity_id: str
    entity_id: str
    used_at: datetime
    role: str
    usage_type: str
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ProvenanceGeneration:
    """
    Generation of entity by activity (what data was produced by the activity).
    
    Phase 2: Pure data structure - no generation tracking logic.
    Based on PROV-O Generation concept.
    """
    generation_id: str
    activity_id: str
    entity_id: str
    generated_at: datetime
    role: str
    generation_type: str
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProvenanceRecord:
    """
    Complete provenance record containing all provenance information.
    
    Phase 2: Pure data container - no provenance processing logic.
    """
    record_id: str
    created_at: datetime
    created_by: str
    entities: Dict[str, ProvenanceEntity] = field(default_factory=dict)
    activities: Dict[str, ProvenanceActivity] = field(default_factory=dict)
    agents: Dict[str, ProvenanceAgent] = field(default_factory=dict)
    associations: Dict[str, ProvenanceAssociation] = field(default_factory=dict)
    attributions: Dict[str, ProvenanceAttribution] = field(default_factory=dict)
    derivations: Dict[str, ProvenanceDerivation] = field(default_factory=dict)
    usages: Dict[str, ProvenanceUsage] = field(default_factory=dict)
    generations: Dict[str, ProvenanceGeneration] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_entity(self, entity: ProvenanceEntity) -> None:
        """Add entity to record. Phase 2: Simple data operation."""
        self.entities[entity.entity_id] = entity
    
    def add_activity(self, activity: ProvenanceActivity) -> None:
        """Add activity to record. Phase 2: Simple data operation."""
        self.activities[activity.activity_id] = activity
    
    def add_agent(self, agent: ProvenanceAgent) -> None:
        """Add agent to record. Phase 2: Simple data operation."""
        self.agents[agent.agent_id] = agent
    
    def add_association(self, association: ProvenanceAssociation) -> None:
        """Add association to record. Phase 2: Simple data operation."""
        self.associations[association.association_id] = association
    
    def add_attribution(self, attribution: ProvenanceAttribution) -> None:
        """Add attribution to record. Phase 2: Simple data operation."""
        self.attributions[attribution.attribution_id] = attribution
    
    def add_derivation(self, derivation: ProvenanceDerivation) -> None:
        """Add derivation to record. Phase 2: Simple data operation."""
        self.derivations[derivation.derivation_id] = derivation
    
    def add_usage(self, usage: ProvenanceUsage) -> None:
        """Add usage to record. Phase 2: Simple data operation."""
        self.usages[usage.usage_id] = usage
    
    def add_generation(self, generation: ProvenanceGeneration) -> None:
        """Add generation to record. Phase 2: Simple data operation."""
        self.generations[generation.generation_id] = generation


# Provenance Tracking Interface Contracts
# Phase 2: Interface definitions ONLY - no tracking implementations

class ProvenanceTracker(ABC):
    """
    Abstract interface for provenance tracking operations.
    
    Phase 2: Interface contract only - no tracking implementation.
    Defines how provenance information is captured and managed.
    """
    
    @abstractmethod
    def create_provenance_record(self, record_id: str, created_by: str) -> ProvenanceRecord:
        """
        Create new provenance record.
        
        Phase 2: Interface only - no record creation logic.
        
        Args:
            record_id: Unique record identifier
            created_by: Creator identifier
            
        Returns:
            New provenance record instance
        """
        pass
    
    @abstractmethod
    def track_entity_creation(
        self,
        record: ProvenanceRecord,
        entity_id: str,
        entity_type: ProvenanceEntityType,
        attributes: Dict[str, Any],
        created_by_agent_id: str
    ) -> ProvenanceEntity:
        """
        Track creation of a provenance entity.
        
        Phase 2: Interface only - no tracking logic.
        
        Args:
            record: Target provenance record
            entity_id: Unique entity identifier
            entity_type: Type of entity
            attributes: Entity attributes
            created_by_agent_id: Creating agent identifier
            
        Returns:
            Created provenance entity
        """
        pass
    
    @abstractmethod
    def track_activity_execution(
        self,
        record: ProvenanceRecord,
        activity_id: str,
        activity_type: ProvenanceActivityType,
        performed_by_agent_id: str,
        parameters: Dict[str, Any]
    ) -> ProvenanceActivity:
        """
        Track execution of a provenance activity.
        
        Phase 2: Interface only - no tracking logic.
        
        Args:
            record: Target provenance record
            activity_id: Unique activity identifier
            activity_type: Type of activity
            performed_by_agent_id: Performing agent identifier
            parameters: Activity parameters
            
        Returns:
            Created provenance activity
        """
        pass
    
    @abstractmethod
    def track_entity_usage(
        self,
        record: ProvenanceRecord,
        activity_id: str,
        entity_id: str,
        role: str,
        usage_type: str
    ) -> ProvenanceUsage:
        """
        Track usage of entity by activity.
        
        Phase 2: Interface only - no tracking logic.
        
        Args:
            record: Target provenance record
            activity_id: Activity identifier
            entity_id: Used entity identifier
            role: Role of entity in activity
            usage_type: Type of usage
            
        Returns:
            Created provenance usage
        """
        pass
    
    @abstractmethod
    def track_entity_generation(
        self,
        record: ProvenanceRecord,
        activity_id: str,
        entity_id: str,
        role: str,
        generation_type: str
    ) -> ProvenanceGeneration:
        """
        Track generation of entity by activity.
        
        Phase 2: Interface only - no tracking logic.
        
        Args:
            record: Target provenance record
            activity_id: Activity identifier
            entity_id: Generated entity identifier
            role: Role of entity in activity
            generation_type: Type of generation
            
        Returns:
            Created provenance generation
        """
        pass
    
    @abstractmethod
    def track_entity_derivation(
        self,
        record: ProvenanceRecord,
        derived_entity_id: str,
        source_entity_id: str,
        derivation_type: str,
        activity_id: Optional[str] = None
    ) -> ProvenanceDerivation:
        """
        Track derivation between entities.
        
        Phase 2: Interface only - no tracking logic.
        
        Args:
            record: Target provenance record
            derived_entity_id: Derived entity identifier
            source_entity_id: Source entity identifier
            derivation_type: Type of derivation
            activity_id: Optional activity that performed derivation
            
        Returns:
            Created provenance derivation
        """
        pass
    
    @abstractmethod
    def get_entity_provenance(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """
        Get complete provenance information for entity.
        
        Phase 2: Interface only - no provenance retrieval logic.
        
        Args:
            entity_id: Entity identifier
            
        Returns:
            Entity provenance information or None if not found
        """
        pass
    
    @abstractmethod
    def get_activity_provenance(self, activity_id: str) -> Optional[Dict[str, Any]]:
        """
        Get complete provenance information for activity.
        
        Phase 2: Interface only - no provenance retrieval logic.
        
        Args:
            activity_id: Activity identifier
            
        Returns:
            Activity provenance information or None if not found
        """
        pass