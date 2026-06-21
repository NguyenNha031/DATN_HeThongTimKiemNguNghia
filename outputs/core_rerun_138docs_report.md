# Core baseline/metrics/latency rerun report for 138-doc corpus

## Executive summary

| metric | value |
| --- | --- |
| status | PASS |
| metadata docs | 138 |
| vector docs | 138 |
| KG docs | 138 |
| core queries | 28 |
| judgment rows | 181 |
| baseline files generated | 5 official + 1 diagnostic support |
| metrics generated | yes |
| latency generated | yes |
| figures generated | 3 figure pairs |
| can proceed to supplementary diagnostics | YES |

No extended evaluation, candidate fusion, query expansion, or KG ablation was run in this step.

## Backup summary

- Backup folder: `archive_pre_final/before_138docs_core_rerun_20260531_133316`
- Files copied: 31
- Missing optional files: 6
- Manifest: `archive_pre_final/before_138docs_core_rerun_20260531_133316/backup_manifest.csv`

## Input validation

| check | value |
| --- | --- |
| core queries | 28 |
| query groups | {"local": 7, "biosecurity-management": 6, "disease-specific": 6, "species-location": 5, "hatchery-production-mode": 4} |
| judgment rows | 181 |
| label distribution | {"0": 60, "1": 63, "2": 58} |
| queries without relevant doc | 0 |
| judgments to removed docs | RIA3_002; RIA3_003 |
| metadata/vector/KG docs | 138/138/138 |
| FAISS ntotal/chunks_meta | 28542/28542 |
| KNQG_002 metadata/vector/KG | True/True/True |
| RIA3_002 metadata/vector/KG | False/False/False |
| RIA3_003 metadata/vector/KG | False/False/False |

## Baseline result audit

| baseline_name | rows | queries | unique_docs | top10_complete | removed_docs_present | doc_id_not_in_metadata_count | KNQG_002_appears | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| lexical | 280 | 28 | 57 | True | False | 0 | True | PASS |
| vector | 280 | 28 | 91 | True | False | 0 | True | PASS |
| vector_metadata | 280 | 28 | 95 | True | False | 0 | True | PASS |
| ontology_sparql | 280 | 28 | 63 | True | False | 0 | True | PASS |
| hybrid | 280 | 28 | 101 | True | False | 0 | True | PASS |
| vector_metadata_kg_no_intent | 280 | 28 | 101 | True | False | 0 | True | SUPPORT_PASS |

## Metrics summary

| baseline_name | num_queries | p_at_1 | p_at_5 | recall_at_5 | recall_at_10 | mrr | ndcg_at_5 | ndcg_at_10 | map |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| lexical | 28 | 0.392857 | 0.121429 | 0.179167 | 0.188095 | 0.404762 | 0.267285 | 0.267647 | 0.165551 |
| vector | 28 | 0.642857 | 0.321429 | 0.40102 | 0.471854 | 0.723951 | 0.534203 | 0.558917 | 0.365488 |
| vector_metadata | 28 | 0.642857 | 0.371429 | 0.459014 | 0.578741 | 0.745238 | 0.553576 | 0.601359 | 0.398379 |
| ontology_sparql | 28 | 0.535714 | 0.314286 | 0.34983 | 0.48682 | 0.626786 | 0.407718 | 0.458943 | 0.342683 |
| hybrid | 28 | 0.821429 | 0.392857 | 0.486139 | 0.624575 | 0.875 | 0.664514 | 0.710981 | 0.456584 |

Hybrid best across listed main metrics: True.

### Delta vs pre-rerun backup

| baseline_name | p_at_1_old | p_at_1_new | p_at_1_delta | mrr_old | mrr_new | mrr_delta | ndcg_at_10_old | ndcg_at_10_new | ndcg_at_10_delta |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| hybrid | 0.821429 | 0.821429 | 0 | 0.869388 | 0.875 | 0.005612 | 0.722203 | 0.710981 | -0.011222 |
| vector_metadata | 0.75 | 0.642857 | -0.107143 | 0.821769 | 0.745238 | -0.076531 | 0.66361 | 0.601359 | -0.062251 |

## Group summary

| query_group | hybrid_ndcg_at_10 | vector_metadata_ndcg_at_10 | delta | winner |
| --- | --- | --- | --- | --- |
| biosecurity-management | 0.762885 | 0.74697 | 0.015915 | hybrid |
| disease-specific | 0.631941 | 0.546053 | 0.085888 | hybrid |
| hatchery-production-mode | 0.68911 | 0.486798 | 0.202312 | hybrid |
| local | 0.719863 | 0.53003 | 0.189833 | hybrid |
| species-location | 0.748609 | 0.684506 | 0.064103 | hybrid |

Hybrid improves nDCG@10 over Vector+Metadata in all listed query groups in this rerun.

## Wilcoxon summary

| metric | n_queries | mean_hybrid | mean_vector_metadata | mean_diff | p_value | significant_at_0_05 | effect_direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P@1 | 28 | 0.821429 | 0.642857 | 0.178571 | 0.0253473 | True | hybrid>vector_metadata |
| MRR | 28 | 0.875 | 0.745238 | 0.129762 | 0.0421535 | True | hybrid>vector_metadata |
| nDCG@10 | 28 | 0.710981 | 0.601359 | 0.109622 | 0.00759822 | True | hybrid>vector_metadata |
| P@5 | 28 | 0.392857 | 0.371429 | 0.0214286 | 0.195668 | False | hybrid>vector_metadata |
| Recall@5 | 28 | 0.486139 | 0.459014 | 0.0271259 | 0.262033 | False | hybrid>vector_metadata |
| nDCG@5 | 28 | 0.664514 | 0.553576 | 0.110938 | 0.0231298 | True | hybrid>vector_metadata |

Interpretation is limited to the 28 paired core queries. Do not claim significance where p > 0.05.

## Latency summary

| baseline_name | num_queries | runs_per_query | mean_query_latency_ms | median_query_latency_ms | p95_query_latency_ms | max_query_latency_ms |
| --- | --- | --- | --- | --- | --- | --- |
| lexical | 28 | 5 | 425.216 | 423.98 | 454.048 | 481.054 |
| vector | 28 | 5 | 86.011 | 96.869 | 105.621 | 109.465 |
| vector_metadata | 28 | 5 | 56.033 | 55.036 | 69.053 | 72.019 |
| ontology_sparql | 28 | 5 | 56.545 | 55.562 | 80.301 | 91.771 |
| hybrid | 28 | 5 | 111.79 | 108.754 | 135.082 | 152.345 |

Latency was measured with the official five baseline builders. The existing latency script was not edited; a direct equivalent runner was used because it imports a removed diagnostic function.

## Figure check

| figure_path | exists | size_bytes | status | suggested_caption |
| --- | --- | --- | --- | --- |
| outputs\figures\fig_baseline_key_metrics.png | True | 57448 | PASS | Comparison of key retrieval metrics on the 28-query core set for the 138-document corpus. |
| outputs\figures\fig_baseline_key_metrics.pdf | True | 17444 | PASS | Comparison of key retrieval metrics on the 28-query core set for the 138-document corpus. |
| outputs\figures\fig_hybrid_vs_vector_metadata_by_group.png | True | 95905 | PASS | nDCG@10 comparison between Hybrid and Vector+Metadata by query group. |
| outputs\figures\fig_hybrid_vs_vector_metadata_by_group.pdf | True | 15667 | PASS | nDCG@10 comparison between Hybrid and Vector+Metadata by query group. |
| outputs\figures\fig_quality_latency_tradeoff.png | True | 64486 | PASS | Quality-latency tradeoff using nDCG@10 and mean per-query latency. |
| outputs\figures\fig_quality_latency_tradeoff.pdf | True | 18780 | PASS | Quality-latency tradeoff using nDCG@10 and mean per-query latency. |

## Problems / warnings

| severity | scope | issue | suggestion |
| --- | --- | --- | --- |
| WARNING | judgments | relevance_judgments_core.csv still contains RIA3_002/RIA3_003 | Not a runtime blocker because removed docs are absent from new baseline outputs; update judgments before final publication if strict corpus-only qrels are required |
| INFO | judgments | 30 new docs have no explicit judgments | Only informational; do not edit judgments in this step |

## Next step recommendation

Can proceed to supplementary diagnostics/experiments if needed: corpus topic distribution, KG score components, explanation quality, KG ablation, candidate fusion, and extended evaluation. Do not update final report text until the user confirms the next scope.

## Output files

- `outputs/core_rerun_138docs_report.md`
- `outputs/core_rerun_138docs_summary.csv`
- `outputs/core_baseline_results_138docs_audit.csv`
- `outputs/core_metrics_138docs_summary.csv`
- `outputs/core_latency_138docs_summary.csv`
- `outputs/core_figures_138docs_check.csv`
- `outputs/wilcoxon_hybrid_vs_vector_metadata_138docs.md`
- `outputs/core_rerun_138docs_input_validation_summary.csv`
- `outputs/core_metrics_138docs_vs_backup_delta.csv`