# Chapter 4 Figures Update Report - 138 Docs

## Executive Summary

| item | value |
| --- | --- |
| status | PASS |
| archive directory | `outputs/figures/archive_pre_final_138docs_update_20260601_154150` |
| figures generated | 8 mapped figures, PNG and PDF |
| metadata/raw docs/vector store/ontology/KG/scoring/runtime modified | No |
| baseline/metrics/latency rerun | No |
| query expansion final figure | Not generated; future work only |
| can use in Chapter 4 final | Yes |

Old figure PNG/PDF files in `outputs/figures/` were moved into the archive before generating the final 138-doc figures. No figure file was permanently deleted.

## Generated Figures

| figure | PNG | PDF | source data | status |
| --- | --- | --- | --- | --- |
| 4.1 | `outputs/figures/baseline_key_metrics_138docs.png` | `outputs/figures/baseline_key_metrics_138docs.pdf` | `data/eval/metrics/baseline_metrics_summary_plus.csv` | PASS |
| 4.2 | `outputs/figures/quality_latency_tradeoff_138docs.png` | `outputs/figures/quality_latency_tradeoff_138docs.pdf` | `data/eval/metrics/baseline_metrics_summary_plus.csv; data/eval/metrics/baseline_latency_summary.csv` | PASS |
| 4.3 | `outputs/figures/hybrid_vs_vector_metadata_by_group_138docs.png` | `outputs/figures/hybrid_vs_vector_metadata_by_group_138docs.pdf` | `data/eval/metrics/baseline_metrics_by_group.csv` | PASS |
| 4.6 | `outputs/figures/hybrid_ablation_signal_layers_138docs.png` | `outputs/figures/hybrid_ablation_signal_layers_138docs.pdf` | `data/eval/metrics/baseline_metrics_summary_plus.csv; data/eval/metrics/kg_ablation_metrics_summary.csv` | PASS |
| 4.7 | `outputs/figures/kg_fact_coverage_runtime_contribution_138docs.png` | `outputs/figures/kg_fact_coverage_runtime_contribution_138docs.pdf` | `outputs/kg_sync_138docs_fact_coverage.csv; outputs/kg_runtime_contribution_summary_138docs.csv` | PASS |
| 4.8 | `outputs/figures/kg_ablation_diagnostic_138docs.png` | `outputs/figures/kg_ablation_diagnostic_138docs.pdf` | `data/eval/metrics/kg_ablation_metrics_summary.csv` | PASS |
| 4.9 | `outputs/figures/candidate_fusion_key_metrics_138docs.png` | `outputs/figures/candidate_fusion_key_metrics_138docs.pdf` | `data/eval/metrics/hybrid_candidate_fusion_metrics_summary.csv` | PASS |
| 4.10 | `outputs/figures/extended_evaluation_96_queries_138docs.png` | `outputs/figures/extended_evaluation_96_queries_138docs.pdf` | `data/eval/metrics/baseline_metrics_summary_extended.csv` | PASS |

## Data Notes

- Figure 4.1 uses the five core baselines from `baseline_metrics_summary_plus.csv` with P@1, MRR, and nDCG@10.
- Figure 4.2 joins core nDCG@10 with mean latency from `baseline_latency_summary.csv`.
- Figure 4.3 uses group-level nDCG@10 from `baseline_metrics_by_group.csv`.
- Figure 4.6 uses core vector/vector_metadata/hybrid metrics and `full_kg_no_intent` from `kg_ablation_metrics_summary.csv`.
- Figure 4.7 computes document fact coverage from `kg_sync_138docs_fact_coverage.csv` and runtime contribution from `kg_runtime_contribution_summary_138docs.csv`.
- Figure 4.8 uses `kg_ablation_metrics_summary.csv`.
- Figure 4.9 uses `hybrid_candidate_fusion_metrics_summary.csv`; candidate fusion is below hybrid in the final rerun.
- Figure 4.10 uses `baseline_metrics_summary_extended.csv` for the 96-query extended evaluation and keeps the main plot readable with four methods.

## Audit Outputs

- File validation: `outputs/figures_update_138docs_file_validation.csv`
- Data validation: `outputs/figures_update_138docs_data_validation.csv`
- Source value check: `outputs/figures_update_138docs_source_value_check.csv`
- Caption mapping: `outputs/chapter4_figure_caption_to_file_mapping_138docs.csv`
- Summary CSV: `outputs/figures_update_138docs_summary.csv`

## Stale/Future Work Figures

Query expansion figures were archived and not regenerated as final Chapter 4 figures because query expansion has not been rerun on the 138-doc snapshot.
