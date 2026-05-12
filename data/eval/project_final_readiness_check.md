# Project Final Readiness Check

Checked at: 2026-05-11 19:55:29 +07:00

## Active Files

All required active project files/directories are present.

| Item | Status |
|---|---|
| `data/ontology/taxon_enriched_facts_v2.owl` | OK |
| `data/metadata/document_metadata_cleaned.xlsx` | OK |
| `data/eval/final_query_set_core.csv` | OK |
| `data/eval/relevance_judgments_core.csv` | OK |
| `data/eval/relevance_guidelines_core.md` | OK |
| `vector_store/` | OK |
| `outputs/kg_runtime_verification.json` | OK |
| `data/eval/final_freeze_report.md` | OK |
| `data/eval/final_active_files_manifest.csv` | OK |

## KG Runtime

`outputs/kg_runtime_verification.json` confirms the active KG runtime snapshot.

| Field | Value | Status |
|---|---:|---|
| `ontology_file_loaded` | `data\ontology\taxon_enriched_facts_v2.owl` | OK |
| `total_document_nodes_in_kg` | 110 | OK |
| `total_metadata_docs` | 110 | OK |
| `mapped_doc_count` | 110 | OK |
| `unmapped_doc_count` | 0 | OK |

## Baseline Outputs

All required baseline output files are present and each contains 28 unique `query_id` values.

| Baseline file | Unique query_id | Status |
|---|---:|---|
| `data/eval/results/baseline_lexical_core.csv` | 28 | OK |
| `data/eval/results/baseline_vector_core.csv` | 28 | OK |
| `data/eval/results/baseline_vector_metadata_core.csv` | 28 | OK |
| `data/eval/results/baseline_ontology_sparql_core.csv` | 28 | OK |
| `data/eval/results/baseline_hybrid_core.csv` | 28 | OK |

## Metric Outputs

All required metric output files are present.

| Metric file | Status |
|---|---|
| `data/eval/metrics/baseline_metrics_summary.csv` | OK |
| `data/eval/metrics/baseline_metrics_by_group.csv` | OK |
| `data/eval/metrics/baseline_metrics_per_query.csv` | OK |

## Hybrid Final Metrics

The final hybrid metrics in `baseline_metrics_summary.csv` match the locked values.

| Metric | Value | Status |
|---|---:|---|
| P@1 | 0.821429 | OK |
| MRR | 0.869388 | OK |
| nDCG@10 | 0.722203 | OK |

## Latency Outputs

All required latency output files are present. `baseline_latency_per_query.csv` contains 140 rows, with 28 queries for each of the 5 baselines.

| Latency file | Status |
|---|---|
| `data/eval/metrics/baseline_latency_summary.csv` | OK |
| `data/eval/metrics/baseline_latency_per_query.csv` | OK |

Current latency summary:

| baseline_name | num_queries | runs_per_query | warmup_done | mean_query_latency_ms | median_query_latency_ms | min_query_latency_ms | max_query_latency_ms |
|---|---:|---:|---|---:|---:|---:|---:|
| lexical | 28 | 5 | yes (1 call first query) | 421.311 | 422.610 | 388.779 | 458.557 |
| vector | 28 | 5 | yes (1 call first query) | 86.398 | 78.521 | 60.211 | 128.812 |
| vector_metadata | 28 | 5 | yes (1 call first query) | 43.574 | 41.565 | 26.446 | 73.554 |
| ontology_sparql | 28 | 5 | yes (1 call first query) | 56.835 | 55.912 | 36.413 | 99.532 |
| hybrid | 28 | 5 | yes (1 call first query) | 113.287 | 113.579 | 74.850 | 147.299 |

## Legacy Path Check

Checked core scripts:

- `run_core_baselines.py`
- `hybrid_search.py`
- `kg_runtime.py`
- `vector_search.py`
- `verify_kg_runtime.py`
- `data/eval/metrics/compute_core_metrics.py`
- `measure_core_baseline_latency.py`

Findings:

- No usage found for `final_query_set.csv`.
- No usage found for `final_query_set_extended.csv`.
- No usage found for `outputs/archive/`.
- No usage found for `taxon_enriched_facts_v2_backfilled_runtime.owl`.
- `vector_search.py` contains a fallback path to `data/metadata/document_metadata.xlsx`, but it prefers `data/metadata/document_metadata_cleaned.xlsx` when that file exists. Because the cleaned metadata file is present, this fallback does not affect the current runtime.

## Conclusion

Project technical artifacts are complete and internally consistent for the final locked snapshot.

Status: ready to stop technical work.

Operational note: do not open new technical branches and do not modify code, ontology, metadata, query set, relevance judgments, scoring, or heuristic unless there is a new explicit requirement.
