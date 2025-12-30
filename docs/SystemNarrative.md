# SystemNarrative.md
## Governed Patent Intelligence Backend — System Narrative

### Business goal
Generate **new patent claims** grounded in a chosen **open patent specification**, optimized to:
- read on **target products** (e.g., Apple),
- avoid weaknesses exposed by **prior art**, **Office Actions**, and **IPRs**,
- maximize probability of **allowance** and post-grant defensibility,
- preserve **provable lineage** from claim language → supporting disclosures/evidence.

### What the system does end-to-end
The system builds and maintains multiple **corpora** (knowledge sets) and uses them to draft, validate, and refine claim sets with full provenance:

1. **Acquire documents (Research + Manual Upload)**
   - **Research-agent acquisition** (automated):
     - Patent publications, grants, file histories, Office Actions/responses
     - PTAB: IPR petitions, institution decisions, final written decisions
     - Prior art (patents, papers, standards, web pages as approved)
     - **Competitive product documentation** (teardowns, datasheets, marketing pages, manuals, reviews, images)
   - **Manual upload** (human):
     - Any supplemental PDFs, exhibits, screenshots, expert notes, internal analyses

   Each acquired item is registered with `source_type` (e.g., `research_agent`, `manual_upload`) and `doc_type` (e.g., `patent`, `office_action`, `ipr_decision`, `product_doc`, `prior_art`, `claim_drafting_reference`).

2. **Normalize and preserve originals**
   - Store the original artifact (PDF/HTML/XML/images) and normalized forms:
     - normalized text, normalized metadata, structured segments (claims/spec/OA sections), figure assets.

3. **Document processing pipeline (text + image)**
   - **Text extraction first** (native PDF text / XML text).
   - **OCR for images and scanned pages**, including:
     - scanned documents,
     - embedded diagrams/figures in patents,
     - product teardown photos/screenshots.
   - The output is a consistent set of **chunks** ready for retrieval + downstream analysis.

4. **Diagram intelligence (critical)**
   The system treats diagrams as first-class evidence and supports *reuse*:

   **4.1 Figure registry**
   - Every figure is extracted into a canonical “figure object”:
     - `figure_id`, `document_id`, `figure_label` (e.g., “Fig. 1”), page, bounding boxes if available
     - image asset pointer(s)
     - OCR text (if any), plus structured caption text
     - **figure fingerprint** (perceptual hash + metadata) to detect duplicates

   **4.2 Figure description generation**
   - A dedicated step generates a **figure description**:
     - plain-language description of components and relationships,
     - mapping to reference numerals and labels,
     - optional “claim-usable” fragments (noun phrases, functional relationships).
   - Figure descriptions are stored as *structured artifacts* with provenance pointing to the underlying image region and caption.

   **4.3 Figure reuse / dedup**
   - When a new figure is ingested, it is compared against the figure registry:
     - If **identical or near-identical**, the system links it to the prior figure (“same-as”) and reuses the existing description **instead of re-entering**.
     - If partially overlapping, it can inherit components (“derived-from”) with deltas.
   - Reuse is explicit and auditable:
     - “Figure X in Doc B is identical to Figure Y in Doc A (fingerprint match).”
     - The narrative/claim drafting layer may cite the canonical figure description rather than duplicating text.

   **Why it matters**
   - Avoids inconsistent re-descriptions of the same diagram.
   - Reduces HITL effort dramatically over large families / repeated schematic sets.
   - Strengthens defensibility (“this diagram is the same across filings”).

5. **Corpus construction**
   All processed artifacts (text chunks + figure descriptions) populate corpora that remain logically separated but share common tables:
   - **Open Patent Corpus**: the specification that must support new claims (authority).
   - **Adversarial Corpus**: prior art + OA/IPR material used to attack claims.
   - **Product Corpus**: target product evidence used to ensure claim read-on.
   - Optional: **Drafting Guidance Corpus** (treatises, case law, USPTO guidance) if you want RAG grounded in your curated drafting sources.

6. **Retrieval and reasoning (RAG + structured constraints)**
   For any drafting session, the system retrieves:
   - supporting passages from the **Open Patent Corpus**,
   - conflicting or risky passages from the **Adversarial Corpus**,
   - product evidence from the **Product Corpus**,
   - (optional) drafting guidance from curated sources.

   The system does not “just ask the LLM.” It applies:
   - schema-constrained outputs,
   - deterministic step contracts,
   - explicit state transitions,
   - provenance capture at every step.

7. **Claim drafting workflow**
   - **Claim Drafting Agent** produces candidate claim sets grounded in the open patent.
   - **Support/Consistency checks** verify every limitation is supported by citations to the open patent (text and/or figures).
   - **Risk evaluation** scores prior art/OA/IPR vulnerability and flags weak limitations.
   - **Product mapping** checks which limitations read on target products and where evidence is weak.
   - **Revision loop** iterates with constraints and reviewer feedback until accepted.

8. **HITL tasks (when needed)**
   Certain steps generate human tasks:
   - verify OCR of a diagram,
   - confirm figure reuse match,
   - approve figure descriptions,
   - approve a claim set for export.
   HITL is not ad-hoc: it is generated as structured tasks with clear inputs/outputs.

9. **Provenance, lineage, and defensibility**
   Every artifact has a lineage graph:
   - claim sentence → supporting passages/figures → original source doc bytes + extraction method
   - any reuse relationships (figure same-as) are recorded as explicit lineage edges.
   This enables later litigation/prosecution defensibility.

10. **Outputs**
   The system produces:
   - new claim sets (structured + exportable),
   - claim charts / mapping summaries (later phase),
   - risk reports (prior art/OA/IPR),
   - an audit bundle proving how each claim element was derived.

### Where diagram reuse is documented
This behavior is part of the **System Narrative** (this doc) and should also be reflected in:
- **Pipeline & State Machine Spec** (figure registry + reuse steps, failure modes),
- **Provenance/Audit Model** (same-as / derived-from edges),
- **WBS/BuildPlan** (a dedicated work item for figure fingerprinting + reuse logic + HITL confirmation).
