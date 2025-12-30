# DataFlowDiagram.md
## Data Flow Diagram — Governed Patent Intelligence Backend

### Document Authority
- This document is derived from SystemNarrative.md
- It describes how data flows, not what the system means
- It is non-authoritative for requirements or behavior

### Actors
- **Human User**
- **Research Agent**

### Data Stores
- **Raw Artifact Store** (original PDFs/XML/HTML/images)
- **Normalized Store** (normalized text/metadata/assets)
- **Figure Registry** (figure objects + fingerprints + reuse links)
- **Chunk Store** (text chunks + figure-description chunks)
- **Vector Index** (retrieval embeddings)
- **Relational DB** (documents, states, tasks, provenance, corpora membership)
- **HITL Queue** (tasks for human verification)
- **Audit/Lineage Graph** (provenance records)

### Processing Components
- **Ingestion API**
- **Normalization Pipeline**
- **Figure Extractor**
- **OCR/Caption Pipeline**
- **Figure Description Step**
- **Chunking Pipeline**
- **Embedding Step**
- **Corpus Manager**
- **Orchestrator/Supervisor**
- **Retriever**
- **LLM Drafting/Analysis Agents**
- **HITL Task Generator**
- **Provenance/Lineage Recorder**
- **Exports**

### Data Flow Diagram
```mermaid
flowchart LR
  U[Human User] -->|manual upload| API[Ingestion API]
  RA[Research Agent] -->|fetch patents/OA/IPR/prior art/product docs| API

  API -->|register doc + source_type + doc_type| DB[(Relational DB)]
  API -->|store original bytes| RAW[(Raw Artifact Store)]

  RAW -->|normalize: PDF/XML/HTML parse| NORM[Normalization Pipeline]
  NORM -->|normalized text + metadata| NSTORE[(Normalized Store)]
  NORM -->|extracted images/figures| FIGX[Figure Extractor]

  FIGX -->|figure objects + fingerprints| FREG[(Figure Registry)]
  FREG -->|same-as/derived-from links| DB

  FIGX -->|OCR (if needed) + captions| OCR[OCR/Caption Pipeline]
  OCR -->|figure text + regions| NSTORE

  NSTORE -->|chunking| CHUNK[Chunking Pipeline]
  OCR -->|figure descriptions| FDESC[Figure Description Step]
  FDESC -->|figure-description artifacts| CHUNK

  CHUNK -->|persist chunks| CSTORE[(Chunk Store)]
  CHUNK -->|embed chunks| EMB[Embedding Step]
  EMB -->|vectors| VEC[(Vector Index)]

  DB -->|corpus membership| CORP[Corpus Manager]
  CORP --> DB

  U -->|run drafting workflow| ORCH[Orchestrator/Supervisor]
  ORCH -->|retrieve context| RETR[Retriever]
  RETR -->|query| VEC
  RETR -->|citations + evidence| ORCH

  ORCH -->|draft claims| LLM[LLM Drafting/Analysis Agents]
  LLM -->|candidates + structured outputs| ORCH

  ORCH -->|need verification| HITL[HITL Task Generator]
  HITL -->|tasks| DB
  HITL --> QUEUE[(HITL Queue)]
  U -->|review/approve| QUEUE -->|task results| DB --> ORCH

  ORCH -->|record lineage| PROV[Provenance/Lineage Recorder]
  PROV --> DB
  PROV --> GRAPH[(Audit/Lineage Graph)]

  ORCH -->|final claim set + report| OUT[Exports]
  OUT --> U
