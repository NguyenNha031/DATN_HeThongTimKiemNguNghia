# Final Freeze Report - Semantic Search Aquaculture Snapshot

Ngay gio chay final snapshot: 2026-05-09 15:37:19 +07:00.

Pham vi: kiem tra file active, chay lai KG verify, baseline, metric va latency tren snapshot hien tai. Khong thay doi ontology, metadata, query set, relevance judgments, scoring, heuristic, alias logic hoac intent adjustment.

## 1. Active Files

| Thanh phan | File active |
|---|---|
| Ontology runtime | `data/ontology/taxon_enriched_facts_v2.owl` |
| Metadata | `data/metadata/document_metadata_cleaned.xlsx` |
| Query set | `data/eval/final_query_set_core.csv` |
| Relevance judgments | `data/eval/relevance_judgments_core.csv` |
| Relevance guidelines | `data/eval/relevance_guidelines_core.md` |
| Vector store | `vector_store/` |
| KG verification output | `outputs/kg_runtime_verification.json` |

## 2. Main Scripts

- `hybrid_search.py`
- `kg_runtime.py`
- `vector_search.py`
- `verify_kg_runtime.py`
- `run_core_baselines.py`
- `data/eval/metrics/compute_core_metrics.py`
- `measure_core_baseline_latency.py`

## 3. KG Runtime Verification

Command:

```bash
python verify_kg_runtime.py
```

Ket qua chinh trong `outputs/kg_runtime_verification.json`:

| Check | Gia tri |
|---|---:|
| ontology runtime loaded | `data\ontology\taxon_enriched_facts_v2.owl` |
| total_document_nodes_in_kg | 110 |
| total_metadata_docs | 110 |
| mapped_doc_count | 110 |
| unmapped_doc_count | 0 |

Ket luan: KG runtime pass, document mapping dat 110/110.

## 4. Baseline Outputs

Command:

```bash
python run_core_baselines.py
```

Output trong `data/eval/results/`:

| Baseline | File | Query distinct | Rows |
|---|---|---:|---:|
| lexical/BM25 | `baseline_lexical_core.csv` | 28 | 280 |
| vector | `baseline_vector_core.csv` | 28 | 280 |
| vector_metadata | `baseline_vector_metadata_core.csv` | 28 | 280 |
| ontology_sparql | `baseline_ontology_sparql_core.csv` | 28 | 280 |
| hybrid | `baseline_hybrid_core.csv` | 28 | 280 |

## 5. Metric Outputs

Command:

```bash
python data/eval/metrics/compute_core_metrics.py
```

Output:

- `data/eval/metrics/baseline_metrics_summary.csv`
- `data/eval/metrics/baseline_metrics_by_group.csv`
- `data/eval/metrics/baseline_metrics_per_query.csv`

Metric summary:

| baseline_name | num_queries | P@1 | P@3 | P@5 | Recall@5 | MRR | nDCG@5 | nDCG@10 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| lexical | 28 | 0.392857 | 0.214286 | 0.135714 | 0.196173 | 0.433036 | 0.271533 | 0.299142 |
| vector | 28 | 0.678571 | 0.452381 | 0.335714 | 0.415901 | 0.769133 | 0.555952 | 0.602224 |
| vector_metadata | 28 | 0.750000 | 0.523810 | 0.392857 | 0.488776 | 0.821769 | 0.614302 | 0.663610 |
| ontology_sparql | 28 | 0.571429 | 0.428571 | 0.342857 | 0.388520 | 0.644643 | 0.409145 | 0.457700 |
| hybrid | 28 | 0.821429 | 0.535714 | 0.407143 | 0.498044 | 0.869388 | 0.669526 | 0.722203 |

Ket luan: hybrid la baseline tot nhat theo P@1, P@3, P@5, Recall@5, MRR, nDCG@5 va nDCG@10 trong snapshot nay.

## 6. Latency Outputs

Command:

```bash
python measure_core_baseline_latency.py
```

Output:

- `data/eval/metrics/baseline_latency_summary.csv`
- `data/eval/metrics/baseline_latency_per_query.csv`

Latency summary:

| baseline_name | num_queries | runs_per_query | mean_ms | median_ms | min_ms | max_ms |
|---|---:|---:|---:|---:|---:|---:|
| lexical | 28 | 5 | 421.311 | 422.610 | 388.779 | 458.557 |
| vector | 28 | 5 | 86.398 | 78.521 | 60.211 | 128.812 |
| vector_metadata | 28 | 5 | 43.574 | 41.565 | 26.446 | 73.554 |
| ontology_sparql | 28 | 5 | 56.835 | 55.912 | 36.413 | 99.532 |
| hybrid | 28 | 5 | 113.287 | 113.579 | 74.850 | 147.299 |

Latency scope: wall-clock per query; resource loading is outside timed calls; each baseline uses 28 core queries, 5 runs per query, with warmup on first query.

## 7. Comparison With Current Report Numbers

Metric values match the report values for hybrid:

| Metric | Report | Final run | Delta |
|---|---:|---:|---:|
| hybrid P@1 | 0.821429 | 0.821429 | 0.000000 |
| hybrid MRR | 0.869388 | 0.869388 | 0.000000 |
| hybrid nDCG@10 | 0.722203 | 0.722203 | 0.000000 |

Latency values differ from the report values and should be updated in the Word report if this final run is used as the locked snapshot:

| Baseline | Report mean_ms | Final mean_ms | Delta |
|---|---:|---:|---:|
| lexical | 638.587 | 421.311 | -217.276 |
| vector | 99.063 | 86.398 | -12.665 |
| vector_metadata | 53.845 | 43.574 | -10.271 |
| ontology_sparql | 100.958 | 56.835 | -44.123 |
| hybrid | 133.095 | 113.287 | -19.808 |

## 8. Freeze Notes

- `data/eval/final_active_files_manifest.csv` exists and lists the active files, derived outputs, scripts, and legacy query files marked as non-source-of-truth for core metric evaluation.
- Legacy query files such as `data/eval/final_query_set.csv` and `data/eval/final_query_set_extended.csv` remain present but are not used by the final core metric scripts.
- `kg_runtime.py` and `hybrid_search.py` still contain fallback ontology paths (`taxon_enriched_facts.owl`, `taxon_enriched_aliases.owl`, `taxon_enriched.owl`, `taxon.owl`), but final runtime verification confirms that the active loaded ontology is `taxon_enriched_facts_v2.owl`.
- `vector_search.py` contains fallback metadata `data/metadata/document_metadata.xlsx`; because `data/metadata/document_metadata_cleaned.xlsx` exists, the cleaned metadata file is selected.
- After this snapshot, do not change code, ontology, metadata, query set, relevance judgments, scoring, heuristic, alias logic, or intent adjustment unless there is a new explicit requirement.
