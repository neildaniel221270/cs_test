Title
Abstract
Acknowledgements
Declaration of GenAI and AI-assisted technologies in the writing, planning, and coding process

1. Introduction
   
   1.1 Background and Context
   
   1.2 Problem Statement
   
   1.3 Objectives
   
   1.4 Research Question and Sub-questions
   
   1.5 Scope of the Project
   
   1.6 Thesis Outline

2. Literature Review
   
   
   2.1 Key Concepts and Theories
   
   2.2 Existing Work
   
   2.3 Gaps in Research

3. Methodology
   
   3.1 Research Design
   
   3.2 Data and Materials
   
   3.3 System Pipeline / Technical Approach
   
   3.4 Tools and Platforms
   
   3.5 Evaluation Methodology
   
   3.6 Constraints, Assumptions, Ethics, and Safety

4. Results and Discussion
   
   4.1 Results
   
   4.2 Discussion
   
   4.3 Comparison with Existing Work
   
   4.4 Strengths and Limitations

5. Conclusion
   
   5.1 Key Findings
   
   5.2 Answer to the Research Question
   
   5.3 Future Work
   
   5.4 Final Remarks

References
Appendices

---

# 1. Introduction

## 1.1 Background and Context

Industrial maintenance work depends heavily on accurate procedural knowledge, yet this knowledge is often embedded in long-form training videos that are not designed for rapid, just-in-time retrieval during troubleshooting or refresher learning. In the current project context, maintenance technicians must manually search through lengthy video material to locate the few steps that are relevant to a specific problem, symptom, error code, or maintenance task. This creates friction in the learning process and reduces the practical usefulness of existing training assets for time-sensitive service scenarios. [1](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/_layouts/15/Doc.aspx?sourcedoc=%7BDAA992C8-1301-4F13-9F64-AA3E79CC8408%7D&file=Project_Scope_v3.docx&action=default&mobileredirect=true)

From a learning perspective, this challenge aligns well with the rationale for microlearning. The literature shows that short, targeted learning units can reduce cognitive overload and support work-integrated learning, particularly for vocational and technical environments where learners need concise, task-oriented support rather than long classroom-style instruction. In industrial settings, technology-mediated procedural guidance has also been shown to improve performance and reduce errors, suggesting that maintenance learning benefits from accessible, stepwise, context-specific content delivery. [2](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/Documents/Microsoft%20Copilot%20Chat%20Files/Literature_review.md)

Recent developments in artificial intelligence create an opportunity to transform long training videos into searchable micro-learning assets. Automatic speech recognition (ASR) can convert spoken content into text, large language models (LLMs) can structure transcripts into procedural segments with metadata, and retrieval-augmented approaches can support semantic search over those segments. Combined with timestamp alignment, such a pipeline can enable clip-level retrieval, where a user’s query returns a relevant portion of the original video rather than an entire long recording. The project therefore sits at the intersection of microlearning, instructional video retrieval, maintenance knowledge structuring, and applied AI. [1](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/_layouts/15/Doc.aspx?sourcedoc=%7BDAA992C8-1301-4F13-9F64-AA3E79CC8408%7D&file=Project_Scope_v3.docx&action=default&mobileredirect=true)[2](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/Documents/Microsoft%20Copilot%20Chat%20Files/Literature_review.md)

## 1.2 Problem Statement

ASML’s machine maintenance technicians currently rely on lengthy customer support and training videos to find troubleshooting guidance. Locating the specific procedural steps required for a particular maintenance issue involves manually scrubbing through long-form content, which is time-consuming, inefficient, and error-prone. At present, no system automatically extracts, structures, and retrieves the most relevant video segments from ASML’s proprietary training library based on practical service-oriented inputs such as symptoms, tool or module names, task intent, and alarm or error codes. [1](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/_layouts/15/Doc.aspx?sourcedoc=%7BDAA992C8-1301-4F13-9F64-AA3E79CC8408%7D&file=Project_Scope_v3.docx&action=default&mobileredirect=true)

The problem is not merely one of information access, but of information granularity, traceability, and safe use. Existing long-form videos are too coarse-grained for just-in-time support, while any AI-based retrieval system in a maintenance domain must ensure that retrieved content remains traceable to the original source and is presented with appropriate context, disclaimers, and safety metadata. The challenge is therefore to move from unstructured long video content to short, semantically meaningful, clip-level learning units without compromising technical fidelity or user safety. [1](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/_layouts/15/Doc.aspx?sourcedoc=%7BDAA992C8-1301-4F13-9F64-AA3E79CC8408%7D&file=Project_Scope_v3.docx&action=default&mobileredirect=true)[2](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/Documents/Microsoft%20Copilot%20Chat%20Files/Literature_review.md)

## 1.3 Objectives

The main objective of this thesis is to design and evaluate an AI-powered micro-learning pipeline that converts long maintenance training videos into searchable, traceable, and context-aware micro-clips for technician learning support. [1](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/_layouts/15/Doc.aspx?sourcedoc=%7BDAA992C8-1301-4F13-9F64-AA3E79CC8408%7D&file=Project_Scope_v3.docx&action=default&mobileredirect=true)

More specifically, the project has the following objectives:

1. To transcribe proprietary maintenance training videos using ASR and assess transcription quality for technical, domain-specific spoken content. [1](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/_layouts/15/Doc.aspx?sourcedoc=%7BDAA992C8-1301-4F13-9F64-AA3E79CC8408%7D&file=Project_Scope_v3.docx&action=default&mobileredirect=true)[2](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/Documents/Microsoft%20Copilot%20Chat%20Files/Literature_review.md)
2. To structure raw transcripts into customer-support-relevant procedural segments using LLM-based processing, including titles, steps, prerequisites, tools or parts, and safety-related metadata. [1](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/_layouts/15/Doc.aspx?sourcedoc=%7BDAA992C8-1301-4F13-9F64-AA3E79CC8408%7D&file=Project_Scope_v3.docx&action=default&mobileredirect=true)[2](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/Documents/Microsoft%20Copilot%20Chat%20Files/Literature_review.md)
3. To align structured transcript segments with source-video timestamps so that precise micro-clips can be extracted from the original recordings. [1](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/_layouts/15/Doc.aspx?sourcedoc=%7BDAA992C8-1301-4F13-9F64-AA3E79CC8408%7D&file=Project_Scope_v3.docx&action=default&mobileredirect=true)
4. To build and test a retrieval system that can identify and rank relevant video segments using realistic maintenance-oriented queries such as symptom descriptions, alarm codes, module names, and task intents. [1](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/_layouts/15/Doc.aspx?sourcedoc=%7BDAA992C8-1301-4F13-9F64-AA3E79CC8408%7D&file=Project_Scope_v3.docx&action=default&mobileredirect=true)[2](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/Documents/Microsoft%20Copilot%20Chat%20Files/Literature_review.md)
5. To evaluate the proposed pipeline using both ASR and information retrieval metrics, supported by expert-labelled ground truth and practical quality targets. [1](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/_layouts/15/Doc.aspx?sourcedoc=%7BDAA992C8-1301-4F13-9F64-AA3E79CC8408%7D&file=Project_Scope_v3.docx&action=default&mobileredirect=true)[2](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/Documents/Microsoft%20Copilot%20Chat%20Files/Literature_review.md)
6. To ensure that retrieved content is presented with traceability, governance, and safety considerations so that it supports learning without being mistaken for authoritative service instructions. [1](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/_layouts/15/Doc.aspx?sourcedoc=%7BDAA992C8-1301-4F13-9F64-AA3E79CC8408%7D&file=Project_Scope_v3.docx&action=default&mobileredirect=true)

## 1.4 Research Question and Sub-questions

The central research question of this thesis is:

**How can ASR, LLM-based transcript structuring, and retrieval-augmented generation be combined to automatically extract, segment, and retrieve relevant micro-clips from ASML Customer Support training videos, based on service tasks, symptoms, and alarm/error codes, with measurable retrieval quality, traceability to the source, and safe/appropriate presentation?** [1](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/_layouts/15/Doc.aspx?sourcedoc=%7BDAA992C8-1301-4F13-9F64-AA3E79CC8408%7D&file=Project_Scope_v3.docx&action=default&mobileredirect=true)

To answer this question, the project addresses the following sub-questions:

- **SQ1:** How accurately can ASR transcribe ASML customer support training videos, and how effectively can LLMs structure the transcripts into customer-support-relevant procedural segments? [1](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/_layouts/15/Doc.aspx?sourcedoc=%7BDAA992C8-1301-4F13-9F64-AA3E79CC8408%7D&file=Project_Scope_v3.docx&action=default&mobileredirect=true)
- **SQ2:** How precisely can transcript segments be aligned with video timestamps to enable clip-level extraction? [1](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/_layouts/15/Doc.aspx?sourcedoc=%7BDAA992C8-1301-4F13-9F64-AA3E79CC8408%7D&file=Project_Scope_v3.docx&action=default&mobileredirect=true)
- **SQ3:** How well can a retrieval system identify and rank relevant video segments for typical customer-support inputs such as symptom descriptions, error codes, tool or module names, and maintenance tasks? [1](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/_layouts/15/Doc.aspx?sourcedoc=%7BDAA992C8-1301-4F13-9F64-AA3E79CC8408%7D&file=Project_Scope_v3.docx&action=default&mobileredirect=true)
- **SQ4:** What governance, safety, and traceability metadata are required so that retrieved clips can support learning without being interpreted as official or authoritative service instructions? [1](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/_layouts/15/Doc.aspx?sourcedoc=%7BDAA992C8-1301-4F13-9F64-AA3E79CC8408%7D&file=Project_Scope_v3.docx&action=default&mobileredirect=true)

## 1.5 Scope of the Project

This project focuses on the design and proof-of-concept implementation of a pipeline for AI-powered micro-learning based on existing ASML training videos. The core in-scope elements are ASR transcription, transcript clean-up and structuring, semantic segmentation, timestamp alignment, vector-based retrieval, an evaluation framework, and a proof-of-concept micro-clip assembly step using programmatic extraction from the original videos. The primary implementation environment is the Microsoft Azure ecosystem, with selected open-source tools used for benchmarking or local development. [1](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/_layouts/15/Doc.aspx?sourcedoc=%7BDAA992C8-1301-4F13-9F64-AA3E79CC8408%7D&file=Project_Scope_v3.docx&action=default&mobileredirect=true)

The project is explicitly limited to a prototype and does not aim to deliver a production-ready system. Real-time deployment, integration with live machine diagnostics or customer log feeds, controlled field studies at customer sites, automated compliance validation, and the generation of entirely new synthetic training videos are outside the scope. Likewise, the system does not replace or modify official service documentation; it only surfaces existing training content with traceability to the source. Multimodal visual grounding is considered only as a possible future direction if text-based methods prove insufficient. [1](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/_layouts/15/Doc.aspx?sourcedoc=%7BDAA992C8-1301-4F13-9F64-AA3E79CC8408%7D&file=Project_Scope_v3.docx&action=default&mobileredirect=true)

This scope is consistent with the literature, which provides strong support for microlearning, transcript-based retrieval, ASR, semantic search, and evaluation methods, but shows weaker coverage on safety, governance, and traceability in maintenance AI systems. As a result, these latter aspects form an important practical contribution of the project. [2](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/Documents/Microsoft%20Copilot%20Chat%20Files/Literature_review.md)

## 1.6 Thesis Outline

This thesis is structured as follows. Chapter 1 introduces the background, problem context, objectives, research questions, and project scope. Chapter 2 reviews the relevant literature on microlearning, industrial training, automatic speech recognition, transcript structuring, semantic segmentation, retrieval-augmented generation, and evaluation methodology. Chapter 3 presents the research methodology, including the system design, data and materials, technical pipeline, tools and platforms, evaluation approach, and ethical and safety considerations. Subsequent chapters can then describe implementation, results, discussion, and conclusions based on the developed prototype and its evaluation. [1](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/_layouts/15/Doc.aspx?sourcedoc=%7BDAA992C8-1301-4F13-9F64-AA3E79CC8408%7D&file=Project_Scope_v3.docx&action=default&mobileredirect=true)[2](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/Documents/Microsoft%20Copilot%20Chat%20Files/Literature_review.md)


# 2. Literature Review

## 2.1 Key Concepts and Theories

### Microlearning in technical and industrial contexts

Microlearning refers to the delivery of learning content in short, focused units that are designed to support specific learning goals with minimal cognitive overload. In the context of technical and vocational learning, the literature suggests that microlearning can improve cognitive, behavioural, and affective learning outcomes when appropriately designed. It is especially relevant for work-integrated settings in which learners need quick access to procedural knowledge rather than broad conceptual overviews. This theoretical framing is supported by links to Cognitive Load Theory, Bloom’s Taxonomy, and andragogical principles, all of which are highly relevant to maintenance technicians seeking just-in-time support. [2](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/Documents/Microsoft%20Copilot%20Chat%20Files/Literature_review.md)

For industrial environments, the value of microlearning lies in its practical fit with work processes. Studies in vocational and maintenance training indicate that technology-mediated procedural support can improve training effectiveness, reduce errors, and better align learning with operational tasks. Although some prior studies focus on immersive environments such as VR and 360-degree learning rather than searchable videos, they still reinforce the broader principle that short, task-specific, digital guidance can be valuable in industrial maintenance contexts. [2](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/Documents/Microsoft%20Copilot%20Chat%20Files/Literature_review.md)

### ASR, transcript quality, and preprocessing

Automatic speech recognition forms the first technical foundation of the proposed system. The literature identifies Whisper as a strong baseline for robust long-form speech transcription, particularly under varied recording conditions, while Microsoft’s Custom Speech capabilities offer practical options for domain adaptation in Azure-based pipelines. Since maintenance videos may contain specialist vocabulary such as tool names, module identifiers, alarms, and part numbers, domain adaptation and vocabulary handling are especially important. [1](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/_layouts/15/Doc.aspx?sourcedoc=%7BDAA992C8-1301-4F13-9F64-AA3E79CC8408%7D&file=Project_Scope_v3.docx&action=default&mobileredirect=true)[2](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/Documents/Microsoft%20Copilot%20Chat%20Files/Literature_review.md)

Transcript quality is not only about raw recognition accuracy but also about downstream usability. Punctuation restoration and transcript cleaning are important preprocessing steps because they improve readability and make subsequent segmentation and structured extraction more reliable. For this reason, ASR in this project is not treated as a standalone output but as the entry point to a larger knowledge-processing pipeline. [1](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/_layouts/15/Doc.aspx?sourcedoc=%7BDAA992C8-1301-4F13-9F64-AA3E79CC8408%7D&file=Project_Scope_v3.docx&action=default&mobileredirect=true)[2](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/Documents/Microsoft%20Copilot%20Chat%20Files/Literature_review.md)

### LLM-based transcript structuring and knowledge extraction

Long instructional transcripts are difficult to use directly for retrieval. The literature therefore highlights the importance of LLM-based processing for chunking, chapterization, structured extraction, and summarization of long-form speech. These methods are highly relevant to this project because the goal is not simply to summarize a video, but to transform raw transcripts into procedural units containing titles, ordered steps, prerequisites, tools or parts, and safety-related metadata. [1](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/_layouts/15/Doc.aspx?sourcedoc=%7BDAA992C8-1301-4F13-9F64-AA3E79CC8408%7D&file=Project_Scope_v3.docx&action=default&mobileredirect=true)[2](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/Documents/Microsoft%20Copilot%20Chat%20Files/Literature_review.md)

In maintenance-oriented contexts, emerging work on ontology-guided extraction and structured knowledge generation suggests that technical texts can be transformed into more formalized representations, such as relations between actions, components, faults, and constraints. While these approaches are not identical to long-form spoken-video processing, they provide an important conceptual basis for viewing transcript structuring as a form of maintenance knowledge extraction rather than simple text summarization. [2](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/Documents/Microsoft%20Copilot%20Chat%20Files/Literature_review.md)

### Semantic segmentation, embeddings, and retrieval-augmented generation

The retrieval component of the project draws on literature from dense retrieval, sentence embeddings, and retrieval-augmented generation (RAG). Sentence-BERT and related embedding methods are widely used to represent text segments in vector space so that semantically similar content can be retrieved even when the query wording differs from the original transcript wording. This is especially useful in maintenance scenarios, where technicians may search by symptom or alarm code rather than by the exact phrasing used in training videos. [1](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/_layouts/15/Doc.aspx?sourcedoc=%7BDAA992C8-1301-4F13-9F64-AA3E79CC8408%7D&file=Project_Scope_v3.docx&action=default&mobileredirect=true)[2](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/Documents/Microsoft%20Copilot%20Chat%20Files/Literature_review.md)

At the same time, the literature warns that models that perform well on sentence similarity do not necessarily perform equally well on topic segmentation. This is important because the project depends not only on semantic retrieval but also on the identification of meaningful segment boundaries that correspond to procedural steps. The RAG literature further supports the principle of grounding responses in retrieved source material, which is particularly relevant in technical environments where hallucinated guidance could be problematic. [2](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/Documents/Microsoft%20Copilot%20Chat%20Files/Literature_review.md)

### Retrieval evaluation and system quality

The literature on information retrieval provides a mature framework for evaluating ranking quality using metrics such as Precision@k, Recall@k, and NDCG. Likewise, speech recognition literature provides standard definitions and interpretations for Word Error Rate (WER) and related ASR quality measures. These frameworks are directly applicable to the present project, which defines success in terms of both transcription quality and retrieval performance rather than relying on anecdotal system demonstrations. [1](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/_layouts/15/Doc.aspx?sourcedoc=%7BDAA992C8-1301-4F13-9F64-AA3E79CC8408%7D&file=Project_Scope_v3.docx&action=default&mobileredirect=true)[2](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/Documents/Microsoft%20Copilot%20Chat%20Files/Literature_review.md)

## 2.2 Existing Work

The existing literature offers strong support for several parts of the proposed pipeline, although most contributions address individual components rather than the full end-to-end problem. First, the pedagogical justification for microlearning is well established. Systematic review evidence and vocational training studies indicate that short, focused learning units can improve learning outcomes and integrate effectively into work processes. This supports the idea of transforming long maintenance videos into smaller, targeted clips that are easier to consume during task preparation or troubleshooting. [2](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/Documents/Microsoft%20Copilot%20Chat%20Files/Literature_review.md)

Second, transcript generation and preprocessing are well supported by current ASR research and tooling. Whisper provides a credible open benchmark for robust long-form transcription, while Azure Speech and Custom Speech offer a practical industrial implementation path with support for domain-specific vocabulary. The literature also highlights the role of punctuation restoration and transcript cleanup in improving downstream NLP tasks. Together, these sources justify the project’s decision to combine an Azure-first ASR pipeline with an open benchmark baseline and additional preprocessing steps. [1](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/_layouts/15/Doc.aspx?sourcedoc=%7BDAA992C8-1301-4F13-9F64-AA3E79CC8408%7D&file=Project_Scope_v3.docx&action=default&mobileredirect=true)[2](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/Documents/Microsoft%20Copilot%20Chat%20Files/Literature_review.md)

Third, LLM-based handling of long transcripts is an active and practically relevant area. Existing work on transcript summarization and long-context processing provides useful lessons on prompt design, chunking strategy, and structured extraction. Although most studies focus on meetings or general long-form speech rather than maintenance videos, they still provide a strong methodological basis for using LLMs to reorganize raw transcript text into concise, structured units suitable for retrieval and learning support. [2](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/Documents/Microsoft%20Copilot%20Chat%20Files/Literature_review.md)

Fourth, the retrieval layer is supported by a rich body of literature on dense vector representations, approximate nearest neighbour search, and RAG. Foundational work on sentence embeddings and vector search explains how semantically similar content can be retrieved efficiently at scale, while RAG literature provides a theoretical framework for grounding system outputs in retrieved evidence. In addition, older instructional video retrieval research demonstrates that educational or instructional videos can be indexed and searched using transcript-like textual signals, making this project a contemporary extension of an established idea using newer AI methods. [2](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/Documents/Microsoft%20Copilot%20Chat%20Files/Literature_review.md)

Finally, evaluation is one of the better-supported areas in the literature. Standard IR metrics, ASR metrics, and test collection approaches provide a solid basis for the project’s planned evaluation framework. The scope document operationalizes this by setting concrete targets for WER, Precision@5, Recall@10, NDCG@5, and segment boundary F1, and by proposing expert-labelled ground truth using ASML subject-matter experts. [1](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/_layouts/15/Doc.aspx?sourcedoc=%7BDAA992C8-1301-4F13-9F64-AA3E79CC8408%7D&file=Project_Scope_v3.docx&action=default&mobileredirect=true)[2](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/Documents/Microsoft%20Copilot%20Chat%20Files/Literature_review.md)

## 2.3 Gaps in Research

Despite strong coverage of the individual building blocks, the literature reveals an important gap at the system level. There is limited prior work that combines microlearning theory, ASR, LLM-based structuring, timestamp-aware segmentation, semantic retrieval, and clip-level video extraction into one end-to-end pipeline for industrial maintenance training. Most existing studies focus on only one or two components, such as ASR accuracy, transcript summarization, or vector retrieval, rather than the complete transformation from long instructional videos to searchable micro-clips. [1](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/_layouts/15/Doc.aspx?sourcedoc=%7BDAA992C8-1301-4F13-9F64-AA3E79CC8408%7D&file=Project_Scope_v3.docx&action=default&mobileredirect=true)[2](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/Documents/Microsoft%20Copilot%20Chat%20Files/Literature_review.md)

A second gap concerns maintenance-specific transcript structuring. While there is emerging work on extracting structured knowledge from maintenance texts, the literature is still limited when it comes to long spoken instructional transcripts that contain domain jargon, procedural dependencies, and safety-critical context. This means there is still uncertainty about how reliably LLMs can identify step boundaries, prerequisites, parts, tools, and safety constraints in real industrial video transcripts without careful prompt design and expert validation. [2](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/Documents/Microsoft%20Copilot%20Chat%20Files/Literature_review.md)

A third gap concerns segmentation quality. The literature suggests that semantic similarity models do not automatically yield strong topic segmentation performance, especially across domains. In the maintenance-video setting, segment boundaries must correspond not only to topical changes but also to meaningful procedural units that can stand on their own as micro-learning clips. This creates a practical research challenge that is not fully addressed in current studies. [1](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/_layouts/15/Doc.aspx?sourcedoc=%7BDAA992C8-1301-4F13-9F64-AA3E79CC8408%7D&file=Project_Scope_v3.docx&action=default&mobileredirect=true)[2](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/Documents/Microsoft%20Copilot%20Chat%20Files/Literature_review.md)

A fourth and especially important gap lies in governance, safety, and traceability. The literature matrix explicitly identifies this area as weakly covered. In a maintenance setting, retrieved clips must be presented in a way that supports learning without being mistaken for official service instructions. This requires metadata, disclaimers, version awareness, source traceability, and expert review considerations that are often absent from generic AI retrieval literature. Addressing this gap is therefore one of the main applied contributions of the present thesis. [1](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/_layouts/15/Doc.aspx?sourcedoc=%7BDAA992C8-1301-4F13-9F64-AA3E79CC8408%7D&file=Project_Scope_v3.docx&action=default&mobileredirect=true)[2](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/Documents/Microsoft%20Copilot%20Chat%20Files/Literature_review.md)


# 3. Methodology

## 3.1 Research Design

This study follows an applied, prototype-oriented research design in which an end-to-end AI pipeline is developed and evaluated against clearly defined technical and practical criteria. The work is problem-driven: it starts from a concrete industrial challenge—difficulty in locating relevant procedures in long maintenance training videos—and translates that challenge into a set of design objectives for transcription, segmentation, retrieval, and safe presentation. The resulting artefact is a proof-of-concept system rather than a production deployment. [1](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/_layouts/15/Doc.aspx?sourcedoc=%7BDAA992C8-1301-4F13-9F64-AA3E79CC8408%7D&file=Project_Scope_v3.docx&action=default&mobileredirect=true)

Methodologically, the study combines system design with empirical evaluation. The design component focuses on building a pipeline that transforms long-form video content into searchable procedural segments and micro-clips. The evaluation component focuses on measuring whether each stage performs adequately using standard metrics and expert-labelled relevance judgements. This combination is appropriate because the thesis aims both to create a functioning technical solution and to generate evidence about its effectiveness in the target application context. [1](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/_layouts/15/Doc.aspx?sourcedoc=%7BDAA992C8-1301-4F13-9F64-AA3E79CC8408%7D&file=Project_Scope_v3.docx&action=default&mobileredirect=true)[2](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/Documents/Microsoft%20Copilot%20Chat%20Files/Literature_review.md)

## 3.2 Data and Materials

The primary data for this project consist of proprietary ASML customer support and maintenance training videos. These videos form the source material from which spoken transcripts, structured procedural segments, and final micro-clips are derived. Because the content is confidential, the dataset is handled within ASML’s governance constraints and is not intended for open publication. The data are expected to include technical vocabulary such as module names, tool references, part numbers, symptoms, and alarm or error codes. [1](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/_layouts/15/Doc.aspx?sourcedoc=%7BDAA992C8-1301-4F13-9F64-AA3E79CC8408%7D&file=Project_Scope_v3.docx&action=default&mobileredirect=true)

In addition to the source videos, the study requires several derived data artefacts:

- raw ASR transcripts; [1](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/_layouts/15/Doc.aspx?sourcedoc=%7BDAA992C8-1301-4F13-9F64-AA3E79CC8408%7D&file=Project_Scope_v3.docx&action=default&mobileredirect=true)
- cleaned or punctuated transcripts; [1](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/_layouts/15/Doc.aspx?sourcedoc=%7BDAA992C8-1301-4F13-9F64-AA3E79CC8408%7D&file=Project_Scope_v3.docx&action=default&mobileredirect=true)[2](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/Documents/Microsoft%20Copilot%20Chat%20Files/Literature_review.md)
- LLM-structured transcript segments with metadata fields such as title, steps, prerequisites, tools or parts, and safety flags; [1](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/_layouts/15/Doc.aspx?sourcedoc=%7BDAA992C8-1301-4F13-9F64-AA3E79CC8408%7D&file=Project_Scope_v3.docx&action=default&mobileredirect=true)[2](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/Documents/Microsoft%20Copilot%20Chat%20Files/Literature_review.md)
- timestamp mappings between text segments and the original video; [1](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/_layouts/15/Doc.aspx?sourcedoc=%7BDAA992C8-1301-4F13-9F64-AA3E79CC8408%7D&file=Project_Scope_v3.docx&action=default&mobileredirect=true)
- embeddings or vector representations for retrieval; [1](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/_layouts/15/Doc.aspx?sourcedoc=%7BDAA992C8-1301-4F13-9F64-AA3E79CC8408%7D&file=Project_Scope_v3.docx&action=default&mobileredirect=true)[2](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/Documents/Microsoft%20Copilot%20Chat%20Files/Literature_review.md)
- a labelled evaluation set created with the support of subject-matter experts for both ASR comparison and retrieval relevance assessment. [1](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/_layouts/15/Doc.aspx?sourcedoc=%7BDAA992C8-1301-4F13-9F64-AA3E79CC8408%7D&file=Project_Scope_v3.docx&action=default&mobileredirect=true)

The labelled evaluation material is expected to include representative transcript excerpts for WER analysis and a set of realistic maintenance queries with relevance labels for retrieval evaluation. Since the size of this ground-truth dataset depends on expert availability, it is treated as a practical constraint within the study design. [1](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/_layouts/15/Doc.aspx?sourcedoc=%7BDAA992C8-1301-4F13-9F64-AA3E79CC8408%7D&file=Project_Scope_v3.docx&action=default&mobileredirect=true)

## 3.3 System Pipeline / Technical Approach

The technical approach is organised as a multi-stage pipeline that maps raw training videos to retrieved micro-clips. The design follows the project scope and aligns each stage with either a primary Azure-based implementation or an open-source fallback for benchmarking and development. [1](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/_layouts/15/Doc.aspx?sourcedoc=%7BDAA992C8-1301-4F13-9F64-AA3E79CC8408%7D&file=Project_Scope_v3.docx&action=default&mobileredirect=true)

### Stage 1: ASR transcription

The first stage converts spoken video content into text using Azure Speech-to-Text as the primary ASR service. Whisper large-v3 is used as a benchmark baseline to compare transcription quality and robustness. Since the source material contains domain-specific terminology, the design includes vocabulary handling and, if needed, custom speech adaptation. [1](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/_layouts/15/Doc.aspx?sourcedoc=%7BDAA992C8-1301-4F13-9F64-AA3E79CC8408%7D&file=Project_Scope_v3.docx&action=default&mobileredirect=true)[2](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/Documents/Microsoft%20Copilot%20Chat%20Files/Literature_review.md)

### Stage 2: Transcript cleanup and normalization

After transcription, the text is cleaned to improve downstream processing. This includes punctuation restoration and normalization so that the transcript becomes more readable and structurally suitable for LLM processing and segmentation. This stage is important because unpunctuated ASR output can reduce the quality of both semantic boundary detection and structured extraction. [1](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/_layouts/15/Doc.aspx?sourcedoc=%7BDAA992C8-1301-4F13-9F64-AA3E79CC8408%7D&file=Project_Scope_v3.docx&action=default&mobileredirect=true)[2](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/Documents/Microsoft%20Copilot%20Chat%20Files/Literature_review.md)

### Stage 3: LLM-based transcript structuring

The cleaned transcripts are processed with an LLM to produce procedural segments relevant to customer support and maintenance workflows. Each segment is intended to include a title and structured fields such as step-by-step actions, prerequisites, tools, parts, and safety flags. The purpose of this stage is to transform raw speech text into a more interpretable knowledge unit that supports both learning and retrieval. [1](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/_layouts/15/Doc.aspx?sourcedoc=%7BDAA992C8-1301-4F13-9F64-AA3E79CC8408%7D&file=Project_Scope_v3.docx&action=default&mobileredirect=true)[2](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/Documents/Microsoft%20Copilot%20Chat%20Files/Literature_review.md)

### Stage 4: Semantic segmentation and timestamp alignment

To enable precise clip extraction, the system identifies semantic boundaries within the transcript so that content can be split into natural procedural units such as inspections, replacements, calibrations, or validation steps. These segments are then aligned with source-video timestamps, for example by using word-level timing information from the ASR output. The result is a mapping from structured segment to exact video interval. [1](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/_layouts/15/Doc.aspx?sourcedoc=%7BDAA992C8-1301-4F13-9F64-AA3E79CC8408%7D&file=Project_Scope_v3.docx&action=default&mobileredirect=true)[2](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/Documents/Microsoft%20Copilot%20Chat%20Files/Literature_review.md)

### Stage 5: Retrieval and ranking

Structured segments are indexed in a vector retrieval system. The primary approach uses Azure AI Search with vector indexing and semantic ranking, while FAISS serves as a local fallback for development or experimentation. At query time, the system accepts maintenance-oriented inputs such as symptom descriptions, task names, tool or module references, and error codes, and returns ranked, traceable segment results. [1](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/_layouts/15/Doc.aspx?sourcedoc=%7BDAA992C8-1301-4F13-9F64-AA3E79CC8408%7D&file=Project_Scope_v3.docx&action=default&mobileredirect=true)[2](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/Documents/Microsoft%20Copilot%20Chat%20Files/Literature_review.md)

### Stage 6: Micro-clip assembly

For the proof-of-concept output, retrieved segments are used to extract corresponding portions of the original video via `ffmpeg`. Where useful, clips may be enriched with captions and templated disclaimer or safety overlays. This stage demonstrates the final micro-learning concept, but it is not intended as a full production content-delivery system. [1](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/_layouts/15/Doc.aspx?sourcedoc=%7BDAA992C8-1301-4F13-9F64-AA3E79CC8408%7D&file=Project_Scope_v3.docx&action=default&mobileredirect=true)

Overall, the pipeline operationalizes the literature’s core insight that microlearning is pedagogically valuable and that modern AI methods make transcript-based retrieval technically feasible, while also acknowledging that segmentation quality, traceability, and safe presentation require careful design. [1](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/_layouts/15/Doc.aspx?sourcedoc=%7BDAA992C8-1301-4F13-9F64-AA3E79CC8408%7D&file=Project_Scope_v3.docx&action=default&mobileredirect=true)[2](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/Documents/Microsoft%20Copilot%20Chat%20Files/Literature_review.md)

## 3.4 Tools and Platforms

The project uses the Microsoft Azure ecosystem as its primary platform, in line with organizational policy. Azure Speech-to-Text is used for transcription, Azure OpenAI for LLM-based transcript structuring, and Azure AI Search for vector-based indexing and retrieval. Azure Video Indexer is considered as a possible accelerator during exploratory phases if it proves sufficiently accurate for the intended use case. [1](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/_layouts/15/Doc.aspx?sourcedoc=%7BDAA992C8-1301-4F13-9F64-AA3E79CC8408%7D&file=Project_Scope_v3.docx&action=default&mobileredirect=true)

To support benchmarking and local experimentation, several open-source tools are included in the methodological design. Whisper large-v3 is used as an ASR baseline, sentence-transformers are used for semantic embeddings and segmentation experiments, FAISS or ChromaDB can support local retrieval experiments, and `ffmpeg` is used for programmatic video clipping. For demonstration purposes, a lightweight Gradio interface or a Jupyter notebook may be used to expose the search-and-playback functionality. [1](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/_layouts/15/Doc.aspx?sourcedoc=%7BDAA992C8-1301-4F13-9F64-AA3E79CC8408%7D&file=Project_Scope_v3.docx&action=default&mobileredirect=true)[2](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/Documents/Microsoft%20Copilot%20Chat%20Files/Literature_review.md)

The use of both Azure-native and open-source tools is methodologically useful because it allows the study to compare practicality, quality, and flexibility while still keeping the primary solution aligned with the target deployment environment. [1](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/_layouts/15/Doc.aspx?sourcedoc=%7BDAA992C8-1301-4F13-9F64-AA3E79CC8408%7D&file=Project_Scope_v3.docx&action=default&mobileredirect=true)

## 3.5 Evaluation Methodology

The evaluation strategy is designed to assess the pipeline at multiple levels: transcription quality, segmentation quality, retrieval effectiveness, and practical suitability for maintenance learning support. The approach relies on standard metrics from ASR and information retrieval, combined with expert-labelled test material. [1](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/_layouts/15/Doc.aspx?sourcedoc=%7BDAA992C8-1301-4F13-9F64-AA3E79CC8408%7D&file=Project_Scope_v3.docx&action=default&mobileredirect=true)[2](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/Documents/Microsoft%20Copilot%20Chat%20Files/Literature_review.md)

### ASR evaluation

ASR performance is evaluated primarily using **Word Error Rate (WER)** by comparing system transcripts with manually annotated reference transcripts from a representative sample of video segments. The project scope sets an initial target of **WER < 10%**, with a stretch goal of **WER < 5%** after post-processing or adaptation. This evaluation helps determine whether transcript quality is sufficient for downstream structuring and retrieval. [1](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/_layouts/15/Doc.aspx?sourcedoc=%7BDAA992C8-1301-4F13-9F64-AA3E79CC8408%7D&file=Project_Scope_v3.docx&action=default&mobileredirect=true)[2](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/Documents/Microsoft%20Copilot%20Chat%20Files/Literature_review.md)

### Segmentation evaluation

Segment boundary quality is evaluated using **segment boundary F1**, comparing automatically detected boundaries with manually annotated boundaries under a tolerance window (e.g., ±30 seconds). This is important because poor segmentation would directly affect clip quality and retrieval granularity, even if the transcript text itself is accurate. [1](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/_layouts/15/Doc.aspx?sourcedoc=%7BDAA992C8-1301-4F13-9F64-AA3E79CC8408%7D&file=Project_Scope_v3.docx&action=default&mobileredirect=true)[2](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/Documents/Microsoft%20Copilot%20Chat%20Files/Literature_review.md)

### Retrieval evaluation

Retrieval quality is evaluated using expert-labelled relevance judgements on a set of realistic maintenance queries. The main metrics are:

- **Precision@5**, with an initial target greater than 0.7; [1](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/_layouts/15/Doc.aspx?sourcedoc=%7BDAA992C8-1301-4F13-9F64-AA3E79CC8408%7D&file=Project_Scope_v3.docx&action=default&mobileredirect=true)[2](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/Documents/Microsoft%20Copilot%20Chat%20Files/Literature_review.md)
- **Recall@10**, with an initial target greater than 0.6; [1](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/_layouts/15/Doc.aspx?sourcedoc=%7BDAA992C8-1301-4F13-9F64-AA3E79CC8408%7D&file=Project_Scope_v3.docx&action=default&mobileredirect=true)[2](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/Documents/Microsoft%20Copilot%20Chat%20Files/Literature_review.md)
- **NDCG@5**, with an initial target greater than 0.7. [1](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/_layouts/15/Doc.aspx?sourcedoc=%7BDAA992C8-1301-4F13-9F64-AA3E79CC8408%7D&file=Project_Scope_v3.docx&action=default&mobileredirect=true)[2](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/Documents/Microsoft%20Copilot%20Chat%20Files/Literature_review.md)

These metrics are appropriate because the system is intended to rank the most relevant segments near the top of the result list rather than simply retrieve all possibly relevant content. They also align with established IR evaluation practices. [1](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/_layouts/15/Doc.aspx?sourcedoc=%7BDAA992C8-1301-4F13-9F64-AA3E79CC8408%7D&file=Project_Scope_v3.docx&action=default&mobileredirect=true)[2](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/Documents/Microsoft%20Copilot%20Chat%20Files/Literature_review.md)

### Qualitative validation

In addition to metric-based evaluation, qualitative review by subject-matter experts is important for judging whether retrieved clips are genuinely useful, sufficiently contextualized, and safely interpretable for learning support. Expert feedback can also help identify failure cases, such as incomplete step sequences, ambiguous segment titles, poor timestamp alignment, or results that are semantically related but operationally unhelpful. [1](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/_layouts/15/Doc.aspx?sourcedoc=%7BDAA992C8-1301-4F13-9F64-AA3E79CC8408%7D&file=Project_Scope_v3.docx&action=default&mobileredirect=true)

## 3.6 Constraints, Assumptions, Ethics, and Safety

This study is subject to several practical constraints. First, the Microsoft Azure ecosystem is the primary tooling environment due to organizational policy, while open-source tools are used mainly for local development and benchmarking. Second, the video data are confidential and governed by internal data policies and GDPR-related requirements, which restrict data handling, sharing, and reproducibility outside the company environment. Third, compute availability may vary, so the pipeline must degrade gracefully when GPU resources are limited. Finally, the project timeline is limited to an 18-week graduation period, which reinforces the choice of a proof-of-concept rather than production-grade deployment. [1](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/_layouts/15/Doc.aspx?sourcedoc=%7BDAA992C8-1301-4F13-9F64-AA3E79CC8408%7D&file=Project_Scope_v3.docx&action=default&mobileredirect=true)

Several assumptions also shape the methodological choices. It is assumed that the source videos contain enough spoken procedural content for transcript-based retrieval to be viable, that expert time will be available for at least a modest labelled evaluation set, and that maintenance-relevant semantics can be captured sufficiently well through text-based segmentation and retrieval without requiring full multimodal understanding. These assumptions are reasonable given the current scope, but they also define the limits of what the prototype can claim. [1](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/_layouts/15/Doc.aspx?sourcedoc=%7BDAA992C8-1301-4F13-9F64-AA3E79CC8408%7D&file=Project_Scope_v3.docx&action=default&mobileredirect=true)[2](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/Documents/Microsoft%20Copilot%20Chat%20Files/Literature_review.md)

Ethically, the project operates in a sensitive technical domain where AI outputs could be misinterpreted as authoritative instructions. For that reason, the system is explicitly positioned as a learning-support tool rather than an operational decision system. Retrieved clips must remain traceable to their original source videos, and any captions, overlays, or interface elements should include templated disclaimers indicating that the content is supportive and not a substitute for official service documentation or validated procedures. Safety-critical content requires subject-matter expert review before any operational use. [1](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/_layouts/15/Doc.aspx?sourcedoc=%7BDAA992C8-1301-4F13-9F64-AA3E79CC8408%7D&file=Project_Scope_v3.docx&action=default&mobileredirect=true)[2](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/Documents/Microsoft%20Copilot%20Chat%20Files/Literature_review.md)

A final methodological consideration is governance. The literature matrix highlights that safety, governance, and traceability remain underdeveloped areas in current research, especially for maintenance AI applications. This means the project must go beyond technical performance and include metadata fields such as tool type, version or release, safety classification, prerequisites, and source references wherever possible. These measures help reduce misuse and support responsible deployment discussions, even at the prototype stage. [1](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/_layouts/15/Doc.aspx?sourcedoc=%7BDAA992C8-1301-4F13-9F64-AA3E79CC8408%7D&file=Project_Scope_v3.docx&action=default&mobileredirect=true)[2](https://asml-my.sharepoint.com/personal/neilross_daniel_manohar_asml_com/Documents/Microsoft%20Copilot%20Chat%20Files/Literature_review.md)
``