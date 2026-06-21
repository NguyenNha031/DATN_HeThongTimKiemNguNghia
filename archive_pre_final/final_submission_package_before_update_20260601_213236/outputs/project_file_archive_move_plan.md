# Project File Archive Move Plan

Generated at: `2026-05-27T22:14:14`

Source audit files:
- `outputs/project_file_cleanup_audit.md`
- `outputs/project_file_cleanup_audit.csv`

## Executive Summary

- Total files in plan: **386**
- ready_to_move: **126**
- hold: **128**
- never_touch: **132**
- No files were moved, deleted, renamed, or modified by this plan.
- The two figure classification changes requested are applied in this plan: `fig_query_expansion_examples.png` and `fig_kg_score_components.png` are `hold` as supporting artifacts, not final/archive-now files.
- `fig_hybrid_vector_metadata_delta_by_group.png` is marked `ready_to_move` because no reference was found outside audit files; verify the thesis/report text before executing any move.

Risk breakdown:

- ready_to_move: low: 108, medium: 18
- hold: low: 103, medium: 25
- never_touch: high: 132

## Proposed Archive Folder Structure

```text
archive_pre_final/
  temp_cache/
  vector_store_backups/
  old_candidate_fusion_v1/
  old_semantic_patch/
  old_metadata_outputs/
  old_debug_scripts/
  old_semantic_rule_prototype/
  old_figures/
  already_archived/
```

## Ready To Move

| source_path | proposed_archive_path | reason | risk_level | action_status |
|---|---|---|---|---|
| `__pycache__/analyze_ontology_alias_gaps.cpython-313.pyc` | `archive_pre_final/temp_cache/__pycache__/analyze_ontology_alias_gaps.cpython-313.pyc` | Generated Python cache. Approved for archive under temp_cache; can be regenerated. | low | ready_to_move |
| `__pycache__/audit_document_fact_coverage.cpython-313.pyc` | `archive_pre_final/temp_cache/__pycache__/audit_document_fact_coverage.cpython-313.pyc` | Generated Python cache. Approved for archive under temp_cache; can be regenerated. | low | ready_to_move |
| `__pycache__/backfill_document_facts_from_metadata.cpython-313.pyc` | `archive_pre_final/temp_cache/__pycache__/backfill_document_facts_from_metadata.cpython-313.pyc` | Generated Python cache. Approved for archive under temp_cache; can be regenerated. | low | ready_to_move |
| `__pycache__/enrich_ontology_aliases.cpython-313.pyc` | `archive_pre_final/temp_cache/__pycache__/enrich_ontology_aliases.cpython-313.pyc` | Generated Python cache. Approved for archive under temp_cache; can be regenerated. | low | ready_to_move |
| `__pycache__/hybrid_search.cpython-313.pyc` | `archive_pre_final/temp_cache/__pycache__/hybrid_search.cpython-313.pyc` | Generated Python cache. Approved for archive under temp_cache; can be regenerated. | low | ready_to_move |
| `__pycache__/kg_runtime.cpython-313.pyc` | `archive_pre_final/temp_cache/__pycache__/kg_runtime.cpython-313.pyc` | Generated Python cache. Approved for archive under temp_cache; can be regenerated. | low | ready_to_move |
| `__pycache__/run_core_baselines.cpython-313.pyc` | `archive_pre_final/temp_cache/__pycache__/run_core_baselines.cpython-313.pyc` | Generated Python cache. Approved for archive under temp_cache; can be regenerated. | low | ready_to_move |
| `__pycache__/semantic_normalization.cpython-313.pyc` | `archive_pre_final/temp_cache/__pycache__/semantic_normalization.cpython-313.pyc` | Generated Python cache. Approved for archive under temp_cache; can be regenerated. | low | ready_to_move |
| `__pycache__/sync_metadata_to_owl.cpython-313.pyc` | `archive_pre_final/temp_cache/__pycache__/sync_metadata_to_owl.cpython-313.pyc` | Generated Python cache. Approved for archive under temp_cache; can be regenerated. | low | ready_to_move |
| `__pycache__/vector_search.cpython-313.pyc` | `archive_pre_final/temp_cache/__pycache__/vector_search.cpython-313.pyc` | Generated Python cache. Approved for archive under temp_cache; can be regenerated. | low | ready_to_move |
| `__pycache__/verify_kg_runtime.cpython-313.pyc` | `archive_pre_final/temp_cache/__pycache__/verify_kg_runtime.cpython-313.pyc` | Generated Python cache. Approved for archive under temp_cache; can be regenerated. | low | ready_to_move |
| `build_imn_lobster_comparison.py` | `archive_pre_final/old_debug_scripts/build_imn_lobster_comparison.py` | Old debug/comparison helper tied to archived snapshots, not final runtime/evaluation. | low | ready_to_move |
| `build_weak_query_comparison.py` | `archive_pre_final/old_debug_scripts/build_weak_query_comparison.py` | Old debug/comparison helper tied to archived snapshots, not final runtime/evaluation. | low | ready_to_move |
| `capture_focus_two_queries.py` | `archive_pre_final/old_debug_scripts/capture_focus_two_queries.py` | Old debug/comparison helper tied to archived snapshots, not final runtime/evaluation. | low | ready_to_move |
| `capture_focus_two_queries_round2.py` | `archive_pre_final/old_debug_scripts/capture_focus_two_queries_round2.py` | Old debug/comparison helper tied to archived snapshots, not final runtime/evaluation. | low | ready_to_move |
| `capture_weak_queries.py` | `archive_pre_final/old_debug_scripts/capture_weak_queries.py` | Old debug/comparison helper tied to archived snapshots, not final runtime/evaluation. | low | ready_to_move |
| `data/metadata/archive/document_metadata.xlsx.bak_20260330_212917` | `archive_pre_final/already_archived/data/metadata/archive/document_metadata.xlsx.bak_20260330_212917` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `data/metadata/archive/document_metadata_cleaned_before_round2A.xlsx` | `archive_pre_final/already_archived/data/metadata/archive/document_metadata_cleaned_before_round2A.xlsx` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `data/metadata/archive/document_metadata_cleaned_before_round4.xlsx` | `archive_pre_final/already_archived/data/metadata/archive/document_metadata_cleaned_before_round4.xlsx` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `data/ontology/archive/manual_cleanup_202606/mapping_report_round8_facts_v2.csv` | `archive_pre_final/already_archived/data/ontology/archive/manual_cleanup_202606/mapping_report_round8_facts_v2.csv` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `data/ontology/archive/manual_cleanup_202606/mapping_report_round8_taxonowl.csv` | `archive_pre_final/already_archived/data/ontology/archive/manual_cleanup_202606/mapping_report_round8_taxonowl.csv` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `data/ontology/archive/manual_cleanup_202606/taxon.owl.bak_20260418_231237` | `archive_pre_final/already_archived/data/ontology/archive/manual_cleanup_202606/taxon.owl.bak_20260418_231237` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `data/ontology/archive/manual_cleanup_202606/taxon.owl.bak_round6_location_enrichment` | `archive_pre_final/already_archived/data/ontology/archive/manual_cleanup_202606/taxon.owl.bak_round6_location_enrichment` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `data/ontology/archive/manual_cleanup_202606/taxon.owl.bak_round7_camranh_disambiguation` | `archive_pre_final/already_archived/data/ontology/archive/manual_cleanup_202606/taxon.owl.bak_round7_camranh_disambiguation` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `data/ontology/archive/manual_cleanup_202606/taxon.owl.bak_round8_before_sync` | `archive_pre_final/already_archived/data/ontology/archive/manual_cleanup_202606/taxon.owl.bak_round8_before_sync` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `data/ontology/archive/manual_cleanup_202606/taxon_enriched_facts_v2.owl.bak_20260418_231244` | `archive_pre_final/already_archived/data/ontology/archive/manual_cleanup_202606/taxon_enriched_facts_v2.owl.bak_20260418_231244` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `data/ontology/archive/manual_cleanup_202606/taxon_enriched_facts_v2.owl.bak_round6_location_enrichment` | `archive_pre_final/already_archived/data/ontology/archive/manual_cleanup_202606/taxon_enriched_facts_v2.owl.bak_round6_location_enrichment` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `data/ontology/archive/manual_cleanup_202606/taxon_enriched_facts_v2.owl.bak_round7_camranh_disambiguation` | `archive_pre_final/already_archived/data/ontology/archive/manual_cleanup_202606/taxon_enriched_facts_v2.owl.bak_round7_camranh_disambiguation` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `data/ontology/archive/manual_cleanup_202606/taxon_enriched_facts_v2.owl.bak_round8_before_sync` | `archive_pre_final/already_archived/data/ontology/archive/manual_cleanup_202606/taxon_enriched_facts_v2.owl.bak_round8_before_sync` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `dump_six_queries.py` | `archive_pre_final/old_debug_scripts/dump_six_queries.py` | Old debug/comparison helper tied to archived snapshots, not final runtime/evaluation. | low | ready_to_move |
| `generate_semantic_rule_candidates.py` | `archive_pre_final/old_semantic_rule_prototype/generate_semantic_rule_candidates.py` | Semantic-rule prototype/future-work artifact approved for archive; query expansion prototype remains supporting. | medium | ready_to_move |
| `hybrid_comparison.csv` | `archive_pre_final/old_debug_scripts/hybrid_comparison.csv` | Old snapshot or ad hoc result dump outside the final evaluation layout. | low | ready_to_move |
| `hybrid_results.txt` | `archive_pre_final/old_debug_scripts/hybrid_results.txt` | Old snapshot or ad hoc result dump outside the final evaluation layout. | low | ready_to_move |
| `metadata_snapshot.txt` | `archive_pre_final/old_debug_scripts/metadata_snapshot.txt` | Old snapshot or ad hoc result dump outside the final evaluation layout. | low | ready_to_move |
| `outputs/archive/manual_cleanup_202606/tmp_tb007_debug.json` | `archive_pre_final/already_archived/outputs/archive/manual_cleanup_202606/tmp_tb007_debug.json` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `outputs/archive/old_outputs/added_triples_grouped_summary.json` | `archive_pre_final/already_archived/outputs/archive/old_outputs/added_triples_grouped_summary.json` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `outputs/archive/old_outputs/added_triples_sample.json` | `archive_pre_final/already_archived/outputs/archive/old_outputs/added_triples_sample.json` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `outputs/archive/old_outputs/alias_metadata_noise_audit.json` | `archive_pre_final/already_archived/outputs/archive/old_outputs/alias_metadata_noise_audit.json` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `outputs/archive/old_outputs/alias_metadata_noise_audit_top_terms.csv` | `archive_pre_final/already_archived/outputs/archive/old_outputs/alias_metadata_noise_audit_top_terms.csv` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `outputs/archive/old_outputs/document_fact_backfill_report.csv` | `archive_pre_final/already_archived/outputs/archive/old_outputs/document_fact_backfill_report.csv` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `outputs/archive/old_outputs/document_fact_backfill_report.json` | `archive_pre_final/already_archived/outputs/archive/old_outputs/document_fact_backfill_report.json` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `outputs/archive/old_outputs/document_fact_backfill_report_facts.csv` | `archive_pre_final/already_archived/outputs/archive/old_outputs/document_fact_backfill_report_facts.csv` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `outputs/archive/old_outputs/document_fact_backfill_report_facts.json` | `archive_pre_final/already_archived/outputs/archive/old_outputs/document_fact_backfill_report_facts.json` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `outputs/archive/old_outputs/document_fact_coverage_audit.csv` | `archive_pre_final/already_archived/outputs/archive/old_outputs/document_fact_coverage_audit.csv` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `outputs/archive/old_outputs/document_fact_coverage_audit.json` | `archive_pre_final/already_archived/outputs/archive/old_outputs/document_fact_coverage_audit.json` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `outputs/archive/old_outputs/document_fact_coverage_audit_after_fact_backfill.csv` | `archive_pre_final/already_archived/outputs/archive/old_outputs/document_fact_coverage_audit_after_fact_backfill.csv` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `outputs/archive/old_outputs/document_fact_coverage_audit_after_fact_backfill.json` | `archive_pre_final/already_archived/outputs/archive/old_outputs/document_fact_coverage_audit_after_fact_backfill.json` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `outputs/archive/old_outputs/document_fact_coverage_audit_after_semantic_backfill.csv` | `archive_pre_final/already_archived/outputs/archive/old_outputs/document_fact_coverage_audit_after_semantic_backfill.csv` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `outputs/archive/old_outputs/document_fact_coverage_audit_after_semantic_backfill.json` | `archive_pre_final/already_archived/outputs/archive/old_outputs/document_fact_coverage_audit_after_semantic_backfill.json` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `outputs/archive/old_outputs/document_fact_coverage_audit_alias.csv` | `archive_pre_final/already_archived/outputs/archive/old_outputs/document_fact_coverage_audit_alias.csv` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `outputs/archive/old_outputs/document_fact_coverage_audit_alias.json` | `archive_pre_final/already_archived/outputs/archive/old_outputs/document_fact_coverage_audit_alias.json` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `outputs/archive/old_outputs/document_fact_coverage_audit_before_fact_backfill.csv` | `archive_pre_final/already_archived/outputs/archive/old_outputs/document_fact_coverage_audit_before_fact_backfill.csv` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `outputs/archive/old_outputs/document_fact_coverage_audit_before_fact_backfill.json` | `archive_pre_final/already_archived/outputs/archive/old_outputs/document_fact_coverage_audit_before_fact_backfill.json` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `outputs/archive/old_outputs/full_corpus_metadata_audit.json` | `archive_pre_final/already_archived/outputs/archive/old_outputs/full_corpus_metadata_audit.json` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `outputs/archive/old_outputs/full_corpus_metadata_audit_summary.csv` | `archive_pre_final/already_archived/outputs/archive/old_outputs/full_corpus_metadata_audit_summary.csv` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `outputs/archive/old_outputs/full_corpus_metadata_cleanup_effect_summary.json` | `archive_pre_final/already_archived/outputs/archive/old_outputs/full_corpus_metadata_cleanup_effect_summary.json` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `outputs/archive/old_outputs/full_corpus_metadata_cleanup_report.csv` | `archive_pre_final/already_archived/outputs/archive/old_outputs/full_corpus_metadata_cleanup_report.csv` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `outputs/archive/old_outputs/full_corpus_metadata_cleanup_report.json` | `archive_pre_final/already_archived/outputs/archive/old_outputs/full_corpus_metadata_cleanup_report.json` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `outputs/archive/old_outputs/full_corpus_pipeline_summary.json` | `archive_pre_final/already_archived/outputs/archive/old_outputs/full_corpus_pipeline_summary.json` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `outputs/archive/old_outputs/metadata_cleanup_effect_summary.json` | `archive_pre_final/already_archived/outputs/archive/old_outputs/metadata_cleanup_effect_summary.json` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `outputs/archive/old_outputs/metadata_cleanup_report.csv` | `archive_pre_final/already_archived/outputs/archive/old_outputs/metadata_cleanup_report.csv` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `outputs/archive/old_outputs/metadata_cleanup_report.json` | `archive_pre_final/already_archived/outputs/archive/old_outputs/metadata_cleanup_report.json` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `outputs/archive/old_outputs/metadata_normalization_report.csv` | `archive_pre_final/already_archived/outputs/archive/old_outputs/metadata_normalization_report.csv` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `outputs/archive/old_outputs/metadata_normalization_report.json` | `archive_pre_final/already_archived/outputs/archive/old_outputs/metadata_normalization_report.json` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `outputs/archive/old_outputs/new_or_used_generic_entities_review.json` | `archive_pre_final/already_archived/outputs/archive/old_outputs/new_or_used_generic_entities_review.json` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `outputs/archive/old_outputs/ontology_alias_added.json` | `archive_pre_final/already_archived/outputs/archive/old_outputs/ontology_alias_added.json` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `outputs/archive/old_outputs/ontology_alias_gap_report.csv` | `archive_pre_final/already_archived/outputs/archive/old_outputs/ontology_alias_gap_report.csv` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `outputs/archive/old_outputs/ontology_alias_gap_report.json` | `archive_pre_final/already_archived/outputs/archive/old_outputs/ontology_alias_gap_report.json` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `outputs/archive/old_outputs/pipeline_run_query_summary.json` | `archive_pre_final/already_archived/outputs/archive/old_outputs/pipeline_run_query_summary.json` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `outputs/archive/old_outputs/post_clean_metadata_cleanup_report.json` | `archive_pre_final/already_archived/outputs/archive/old_outputs/post_clean_metadata_cleanup_report.json` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `outputs/archive/old_outputs/semantic_backfill_false_positive_review.json` | `archive_pre_final/already_archived/outputs/archive/old_outputs/semantic_backfill_false_positive_review.json` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `outputs/archive/old_reports/cursor_fix_report.md` | `archive_pre_final/already_archived/outputs/archive/old_reports/cursor_fix_report.md` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `outputs/archive/old_reports/focus_two_weak_queries_report.md` | `archive_pre_final/already_archived/outputs/archive/old_reports/focus_two_weak_queries_report.md` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `outputs/archive/old_reports/focus_two_weak_queries_report_round2.md` | `archive_pre_final/already_archived/outputs/archive/old_reports/focus_two_weak_queries_report_round2.md` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `outputs/archive/old_reports/imn_lobster_fix_report.md` | `archive_pre_final/already_archived/outputs/archive/old_reports/imn_lobster_fix_report.md` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `outputs/archive/old_snapshots/focus_two_queries_after.json` | `archive_pre_final/already_archived/outputs/archive/old_snapshots/focus_two_queries_after.json` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `outputs/archive/old_snapshots/focus_two_queries_before.json` | `archive_pre_final/already_archived/outputs/archive/old_snapshots/focus_two_queries_before.json` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `outputs/archive/old_snapshots/focus_two_queries_metrics.json` | `archive_pre_final/already_archived/outputs/archive/old_snapshots/focus_two_queries_metrics.json` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `outputs/archive/old_snapshots/focus_two_queries_round2_after.json` | `archive_pre_final/already_archived/outputs/archive/old_snapshots/focus_two_queries_round2_after.json` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `outputs/archive/old_snapshots/focus_two_queries_round2_before.json` | `archive_pre_final/already_archived/outputs/archive/old_snapshots/focus_two_queries_round2_before.json` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `outputs/archive/old_snapshots/imn_lobster_after.json` | `archive_pre_final/already_archived/outputs/archive/old_snapshots/imn_lobster_after.json` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `outputs/archive/old_snapshots/imn_lobster_before.json` | `archive_pre_final/already_archived/outputs/archive/old_snapshots/imn_lobster_before.json` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `outputs/archive/old_snapshots/imn_lobster_comparison.json` | `archive_pre_final/already_archived/outputs/archive/old_snapshots/imn_lobster_comparison.json` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `outputs/archive/old_snapshots/weak_query_fix_after.json` | `archive_pre_final/already_archived/outputs/archive/old_snapshots/weak_query_fix_after.json` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `outputs/archive/old_snapshots/weak_query_fix_before.json` | `archive_pre_final/already_archived/outputs/archive/old_snapshots/weak_query_fix_before.json` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `outputs/archive/old_snapshots/weak_query_fix_comparison.json` | `archive_pre_final/already_archived/outputs/archive/old_snapshots/weak_query_fix_comparison.json` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `outputs/archive/old_verification/alias_metadata_cleanup_query_verification.json` | `archive_pre_final/already_archived/outputs/archive/old_verification/alias_metadata_cleanup_query_verification.json` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `outputs/archive/old_verification/disease_priority_queries_verification.json` | `archive_pre_final/already_archived/outputs/archive/old_verification/disease_priority_queries_verification.json` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `outputs/archive/old_verification/disease_priority_queries_verification_after_canonical_bridge.json` | `archive_pre_final/already_archived/outputs/archive/old_verification/disease_priority_queries_verification_after_canonical_bridge.json` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `outputs/archive/old_verification/disease_priority_queries_verification_after_tightening.json` | `archive_pre_final/already_archived/outputs/archive/old_verification/disease_priority_queries_verification_after_tightening.json` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `outputs/archive/old_verification/disease_priority_queries_verification_before_tightening.json` | `archive_pre_final/already_archived/outputs/archive/old_verification/disease_priority_queries_verification_before_tightening.json` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `outputs/archive/old_verification/full_corpus_query_verification.json` | `archive_pre_final/already_archived/outputs/archive/old_verification/full_corpus_query_verification.json` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `outputs/archive/old_verification/kg_runtime_verification_after_canonical_bridge.json` | `archive_pre_final/already_archived/outputs/archive/old_verification/kg_runtime_verification_after_canonical_bridge.json` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `outputs/archive/old_verification/kg_runtime_verification_after_disease_tightening.json` | `archive_pre_final/already_archived/outputs/archive/old_verification/kg_runtime_verification_after_disease_tightening.json` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `outputs/archive/old_verification/kg_runtime_verification_before_alias_enrichment.json` | `archive_pre_final/already_archived/outputs/archive/old_verification/kg_runtime_verification_before_alias_enrichment.json` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `outputs/archive/old_verification/kg_runtime_verification_before_disease_tightening.json` | `archive_pre_final/already_archived/outputs/archive/old_verification/kg_runtime_verification_before_disease_tightening.json` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `outputs/archive/old_verification/kg_runtime_verification_before_fact_backfill.json` | `archive_pre_final/already_archived/outputs/archive/old_verification/kg_runtime_verification_before_fact_backfill.json` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `outputs/archive/old_verification/kg_runtime_verification_before_semantic_backfill.json` | `archive_pre_final/already_archived/outputs/archive/old_verification/kg_runtime_verification_before_semantic_backfill.json` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `outputs/archive/old_verification/kg_runtime_verification_semantic_patch_expanded.json` | `archive_pre_final/already_archived/outputs/archive/old_verification/kg_runtime_verification_semantic_patch_expanded.json` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `outputs/archive/old_verification/kg_runtime_verification_semantic_patch_summary.json` | `archive_pre_final/already_archived/outputs/archive/old_verification/kg_runtime_verification_semantic_patch_summary.json` | Already in an archive location. Plan records it under already_archived for final-package exclusion. | low | ready_to_move |
| `outputs/candidate_fusion_experiment_summary.csv` | `archive_pre_final/old_candidate_fusion_v1/candidate_fusion_experiment_summary.csv` | Candidate-fusion v1 artifact superseded by experiments/run_hybrid_candidate_fusion.py and current candidate-fusion reports/metrics. | low | ready_to_move |
| `outputs/candidate_fusion_experiment_summary.json` | `archive_pre_final/old_candidate_fusion_v1/candidate_fusion_experiment_summary.json` | Candidate-fusion v1 artifact superseded by experiments/run_hybrid_candidate_fusion.py and current candidate-fusion reports/metrics. | low | ready_to_move |
| `outputs/candidate_fusion_experiment_summary.md` | `archive_pre_final/old_candidate_fusion_v1/candidate_fusion_experiment_summary.md` | Candidate-fusion v1 artifact superseded by experiments/run_hybrid_candidate_fusion.py and current candidate-fusion reports/metrics. | low | ready_to_move |
| `outputs/candidate_fusion_per_query_delta.csv` | `archive_pre_final/old_candidate_fusion_v1/candidate_fusion_per_query_delta.csv` | Candidate-fusion v1 artifact superseded by experiments/run_hybrid_candidate_fusion.py and current candidate-fusion reports/metrics. | low | ready_to_move |
| `outputs/document_fact_backfill_report.csv` | `archive_pre_final/old_metadata_outputs/document_fact_backfill_report.csv` | Intermediate metadata/backfill output superseded by cleaned metadata and current coverage audits. | low | ready_to_move |
| `outputs/document_fact_backfill_report.json` | `archive_pre_final/old_metadata_outputs/document_fact_backfill_report.json` | Intermediate metadata/backfill output superseded by cleaned metadata and current coverage audits. | low | ready_to_move |
| `outputs/figures/fig_hybrid_vector_metadata_delta_by_group.png` | `archive_pre_final/old_figures/fig_hybrid_vector_metadata_delta_by_group.png` | Figure is not in the expected final figure list and no reference was found outside audit files; archive if the main report does not use it. | medium | ready_to_move |
| `outputs/metadata_normalization_report.csv` | `archive_pre_final/old_metadata_outputs/metadata_normalization_report.csv` | Intermediate metadata/backfill output superseded by cleaned metadata and current coverage audits. | low | ready_to_move |
| `outputs/metadata_normalization_report.json` | `archive_pre_final/old_metadata_outputs/metadata_normalization_report.json` | Intermediate metadata/backfill output superseded by cleaned metadata and current coverage audits. | low | ready_to_move |
| `outputs/semantic_patch_final_assessment.md` | `archive_pre_final/old_semantic_patch/semantic_patch_final_assessment.md` | Old semantic-patch/runtime-ontology artifact. Final ontology remains data/ontology/taxon_enriched_facts_v2.owl. | medium | ready_to_move |
| `outputs/semantic_rule_candidate_facts.csv` | `archive_pre_final/old_semantic_rule_prototype/semantic_rule_candidate_facts.csv` | Semantic-rule prototype/future-work artifact approved for archive; query expansion prototype remains supporting. | medium | ready_to_move |
| `outputs/semantic_rule_candidate_facts.json` | `archive_pre_final/old_semantic_rule_prototype/semantic_rule_candidate_facts.json` | Semantic-rule prototype/future-work artifact approved for archive; query expansion prototype remains supporting. | medium | ready_to_move |
| `outputs/semantic_rule_candidate_facts.md` | `archive_pre_final/old_semantic_rule_prototype/semantic_rule_candidate_facts.md` | Semantic-rule prototype/future-work artifact approved for archive; query expansion prototype remains supporting. | medium | ready_to_move |
| `outputs/semantic_rule_scoring_opportunities.csv` | `archive_pre_final/old_semantic_rule_prototype/semantic_rule_scoring_opportunities.csv` | Semantic-rule prototype/future-work artifact approved for archive; query expansion prototype remains supporting. | medium | ready_to_move |
| `outputs/semantic_rules_and_label_strategy.md` | `archive_pre_final/old_semantic_rule_prototype/semantic_rules_and_label_strategy.md` | Semantic-rule prototype/future-work artifact approved for archive; query expansion prototype remains supporting. | medium | ready_to_move |
| `outputs/taxon_enriched_facts_v2_backfilled_runtime.owl` | `archive_pre_final/old_semantic_patch/taxon_enriched_facts_v2_backfilled_runtime.owl` | Old semantic-patch/runtime-ontology artifact. Final ontology remains data/ontology/taxon_enriched_facts_v2.owl. | medium | ready_to_move |
| `run_candidate_fusion_experiment.py` | `archive_pre_final/old_candidate_fusion_v1/run_candidate_fusion_experiment.py` | Candidate-fusion v1 artifact superseded by experiments/run_hybrid_candidate_fusion.py and current candidate-fusion reports/metrics. | low | ready_to_move |
| `vector_store_backup_round10/chunks.index` | `archive_pre_final/vector_store_backups/vector_store_backup_round10/chunks.index` | Historical vector-store backup. Current runtime vector_store/ is protected; backup can be moved after approval. | medium | ready_to_move |
| `vector_store_backup_round10/chunks_meta.pkl` | `archive_pre_final/vector_store_backups/vector_store_backup_round10/chunks_meta.pkl` | Historical vector-store backup. Current runtime vector_store/ is protected; backup can be moved after approval. | medium | ready_to_move |
| `vector_store_backup_round10/config.pkl` | `archive_pre_final/vector_store_backups/vector_store_backup_round10/config.pkl` | Historical vector-store backup. Current runtime vector_store/ is protected; backup can be moved after approval. | medium | ready_to_move |
| `vector_store_backup_round11_after_tb_fix/chunks.index` | `archive_pre_final/vector_store_backups/vector_store_backup_round11_after_tb_fix/chunks.index` | Historical vector-store backup. Current runtime vector_store/ is protected; backup can be moved after approval. | medium | ready_to_move |
| `vector_store_backup_round11_after_tb_fix/chunks_meta.pkl` | `archive_pre_final/vector_store_backups/vector_store_backup_round11_after_tb_fix/chunks_meta.pkl` | Historical vector-store backup. Current runtime vector_store/ is protected; backup can be moved after approval. | medium | ready_to_move |
| `vector_store_backup_round11_after_tb_fix/config.pkl` | `archive_pre_final/vector_store_backups/vector_store_backup_round11_after_tb_fix/config.pkl` | Historical vector-store backup. Current runtime vector_store/ is protected; backup can be moved after approval. | medium | ready_to_move |
| `vector_store_backup_round12_after_ria3_fix/chunks.index` | `archive_pre_final/vector_store_backups/vector_store_backup_round12_after_ria3_fix/chunks.index` | Historical vector-store backup. Current runtime vector_store/ is protected; backup can be moved after approval. | medium | ready_to_move |
| `vector_store_backup_round12_after_ria3_fix/chunks_meta.pkl` | `archive_pre_final/vector_store_backups/vector_store_backup_round12_after_ria3_fix/chunks_meta.pkl` | Historical vector-store backup. Current runtime vector_store/ is protected; backup can be moved after approval. | medium | ready_to_move |
| `vector_store_backup_round12_after_ria3_fix/config.pkl` | `archive_pre_final/vector_store_backups/vector_store_backup_round12_after_ria3_fix/config.pkl` | Historical vector-store backup. Current runtime vector_store/ is protected; backup can be moved after approval. | medium | ready_to_move |

## Hold

| source_path | proposed_archive_path | reason | risk_level | action_status |
|---|---|---|---|---|
| `.vscode/settings.json` |  | Requires explicit confirmation before any archive action. | medium | hold |
| `analyze_ontology_alias_gaps.py` |  | Hold by user rule: keep for provenance/regeneration or because final use is not fully decided. | medium | hold |
| `analyze_query_understanding_profiles.py` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `audit_alias_and_metadata_noise.py` |  | Hold by user rule: keep for provenance/regeneration or because final use is not fully decided. | medium | hold |
| `audit_document_fact_coverage.py` |  | Hold by user rule: keep for provenance/regeneration or because final use is not fully decided. | medium | hold |
| `backfill_document_facts_from_metadata.py` |  | Hold by user rule: keep for provenance/regeneration or because final use is not fully decided. | medium | hold |
| `clean_metadata_for_entity_matching.py` |  | Hold by user rule: keep for provenance/regeneration or because final use is not fully decided. | medium | hold |
| `compute_core_metrics.py` |  | Requires explicit confirmation before any archive action. | medium | hold |
| `data/eval/analysis/baseline_strengths_by_group.csv` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `data/eval/analysis/error_analysis_and_final_improvement_plan.md` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `data/eval/analysis/final_technical_iteration_report.md` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `data/eval/analysis/query_failure_buckets.csv` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `data/eval/competency_questions_core.csv` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `data/eval/final_active_files_manifest.csv` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `data/eval/final_freeze_report.md` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `data/eval/final_query_set.csv` |  | Hold by user rule: keep for provenance/regeneration or because final use is not fully decided. | medium | hold |
| `data/eval/final_query_set_extended.csv` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `data/eval/final_query_set_notes.md` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `data/eval/metrics/baseline_latency_per_query.csv` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `data/eval/metrics/baseline_metrics_by_group_extended.csv` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `data/eval/metrics/baseline_metrics_by_group_plus.csv` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `data/eval/metrics/baseline_metrics_by_query_extended.csv` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `data/eval/metrics/baseline_metrics_by_query_plus.csv` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `data/eval/metrics/baseline_metrics_summary_extended.csv` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `data/eval/metrics/baseline_metrics_summary_plus.csv` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `data/eval/metrics/compute_core_metrics.py` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `data/eval/metrics/hybrid_candidate_fusion_metrics_by_group.csv` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `data/eval/metrics/hybrid_candidate_fusion_metrics_by_query.csv` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `data/eval/metrics/hybrid_candidate_fusion_metrics_summary.csv` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `data/eval/metrics/kg_ablation_metrics_by_group.csv` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `data/eval/metrics/kg_ablation_metrics_by_query.csv` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `data/eval/metrics/kg_ablation_metrics_summary.csv` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `data/eval/metrics/metrics_notes.md` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `data/eval/project_final_readiness_check.md` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `data/eval/relevance_guidelines_core.md` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `data/eval/relevance_judgments_core_summary.md` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `data/eval/relevance_judgments_extended.csv` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `data/eval/results/baseline_hybrid_candidate_fusion_core.csv` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `data/eval/results/baseline_hybrid_candidate_fusion_extended.csv` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `data/eval/results/baseline_hybrid_extended.csv` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `data/eval/results/baseline_lexical_extended.csv` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `data/eval/results/baseline_ontology_sparql_extended.csv` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `data/eval/results/baseline_vector_extended.csv` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `data/eval/results/baseline_vector_metadata_extended.csv` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `data/eval/results/baseline_vector_metadata_kg_no_intent_core.csv` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `data/eval/results/kg_ablation_results_core.csv` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `data/eval/results/results_generation_notes.md` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `data/metadata/document_metadata.xlsx` |  | Hold by user rule: keep for provenance/regeneration or because final use is not fully decided. | medium | hold |
| `data/ontology/mapping_report.csv` |  | Hold by user rule: keep for provenance/regeneration or because final use is not fully decided. | medium | hold |
| `data/ontology/taxon.owl` |  | Hold by user rule: keep for provenance/regeneration or because final use is not fully decided. | medium | hold |
| `data/ontology/taxon_enriched.owl` |  | Not included in approved archive-now set. | low | hold |
| `data/ontology/taxon_enriched_aliases.owl` |  | Not included in approved archive-now set. | low | hold |
| `data/ontology/taxon_enriched_facts.owl` |  | Not included in approved archive-now set. | low | hold |
| `data/ontology/taxon_enriched_semantic.owl` |  | Not included in approved archive-now set. | low | hold |
| `enrich_ontology_aliases.py` |  | Requires explicit confirmation before any archive action. | medium | hold |
| `enrich_ontology_semantic_entities.py` |  | Requires explicit confirmation before any archive action. | medium | hold |
| `evaluate_competency_questions.py` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `experiments/analyze_kg_score_components.py` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `experiments/compute_baseline_metrics_plus.py` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `experiments/generate_query_expansion_examples.py` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `experiments/run_extended_evaluation.py` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `experiments/run_hybrid_candidate_fusion.py` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `experiments/run_kg_ablation.py` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `full_corpus_metadata_audit.py` |  | Requires explicit confirmation before any archive action. | medium | hold |
| `full_corpus_metadata_cleanup.py` |  | Requires explicit confirmation before any archive action. | medium | hold |
| `full_corpus_pipeline_summary.py` |  | Requires explicit confirmation before any archive action. | medium | hold |
| `full_corpus_query_verification.py` |  | Requires explicit confirmation before any archive action. | medium | hold |
| `generate_error_analysis_core.py` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `generate_evaluation_layers_summary.py` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `measure_core_baseline_latency.py` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `outputs/baseline_metrics_plus_report.md` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `outputs/competency_questions_results.csv` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `outputs/competency_questions_summary.json` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `outputs/document_fact_coverage_audit.csv` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `outputs/document_fact_coverage_audit.json` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `outputs/error_analysis_core.csv` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `outputs/error_analysis_summary.json` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `outputs/evaluation_layers_summary.json` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `outputs/evaluation_layers_summary.md` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `outputs/extended_query_evaluation_report.md` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `outputs/extended_query_judgment_audit.md` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `outputs/figures/fig_ablation_key_metrics.pdf` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `outputs/figures/fig_ablation_key_metrics.png` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `outputs/figures/fig_baseline_key_metrics.pdf` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `outputs/figures/fig_baseline_key_metrics.png` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `outputs/figures/fig_candidate_fusion_summary.png` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `outputs/figures/fig_extended_evaluation_summary.png` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `outputs/figures/fig_hybrid_vs_vector_metadata_by_group.pdf` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `outputs/figures/fig_hybrid_vs_vector_metadata_by_group.png` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `outputs/figures/fig_kg_ablation_summary.png` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `outputs/figures/fig_kg_runtime_contribution_summary.png` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `outputs/figures/fig_kg_score_components.png` |  | Reclassified from KEEP_FINAL to KEEP_SUPPORTING: diagnostic figure, useful as supporting evidence but not archive-ready. | medium | hold |
| `outputs/figures/fig_quality_latency_tradeoff.pdf` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `outputs/figures/fig_quality_latency_tradeoff.png` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `outputs/figures/fig_query_expansion_examples.png` |  | Reclassified from KEEP_FINAL to KEEP_SUPPORTING: query expansion is future-work/prototype, not final runtime. | medium | hold |
| `outputs/final_score_formula_and_runtime_flow.md` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `outputs/final_submission_file_checklist.md` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `outputs/hybrid_candidate_fusion_analysis.md` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `outputs/hybrid_vs_vector_metadata_by_group.csv` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `outputs/hybrid_vs_vector_metadata_by_group.md` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `outputs/kg_ablation_analysis.md` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `outputs/kg_runtime_verification.json` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `outputs/kg_score_component_analysis.csv` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `outputs/kg_score_component_analysis.md` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `outputs/ontology_quality_check.json` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `outputs/ontology_quality_check.md` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `outputs/ontology_reasoner_consistency_check.json` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `outputs/ontology_reasoner_consistency_check.md` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `outputs/query_expansion_design.md` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `outputs/query_expansion_examples.csv` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `outputs/query_understanding_profiles.csv` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `outputs/query_understanding_profiles.json` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `outputs/query_understanding_profiles.md` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `outputs/streamlit_demo_notes.md` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `outputs/wilcoxon_hybrid_vs_vector_metadata.csv` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `outputs/wilcoxon_hybrid_vs_vector_metadata.json` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `outputs/wilcoxon_hybrid_vs_vector_metadata.md` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `post_clean_metadata_cleanup.py` |  | Requires explicit confirmation before any archive action. | medium | hold |
| `README.md` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `run_wilcoxon_significance_test.py` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `semantic_normalization.py` |  | Hold by user rule: keep for provenance/regeneration or because final use is not fully decided. | medium | hold |
| `sync_metadata_to_owl.py` |  | Hold by user rule: keep for provenance/regeneration or because final use is not fully decided. | medium | hold |
| `validate_semantic_patch.py` |  | Hold by user rule: keep for provenance/regeneration or because final use is not fully decided. | medium | hold |
| `verify_disease_priority_queries.py` |  | Requires explicit confirmation before any archive action. | medium | hold |
| `verify_kg_runtime.py` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `verify_ontology_quality.py` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `verify_ontology_reasoner_consistency.py` |  | Keep for final/supporting package; not part of approved archive-now set. | low | hold |
| `verify_queries_after_alias_metadata_cleanup.py` |  | Requires explicit confirmation before any archive action. | medium | hold |

## Never Touch

| source_path | proposed_archive_path | reason | risk_level | action_status |
|---|---|---|---|---|
| `.streamlit/config.toml` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `app_streamlit.py` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/eval/final_query_set_core.csv` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/eval/metrics/baseline_latency_summary.csv` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/eval/metrics/baseline_metrics_by_group.csv` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/eval/metrics/baseline_metrics_per_query.csv` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/eval/metrics/baseline_metrics_summary.csv` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/eval/relevance_judgments_core.csv` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/eval/results/baseline_hybrid_core.csv` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/eval/results/baseline_lexical_core.csv` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/eval/results/baseline_ontology_sparql_core.csv` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/eval/results/baseline_vector_core.csv` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/eval/results/baseline_vector_metadata_core.csv` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/metadata/document_metadata_cleaned.xlsx` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/ontology/taxon_enriched_facts_v2.owl` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/BIOLOGY_001_biology13100758.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/FAO_001_cb2119en.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/FAO_002_a1152e.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/FAO_003_ca2976en.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/FAO_004_cc6858en.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/FAO_005_y5040e.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/FAO_006_bt131e.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/FAO_007_cd8164en.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/FAO_008_cb8926en.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/FAO_009_y1679e.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/FAO_010_ca6052en.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/FAO_011_ad824e.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/FAO_012_ad505e.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/FAO_013_y5325e.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/FAO_014_cd8658en.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/FAO_015_t0411e.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/FAO_016_cd7559en.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/FAO_017_ca7588en.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/FAO_018_t1623e.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/FAO_019_i0490e.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/FAO_020_i2571e.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/FAO_021_cd8667en.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/FAO_022_i1750e.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/FAO_023_i0970e.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/FAO_024_u3100e.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/FAO_025_a0366e.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/FAO_026_br813e.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/FAO_027_cd6476en.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/FAO_028_i3569e.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/FAO_029_i9705en.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/FAO_031_cd8563en.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/FAO_032_cd8633en.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/FAO_033_cc6625en.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/FAO_034_ca2705en.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/FAO_035_w3594e.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/FAO_036_i1137e.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/FAO_037_na265en.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/FAO_038_ca6702en.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/FAO_039_ad893e.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/FAO_040_i8064en.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/FAO_041_cd3785en.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/FAO_042_biosecurity_philippines.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/FAO_042_i3720e.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/FAO_043_boosting_biosecurity_peru.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/FAO_044_i2734e03i.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/FAO_045_ca6163en.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/IJMS_001_ijms26178478.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/NACA_001_1737869839.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/NACA_002_1749824700.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/NACA_003_1494554353.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/PLOS_001_pone.0091930.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/PMC_001_PMC10820212.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/PMC_002_PMC6963587.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/PMC_003_PMC11657822.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/PMC_004_PMC12128546.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/PMC_005_PMC12552485.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/PMC_006_PMC8042889.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/PMC_007_PMC8067269.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/PMC_008_PMC11611405.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/PMC_009_PMC12030750.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/PMC_010_PMC7409025.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/PMC_011_PMC5742833.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/PMC_012_PMC7223513.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/PMC_013_PMC12825151.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/PMC_014_PMC9531857.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/PMC_015_PMC12006376.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/PMC_016_PMC4815145.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/PMC_017_PMC11223889.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/PMC_018_PMC12008197.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/PMC_019_PMC6797625.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/PMC_020_PMC10701378.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/PMC_021_PMC9427843.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/PMC_022_PMC11081493.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/PMC_023_PMC10229113.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/PMC_024_PMC9139878.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/PMC_025_PMC4510448.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/PMC_026_PMC11205452.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/PMC_027_PMC12745081.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/PMC_028_PMC5603525.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/PMC_029_PMC6955853.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/PMC_030_PMC10476614.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/PMC_031_PMC91383.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/PMC_032_PMC12435696.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/PMC_033_PMC8339124.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/PMC_034_PMC10141217.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/PMC_035_PMC11861540.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/PMC_036_PMC9125206.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/RIA3_001_quy_hoach_nuoi_tom_hum_2030.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/RIA3_002_TBKQ_QTDX_PhuYen_KhanhHoa_17112023.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/RIA3_003_TBKQ_QTMT_DOT14_T6_2025.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/SEAFDEC_001_DharAK2021.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/SEAFDEC_002_Wong2016.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/SEAFDEC_003_Yuasa2016.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/SEAFDEC_004_sp15-3.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/SEAFDEC_005_WahSLP2016.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/SEAFDEC_006_Apostol2016.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/SEAFDEC_007_Penir2019.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/SEAFDEC_008_Putth2016.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/SEAFDEC_009_Hastuti2016.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/SEAFDEC_010_Hirono2016.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/SEAFDEC_011_Kua2016.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/TB_001_NyanTawCRSDCaMau.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/TB_002_cong_nghe_gen_va_chon_giong_tom_khang_benh.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/TB_003_co_che_co_ban_cua_nhiem_don_le_va_dong_nhiem_DIV1_va_WSSV_o_tom_the_chan_trang.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/TB_004_hoai_tu_co_o_tom_the_chan_trang.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/TB_005_su_hien_dien_cua_benh_dom_trang_va_EHP_va_AHPND_tai_DBSCL_2022_2024.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/TB_006_hoai_tu_co_IMNV_tren_tom_va_chien_luoc_kiem_soat.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/TB_007_benh_dom_trang_o_tom_nuoi_va_cong_nghe_nuoi_tom_nham_phong_benh_dom_trang.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/TCKHTS_001.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `data/raw_docs/TCTS_001_024286.pdf` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `hybrid_search.py` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `kg_runtime.py` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `run_core_baselines.py` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `vector_search.py` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `vector_store/chunks.index` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `vector_store/chunks_meta.pkl` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |
| `vector_store/config.pkl` |  | Protected by user rule: final runtime/data/source corpus/evaluation source-of-truth. Do not move. | high | never_touch |

## Execution Notes

- This is only a move plan. It intentionally does not create `archive_pre_final/` and does not move anything into it.
- Before executing later, review every `risk_level=medium` row, especially vector-store backups, semantic patch artifacts, semantic-rule prototype artifacts, and `fig_hybrid_vector_metadata_delta_by_group.png`.
- Keep all `never_touch` rows out of any archive command.
- Use literal paths if a later move script is created, and verify destination paths stay inside `archive_pre_final/` before moving.
