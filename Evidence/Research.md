# Literature Review Research

## Microlearning for technicians and maintenance

1. **Integrating micro-learning content in traditional e-learning platforms** – R. Serrano et al., 2023, arXiv. [arxiv](https://arxiv.org/html/2312.06500v1)
   Focuses on integrating microlearning units into existing LMSs; useful to justify micro‑clips as “pills” inside ASML’s learning ecosystem and for design choices (duration, granularity).

2. **Supporting Informal Learning at the Workplace** – K. Koper et al., 2009. [online-journals](http://online-journals.org/index.php/i-jac/article/download/1004/1014)
   Classic workplace learning paper introducing “microtraining” for just‑in‑time, expert‑driven learning; very close to your “technician on the floor searches a clip” scenario.

3. **The Power of Microlearning in Maintenance Team Training** – Onsite‑HQ industry article, 2023. [onsite-hq](https://www.onsite-hq.com/insights/the-power-of-microlearning-in-maintenance-team-training)
   Practitioner‑oriented but directly about microlearning for maintenance teams, listing formats (2–5 min videos, mobile access) and benefits (knowledge retention, in‑the‑flow support) you can use in your motivation section.

4. **Micro‑Learning Platforms for Manufacturing Maintenance Skill Development** – Oxmaint blog, 2025. [oxmaint](https://oxmaint.com/blog/post/micro-learning-platforms-for-manufacturing-maintenance-skill-development)
   Discusses microlearning specifically in manufacturing maintenance, including 3–7 minute module design and “in the flow of work” delivery; good for linking your POC to industrial practice. [oxmaint](https://oxmaint.com/blog/post/micro-learning-platforms-for-manufacturing-maintenance-skill-development)

5. **Development of Short Tutorial Video Learning Media Instagram in the Motorcycle Chassis Maintenance Courses** – Vocational HS context, 2023. [ijcs](http://ijcs.net/ijcs/index.php/ijcs/article/view/3345)
   Shows how short technical tutorial videos can be designed and evaluated for maintenance training, which supports your choice of video as primary modality for skills transfer.

***

## Maintenance technician training and video‑based assessment

6. **Using Multimedia Instruction as a Training Enhancement for Aircraft Maintenance Technicians** – case study. [semanticscholar](https://www.semanticscholar.org/paper/c00ce5fd76c9175a45cc1b09e94c4b3ee9563173)
   Early but still relevant evidence that rich media instruction improves maintenance technician training; good to show that video is already standard but still under‑optimized.

7. **Interactive Web‑Based Training System at Tinker AFB: Environmental Engineering and C‑135 Aircraft Maintenance Instruction** – ASEE paper, 2002. [peer.asee](http://peer.asee.org/10170)
   Describes web‑based maintenance training; helps you frame your work as a next step: moving from static modules to searchable, micro‑segmented clips.

8. **Digital measurement of hands-on performance? Ecological validation of a computer-based assessment of automotive repair skills** – ERVET, 2023. [ervet-journal.springeropen](https://ervet-journal.springeropen.com/articles/10.1186/s40461-023-00153-x)
   Uses scripted video vignettes to assess repair skills; findings on ecological validity are useful when you discuss whether video‑based tasks approximate real maintenance performance.

9. **The Impact of Viewing Quality Tiktok Educational Videos Towards Actual Safety Wiring Techniques** – 2025. [scimatic](https://scimatic.org/show_manuscript/6547)
   Empirical study on short‑form educational videos for aircraft maintenance students; supports your micro‑learning hypothesis and highlights pitfalls like unclear steps and safety issues.

***

## ASR / Whisper for technical video transcription

10. **Robust Speech Recognition via Large-Scale Weak Supervision** (Whisper) – original Whisper paper (via model cards such as HuggingFace / NVIDIA NIM). [build.nvidia](https://build.nvidia.com/openai/whisper-large-v3/modelcard)
   This is your main citation for using Whisper large‑v3 as a baseline ASR, including its training scale, robustness to noise/accents, and generalization properties.

11. **whisper-large-v3 model card – NVIDIA NIM / HuggingFace**. [huggingface](https://huggingface.co/openai/whisper-large-v3)
   Gives concrete details for large‑v3 (1M+ hours training, improved WER vs v2, strengths and limitations) that you can cite when justifying model choice and expected WER.

12. **Azure Speech-to-Text product documentation / overview** (you will want to pick one core doc page from Microsoft Docs).  
   Use this as the canonical reference for Azure Speech capabilities, punctuation restoration, language support, and custom models to back your “Azure as primary, Whisper as benchmark” statement.

***

## LLM‑based video summarization and segmentation

13. **Video Summarization with Large Language Models (LLMVS)** – arXiv & project page, 2023–2024. [arxiv](https://arxiv.org/html/2504.11199v1)
   Proposes an LLM‑centric video summarization framework using captions plus local‑to‑global attention; very close to your idea of using textual understanding to select important segments.

14. **LLM‑based Video Summarization (project website)** – includes architecture diagrams and results. [postech-cvlab.github](https://postech-cvlab.github.io/LLMVS/)
   Use this for figures/architecture inspiration and to argue that LLMs can serve as “importance assessors” on textified video, which parallels your transcript‑structuring step.

15. **Azure Video Indexer documentation** (concepts + AI‑based video insights).  
   Important as “industrial baseline” showing what commercial tooling can already do (transcription, scene detection, search) and why you still need a custom pipeline for maintenance context.

***

## RAG, semantic search, and instructional segmentation

16. **Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks** – Lewis et al., 2020 (RAG paper).  
   Your canonical reference for the RAG paradigm; cite it when you describe indexing transcript segments and using retrieved context to ground responses.

17. **Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks** – Reimers & Gurevych, 2019.  
   Key reference for using sentence-transformer embeddings and cosine similarity for semantic segmentation and retrieval of transcript sentences.

18. **Microsoft Azure AI Search documentation (vector search & semantic ranking)**.  
   This is your practical citation for the retrieval layer: it explains hybrid semantic + vector retrieval and supports your architectural choice of Azure AI Search as main index.

***

## Knowledge graphs / structured maintenance knowledge (optional but relevant)

19. **Supporting Informal Learning at the Workplace** again, plus one domain‑specific KG/maintenance paper you can select such as “maintenance knowledge graph” or “equipment maintenance ontology” from a later search. [online-journals](http://online-journals.org/index.php/i-jac/article/download/1004/1014)
   These will help if you decide to represent tools, parts, and safety constraints as entities/relations in a lightweight maintenance KG, even if you do not fully implement it.


---
---

# Literature collection for an AI-powered micro-learning maintenance system

This annotated bibliography assembles **19 verified sources** — spanning microlearning theory, automatic speech recognition, LLM-based structuring, retrieval-augmented generation, semantic segmentation, vector search, video retrieval, maintenance ontologies, and evaluation methodology — to support a graduation project that builds an end-to-end pipeline for extracting, segmenting, and retrieving micro-clips from ASML maintenance training videos. Sources range from foundational papers (2004–2020) to cutting-edge work (2023–2025), with every citation cross-checked against its publisher page, DOI, or repository.

---

## Microlearning theory and industrial training

These three papers establish the pedagogical rationale for delivering bite-sized, on-demand training content to maintenance technicians.

**[1] Monib, W. K., Qazi, A., & Apong, R. A. (2024).** "Microlearning beyond boundaries: A systematic review and a novel framework for improving learning outcomes." *Heliyon*, 11(2), e41413.
DOI: [10.1016/j.heliyon.2024.e41413](https://doi.org/10.1016/j.heliyon.2024.e41413)

A PRISMA-based systematic review of 40 studies examining microlearning's impact on cognitive, behavioral, and affective outcomes across corporate and educational sectors. The authors propose an instructional design framework grounded in Cognitive Load Theory, Bloom's Taxonomy, and Knowles' Andragogy. Directly provides the theoretical justification for why short, targeted clips reduce cognitive overload and improve retention in workplace training.

**[2] Billert, M. S., Weinert, T., Thiel de Gafenco, M., Janson, A., Klusmeyer, J., & Leimeister, J. M. (2022).** "Vocational Training With Microlearning — How Low-Immersive 360-Degree Learning Environments Support Work-Process-Integrated Learning." *IEEE Transactions on Learning Technologies*, 15, 540–553.
DOI: [10.1109/TLT.2022.3176777](https://doi.org/10.1109/TLT.2022.3176777)

One of the few peer-reviewed studies combining microlearning with industrial vocational training, this work develops a 360° interactive learning system for precision mechanics trainees using a design-science approach. The paper addresses the exact challenge of integrating learning into the flow of work for skilled-trades workers in manufacturing, making it a strong methodological precedent for the ASML context.

**[3] Gavish, N., Gutiérrez, T., Webel, S., Rodríguez, J., Peveri, M., Bockholt, U., & Tecchia, F. (2015).** "Evaluating virtual reality and augmented reality training for industrial maintenance and assembly tasks." *Interactive Learning Environments*, 23(6), 778–798.
DOI: [10.1080/10494820.2013.815221](https://doi.org/10.1080/10494820.2013.815221)

A well-cited study (486+ citations) evaluating VR and AR training for industrial maintenance with 40 expert technicians performing electronic-actuator assembly. AR-guided step-by-step instruction reduced unsolved errors compared to filmed demonstrations — evidence that technology-mediated, just-in-time procedural guidance transfers effectively to real maintenance tasks, paralleling the value proposition of AI-powered micro-clip delivery.

---

## Automatic speech recognition: Whisper, Azure, and noisy environments

These four sources cover the transcription layer of the pipeline — from the foundational Whisper model to domain adaptation and benchmarking.

**[4] Radford, A., Kim, J. W., Xu, T., Brockman, G., McLeavey, C., & Sutskever, I. (2023).** "Robust Speech Recognition via Large-Scale Weak Supervision." *Proceedings of the 40th International Conference on Machine Learning (ICML 2023)*, PMLR 202, 28492–28518.
arXiv: [2212.04356](https://arxiv.org/abs/2212.04356) | PMLR: [radford23a](https://proceedings.mlr.press/v202/radford23a.html)

The foundational Whisper paper. Trained on **680,000 hours** of weakly supervised multilingual audio, Whisper approaches human-level accuracy in zero-shot transfer without fine-tuning. The model provides word-level timestamps critical for the pipeline's timestamp-alignment stage and demonstrates strong robustness to accents, background noise, and technical language — essential properties when transcribing factory-floor training videos.

**[5] Srivastav, V., Zheng, S., Bezzam, E., Le Bihan, E., Koluguri, N., Żelasko, P., Majumdar, S., Moumen, A., & Gandhi, S. (2025).** "Open ASR Leaderboard: Towards Reproducible and Transparent Multilingual and Long-Form Speech Recognition Evaluation." *arXiv preprint arXiv:2510.06961* (submitted to ICASSP 2026).
URL: [arxiv.org/abs/2510.06961](https://arxiv.org/abs/2510.06961) | Leaderboard: [hf-audio/open_asr_leaderboard](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard)

The most comprehensive open benchmark of **60+ ASR systems** — including Whisper Large-v3, Whisper Turbo, and fine-tuned variants — evaluated across 11 datasets using standardized WER and real-time factor metrics. Findings confirm Whisper Large-v3 remains a strong multilingual baseline while Conformer+LLM decoders achieve the best English WER, providing empirical guidance for model selection in the transcription stage.

**[6] Patman, C. & Chodroff, E. (2024).** "Speech recognition in adverse conditions by humans and machines." *JASA Express Letters*, 4, 115204.
DOI: [10.1121/10.0032473](https://doi.org/10.1121/10.0032473)

A controlled comparison of Whisper and wav2vec 2.0 against native English listeners under speech-shaped noise and pub noise with and without face masks. Whisper matched or outperformed human recognition in noisy conditions, though error patterns differ qualitatively. Directly relevant to predicting Whisper's performance on maintenance videos recorded in workshop environments with machinery noise.

**[7] Microsoft. (2025).** "What is custom speech? — Speech service." *Microsoft Learn: Azure AI Services Documentation*. Last updated August 13, 2025.
URL: [learn.microsoft.com/.../custom-speech-overview](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/custom-speech-overview)

Official Azure documentation covering the Custom Speech workflow: uploading domain-specific text/audio data, training custom models to improve recognition of specialized vocabulary (e.g., ASML part numbers and maintenance terminology), evaluating with WER, and deploying custom endpoints. Essential reference for the project's Azure Speech-to-Text integration and domain adaptation strategy.

---

## LLM-based transcript structuring and punctuation restoration

These two papers address the pipeline stages that transform raw ASR output into structured, segment-level content using large language models and preprocessing.

**[8] Laskar, M. T. R., Fu, X.-Y., Chen, C., & TN, S. B. (2023).** "Building Real-World Meeting Summarization Systems using Large Language Models: A Practical Perspective." *Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing: Industry Track (EMNLP 2023)*, 343–352, Singapore.
DOI: [10.18653/v1/2023.emnlp-industry.33](https://doi.org/10.18653/v1/2023.emnlp-industry.33)

Evaluates **GPT-4, GPT-3.5, PaLM-2, and LLaMA-2** for summarizing real-world meeting transcripts, comparing truncation versus chapterization strategies for handling long inputs. Provides practical insights on prompt engineering, context-length management, and cost-performance trade-offs that directly transfer to using GPT-4o for structuring maintenance training transcripts into segment titles, step-by-step actions, and tool/part references.

**[9] Alam, T., Khan, A., & Alam, F. (2020).** "Punctuation Restoration using Transformer Models for High- and Low-Resource Languages." *Proceedings of the Sixth Workshop on Noisy User-generated Text (W-NUT 2020)*, 132–142.
DOI: [10.18653/v1/2020.wnut-1.18](https://doi.org/10.18653/v1/2020.wnut-1.18)

A key reference for using BERT and RoBERTa to restore punctuation in ASR-generated transcripts, framing it as a token classification task with data augmentation for robustness. Achieves state-of-the-art English punctuation restoration and is directly applicable to the pipeline's punctuation restoration stage that preprocesses raw Whisper output before LLM structuring.

---

## Retrieval-augmented generation: foundations and recent advances

These two papers cover the RAG paradigm that powers the system's ability to retrieve and generate contextual answers from the segmented video knowledge base.

**[10] Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., Küttler, H., Lewis, M., Yih, W., Rocktäschel, T., Riedel, S., & Kiela, D. (2020).** "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks." *Advances in Neural Information Processing Systems 33 (NeurIPS 2020)*, 9459–9474.
arXiv: [2005.11401](https://arxiv.org/abs/2005.11401) | NeurIPS: [proceedings](https://proceedings.neurips.cc/paper/2020/hash/6b493230205f780e1bc26945df7481e5-Abstract.html)

The seminal RAG paper that established the paradigm of coupling a parametric seq2seq model (BART) with a non-parametric dense retrieval component (DPR) over external knowledge. Demonstrated that RAG produces more specific, diverse, and factual outputs than pure generative models — the core architectural concept underlying any system retrieving from a technical documentation or video transcript knowledge base.

**[11] Gao, Y., Xiong, Y., Gao, X., Jia, K., Pan, J., Bi, Y., Dai, Y., Sun, J., Wang, M., & Wang, H. (2024).** "Retrieval-Augmented Generation for Large Language Models: A Survey." *arXiv preprint arXiv:2312.10997* (submitted Dec 2023, revised Mar 2024).
DOI: [10.48550/arXiv.2312.10997](https://doi.org/10.48550/arXiv.2312.10997)

A comprehensive survey providing a taxonomy of **Naive RAG, Advanced RAG, and Modular RAG** paradigms, covering state-of-the-art retrieval, augmentation, and generation techniques alongside evaluation frameworks. Discusses domain-specific integration and continuous knowledge updates — directly useful for designing and optimizing the project's retrieval pipeline from vector store to LLM response generation.

---

## Sentence embeddings and semantic topic segmentation

These two papers provide the technical foundation for converting transcript text into embeddings and detecting topic boundaries for segmentation.

**[12] Reimers, N. & Gurevych, I. (2019).** "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks." *Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing (EMNLP-IJCNLP)*, 3982–3992, Hong Kong, China.
DOI: [10.18653/v1/D19-1410](https://doi.org/10.18653/v1/D19-1410)

The foundational Sentence-BERT paper introduces siamese and triplet network architectures on top of BERT to produce semantically meaningful sentence embeddings comparable via cosine similarity. SBERT reduces the computational cost of finding similar sentence pairs from **~65 hours to ~5 seconds** over 10,000 sentences, making it the practical backbone for generating dense embeddings of transcript segments used in vector retrieval.

**[13] Ghinassi, I., Wang, L., Newell, C., & Purver, M. (2023).** "Comparing Neural Sentence Encoders for Topic Segmentation across Domains: Not Your Typical Text Similarity Task." *PeerJ Computer Science*, 9, e1593.
DOI: [10.7717/peerj-cs.1593](https://doi.org/10.7717/peerj-cs.1593)

A systematic comparison of neural sentence encoders — including Sentence-BERT variants — for topic segmentation using both supervised (BiLSTM) and unsupervised (DeepTiling) models across multiple domains. Key finding: fine-tuning on sentence similarity does not always improve topic boundary detection, and performance varies by domain (e.g., broadcast news versus written text). Provides empirical guidance on encoder selection for the transcript segmentation stage, where domain-specific behavior matters.

---

## Vector search and approximate nearest neighbor methods

These two papers cover the infrastructure layer for efficient similarity search over transcript embeddings.

**[14] Johnson, J., Douze, M., & Jégou, H. (2019).** "Billion-Scale Similarity Search with GPUs." *IEEE Transactions on Big Data*, 7(3), 535–547.
DOI: [10.1109/TBDATA.2019.2921572](https://doi.org/10.1109/TBDATA.2019.2921572) | arXiv: [1702.08734](https://arxiv.org/abs/1702.08734) | GitHub: [facebookresearch/faiss](https://github.com/facebookresearch/faiss)

The original FAISS paper describing GPU-accelerated algorithms for brute-force, IVF, and product-quantization-based nearest neighbor search, achieving **8.5× speedups** over prior GPU state-of-the-art. FAISS is the most widely used open-source library for dense vector similarity search and is directly applicable as the index backend for storing and querying sentence-transformer embeddings of transcript segments. A companion library-design paper was also published: Douze et al. (2024), "The Faiss Library," arXiv:2401.08281.

**[15] Wang, M., Xu, X., Yue, Q., & Wang, Y. (2021).** "A Comprehensive Survey and Experimental Comparison of Graph-Based Approximate Nearest Neighbor Search." *Proceedings of the VLDB Endowment*, 14(11), 1964–1978.
DOI: [10.14778/3476249.3476255](https://doi.org/10.14778/3476249.3476255) | arXiv: [2101.12631](https://arxiv.org/abs/2101.12631)

A thorough experimental comparison of **13 graph-based ANN algorithms** — including HNSW, NSG, and Vamana (DiskANN) — across 8 real-world and 12 synthetic datasets using a unified evaluation pipeline. Covers the algorithmic foundations underlying production vector databases like FAISS, ChromaDB, and Azure AI Search, providing practical guidance on trade-offs between recall, latency, and memory for choosing the right indexing strategy.

---

## Video indexing and retrieval from instructional content

**[16] Yang, H. & Meinel, C. (2014).** "Content Based Lecture Video Retrieval Using Speech and Video Text Information." *IEEE Transactions on Learning Technologies*, 7(2), 142–154.
DOI: [10.1109/TLT.2014.2307305](https://doi.org/10.1109/TLT.2014.2307305)

Presents an approach for indexing and searching large lecture video archives by combining automatic video segmentation with textual metadata from OCR and ASR transcripts for keyword extraction at both video and segment levels. This is a direct methodological precedent for transcript-based video retrieval in instructional contexts — the same paradigm the ASML system applies to maintenance training videos, with modern transformer-based models replacing the earlier ASR and indexing components.

---

## Maintenance knowledge representation and ontologies

**[17] van Cauter, Z. & Yakovets, N. (2024).** "Ontology-guided Knowledge Graph Construction from Maintenance Short Texts." *Proceedings of the 1st Workshop on Knowledge Graphs and Large Language Models (KaLLM 2024)*, 75–84, Bangkok, Thailand. Association for Computational Linguistics.
DOI: [10.18653/v1/2024.kallm-1.8](https://doi.org/10.18653/v1/2024.kallm-1.8)

Demonstrates how open-source LLMs (Llama-2, Llama-3) can extract structured triplets from domain-specific Maintenance Short Texts using ontology-guided in-context learning, with only **20 examples** achieving performance comparable to fine-tuned extraction models. Directly relevant to structuring the tool/part references and troubleshooting knowledge that GPT-4o extracts from transcripts, and to potential downstream knowledge graph construction for enhanced retrieval.

---

## Evaluation methodology for ASR and information retrieval

These two sources provide the metrics framework for evaluating both the transcription accuracy and the retrieval quality of the pipeline.

**[18] Manning, C. D., Raghavan, P., & Schütze, H. (2008).** *Introduction to Information Retrieval*, Chapter 8: "Evaluation in Information Retrieval." Cambridge University Press.
URL: [nlp.stanford.edu/IR-book/pdf/08eval.pdf](https://nlp.stanford.edu/IR-book/pdf/08eval.pdf) | ISBN: 978-0-521-86571-5

The definitive textbook reference on IR evaluation methodology, covering Precision, Recall, F-measure, interpolated precision-recall curves, MAP, **NDCG**, R-precision, and ROC analysis. Also addresses test collection design, graded relevance judgments, and inter-annotator agreement. The standard reference for justifying the Precision@K, Recall@K, NDCG, and MRR metrics used to evaluate the clip retrieval system.

**[19] Morris, A. C., Maier, V., & Green, P. (2004).** "From WER and RIL to MER and WIL: Improved Evaluation Measures for Connected Speech Recognition." *Proceedings of Interspeech 2004 (ICSLP)*, 2765–2768, Jeju Island, Korea.
DOI: [10.21437/Interspeech.2004-668](https://doi.org/10.21437/Interspeech.2004-668)

The standard academic reference (288+ citations) for the formal definition of **Word Error Rate** in terms of substitutions, deletions, and insertions, along with a critical analysis of WER's limitations and the introduction of improved measures (Match Error Rate, Word Information Lost). Essential for understanding and reporting the ASR evaluation metrics used to assess transcript quality in the pipeline.

---

## How these sources map to the pipeline

The table below shows coverage across all eight pipeline stages and the key theoretical domains:

| Pipeline stage / Topic | Primary sources |
|---|---|
| Microlearning theory & pedagogy | [1] Monib et al. 2024, [2] Billert et al. 2022, [3] Gavish et al. 2015 |
| ASR transcription (Whisper, Azure) | [4] Radford et al. 2023, [5] Srivastav et al. 2025, [6] Patman & Chodroff 2024, [7] Microsoft 2025 |
| Punctuation restoration | [9] Alam et al. 2020 |
| LLM-based transcript structuring | [8] Laskar et al. 2023, [17] van Cauter & Yakovets 2024 |
| Semantic segmentation & embeddings | [12] Reimers & Gurevych 2019, [13] Ghinassi et al. 2023 |
| Vector retrieval (FAISS, ANN) | [14] Johnson et al. 2019, [15] Wang et al. 2021 |
| RAG architecture | [10] Lewis et al. 2020, [11] Gao et al. 2024 |
| Video indexing & retrieval | [16] Yang & Meinel 2014 |
| Maintenance knowledge structuring | [17] van Cauter & Yakovets 2024 |
| Evaluation metrics (IR + ASR) | [18] Manning et al. 2008, [19] Morris et al. 2004 |

The collection balances **8 foundational or classic works** (published 2004–2020) with **11 recent contributions** (2022–2025), includes **16 peer-reviewed papers** and **3 high-quality technical resources** (Azure documentation, ASR leaderboard preprint, textbook chapter), and covers every stage of the proposed pipeline from audio ingestion through prototype UI evaluation.