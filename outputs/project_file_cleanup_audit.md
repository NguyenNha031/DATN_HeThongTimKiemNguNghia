# Project File Cleanup Audit

Generated at: `2026-05-27T22:08:33`

## 1. Executive summary

- Total files reviewed: **386**
- KEEP_FINAL: **21**
- KEEP_SUPPORTING: **81**
- ARCHIVE_CANDIDATE: **123**
- ASK_BEFORE_ARCHIVE: **30**
- NEVER_TOUCH: **131**
- Note: expected file name(s) not found during audit: `data/eval/metrics/baseline_metrics_by_query.csv`. Current equivalent kept: `data/eval/metrics/baseline_metrics_per_query.csv`.

Scope: `.git`, `.venv`, `venv`, `env`, and `node_modules` were excluded. No experiment was rerun.

## 2. KEEP FINAL list

| path | reason | confidence | superseded_by | size_bytes | modified_time |
|---|---|---|---|---:|---|
| `data/eval/metrics/baseline_latency_per_query.csv` | Current final report/figure/metric artifact used for the main submission package. | high |  | 4892 | 2026-05-09T15:36:57 |
| `data/eval/metrics/baseline_metrics_per_query.csv` | Current final report/figure/metric artifact used for the main submission package. | high |  | 31548 | 2026-05-21T19:40:22 |
| `outputs/figures/fig_ablation_key_metrics.pdf` | Current final report/figure/metric artifact used for the main submission package. | high |  | 25629 | 2026-05-26T19:53:52 |
| `outputs/figures/fig_ablation_key_metrics.png` | Current final report/figure/metric artifact used for the main submission package. | high |  | 216020 | 2026-05-26T19:53:51 |
| `outputs/figures/fig_baseline_key_metrics.pdf` | Current final report/figure/metric artifact used for the main submission package. | high |  | 24211 | 2026-05-26T19:49:46 |
| `outputs/figures/fig_baseline_key_metrics.png` | Current final report/figure/metric artifact used for the main submission package. | high |  | 190013 | 2026-05-26T19:49:45 |
| `outputs/figures/fig_candidate_fusion_summary.png` | Current final report/figure/metric artifact used for the main submission package. | high |  | 159510 | 2026-05-27T09:55:27 |
| `outputs/figures/fig_extended_evaluation_summary.png` | Current final report/figure/metric artifact used for the main submission package. | high |  | 183330 | 2026-05-27T10:22:26 |
| `outputs/figures/fig_hybrid_vs_vector_metadata_by_group.pdf` | Current final report/figure/metric artifact used for the main submission package. | high |  | 25209 | 2026-05-26T19:52:25 |
| `outputs/figures/fig_hybrid_vs_vector_metadata_by_group.png` | Current final report/figure/metric artifact used for the main submission package. | high |  | 165347 | 2026-05-26T19:52:24 |
| `outputs/figures/fig_kg_ablation_summary.png` | Current final report/figure/metric artifact used for the main submission package. | high |  | 175540 | 2026-05-27T10:41:18 |
| `outputs/figures/fig_kg_runtime_contribution_summary.png` | Current final report/figure/metric artifact used for the main submission package. | high |  | 245471 | 2026-05-27T18:13:39 |
| `outputs/figures/fig_kg_score_components.png` | Current final report/figure/metric artifact used for the main submission package. | high |  | 136658 | 2026-05-27T10:34:08 |
| `outputs/figures/fig_quality_latency_tradeoff.pdf` | Current final report/figure/metric artifact used for the main submission package. | high |  | 24883 | 2026-05-26T19:55:00 |
| `outputs/figures/fig_quality_latency_tradeoff.png` | Current final report/figure/metric artifact used for the main submission package. | high |  | 149441 | 2026-05-27T17:41:58 |
| `outputs/figures/fig_query_expansion_examples.png` | Current final report/figure/metric artifact used for the main submission package. | high |  | 190973 | 2026-05-27T10:50:20 |
| `outputs/final_score_formula_and_runtime_flow.md` | Current final report/figure/metric artifact used for the main submission package. | high |  | 4268 | 2026-05-25T19:37:14 |
| `outputs/final_submission_file_checklist.md` | Current final report/figure/metric artifact used for the main submission package. | high |  | 8973 | 2026-05-25T19:39:25 |
| `outputs/hybrid_vs_vector_metadata_by_group.csv` | Current final report/figure/metric artifact used for the main submission package. | high |  | 1059 | 2026-05-25T19:05:27 |
| `outputs/hybrid_vs_vector_metadata_by_group.md` | Current final report/figure/metric artifact used for the main submission package. | high |  | 1725 | 2026-05-25T19:05:27 |
| `README.md` | Current final report/figure/metric artifact used for the main submission package. | high |  | 1781 | 2026-05-18T19:15:00 |

## 3. KEEP SUPPORTING list

| path | reason | confidence | superseded_by | size_bytes | modified_time |
|---|---|---|---|---:|---|
| `analyze_query_understanding_profiles.py` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 20895 | 2026-05-23T23:31:02 |
| `data/eval/analysis/baseline_strengths_by_group.csv` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 629 | 2026-05-03T14:48:19 |
| `data/eval/analysis/error_analysis_and_final_improvement_plan.md` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 15757 | 2026-05-03T14:49:00 |
| `data/eval/analysis/final_technical_iteration_report.md` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 6781 | 2026-05-03T15:29:00 |
| `data/eval/analysis/query_failure_buckets.csv` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 1176 | 2026-05-03T14:48:21 |
| `data/eval/competency_questions_core.csv` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 2215 | 2026-05-21T19:49:53 |
| `data/eval/final_active_files_manifest.csv` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 3595 | 2026-05-03T16:16:18 |
| `data/eval/final_freeze_report.md` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 5547 | 2026-05-09T15:38:00 |
| `data/eval/final_query_set_extended.csv` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 39613 | 2026-05-27T10:12:35 |
| `data/eval/final_query_set_notes.md` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 3632 | 2026-05-03T13:29:23 |
| `data/eval/metrics/baseline_metrics_by_group_extended.csv` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 6128 | 2026-05-27T10:15:54 |
| `data/eval/metrics/baseline_metrics_by_group_plus.csv` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 5336 | 2026-05-27T10:24:50 |
| `data/eval/metrics/baseline_metrics_by_query_extended.csv` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 114008 | 2026-05-27T10:15:54 |
| `data/eval/metrics/baseline_metrics_by_query_plus.csv` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 31956 | 2026-05-27T10:24:50 |
| `data/eval/metrics/baseline_metrics_summary_extended.csv` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 1189 | 2026-05-27T10:15:54 |
| `data/eval/metrics/baseline_metrics_summary_plus.csv` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 1217 | 2026-05-27T10:24:50 |
| `data/eval/metrics/compute_core_metrics.py` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 14098 | 2026-05-21T19:42:21 |
| `data/eval/metrics/hybrid_candidate_fusion_metrics_by_group.csv` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 2841 | 2026-05-27T09:51:58 |
| `data/eval/metrics/hybrid_candidate_fusion_metrics_by_query.csv` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 16639 | 2026-05-27T09:51:58 |
| `data/eval/metrics/hybrid_candidate_fusion_metrics_summary.csv` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 650 | 2026-05-27T09:51:58 |
| `data/eval/metrics/kg_ablation_metrics_by_group.csv` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 4836 | 2026-05-27T10:41:17 |
| `data/eval/metrics/kg_ablation_metrics_by_query.csv` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 27789 | 2026-05-27T10:41:17 |
| `data/eval/metrics/kg_ablation_metrics_summary.csv` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 999 | 2026-05-27T10:41:17 |
| `data/eval/metrics/metrics_notes.md` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 10637 | 2026-05-05T18:42:47 |
| `data/eval/project_final_readiness_check.md` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 4038 | 2026-05-11T19:55:57 |
| `data/eval/relevance_guidelines_core.md` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 8769 | 2026-05-12T20:41:10 |
| `data/eval/relevance_judgments_core_summary.md` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 1204 | 2026-05-03T13:58:19 |
| `data/eval/relevance_judgments_extended.csv` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 1250368 | 2026-05-27T10:15:54 |
| `data/eval/results/baseline_hybrid_candidate_fusion_core.csv` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 259666 | 2026-05-27T09:51:58 |
| `data/eval/results/baseline_hybrid_candidate_fusion_extended.csv` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 894380 | 2026-05-27T10:15:43 |
| `data/eval/results/baseline_hybrid_extended.csv` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 344465 | 2026-05-27T10:15:43 |
| `data/eval/results/baseline_lexical_extended.csv` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 351784 | 2026-05-27T10:15:43 |
| `data/eval/results/baseline_ontology_sparql_extended.csv` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 359839 | 2026-05-27T10:15:43 |
| `data/eval/results/baseline_vector_extended.csv` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 385730 | 2026-05-27T10:15:43 |
| `data/eval/results/baseline_vector_metadata_extended.csv` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 389358 | 2026-05-27T10:15:43 |
| `data/eval/results/baseline_vector_metadata_kg_no_intent_core.csv` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 135000 | 2026-05-21T19:40:11 |
| `data/eval/results/kg_ablation_results_core.csv` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 569320 | 2026-05-27T10:41:17 |
| `data/eval/results/results_generation_notes.md` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 3510 | 2026-05-09T15:33:31 |
| `evaluate_competency_questions.py` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 10792 | 2026-05-21T19:50:58 |
| `experiments/analyze_kg_score_components.py` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 25036 | 2026-05-27T10:33:48 |
| `experiments/compute_baseline_metrics_plus.py` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 12110 | 2026-05-27T10:24:41 |
| `experiments/generate_query_expansion_examples.py` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 39638 | 2026-05-27T10:49:59 |
| `experiments/run_extended_evaluation.py` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 81344 | 2026-05-27T10:12:16 |
| `experiments/run_hybrid_candidate_fusion.py` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 27908 | 2026-05-27T09:51:01 |
| `experiments/run_kg_ablation.py` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 23839 | 2026-05-27T10:41:04 |
| `generate_error_analysis_core.py` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 10660 | 2026-05-21T19:59:22 |
| `generate_evaluation_layers_summary.py` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 19879 | 2026-05-23T23:13:19 |
| `measure_core_baseline_latency.py` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 9022 | 2026-05-21T19:38:58 |
| `outputs/baseline_metrics_plus_report.md` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 1875 | 2026-05-27T10:24:50 |
| `outputs/competency_questions_results.csv` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 22520 | 2026-05-21T19:51:13 |
| `outputs/competency_questions_summary.json` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 1285 | 2026-05-21T19:51:13 |
| `outputs/document_fact_coverage_audit.csv` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 29718 | 2026-04-25T21:58:35 |
| `outputs/document_fact_coverage_audit.json` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 101245 | 2026-04-25T21:58:35 |
| `outputs/error_analysis_core.csv` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 8987 | 2026-05-21T20:00:28 |
| `outputs/error_analysis_summary.json` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 619 | 2026-05-21T20:00:28 |
| `outputs/evaluation_layers_summary.json` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 28227 | 2026-05-23T23:13:33 |
| `outputs/evaluation_layers_summary.md` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 8041 | 2026-05-23T23:13:33 |
| `outputs/extended_query_evaluation_report.md` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 5464 | 2026-05-27T10:15:54 |
| `outputs/extended_query_judgment_audit.md` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 1392 | 2026-05-27T10:15:54 |
| `outputs/hybrid_candidate_fusion_analysis.md` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 4255 | 2026-05-27T09:51:58 |
| `outputs/kg_ablation_analysis.md` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 4818 | 2026-05-27T10:41:18 |
| `outputs/kg_runtime_verification.json` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 23455 | 2026-05-09T15:27:35 |
| `outputs/kg_score_component_analysis.csv` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 212887 | 2026-05-27T10:34:08 |
| `outputs/kg_score_component_analysis.md` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 6222 | 2026-05-27T10:34:08 |
| `outputs/ontology_quality_check.json` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 3759 | 2026-05-21T20:02:15 |
| `outputs/ontology_quality_check.md` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 2652 | 2026-05-23T00:58:33 |
| `outputs/ontology_reasoner_consistency_check.json` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 6204 | 2026-05-23T23:07:27 |
| `outputs/ontology_reasoner_consistency_check.md` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 2807 | 2026-05-23T23:07:27 |
| `outputs/query_expansion_design.md` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 7330 | 2026-05-27T10:50:20 |
| `outputs/query_expansion_examples.csv` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 61704 | 2026-05-27T10:50:20 |
| `outputs/query_understanding_profiles.csv` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 14799 | 2026-05-23T23:31:44 |
| `outputs/query_understanding_profiles.json` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 41738 | 2026-05-23T23:31:44 |
| `outputs/query_understanding_profiles.md` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 9673 | 2026-05-23T23:31:44 |
| `outputs/streamlit_demo_notes.md` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 1419 | 2026-05-25T19:05:27 |
| `outputs/wilcoxon_hybrid_vs_vector_metadata.csv` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 1146 | 2026-05-23T22:51:30 |
| `outputs/wilcoxon_hybrid_vs_vector_metadata.json` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 3481 | 2026-05-23T22:51:30 |
| `outputs/wilcoxon_hybrid_vs_vector_metadata.md` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 2285 | 2026-05-23T22:51:30 |
| `run_wilcoxon_significance_test.py` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 14551 | 2026-05-23T22:52:16 |
| `verify_kg_runtime.py` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 11289 | 2026-04-25T20:35:35 |
| `verify_ontology_quality.py` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 15245 | 2026-05-21T20:02:09 |
| `verify_ontology_reasoner_consistency.py` | Supporting experiment, verification, evaluation, or reproducibility artifact worth retaining outside the main final core. | high |  | 18133 | 2026-05-23T23:07:18 |

## 4. ARCHIVE CANDIDATE list

| path | reason | confidence | superseded_by | size_bytes | modified_time |
|---|---|---|---|---:|---|
| `__pycache__/analyze_ontology_alias_gaps.cpython-313.pyc` | Generated Python cache artifact, safe to exclude/archive from final package. | high |  | 13956 | 2026-03-26T19:49:22 |
| `__pycache__/audit_document_fact_coverage.cpython-313.pyc` | Generated Python cache artifact, safe to exclude/archive from final package. | high |  | 18052 | 2026-03-26T20:03:51 |
| `__pycache__/backfill_document_facts_from_metadata.cpython-313.pyc` | Generated Python cache artifact, safe to exclude/archive from final package. | high |  | 13305 | 2026-03-26T20:50:48 |
| `__pycache__/enrich_ontology_aliases.cpython-313.pyc` | Generated Python cache artifact, safe to exclude/archive from final package. | high |  | 8524 | 2026-03-26T19:49:22 |
| `__pycache__/hybrid_search.cpython-313.pyc` | Generated Python cache artifact, safe to exclude/archive from final package. | high |  | 71821 | 2026-05-23T23:22:43 |
| `__pycache__/kg_runtime.cpython-313.pyc` | Generated Python cache artifact, safe to exclude/archive from final package. | high |  | 42666 | 2026-04-18T12:40:13 |
| `__pycache__/run_core_baselines.cpython-313.pyc` | Generated Python cache artifact, safe to exclude/archive from final package. | high |  | 30524 | 2026-05-23T23:23:19 |
| `__pycache__/semantic_normalization.cpython-313.pyc` | Generated Python cache artifact, safe to exclude/archive from final package. | high |  | 5422 | 2026-04-01T20:42:02 |
| `__pycache__/sync_metadata_to_owl.cpython-313.pyc` | Generated Python cache artifact, safe to exclude/archive from final package. | high |  | 19072 | 2026-03-30T21:52:29 |
| `__pycache__/vector_search.cpython-313.pyc` | Generated Python cache artifact, safe to exclude/archive from final package. | high |  | 13128 | 2026-05-23T23:22:43 |
| `__pycache__/verify_kg_runtime.cpython-313.pyc` | Generated Python cache artifact, safe to exclude/archive from final package. | high |  | 13003 | 2026-04-18T12:40:13 |
| `build_imn_lobster_comparison.py` | Old IMN/lobster comparison helper tied to archived snapshots/reports. | high | outputs/archive/old_reports/imn_lobster_fix_report.md | 5272 | 2026-04-05T23:36:32 |
| `build_weak_query_comparison.py` | Old weak-query comparison helper tied to archived snapshots/reports. | high | outputs/archive/old_reports/focus_two_weak_queries_report.md | 4140 | 2026-04-05T23:06:29 |
| `capture_focus_two_queries.py` | Old query-capture/debug helper tied to archived focus-query snapshots. | high | outputs/archive/old_reports/focus_two_weak_queries_report.md | 2600 | 2026-04-12T21:39:29 |
| `capture_focus_two_queries_round2.py` | Old round-2 query-capture helper tied to archived focus-query snapshots. | high | outputs/archive/old_reports/focus_two_weak_queries_report_round2.md | 2892 | 2026-04-13T18:40:33 |
| `capture_weak_queries.py` | Old query-capture/debug helper tied to archived weak-query snapshots. | high | outputs/archive/old_snapshots/weak_query_fix_comparison.json | 4210 | 2026-04-05T23:06:29 |
| `data/metadata/archive/document_metadata.xlsx.bak_20260330_212917` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 21611 | 2026-03-22T20:45:39 |
| `data/metadata/archive/document_metadata_cleaned_before_round2A.xlsx` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 42059 | 2026-04-18T22:07:17 |
| `data/metadata/archive/document_metadata_cleaned_before_round4.xlsx` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 42059 | 2026-04-18T22:07:17 |
| `data/ontology/archive/manual_cleanup_202606/mapping_report_round8_facts_v2.csv` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 155867 | 2026-04-18T23:12:44 |
| `data/ontology/archive/manual_cleanup_202606/mapping_report_round8_taxonowl.csv` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 151474 | 2026-04-18T23:12:37 |
| `data/ontology/archive/manual_cleanup_202606/taxon.owl.bak_20260418_231237` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 67767 | 2026-04-18T23:08:13 |
| `data/ontology/archive/manual_cleanup_202606/taxon.owl.bak_round6_location_enrichment` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 64679 | 2026-03-13T16:46:38 |
| `data/ontology/archive/manual_cleanup_202606/taxon.owl.bak_round7_camranh_disambiguation` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 67829 | 2026-04-18T23:05:26 |
| `data/ontology/archive/manual_cleanup_202606/taxon.owl.bak_round8_before_sync` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 67767 | 2026-04-18T23:08:13 |
| `data/ontology/archive/manual_cleanup_202606/taxon_enriched_facts_v2.owl.bak_20260418_231244` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 161367 | 2026-04-18T23:08:19 |
| `data/ontology/archive/manual_cleanup_202606/taxon_enriched_facts_v2.owl.bak_round6_location_enrichment` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 158686 | 2026-04-05T23:27:03 |
| `data/ontology/archive/manual_cleanup_202606/taxon_enriched_facts_v2.owl.bak_round7_camranh_disambiguation` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 161425 | 2026-04-18T23:04:53 |
| `data/ontology/archive/manual_cleanup_202606/taxon_enriched_facts_v2.owl.bak_round8_before_sync` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 161367 | 2026-04-18T23:08:19 |
| `data/ontology/taxon_enriched.owl` | Older ontology enrichment variant; final runtime ontology is taxon_enriched_facts_v2.owl. | medium | data/ontology/taxon_enriched_facts_v2.owl | 141708 | 2026-04-01T20:28:06 |
| `data/ontology/taxon_enriched_aliases.owl` | Older ontology enrichment variant; final runtime ontology is taxon_enriched_facts_v2.owl. | medium | data/ontology/taxon_enriched_facts_v2.owl | 142280 | 2026-04-01T20:41:48 |
| `data/ontology/taxon_enriched_facts.owl` | Older ontology enrichment variant; final runtime ontology is taxon_enriched_facts_v2.owl. | medium | data/ontology/taxon_enriched_facts_v2.owl | 142693 | 2026-04-01T20:44:47 |
| `data/ontology/taxon_enriched_semantic.owl` | Older ontology enrichment variant; final runtime ontology is taxon_enriched_facts_v2.owl. | medium | data/ontology/taxon_enriched_facts_v2.owl | 145327 | 2026-04-01T20:42:03 |
| `dump_six_queries.py` | Old manual query dump/debug helper, not part of final evaluation pipeline. | high | data/eval/final_query_set_core.csv | 3627 | 2026-04-05T23:06:29 |
| `hybrid_comparison.csv` | Old ad hoc hybrid comparison output, outside final evaluation layout. | high | data/eval/results/baseline_hybrid_core.csv | 56970 | 2026-04-20T21:16:13 |
| `hybrid_results.txt` | Old text dump of hybrid results, superseded by structured core/extended CSV outputs. | high | data/eval/results/baseline_hybrid_core.csv | 106904 | 2026-04-27T16:00:37 |
| `metadata_snapshot.txt` | Large metadata snapshot/debug artifact, not part of final runtime or report package. | high | data/metadata/document_metadata_cleaned.xlsx | 197582 | 2026-05-27T09:59:59 |
| `outputs/archive/manual_cleanup_202606/tmp_tb007_debug.json` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 1972 | 2026-04-25T21:15:08 |
| `outputs/archive/old_outputs/added_triples_grouped_summary.json` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 6799 | 2026-03-29T15:50:59 |
| `outputs/archive/old_outputs/added_triples_sample.json` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 29461 | 2026-03-26T21:03:50 |
| `outputs/archive/old_outputs/alias_metadata_noise_audit.json` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 32711 | 2026-03-30T21:27:51 |
| `outputs/archive/old_outputs/alias_metadata_noise_audit_top_terms.csv` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 4799 | 2026-03-30T21:27:51 |
| `outputs/archive/old_outputs/document_fact_backfill_report.csv` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 37466 | 2026-04-01T20:42:26 |
| `outputs/archive/old_outputs/document_fact_backfill_report.json` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 71914 | 2026-04-01T20:42:26 |
| `outputs/archive/old_outputs/document_fact_backfill_report_facts.csv` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 32969 | 2026-04-01T20:44:47 |
| `outputs/archive/old_outputs/document_fact_backfill_report_facts.json` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 67418 | 2026-04-01T20:44:47 |
| `outputs/archive/old_outputs/document_fact_coverage_audit.csv` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 27948 | 2026-04-01T20:42:18 |
| `outputs/archive/old_outputs/document_fact_coverage_audit.json` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 92442 | 2026-04-01T20:42:18 |
| `outputs/archive/old_outputs/document_fact_coverage_audit_after_fact_backfill.csv` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 11091 | 2026-03-26T20:04:43 |
| `outputs/archive/old_outputs/document_fact_coverage_audit_after_fact_backfill.json` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 39376 | 2026-03-26T20:04:43 |
| `outputs/archive/old_outputs/document_fact_coverage_audit_after_semantic_backfill.csv` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 10666 | 2026-03-26T20:51:44 |
| `outputs/archive/old_outputs/document_fact_coverage_audit_after_semantic_backfill.json` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 38489 | 2026-03-26T20:51:44 |
| `outputs/archive/old_outputs/document_fact_coverage_audit_alias.csv` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 27853 | 2026-04-01T20:44:36 |
| `outputs/archive/old_outputs/document_fact_coverage_audit_alias.json` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 93396 | 2026-04-01T20:44:36 |
| `outputs/archive/old_outputs/document_fact_coverage_audit_before_fact_backfill.csv` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 11091 | 2026-03-26T19:59:53 |
| `outputs/archive/old_outputs/document_fact_coverage_audit_before_fact_backfill.json` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 39378 | 2026-03-26T19:59:53 |
| `outputs/archive/old_outputs/full_corpus_metadata_audit.json` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 11451 | 2026-04-01T20:10:35 |
| `outputs/archive/old_outputs/full_corpus_metadata_audit_summary.csv` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 386 | 2026-04-01T20:10:35 |
| `outputs/archive/old_outputs/full_corpus_metadata_cleanup_effect_summary.json` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 354 | 2026-04-01T20:12:03 |
| `outputs/archive/old_outputs/full_corpus_metadata_cleanup_report.csv` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 2850 | 2026-04-01T20:12:03 |
| `outputs/archive/old_outputs/full_corpus_metadata_cleanup_report.json` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 78337 | 2026-04-01T20:12:03 |
| `outputs/archive/old_outputs/full_corpus_pipeline_summary.json` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 15087 | 2026-04-01T20:31:36 |
| `outputs/archive/old_outputs/metadata_cleanup_effect_summary.json` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 104 | 2026-03-30T21:35:35 |
| `outputs/archive/old_outputs/metadata_cleanup_report.csv` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 7151 | 2026-03-30T21:29:17 |
| `outputs/archive/old_outputs/metadata_cleanup_report.json` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 34966 | 2026-03-30T21:29:17 |
| `outputs/archive/old_outputs/metadata_normalization_report.csv` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 46476 | 2026-04-01T20:44:47 |
| `outputs/archive/old_outputs/metadata_normalization_report.json` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 101026 | 2026-04-01T20:44:47 |
| `outputs/archive/old_outputs/new_or_used_generic_entities_review.json` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 4058 | 2026-03-26T21:03:51 |
| `outputs/archive/old_outputs/ontology_alias_added.json` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 3178 | 2026-04-01T20:41:48 |
| `outputs/archive/old_outputs/ontology_alias_gap_report.csv` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 7247 | 2026-03-26T19:46:54 |
| `outputs/archive/old_outputs/ontology_alias_gap_report.json` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 32392 | 2026-03-26T19:46:54 |
| `outputs/archive/old_outputs/pipeline_run_query_summary.json` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 3825 | 2026-03-30T22:12:10 |
| `outputs/archive/old_outputs/post_clean_metadata_cleanup_report.json` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 527 | 2026-03-30T21:50:46 |
| `outputs/archive/old_outputs/semantic_backfill_false_positive_review.json` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 28046 | 2026-03-26T21:03:51 |
| `outputs/archive/old_reports/cursor_fix_report.md` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 7627 | 2026-04-05T23:06:29 |
| `outputs/archive/old_reports/focus_two_weak_queries_report.md` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 5633 | 2026-04-12T22:17:17 |
| `outputs/archive/old_reports/focus_two_weak_queries_report_round2.md` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 4855 | 2026-04-13T18:44:59 |
| `outputs/archive/old_reports/imn_lobster_fix_report.md` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 8937 | 2026-04-05T23:37:38 |
| `outputs/archive/old_snapshots/focus_two_queries_after.json` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 4549 | 2026-04-12T22:12:51 |
| `outputs/archive/old_snapshots/focus_two_queries_before.json` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 4620 | 2026-04-12T21:42:08 |
| `outputs/archive/old_snapshots/focus_two_queries_metrics.json` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 4549 | 2026-04-12T22:12:51 |
| `outputs/archive/old_snapshots/focus_two_queries_round2_after.json` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 4549 | 2026-04-13T18:42:17 |
| `outputs/archive/old_snapshots/focus_two_queries_round2_before.json` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 4549 | 2026-04-13T18:41:03 |
| `outputs/archive/old_snapshots/imn_lobster_after.json` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 16155 | 2026-04-05T23:35:04 |
| `outputs/archive/old_snapshots/imn_lobster_before.json` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 16173 | 2026-04-05T23:25:48 |
| `outputs/archive/old_snapshots/imn_lobster_comparison.json` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 32472 | 2026-04-05T23:36:45 |
| `outputs/archive/old_snapshots/weak_query_fix_after.json` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 15452 | 2026-04-05T14:14:31 |
| `outputs/archive/old_snapshots/weak_query_fix_before.json` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 15444 | 2026-04-05T23:06:29 |
| `outputs/archive/old_snapshots/weak_query_fix_comparison.json` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 29434 | 2026-04-05T14:14:32 |
| `outputs/archive/old_verification/alias_metadata_cleanup_query_verification.json` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 17119 | 2026-03-30T22:13:01 |
| `outputs/archive/old_verification/disease_priority_queries_verification.json` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 10055 | 2026-03-30T21:16:43 |
| `outputs/archive/old_verification/disease_priority_queries_verification_after_canonical_bridge.json` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 9942 | 2026-03-30T21:16:24 |
| `outputs/archive/old_verification/disease_priority_queries_verification_after_tightening.json` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 9645 | 2026-03-30T21:11:19 |
| `outputs/archive/old_verification/disease_priority_queries_verification_before_tightening.json` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 9645 | 2026-03-30T21:10:23 |
| `outputs/archive/old_verification/full_corpus_query_verification.json` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 13615 | 2026-04-05T14:12:40 |
| `outputs/archive/old_verification/kg_runtime_verification_after_canonical_bridge.json` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 18399 | 2026-03-30T21:16:24 |
| `outputs/archive/old_verification/kg_runtime_verification_after_disease_tightening.json` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 18083 | 2026-03-30T21:11:19 |
| `outputs/archive/old_verification/kg_runtime_verification_before_alias_enrichment.json` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 17173 | 2026-03-26T19:35:11 |
| `outputs/archive/old_verification/kg_runtime_verification_before_disease_tightening.json` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 18083 | 2026-03-30T20:42:58 |
| `outputs/archive/old_verification/kg_runtime_verification_before_fact_backfill.json` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 18082 | 2026-03-26T19:48:48 |
| `outputs/archive/old_verification/kg_runtime_verification_before_semantic_backfill.json` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 18080 | 2026-03-26T20:04:26 |
| `outputs/archive/old_verification/kg_runtime_verification_semantic_patch_expanded.json` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 81634 | 2026-03-26T21:04:09 |
| `outputs/archive/old_verification/kg_runtime_verification_semantic_patch_summary.json` | Already located under an archive folder; keep excluded from the final submission package, no move/delete performed. | high |  | 8855 | 2026-03-26T21:04:09 |
| `outputs/candidate_fusion_experiment_summary.csv` | Earlier candidate-fusion summary table, superseded by current metrics CSVs. | high | data/eval/metrics/hybrid_candidate_fusion_metrics_summary.csv | 520 | 2026-05-23T23:25:47 |
| `outputs/candidate_fusion_experiment_summary.json` | Earlier candidate-fusion JSON summary, superseded by current metrics/report artifacts. | high | outputs/hybrid_candidate_fusion_analysis.md | 8642 | 2026-05-23T23:25:47 |
| `outputs/candidate_fusion_experiment_summary.md` | Earlier candidate-fusion summary, superseded by current hybrid_candidate_fusion_analysis.md. | high | outputs/hybrid_candidate_fusion_analysis.md | 3513 | 2026-05-23T23:25:47 |
| `outputs/candidate_fusion_per_query_delta.csv` | Earlier candidate-fusion per-query delta, superseded by current by-query metrics. | high | data/eval/metrics/hybrid_candidate_fusion_metrics_by_query.csv | 4152 | 2026-05-23T23:25:47 |
| `outputs/document_fact_backfill_report.csv` | Backfill-generation report; final coverage audit and final ontology are the current evidence. | high | outputs/document_fact_coverage_audit.json | 16159 | 2026-04-20T20:59:49 |
| `outputs/document_fact_backfill_report.json` | Backfill-generation report; final coverage audit and final ontology are the current evidence. | high | outputs/document_fact_coverage_audit.json | 32666 | 2026-04-20T20:59:49 |
| `outputs/metadata_normalization_report.csv` | Intermediate metadata normalization report; cleaned metadata XLSX is final. | high | data/metadata/document_metadata_cleaned.xlsx | 18236 | 2026-04-20T20:59:49 |
| `outputs/metadata_normalization_report.json` | Intermediate metadata normalization report; cleaned metadata XLSX is final. | high | data/metadata/document_metadata_cleaned.xlsx | 44426 | 2026-04-20T20:59:49 |
| `outputs/semantic_patch_final_assessment.md` | Old semantic patch assessment; final ontology/runtime checks are newer and source-of-truth remains data/ontology/taxon_enriched_facts_v2.owl. | high | outputs/ontology_quality_check.md | 1480 | 2026-03-28T14:59:31 |
| `outputs/taxon_enriched_facts_v2_backfilled_runtime.owl` | Experimental backfilled runtime ontology; final runtime ontology is in data/ontology/. | high | data/ontology/taxon_enriched_facts_v2.owl | 179851 | 2026-04-20T20:59:49 |
| `run_candidate_fusion_experiment.py` | Earlier candidate-fusion runner at project root; newer experiment script is under experiments/. | high | experiments/run_hybrid_candidate_fusion.py | 32842 | 2026-05-23T23:24:45 |
| `vector_store_backup_round10/chunks.index` | Backup vector index directory; current runtime uses vector_store/ and backups are large historical artifacts. | high | vector_store/ | 38518317 | 2026-04-01T20:25:46 |
| `vector_store_backup_round10/chunks_meta.pkl` | Backup vector index directory; current runtime uses vector_store/ and backups are large historical artifacts. | high | vector_store/ | 21633189 | 2026-04-01T20:25:46 |
| `vector_store_backup_round10/config.pkl` | Backup vector index directory; current runtime uses vector_store/ and backups are large historical artifacts. | high | vector_store/ | 90 | 2026-04-01T20:25:46 |
| `vector_store_backup_round11_after_tb_fix/chunks.index` | Backup vector index directory; current runtime uses vector_store/ and backups are large historical artifacts. | high | vector_store/ | 39075885 | 2026-04-18T23:44:53 |
| `vector_store_backup_round11_after_tb_fix/chunks_meta.pkl` | Backup vector index directory; current runtime uses vector_store/ and backups are large historical artifacts. | high | vector_store/ | 22023357 | 2026-04-18T23:44:53 |
| `vector_store_backup_round11_after_tb_fix/config.pkl` | Backup vector index directory; current runtime uses vector_store/ and backups are large historical artifacts. | high | vector_store/ | 90 | 2026-04-18T23:44:53 |
| `vector_store_backup_round12_after_ria3_fix/chunks.index` | Backup vector index directory; current runtime uses vector_store/ and backups are large historical artifacts. | high | vector_store/ | 38694957 | 2026-04-19T00:30:43 |
| `vector_store_backup_round12_after_ria3_fix/chunks_meta.pkl` | Backup vector index directory; current runtime uses vector_store/ and backups are large historical artifacts. | high | vector_store/ | 21754021 | 2026-04-19T00:30:44 |
| `vector_store_backup_round12_after_ria3_fix/config.pkl` | Backup vector index directory; current runtime uses vector_store/ and backups are large historical artifacts. | high | vector_store/ | 90 | 2026-04-19T00:30:44 |

## 5. ASK BEFORE ARCHIVE list

| path | reason | confidence | superseded_by | size_bytes | modified_time |
|---|---|---|---|---:|---|
| `.vscode/settings.json` | Local IDE configuration; not needed for final package but ask before archiving local setup files. | medium |  | 68 | 2026-03-12T19:06:20 |
| `analyze_ontology_alias_gaps.py` | One-off metadata/ontology cleanup or verification script; likely not in final package, but may be needed for provenance/regeneration. | medium | data/ontology/taxon_enriched_facts_v2.owl; data/metadata/document_metadata_cleaned.xlsx | 12496 | 2026-03-26T19:46:46 |
| `audit_alias_and_metadata_noise.py` | One-off metadata/ontology cleanup or verification script; likely not in final package, but may be needed for provenance/regeneration. | medium | data/ontology/taxon_enriched_facts_v2.owl; data/metadata/document_metadata_cleaned.xlsx | 6275 | 2026-03-30T22:03:33 |
| `audit_document_fact_coverage.py` | One-off metadata/ontology cleanup or verification script; likely not in final package, but may be needed for provenance/regeneration. | medium | data/ontology/taxon_enriched_facts_v2.owl; data/metadata/document_metadata_cleaned.xlsx | 15085 | 2026-04-01T20:41:17 |
| `backfill_document_facts_from_metadata.py` | One-off metadata/ontology cleanup or verification script; likely not in final package, but may be needed for provenance/regeneration. | medium | data/ontology/taxon_enriched_facts_v2.owl; data/metadata/document_metadata_cleaned.xlsx | 14798 | 2026-04-01T20:41:26 |
| `clean_metadata_for_entity_matching.py` | One-off metadata/ontology cleanup or verification script; likely not in final package, but may be needed for provenance/regeneration. | medium | data/ontology/taxon_enriched_facts_v2.owl; data/metadata/document_metadata_cleaned.xlsx | 10137 | 2026-03-30T22:03:33 |
| `compute_core_metrics.py` | Root-level stub/placeholder; real metric implementation is under data/eval/metrics, but checklist mentions this path. | medium | data/eval/metrics/compute_core_metrics.py | 240 | 2026-05-18T19:14:59 |
| `data/eval/final_query_set.csv` | Older/general query-set file; core and extended sets are current, but confirm before archiving. | medium | data/eval/final_query_set_core.csv; data/eval/final_query_set_extended.csv | 16088 | 2026-05-03T13:29:13 |
| `data/metadata/document_metadata.xlsx` | Original metadata workbook; cleaned workbook is final, but original source should be confirmed before archiving. | medium | data/metadata/document_metadata_cleaned.xlsx | 21611 | 2026-03-22T20:45:39 |
| `data/ontology/mapping_report.csv` | Ontology mapping/provenance report may still be useful; ask before archiving. | medium | data/ontology/taxon_enriched_facts_v2.owl | 135182 | 2026-04-01T20:28:06 |
| `data/ontology/taxon.owl` | Base ontology source may be needed for provenance/regeneration; ask before archiving. | medium | data/ontology/taxon_enriched_facts_v2.owl | 155078 | 2026-04-18T23:12:37 |
| `enrich_ontology_aliases.py` | One-off metadata/ontology cleanup or verification script; likely not in final package, but may be needed for provenance/regeneration. | medium | data/ontology/taxon_enriched_facts_v2.owl; data/metadata/document_metadata_cleaned.xlsx | 6010 | 2026-03-26T19:47:46 |
| `enrich_ontology_semantic_entities.py` | One-off metadata/ontology cleanup or verification script; likely not in final package, but may be needed for provenance/regeneration. | medium | data/ontology/taxon_enriched_facts_v2.owl; data/metadata/document_metadata_cleaned.xlsx | 7025 | 2026-04-01T20:41:13 |
| `full_corpus_metadata_audit.py` | One-off metadata/ontology cleanup or verification script; likely not in final package, but may be needed for provenance/regeneration. | medium | data/ontology/taxon_enriched_facts_v2.owl; data/metadata/document_metadata_cleaned.xlsx | 8304 | 2026-04-01T20:09:57 |
| `full_corpus_metadata_cleanup.py` | One-off metadata/ontology cleanup or verification script; likely not in final package, but may be needed for provenance/regeneration. | medium | data/ontology/taxon_enriched_facts_v2.owl; data/metadata/document_metadata_cleaned.xlsx | 12622 | 2026-04-01T20:11:48 |
| `full_corpus_pipeline_summary.py` | One-off metadata/ontology cleanup or verification script; likely not in final package, but may be needed for provenance/regeneration. | medium | data/ontology/taxon_enriched_facts_v2.owl; data/metadata/document_metadata_cleaned.xlsx | 3779 | 2026-04-01T20:31:32 |
| `full_corpus_query_verification.py` | One-off metadata/ontology cleanup or verification script; likely not in final package, but may be needed for provenance/regeneration. | medium | data/ontology/taxon_enriched_facts_v2.owl; data/metadata/document_metadata_cleaned.xlsx | 5086 | 2026-04-01T20:43:43 |
| `generate_semantic_rule_candidates.py` | Semantic-rule prototype generator; unclear whether thesis/future-work section still cites it. | medium | outputs/semantic_rule_candidate_facts.md | 27611 | 2026-05-23T23:40:52 |
| `outputs/figures/fig_hybrid_vector_metadata_delta_by_group.png` | Similar to the final hybrid-vs-vector-metadata group figure but not in the expected final figure list; recently modified, so confirm. | medium | outputs/figures/fig_hybrid_vs_vector_metadata_by_group.png | 227742 | 2026-05-27T17:47:34 |
| `outputs/semantic_rule_candidate_facts.csv` | Large semantic-rule prototype output; confirm whether still cited before archiving. | medium | outputs/semantic_rule_candidate_facts.md | 350130 | 2026-05-23T23:40:58 |
| `outputs/semantic_rule_candidate_facts.json` | Large semantic-rule prototype output; confirm whether still cited before archiving. | medium | outputs/semantic_rule_candidate_facts.md | 707687 | 2026-05-23T23:40:58 |
| `outputs/semantic_rule_candidate_facts.md` | Semantic-rule prototype report; keep only if cited as future work. | medium | outputs/query_expansion_design.md | 6896 | 2026-05-23T23:40:58 |
| `outputs/semantic_rule_scoring_opportunities.csv` | Semantic-rule opportunity table; unclear final use. | medium | outputs/semantic_rule_candidate_facts.md | 2829 | 2026-05-23T23:40:58 |
| `outputs/semantic_rules_and_label_strategy.md` | Semantic-rule/label strategy note; keep only if thesis text still cites this future-work discussion. | medium | outputs/query_expansion_design.md | 17078 | 2026-05-21T20:10:14 |
| `post_clean_metadata_cleanup.py` | One-off metadata/ontology cleanup or verification script; likely not in final package, but may be needed for provenance/regeneration. | medium | data/ontology/taxon_enriched_facts_v2.owl; data/metadata/document_metadata_cleaned.xlsx | 3545 | 2026-03-30T22:03:33 |
| `semantic_normalization.py` | One-off metadata/ontology cleanup or verification script; likely not in final package, but may be needed for provenance/regeneration. | medium | data/ontology/taxon_enriched_facts_v2.owl; data/metadata/document_metadata_cleaned.xlsx | 8261 | 2026-03-30T22:03:33 |
| `sync_metadata_to_owl.py` | One-off metadata/ontology cleanup or verification script; likely not in final package, but may be needed for provenance/regeneration. | medium | data/ontology/taxon_enriched_facts_v2.owl; data/metadata/document_metadata_cleaned.xlsx | 19167 | 2026-04-07T10:36:35 |
| `validate_semantic_patch.py` | One-off metadata/ontology cleanup or verification script; likely not in final package, but may be needed for provenance/regeneration. | medium | data/ontology/taxon_enriched_facts_v2.owl; data/metadata/document_metadata_cleaned.xlsx | 19963 | 2026-03-30T22:03:34 |
| `verify_disease_priority_queries.py` | One-off metadata/ontology cleanup or verification script; likely not in final package, but may be needed for provenance/regeneration. | medium | data/ontology/taxon_enriched_facts_v2.owl; data/metadata/document_metadata_cleaned.xlsx | 3563 | 2026-03-30T22:03:33 |
| `verify_queries_after_alias_metadata_cleanup.py` | One-off metadata/ontology cleanup or verification script; likely not in final package, but may be needed for provenance/regeneration. | medium | data/ontology/taxon_enriched_facts_v2.owl; data/metadata/document_metadata_cleaned.xlsx | 4180 | 2026-03-30T22:03:33 |

## 6. NEVER TOUCH list

| path | reason | confidence | superseded_by | size_bytes | modified_time |
|---|---|---|---|---:|---|
| `.streamlit/config.toml` | Final runtime/evaluation source-of-truth explicitly protected from archive proposals. | high |  | 155 | 2026-05-26T19:01:49 |
| `app_streamlit.py` | Final runtime/evaluation source-of-truth explicitly protected from archive proposals. | high |  | 23890 | 2026-05-26T19:07:44 |
| `data/eval/final_query_set_core.csv` | Final runtime/evaluation source-of-truth explicitly protected from archive proposals. | high |  | 8582 | 2026-05-03T13:29:13 |
| `data/eval/metrics/baseline_latency_summary.csv` | Final runtime/evaluation source-of-truth explicitly protected from archive proposals. | high |  | 2575 | 2026-05-09T15:36:57 |
| `data/eval/metrics/baseline_metrics_by_group.csv` | Final runtime/evaluation source-of-truth explicitly protected from archive proposals. | high |  | 2744 | 2026-05-21T19:40:22 |
| `data/eval/metrics/baseline_metrics_summary.csv` | Final runtime/evaluation source-of-truth explicitly protected from archive proposals. | high |  | 1267 | 2026-05-21T19:40:22 |
| `data/eval/relevance_judgments_core.csv` | Final runtime/evaluation source-of-truth explicitly protected from archive proposals. | high |  | 67133 | 2026-05-03T13:54:14 |
| `data/eval/results/baseline_hybrid_core.csv` | Final runtime/evaluation source-of-truth explicitly protected from archive proposals. | high |  | 102387 | 2026-05-09T15:33:31 |
| `data/eval/results/baseline_lexical_core.csv` | Final runtime/evaluation source-of-truth explicitly protected from archive proposals. | high |  | 103963 | 2026-05-09T15:33:31 |
| `data/eval/results/baseline_ontology_sparql_core.csv` | Final runtime/evaluation source-of-truth explicitly protected from archive proposals. | high |  | 105698 | 2026-05-09T15:33:31 |
| `data/eval/results/baseline_vector_core.csv` | Final runtime/evaluation source-of-truth explicitly protected from archive proposals. | high |  | 113075 | 2026-05-09T15:33:31 |
| `data/eval/results/baseline_vector_metadata_core.csv` | Final runtime/evaluation source-of-truth explicitly protected from archive proposals. | high |  | 115214 | 2026-05-09T15:33:31 |
| `data/metadata/document_metadata_cleaned.xlsx` | Final runtime/evaluation source-of-truth explicitly protected from archive proposals. | high |  | 41497 | 2026-04-19T00:38:00 |
| `data/ontology/taxon_enriched_facts_v2.owl` | Final runtime/evaluation source-of-truth explicitly protected from archive proposals. | high |  | 185160 | 2026-04-25T21:58:26 |
| `data/raw_docs/BIOLOGY_001_biology13100758.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 3656901 | 2026-03-31T21:13:55 |
| `data/raw_docs/FAO_001_cb2119en.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 2837382 | 2026-03-12T15:20:28 |
| `data/raw_docs/FAO_002_a1152e.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 3581648 | 2026-03-12T15:27:31 |
| `data/raw_docs/FAO_003_ca2976en.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 6691426 | 2026-03-12T15:39:10 |
| `data/raw_docs/FAO_004_cc6858en.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 34677269 | 2026-03-12T15:47:08 |
| `data/raw_docs/FAO_005_y5040e.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 392844 | 2026-03-12T17:29:33 |
| `data/raw_docs/FAO_006_bt131e.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 2438802 | 2026-03-18T20:34:34 |
| `data/raw_docs/FAO_007_cd8164en.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 1235572 | 2026-03-18T21:34:19 |
| `data/raw_docs/FAO_008_cb8926en.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 3368163 | 2026-03-18T21:41:17 |
| `data/raw_docs/FAO_009_y1679e.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 3475127 | 2026-03-18T21:39:29 |
| `data/raw_docs/FAO_010_ca6052en.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 2857806 | 2026-03-18T21:44:59 |
| `data/raw_docs/FAO_011_ad824e.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 238076 | 2026-03-18T21:49:09 |
| `data/raw_docs/FAO_012_ad505e.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 672185 | 2026-03-18T21:50:57 |
| `data/raw_docs/FAO_013_y5325e.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 538879 | 2026-03-18T21:53:26 |
| `data/raw_docs/FAO_014_cd8658en.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 409149 | 2026-03-18T22:02:55 |
| `data/raw_docs/FAO_015_t0411e.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 534703 | 2026-03-18T22:04:56 |
| `data/raw_docs/FAO_016_cd7559en.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 2637352 | 2026-03-18T22:08:52 |
| `data/raw_docs/FAO_017_ca7588en.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 34994958 | 2026-03-18T22:11:22 |
| `data/raw_docs/FAO_018_t1623e.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 870732 | 2026-03-18T22:12:47 |
| `data/raw_docs/FAO_019_i0490e.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 4521107 | 2026-03-18T22:14:19 |
| `data/raw_docs/FAO_020_i2571e.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 4048265 | 2026-03-18T22:15:48 |
| `data/raw_docs/FAO_021_cd8667en.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 1976309 | 2026-03-18T22:18:19 |
| `data/raw_docs/FAO_022_i1750e.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 1804971 | 2026-03-18T22:19:42 |
| `data/raw_docs/FAO_023_i0970e.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 7120652 | 2026-03-18T22:21:39 |
| `data/raw_docs/FAO_024_u3100e.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 335212 | 2026-03-18T22:23:21 |
| `data/raw_docs/FAO_025_a0366e.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 1078825 | 2026-03-18T22:24:25 |
| `data/raw_docs/FAO_026_br813e.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 366409 | 2026-03-18T22:25:47 |
| `data/raw_docs/FAO_027_cd6476en.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 1950755 | 2026-03-18T22:30:49 |
| `data/raw_docs/FAO_028_i3569e.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 2583818 | 2026-03-18T22:32:23 |
| `data/raw_docs/FAO_029_i9705en.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 16659485 | 2026-03-18T22:33:45 |
| `data/raw_docs/FAO_031_cd8563en.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 9202961 | 2026-03-18T22:38:01 |
| `data/raw_docs/FAO_032_cd8633en.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 430307 | 2026-03-18T22:39:03 |
| `data/raw_docs/FAO_033_cc6625en.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 5923373 | 2026-03-18T22:40:17 |
| `data/raw_docs/FAO_034_ca2705en.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 555647 | 2026-03-18T22:44:02 |
| `data/raw_docs/FAO_035_w3594e.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 526773 | 2026-03-18T22:49:35 |
| `data/raw_docs/FAO_036_i1137e.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 1713567 | 2026-03-18T22:52:19 |
| `data/raw_docs/FAO_037_na265en.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 683985 | 2026-03-18T22:56:17 |
| `data/raw_docs/FAO_038_ca6702en.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 861870 | 2026-03-18T22:59:36 |
| `data/raw_docs/FAO_039_ad893e.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 633135 | 2026-03-18T23:03:32 |
| `data/raw_docs/FAO_040_i8064en.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 3778749 | 2026-03-18T23:04:48 |
| `data/raw_docs/FAO_041_cd3785en.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 2206169 | 2026-03-18T23:07:11 |
| `data/raw_docs/FAO_042_biosecurity_philippines.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 4655063 | 2026-04-01T16:35:09 |
| `data/raw_docs/FAO_042_i3720e.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 8839521 | 2026-03-18T23:11:04 |
| `data/raw_docs/FAO_043_boosting_biosecurity_peru.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 614195 | 2026-04-01T16:37:25 |
| `data/raw_docs/FAO_044_i2734e03i.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 4882582 | 2026-04-01T17:05:29 |
| `data/raw_docs/FAO_045_ca6163en.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 520499 | 2026-04-01T17:15:50 |
| `data/raw_docs/IJMS_001_ijms26178478.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 4165432 | 2026-03-31T21:12:08 |
| `data/raw_docs/NACA_001_1737869839.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 56312263 | 2026-03-31T15:14:44 |
| `data/raw_docs/NACA_002_1749824700.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 1162852 | 2026-03-31T15:16:26 |
| `data/raw_docs/NACA_003_1494554353.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 2425728 | 2026-03-31T15:19:20 |
| `data/raw_docs/PLOS_001_pone.0091930.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 1783090 | 2026-03-31T21:15:21 |
| `data/raw_docs/PMC_001_PMC10820212.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 825771 | 2026-04-01T17:21:10 |
| `data/raw_docs/PMC_002_PMC6963587.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 198189 | 2026-04-01T17:24:45 |
| `data/raw_docs/PMC_003_PMC11657822.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 3666087 | 2026-04-01T17:25:57 |
| `data/raw_docs/PMC_004_PMC12128546.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 3692281 | 2026-04-01T17:27:01 |
| `data/raw_docs/PMC_005_PMC12552485.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 2695289 | 2026-04-01T17:28:31 |
| `data/raw_docs/PMC_006_PMC8042889.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 2332238 | 2026-04-01T17:31:46 |
| `data/raw_docs/PMC_007_PMC8067269.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 2962901 | 2026-04-01T17:32:57 |
| `data/raw_docs/PMC_008_PMC11611405.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 3250959 | 2026-04-01T17:33:54 |
| `data/raw_docs/PMC_009_PMC12030750.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 2350238 | 2026-04-01T17:34:54 |
| `data/raw_docs/PMC_010_PMC7409025.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 1592624 | 2026-04-01T17:35:49 |
| `data/raw_docs/PMC_011_PMC5742833.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 4873671 | 2026-04-01T17:37:26 |
| `data/raw_docs/PMC_012_PMC7223513.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 518367 | 2026-04-01T17:39:04 |
| `data/raw_docs/PMC_013_PMC12825151.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 1384168 | 2026-04-01T18:57:58 |
| `data/raw_docs/PMC_014_PMC9531857.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 1479014 | 2026-04-01T19:00:21 |
| `data/raw_docs/PMC_015_PMC12006376.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 2713899 | 2026-04-01T19:03:45 |
| `data/raw_docs/PMC_016_PMC4815145.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 1733261 | 2026-04-01T19:05:21 |
| `data/raw_docs/PMC_017_PMC11223889.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 4207087 | 2026-04-01T19:06:46 |
| `data/raw_docs/PMC_018_PMC12008197.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 3776158 | 2026-04-01T19:08:08 |
| `data/raw_docs/PMC_019_PMC6797625.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 1688443 | 2026-04-01T19:09:30 |
| `data/raw_docs/PMC_020_PMC10701378.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 5632033 | 2026-04-01T19:16:12 |
| `data/raw_docs/PMC_021_PMC9427843.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 7470050 | 2026-04-01T19:19:12 |
| `data/raw_docs/PMC_022_PMC11081493.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 2595651 | 2026-04-01T19:20:22 |
| `data/raw_docs/PMC_023_PMC10229113.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 1442350 | 2026-04-01T19:23:00 |
| `data/raw_docs/PMC_024_PMC9139878.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 1883191 | 2026-04-01T19:26:06 |
| `data/raw_docs/PMC_025_PMC4510448.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 227195 | 2026-04-01T19:29:52 |
| `data/raw_docs/PMC_026_PMC11205452.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 3812393 | 2026-04-01T19:30:59 |
| `data/raw_docs/PMC_027_PMC12745081.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 1780141 | 2026-04-01T19:34:38 |
| `data/raw_docs/PMC_028_PMC5603525.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 4179909 | 2026-04-01T19:38:00 |
| `data/raw_docs/PMC_029_PMC6955853.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 17528305 | 2026-04-01T19:39:26 |
| `data/raw_docs/PMC_030_PMC10476614.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 2727978 | 2026-04-01T19:43:48 |
| `data/raw_docs/PMC_031_PMC91383.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 129405 | 2026-04-01T19:45:14 |
| `data/raw_docs/PMC_032_PMC12435696.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 2374633 | 2026-04-01T19:46:29 |
| `data/raw_docs/PMC_033_PMC8339124.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 3148392 | 2026-04-01T19:47:54 |
| `data/raw_docs/PMC_034_PMC10141217.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 22251326 | 2026-04-01T19:54:29 |
| `data/raw_docs/PMC_035_PMC11861540.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 12708855 | 2026-04-01T19:58:11 |
| `data/raw_docs/PMC_036_PMC9125206.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 5285910 | 2026-04-01T20:00:24 |
| `data/raw_docs/RIA3_001_quy_hoach_nuoi_tom_hum_2030.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 2533358 | 2026-04-18T21:09:06 |
| `data/raw_docs/RIA3_002_TBKQ_QTDX_PhuYen_KhanhHoa_17112023.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 1670425 | 2026-04-18T21:23:53 |
| `data/raw_docs/RIA3_003_TBKQ_QTMT_DOT14_T6_2025.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 1843283 | 2026-04-18T21:26:12 |
| `data/raw_docs/SEAFDEC_001_DharAK2021.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 1734398 | 2026-03-31T21:21:48 |
| `data/raw_docs/SEAFDEC_002_Wong2016.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 230067 | 2026-03-31T21:38:38 |
| `data/raw_docs/SEAFDEC_003_Yuasa2016.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 252706 | 2026-03-31T21:39:54 |
| `data/raw_docs/SEAFDEC_004_sp15-3.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 449077 | 2026-03-31T21:40:59 |
| `data/raw_docs/SEAFDEC_005_WahSLP2016.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 235457 | 2026-03-31T21:42:02 |
| `data/raw_docs/SEAFDEC_006_Apostol2016.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 435532 | 2026-03-31T21:46:13 |
| `data/raw_docs/SEAFDEC_007_Penir2019.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 113485 | 2026-03-31T21:47:25 |
| `data/raw_docs/SEAFDEC_008_Putth2016.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 584977 | 2026-03-31T21:49:57 |
| `data/raw_docs/SEAFDEC_009_Hastuti2016.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 264524 | 2026-03-31T21:51:00 |
| `data/raw_docs/SEAFDEC_010_Hirono2016.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 401561 | 2026-03-31T21:53:13 |
| `data/raw_docs/SEAFDEC_011_Kua2016.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 335696 | 2026-03-31T21:55:25 |
| `data/raw_docs/TB_001_NyanTawCRSDCaMau.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 8173752 | 2026-04-18T21:33:57 |
| `data/raw_docs/TB_002_cong_nghe_gen_va_chon_giong_tom_khang_benh.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 311117 | 2026-04-18T21:39:36 |
| `data/raw_docs/TB_003_co_che_co_ban_cua_nhiem_don_le_va_dong_nhiem_DIV1_va_WSSV_o_tom_the_chan_trang.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 431191 | 2026-04-18T21:40:46 |
| `data/raw_docs/TB_004_hoai_tu_co_o_tom_the_chan_trang.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 227871 | 2026-04-18T21:41:00 |
| `data/raw_docs/TB_005_su_hien_dien_cua_benh_dom_trang_va_EHP_va_AHPND_tai_DBSCL_2022_2024.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 233937 | 2026-04-18T21:41:49 |
| `data/raw_docs/TB_006_hoai_tu_co_IMNV_tren_tom_va_chien_luoc_kiem_soat.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 969292 | 2026-04-18T21:55:21 |
| `data/raw_docs/TB_007_benh_dom_trang_o_tom_nuoi_va_cong_nghe_nuoi_tom_nham_phong_benh_dom_trang.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 6218939 | 2026-04-18T22:00:20 |
| `data/raw_docs/TCKHTS_001.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 910982 | 2026-04-01T17:01:33 |
| `data/raw_docs/TCTS_001_024286.pdf` | Raw source document corpus used to build/search the project; do not archive without explicit data-package decision. | high |  | 710724 | 2026-03-31T20:42:03 |
| `hybrid_search.py` | Final runtime/evaluation source-of-truth explicitly protected from archive proposals. | high |  | 62348 | 2026-05-18T19:16:12 |
| `kg_runtime.py` | Final runtime/evaluation source-of-truth explicitly protected from archive proposals. | high |  | 33931 | 2026-04-18T12:40:08 |
| `run_core_baselines.py` | Final runtime/evaluation source-of-truth explicitly protected from archive proposals. | high |  | 26269 | 2026-05-23T00:59:00 |
| `vector_search.py` | Final runtime/evaluation source-of-truth explicitly protected from archive proposals. | high |  | 8624 | 2026-05-18T19:16:06 |
| `vector_store/chunks.index` | Current vector index needed by demo/runtime; do not archive unless demo/index regeneration is explicitly approved. | high |  | 39252525 | 2026-04-19T00:59:33 |
| `vector_store/chunks_meta.pkl` | Current vector index needed by demo/runtime; do not archive unless demo/index regeneration is explicitly approved. | high |  | 22144185 | 2026-04-19T00:59:33 |
| `vector_store/config.pkl` | Current vector index needed by demo/runtime; do not archive unless demo/index regeneration is explicitly approved. | high |  | 90 | 2026-04-19T00:59:33 |

## 7. Potential duplicates/superseded files

| path | reason | confidence | superseded_by | size_bytes | modified_time |
|---|---|---|---|---:|---|
| `analyze_ontology_alias_gaps.py` | One-off metadata/ontology cleanup or verification script; likely not in final package, but may be needed for provenance/regeneration. | medium | data/ontology/taxon_enriched_facts_v2.owl; data/metadata/document_metadata_cleaned.xlsx | 12496 | 2026-03-26T19:46:46 |
| `audit_alias_and_metadata_noise.py` | One-off metadata/ontology cleanup or verification script; likely not in final package, but may be needed for provenance/regeneration. | medium | data/ontology/taxon_enriched_facts_v2.owl; data/metadata/document_metadata_cleaned.xlsx | 6275 | 2026-03-30T22:03:33 |
| `audit_document_fact_coverage.py` | One-off metadata/ontology cleanup or verification script; likely not in final package, but may be needed for provenance/regeneration. | medium | data/ontology/taxon_enriched_facts_v2.owl; data/metadata/document_metadata_cleaned.xlsx | 15085 | 2026-04-01T20:41:17 |
| `backfill_document_facts_from_metadata.py` | One-off metadata/ontology cleanup or verification script; likely not in final package, but may be needed for provenance/regeneration. | medium | data/ontology/taxon_enriched_facts_v2.owl; data/metadata/document_metadata_cleaned.xlsx | 14798 | 2026-04-01T20:41:26 |
| `build_imn_lobster_comparison.py` | Old IMN/lobster comparison helper tied to archived snapshots/reports. | high | outputs/archive/old_reports/imn_lobster_fix_report.md | 5272 | 2026-04-05T23:36:32 |
| `build_weak_query_comparison.py` | Old weak-query comparison helper tied to archived snapshots/reports. | high | outputs/archive/old_reports/focus_two_weak_queries_report.md | 4140 | 2026-04-05T23:06:29 |
| `capture_focus_two_queries.py` | Old query-capture/debug helper tied to archived focus-query snapshots. | high | outputs/archive/old_reports/focus_two_weak_queries_report.md | 2600 | 2026-04-12T21:39:29 |
| `capture_focus_two_queries_round2.py` | Old round-2 query-capture helper tied to archived focus-query snapshots. | high | outputs/archive/old_reports/focus_two_weak_queries_report_round2.md | 2892 | 2026-04-13T18:40:33 |
| `capture_weak_queries.py` | Old query-capture/debug helper tied to archived weak-query snapshots. | high | outputs/archive/old_snapshots/weak_query_fix_comparison.json | 4210 | 2026-04-05T23:06:29 |
| `clean_metadata_for_entity_matching.py` | One-off metadata/ontology cleanup or verification script; likely not in final package, but may be needed for provenance/regeneration. | medium | data/ontology/taxon_enriched_facts_v2.owl; data/metadata/document_metadata_cleaned.xlsx | 10137 | 2026-03-30T22:03:33 |
| `compute_core_metrics.py` | Root-level stub/placeholder; real metric implementation is under data/eval/metrics, but checklist mentions this path. | medium | data/eval/metrics/compute_core_metrics.py | 240 | 2026-05-18T19:14:59 |
| `data/eval/final_query_set.csv` | Older/general query-set file; core and extended sets are current, but confirm before archiving. | medium | data/eval/final_query_set_core.csv; data/eval/final_query_set_extended.csv | 16088 | 2026-05-03T13:29:13 |
| `data/metadata/document_metadata.xlsx` | Original metadata workbook; cleaned workbook is final, but original source should be confirmed before archiving. | medium | data/metadata/document_metadata_cleaned.xlsx | 21611 | 2026-03-22T20:45:39 |
| `data/ontology/mapping_report.csv` | Ontology mapping/provenance report may still be useful; ask before archiving. | medium | data/ontology/taxon_enriched_facts_v2.owl | 135182 | 2026-04-01T20:28:06 |
| `data/ontology/taxon.owl` | Base ontology source may be needed for provenance/regeneration; ask before archiving. | medium | data/ontology/taxon_enriched_facts_v2.owl | 155078 | 2026-04-18T23:12:37 |
| `data/ontology/taxon_enriched.owl` | Older ontology enrichment variant; final runtime ontology is taxon_enriched_facts_v2.owl. | medium | data/ontology/taxon_enriched_facts_v2.owl | 141708 | 2026-04-01T20:28:06 |
| `data/ontology/taxon_enriched_aliases.owl` | Older ontology enrichment variant; final runtime ontology is taxon_enriched_facts_v2.owl. | medium | data/ontology/taxon_enriched_facts_v2.owl | 142280 | 2026-04-01T20:41:48 |
| `data/ontology/taxon_enriched_facts.owl` | Older ontology enrichment variant; final runtime ontology is taxon_enriched_facts_v2.owl. | medium | data/ontology/taxon_enriched_facts_v2.owl | 142693 | 2026-04-01T20:44:47 |
| `data/ontology/taxon_enriched_semantic.owl` | Older ontology enrichment variant; final runtime ontology is taxon_enriched_facts_v2.owl. | medium | data/ontology/taxon_enriched_facts_v2.owl | 145327 | 2026-04-01T20:42:03 |
| `dump_six_queries.py` | Old manual query dump/debug helper, not part of final evaluation pipeline. | high | data/eval/final_query_set_core.csv | 3627 | 2026-04-05T23:06:29 |
| `enrich_ontology_aliases.py` | One-off metadata/ontology cleanup or verification script; likely not in final package, but may be needed for provenance/regeneration. | medium | data/ontology/taxon_enriched_facts_v2.owl; data/metadata/document_metadata_cleaned.xlsx | 6010 | 2026-03-26T19:47:46 |
| `enrich_ontology_semantic_entities.py` | One-off metadata/ontology cleanup or verification script; likely not in final package, but may be needed for provenance/regeneration. | medium | data/ontology/taxon_enriched_facts_v2.owl; data/metadata/document_metadata_cleaned.xlsx | 7025 | 2026-04-01T20:41:13 |
| `full_corpus_metadata_audit.py` | One-off metadata/ontology cleanup or verification script; likely not in final package, but may be needed for provenance/regeneration. | medium | data/ontology/taxon_enriched_facts_v2.owl; data/metadata/document_metadata_cleaned.xlsx | 8304 | 2026-04-01T20:09:57 |
| `full_corpus_metadata_cleanup.py` | One-off metadata/ontology cleanup or verification script; likely not in final package, but may be needed for provenance/regeneration. | medium | data/ontology/taxon_enriched_facts_v2.owl; data/metadata/document_metadata_cleaned.xlsx | 12622 | 2026-04-01T20:11:48 |
| `full_corpus_pipeline_summary.py` | One-off metadata/ontology cleanup or verification script; likely not in final package, but may be needed for provenance/regeneration. | medium | data/ontology/taxon_enriched_facts_v2.owl; data/metadata/document_metadata_cleaned.xlsx | 3779 | 2026-04-01T20:31:32 |
| `full_corpus_query_verification.py` | One-off metadata/ontology cleanup or verification script; likely not in final package, but may be needed for provenance/regeneration. | medium | data/ontology/taxon_enriched_facts_v2.owl; data/metadata/document_metadata_cleaned.xlsx | 5086 | 2026-04-01T20:43:43 |
| `generate_semantic_rule_candidates.py` | Semantic-rule prototype generator; unclear whether thesis/future-work section still cites it. | medium | outputs/semantic_rule_candidate_facts.md | 27611 | 2026-05-23T23:40:52 |
| `hybrid_comparison.csv` | Old ad hoc hybrid comparison output, outside final evaluation layout. | high | data/eval/results/baseline_hybrid_core.csv | 56970 | 2026-04-20T21:16:13 |
| `hybrid_results.txt` | Old text dump of hybrid results, superseded by structured core/extended CSV outputs. | high | data/eval/results/baseline_hybrid_core.csv | 106904 | 2026-04-27T16:00:37 |
| `metadata_snapshot.txt` | Large metadata snapshot/debug artifact, not part of final runtime or report package. | high | data/metadata/document_metadata_cleaned.xlsx | 197582 | 2026-05-27T09:59:59 |
| `outputs/candidate_fusion_experiment_summary.csv` | Earlier candidate-fusion summary table, superseded by current metrics CSVs. | high | data/eval/metrics/hybrid_candidate_fusion_metrics_summary.csv | 520 | 2026-05-23T23:25:47 |
| `outputs/candidate_fusion_experiment_summary.json` | Earlier candidate-fusion JSON summary, superseded by current metrics/report artifacts. | high | outputs/hybrid_candidate_fusion_analysis.md | 8642 | 2026-05-23T23:25:47 |
| `outputs/candidate_fusion_experiment_summary.md` | Earlier candidate-fusion summary, superseded by current hybrid_candidate_fusion_analysis.md. | high | outputs/hybrid_candidate_fusion_analysis.md | 3513 | 2026-05-23T23:25:47 |
| `outputs/candidate_fusion_per_query_delta.csv` | Earlier candidate-fusion per-query delta, superseded by current by-query metrics. | high | data/eval/metrics/hybrid_candidate_fusion_metrics_by_query.csv | 4152 | 2026-05-23T23:25:47 |
| `outputs/document_fact_backfill_report.csv` | Backfill-generation report; final coverage audit and final ontology are the current evidence. | high | outputs/document_fact_coverage_audit.json | 16159 | 2026-04-20T20:59:49 |
| `outputs/document_fact_backfill_report.json` | Backfill-generation report; final coverage audit and final ontology are the current evidence. | high | outputs/document_fact_coverage_audit.json | 32666 | 2026-04-20T20:59:49 |
| `outputs/figures/fig_hybrid_vector_metadata_delta_by_group.png` | Similar to the final hybrid-vs-vector-metadata group figure but not in the expected final figure list; recently modified, so confirm. | medium | outputs/figures/fig_hybrid_vs_vector_metadata_by_group.png | 227742 | 2026-05-27T17:47:34 |
| `outputs/metadata_normalization_report.csv` | Intermediate metadata normalization report; cleaned metadata XLSX is final. | high | data/metadata/document_metadata_cleaned.xlsx | 18236 | 2026-04-20T20:59:49 |
| `outputs/metadata_normalization_report.json` | Intermediate metadata normalization report; cleaned metadata XLSX is final. | high | data/metadata/document_metadata_cleaned.xlsx | 44426 | 2026-04-20T20:59:49 |
| `outputs/semantic_patch_final_assessment.md` | Old semantic patch assessment; final ontology/runtime checks are newer and source-of-truth remains data/ontology/taxon_enriched_facts_v2.owl. | high | outputs/ontology_quality_check.md | 1480 | 2026-03-28T14:59:31 |
| `outputs/semantic_rule_candidate_facts.csv` | Large semantic-rule prototype output; confirm whether still cited before archiving. | medium | outputs/semantic_rule_candidate_facts.md | 350130 | 2026-05-23T23:40:58 |
| `outputs/semantic_rule_candidate_facts.json` | Large semantic-rule prototype output; confirm whether still cited before archiving. | medium | outputs/semantic_rule_candidate_facts.md | 707687 | 2026-05-23T23:40:58 |
| `outputs/semantic_rule_candidate_facts.md` | Semantic-rule prototype report; keep only if cited as future work. | medium | outputs/query_expansion_design.md | 6896 | 2026-05-23T23:40:58 |
| `outputs/semantic_rule_scoring_opportunities.csv` | Semantic-rule opportunity table; unclear final use. | medium | outputs/semantic_rule_candidate_facts.md | 2829 | 2026-05-23T23:40:58 |
| `outputs/semantic_rules_and_label_strategy.md` | Semantic-rule/label strategy note; keep only if thesis text still cites this future-work discussion. | medium | outputs/query_expansion_design.md | 17078 | 2026-05-21T20:10:14 |
| `outputs/taxon_enriched_facts_v2_backfilled_runtime.owl` | Experimental backfilled runtime ontology; final runtime ontology is in data/ontology/. | high | data/ontology/taxon_enriched_facts_v2.owl | 179851 | 2026-04-20T20:59:49 |
| `post_clean_metadata_cleanup.py` | One-off metadata/ontology cleanup or verification script; likely not in final package, but may be needed for provenance/regeneration. | medium | data/ontology/taxon_enriched_facts_v2.owl; data/metadata/document_metadata_cleaned.xlsx | 3545 | 2026-03-30T22:03:33 |
| `run_candidate_fusion_experiment.py` | Earlier candidate-fusion runner at project root; newer experiment script is under experiments/. | high | experiments/run_hybrid_candidate_fusion.py | 32842 | 2026-05-23T23:24:45 |
| `semantic_normalization.py` | One-off metadata/ontology cleanup or verification script; likely not in final package, but may be needed for provenance/regeneration. | medium | data/ontology/taxon_enriched_facts_v2.owl; data/metadata/document_metadata_cleaned.xlsx | 8261 | 2026-03-30T22:03:33 |
| `sync_metadata_to_owl.py` | One-off metadata/ontology cleanup or verification script; likely not in final package, but may be needed for provenance/regeneration. | medium | data/ontology/taxon_enriched_facts_v2.owl; data/metadata/document_metadata_cleaned.xlsx | 19167 | 2026-04-07T10:36:35 |
| `validate_semantic_patch.py` | One-off metadata/ontology cleanup or verification script; likely not in final package, but may be needed for provenance/regeneration. | medium | data/ontology/taxon_enriched_facts_v2.owl; data/metadata/document_metadata_cleaned.xlsx | 19963 | 2026-03-30T22:03:34 |
| `vector_store_backup_round10/chunks.index` | Backup vector index directory; current runtime uses vector_store/ and backups are large historical artifacts. | high | vector_store/ | 38518317 | 2026-04-01T20:25:46 |
| `vector_store_backup_round10/chunks_meta.pkl` | Backup vector index directory; current runtime uses vector_store/ and backups are large historical artifacts. | high | vector_store/ | 21633189 | 2026-04-01T20:25:46 |
| `vector_store_backup_round10/config.pkl` | Backup vector index directory; current runtime uses vector_store/ and backups are large historical artifacts. | high | vector_store/ | 90 | 2026-04-01T20:25:46 |
| `vector_store_backup_round11_after_tb_fix/chunks.index` | Backup vector index directory; current runtime uses vector_store/ and backups are large historical artifacts. | high | vector_store/ | 39075885 | 2026-04-18T23:44:53 |
| `vector_store_backup_round11_after_tb_fix/chunks_meta.pkl` | Backup vector index directory; current runtime uses vector_store/ and backups are large historical artifacts. | high | vector_store/ | 22023357 | 2026-04-18T23:44:53 |
| `vector_store_backup_round11_after_tb_fix/config.pkl` | Backup vector index directory; current runtime uses vector_store/ and backups are large historical artifacts. | high | vector_store/ | 90 | 2026-04-18T23:44:53 |
| `vector_store_backup_round12_after_ria3_fix/chunks.index` | Backup vector index directory; current runtime uses vector_store/ and backups are large historical artifacts. | high | vector_store/ | 38694957 | 2026-04-19T00:30:43 |
| `vector_store_backup_round12_after_ria3_fix/chunks_meta.pkl` | Backup vector index directory; current runtime uses vector_store/ and backups are large historical artifacts. | high | vector_store/ | 21754021 | 2026-04-19T00:30:44 |
| `vector_store_backup_round12_after_ria3_fix/config.pkl` | Backup vector index directory; current runtime uses vector_store/ and backups are large historical artifacts. | high | vector_store/ | 90 | 2026-04-19T00:30:44 |
| `verify_disease_priority_queries.py` | One-off metadata/ontology cleanup or verification script; likely not in final package, but may be needed for provenance/regeneration. | medium | data/ontology/taxon_enriched_facts_v2.owl; data/metadata/document_metadata_cleaned.xlsx | 3563 | 2026-03-30T22:03:33 |
| `verify_queries_after_alias_metadata_cleanup.py` | One-off metadata/ontology cleanup or verification script; likely not in final package, but may be needed for provenance/regeneration. | medium | data/ontology/taxon_enriched_facts_v2.owl; data/metadata/document_metadata_cleaned.xlsx | 4180 | 2026-03-30T22:03:33 |

## 8. Suggested archive folder structure

```text
archive_pre_final/
  old_reports/
  old_figures/
  old_experiments/
  old_ontology_experiments/
  old_metadata_pipeline_outputs/
  vector_store_backups/
  temp_cache/
```

Suggested mapping if archive is approved later:

- `old_reports/`: superseded `outputs/*.md`, Wilcoxon/semantic patch notes only if no longer cited.
- `old_figures/`: unlisted or duplicate figures after confirming report references.
- `old_experiments/`: old one-off query capture/comparison scripts and candidate-fusion v1 runner.
- `old_ontology_experiments/`: experimental ontology variants and semantic/backfill outputs, never the final `data/ontology/taxon_enriched_facts_v2.owl`.
- `old_metadata_pipeline_outputs/`: normalization/backfill reports superseded by cleaned metadata and coverage audits.
- `vector_store_backups/`: `vector_store_backup_round*` after confirming the current `vector_store/` is enough for the demo.
- `temp_cache/`: `__pycache__` and other generated runtime caches.

## 9. Safety notes

- No files were deleted, moved, renamed, or edited as part of this audit, except creating this Markdown report and the CSV audit file.
- No runtime, scoring, ontology, metadata, query set, judgment file, baseline result, or vector index was changed.
- `NEVER_TOUCH` files should be treated as protected final/runtime/source corpus assets unless the project owner explicitly approves a separate packaging policy.
- `ARCHIVE_CANDIDATE` is a recommendation only. It does not mean the file was moved.
- Existing files already under `archive/` were left in place and listed as archive candidates only to keep them out of the final submission package.

Files requiring user confirmation before any archive action:

- `.vscode/settings.json`: Local IDE configuration; not needed for final package but ask before archiving local setup files.
- `analyze_ontology_alias_gaps.py`: One-off metadata/ontology cleanup or verification script; likely not in final package, but may be needed for provenance/regeneration.
- `audit_alias_and_metadata_noise.py`: One-off metadata/ontology cleanup or verification script; likely not in final package, but may be needed for provenance/regeneration.
- `audit_document_fact_coverage.py`: One-off metadata/ontology cleanup or verification script; likely not in final package, but may be needed for provenance/regeneration.
- `backfill_document_facts_from_metadata.py`: One-off metadata/ontology cleanup or verification script; likely not in final package, but may be needed for provenance/regeneration.
- `clean_metadata_for_entity_matching.py`: One-off metadata/ontology cleanup or verification script; likely not in final package, but may be needed for provenance/regeneration.
- `compute_core_metrics.py`: Root-level stub/placeholder; real metric implementation is under data/eval/metrics, but checklist mentions this path.
- `data/eval/final_query_set.csv`: Older/general query-set file; core and extended sets are current, but confirm before archiving.
- `data/metadata/document_metadata.xlsx`: Original metadata workbook; cleaned workbook is final, but original source should be confirmed before archiving.
- `data/ontology/mapping_report.csv`: Ontology mapping/provenance report may still be useful; ask before archiving.
- `data/ontology/taxon.owl`: Base ontology source may be needed for provenance/regeneration; ask before archiving.
- `enrich_ontology_aliases.py`: One-off metadata/ontology cleanup or verification script; likely not in final package, but may be needed for provenance/regeneration.
- `enrich_ontology_semantic_entities.py`: One-off metadata/ontology cleanup or verification script; likely not in final package, but may be needed for provenance/regeneration.
- `full_corpus_metadata_audit.py`: One-off metadata/ontology cleanup or verification script; likely not in final package, but may be needed for provenance/regeneration.
- `full_corpus_metadata_cleanup.py`: One-off metadata/ontology cleanup or verification script; likely not in final package, but may be needed for provenance/regeneration.
- `full_corpus_pipeline_summary.py`: One-off metadata/ontology cleanup or verification script; likely not in final package, but may be needed for provenance/regeneration.
- `full_corpus_query_verification.py`: One-off metadata/ontology cleanup or verification script; likely not in final package, but may be needed for provenance/regeneration.
- `generate_semantic_rule_candidates.py`: Semantic-rule prototype generator; unclear whether thesis/future-work section still cites it.
- `outputs/figures/fig_hybrid_vector_metadata_delta_by_group.png`: Similar to the final hybrid-vs-vector-metadata group figure but not in the expected final figure list; recently modified, so confirm.
- `outputs/semantic_rule_candidate_facts.csv`: Large semantic-rule prototype output; confirm whether still cited before archiving.
- `outputs/semantic_rule_candidate_facts.json`: Large semantic-rule prototype output; confirm whether still cited before archiving.
- `outputs/semantic_rule_candidate_facts.md`: Semantic-rule prototype report; keep only if cited as future work.
- `outputs/semantic_rule_scoring_opportunities.csv`: Semantic-rule opportunity table; unclear final use.
- `outputs/semantic_rules_and_label_strategy.md`: Semantic-rule/label strategy note; keep only if thesis text still cites this future-work discussion.
- `post_clean_metadata_cleanup.py`: One-off metadata/ontology cleanup or verification script; likely not in final package, but may be needed for provenance/regeneration.
- `semantic_normalization.py`: One-off metadata/ontology cleanup or verification script; likely not in final package, but may be needed for provenance/regeneration.
- `sync_metadata_to_owl.py`: One-off metadata/ontology cleanup or verification script; likely not in final package, but may be needed for provenance/regeneration.
- `validate_semantic_patch.py`: One-off metadata/ontology cleanup or verification script; likely not in final package, but may be needed for provenance/regeneration.
- `verify_disease_priority_queries.py`: One-off metadata/ontology cleanup or verification script; likely not in final package, but may be needed for provenance/regeneration.
- `verify_queries_after_alias_metadata_cleanup.py`: One-off metadata/ontology cleanup or verification script; likely not in final package, but may be needed for provenance/regeneration.
