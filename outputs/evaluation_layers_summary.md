# Evaluation Layers Summary

## 1. Purpose

This artifact separates three evaluation layers of the project so that retrieval metrics, ontology/KG evaluation, and full-system contribution analysis are not mixed together.
It is a summary artifact only. It does not modify ontology files, metadata, query sets, relevance judgments, baseline outputs, metric outputs, or runtime retrieval code.

## 2. Layer 1 - Retrieval evaluation

Layer 1 evaluates search and ranking quality over the 28-query core retrieval benchmark.

**Input files**

- Query set: `data/eval/final_query_set_core.csv`
- Relevance judgments: `data/eval/relevance_judgments_core.csv`
- Baseline result files: lexical, vector, vector_metadata, ontology_sparql, hybrid, and vector_metadata_kg_no_intent.

**Baselines**

- `lexical`: BM25-style lexical retrieval.
- `vector`: FAISS + SentenceTransformer vector retrieval.
- `vector_metadata`: vector score plus metadata reranking.
- `ontology_sparql`: structured ontology/SPARQL baseline.
- `hybrid`: full hybrid retrieval.

**Metrics**

- P@1, P@3, P@5, Recall@5, MRR, nDCG@5, nDCG@10.
- Latency is reported separately when `baseline_latency_summary.csv` is available.

**Main outputs**

- `data/eval/metrics/baseline_metrics_summary.csv`
- `data/eval/metrics/baseline_metrics_by_group.csv`
- `data/eval/metrics/baseline_latency_summary.csv`

**Overall retrieval metrics**

| baseline | queries | P@1 | P@5 | Recall@5 | MRR | nDCG@10 |
| --- | --- | --- | --- | --- | --- | --- |
| lexical | 28 | 0.3929 | 0.1357 | 0.1962 | 0.4330 | 0.2991 |
| vector | 28 | 0.6786 | 0.3357 | 0.4159 | 0.7691 | 0.6022 |
| vector_metadata | 28 | 0.7500 | 0.3929 | 0.4888 | 0.8218 | 0.6636 |
| vector_metadata_kg_no_intent | 28 | 0.7500 | 0.3857 | 0.4790 | 0.8230 | 0.6779 |
| ontology_sparql | 28 | 0.5714 | 0.3429 | 0.3885 | 0.6446 | 0.4577 |
| hybrid | 28 | 0.8214 | 0.4071 | 0.4980 | 0.8694 | 0.7222 |

**Latency summary**

| baseline | runs/query | warmup | mean ms | median ms |
| --- | --- | --- | --- | --- |
| lexical | 5 | yes (1 call first query) | 421.311 | 422.610 |
| vector | 5 | yes (1 call first query) | 86.398 | 78.521 |
| vector_metadata | 5 | yes (1 call first query) | 43.574 | 41.565 |
| ontology_sparql | 5 | yes (1 call first query) | 56.835 | 55.912 |
| hybrid | 5 | yes (1 call first query) | 113.287 | 113.579 |

**Key result summary**

- Hybrid is the highest overall baseline across the primary summary metrics in this snapshot: `True`.
- `vector_metadata` is close to hybrid on several metrics, especially P@1 and MRR.
- `ontology_sparql` is not the best overall ranking baseline, but it is strong for structured/entity-heavy groups such as disease-specific queries.
- Lexical retrieval remains competitive in the local group; in `baseline_metrics_by_group.csv`, lexical leads or ties some local metrics such as P@1/MRR/nDCG@10.
- This is retrieval ranking evaluation, not competency-question evaluation.

## 3. Layer 2 - Ontology/KG evaluation

Layer 2 evaluates the ontology/KG as a structured knowledge layer. It does not measure end-to-end ranking quality.

**Competency questions**

- Total CQ: 10
- Correct: 10
- Partial: 0
- Incorrect: 0
- Accuracy-like ratio: 1.0000

| CQ group | total | correct | partial | incorrect |
| --- | --- | --- | --- | --- |
| document_retrieval | 4 | 4 | 0 | 0 |
| taxon_query | 2 | 2 | 0 | 0 |
| disease_query | 1 | 1 | 0 | 0 |
| pathogen_query | 1 | 1 | 0 | 0 |
| symptom_query | 1 | 1 | 0 | 0 |
| explanation | 1 | 1 | 0 | 0 |

**SPARQL / structured query role**

- Competency questions and the `ontology_sparql` baseline test whether structured relations/facts can be queried and used as evidence.
- This checks KG fact usability; it does not replace judged retrieval ranking metrics.

**Runtime-oriented ontology quality**

- Ontology file: `data\ontology\taxon_enriched_facts_v2.owl`
- Total triples: 1324
- Document nodes: 110
- Metadata docs mapped to KG: 110 / 110
- aboutTaxon coverage: 108 docs (0.9818)
- aboutDisease coverage: 68 docs (0.6182)
- aboutLocation coverage: 47 docs (0.4273)
- documentProductionMode coverage: 109 docs (0.9909)
- Dangling fact objects: 0

**Reasoner-based consistency check**

- Reasoner used: `owlready2_hermit`
- Check status: `completed`
- is_consistent: `True`
- Unsatisfiable classes count: 0
- Limitation: reasoner consistency does not prove that every asserted fact is correct in the aquaculture domain.
- Competency questions and reasoner checks do not replace retrieval metrics.

## 4. Layer 3 - Full-system contribution analysis

Layer 3 analyzes how each signal layer contributes to the full hybrid system.

**Ablation configurations**

- `vector`: score = vector_score.
- `vector_metadata`: score = vector_score + metadata_delta.
- `vector_metadata_kg_no_intent`: score = vector_score + metadata_delta + kg_score.
- `hybrid`: score = vector_score + metadata_delta + kg_score + intent_adjustment.

**Ablation metric summary**

| configuration | P@1 | P@5 | MRR | nDCG@10 |
| --- | --- | --- | --- | --- |
| vector | 0.6786 | 0.3357 | 0.7691 | 0.6022 |
| vector_metadata | 0.7500 | 0.3929 | 0.8218 | 0.6636 |
| vector_metadata_kg_no_intent | 0.7500 | 0.3857 | 0.8230 | 0.6779 |
| hybrid | 0.8214 | 0.4071 | 0.8694 | 0.7222 |

**Wilcoxon hybrid vs vector_metadata**

| metric | n | mean hybrid | mean vector_metadata | p-value | significant @0.05 |
| --- | --- | --- | --- | --- | --- |
| P@1 | 28 | 0.8214 | 0.7500 | 0.3173 | False |
| MRR | 28 | 0.8694 | 0.8218 | 0.3430 | False |
| nDCG@10 | 28 | 0.7222 | 0.6636 | 0.0884 | False |

- The Wilcoxon result should be interpreted cautiously: hybrid has higher means on the main metrics, but the tested differences are not significant at p < 0.05 in the current 28-query core set.

**Error analysis**

- Total curated cases: 10
- metadata_incomplete: 1
- missing_alias: 1
- missing_disease_fact: 1
- missing_location_fact: 2
- not_error_but_baseline_limitation: 2
- scoring_or_intent_issue: 1
- weak_candidate_pool: 2

- Ablation is not the same as the overall baseline comparison; it isolates contribution of signal layers inside the hybrid design.

## 5. Cross-layer interpretation

- Retrieval evaluation answers: which method retrieves and ranks judged documents better?
- Ontology/KG evaluation answers: can the ontology/KG expose structured knowledge, answer competency questions, and remain logically consistent under a reasoner?
- Contribution analysis answers: how do metadata, KG scoring, and intent adjustment contribute to the full hybrid score?
- Retrieval metrics are not competency questions. Competency questions/reasoner checks are not retrieval ranking. Ablation is not the overall baseline comparison.

## 6. Files checklist

**Files read**

- `data/eval/final_query_set_core.csv`
- `data/eval/relevance_judgments_core.csv`
- `data/eval/results/baseline_lexical_core.csv`
- `data/eval/results/baseline_vector_core.csv`
- `data/eval/results/baseline_vector_metadata_core.csv`
- `data/eval/results/baseline_ontology_sparql_core.csv`
- `data/eval/results/baseline_hybrid_core.csv`
- `data/eval/results/baseline_vector_metadata_kg_no_intent_core.csv`
- `data/eval/metrics/baseline_metrics_summary.csv`
- `data/eval/metrics/baseline_metrics_by_group.csv`
- `data/eval/metrics/baseline_latency_summary.csv`
- `outputs/competency_questions_results.csv`
- `outputs/competency_questions_summary.json`
- `outputs/ontology_quality_check.md`
- `outputs/ontology_quality_check.json`
- `outputs/ontology_reasoner_consistency_check.md`
- `outputs/ontology_reasoner_consistency_check.json`
- `outputs/wilcoxon_hybrid_vs_vector_metadata.csv`
- `outputs/wilcoxon_hybrid_vs_vector_metadata.json`
- `outputs/error_analysis_core.csv`
- `outputs/error_analysis_summary.json`

**Missing or not found**

- None from the expected file list.

Generated at: `2026-05-23T16:13:33.942445+00:00`
