# Figures and supplementary diagnostics update report for 138-doc snapshot

## Executive summary

| metric | value | detail |
| --- | --- | --- |
| status | PARTIAL | Priority/main and diagnostic figures are current; optional experiment figures are stale unless rerun. |
| figures_audited | 17 |  |
| figures_current_138 | 13 |  |
| figures_optional_or_future_work | 4 |  |
| diagnostics_rerun | 4 | corpus topic, KG score components/runtime contribution, explanation quality, KG ablation |
| diagnostics_not_rerun_optional | 3 | candidate fusion, extended evaluation, query expansion |
| candidate_fusion_removed_docs_present | RIA3_002; RIA3_003 | Do not use without rerun. |
| can_proceed_to_report_editing | PARTIAL | Yes for current figures; exclude or rerun stale optional experiment figures. |
| backup_folder | archive_pre_final/before_138docs_supplementary_rerun_20260531_135152 |  |

Không sửa metadata/raw docs/vector store/KG/runtime/scoring và không sửa báo cáo Word/LaTeX trong bước này.

## Figure audit table

| file_name | size_bytes | modified_time | figure_group | current_138_status | likely_old_110_or_pre138 | recommended_use |
| --- | --- | --- | --- | --- | --- | --- |
| fig_ablation_key_metrics.pdf | 17054 | 2026-05-31 13:53:46 | KG ablation | KEEP_CURRENT_138 | No | supporting diagnostic / Chapter 4 if used |
| fig_ablation_key_metrics.png | 56453 | 2026-05-31 13:53:46 | KG ablation | KEEP_CURRENT_138 | No | supporting diagnostic / Chapter 4 if used |
| fig_baseline_key_metrics.pdf | 17444 | 2026-05-31 13:42:24 | core metrics | KEEP_CURRENT_138 | No | main report |
| fig_baseline_key_metrics.png | 57448 | 2026-05-31 13:42:24 | core metrics | KEEP_CURRENT_138 | No | main report |
| fig_candidate_fusion_summary.png | 159510 | 2026-05-27 09:55:27 | candidate fusion | OPTIONAL_RERUN | Yes - pre-138 and result contains removed docs | supporting/future work only |
| fig_corpus_topic_distribution.png | 77234 | 2026-05-31 13:52:09 | corpus topic distribution | KEEP_CURRENT_138 | No | main/supporting corpus description |
| fig_explanation_quality_summary.png | 69459 | 2026-05-31 13:53:02 | explanation quality | KEEP_CURRENT_138 | No | supporting diagnostic |
| fig_extended_evaluation_summary.png | 183330 | 2026-05-27 10:22:26 | extended evaluation | OPTIONAL_RERUN | Yes - pre-138/unknown snapshot | supporting only if rerun |
| fig_hybrid_vs_vector_metadata_by_group.pdf | 15667 | 2026-05-31 13:42:25 | group comparison | KEEP_CURRENT_138 | No | main report |
| fig_hybrid_vs_vector_metadata_by_group.png | 95905 | 2026-05-31 13:42:25 | group comparison | KEEP_CURRENT_138 | No | main report |
| fig_kg_ablation_summary.png | 179322 | 2026-05-31 13:53:14 | KG ablation | KEEP_CURRENT_138 | No | supporting diagnostic / Chapter 4 if used |
| fig_kg_runtime_contribution_summary.png | 94105 | 2026-05-31 13:53:46 | KG diagnostics | KEEP_CURRENT_138 | No | supporting diagnostic |
| fig_kg_score_components.png | 136838 | 2026-05-31 13:52:34 | KG diagnostics | KEEP_CURRENT_138 | No | supporting diagnostic |
| fig_quality_latency_tradeoff.pdf | 18780 | 2026-05-31 13:42:25 | latency/tradeoff | KEEP_CURRENT_138 | No | main report |
| fig_quality_latency_tradeoff.png | 64486 | 2026-05-31 13:42:25 | latency/tradeoff | KEEP_CURRENT_138 | No | main report |
| fig_query_expansion_examples.png | 190973 | 2026-05-27 10:50:20 | query expansion | FUTURE_WORK_ONLY | Yes - pre-138/optional experiment | future work only unless rerun |
| fig_query_expansion_experiment_summary.png | 79146 | 2026-05-29 22:31:06 | query expansion | FUTURE_WORK_ONLY | Yes - pre-138/optional experiment | future work only unless rerun |

## Regenerated diagnostics summary

| diagnostic | script | status | key_numbers | figure_updated | caveat |
| --- | --- | --- | --- | --- | --- |
| Corpus topic distribution | experiments/analyze_corpus_topic_distribution.py | PASS | total_docs=138; species_taxon_specific=137; aquatic_disease=106; biosecurity_management=63 | outputs/figures/fig_corpus_topic_distribution.png | Multi-label topic counts; totals exceed corpus size. |
| KG score components | experiments/analyze_kg_score_components.py | PASS | rows=280; queries=28; kg_score_positive_rate=0.614; direct_fact_rate=0.604; relation_rate=0.318 | outputs/figures/fig_kg_score_components.png; outputs/figures/fig_kg_runtime_contribution_summary.png | Diagnostic approximation; final hybrid scoring unchanged. |
| Explanation quality | experiments/evaluate_explanation_quality.py | PASS | n_queries=28; n_rows=280; has_explanation_rate=1.000; kg_evidence_rate=0.614 | outputs/figures/fig_explanation_quality_summary.png | Automatic diagnostic, not a user study. |
| KG ablation fixed-pool | experiments/run_kg_ablation.py | PASS | results_rows=1400; methods=5; full_hybrid_ndcg10=0.711; full_kg_no_intent_ndcg10=0.669 | outputs/figures/fig_kg_ablation_summary.png; outputs/figures/fig_ablation_key_metrics.png/pdf | Fixed hybrid Top-10 pool; not an official baseline. |

## Corpus topic distribution 138 docs

| topic_group | n_documents | percentage_of_corpus |
| --- | --- | --- |
| aquatic_disease | 106 | 76.81 |
| marine_aquaculture | 23 | 16.67 |
| hatchery_seed_production | 21 | 15.22 |
| biosecurity_management | 63 | 45.65 |
| environment_water_quality | 28 | 20.29 |
| local_vietnam_khanhhoa | 39 | 28.26 |
| species_taxon_specific | 137 | 99.28 |
| general_policy_technical | 0 | 0 |
| uncategorized | 0 | 0 |

Caveat: topic labels are multi-label rules from metadata; percentages can sum above 100%. Corpus is skewed toward disease/taxon-specific aquaculture documents.

## KG diagnostic 138 docs

| metric | value |
| --- | --- |
| rows analyzed | 280 |
| queries | 28 |
| KG score > 0 rate | 0.614 |
| direct fact evidence rate | 0.604 |
| relation/context evidence rate | 0.318 |
| explanation evidence rate | 0.614 |

Diagnostic is recomputed over the current hybrid Top-10: 28 queries x 10 rows = 280 rows, using the 138-doc ontology runtime.

## Explanation diagnostic 138 docs

| metric | value |
| --- | --- |
| n_queries | 28 |
| n_rows | 280 |
| has_explanation_rate | 1.000 |
| has_metadata_evidence_rate | 0.793 |
| has_kg_evidence_rate | 0.614 |
| mean_evidence_count | 10.393 |

This is an automatic diagnostic over generated explanations, not a human explanation-quality study.

## KG ablation diagnostic 138 docs

| method | num_queries | p_at_1 | mrr | ndcg_at_10 | map |
| --- | --- | --- | --- | --- | --- |
| vector_metadata | 28 | 0.6071 | 0.7292 | 0.6104 | 0.3992 |
| kg_direct_only | 28 | 0.6786 | 0.7821 | 0.6629 | 0.4305 |
| kg_relation_only | 28 | 0.6429 | 0.7518 | 0.6206 | 0.399 |
| full_kg_no_intent | 28 | 0.75 | 0.8226 | 0.6686 | 0.4324 |
| full_hybrid | 28 | 0.8214 | 0.875 | 0.711 | 0.4566 |

The ablation is fixed-pool over the current hybrid Top-10 candidates; it is supporting analysis, not an official baseline.

## Optional outputs not rerun

| diagnostic | result_path | result_exists | result_rows | queries | removed_docs_present | figure_path | figure_exists | figure_modified_time | status | recommendation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| candidate_fusion | data/eval/results/baseline_hybrid_candidate_fusion_core.csv | True | 280 | 28 | RIA3_002; RIA3_003 | outputs/figures/fig_candidate_fusion_summary.png | True | 2026-05-27 09:55:27 | NEEDS_RERUN_IF_USED_IN_REPORT | Do not use as final evidence unless rerun for 138-doc snapshot. |
| extended_evaluation | data/eval/results/baseline_hybrid_extended.csv | True | 951 | 96 |  | outputs/figures/fig_extended_evaluation_summary.png | True | 2026-05-27 10:22:26 | NEEDS_RERUN_IF_USED_IN_REPORT | Do not use as final evidence unless rerun for 138-doc snapshot. |
| query_expansion | data/eval/results/baseline_hybrid_query_expansion_core.csv | True | 280 | 28 |  | outputs/figures/fig_query_expansion_experiment_summary.png | True | 2026-05-29 22:31:06 | FUTURE_WORK_ONLY_OR_RERUN_IF_USED | Do not use as final evidence unless rerun for 138-doc snapshot. |

Candidate fusion, extended evaluation, and query expansion should be rerun only if they will be cited as final quantitative evidence. Otherwise, move them to supporting/future work and avoid using stale metrics.

## Figure captions for report

| file_name | caption_vi | recommended_use |
| --- | --- | --- |
| fig_ablation_key_metrics.pdf | So sánh các cấu hình KG ablation fixed-pool theo metric chính. | supporting diagnostic / Chapter 4 if used |
| fig_ablation_key_metrics.png | So sánh các cấu hình KG ablation fixed-pool theo metric chính. | supporting diagnostic / Chapter 4 if used |
| fig_baseline_key_metrics.pdf | So sánh các chỉ số truy hồi chính trên 28 truy vấn core cho corpus 138 tài liệu. | main report |
| fig_baseline_key_metrics.png | So sánh các chỉ số truy hồi chính trên 28 truy vấn core cho corpus 138 tài liệu. | main report |
| fig_corpus_topic_distribution.png | Phân bố chủ đề đa nhãn của corpus 138 tài liệu thủy sản. | main/supporting corpus description |
| fig_explanation_quality_summary.png | Tóm tắt độ phủ giải thích tự động cho Hybrid Top-10. | supporting diagnostic |
| fig_hybrid_vs_vector_metadata_by_group.pdf | So sánh nDCG@10 giữa Hybrid và Vector+Metadata theo nhóm truy vấn. | main report |
| fig_hybrid_vs_vector_metadata_by_group.png | So sánh nDCG@10 giữa Hybrid và Vector+Metadata theo nhóm truy vấn. | main report |
| fig_kg_ablation_summary.png | Kết quả KG ablation fixed-pool trên Top-10 Hybrid, dùng như diagnostic hỗ trợ. | supporting diagnostic / Chapter 4 if used |
| fig_kg_runtime_contribution_summary.png | Tỷ lệ hàng Top-10 Hybrid có bằng chứng KG trực tiếp, quan hệ/ngữ cảnh và giải thích. | supporting diagnostic |
| fig_kg_score_components.png | Phân rã đóng góp điểm KG trong Top-10 Hybrid trên 28 truy vấn core. | supporting diagnostic |
| fig_quality_latency_tradeoff.pdf | Quan hệ giữa chất lượng truy hồi nDCG@10 và độ trễ trung bình. | main report |
| fig_quality_latency_tradeoff.png | Quan hệ giữa chất lượng truy hồi nDCG@10 và độ trễ trung bình. | main report |

## Problems / warnings

| severity | scope | issue |
| --- | --- | --- |
| WARNING | candidate_fusion | Existing candidate fusion results include RIA3_002/RIA3_003 and are pre-138; do not use as final evidence without rerun. |
| WARNING | extended/query_expansion | Extended evaluation and query expansion figures are pre-138 or unknown snapshot; use only as future work unless rerun. |
| INFO | diagnostics | KG ablation is fixed-pool diagnostic, not official baseline. |
| INFO | figures | Core and priority supplementary figures are current for the 138-doc snapshot. |

## Next step recommendation

Có thể bắt đầu sửa báo cáo nếu chỉ dùng các figure/current diagnostics đã đánh dấu KEEP_CURRENT_138. Nếu muốn trình bày candidate fusion, extended evaluation hoặc query expansion như kết quả thực nghiệm final, cần rerun riêng các phần đó cho snapshot 138 docs.

## Output files

- `outputs/figures_and_supplementary_rerun_138docs_report.md`
- `outputs/figures_and_supplementary_rerun_138docs_summary.csv`
- `outputs/figures_138docs_audit.csv`
- `outputs/supplementary_outputs_138docs_check.csv`
- `outputs/figures_and_supplementary_rerun_138docs_backup_manifest.csv`