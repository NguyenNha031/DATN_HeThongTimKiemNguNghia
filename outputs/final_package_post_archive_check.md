# Final Package Post-Archive Check

Generated at: `2026-05-27T22:24:08`

## 1. Overview

- Overall result: **PASS**
- Checked paths/compile rows: **62**
- Missing required paths: **0**
- Compile failures: **0**
- No files were moved, deleted, renamed, or archived by this check.
- No experiment was rerun.
- Python compile was performed with `py_compile.compile` and bytecode output redirected outside the workspace to avoid recreating `__pycache__` in the project.

## 2. Missing Files

No missing required files found.

## 3. Compile Result

| path | status | details |
|---|---|---|
| app_streamlit.py | PASS | py_compile.compile passed; bytecode target was outside workspace to avoid __pycache__ regeneration. |
| hybrid_search.py | PASS | py_compile.compile passed; bytecode target was outside workspace to avoid __pycache__ regeneration. |
| kg_runtime.py | PASS | py_compile.compile passed; bytecode target was outside workspace to avoid __pycache__ regeneration. |
| vector_search.py | PASS | py_compile.compile passed; bytecode target was outside workspace to avoid __pycache__ regeneration. |
| run_core_baselines.py | PASS | py_compile.compile passed; bytecode target was outside workspace to avoid __pycache__ regeneration. |

## 4. Archive Confirmation

| path | expected_type | exists | status |
|---|---|---|---|
| archive_pre_final | dir | True | PASS |
| archive_pre_final/old_candidate_fusion_v1/run_candidate_fusion_experiment.py | file | True | PASS |
| archive_pre_final/old_semantic_patch/semantic_patch_final_assessment.md | file | True | PASS |
| archive_pre_final/old_semantic_patch/taxon_enriched_facts_v2_backfilled_runtime.owl | file | True | PASS |
| archive_pre_final/old_figures/fig_hybrid_vector_metadata_delta_by_group.png | file | True | PASS |
| archive_pre_final/vector_store_backups | dir | True | PASS |

## 5. Git Status Summary

Status counts:

- `??` (untracked): **214**
- `D` (deleted/moved from original path): **113**
- `M` (modified): **7**

Full `git status --porcelain=v1 --untracked-files=all`:

```text
 D __pycache__/analyze_ontology_alias_gaps.cpython-313.pyc
 D __pycache__/audit_document_fact_coverage.cpython-313.pyc
 D __pycache__/backfill_document_facts_from_metadata.cpython-313.pyc
 D __pycache__/enrich_ontology_aliases.cpython-313.pyc
 D __pycache__/hybrid_search.cpython-313.pyc
 D __pycache__/kg_runtime.cpython-313.pyc
 D __pycache__/run_core_baselines.cpython-313.pyc
 D __pycache__/semantic_normalization.cpython-313.pyc
 D __pycache__/sync_metadata_to_owl.cpython-313.pyc
 D __pycache__/vector_search.cpython-313.pyc
 D __pycache__/verify_kg_runtime.cpython-313.pyc
 D build_imn_lobster_comparison.py
 D build_weak_query_comparison.py
 D capture_focus_two_queries.py
 D capture_focus_two_queries_round2.py
 D capture_weak_queries.py
 M data/eval/final_query_set_extended.csv
 M data/eval/metrics/baseline_metrics_by_group.csv
 M data/eval/metrics/baseline_metrics_per_query.csv
 M data/eval/metrics/baseline_metrics_summary.csv
 M data/eval/metrics/compute_core_metrics.py
 D data/metadata/archive/document_metadata.xlsx.bak_20260330_212917
 D data/metadata/archive/document_metadata_cleaned_before_round2A.xlsx
 D data/metadata/archive/document_metadata_cleaned_before_round4.xlsx
 D data/ontology/archive/manual_cleanup_202606/mapping_report_round8_facts_v2.csv
 D data/ontology/archive/manual_cleanup_202606/mapping_report_round8_taxonowl.csv
 D data/ontology/archive/manual_cleanup_202606/taxon.owl.bak_20260418_231237
 D data/ontology/archive/manual_cleanup_202606/taxon.owl.bak_round6_location_enrichment
 D data/ontology/archive/manual_cleanup_202606/taxon.owl.bak_round7_camranh_disambiguation
 D data/ontology/archive/manual_cleanup_202606/taxon.owl.bak_round8_before_sync
 D data/ontology/archive/manual_cleanup_202606/taxon_enriched_facts_v2.owl.bak_20260418_231244
 D data/ontology/archive/manual_cleanup_202606/taxon_enriched_facts_v2.owl.bak_round6_location_enrichment
 D data/ontology/archive/manual_cleanup_202606/taxon_enriched_facts_v2.owl.bak_round7_camranh_disambiguation
 D data/ontology/archive/manual_cleanup_202606/taxon_enriched_facts_v2.owl.bak_round8_before_sync
 D dump_six_queries.py
 D hybrid_comparison.csv
 D hybrid_results.txt
 M measure_core_baseline_latency.py
 D outputs/archive/manual_cleanup_202606/tmp_tb007_debug.json
 D outputs/archive/old_outputs/added_triples_grouped_summary.json
 D outputs/archive/old_outputs/added_triples_sample.json
 D outputs/archive/old_outputs/alias_metadata_noise_audit.json
 D outputs/archive/old_outputs/alias_metadata_noise_audit_top_terms.csv
 D outputs/archive/old_outputs/document_fact_backfill_report.csv
 D outputs/archive/old_outputs/document_fact_backfill_report.json
 D outputs/archive/old_outputs/document_fact_backfill_report_facts.csv
 D outputs/archive/old_outputs/document_fact_backfill_report_facts.json
 D outputs/archive/old_outputs/document_fact_coverage_audit.csv
 D outputs/archive/old_outputs/document_fact_coverage_audit.json
 D outputs/archive/old_outputs/document_fact_coverage_audit_after_fact_backfill.csv
 D outputs/archive/old_outputs/document_fact_coverage_audit_after_fact_backfill.json
 D outputs/archive/old_outputs/document_fact_coverage_audit_after_semantic_backfill.csv
 D outputs/archive/old_outputs/document_fact_coverage_audit_after_semantic_backfill.json
 D outputs/archive/old_outputs/document_fact_coverage_audit_alias.csv
 D outputs/archive/old_outputs/document_fact_coverage_audit_alias.json
 D outputs/archive/old_outputs/document_fact_coverage_audit_before_fact_backfill.csv
 D outputs/archive/old_outputs/document_fact_coverage_audit_before_fact_backfill.json
 D outputs/archive/old_outputs/full_corpus_metadata_audit.json
 D outputs/archive/old_outputs/full_corpus_metadata_audit_summary.csv
 D outputs/archive/old_outputs/full_corpus_metadata_cleanup_effect_summary.json
 D outputs/archive/old_outputs/full_corpus_metadata_cleanup_report.csv
 D outputs/archive/old_outputs/full_corpus_metadata_cleanup_report.json
 D outputs/archive/old_outputs/full_corpus_pipeline_summary.json
 D outputs/archive/old_outputs/metadata_cleanup_effect_summary.json
 D outputs/archive/old_outputs/metadata_cleanup_report.csv
 D outputs/archive/old_outputs/metadata_cleanup_report.json
 D outputs/archive/old_outputs/metadata_normalization_report.csv
 D outputs/archive/old_outputs/metadata_normalization_report.json
 D outputs/archive/old_outputs/new_or_used_generic_entities_review.json
 D outputs/archive/old_outputs/ontology_alias_added.json
 D outputs/archive/old_outputs/ontology_alias_gap_report.csv
 D outputs/archive/old_outputs/ontology_alias_gap_report.json
 D outputs/archive/old_outputs/pipeline_run_query_summary.json
 D outputs/archive/old_outputs/post_clean_metadata_cleanup_report.json
 D outputs/archive/old_outputs/semantic_backfill_false_positive_review.json
 D outputs/archive/old_reports/cursor_fix_report.md
 D outputs/archive/old_reports/focus_two_weak_queries_report.md
 D outputs/archive/old_reports/focus_two_weak_queries_report_round2.md
 D outputs/archive/old_reports/imn_lobster_fix_report.md
 D outputs/archive/old_snapshots/focus_two_queries_after.json
 D outputs/archive/old_snapshots/focus_two_queries_before.json
 D outputs/archive/old_snapshots/focus_two_queries_metrics.json
 D outputs/archive/old_snapshots/focus_two_queries_round2_after.json
 D outputs/archive/old_snapshots/focus_two_queries_round2_before.json
 D outputs/archive/old_snapshots/imn_lobster_after.json
 D outputs/archive/old_snapshots/imn_lobster_before.json
 D outputs/archive/old_snapshots/imn_lobster_comparison.json
 D outputs/archive/old_snapshots/weak_query_fix_after.json
 D outputs/archive/old_snapshots/weak_query_fix_before.json
 D outputs/archive/old_snapshots/weak_query_fix_comparison.json
 D outputs/archive/old_verification/alias_metadata_cleanup_query_verification.json
 D outputs/archive/old_verification/disease_priority_queries_verification.json
 D outputs/archive/old_verification/disease_priority_queries_verification_after_canonical_bridge.json
 D outputs/archive/old_verification/disease_priority_queries_verification_after_tightening.json
 D outputs/archive/old_verification/disease_priority_queries_verification_before_tightening.json
 D outputs/archive/old_verification/full_corpus_query_verification.json
 D outputs/archive/old_verification/kg_runtime_verification_after_canonical_bridge.json
 D outputs/archive/old_verification/kg_runtime_verification_after_disease_tightening.json
 D outputs/archive/old_verification/kg_runtime_verification_before_alias_enrichment.json
 D outputs/archive/old_verification/kg_runtime_verification_before_disease_tightening.json
 D outputs/archive/old_verification/kg_runtime_verification_before_fact_backfill.json
 D outputs/archive/old_verification/kg_runtime_verification_before_semantic_backfill.json
 D outputs/archive/old_verification/kg_runtime_verification_semantic_patch_expanded.json
 D outputs/archive/old_verification/kg_runtime_verification_semantic_patch_summary.json
 D outputs/document_fact_backfill_report.csv
 D outputs/document_fact_backfill_report.json
 D outputs/metadata_normalization_report.csv
 D outputs/metadata_normalization_report.json
 D outputs/semantic_patch_final_assessment.md
 D outputs/taxon_enriched_facts_v2_backfilled_runtime.owl
 M run_core_baselines.py
 D vector_store_backup_round10/chunks.index
 D vector_store_backup_round10/chunks_meta.pkl
 D vector_store_backup_round10/config.pkl
 D vector_store_backup_round11_after_tb_fix/chunks.index
 D vector_store_backup_round11_after_tb_fix/chunks_meta.pkl
 D vector_store_backup_round11_after_tb_fix/config.pkl
 D vector_store_backup_round12_after_ria3_fix/chunks.index
 D vector_store_backup_round12_after_ria3_fix/chunks_meta.pkl
 D vector_store_backup_round12_after_ria3_fix/config.pkl
?? .streamlit/config.toml
?? analyze_query_understanding_profiles.py
?? app_streamlit.py
?? archive_pre_final/already_archived/data/metadata/archive/document_metadata.xlsx.bak_20260330_212917
?? archive_pre_final/already_archived/data/metadata/archive/document_metadata_cleaned_before_round2A.xlsx
?? archive_pre_final/already_archived/data/metadata/archive/document_metadata_cleaned_before_round4.xlsx
?? archive_pre_final/already_archived/data/ontology/archive/manual_cleanup_202606/mapping_report_round8_facts_v2.csv
?? archive_pre_final/already_archived/data/ontology/archive/manual_cleanup_202606/mapping_report_round8_taxonowl.csv
?? archive_pre_final/already_archived/data/ontology/archive/manual_cleanup_202606/taxon.owl.bak_20260418_231237
?? archive_pre_final/already_archived/data/ontology/archive/manual_cleanup_202606/taxon.owl.bak_round6_location_enrichment
?? archive_pre_final/already_archived/data/ontology/archive/manual_cleanup_202606/taxon.owl.bak_round7_camranh_disambiguation
?? archive_pre_final/already_archived/data/ontology/archive/manual_cleanup_202606/taxon.owl.bak_round8_before_sync
?? archive_pre_final/already_archived/data/ontology/archive/manual_cleanup_202606/taxon_enriched_facts_v2.owl.bak_20260418_231244
?? archive_pre_final/already_archived/data/ontology/archive/manual_cleanup_202606/taxon_enriched_facts_v2.owl.bak_round6_location_enrichment
?? archive_pre_final/already_archived/data/ontology/archive/manual_cleanup_202606/taxon_enriched_facts_v2.owl.bak_round7_camranh_disambiguation
?? archive_pre_final/already_archived/data/ontology/archive/manual_cleanup_202606/taxon_enriched_facts_v2.owl.bak_round8_before_sync
?? archive_pre_final/already_archived/outputs/archive/manual_cleanup_202606/tmp_tb007_debug.json
?? archive_pre_final/already_archived/outputs/archive/old_outputs/added_triples_grouped_summary.json
?? archive_pre_final/already_archived/outputs/archive/old_outputs/added_triples_sample.json
?? archive_pre_final/already_archived/outputs/archive/old_outputs/alias_metadata_noise_audit.json
?? archive_pre_final/already_archived/outputs/archive/old_outputs/alias_metadata_noise_audit_top_terms.csv
?? archive_pre_final/already_archived/outputs/archive/old_outputs/document_fact_backfill_report.csv
?? archive_pre_final/already_archived/outputs/archive/old_outputs/document_fact_backfill_report.json
?? archive_pre_final/already_archived/outputs/archive/old_outputs/document_fact_backfill_report_facts.csv
?? archive_pre_final/already_archived/outputs/archive/old_outputs/document_fact_backfill_report_facts.json
?? archive_pre_final/already_archived/outputs/archive/old_outputs/document_fact_coverage_audit.csv
?? archive_pre_final/already_archived/outputs/archive/old_outputs/document_fact_coverage_audit.json
?? archive_pre_final/already_archived/outputs/archive/old_outputs/document_fact_coverage_audit_after_fact_backfill.csv
?? archive_pre_final/already_archived/outputs/archive/old_outputs/document_fact_coverage_audit_after_fact_backfill.json
?? archive_pre_final/already_archived/outputs/archive/old_outputs/document_fact_coverage_audit_after_semantic_backfill.csv
?? archive_pre_final/already_archived/outputs/archive/old_outputs/document_fact_coverage_audit_after_semantic_backfill.json
?? archive_pre_final/already_archived/outputs/archive/old_outputs/document_fact_coverage_audit_alias.csv
?? archive_pre_final/already_archived/outputs/archive/old_outputs/document_fact_coverage_audit_alias.json
?? archive_pre_final/already_archived/outputs/archive/old_outputs/document_fact_coverage_audit_before_fact_backfill.csv
?? archive_pre_final/already_archived/outputs/archive/old_outputs/document_fact_coverage_audit_before_fact_backfill.json
?? archive_pre_final/already_archived/outputs/archive/old_outputs/full_corpus_metadata_audit.json
?? archive_pre_final/already_archived/outputs/archive/old_outputs/full_corpus_metadata_audit_summary.csv
?? archive_pre_final/already_archived/outputs/archive/old_outputs/full_corpus_metadata_cleanup_effect_summary.json
?? archive_pre_final/already_archived/outputs/archive/old_outputs/full_corpus_metadata_cleanup_report.csv
?? archive_pre_final/already_archived/outputs/archive/old_outputs/full_corpus_metadata_cleanup_report.json
?? archive_pre_final/already_archived/outputs/archive/old_outputs/full_corpus_pipeline_summary.json
?? archive_pre_final/already_archived/outputs/archive/old_outputs/metadata_cleanup_effect_summary.json
?? archive_pre_final/already_archived/outputs/archive/old_outputs/metadata_cleanup_report.csv
?? archive_pre_final/already_archived/outputs/archive/old_outputs/metadata_cleanup_report.json
?? archive_pre_final/already_archived/outputs/archive/old_outputs/metadata_normalization_report.csv
?? archive_pre_final/already_archived/outputs/archive/old_outputs/metadata_normalization_report.json
?? archive_pre_final/already_archived/outputs/archive/old_outputs/new_or_used_generic_entities_review.json
?? archive_pre_final/already_archived/outputs/archive/old_outputs/ontology_alias_added.json
?? archive_pre_final/already_archived/outputs/archive/old_outputs/ontology_alias_gap_report.csv
?? archive_pre_final/already_archived/outputs/archive/old_outputs/ontology_alias_gap_report.json
?? archive_pre_final/already_archived/outputs/archive/old_outputs/pipeline_run_query_summary.json
?? archive_pre_final/already_archived/outputs/archive/old_outputs/post_clean_metadata_cleanup_report.json
?? archive_pre_final/already_archived/outputs/archive/old_outputs/semantic_backfill_false_positive_review.json
?? archive_pre_final/already_archived/outputs/archive/old_reports/cursor_fix_report.md
?? archive_pre_final/already_archived/outputs/archive/old_reports/focus_two_weak_queries_report.md
?? archive_pre_final/already_archived/outputs/archive/old_reports/focus_two_weak_queries_report_round2.md
?? archive_pre_final/already_archived/outputs/archive/old_reports/imn_lobster_fix_report.md
?? archive_pre_final/already_archived/outputs/archive/old_snapshots/focus_two_queries_after.json
?? archive_pre_final/already_archived/outputs/archive/old_snapshots/focus_two_queries_before.json
?? archive_pre_final/already_archived/outputs/archive/old_snapshots/focus_two_queries_metrics.json
?? archive_pre_final/already_archived/outputs/archive/old_snapshots/focus_two_queries_round2_after.json
?? archive_pre_final/already_archived/outputs/archive/old_snapshots/focus_two_queries_round2_before.json
?? archive_pre_final/already_archived/outputs/archive/old_snapshots/imn_lobster_after.json
?? archive_pre_final/already_archived/outputs/archive/old_snapshots/imn_lobster_before.json
?? archive_pre_final/already_archived/outputs/archive/old_snapshots/imn_lobster_comparison.json
?? archive_pre_final/already_archived/outputs/archive/old_snapshots/weak_query_fix_after.json
?? archive_pre_final/already_archived/outputs/archive/old_snapshots/weak_query_fix_before.json
?? archive_pre_final/already_archived/outputs/archive/old_snapshots/weak_query_fix_comparison.json
?? archive_pre_final/already_archived/outputs/archive/old_verification/alias_metadata_cleanup_query_verification.json
?? archive_pre_final/already_archived/outputs/archive/old_verification/disease_priority_queries_verification.json
?? archive_pre_final/already_archived/outputs/archive/old_verification/disease_priority_queries_verification_after_canonical_bridge.json
?? archive_pre_final/already_archived/outputs/archive/old_verification/disease_priority_queries_verification_after_tightening.json
?? archive_pre_final/already_archived/outputs/archive/old_verification/disease_priority_queries_verification_before_tightening.json
?? archive_pre_final/already_archived/outputs/archive/old_verification/full_corpus_query_verification.json
?? archive_pre_final/already_archived/outputs/archive/old_verification/kg_runtime_verification_after_canonical_bridge.json
?? archive_pre_final/already_archived/outputs/archive/old_verification/kg_runtime_verification_after_disease_tightening.json
?? archive_pre_final/already_archived/outputs/archive/old_verification/kg_runtime_verification_before_alias_enrichment.json
?? archive_pre_final/already_archived/outputs/archive/old_verification/kg_runtime_verification_before_disease_tightening.json
?? archive_pre_final/already_archived/outputs/archive/old_verification/kg_runtime_verification_before_fact_backfill.json
?? archive_pre_final/already_archived/outputs/archive/old_verification/kg_runtime_verification_before_semantic_backfill.json
?? archive_pre_final/already_archived/outputs/archive/old_verification/kg_runtime_verification_semantic_patch_expanded.json
?? archive_pre_final/already_archived/outputs/archive/old_verification/kg_runtime_verification_semantic_patch_summary.json
?? archive_pre_final/old_candidate_fusion_v1/candidate_fusion_experiment_summary.csv
?? archive_pre_final/old_candidate_fusion_v1/candidate_fusion_experiment_summary.json
?? archive_pre_final/old_candidate_fusion_v1/candidate_fusion_experiment_summary.md
?? archive_pre_final/old_candidate_fusion_v1/candidate_fusion_per_query_delta.csv
?? archive_pre_final/old_candidate_fusion_v1/run_candidate_fusion_experiment.py
?? archive_pre_final/old_debug_scripts/build_imn_lobster_comparison.py
?? archive_pre_final/old_debug_scripts/build_weak_query_comparison.py
?? archive_pre_final/old_debug_scripts/capture_focus_two_queries.py
?? archive_pre_final/old_debug_scripts/capture_focus_two_queries_round2.py
?? archive_pre_final/old_debug_scripts/capture_weak_queries.py
?? archive_pre_final/old_debug_scripts/dump_six_queries.py
?? archive_pre_final/old_debug_scripts/hybrid_comparison.csv
?? archive_pre_final/old_debug_scripts/hybrid_results.txt
?? archive_pre_final/old_debug_scripts/metadata_snapshot.txt
?? archive_pre_final/old_figures/fig_hybrid_vector_metadata_delta_by_group.png
?? archive_pre_final/old_metadata_outputs/document_fact_backfill_report.csv
?? archive_pre_final/old_metadata_outputs/document_fact_backfill_report.json
?? archive_pre_final/old_metadata_outputs/metadata_normalization_report.csv
?? archive_pre_final/old_metadata_outputs/metadata_normalization_report.json
?? archive_pre_final/old_semantic_patch/semantic_patch_final_assessment.md
?? archive_pre_final/old_semantic_patch/taxon_enriched_facts_v2_backfilled_runtime.owl
?? archive_pre_final/old_semantic_rule_prototype/generate_semantic_rule_candidates.py
?? archive_pre_final/old_semantic_rule_prototype/semantic_rule_candidate_facts.csv
?? archive_pre_final/old_semantic_rule_prototype/semantic_rule_candidate_facts.json
?? archive_pre_final/old_semantic_rule_prototype/semantic_rule_candidate_facts.md
?? archive_pre_final/old_semantic_rule_prototype/semantic_rule_scoring_opportunities.csv
?? archive_pre_final/old_semantic_rule_prototype/semantic_rules_and_label_strategy.md
?? archive_pre_final/temp_cache/__pycache__/analyze_ontology_alias_gaps.cpython-313.pyc
?? archive_pre_final/temp_cache/__pycache__/audit_document_fact_coverage.cpython-313.pyc
?? archive_pre_final/temp_cache/__pycache__/backfill_document_facts_from_metadata.cpython-313.pyc
?? archive_pre_final/temp_cache/__pycache__/enrich_ontology_aliases.cpython-313.pyc
?? archive_pre_final/temp_cache/__pycache__/hybrid_search.cpython-313.pyc
?? archive_pre_final/temp_cache/__pycache__/kg_runtime.cpython-313.pyc
?? archive_pre_final/temp_cache/__pycache__/run_core_baselines.cpython-313.pyc
?? archive_pre_final/temp_cache/__pycache__/semantic_normalization.cpython-313.pyc
?? archive_pre_final/temp_cache/__pycache__/sync_metadata_to_owl.cpython-313.pyc
?? archive_pre_final/temp_cache/__pycache__/vector_search.cpython-313.pyc
?? archive_pre_final/temp_cache/__pycache__/verify_kg_runtime.cpython-313.pyc
?? archive_pre_final/vector_store_backups/vector_store_backup_round10/chunks.index
?? archive_pre_final/vector_store_backups/vector_store_backup_round10/chunks_meta.pkl
?? archive_pre_final/vector_store_backups/vector_store_backup_round10/config.pkl
?? archive_pre_final/vector_store_backups/vector_store_backup_round11_after_tb_fix/chunks.index
?? archive_pre_final/vector_store_backups/vector_store_backup_round11_after_tb_fix/chunks_meta.pkl
?? archive_pre_final/vector_store_backups/vector_store_backup_round11_after_tb_fix/config.pkl
?? archive_pre_final/vector_store_backups/vector_store_backup_round12_after_ria3_fix/chunks.index
?? archive_pre_final/vector_store_backups/vector_store_backup_round12_after_ria3_fix/chunks_meta.pkl
?? archive_pre_final/vector_store_backups/vector_store_backup_round12_after_ria3_fix/config.pkl
?? data/eval/competency_questions_core.csv
?? data/eval/metrics/baseline_metrics_by_group_extended.csv
?? data/eval/metrics/baseline_metrics_by_group_plus.csv
?? data/eval/metrics/baseline_metrics_by_query_extended.csv
?? data/eval/metrics/baseline_metrics_by_query_plus.csv
?? data/eval/metrics/baseline_metrics_summary_extended.csv
?? data/eval/metrics/baseline_metrics_summary_plus.csv
?? data/eval/metrics/hybrid_candidate_fusion_metrics_by_group.csv
?? data/eval/metrics/hybrid_candidate_fusion_metrics_by_query.csv
?? data/eval/metrics/hybrid_candidate_fusion_metrics_summary.csv
?? data/eval/metrics/kg_ablation_metrics_by_group.csv
?? data/eval/metrics/kg_ablation_metrics_by_query.csv
?? data/eval/metrics/kg_ablation_metrics_summary.csv
?? data/eval/relevance_judgments_extended.csv
?? data/eval/results/baseline_hybrid_candidate_fusion_core.csv
?? data/eval/results/baseline_hybrid_candidate_fusion_extended.csv
?? data/eval/results/baseline_hybrid_extended.csv
?? data/eval/results/baseline_lexical_extended.csv
?? data/eval/results/baseline_ontology_sparql_extended.csv
?? data/eval/results/baseline_vector_extended.csv
?? data/eval/results/baseline_vector_metadata_extended.csv
?? data/eval/results/baseline_vector_metadata_kg_no_intent_core.csv
?? data/eval/results/kg_ablation_results_core.csv
?? evaluate_competency_questions.py
?? experiments/analyze_kg_score_components.py
?? experiments/compute_baseline_metrics_plus.py
?? experiments/generate_query_expansion_examples.py
?? experiments/run_extended_evaluation.py
?? experiments/run_hybrid_candidate_fusion.py
?? experiments/run_kg_ablation.py
?? generate_error_analysis_core.py
?? generate_evaluation_layers_summary.py
?? outputs/baseline_metrics_plus_report.md
?? outputs/competency_questions_results.csv
?? outputs/competency_questions_summary.json
?? outputs/error_analysis_core.csv
?? outputs/error_analysis_summary.json
?? outputs/evaluation_layers_summary.json
?? outputs/evaluation_layers_summary.md
?? outputs/extended_query_evaluation_report.md
?? outputs/extended_query_judgment_audit.md
?? outputs/figures/fig_ablation_key_metrics.pdf
?? outputs/figures/fig_ablation_key_metrics.png
?? outputs/figures/fig_baseline_key_metrics.pdf
?? outputs/figures/fig_baseline_key_metrics.png
?? outputs/figures/fig_candidate_fusion_summary.png
?? outputs/figures/fig_extended_evaluation_summary.png
?? outputs/figures/fig_hybrid_vs_vector_metadata_by_group.pdf
?? outputs/figures/fig_hybrid_vs_vector_metadata_by_group.png
?? outputs/figures/fig_kg_ablation_summary.png
?? outputs/figures/fig_kg_runtime_contribution_summary.png
?? outputs/figures/fig_kg_score_components.png
?? outputs/figures/fig_quality_latency_tradeoff.pdf
?? outputs/figures/fig_quality_latency_tradeoff.png
?? outputs/figures/fig_query_expansion_examples.png
?? outputs/final_score_formula_and_runtime_flow.md
?? outputs/final_submission_file_checklist.md
?? outputs/hybrid_candidate_fusion_analysis.md
?? outputs/hybrid_vs_vector_metadata_by_group.csv
?? outputs/hybrid_vs_vector_metadata_by_group.md
?? outputs/kg_ablation_analysis.md
?? outputs/kg_score_component_analysis.csv
?? outputs/kg_score_component_analysis.md
?? outputs/ontology_quality_check.json
?? outputs/ontology_quality_check.md
?? outputs/ontology_reasoner_consistency_check.json
?? outputs/ontology_reasoner_consistency_check.md
?? outputs/project_file_archive_execution_log.csv
?? outputs/project_file_archive_execution_report.md
?? outputs/project_file_archive_move_plan.csv
?? outputs/project_file_archive_move_plan.md
?? outputs/project_file_cleanup_audit.csv
?? outputs/project_file_cleanup_audit.md
?? outputs/query_expansion_design.md
?? outputs/query_expansion_examples.csv
?? outputs/query_understanding_profiles.csv
?? outputs/query_understanding_profiles.json
?? outputs/query_understanding_profiles.md
?? outputs/streamlit_demo_notes.md
?? outputs/wilcoxon_hybrid_vs_vector_metadata.csv
?? outputs/wilcoxon_hybrid_vs_vector_metadata.json
?? outputs/wilcoxon_hybrid_vs_vector_metadata.md
?? run_wilcoxon_significance_test.py
?? verify_ontology_quality.py
?? verify_ontology_reasoner_consistency.py
```

## 6. Protected File Git Warnings

Protected files currently marked modified (`M`) in git status:

- `run_core_baselines.py`: ` M`
- `data/eval/metrics/baseline_metrics_summary.csv`: ` M`
- `data/eval/metrics/baseline_metrics_by_group.csv`: ` M`
- `data/eval/metrics/baseline_metrics_per_query.csv`: ` M`

Protected files with any git status entry:

- `app_streamlit.py`: `??`
- `.streamlit/config.toml`: `??`
- `run_core_baselines.py`: ` M`
- `data/eval/metrics/baseline_metrics_summary.csv`: ` M`
- `data/eval/metrics/baseline_metrics_by_group.csv`: ` M`
- `data/eval/metrics/baseline_metrics_per_query.csv`: ` M`

## 7. Detailed Check Table

| section | path | expected_type | exists | status | details |
|---|---|---|---|---|---|
| A_protected | app_streamlit.py | file | True | PASS |  |
| A_protected | .streamlit/config.toml | file | True | PASS |  |
| A_protected | hybrid_search.py | file | True | PASS |  |
| A_protected | kg_runtime.py | file | True | PASS |  |
| A_protected | vector_search.py | file | True | PASS |  |
| A_protected | run_core_baselines.py | file | True | PASS |  |
| A_protected | data/ontology/taxon_enriched_facts_v2.owl | file | True | PASS |  |
| A_protected | data/metadata/document_metadata_cleaned.xlsx | file | True | PASS |  |
| A_protected | data/eval/final_query_set_core.csv | file | True | PASS |  |
| A_protected | data/eval/relevance_judgments_core.csv | file | True | PASS |  |
| A_protected | data/eval/metrics/baseline_metrics_summary.csv | file | True | PASS |  |
| A_protected | data/eval/metrics/baseline_metrics_by_group.csv | file | True | PASS |  |
| A_protected | data/eval/metrics/baseline_metrics_per_query.csv | file | True | PASS |  |
| A_protected | data/eval/metrics/baseline_latency_summary.csv | file | True | PASS |  |
| A_protected | data/eval/results/baseline_hybrid_core.csv | file | True | PASS |  |
| A_protected | data/eval/results/baseline_vector_metadata_core.csv | file | True | PASS |  |
| A_protected | vector_store/chunks.index | file | True | PASS |  |
| A_protected | vector_store/chunks_meta.pkl | file | True | PASS |  |
| A_protected | vector_store/config.pkl | file | True | PASS |  |
| B_new_submission | experiments/run_hybrid_candidate_fusion.py | file | True | PASS |  |
| B_new_submission | experiments/run_extended_evaluation.py | file | True | PASS |  |
| B_new_submission | experiments/compute_baseline_metrics_plus.py | file | True | PASS |  |
| B_new_submission | experiments/analyze_kg_score_components.py | file | True | PASS |  |
| B_new_submission | experiments/run_kg_ablation.py | file | True | PASS |  |
| B_new_submission | experiments/generate_query_expansion_examples.py | file | True | PASS |  |
| B_new_submission | data/eval/final_query_set_extended.csv | file | True | PASS |  |
| B_new_submission | data/eval/relevance_judgments_extended.csv | file | True | PASS |  |
| B_new_submission | data/eval/results/baseline_hybrid_candidate_fusion_core.csv | file | True | PASS |  |
| B_new_submission | data/eval/results/kg_ablation_results_core.csv | file | True | PASS |  |
| B_new_submission | data/eval/metrics/hybrid_candidate_fusion_metrics_summary.csv | file | True | PASS |  |
| B_new_submission | data/eval/metrics/baseline_metrics_summary_extended.csv | file | True | PASS |  |
| B_new_submission | data/eval/metrics/baseline_metrics_summary_plus.csv | file | True | PASS |  |
| B_new_submission | data/eval/metrics/kg_ablation_metrics_summary.csv | file | True | PASS |  |
| B_new_submission | outputs/hybrid_candidate_fusion_analysis.md | file | True | PASS |  |
| B_new_submission | outputs/extended_query_evaluation_report.md | file | True | PASS |  |
| B_new_submission | outputs/extended_query_judgment_audit.md | file | True | PASS |  |
| B_new_submission | outputs/baseline_metrics_plus_report.md | file | True | PASS |  |
| B_new_submission | outputs/kg_score_component_analysis.md | file | True | PASS |  |
| B_new_submission | outputs/kg_ablation_analysis.md | file | True | PASS |  |
| B_new_submission | outputs/query_expansion_design.md | file | True | PASS |  |
| B_new_submission | outputs/query_expansion_examples.csv | file | True | PASS |  |
| C_final_figures | outputs/figures/fig_baseline_key_metrics.png | file | True | PASS |  |
| C_final_figures | outputs/figures/fig_quality_latency_tradeoff.png | file | True | PASS |  |
| C_final_figures | outputs/figures/fig_hybrid_vs_vector_metadata_by_group.png | file | True | PASS |  |
| C_final_figures | outputs/figures/fig_ablation_key_metrics.png | file | True | PASS |  |
| C_final_figures | outputs/figures/fig_kg_runtime_contribution_summary.png | file | True | PASS |  |
| C_final_figures | outputs/figures/fig_kg_ablation_summary.png | file | True | PASS |  |
| C_final_figures | outputs/figures/fig_candidate_fusion_summary.png | file | True | PASS |  |
| C_final_figures | outputs/figures/fig_extended_evaluation_summary.png | file | True | PASS |  |
| D_supporting_figures | outputs/figures/fig_query_expansion_examples.png | file | True | PASS |  |
| D_supporting_figures | outputs/figures/fig_kg_score_components.png | file | True | PASS |  |
| E_archive_confirmation | archive_pre_final | dir | True | PASS |  |
| E_archive_confirmation | archive_pre_final/old_candidate_fusion_v1/run_candidate_fusion_experiment.py | file | True | PASS |  |
| E_archive_confirmation | archive_pre_final/old_semantic_patch/semantic_patch_final_assessment.md | file | True | PASS |  |
| E_archive_confirmation | archive_pre_final/old_semantic_patch/taxon_enriched_facts_v2_backfilled_runtime.owl | file | True | PASS |  |
| E_archive_confirmation | archive_pre_final/old_figures/fig_hybrid_vector_metadata_delta_by_group.png | file | True | PASS |  |
| E_archive_confirmation | archive_pre_final/vector_store_backups | dir | True | PASS |  |
| F_py_compile | app_streamlit.py | file | True | PASS | py_compile.compile passed; bytecode target was outside workspace to avoid __pycache__ regeneration. |
| F_py_compile | hybrid_search.py | file | True | PASS | py_compile.compile passed; bytecode target was outside workspace to avoid __pycache__ regeneration. |
| F_py_compile | kg_runtime.py | file | True | PASS | py_compile.compile passed; bytecode target was outside workspace to avoid __pycache__ regeneration. |
| F_py_compile | vector_search.py | file | True | PASS | py_compile.compile passed; bytecode target was outside workspace to avoid __pycache__ regeneration. |
| F_py_compile | run_core_baselines.py | file | True | PASS | py_compile.compile passed; bytecode target was outside workspace to avoid __pycache__ regeneration. |
