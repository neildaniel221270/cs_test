# Annotated Literature Matrix
**Project:** AI-Powered Micro-Learning System for Machine Maintenance

> **Purpose of this matrix:**  
> This matrix organizes the sources from `Research.md` into a structured overview that can support the literature review and methodology chapters of the project.  
> It is tailored to the project scope: microlearning for technicians, ASR transcription, LLM-based structuring, semantic segmentation, vector retrieval/RAG, and evaluation.

---

## Legend
- **Pipeline fit** = where the paper/resource contributes in your system
- **Priority** = suggested importance for your thesis/report
  - **High** = should likely be cited in core methodology or theoretical framework
  - **Medium** = useful supporting source
  - **Low** = contextual or optional

---

## 1) Microlearning Theory and Industrial Training

| ID | Citation | Type / Context | Method / Design | Key Findings / Contribution | Relevance to This Project | Limitations / Cautions | Pipeline Fit | Priority |
|---|---|---|---|---|---|---|---|---|
| 1 | **Monib, W. K., Qazi, A., & Apong, R. A. (2024).** *Microlearning beyond boundaries: A systematic review and a novel framework for improving learning outcomes.* **Heliyon, 11(2), e41413.** https://doi.org/10.1016/j.heliyon.2024.e41413 | Systematic review of microlearning | PRISMA-based review of 40 studies | Establishes that microlearning can improve cognitive, behavioral, and affective outcomes; provides a framework grounded in Cognitive Load Theory, Bloom’s Taxonomy, and Andragogy | Strong theoretical justification for why **short, targeted maintenance micro-clips** may improve retention and reduce overload for technicians searching for just-in-time support | Review-level evidence; not specific to maintenance videos or retrieval systems; effectiveness depends on implementation quality | Motivation, pedagogical framing | **High** |
| 2 | **Billert, M. S., Weinert, T., Thiel de Gafenco, M., Janson, A., Klusmeyer, J., & Leimeister, J. M. (2022).** *Vocational Training With Microlearning — How Low-Immersive 360-Degree Learning Environments Support Work-Process-Integrated Learning.* **IEEE Transactions on Learning Technologies, 15, 540–553.** https://doi.org/10.1109/TLT.2022.3176777 | Industrial vocational training / work-integrated learning | Design science approach using 360° learning environments for vocational education | Shows that microlearning can be integrated into the flow of work for industrial trainees; especially relevant for procedural/technical tasks | Very relevant to the ASML use case because your system also aims to deliver **work-process-integrated**, just-in-time support rather than long-form classroom training | Focuses on immersive/360° learning rather than searchable transcript-based retrieval; not about ASR or video segmentation | Motivation, industrial training framing | **High** |
| 3 | **Gavish, N., Gutiérrez, T., Webel, S., Rodríguez, J., Peveri, M., Bockholt, U., & Tecchia, F. (2015).** *Evaluating virtual reality and augmented reality training for industrial maintenance and assembly tasks.* **Interactive Learning Environments, 23(6), 778–798.** https://doi.org/10.1080/10494820.2013.815221 | Industrial maintenance training | Empirical evaluation with expert technicians performing assembly/maintenance tasks | Technology-mediated, stepwise procedural guidance can improve maintenance training performance and reduce errors | Supports the broader argument that **digital procedural support** works in maintenance contexts, even though your solution is video retrieval rather than VR/AR | Different modality (VR/AR), so it is indirect evidence; not specific to microlearning clips or transcript retrieval | Motivation, industrial maintenance training evidence | **Medium** |

---

## 2) ASR, Speech Processing, and Transcript Quality

| ID | Citation | Type / Context | Method / Design | Key Findings / Contribution | Relevance to This Project | Limitations / Cautions | Pipeline Fit | Priority |
|---|---|---|---|---|---|---|---|---|
| 4 | **Radford, A., Kim, J. W., Xu, T., Brockman, G., McLeavey, C., & Sutskever, I. (2023).** *Robust Speech Recognition via Large-Scale Weak Supervision.* **ICML 2023 / PMLR 202, 28492–28518.** https://arxiv.org/abs/2212.04356 | Foundational ASR paper (Whisper) | Large-scale weakly supervised training on 680,000 hours of multilingual audio | Whisper achieves strong zero-shot ASR robustness across accents, noise, and domains; provides a solid baseline for transcription | Core citation for using **Whisper as a benchmark ASR baseline** against Azure Speech; supports your transcription and timestamp alignment stages | General-purpose model; not optimized specifically for ASML maintenance vocabulary; factory jargon/part numbers may still challenge performance | ASR baseline, timestamp alignment | **High** |
| 5 | **Srivastav, V., Zheng, S., Bezzam, E., Le Bihan, E., Koluguri, N., Żelasko, P., Majumdar, S., Moumen, A., & Gandhi, S. (2025).** *Open ASR Leaderboard: Towards Reproducible and Transparent Multilingual and Long-Form Speech Recognition Evaluation.* **arXiv:2510.06961** | Benchmarking resource for ASR systems | Comparative evaluation of 60+ ASR systems across multiple datasets | Gives up-to-date benchmarking perspective on Whisper Large-v3 and other ASR systems, useful for model selection and expected performance trade-offs | Useful if you want to justify **why Whisper is a reasonable benchmark** and to discuss reproducible evaluation of WER and long-form speech transcription | Preprint rather than mature peer-reviewed publication; leaderboard findings may evolve rapidly | ASR benchmarking, evaluation design | **Medium** |
| 6 | **Patman, C. & Chodroff, E. (2024).** *Speech recognition in adverse conditions by humans and machines.* **JASA Express Letters, 4, 115204.** https://doi.org/10.1121/10.0032473 | ASR under noisy conditions | Controlled study comparing human listeners, Whisper, and wav2vec 2.0 under noise/mask conditions | Whisper performs competitively in adverse acoustic environments, relevant for recordings with background industrial noise | Important for arguing that maintenance training recordings may still be transcribable even if audio is imperfect | Experimental setting may differ from ASML videos; “adverse conditions” in lab studies do not fully capture real maintenance content complexity | ASR robustness discussion | **Medium** |
| 7 | **Microsoft. (2025).** *What is custom speech? — Speech service.* **Microsoft Learn.** | Official technical documentation | Product/documentation resource rather than empirical study | Describes custom vocabulary/model adaptation, WER evaluation, and deployment options for Azure Speech | Essential practical source for your **primary Azure Speech-to-Text pipeline**, especially because your scope includes domain vocabulary (module names, alarms, part numbers) | Documentation is vendor-oriented and not independent empirical validation; capabilities may differ in practice depending on data and setup | Azure implementation, domain adaptation | **High** |
| 8 | **Laskar, M. T. R., Fu, X.-Y., Chen, C., & TN, S. B. (2023).** *Building Real-World Meeting Summarization Systems using Large Language Models: A Practical Perspective.* **EMNLP 2023 Industry Track, 343–352.** https://doi.org/10.18653/v1/2023.emnlp-industry.33 | LLM processing of long transcripts | Practical evaluation of GPT-4, GPT-3.5, PaLM-2, and LLaMA-2 for transcript summarization | Offers concrete lessons on chunking/chapterization, prompt design, long-context handling, and cost-performance trade-offs | Directly transferable to your **LLM-based transcript structuring** step where GPT-4o converts raw transcripts into procedural segments with titles, steps, tools, and metadata | Meeting transcripts are different from instructional maintenance videos; summarization is not identical to structured extraction | LLM structuring, prompt engineering | **High** |
| 9 | **Alam, T., Khan, A., & Alam, F. (2020).** *Punctuation Restoration using Transformer Models for High- and Low-Resource Languages.* **W-NUT 2020, 132–142.** https://doi.org/10.18653/v1/2020.wnut-1.18 | ASR text post-processing | Transformer-based token classification for punctuation restoration | Demonstrates that punctuation restoration substantially improves transcript readability and downstream NLP usability | Strongly supports your preprocessing stage before LLM structuring; punctuated transcripts should improve segmentation quality and extraction accuracy | Focuses on punctuation only; does not solve speaker ambiguity, domain terminology, or procedural structure by itself | Transcript cleanup, preprocessing | **High** |

---

## 3) Retrieval-Augmented Generation, Embeddings, and Segmentation

| ID | Citation | Type / Context | Method / Design | Key Findings / Contribution | Relevance to This Project | Limitations / Cautions | Pipeline Fit | Priority |
|---|---|---|---|---|---|---|---|---|
| 10 | **Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., Küttler, H., Lewis, M., Yih, W., Rocktäschel, T., Riedel, S., & Kiela, D. (2020).** *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks.* **NeurIPS 2020.** https://arxiv.org/abs/2005.11401 | Foundational RAG paper | Dense retrieval + seq2seq generation over external knowledge | Establishes the RAG paradigm: retrieve relevant knowledge first, then generate grounded outputs | Canonical theoretical basis for your **retrieval layer** and for grounding responses in retrieved transcript segments instead of relying on model memory | Original RAG setup is document-oriented and text-centric; adapting it to clip retrieval and maintenance procedures requires extra design work | RAG architecture, grounding | **High** |
| 11 | **Gao, Y., Xiong, Y., Gao, X., Jia, K., Pan, J., Bi, Y., Dai, Y., Sun, J., Wang, M., & Wang, H. (2024).** *Retrieval-Augmented Generation for Large Language Models: A Survey.* **arXiv:2312.10997** | Survey of RAG methods | Taxonomy and synthesis of Naive, Advanced, and Modular RAG methods | Helps position your system within the broader RAG design space and identify design choices for retrieval, re-ranking, and generation | Useful for the literature review and architecture section when justifying a **hybrid retrieval pipeline** and discussing evaluation considerations | Survey paper; does not itself provide maintenance-specific experiments | RAG design choices, conceptual framing | **High** |
| 12 | **Reimers, N. & Gurevych, I. (2019).** *Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks.* **EMNLP-IJCNLP 2019, 3982–3992.** https://doi.org/10.18653/v1/D19-1410 | Foundational sentence embedding paper | Siamese/triplet network architecture for efficient semantic similarity | Produces semantically meaningful sentence embeddings and drastically reduces pairwise similarity cost | Key citation for using **sentence-transformer embeddings** to index transcript segments and support semantic search/retrieval | Generic semantic similarity training may not perfectly capture procedural boundaries or domain-specific maintenance language | Embeddings, vector retrieval | **High** |
| 13 | **Ghinassi, I., Wang, L., Newell, C., & Purver, M. (2023).** *Comparing Neural Sentence Encoders for Topic Segmentation across Domains: Not Your Typical Text Similarity Task.* **PeerJ Computer Science, 9, e1593.** https://doi.org/10.7717/peerj-cs.1593 | Topic segmentation / encoder comparison | Comparative evaluation of encoders and segmentation approaches across domains | Important finding: encoders that perform well on sentence similarity do **not automatically** perform best on topic segmentation | Very relevant to your **semantic segmentation** stage; supports careful evaluation instead of assuming SBERT embeddings alone will give good segment boundaries | Not specific to maintenance transcripts; may require further domain tuning or heuristics | Topic segmentation, boundary detection | **High** |
| 14 | **Johnson, J., Douze, M., & Jégou, H. (2019).** *Billion-Scale Similarity Search with GPUs.* **IEEE Transactions on Big Data, 7(3), 535–547.** https://doi.org/10.1109/TBDATA.2019.2921572 | Foundational vector search / FAISS paper | GPU-accelerated nearest neighbor search using IVF, PQ, and brute-force variants | Provides the technical basis for scalable dense vector retrieval and efficient similarity search | Directly supports your **FAISS fallback/local development index** and helps justify dense retrieval infrastructure | Focuses on ANN infrastructure rather than task-specific retrieval quality; engineering-oriented rather than instructional retrieval-oriented | Vector store implementation | **Medium** |
| 15 | **Wang, M., Xu, X., Yue, Q., & Wang, Y. (2021).** *A Comprehensive Survey and Experimental Comparison of Graph-Based Approximate Nearest Neighbor Search.* **PVLDB, 14(11), 1964–1978.** https://doi.org/10.14778/3476249.3476255 | ANN methods survey/comparison | Comparative evaluation of 13 graph-based ANN algorithms | Useful for understanding recall/latency/memory trade-offs behind production vector search systems | Helpful for discussing retrieval backend choices and possible trade-offs if system performance matters | Indirectly relevant: focuses on ANN algorithms rather than maintenance clip retrieval effectiveness | Retrieval infrastructure, scalability trade-offs | **Medium** |
| 16 | **Yang, H. & Meinel, C. (2014).** *Content Based Lecture Video Retrieval Using Speech and Video Text Information.* **IEEE Transactions on Learning Technologies, 7(2), 142–154.** https://doi.org/10.1109/TLT.2014.2307305 | Instructional video retrieval | Combines ASR/OCR-derived textual metadata with video segmentation for retrieval | Shows that instructional videos can be indexed and searched using transcript-like text signals at both video and segment level | This is one of the **closest methodological precedents** for your project: retrieve useful pieces of long instructional videos based on text indexing | Older pre-transformer approach; results may not reflect modern transformer embeddings, LLMs, or industrial maintenance complexity | Video retrieval, segment indexing | **High** |

---

## 4) Knowledge Structuring and Maintenance Semantics

| ID | Citation | Type / Context | Method / Design | Key Findings / Contribution | Relevance to This Project | Limitations / Cautions | Pipeline Fit | Priority |
|---|---|---|---|---|---|---|---|---|
| 17 | **van Cauter, Z. & Yakovets, N. (2024).** *Ontology-guided Knowledge Graph Construction from Maintenance Short Texts.* **Proceedings of KaLLM 2024, 75–84.** https://doi.org/10.18653/v1/2024.kallm-1.8 | Maintenance knowledge extraction / structuring | LLM-based triplet extraction with ontology-guided in-context learning | Shows that structured maintenance knowledge can be extracted from short technical texts using ontology-aware prompting with limited examples | Very relevant if you want transcript structuring to output **tools, parts, alarms, steps, safety constraints, prerequisites**, or to later evolve into a lightweight maintenance knowledge graph | Works on short maintenance texts rather than long spoken transcripts; ontology creation effort may be non-trivial | Metadata extraction, structured knowledge | **High** |

---

## 5) Evaluation Methodology

| ID | Citation | Type / Context | Method / Design | Key Findings / Contribution | Relevance to This Project | Limitations / Cautions | Pipeline Fit | Priority |
|---|---|---|---|---|---|---|---|---|
| 18 | **Manning, C. D., Raghavan, P., & Schütze, H. (2008).** *Introduction to Information Retrieval*, Chapter 8: “Evaluation in Information Retrieval.” Cambridge University Press. https://nlp.stanford.edu/IR-book/pdf/08eval.pdf | Canonical IR textbook reference | Theoretical treatment of retrieval metrics and evaluation design | Defines and explains Precision, Recall, F-measure, MAP, NDCG, graded relevance, and test collection methodology | Essential source for justifying your retrieval metrics such as **Precision@5, Recall@10, NDCG@5**, and relevance labeling by SMEs | Textbook source rather than domain-specific experiment; you will still need to adapt metrics to your clip retrieval setting | Retrieval evaluation | **High** |
| 19 | **Morris, A. C., Maier, V., & Green, P. (2004).** *From WER and RIL to MER and WIL: Improved Evaluation Measures for Connected Speech Recognition.* **Interspeech 2004, 2765–2768.** https://doi.org/10.21437/Interspeech.2004-668 | ASR evaluation methodology | Formal analysis of WER and alternative speech evaluation metrics | Gives the standard academic definition of **Word Error Rate** and discusses its limitations | Important for the ASR evaluation section of your project, especially because your scope explicitly sets WER targets | Older evaluation source; useful for metric definition, but not enough for discussing modern long-form ASR benchmarking on its own | ASR evaluation | **High** |

---

# Recommended Core Set for the Thesis/Report

If you want a **smaller “must-cite” core set**, these are the strongest candidates:

1. **Monib et al. (2024)** – theoretical basis for microlearning  
2. **Billert et al. (2022)** – work-integrated vocational microlearning  
3. **Radford et al. (2023)** – Whisper / ASR baseline  
4. **Microsoft Custom Speech (2025)** – Azure implementation and domain adaptation  
5. **Laskar et al. (2023)** – LLM handling of long transcripts  
6. **Alam et al. (2020)** – punctuation restoration before structuring  
7. **Lewis et al. (2020)** – RAG foundation  
8. **Reimers & Gurevych (2019)** – sentence embeddings for retrieval  
9. **Ghinassi et al. (2023)** – topic segmentation caution and encoder selection  
10. **Yang & Meinel (2014)** – transcript-based instructional video retrieval precedent  
11. **van Cauter & Yakovets (2024)** – structured maintenance knowledge extraction  
12. **Manning et al. (2008)** – retrieval metrics  
13. **Morris et al. (2004)** – WER definition and ASR evaluation  

---

# Gap Analysis / What the Current Literature Covers Well

| Area | Coverage Strength | Notes |
|---|---|---|
| Microlearning theory | Strong | Good pedagogical justification for short-form learning in workplace contexts |
| ASR foundation | Strong | Whisper + Azure together give a solid technical basis |
| LLM transcript structuring | Moderate | Good transferable evidence, but not much specifically on maintenance transcripts |
| Semantic retrieval / vector search | Strong | Well covered through SBERT, FAISS, ANN, and RAG literature |
| Topic segmentation | Moderate | Useful but still not maintenance-specific |
| Instructional video retrieval | Moderate | Yang & Meinel is relevant, but somewhat dated |
| Maintenance-specific knowledge structuring | Moderate | van Cauter & Yakovets is promising but still adjacent rather than identical |
| Evaluation metrics | Strong | IR and ASR evaluation are well supported |
| Safety / governance / traceability in maintenance AI | Weak | This appears to be the least-covered area and may require internal policy references or a dedicated governance section |

---

# Suggested Use in Your Report

## For the **Introduction / Problem Framing**
Use:
- Monib et al. (2024)
- Billert et al. (2022)
- Gavish et al. (2015)

## For the **ASR / Data Processing** chapter
Use:
- Radford et al. (2023)
- Patman & Chodroff (2024)
- Microsoft Custom Speech (2025)
- Alam et al. (2020)

## For the **Transcript Structuring / Segmentation** chapter
Use:
- Laskar et al. (2023)
- Reimers & Gurevych (2019)
- Ghinassi et al. (2023)
- van Cauter & Yakovets (2024)

## For the **Retrieval / RAG** chapter
Use:
- Lewis et al. (2020)
- Gao et al. (2024)
- Johnson et al. (2019)
- Wang et al. (2021)
- Yang & Meinel (2014)

## For the **Evaluation** chapter
Use:
- Manning et al. (2008)
- Morris et al. (2004)

---

# One-Sentence Synthesis You Can Reuse

The literature suggests that microlearning is pedagogically well suited to just-in-time technical training, while modern ASR, LLM-based transcript structuring, dense embeddings, and retrieval-augmented generation together provide a feasible technical foundation for transforming long maintenance training videos into searchable, traceable micro-clips; however, domain adaptation, segmentation quality, and governance/safety remain key practical challenges.

``