# ER Diagram - Multimodal Processing

## Purpose

Image analysis pipeline extracting visual content from patent documents. Performs OCR on diagrams/figures, generates LLM-based descriptions of technical imagery, and creates searchable text representations of visual patent elements.

## Multimodal Processing Domain

```mermaid
%%{init: {"securityLevel": "loose"}}%%
erDiagram
    %% Referenced table (from Document Management domain)
    IMAGES_ref {
        uuid image_id PK
        uuid document_uuid FK
        varchar image_path
        varchar original_filename
        integer file_size_bytes
        varchar image_format
        varchar dimensions
        varchar perceptual_hash
        timestamp extracted_at
        varchar processing_state
        jsonb vision_analysis_result
        jsonb document_context
        text multimodal_description
        decimal generation_confidence
        decimal context_correlation_score
        jsonb sources_used
        jsonb ref_numerals_correlated
        varchar figure_type
        varchar technical_complexity
        varchar llm_model_used
        integer ocr_attempts
        integer vision_attempts
        boolean human_validated
        jsonb metadata
    }
    
    %% Multimodal Processing Tables
    IMAGE_OCR_RESULTS {
        uuid ocr_result_id PK
        uuid image_id FK
        varchar ocr_engine
        text extracted_text
        decimal confidence_score
        integer processing_time
        varchar language
        varchar engine_version
        varchar preprocessing_app
        timestamp created_timestamp
        timestamp updated_timestamp
        uuid created_by FK
        uuid updated_by FK
    }
    
    IMAGE_VISION_ANALYSIS {
        uuid vision_analysis_id PK
        uuid image_id FK
        jsonb detected_objects
        jsonb spatial_relations
        varchar layout_class
        decimal analysis_conf
        varchar processing_model
        timestamp created_timestamp
        timestamp updated_timestamp
        uuid created_by FK
        uuid updated_by FK
    }
    
    %% Domain Relationships
    IMAGES_ref ||--o{ IMAGE_OCR_RESULTS : processed_by
    IMAGES_ref ||--o{ IMAGE_VISION_ANALYSIS : analyzed_by
```

## Referenced Tables Legend
- **IMAGES_ref** → **IMAGES** (Document Management domain) - Source images for multimodal processing

## Cross-Domain Relationships

**To System Foundation domain:**
- `IMAGE_OCR_RESULTS.created_by` → `USERS.user_id`
- `IMAGE_OCR_RESULTS.updated_by` → `USERS.user_id`
- `IMAGE_VISION_ANALYSIS.created_by` → `USERS.user_id`
- `IMAGE_VISION_ANALYSIS.updated_by` → `USERS.user_id`

**To Document Management domain:**
- `IMAGE_OCR_RESULTS.image_id` → `IMAGES.image_id`
- `IMAGE_VISION_ANALYSIS.image_id` → `IMAGES.image_id`

## Domain Tables (2 + 1 referenced)

1. **`IMAGE_OCR_RESULTS`** - OCR extraction results with confidence scoring
2. **`IMAGE_VISION_ANALYSIS`** - Vision model analysis with spatial relationships
3. **`IMAGES`** (referenced) - Image metadata from Document Management domain

## Key Features

- **OCR Processing**: Multi-engine text extraction with confidence metrics
- **Vision Analysis**: Object detection and spatial relationship analysis
- **Performance Tracking**: Processing times and engine version tracking
- **Quality Assurance**: Confidence scoring and human validation workflows

## Processing Workflow

1. Images are stored in the Document Management domain
2. OCR engines extract text content with confidence scoring
3. Vision models analyze visual content and spatial relationships
4. Results are correlated with document context for multimodal understanding

---

**Last Updated**: January 7, 2026  
**Domain Tables**: 2 processing tables + 1 referenced  
**Status**: Multimodal content analysis pipeline

---
**VISUAL AUTHORITY** | **Implementation**: [database.py](../src/app/models/database.py) | **Requirements**: [DatabaseSchemaSpec.md](../design/DatabaseSchemaSpec.md), [CorpusRequirements.md](../proposals/CorpusDesign/CorpusRequirements.md)