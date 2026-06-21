# Hybrid Candidate Fusion Experiment

## Purpose

Thí nghiệm này nhằm giảm phụ thuộc vào vector candidate pool ban đầu bằng cách hợp nhất ứng viên từ BM25, vector search và KG/SPARQL seed trước khi rerank. Đây là experiment/extension, không thay baseline `hybrid` final.

## Method

- Lexical candidates: BM25 over vector-store chunk text, aggregated to document level, `lexical_top_k=20`.
- Vector candidates: FAISS vector search, aggregated to document level, `vector_top_k=20`.
- KG/SPARQL seed candidates: top documents from `baseline_ontology_sparql_core.csv`, `kg_seed_top_k=20`; actual file has top 10 average seeds/query available.
- Candidate pool is deduplicated by `doc_id`; each row keeps `candidate_sources`, source ranks and source scores when available.
- Reranking/scoring reuses current hybrid components through existing functions: `vector_score + metadata_delta + kg_score + intent_adjustment`.
- The experiment does not change the query set, judgments, metadata, ontology, runtime final, or old baseline outputs/metrics.

Candidate pool statistics:

- Average vector candidates/query: 19.5714
- Average lexical candidates/query: 10.0357
- Average KG seed candidates/query: 10.0000
- Average union candidates/query: 31.8929

Existing baseline metric files read for comparison:

- `data\eval\metrics\baseline_metrics_summary.csv`
- `data\eval\metrics\baseline_metrics_by_group.csv`
- `data\eval\metrics\baseline_metrics_per_query.csv`

## Outputs

- `data\eval\results\baseline_hybrid_candidate_fusion_core.csv`
- `data\eval\metrics\hybrid_candidate_fusion_metrics_summary.csv`
- `data\eval\metrics\hybrid_candidate_fusion_metrics_by_query.csv`
- `data\eval\metrics\hybrid_candidate_fusion_metrics_by_group.csv`
- `outputs\hybrid_candidate_fusion_analysis.md`

## Metrics summary

| method | P@1 | P@5 | Recall@5 | Recall@10 | MRR | nDCG@5 | nDCG@10 | MAP |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| vector_metadata | 0.7500 | 0.3929 | 0.4888 | 0.6246 | 0.8218 | 0.6143 | 0.6636 | 0.4750 |
| hybrid | 0.8214 | 0.4071 | 0.4980 | 0.6365 | 0.8694 | 0.6695 | 0.7222 | 0.4972 |
| hybrid_candidate_fusion | 0.8571 | 0.4214 | 0.5278 | 0.7061 | 0.9000 | 0.6721 | 0.7345 | 0.5428 |

## Group-level analysis

| query_group | hybrid nDCG@10 | candidate_fusion nDCG@10 | delta | interpretation |
| --- | ---: | ---: | ---: | --- |
| biosecurity-management | 0.7794 | 0.7794 | 0.0000 | roughly unchanged |
| disease-specific | 0.6450 | 0.6488 | 0.0039 | roughly unchanged |
| hatchery-production-mode | 0.6891 | 0.6535 | -0.0356 | decreased |
| local | 0.7334 | 0.8323 | 0.0990 | improved |
| species-location | 0.7571 | 0.7110 | -0.0461 | decreased |

## Interpretation

- Compared with `hybrid`, candidate fusion changes P@1 by 0.0357, MRR by 0.0306, nDCG@10 by 0.0123, and Recall@10 by 0.0696.
- Summary-level metrics improve, but the result is still mixed because some query groups regress.
- Groups improved by nDCG@10: local.
- Groups decreased by nDCG@10: hatchery-production-mode, species-location.
- Candidate fusion expands the candidate pool, so it can recover documents from lexical/KG seed sources that are weak in vector ranking.
- Trade-off: adding lexical/KG seed candidates can introduce noise; because the reranker is reused without tuning, some top-5 metrics or group-level nDCG can decrease.

Largest query-level nDCG@10 changes vs hybrid:

- `LO_001` (local): 0.2658
- `LO_005` (local): 0.2291
- `LO_004` (local): 0.1979
- `SL_001` (species-location): -0.3680
- `HM_002` (hatchery-production-mode): -0.1677
- `HM_010` (hatchery-production-mode): -0.1258

## Report recommendation

B. Ket qua mixed: chi nen dua vao Chuong 5/huong phat trien hoac phu luc ky thuat, khong thay hybrid final.

## Safety note

- Không sửa `hybrid_search.py`.
- Không sửa `kg_runtime.py`.
- Không sửa `vector_search.py`.
- Không sửa ontology final.
- Không sửa metadata.
- Không sửa query set.
- Không sửa relevance judgments.
- Không sửa baseline metrics cũ.
- Không sửa baseline outputs cũ ngoài output riêng của experiment `baseline_hybrid_candidate_fusion_core.csv`.
