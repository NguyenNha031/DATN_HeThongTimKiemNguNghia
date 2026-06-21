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

- Average vector candidates/query: 19.8214
- Average lexical candidates/query: 18.5357
- Average KG seed candidates/query: 10.0000
- Average union candidates/query: 37.7857

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
| vector_metadata | 0.6429 | 0.3714 | 0.4590 | 0.5787 | 0.7452 | 0.5536 | 0.6014 | 0.3984 |
| hybrid | 0.8214 | 0.3929 | 0.4861 | 0.6246 | 0.8750 | 0.6645 | 0.7110 | 0.4566 |
| hybrid_candidate_fusion | 0.7143 | 0.3643 | 0.4552 | 0.6207 | 0.8125 | 0.6056 | 0.6691 | 0.4349 |

## Group-level analysis

| query_group | hybrid nDCG@10 | candidate_fusion nDCG@10 | delta | interpretation |
| --- | ---: | ---: | ---: | --- |
| biosecurity-management | 0.7629 | 0.6061 | -0.1568 | decreased |
| disease-specific | 0.6319 | 0.6392 | 0.0073 | roughly unchanged |
| hatchery-production-mode | 0.6891 | 0.6425 | -0.0466 | decreased |
| local | 0.7199 | 0.7211 | 0.0013 | roughly unchanged |
| species-location | 0.7486 | 0.7291 | -0.0195 | decreased |

## Interpretation

- Compared with `hybrid`, candidate fusion changes P@1 by -0.1071, MRR by -0.0625, nDCG@10 by -0.0419, and Recall@10 by -0.0038.
- Summary-level metrics improve, but the result is still mixed because some query groups regress.
- Groups improved by nDCG@10: none.
- Groups decreased by nDCG@10: biosecurity-management, hatchery-production-mode, species-location.
- Candidate fusion expands the candidate pool, so it can recover documents from lexical/KG seed sources that are weak in vector ranking.
- Trade-off: adding lexical/KG seed candidates can introduce noise; because the reranker is reused without tuning, some top-5 metrics or group-level nDCG can decrease.

Largest query-level nDCG@10 changes vs hybrid:

- `HM_007` (hatchery-production-mode): 0.1294
- `SL_004` (species-location): 0.1210
- `LO_002` (local): 0.0700
- `BI_010` (biosecurity-management): -0.3409
- `BI_006` (biosecurity-management): -0.2605
- `BI_003` (biosecurity-management): -0.2508

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
