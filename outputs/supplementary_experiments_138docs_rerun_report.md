# Supplementary experiments rerun report for 138-doc snapshot

## Executive summary

| item | value |
| --- | --- |
| status | PASS |
| generated_at | 2026-05-31 16:03:21 |
| metadata_rows | 138 |
| raw_files | 138 |
| candidate_fusion | PASS |
| extended_evaluation | PASS |
| figures_updated | PASS |
| query_expansion | FUTURE_WORK_ONLY |

No metadata/raw docs/vector store/ontology/KG/scoring/runtime files were modified. Core official baseline files were not overwritten; only supplementary candidate-fusion and extended-evaluation outputs were updated.

## Backup

- Backup manifest: `outputs/supplementary_experiments_138docs_rerun_backup_manifest.csv`
- Backup folder is listed in the manifest copied from `archive_pre_final/`.

## Candidate fusion core rerun

- Result file: `data\eval\results\baseline_hybrid_candidate_fusion_core.csv`
- Rows: 280
- Queries: 28
- Removed docs present: False 
- Run note: `experiments/run_hybrid_candidate_fusion.py` required temporary `PYTHONPATH=archive_pre_final/old_candidate_fusion_v1` because its legacy helper module is archived, not present at project root.

### Candidate fusion metrics

| method | queries | P@1 | P@5 | Recall@10 | MRR | nDCG@10 | MAP |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| vector_metadata | 28 | 0.6429 | 0.3714 | 0.5787 | 0.7452 | 0.6014 | 0.3984 |
| hybrid | 28 | 0.8214 | 0.3929 | 0.6246 | 0.8750 | 0.7110 | 0.4566 |
| hybrid_candidate_fusion | 28 | 0.7143 | 0.3643 | 0.6207 | 0.8125 | 0.6691 | 0.4349 |

## Extended evaluation rerun

- Summary metrics: `data\eval\metrics\baseline_metrics_summary_extended.csv`
- By-query metrics: `data\eval\metrics\baseline_metrics_by_query_extended.csv`
- By-group metrics: `data\eval\metrics\baseline_metrics_by_group_extended.csv`
- Removed docs present in any extended result: False

| method | result_file | rows | queries | removed_docs_present |
| --- | --- | ---: | ---: | --- |
| lexical | `data\eval\results\baseline_lexical_extended.csv` | 960 | 96 | False  |
| vector | `data\eval\results\baseline_vector_extended.csv` | 960 | 96 | False  |
| vector_metadata | `data\eval\results\baseline_vector_metadata_extended.csv` | 954 | 96 | False  |
| ontology_sparql | `data\eval\results\baseline_ontology_sparql_extended.csv` | 960 | 96 | False  |
| hybrid | `data\eval\results\baseline_hybrid_extended.csv` | 954 | 96 | False  |
| hybrid_candidate_fusion | `data\eval\results\baseline_hybrid_candidate_fusion_extended.csv` | 960 | 96 | False  |

### Extended metrics

| method | queries | P@1 | P@5 | Recall@10 | MRR | nDCG@10 | MAP |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| lexical | 96 | 0.7917 | 0.6354 | 0.3297 | 0.8082 | 0.5946 | 0.3016 |
| vector | 96 | 0.8438 | 0.6750 | 0.4122 | 0.8886 | 0.6410 | 0.3521 |
| vector_metadata | 96 | 0.8854 | 0.7583 | 0.4796 | 0.9179 | 0.7226 | 0.4080 |
| ontology_sparql | 96 | 0.7708 | 0.6958 | 0.4311 | 0.8247 | 0.5805 | 0.3672 |
| hybrid | 96 | 0.9375 | 0.7625 | 0.4972 | 0.9546 | 0.7570 | 0.4292 |
| hybrid_candidate_fusion | 96 | 0.9062 | 0.7542 | 0.4957 | 0.9366 | 0.7547 | 0.4261 |

## Updated figures

| figure | status |
| --- | --- |
| `outputs/figures/fig_candidate_fusion_summary.png` | updated |
| `outputs/figures/fig_extended_evaluation_summary.png` | updated |

## Still stale / future work

- Query expansion was not rerun in this step and should remain future-work/supporting-only unless rerun for the 138-doc snapshot.
- Core official baseline/metrics remain the source of truth for the main 28-query evaluation.

## Can be used in final Chapter 4?

- Candidate fusion: usable as a supplementary/extension experiment for the 138-doc snapshot. It should not replace the official Hybrid baseline because its metrics are lower than Hybrid on the 28-query core set.
- Extended evaluation: usable as supplementary stress-test evidence for the 138-doc snapshot, with the existing caveat that extended judgments were generated automatically and should be described as extension/supporting evidence.
- Query expansion: do not use as final quantitative evidence unless rerun.

## Output files

- `outputs/supplementary_experiments_138docs_rerun_report.md`
- `outputs/supplementary_experiments_138docs_rerun_summary.csv`
- `outputs/supplementary_candidate_fusion_138docs_run_log.txt`
- `outputs/supplementary_extended_evaluation_138docs_run_log.txt`