"""
Lineage Data Models

Defines data lineage tracking models for understanding data flow and
transformation history through the system.

Phase 2: Pure data structures ONLY - no lineage collection or storage logic.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Union, TypeVar, Generic


class LineageNodeType(Enum):
    """
    Types of nodes in lineage graph.
    
    Phase 2: Enumeration only - no node processing logic.
    """
    DATA_SOURCE = "data_source"        # External data input
    DATA_SINK = "data_sink"            # External data output
    TRANSFORMATION = "transformation"   # Data transformation process
    VALIDATION = "validation"          # Data validation process
    ENRICHMENT = "enrichment"          # Data enrichment process
    AGGREGATION = "aggregation"        # Data aggregation process
    FILTER = "filter"                  # Data filtering process
    MERGE = "merge"                    # Data merging process
    SPLIT = "split"                    # Data splitting process
    STORAGE = "storage"                # Data storage operation


class LineageRelationshipType(Enum):
    """
    Types of relationships between lineage nodes.
    
    Phase 2: Enumeration only - no relationship processing logic.
    """
    DERIVED_FROM = "derived_from"      # Output derived from input
    TRANSFORMED_BY = "transformed_by"  # Data transformed by process
    VALIDATED_BY = "validated_by"      # Data validated by process
    ENRICHED_BY = "enriched_by"        # Data enriched by process
    FILTERED_BY = "filtered_by"        # Data filtered by process
    AGGREGATED_BY = "aggregated_by"    # Data aggregated by process
    MERGED_WITH = "merged_with"        # Data merged with other data
    SPLIT_INTO = "split_into"          # Data split into multiple outputs
    STORED_IN = "stored_in"           # Data stored in location
    CONSUMED_BY = "consumed_by"        # Data consumed by process


@dataclass(frozen=True)
class LineageMetadata:
    """
    Metadata associated with lineage tracking.
    
    Phase 2: Pure data structure - no metadata processing logic.
    """
    created_at: datetime
    created_by: str
    version: str
    tags: Set[str]
    properties: Dict[str, Any]
    source_system: Optional[str] = None
    source_version: Optional[str] = None
    confidence_score: Optional[float] = None
    quality_score: Optional[float] = None


@dataclass(frozen=True)
class LineageNode:
    """
    Node in lineage graph representing data or process.
    
    Phase 2: Pure data structure - no node behavior logic.
    """
    node_id: str
    node_type: LineageNodeType
    name: str
    description: str
    metadata: LineageMetadata
    schema_info: Optional[Dict[str, Any]] = None
    location: Optional[str] = None
    format: Optional[str] = None
    size_bytes: Optional[int] = None
    record_count: Optional[int] = None
    checksum: Optional[str] = None


@dataclass(frozen=True)
class LineageEdge:
    """
    Edge in lineage graph representing relationship between nodes.
    
    Phase 2: Pure data structure - no relationship logic.
    """
    edge_id: str
    source_node_id: str
    target_node_id: str
    relationship_type: LineageRelationshipType
    metadata: LineageMetadata
    transformation_rules: Optional[Dict[str, Any]] = None
    data_flow_info: Optional[Dict[str, Any]] = None
    quality_impact: Optional[Dict[str, Any]] = None


@dataclass
class LineageGraph:
    """
    Complete lineage graph with nodes and edges.
    
    Phase 2: Pure data container - no graph processing logic.
    """
    graph_id: str
    nodes: Dict[str, LineageNode] = field(default_factory=dict)
    edges: Dict[str, LineageEdge] = field(default_factory=dict)
    metadata: Optional[LineageMetadata] = None
    
    def add_node(self, node: LineageNode) -> None:
        """Add node to graph. Phase 2: Simple data operation."""
        self.nodes[node.node_id] = node
    
    def add_edge(self, edge: LineageEdge) -> None:
        """Add edge to graph. Phase 2: Simple data operation."""
        self.edges[edge.edge_id] = edge
    
    def get_node_ids(self) -> Set[str]:
        """Get all node IDs. Phase 2: Simple data access."""
        return set(self.nodes.keys())
    
    def get_edge_ids(self) -> Set[str]:
        """Get all edge IDs. Phase 2: Simple data access."""
        return set(self.edges.keys())


@dataclass(frozen=True)
class DataLineage:
    """
    Data-focused lineage information.
    
    Phase 2: Pure data structure - no lineage computation logic.
    """
    data_id: str
    data_name: str
    data_type: str
    upstream_dependencies: Set[str]
    downstream_dependents: Set[str]
    transformations: List[str]
    quality_metrics: Dict[str, Any]
    lineage_graph: LineageGraph
    metadata: LineageMetadata


@dataclass(frozen=True)
class ProcessLineage:
    """
    Process-focused lineage information.
    
    Phase 2: Pure data structure - no process tracking logic.
    """
    process_id: str
    process_name: str
    process_type: str
    input_data: Set[str]
    output_data: Set[str]
    configuration: Dict[str, Any]
    execution_info: Dict[str, Any]
    lineage_graph: LineageGraph
    metadata: LineageMetadata


class LineageRelationship:
    """
    Relationship descriptor for lineage connections.
    
    Phase 2: Pure data structure - no relationship processing.
    """
    
    def __init__(
        self,
        source_id: str,
        target_id: str,
        relationship_type: LineageRelationshipType,
        properties: Optional[Dict[str, Any]] = None,
        metadata: Optional[LineageMetadata] = None
    ):
        """
        Initialize lineage relationship.
        
        Phase 2: Data initialization only - no relationship logic.
        
        Args:
            source_id: Source entity ID
            target_id: Target entity ID
            relationship_type: Type of relationship
            properties: Optional relationship properties
            metadata: Optional relationship metadata
        """
        self.source_id = source_id
        self.target_id = target_id
        self.relationship_type = relationship_type
        self.properties = properties or {}
        self.metadata = metadata


# Lineage Tracking Interface Contracts
# Phase 2: Interface definitions ONLY - no tracking implementations

class LineageTracker(ABC):
    """
    Abstract interface for lineage tracking operations.
    
    Phase 2: Interface contract only - no tracking implementation.
    Defines how lineage information is captured and managed.
    """
    
    @abstractmethod
    def create_lineage_graph(self, graph_id: str, metadata: Optional[LineageMetadata] = None) -> LineageGraph:
        """
        Create new lineage graph.
        
        Phase 2: Interface only - no graph creation logic.
        
        Args:
            graph_id: Unique graph identifier
            metadata: Optional graph metadata
            
        Returns:
            New lineage graph instance
        """
        pass
    
    @abstractmethod
    def add_data_node(
        self,
        graph: LineageGraph,
        node_id: str,
        name: str,
        data_info: Dict[str, Any],
        metadata: LineageMetadata
    ) -> LineageNode:
        """
        Add data node to lineage graph.
        
        Phase 2: Interface only - no node addition logic.
        
        Args:
            graph: Target lineage graph
            node_id: Unique node identifier
            name: Node display name
            data_info: Data-specific information
            metadata: Node metadata
            
        Returns:
            Created lineage node
        """
        pass
    
    @abstractmethod
    def add_process_node(
        self,
        graph: LineageGraph,
        node_id: str,
        name: str,
        process_info: Dict[str, Any],
        metadata: LineageMetadata
    ) -> LineageNode:
        """
        Add process node to lineage graph.
        
        Phase 2: Interface only - no node addition logic.
        
        Args:
            graph: Target lineage graph
            node_id: Unique node identifier
            name: Node display name
            process_info: Process-specific information
            metadata: Node metadata
            
        Returns:
            Created lineage node
        """
        pass
    
    @abstractmethod
    def add_lineage_relationship(
        self,
        graph: LineageGraph,
        source_node_id: str,
        target_node_id: str,
        relationship_type: LineageRelationshipType,
        metadata: LineageMetadata
    ) -> LineageEdge:
        """
        Add relationship between nodes in lineage graph.
        
        Phase 2: Interface only - no relationship addition logic.
        
        Args:
            graph: Target lineage graph
            source_node_id: Source node identifier
            target_node_id: Target node identifier
            relationship_type: Type of relationship
            metadata: Edge metadata
            
        Returns:
            Created lineage edge
        """
        pass
    
    @abstractmethod
    def get_data_lineage(self, data_id: str) -> Optional[DataLineage]:
        """
        Get complete lineage for data entity.
        
        Phase 2: Interface only - no lineage retrieval logic.
        
        Args:
            data_id: Data entity identifier
            
        Returns:
            Data lineage information or None if not found
        """
        pass
    
    @abstractmethod
    def get_process_lineage(self, process_id: str) -> Optional[ProcessLineage]:
        """
        Get complete lineage for process entity.
        
        Phase 2: Interface only - no lineage retrieval logic.
        
        Args:
            process_id: Process entity identifier
            
        Returns:
            Process lineage information or None if not found
        """
        pass