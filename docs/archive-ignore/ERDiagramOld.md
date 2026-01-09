# xxxxxxxxxx %%{init: {"securityLevel": "loose"}}%%erDiagram    %% Core Document Management    CORPORA {        string corpus_id PK        string name        string description        string corpus_type        string isolation_level        timestamp created_timestamp        timestamp updated_timestamp        string created_by FK        string updated_by FK    }        DOCUMENTS {        uuid document_uuid PK        uuid corpus_id FK        varchar title        varchar source        varchar document_type        varchar current_state        varchar document_hash        jsonb document_structure        jsonb bibliographic_data        varchar deletion_strategy        varchar vector_cleanup_status        timestamp ingestion_timestamp        integer error_count        varchar uploaded_by        jsonb upload_source_info        timestamp created_timestamp        timestamp updated_timestamp        uuid created_by FK        uuid updated_by FK    }        DOCUMENT_VERSIONS {        uuid version_id PK        uuid document_uuid FK        integer version_number        text content        jsonb metadata        varchar version_reason        boolean marked_deleted        timestamp deleted_timestamp        varchar deletion_reason        varchar deleted_by        timestamp created_timestamp        timestamp updated_timestamp        uuid created_by FK        uuid updated_by FK    }        CORPUS_MEMBERSHIPS {        uuid membership_id PK        uuid corpus_id FK        uuid document_uuid FK        timestamp assigned_at        varchar assigned_by        varchar membership_reason        timestamp created_timestamp        timestamp updated_timestamp        uuid created_by FK        uuid updated_by FK    }        ARTIFACTS {        uuid artifact_id PK        uuid document_uuid FK        varchar artifact_type        varchar name        text content        bytea binary_data        jsonb metadata        boolean marked_deleted        timestamp deleted_timestamp        varchar deletion_reason        varchar deleted_by        timestamp created_timestamp        timestamp updated_timestamp        uuid created_by FK        uuid updated_by FK    }        IMAGES {        uuid image_id PK        uuid document_uuid FK        varchar image_path        varchar original_filename        integer file_size_bytes        varchar image_format        varchar dimensions        varchar perceptual_hash        timestamp extracted_at        varchar processing_state        jsonb vision_analysis_result        jsonb document_context        text multimodal_description        decimal generation_confidence        decimal context_correlation_score        jsonb sources_used        jsonb ref_numerals_correlated        varchar figure_type        varchar technical_complexity        varchar llm_model_used        integer ocr_attempts        integer vision_attempts        boolean human_validated        jsonb metadata    }        %% Multimodal Processing    IMAGE_OCR_RESULTS {        uuid ocr_result_id PK        uuid image_id FK        varchar ocr_engine        text extracted_text        decimal confidence_score        integer processing_time        varchar language        varchar engine_version        varchar preprocessing_app        timestamp created_timestamp        timestamp updated_timestamp        uuid created_by FK        uuid updated_by FK    }        IMAGE_VISION_ANALYSIS {        uuid vision_analysis_id PK        uuid image_id FK        jsonb detected_objects        jsonb spatial_relations        varchar layout_class        decimal analysis_conf        varchar processing_model        timestamp created_timestamp        timestamp updated_timestamp        uuid created_by FK        uuid updated_by FK    }        %% Agent & Task Management    AGENT_RUNS {        uuid agent_run_id PK        varchar agent_id        varchar agent_version        jsonb execution_params        jsonb corpus_access        jsonb input_data        jsonb output_data        varchar execution_status        timestamp start_time        timestamp end_time        text error_details        integer retry_count        timestamp created_timestamp        timestamp updated_timestamp        uuid created_by FK        uuid updated_by FK    }        TASKS {        uuid task_id PK        varchar task_type        varchar task_status        varchar assigned_to        integer priority        date due_date        jsonb evidence_bundle        jsonb completion_data        jsonb task_metadata        timestamp created_timestamp        timestamp updated_timestamp        uuid created_by FK        uuid updated_by FK    }        DIAGRAM_CANONICAL {        uuid diagram_id PK        uuid artifact_id FK        varchar canonical_format        jsonb diagram_data        varchar approval_status        varchar approved_by        timestamp approval_date        jsonb version_history        jsonb source_references        jsonb usage_context        timestamp created_timestamp        timestamp updated_timestamp        uuid created_by FK        uuid updated_by FK    }        VECTOR_CLEANUP_AUDIT {        uuid cleanup_audit_id PK        uuid document_uuid FK        varchar cleanup_strategy        integer vectors_deleted        jsonb sections_affected        integer cleanup_time        varchar cleanup_reason        boolean restoration_ok        jsonb audit_trail        timestamp created_timestamp        timestamp updated_timestamp        uuid created_by FK        uuid updated_by FK    }        VECTOR_RESTORATION_CACHE {        uuid restoration_cache_id PK        uuid document_uuid FK        jsonb cached_vectors        jsonb cached_sections        timestamp cache_timestamp        timestamp expiry_timestamp        integer restoration_cnt        timestamp created_timestamp        timestamp updated_timestamp        uuid created_by FK        uuid updated_by FK    }        %% Audit & Provenance System    AUDIT_EVENTS {        uuid audit_event_id PK        varchar event_type        varchar event_name        text event_descript        varchar actor_type        varchar actor_id        varchar actor_name        varchar session_id        varchar resource_type        varchar resource_id        varchar resource_name        varchar action_taken        text action_rationale        jsonb before_state        jsonb after_state        varchar request_id        varchar correlation_id        varchar trace_id        timestamp event_timestamp        varchar timezone        varchar dev_phase        varchar ruleset_version        varchar enforcement_mode        jsonb affected_res        varchar impact_level        boolean requires_hitl        uuid hitl_task_id FK        jsonb additional_ctx        varchar source_system        timestamp created_timestamp        timestamp updated_timestamp        uuid created_by FK        uuid updated_by FK    }        PIPELINE_EVENT_LOGS {        uuid event_log_id PK        uuid audit_event_id FK        varchar event_id        varchar event_type        integer priority        varchar source        timestamp event_timestamp        varchar document_id        varchar image_id        varchar batch_id        varchar user_id        jsonb payload        boolean delivered        integer delivery_attempt        timestamp last_delivery        jsonb delivery_errors        timestamp created_timestamp        timestamp updated_timestamp        uuid created_by FK        uuid updated_by FK    }        PIPELINE_OVERRIDE_AUDITS {        uuid override_audit_id PK        varchar override_id        uuid administrator_id FK        varchar admin_role        varchar admin_ip        varchar action        varchar reason_category        text justification        timestamp requested_at        timestamp executed_at        timestamp completed_at        jsonb context        jsonb metadata        boolean success        text error_message        boolean rollback_done        uuid audit_event_id FK        timestamp created_timestamp        timestamp updated_timestamp        uuid created_by FK        uuid updated_by FK    }        PROVENANCE_RECORDS {        uuid provenance_record_id PK        uuid source_art_id        uuid derived_art_id        varchar transform_type        jsonb transform_detail        varchar processing_agent        decimal confidence_score        timestamp created_timestamp        timestamp updated_timestamp        uuid created_by FK        uuid updated_by FK    }        USERS {        uuid user_id PK        varchar username        varchar email        boolean is_llm_agent        varchar agent_type        varchar agent_version        jsonb capabilities        timestamp created_timestamp        timestamp updated_timestamp    }        %% Relationships    CORPORA ||--o{ DOCUMENTS : contains    CORPORA ||--o{ CORPUS_MEMBERSHIPS : has    DOCUMENTS ||--o{ DOCUMENT_VERSIONS : versioned_as    DOCUMENTS ||--o{ CORPUS_MEMBERSHIPS : member_of    DOCUMENTS ||--o{ ARTIFACTS : contains    DOCUMENTS ||--o{ IMAGES : contains    DOCUMENTS ||--o{ VECTOR_CLEANUP_AUDIT : audited_by    DOCUMENTS ||--o{ VECTOR_RESTORATION_CACHE : cached_by    IMAGES ||--o{ IMAGE_OCR_RESULTS : processed_by    IMAGES ||--o{ IMAGE_VISION_ANALYSIS : analyzed_by    ARTIFACTS ||--o{ DIAGRAM_CANONICAL : canonicalized_as    TASKS ||--o{ AUDIT_EVENTS : triggers    AUDIT_EVENTS ||--o{ PIPELINE_EVENT_LOGS : logged_as    AUDIT_EVENTS ||--o{ PIPELINE_OVERRIDE_AUDITS : overridden_by    USERS ||--o{ PIPELINE_OVERRIDE_AUDITS : administersmermaid#mermaidChart13{font-family:sans-serif;font-size:16px;fill:#333;}@keyframes edge-animation-frame{from{stroke-dashoffset:0;}}@keyframes dash{to{stroke-dashoffset:0;}}#mermaidChart13 .edge-animation-slow{stroke-dasharray:9,5!important;stroke-dashoffset:900;animation:dash 50s linear infinite;stroke-linecap:round;}#mermaidChart13 .edge-animation-fast{stroke-dasharray:9,5!important;stroke-dashoffset:900;animation:dash 20s linear infinite;stroke-linecap:round;}#mermaidChart13 .error-icon{fill:#552222;}#mermaidChart13 .error-text{fill:#552222;stroke:#552222;}#mermaidChart13 .edge-thickness-normal{stroke-width:1px;}#mermaidChart13 .edge-thickness-thick{stroke-width:3.5px;}#mermaidChart13 .edge-pattern-solid{stroke-dasharray:0;}#mermaidChart13 .edge-thickness-invisible{stroke-width:0;fill:none;}#mermaidChart13 .edge-pattern-dashed{stroke-dasharray:3;}#mermaidChart13 .edge-pattern-dotted{stroke-dasharray:2;}#mermaidChart13 .marker{fill:#333333;stroke:#333333;}#mermaidChart13 .marker.cross{stroke:#333333;}#mermaidChart13 svg{font-family:sans-serif;font-size:16px;}#mermaidChart13 p{margin:0;}#mermaidChart13 .entityBox{fill:#ECECFF;stroke:#9370DB;}#mermaidChart13 .relationshipLabelBox{fill:hsl(80, 100%, 96.2745098039%);opacity:0.7;background-color:hsl(80, 100%, 96.2745098039%);}#mermaidChart13 .relationshipLabelBox rect{opacity:0.5;}#mermaidChart13 .labelBkg{background-color:rgba(248.6666666666, 255, 235.9999999999, 0.5);}#mermaidChart13 .edgeLabel .label{fill:#9370DB;font-size:14px;}#mermaidChart13 .label{font-family:sans-serif;color:#333;}#mermaidChart13 .edge-pattern-dashed{stroke-dasharray:8,8;}#mermaidChart13 .node rect,#mermaidChart13 .node circle,#mermaidChart13 .node ellipse,#mermaidChart13 .node polygon{fill:#ECECFF;stroke:#9370DB;stroke-width:1px;}#mermaidChart13 .relationshipLine{stroke:#333333;stroke-width:1;fill:none;}#mermaidChart13 .marker{fill:none!important;stroke:#333333!important;stroke-width:1;}#mermaidChart13 :root{--mermaid-alt-font-family:sans-serif;}containshasversioned_asmember_ofcontainscontainsaudited_bycached_byprocessed_byanalyzed_bycanonicalized_astriggerslogged_asoverridden_byadministersCORPORAstringcorpus_idPKstringnamestringdescriptionstringcorpus_typestringisolation_leveltimestampcreated_timestamptimestampupdated_timestampstringcreated_byFKstringupdated_byFKDOCUMENTSuuiddocument_uuidPKuuidcorpus_idFKvarchartitlevarcharsourcevarchardocument_typevarcharcurrent_statevarchardocument_hashjsonbdocument_structurejsonbbibliographic_datavarchardeletion_strategyvarcharvector_cleanup_statustimestampingestion_timestampintegererror_countvarcharuploaded_byjsonbupload_source_infotimestampcreated_timestamptimestampupdated_timestampuuidcreated_byFKuuidupdated_byFKDOCUMENT_VERSIONSuuidversion_idPKuuiddocument_uuidFKintegerversion_numbertextcontentjsonbmetadatavarcharversion_reasonbooleanmarked_deletedtimestampdeleted_timestampvarchardeletion_reasonvarchardeleted_bytimestampcreated_timestamptimestampupdated_timestampuuidcreated_byFKuuidupdated_byFKCORPUS_MEMBERSHIPSuuidmembership_idPKuuidcorpus_idFKuuiddocument_uuidFKtimestampassigned_atvarcharassigned_byvarcharmembership_reasontimestampcreated_timestamptimestampupdated_timestampuuidcreated_byFKuuidupdated_byFKARTIFACTSuuidartifact_idPKuuiddocument_uuidFKvarcharartifact_typevarcharnametextcontentbyteabinary_datajsonbmetadatabooleanmarked_deletedtimestampdeleted_timestampvarchardeletion_reasonvarchardeleted_bytimestampcreated_timestamptimestampupdated_timestampuuidcreated_byFKuuidupdated_byFKIMAGESuuidimage_idPKuuiddocument_uuidFKvarcharimage_pathvarcharoriginal_filenameintegerfile_size_bytesvarcharimage_formatvarchardimensionsvarcharperceptual_hashtimestampextracted_atvarcharprocessing_statejsonbvision_analysis_resultjsonbdocument_contexttextmultimodal_descriptiondecimalgeneration_confidencedecimalcontext_correlation_scorejsonbsources_usedjsonbref_numerals_correlatedvarcharfigure_typevarchartechnical_complexityvarcharllm_model_usedintegerocr_attemptsintegervision_attemptsbooleanhuman_validatedjsonbmetadataIMAGE_OCR_RESULTSuuidocr_result_idPKuuidimage_idFKvarcharocr_enginetextextracted_textdecimalconfidence_scoreintegerprocessing_timevarcharlanguagevarcharengine_versionvarcharpreprocessing_apptimestampcreated_timestamptimestampupdated_timestampuuidcreated_byFKuuidupdated_byFKIMAGE_VISION_ANALYSISuuidvision_analysis_idPKuuidimage_idFKjsonbdetected_objectsjsonbspatial_relationsvarcharlayout_classdecimalanalysis_confvarcharprocessing_modeltimestampcreated_timestamptimestampupdated_timestampuuidcreated_byFKuuidupdated_byFKAGENT_RUNSuuidagent_run_idPKvarcharagent_idvarcharagent_versionjsonbexecution_paramsjsonbcorpus_accessjsonbinput_datajsonboutput_datavarcharexecution_statustimestampstart_timetimestampend_timetexterror_detailsintegerretry_counttimestampcreated_timestamptimestampupdated_timestampuuidcreated_byFKuuidupdated_byFKTASKSuuidtask_idPKvarchartask_typevarchartask_statusvarcharassigned_tointegerprioritydatedue_datejsonbevidence_bundlejsonbcompletion_datajsonbtask_metadatatimestampcreated_timestamptimestampupdated_timestampuuidcreated_byFKuuidupdated_byFKDIAGRAM_CANONICALuuiddiagram_idPKuuidartifact_idFKvarcharcanonical_formatjsonbdiagram_datavarcharapproval_statusvarcharapproved_bytimestampapproval_datejsonbversion_historyjsonbsource_referencesjsonbusage_contexttimestampcreated_timestamptimestampupdated_timestampuuidcreated_byFKuuidupdated_byFKVECTOR_CLEANUP_AUDITuuidcleanup_audit_idPKuuiddocument_uuidFKvarcharcleanup_strategyintegervectors_deletedjsonbsections_affectedintegercleanup_timevarcharcleanup_reasonbooleanrestoration_okjsonbaudit_trailtimestampcreated_timestamptimestampupdated_timestampuuidcreated_byFKuuidupdated_byFKVECTOR_RESTORATION_CACHEuuidrestoration_cache_idPKuuiddocument_uuidFKjsonbcached_vectorsjsonbcached_sectionstimestampcache_timestamptimestampexpiry_timestampintegerrestoration_cnttimestampcreated_timestamptimestampupdated_timestampuuidcreated_byFKuuidupdated_byFKAUDIT_EVENTSuuidaudit_event_idPKvarcharevent_typevarcharevent_nametextevent_descriptvarcharactor_typevarcharactor_idvarcharactor_namevarcharsession_idvarcharresource_typevarcharresource_idvarcharresource_namevarcharaction_takentextaction_rationalejsonbbefore_statejsonbafter_statevarcharrequest_idvarcharcorrelation_idvarchartrace_idtimestampevent_timestampvarchartimezonevarchardev_phasevarcharruleset_versionvarcharenforcement_modejsonbaffected_resvarcharimpact_levelbooleanrequires_hitluuidhitl_task_idFKjsonbadditional_ctxvarcharsource_systemtimestampcreated_timestamptimestampupdated_timestampuuidcreated_byFKuuidupdated_byFKPIPELINE_EVENT_LOGSuuidevent_log_idPKuuidaudit_event_idFKvarcharevent_idvarcharevent_typeintegerpriorityvarcharsourcetimestampevent_timestampvarchardocument_idvarcharimage_idvarcharbatch_idvarcharuser_idjsonbpayloadbooleandeliveredintegerdelivery_attempttimestamplast_deliveryjsonbdelivery_errorstimestampcreated_timestamptimestampupdated_timestampuuidcreated_byFKuuidupdated_byFKPIPELINE_OVERRIDE_AUDITSuuidoverride_audit_idPKvarcharoverride_iduuidadministrator_idFKvarcharadmin_rolevarcharadmin_ipvarcharactionvarcharreason_categorytextjustificationtimestamprequested_attimestampexecuted_attimestampcompleted_atjsonbcontextjsonbmetadatabooleansuccesstexterror_messagebooleanrollback_doneuuidaudit_event_idFKtimestampcreated_timestamptimestampupdated_timestampuuidcreated_byFKuuidupdated_byFKPROVENANCE_RECORDSuuidprovenance_record_idPKuuidsource_art_iduuidderived_art_idvarchartransform_typejsonbtransform_detailvarcharprocessing_agentdecimalconfidence_scoretimestampcreated_timestamptimestampupdated_timestampuuidcreated_byFKuuidupdated_byFKUSERSuuiduser_idPKvarcharusernamevarcharemailbooleanis_llm_agentvarcharagent_typevarcharagent_versionjsonbcapabilitiestimestampcreated_timestamptimestampupdated_timestamp

**Status**: CONSOLIDATION DOCUMENT - Visual representation of authoritative design specifications  
**Authority**: This document consolidates and visualizes table designs from official APPROVED specifications  
**Source Documents**: [DatabaseSchemaSpec.md](design/DatabaseSchemaSpec.md), [LoggingAndEventsSpec.md](design/LoggingAndEventsSpec.md), [CorpusRequirements.md](proposals/CorpusDesign/CorpusRequirements.md)  
**Last Updated**: January 7, 2026

## Purpose

This document provides a comprehensive visual representation of the complete database schema for the patent intelligence system. It consolidates table definitions from multiple authoritative design documents to show the full system architecture in a single view.

**⚠️ IMPORTANT**: This document is **NOT** the design authority. For implementation details, constraints, and official specifications, refer to the source documents listed above. Any conflicts should be resolved by referring to the authoritative design specifications.

## Complete System Entity Relationship Diagram

```

┌─────────────────┐     ┌────────────────────────────────────────┐     ┌─────────────────┐
│     corpora     │     │           documents                    │     │ document_versions│
├─────────────────┤     ├────────────────────────────────────────┤     │                 │
│ corpus_id (PK)  │◄────│ corpus_id (FK)                         │────►│ version_id (PK) │
│ name            │  │  │ document_uuid (PK)                     │  │  │document_uuid(FK)│
│ description     │  │  │ title, source, document_type           │  │  │ version_number  │
│ corpus_type     │  │  │ current_state, document_hash           │  │  │ content         │
│ isolation_level │  │  │ document_structure (JSONB)             │  │  │ metadata (JSONB)│
│ created_timestamp│ │  │ bibliographic_data (JSONB)             │  │  │ version_reason  │
│ updated_timestamp│ │  │ deletion_strategy                      │  │  │ marked_deleted  │
│ created_by*     │  │  │ vector_cleanup_status                  │  │  │deleted_timestamp│
│ updated_by*     │  │  │ ingestion_timestamp, processing_*      │  │  │ deletion_reason │
└─────────────────┘  │  │ error_count                            │  │  │ deleted_by      │
                     │  │ uploaded_by (user|research_agent)      │  │  │created_timestamp│
        ┌────────────┘  │ upload_source_info (JSONB)             │  │  │ created_by*     │
        │               │ created_timestamp, updated_timestamp   │  │  │updated_timestamp│
        │               │ created_by*, updated_by*               │  │  │ updated_by*     │
        ▼               └────────────────────────────────────────┘  │  └─────────────────┘
┌─────────────────┐                      │                         │                          
│corpus_memberships│                     │ 1:N                     │ 1:N                      
├─────────────────┤                      ▼                         ▼                          
│membership_id(PK)│             ┌─────────────────┐       ┌──────────────────────────────────┐
│ corpus_id (FK)  │             │    artifacts    │       │         images                   │
│document_uuid(FK)│             │                 │       ├──────────────────────────────────┤
│ assigned_at     │             ├─────────────────┤       │ image_id (PK)                    │
│ assigned_by*    │             │ artifact_id(PK) │       │ document_uuid (FK)               │
│ membership_reason│            │document_uuid(FK)│       │ image_path, original_filename    │
│created_timestamp│             │ artifact_type   │       │ file_size_bytes, image_format    │
│ created_by*     │             │ name, content   │       │ dimensions, perceptual_hash      │
│updated_timestamp│             │ binary_data     │       │ extracted_at, processing_state   │
│ updated_by*     │             │ metadata (JSONB)│       │ vision_analysis_result (JSONB)   │
└─────────────────┘             │ marked_deleted  │       │ document_context (JSONB)         │
                                │deleted_timestamp│       │ multimodal_description           │
                                │ deletion_reason │       │ generation_confidence            │
                                │ deleted_by      │       │ context_correlation_score        │
                                │created_timestamp│       │ sources_used (JSONB)             │
                                │ created_by*     │       │ ref_numerals_correlated (JSONB)  │
                                │updated_timestamp│       │ figure_type                      │
                                │ updated_by*     │       │ technical_complexity             │
                                └─────────────────┘       │ llm_model_used                   │
                                                          │ ocr_attempts, vision_attempts    │
                                                          │ human_validated, metadata        │
                                                                   │ 1:N        │ 1:N         
                                                                   ▼            ▼             
                                                        ┌─────────────────┐ ┌─────────────────┐
                                                        │image_ocr_results│ │image_vision_anal│
                                                        ├─────────────────┤ ├─────────────────┤
│ ocr_result_id(PK)│ │vision_analysis  │
│ image_id (FK)   │ │_id (PK)         │
│ ocr_engine      │ │ image_id (FK)   │
│ extracted_text  │ │ detected_objects│
│ confidence_score│ │ spatial_relations│
│ processing_time │ │ layout_class    │
│ language        │ │ analysis_conf   │
│ engine_version  │ │ processing_model│
│preprocessing_app│ │created_timestamp│
│created_timestamp│ │ created_by*     │
│ created_by*     │ │updated_timestamp│
│updated_timestamp│ │ updated_by*     │
│ updated_by*     │ │                 │
└─────────────────┘ │                 │
                    │                 │
                    └─────────────────┘

┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   agent_runs    │     │      tasks      │     │diagram_canonical│     │vector_cleanup   │
├─────────────────┤     ├─────────────────┤     ├─────────────────┤     │_audit           │
│ agent_run_id(PK)│     │ task_id (PK)    │     │ diagram_id (PK) │     ├─────────────────┤
│ agent_id        │     │ task_type       │     │ artifact_id (FK)│     │cleanup_audit_id │
│ agent_version   │     │ task_status     │     │ canonical_format│     │ (PK)            │
│ execution_params│     │ assigned_to     │     │ diagram_data    │     │document_uuid(FK)│
│ corpus_access   │     │ created_by      │     │ approval_status │     │ cleanup_strategy│
│ input_data      │     │ priority        │     │ approved_by     │     │ vectors_deleted │
│ output_data     │     │ due_date        │     │ approval_date   │     │ sections_affected│
│ execution_status│     │ evidence_bundle │     │ version_history │     │ cleanup_time    │
│ start_time      │     │ completion_data │     │ source_references│    │ cleanup_reason  │
│ end_time        │     │ task_metadata   │     │ usage_context   │     │ restoration_ok  │
│ error_details   │     │created_timestamp│     │created_timestamp│     │ audit_trail     │
│ retry_count     │     │ created_by*     │     │ created_by*     │     │created_timestamp│
│created_timestamp│     │updated_timestamp│     │updated_timestamp│     │ created_by*     │
│ created_by*     │     │ updated_by*     │     │ updated_by*     │     │updated_timestamp│
│updated_timestamp│     └─────────────────┘     └─────────────────┘     │ updated_by*     │
│ updated_by*     │                                                     └─────────────────┘
└─────────────────┘     ┌─────────────────┐                                                     
                        │vector_restoration│                                                     
                        │_cache           │                                                     
├─────────────────┤                                                     
│restoration_cache│                                                     
│_id (PK)         │                                                     
│document_uuid(FK)│                                                     
│ cached_vectors  │                                                     
│ cached_sections │                                                     
│ cache_timestamp │                                                     
│ expiry_timestamp│                                                     
│ restoration_cnt │                                                     
│created_timestamp│                                                     
│ created_by*     │                                                     
│updated_timestamp│                                                     
│ updated_by*     │                                                     
└─────────────────┘

┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  audit_events   │     │pipeline_event   │     │pipeline_override│     │provenance_records│
│                 │     │_logs            │     │_audits          │     │                  │
├─────────────────┤     ├─────────────────┤     ├─────────────────┤     ├─────────────────┤
│ audit_event_id  │◄────│ audit_event_id  │◄─┐  │ override_audit  │     │ provenance_     │
│ (PK - uuid)     │     │ (FK audit_events)│  │  │ _id (PK)        │     │ record_id (PK)  │
│ event_type      │     │ event_log_id(PK)│  │  │ override_id     │     │ source_art_id   │
│ event_name      │     │ event_id (uuid) │  │  │ (uuid)          │     │ derived_art_id  │
│ event_descript  │     │ priority        │  │  │ administrator_id│  │  │ transform_type  │
│ actor_type      │     │ source          │  │  │ (FK users)      │──┘  │ transform_detail│
│   │ actor_id        │     │ event_timestamp │  │  │ admin_role      │  │  │ processing_agent│     │
│   │ actor_name      │     │ document_id     │  │  │ admin_ip        │  │  │ confidence_score│     │
│   │ session_id      │     │ image_id        │  │  │ action          │  │  │created_timestamp│     │
│   │ resource_type   │     │ batch_id        │  │  │ reason_category │  │  │ created_by      │     │
│   │ resource_id     │     │ user_id         │  │  │ justification   │  │  │updated_timestamp│     │
│   │ resource_name   │     │ payload (JSONB) │  │  │ requested_at    │  │  │ updated_by      │     │
│   │ action_taken    │     │ delivered       │  │  │ executed_at     │  │  └─────────────────┘     │
│   │ action_rationale│     │ delivery_attempt│  │  │ completed_at    │  │                          │
│   │ before_state    │     │ last_delivery   │  │  │ context (JSONB) │  │                          │
│   │ after_state     │     │ delivery_errors │  │  │ metadata (JSONB)│  │                          │
│   │ request_id      │     │ audit_event_id  │◄─┘  │ success         │  │                          │
│   │ correlation_id  │     │ (FK audit_events│     │ error_message   │  │                          │
│   │ trace_id        │     │created_timestamp│     │ rollback_done   │  │                          │
│   │ event_timestamp │     │ created_by*     │     │ audit_event_id  │◄─────────────────────────────┘
│   │ timezone        │     │updated_timestamp│     │ (FK audit_events)                           │
│   │ dev_phase       │     │ updated_by*     │     │created_timestamp│                             │
│   │ ruleset_version │     └─────────────────┘     │ created_by*     │                             │
│   │ enforcement_mode│                             │updated_timestamp│                             │
│   │ affected_res    │                             │ updated_by*     │                             │
│   │ impact_level    │                             └─────────────────┘                             │
│   │ requires_hitl   │                                                                             │
│   │ hitl_task_id(FK)│  │          ┌─────────────────┐                                             │
│   │ additional_ctx  │  │          │     users       │                                             │
│   │ source_system   │  │          │   (enhanced)    │                                             │
│   │created_timestamp│  │          ├─────────────────┤                                             │
│   │ created_by      │  │          │ user_id (PK)    │──────────────────┐                          │
│   │updated_timestamp│  │          │ username        │                  │                          │
│   │ updated_by      │  │          │ email           │                  │                          │
│   └─────────────────┘  │          │ is_llm_agent    │                  │                          │
│                        │          │ agent_type      │                  │                          │
│                        │          │ agent_version   │                  │                          │
│                        │          │ capabilities    │                  │                          │
│                        │          │created_timestamp│  ┌──────────────┘                           │
│                        │          │updated_timestamp│  │                                          │
└───────────────────────────────────────────────────────────────────────────────────────────────┘

```

**Field Notation:**
- Fields marked with * (asterisk) have foreign key relationships to `users.user_id`
- All `created_by*` and `updated_by*` fields reference the `users` table for audit accountability

## Table Summary

### **Core Document Management (6 tables)**
1. **`corpora`** - Corpus definitions and isolation policies
2. **`documents`** - Primary document entities with enhanced metadata
3. **`document_versions`** - Immutable version history with soft delete
4. **`corpus_memberships`** - Document-to-corpus assignment tracking
5. **`artifacts`** - Document-derived content (text, images, diagrams)
6. **`images`** - Enhanced image metadata with multimodal analysis

### **Multimodal Processing (2 tables)**
7. **`image_ocr_results`** - OCR extraction results with confidence scoring
8. **`image_vision_analysis`** - Vision model analysis with spatial relationships

### **Agent & Task Management (4 tables)**
9. **`agent_runs`** - Agent execution tracking and performance metrics
10. **`tasks`** - HITL task lifecycle and evidence bundle management
11. **`diagram_canonical`** - Canonical diagram representations with approval workflow
12. **`vector_cleanup_audit`** - Vector lifecycle management and cleanup tracking

### **Vector Management (1 table)**
13. **`vector_restoration_cache`** - Cached vector data for restoration operations

### **Audit & Provenance System (5 tables)**
14. **`audit_events`** - Primary audit event logging (immutable)
15. **`pipeline_event_logs`** - Operational pipeline event correlation
16. **`pipeline_override_audits`** - Administrative override tracking
17. **`provenance_records`** - Lineage and transformation tracking
18. **`users`** - Enhanced user/agent identity with LLM agent tracking

## Key Design Features

### **Audit Accountability**
- All tables include standardized audit fields (`created_timestamp`, `updated_timestamp`, `created_by`, `updated_by`)
- Complete traceability through cross-table foreign key relationships
- LLM agent distinction in users table for comprehensive audit trails

### **Multimodal Processing Support**
- Enhanced image processing with OCR and vision analysis
- Confidence scoring and human validation workflows
- Comprehensive metadata capture for all processing steps

### **Corpus Isolation**
- Document-to-corpus assignment tracking via `corpus_memberships`
- Isolation policy enforcement at database level
- Complete audit trails for membership changes

### **Agent Management**
- Full agent execution lifecycle tracking
- HITL task management with evidence bundles
- Performance metrics and error handling

## Authority and Implementation Notes

**Design Authority**: Individual table specifications are defined in:
- [DatabaseSchemaSpec.md](design/DatabaseSchemaSpec.md) - Core P3.1 tables (APPROVED)
- [LoggingAndEventsSpec.md](design/LoggingAndEventsSpec.md) - Audit system tables (APPROVED)
- [CorpusRequirements.md](proposals/CorpusDesign/CorpusRequirements.md) - Enhanced multimodal tables (PROPOSAL)

**Implementation Status**:
- ✅ Core P3.1 tables: Implemented and tested
- 🔄 Multimodal enhancement tables: Proposed (requires approval)
- ✅ Audit system integration: Specified and ready for implementation

**Database Standards**: All implementations must comply with [Standards.md](Standards.md) for naming conventions, session management, and audit field requirements.

---

**Last Updated**: January 7, 2026  
**Total Tables**: 18 tables across 4 functional domains  
**Status**: CONSOLIDATION COMPLETE - All known system tables documented

## Excluded Tables

### **`audit_records` - REMOVED**
**Reason for Original Inclusion**: Appeared in proposal document [CorpusRequirements.md](proposals/CorpusDesign/CorpusRequirements.md) as speculative enhancement

**Why Removed**: 
- **No Implementation**: Does not exist in actual P3.1 database schema (src/app/models/database.py)
- **No Official Requirement**: Not specified in any APPROVED design documents
- **Redundant Functionality**: `audit_events` table already provides comprehensive audit logging
- **Phantom Table**: Only appeared in proposal documents mixing implemented and speculative features

**Foreign Key Analysis**: If it existed, it would likely need:
- `audit_event_id` (FK to audit_events) - Parent audit event reference
- `entity_id` (Polymorphic FK) - Reference to audited entity
- `created_by` (FK to users) - Standard audit field

**Requirements Assessment**: No legitimate requirement drove its inclusion. The existing `audit_events` table fulfills all audit requirements per [DatabaseSchemaSpec.md](design/DatabaseSchemaSpec.md) and [ProvenanceAudit.md](ProvenanceAudit.md).