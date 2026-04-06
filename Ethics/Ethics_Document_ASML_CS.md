# Ethical, Legal, and Organizational Considerations (Revised)

## Project Context and Scope

This document describes the ethical, legal, and organizational considerations for the graduation project: **an AI-powered micro-learning system that retrieves and assembles short (1–2 minute) troubleshooting micro-clips from existing ASML training videos**, enabling technicians to quickly view the exact steps needed to resolve specific machine issues.   
Unlike training *participation* analytics (e.g., completion dashboards), this project focuses on **processing training video content** (and derived transcripts/metadata) to support **just-in-time troubleshooting guidance**.

**Key project design choices (as constraints):**
- **Anonymous by default:** the prototype does not require technician identity; it is designed to work without collecting user identifiers. 
- **Machine-only footage:** source videos are expected to show machines/tools rather than people; however, occasional on-screen prompts (e.g., “scan badge”) may appear and are treated carefully as potentially privacy-relevant context. 
- **Reuse, not generation:** the system extracts and assembles clips from existing footage rather than generating new procedural content, reducing hallucination risk but not eliminating retrieval/assembly risk. 
---

## GDPR and Data Privacy

### Regulatory Context
ASML operates under the EU General Data Protection Regulation (GDPR), which applies broadly to processing of personal data linked to identifiable individuals. 
While this project targets machine-only training footage, **personal data can still appear** in enterprise video corpora (e.g., names spoken in audio, names in overlays, voice if any narration is identifiable, or badge-related prompts). Therefore, the project adopts GDPR principles including lawfulness, fairness, transparency, data minimization, purpose limitation, and security. 

### Data Types and Processing Activities
The prototype may process the following categories:
- **Raw training videos** (confidential internal assets). 
- **Derived transcripts** (ASR output) and structured representations (LLM summaries/step candidates). 
- **Indexing artifacts** such as embeddings, segment metadata (timestamps, tags), and retrieval logs. 
- **User queries** (problem descriptions/error codes). By design, these are handled **without user identity** and stored only if necessary for debugging/evaluation, preferably in aggregated form. 

### Data Minimization
GDPR’s data minimization principle requires limiting data to what is necessary for the stated purpose. 
Accordingly:
- Retrieval is designed to rely primarily on **segment-level metadata** (timestamps + transcript snippets + tags) rather than duplicating entire videos. 
- The system extracts only the **minimum segment duration** required to form a coherent 1–2 minute micro-clip. 
- User interaction is **anonymous by default**; no employee identifiers are required to search and view clips in the prototype. 

### Purpose Limitation and Lawful Basis
The purpose is restricted to **maintenance learning support and troubleshooting guidance** by surfacing relevant segments from approved training materials.   
The system is **not** used for employee monitoring, performance evaluation, disciplinary actions, or any secondary purpose unrelated to learning support. This mirrors the broader ethical stance in the original ethics approach that analytics should not be repurposed for employment decisions. 

### Security, Access Control, and Confidentiality
Training videos and derived artifacts can contain **confidential operational know-how** even when they contain no personal data. Therefore, access is restricted through role-based access control (RBAC), encryption in transit and at rest, and logging/audit practices consistent with organizational accountability expectations.  
- **RBAC:** only authorized technicians/SMEs/safety reviewers and system maintainers can access the platform.
- **Encryption:** TLS in transit; encryption at rest for stores that contain transcripts/metadata.
- **Auditability:** access to clip creation/export is logged and reviewable.

### Retention and Deletion
Retention is defined separately for:
- **Raw video assets:** follow ASML’s established content retention policies (not duplicated unnecessarily). 
- **Derived data (transcripts, embeddings, indices):** retained only as long as needed for the prototype and evaluation; deleted/rotated after the project unless explicitly approved for continuation. 

---

## Safety, Human Factors, and Harm Prevention

### Safety-Critical Nature of Outputs
Even though the system reuses existing training footage, incorrect retrieval, missing prerequisites, or outdated procedures can cause unsafe maintenance actions. The system is therefore treated as **safety-relevant decision support** rather than an autonomous instructor. 

### Safety Controls (Design Requirements)
- **SOP-first framing:** the UI and clip metadata explicitly reference that official procedures/SOPs govern the work; clips are supportive, not authoritative. 
- **Provenance display:** every micro-clip provides source video ID/title and timestamps so users can verify context. 
- **Version and recency cues:** clips surface the source video date/version tags where available to reduce outdated guidance risk. 
- **No automatic actioning:** the system does not auto-trigger maintenance actions or communications; it only surfaces content to humans. This aligns with the original ethics emphasis on analytics as decision support and the importance of oversight. 

### Human Oversight and Approval Workflow
To reduce risk, outputs are categorized:
- **Unreviewed (prototype):** generated micro-clips for experimentation and internal evaluation.
- **Reviewed/Approved:** clips that have been validated by SMEs and, where applicable, safety reviewers before being promoted for broader use.

This operationalizes the “human oversight” principle emphasized in the original ethics document’s governance approach. 

### Incident Handling
A feedback mechanism enables SMEs/technicians to flag issues (wrong segment, missing step, outdated content). Reports are logged, investigated, and lead to corrective actions (re-tagging, re-indexing, removing clips, or adding warnings). 

---

## Bias, Robustness, and Quality Risks (Project-Relevant)

### Primary Sources of Bias
Bias risks in this project differ from training participation analytics. Key risks include:
- **ASR performance variance:** accents, noise, domain jargon, and audio quality can lead to transcript errors, making some content harder to retrieve. 
- **Coverage bias:** common procedures may be overrepresented in the corpus; rare faults may have fewer examples, reducing retrieval quality. 
- **Recency/version bias:** older training videos may be superseded; retrieval must avoid recommending outdated procedures without warning. 

### Mitigation Strategies
- **Domain vocabulary support:** incorporate component names, error codes, and procedure terms into indexing and evaluation sets. 
- **Stratified evaluation:** evaluate retrieval across different categories (procedure type, machine module, audio quality conditions) rather than relying on a single aggregate score. 
- **Version-aware ranking:** prefer newer/approved procedures when multiple matches exist; warn when only older matches are available. 

### Residual Risks
Some procedures may remain hard to retrieve due to poor audio or missing metadata. These limitations are documented and exposed via uncertainty/provenance cues to discourage over-trust. 

---

## Transparency and Explainability

### Provenance-First Transparency
Transparency is delivered through **traceability** rather than opaque “AI answers.” Each result includes:
- Source video reference and exact timestamps
- Tags/labels used for retrieval (error code, component, step)
- Indicators of review status (unreviewed vs approved)

This replaces KPI-style transparency used in analytics dashboards with content provenance suitable for maintenance guidance. 

### “Why this clip?” Explanations
The UI provides short explanations of retrieval rationale (e.g., matched error code + component phrase in transcript; matched metadata tag). Where confidence is low, the system signals uncertainty and suggests broader alternatives (e.g., longer context clip or related procedures). 

---

## Organizational Governance and Accountability

### Roles and Responsibilities
- **Content owners/SMEs:** validate procedure correctness and completeness.
- **Safety reviewers:** validate safety-critical steps and required warnings.
- **Platform maintainers:** enforce access controls, logging, and retention rules.

This aligns with the original ethics document’s emphasis on governance structures, periodic reviews, and accountability.

### Auditability and Change Management
Changes to indexing, retrieval logic, or clip assembly rules are recorded (what changed, when, why). If a clip is removed or superseded, the reason is documented. 

---

## Intellectual Property (IP) and Confidential Information

Training videos, transcripts, and derived embeddings may encode proprietary know-how. Therefore:
- The system is intended for **internal use in approved environments**.
- External demos use **sanitized or synthetic examples** when necessary.
- Export/download is restricted by default, and any sharing follows ASML policy.

This complements GDPR security with organizational confidentiality requirements relevant to maintenance knowledge. 

---

## Summary of Commitments

1. **Anonymous by default** interaction: no technician identifiers required for core functionality. 
2. **Minimize data**: prefer segment-level indices, avoid duplicating raw videos, retain derived artifacts only as needed. 
3. **Safety-first governance**: human review for safety-critical clips; clear provenance and SOP-first messaging. 
4. **Transparency through provenance**: show source video and timestamps and explain retrieval rationale. 
5. **Accountability**: logging, incident reporting, and change management for continuous improvement. 

---

## References (starting set)

The revised ethics approach builds on the regulatory and governance framing already used in the prior ethics document (GDPR, transparency, human oversight, and governance mechanisms). 

- European Parliament & Council of the European Union. (2016). Regulation (EU) 2016/679 (General Data Protection Regulation). 
- European Parliament & Council of the European Union. (2024). Regulation (EU) 2024/1689 (Artificial Intelligence Act). 
- National Institute of Standards and Technology. (2023). AI Risk Management Framework (AI RMF 1.0). 
- International Organization for Standardization. (2023). ISO/IEC 42001:2023.