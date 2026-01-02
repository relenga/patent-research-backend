"""
Pipeline Coordination Module - Tasks 3.2A.3-4

Implements coordination logic for complex document processing:
- 3-type diagram classification (critical/supporting/decorative)
- 3-level similarity thresholds (duplicate/near-duplicate/unique)
- Automatic classification rules based on content analysis
- HITL integration for near-duplicate decisions

Standards.md Compliance:
- Uses PostgreSQL persistence service patterns from P3.1
- Follows API response standards with ErrorCode enum
- Implements structured logging format
- Uses environment-based configuration patterns

Authority: PipelineStateMachine.md defines similarity handling and HITL escalation rules
"""

import logging
import hashlib
from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import re

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, and_

from .state_machine import PipelineImageState, TransitionTrigger
from .completion_calculator import DiagramType
from ...core.logger import get_logger
from ...core.db.database import async_engine


class SimilarityLevel(str, Enum):
    """3-level similarity classification per Phase 3.2A brief."""
    DUPLICATE = "duplicate"           # ≥95% similarity - Auto-link to canonical
    NEAR_DUPLICATE = "near_duplicate" # 80-94% similarity - BLOCKED state, HITL required  
    UNIQUE = "unique"                # <80% similarity - Standard processing pipeline


@dataclass
class DiagramClassification:
    """Result of diagram type classification."""
    image_id: str
    diagram_type: DiagramType
    confidence: float
    classification_reason: str
    auto_classified: bool
    requires_hitl: bool = False


@dataclass
class SimilarityAnalysis:
    """Result of similarity analysis against canonical diagrams."""
    image_id: str
    similarity_level: SimilarityLevel
    similarity_score: float
    canonical_match_id: Optional[str] = None
    canonical_description: Optional[str] = None
    requires_hitl: bool = False
    analysis_metadata: Optional[Dict[str, Any]] = None


@dataclass
class CoordinationDecision:
    """Final coordination decision for image processing."""
    image_id: str
    recommended_state: PipelineImageState
    recommended_trigger: TransitionTrigger
    diagram_classification: DiagramClassification
    similarity_analysis: SimilarityAnalysis
    processing_priority: str  # "CRITICAL", "STANDARD", "LOW"
    hitl_task_required: bool
    reasoning: str


class ClassificationError(Exception):
    """Raised when diagram classification fails."""
    def __init__(self, message: str, error_code: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.error_code = error_code
        self.context = context or {}


class DiagramClassifier:
    """
    Classifies diagrams into critical/supporting/decorative categories.
    
    Implements automatic classification rules per Phase 3.2A brief:
    - critical: Title/method diagrams (completion_weight: 2.0, hitl_priority: CRITICAL)
    - supporting: Detail diagrams (completion_weight: 1.0, hitl_priority: STANDARD)
    - decorative: Logos, borders (completion_weight: 0.1, hitl_priority: LOW)
    """
    
    # Classification confidence thresholds
    HIGH_CONFIDENCE_THRESHOLD = 0.85
    MEDIUM_CONFIDENCE_THRESHOLD = 0.65
    
    # Automatic classification patterns per Phase 3.2A brief
    CRITICAL_PATTERNS = [
        r"figure\s+\d+",           # "Figure 1", "Fig 1"
        r"fig\s*\d+",              
        r"system",                 # "System", "Method", "Process" 
        r"method",
        r"process",
        r"flowchart",
        r"workflow"
    ]
    
    DECORATIVE_PATTERNS = [
        r"logo",                   # Company logos
        r"trademark",              # Trademark symbols
        r"copyright",              # Copyright notices
        r"border",                 # Standard borders
        r"header",                 # Page headers
        r"footer"                  # Page footers
    ]

    def __init__(self):
        self.logger = get_logger(__name__)

    async def classify_diagram(
        self, 
        image_id: str, 
        image_metadata: Dict[str, Any]
    ) -> DiagramClassification:
        """
        Classify diagram type with automatic rules and confidence scoring.
        
        Args:
            image_id: Unique image identifier
            image_metadata: Extracted text, location, size, etc.
            
        Returns:
            DiagramClassification with type, confidence, and reasoning
        """
        try:
            # Extract relevant metadata
            extracted_text = image_metadata.get("extracted_text", "").lower()
            page_number = image_metadata.get("page_number", 0)
            image_position = image_metadata.get("position", {})
            file_size_kb = image_metadata.get("file_size_kb", 0)
            aspect_ratio = image_metadata.get("aspect_ratio", 1.0)
            
            # Apply classification rules
            classification = await self._apply_classification_rules(
                image_id, extracted_text, page_number, image_position, 
                file_size_kb, aspect_ratio
            )
            
            self.logger.info(
                "Diagram classified",
                extra={
                    "image_id": image_id,
                    "diagram_type": classification.diagram_type,
                    "confidence": classification.confidence,
                    "auto_classified": classification.auto_classified,
                    "requires_hitl": classification.requires_hitl
                }
            )
            
            return classification
            
        except Exception as e:
            self.logger.error(
                f"Diagram classification failed: {str(e)}",
                extra={
                    "image_id": image_id,
                    "error": str(e)
                }
            )
            raise ClassificationError(
                f"Classification failed for image {image_id}: {str(e)}",
                "CLASSIFICATION_ERROR",
                {"image_id": image_id, "error": str(e)}
            )

    async def _apply_classification_rules(
        self,
        image_id: str,
        extracted_text: str, 
        page_number: int,
        image_position: Dict[str, Any],
        file_size_kb: float,
        aspect_ratio: float
    ) -> DiagramClassification:
        """Apply automatic classification rules per Phase 3.2A brief."""
        
        confidence = 0.0
        classification_reasons = []
        
        # Rule 1: Check for critical diagram patterns
        critical_score = self._check_patterns(extracted_text, self.CRITICAL_PATTERNS)
        if critical_score > 0:
            confidence += critical_score * 0.4
            classification_reasons.append(f"Critical text patterns detected (score: {critical_score:.2f})")
        
        # Rule 2: Page 1 images with title content are likely critical
        if page_number <= 1 and any(word in extracted_text for word in ["title", "system", "method"]):
            confidence += 0.3
            classification_reasons.append("Title page content detected")
            
        # Rule 3: Check for decorative patterns
        decorative_score = self._check_patterns(extracted_text, self.DECORATIVE_PATTERNS)
        if decorative_score > 0:
            # If decorative patterns found, likely decorative
            return DiagramClassification(
                image_id=image_id,
                diagram_type=DiagramType.DECORATIVE,
                confidence=min(decorative_score, 0.95),
                classification_reason=f"Decorative patterns detected: {', '.join(classification_reasons)}",
                auto_classified=decorative_score >= self.MEDIUM_CONFIDENCE_THRESHOLD,
                requires_hitl=decorative_score < self.MEDIUM_CONFIDENCE_THRESHOLD
            )
            
        # Rule 4: Size and aspect ratio analysis
        if file_size_kb < 10 or aspect_ratio > 10 or aspect_ratio < 0.1:
            return DiagramClassification(
                image_id=image_id,
                diagram_type=DiagramType.DECORATIVE,
                confidence=0.8,
                classification_reason="Size/aspect ratio indicates decorative element",
                auto_classified=True,
                requires_hitl=False
            )
        
        # Determine final classification
        if confidence >= self.HIGH_CONFIDENCE_THRESHOLD:
            diagram_type = DiagramType.CRITICAL
            auto_classified = True
            requires_hitl = False
        elif confidence >= self.MEDIUM_CONFIDENCE_THRESHOLD:
            diagram_type = DiagramType.CRITICAL
            auto_classified = False
            requires_hitl = True  # Moderate confidence requires human confirmation
        else:
            # Default to supporting for technical diagrams
            diagram_type = DiagramType.SUPPORTING
            auto_classified = confidence > 0.3
            requires_hitl = not auto_classified
            
        return DiagramClassification(
            image_id=image_id,
            diagram_type=diagram_type,
            confidence=min(confidence, 0.95),  # Cap at 95% - never 100% certain
            classification_reason="; ".join(classification_reasons) if classification_reasons else "Default supporting classification",
            auto_classified=auto_classified,
            requires_hitl=requires_hitl
        )

    def _check_patterns(self, text: str, patterns: List[str]) -> float:
        """Check text against pattern list and return confidence score."""
        if not text:
            return 0.0
            
        matches = 0
        total_patterns = len(patterns)
        
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                matches += 1
                
        return matches / total_patterns if total_patterns > 0 else 0.0


class SimilarityAnalyzer:
    """
    Analyzes diagram similarity against canonical descriptions.
    
    Implements 3-level similarity thresholds per Phase 3.2A brief:
    - Duplicate (≥95%): Auto-link to canonical, skip processing
    - Near-duplicate (80-94%): BLOCKED state, create HITL task  
    - Unique (<80%): Standard processing pipeline
    """
    
    # Similarity thresholds per Phase 3.2A brief (simplified from original proposal)
    DUPLICATE_THRESHOLD = 95.0       # Auto-link to canonical
    NEAR_DUPLICATE_THRESHOLD = 80.0  # HITL decision required
    UNIQUE_THRESHOLD = 80.0          # Standard processing
    
    def __init__(self):
        self.logger = get_logger(__name__)

    async def analyze_similarity(
        self, 
        image_id: str, 
        perceptual_hash: str,
        corpus_id: str
    ) -> SimilarityAnalysis:
        """
        Analyze image similarity against canonical diagrams in same corpus.
        
        Args:
            image_id: Unique image identifier
            perceptual_hash: Perceptual hash of the image
            corpus_id: Corpus for similarity comparison (isolation enforcement)
            
        Returns:
            SimilarityAnalysis with similarity level and recommendations
        """
        try:
            # TODO: Query canonical diagrams from database when schema is ready
            # For now, simulate similarity analysis
            
            # Mock similarity analysis for Phase 3.2A development
            similarity_score = await self._calculate_mock_similarity(perceptual_hash)
            
            # Determine similarity level per Phase 3.2A thresholds
            if similarity_score >= self.DUPLICATE_THRESHOLD:
                similarity_level = SimilarityLevel.DUPLICATE
                canonical_match_id = f"canonical_{hash(perceptual_hash)[:8]}"
                canonical_description = "Mock canonical description for duplicate"
                requires_hitl = False
            elif similarity_score >= self.NEAR_DUPLICATE_THRESHOLD:
                similarity_level = SimilarityLevel.NEAR_DUPLICATE  
                canonical_match_id = f"canonical_{hash(perceptual_hash)[:8]}"
                canonical_description = "Mock canonical description for near-duplicate"
                requires_hitl = True  # HITL decision required per Phase 3.2A
            else:
                similarity_level = SimilarityLevel.UNIQUE
                canonical_match_id = None
                canonical_description = None
                requires_hitl = False
            
            analysis = SimilarityAnalysis(
                image_id=image_id,
                similarity_level=similarity_level,
                similarity_score=similarity_score,
                canonical_match_id=canonical_match_id,
                canonical_description=canonical_description,
                requires_hitl=requires_hitl,
                analysis_metadata={
                    "corpus_id": corpus_id,
                    "perceptual_hash": perceptual_hash,
                    "analysis_timestamp": "2024-01-01T00:00:00Z",  # TODO: Use TimeService
                    "comparison_method": "perceptual_hash"
                }
            )
            
            self.logger.info(
                "Similarity analysis completed",
                extra={
                    "image_id": image_id,
                    "similarity_level": similarity_level,
                    "similarity_score": similarity_score,
                    "requires_hitl": requires_hitl,
                    "corpus_id": corpus_id
                }
            )
            
            return analysis
            
        except Exception as e:
            self.logger.error(
                f"Similarity analysis failed: {str(e)}",
                extra={
                    "image_id": image_id,
                    "corpus_id": corpus_id,
                    "error": str(e)
                }
            )
            # Default to unique for safety
            return SimilarityAnalysis(
                image_id=image_id,
                similarity_level=SimilarityLevel.UNIQUE,
                similarity_score=0.0,
                requires_hitl=False,
                analysis_metadata={"error": str(e)}
            )

    async def _calculate_mock_similarity(self, perceptual_hash: str) -> float:
        """Mock similarity calculation for Phase 3.2A development."""
        # Use hash to generate consistent but varied similarity scores
        hash_int = int(hashlib.md5(perceptual_hash.encode()).hexdigest()[:8], 16)
        # Convert to 0-100 range with some clustering around thresholds
        base_score = (hash_int % 100)
        
        # Add some clustering around threshold boundaries for testing
        if 75 <= base_score <= 85:
            return float(base_score + 10)  # Push into near-duplicate range
        elif 90 <= base_score <= 95:
            return float(base_score + 5)   # Push into duplicate range
        else:
            return float(base_score)


class PipelineCoordinator:
    """
    Main coordination controller for complex document processing.
    
    Combines diagram classification and similarity analysis to make
    processing decisions for images in documents with 15-20+ diagrams.
    Prevents pipeline starvation through intelligent prioritization.
    """

    def __init__(self):
        self.logger = get_logger(__name__)
        self.classifier = DiagramClassifier()
        self.similarity_analyzer = SimilarityAnalyzer()

    async def coordinate_image_processing(
        self,
        image_id: str,
        image_metadata: Dict[str, Any],
        perceptual_hash: str,
        corpus_id: str
    ) -> CoordinationDecision:
        """
        Make comprehensive coordination decision for image processing.
        
        Combines classification and similarity analysis to determine:
        - Recommended state transition
        - Processing priority level
        - Whether HITL task is required
        - Reasoning for decision
        
        Args:
            image_id: Unique image identifier
            image_metadata: Extracted text, location, size, etc.
            perceptual_hash: Perceptual hash for similarity comparison
            corpus_id: Corpus for isolation enforcement
            
        Returns:
            CoordinationDecision with complete processing recommendations
        """
        try:
            # Perform diagram classification
            classification = await self.classifier.classify_diagram(image_id, image_metadata)
            
            # Perform similarity analysis
            similarity = await self.similarity_analyzer.analyze_similarity(
                image_id, perceptual_hash, corpus_id
            )
            
            # Make coordination decision based on both analyses
            decision = self._make_coordination_decision(classification, similarity)
            
            self.logger.info(
                "Coordination decision made",
                extra={
                    "image_id": image_id,
                    "recommended_state": decision.recommended_state,
                    "processing_priority": decision.processing_priority,
                    "hitl_required": decision.hitl_task_required,
                    "diagram_type": classification.diagram_type,
                    "similarity_level": similarity.similarity_level
                }
            )
            
            return decision
            
        except Exception as e:
            self.logger.error(
                f"Coordination decision failed: {str(e)}",
                extra={
                    "image_id": image_id,
                    "corpus_id": corpus_id,
                    "error": str(e)
                }
            )
            # Return safe default decision
            return self._create_fallback_decision(image_id, str(e))

    def _make_coordination_decision(
        self, 
        classification: DiagramClassification, 
        similarity: SimilarityAnalysis
    ) -> CoordinationDecision:
        """Make final coordination decision based on classification and similarity."""
        
        # Determine recommended state based on similarity level (per PipelineStateMachine.md)
        if similarity.similarity_level == SimilarityLevel.DUPLICATE:
            # Exact duplicate - immediate DUPLICATE_LINKED state
            recommended_state = PipelineImageState.DUPLICATE_LINKED
            recommended_trigger = TransitionTrigger.DUPLICATE_ANALYSIS_COMPLETE
            hitl_required = False
            reasoning = f"Exact duplicate (similarity: {similarity.similarity_score:.1f}%) - auto-linking to canonical"
            
        elif similarity.similarity_level == SimilarityLevel.NEAR_DUPLICATE:
            # Near-duplicate - BLOCKED state, create HITL task per Phase 3.2A
            recommended_state = PipelineImageState.NEEDS_HITL
            recommended_trigger = TransitionTrigger.DUPLICATE_ANALYSIS_COMPLETE
            hitl_required = True
            reasoning = f"Near-duplicate (similarity: {similarity.similarity_score:.1f}%) - human decision required"
            
        else:
            # Unique - standard processing pipeline
            if classification.requires_hitl:
                recommended_state = PipelineImageState.NEEDS_HITL
                recommended_trigger = TransitionTrigger.VISION_ANALYSIS_COMPLETE
                hitl_required = True
                reasoning = f"Unique diagram requiring classification confirmation ({classification.diagram_type})"
            else:
                recommended_state = PipelineImageState.NEEDS_INTERPRETATION
                recommended_trigger = TransitionTrigger.DUPLICATE_ANALYSIS_COMPLETE
                hitl_required = False
                reasoning = f"Unique {classification.diagram_type} diagram - standard processing"
        
        # Determine processing priority based on diagram type and similarity
        if classification.diagram_type == DiagramType.CRITICAL:
            processing_priority = "CRITICAL"
        elif (similarity.similarity_level == SimilarityLevel.DUPLICATE or 
              classification.diagram_type == DiagramType.SUPPORTING):
            processing_priority = "STANDARD"  
        else:
            processing_priority = "LOW"
        
        return CoordinationDecision(
            image_id=classification.image_id,
            recommended_state=recommended_state,
            recommended_trigger=recommended_trigger,
            diagram_classification=classification,
            similarity_analysis=similarity,
            processing_priority=processing_priority,
            hitl_task_required=hitl_required,
            reasoning=reasoning
        )

    def _create_fallback_decision(self, image_id: str, error_message: str) -> CoordinationDecision:
        """Create safe fallback decision when coordination fails."""
        # Default classification
        fallback_classification = DiagramClassification(
            image_id=image_id,
            diagram_type=DiagramType.SUPPORTING,
            confidence=0.0,
            classification_reason=f"Fallback due to error: {error_message}",
            auto_classified=False,
            requires_hitl=True
        )
        
        # Default similarity analysis
        fallback_similarity = SimilarityAnalysis(
            image_id=image_id,
            similarity_level=SimilarityLevel.UNIQUE,
            similarity_score=0.0,
            requires_hitl=True,
            analysis_metadata={"fallback": True, "error": error_message}
        )
        
        return CoordinationDecision(
            image_id=image_id,
            recommended_state=PipelineImageState.NEEDS_HITL,
            recommended_trigger=TransitionTrigger.MANUAL_OVERRIDE,
            diagram_classification=fallback_classification,
            similarity_analysis=fallback_similarity,
            processing_priority="STANDARD",
            hitl_task_required=True,
            reasoning=f"Fallback decision due to coordination error: {error_message}"
        )


# Export classes for use in other pipeline modules
__all__ = [
    "SimilarityLevel",
    "DiagramClassification", 
    "SimilarityAnalysis",
    "CoordinationDecision",
    "ClassificationError",
    "DiagramClassifier",
    "SimilarityAnalyzer", 
    "PipelineCoordinator"
]