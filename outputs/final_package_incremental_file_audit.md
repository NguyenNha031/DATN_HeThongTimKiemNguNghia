# Final package incremental file audit

Generated at: `2026-05-29T22:40:40`

## 1. M?c ti?u

Audit n?y r? so?t c?c file report/result/figure/script m?i ???c t?o sau khi `final_submission_package/` ?? ???c assemble. M?c ti?u l? x?c ??nh file n?o ?ang c? trong project g?c nh?ng ch?a c? trong package ?? chu?n b? cho b??c copy b? sung sau n?y. B??c n?y ch? l?p danh s?ch; kh?ng copy, move, delete, rename ho?c s?a file n?o.

## 2. Summary

- Total files checked: **26**
- needs_copy: **26**
- already_in_package: **0**
- missing_source: **0**
- review_before_copy: **0**

## 3. Files recommended to copy

### corpus_topic_distribution

| relative_path | group | risk_level | reason |
|---|---|---|---|
| `experiments/analyze_corpus_topic_distribution.py` | corpus_topic_distribution | low | New supporting experiment/audit script for report reproducibility. |
| `outputs/corpus_topic_distribution.csv` | corpus_topic_distribution | low | New report/result/figure created after final package was assembled and relevant to final report. |
| `outputs/corpus_topic_distribution_by_source.csv` | corpus_topic_distribution | low | New report/result/figure created after final package was assembled and relevant to final report. |
| `outputs/corpus_topic_distribution_by_location.csv` | corpus_topic_distribution | low | New report/result/figure created after final package was assembled and relevant to final report. |
| `outputs/corpus_topic_distribution_document_labels.csv` | corpus_topic_distribution | low | New report/result/figure created after final package was assembled and relevant to final report. |
| `outputs/corpus_topic_distribution_report.md` | corpus_topic_distribution | low | New report/result/figure created after final package was assembled and relevant to final report. |
| `outputs/figures/fig_corpus_topic_distribution.png` | corpus_topic_distribution | low | New report/result/figure created after final package was assembled and relevant to final report. |

### explanation_quality_diagnostic

| relative_path | group | risk_level | reason |
|---|---|---|---|
| `experiments/evaluate_explanation_quality.py` | explanation_quality_diagnostic | low | New supporting experiment/audit script for report reproducibility. |
| `outputs/explanation_quality_summary.csv` | explanation_quality_diagnostic | low | New report/result/figure created after final package was assembled and relevant to final report. |
| `outputs/explanation_quality_by_group.csv` | explanation_quality_diagnostic | low | New report/result/figure created after final package was assembled and relevant to final report. |
| `outputs/explanation_quality_by_query.csv` | explanation_quality_diagnostic | low | New report/result/figure created after final package was assembled and relevant to final report. |
| `outputs/explanation_quality_examples.csv` | explanation_quality_diagnostic | low | New report/result/figure created after final package was assembled and relevant to final report. |
| `outputs/explanation_quality_report.md` | explanation_quality_diagnostic | low | New report/result/figure created after final package was assembled and relevant to final report. |
| `outputs/figures/fig_explanation_quality_summary.png` | explanation_quality_diagnostic | low | New report/result/figure created after final package was assembled and relevant to final report. |

### final_score_formalization

| relative_path | group | risk_level | reason |
|---|---|---|---|
| `outputs/final_score_formalization_report.md` | final_score_formalization | low | New report/result/figure created after final package was assembled and relevant to final report. |
| `outputs/final_score_component_trace.csv` | final_score_formalization | low | New report/result/figure created after final package was assembled and relevant to final report. |

### query_expansion_experiment

| relative_path | group | risk_level | reason |
|---|---|---|---|
| `experiments/run_query_expansion_experiment.py` | query_expansion_experiment | medium | New experimental query expansion artifact; include as extension/prototype, not as replacement for final hybrid baseline. |
| `data/eval/results/baseline_hybrid_query_expansion_core.csv` | query_expansion_experiment | medium | New experimental query expansion artifact; include as extension/prototype, not as replacement for final hybrid baseline. |
| `data/eval/metrics/query_expansion_metrics_summary.csv` | query_expansion_experiment | medium | New experimental query expansion artifact; include as extension/prototype, not as replacement for final hybrid baseline. |
| `data/eval/metrics/query_expansion_metrics_by_query.csv` | query_expansion_experiment | medium | New experimental query expansion artifact; include as extension/prototype, not as replacement for final hybrid baseline. |
| `data/eval/metrics/query_expansion_metrics_by_group.csv` | query_expansion_experiment | medium | New experimental query expansion artifact; include as extension/prototype, not as replacement for final hybrid baseline. |
| `outputs/query_expansion_experiment_analysis.md` | query_expansion_experiment | low | New experimental query expansion artifact; include as extension/prototype, not as replacement for final hybrid baseline. |
| `outputs/query_expansion_applied_terms.csv` | query_expansion_experiment | medium | New experimental query expansion artifact; include as extension/prototype, not as replacement for final hybrid baseline. |
| `outputs/figures/fig_query_expansion_experiment_summary.png` | query_expansion_experiment | low | New experimental query expansion artifact; include as extension/prototype, not as replacement for final hybrid baseline. |

### relevance_judgment_guideline

| relative_path | group | risk_level | reason |
|---|---|---|---|
| `outputs/relevance_judgment_guideline.md` | relevance_judgment_guideline | low | New report/result/figure created after final package was assembled and relevant to final report. |
| `outputs/relevance_judgment_guideline_examples.csv` | relevance_judgment_guideline | low | New report/result/figure created after final package was assembled and relevant to final report. |

## 4. Files already in package

Kh?ng c?.

## 5. Missing source files

Kh?ng c?.

## 6. Review before copy

Kh?ng c?.

## 7. Safety confirmation

- Kh?ng copy file v?o `final_submission_package/`.
- Kh?ng move/x?a/rename file.
- Kh?ng s?a runtime/source/data ch?nh.
- Kh?ng s?a `hybrid_search.py`, `kg_runtime.py`, `vector_search.py`, `run_core_baselines.py`, ho?c `app_streamlit.py`.
- Kh?ng s?a ontology, metadata, query set, relevance judgments, baseline results ho?c metrics c?.
- Kh?ng ch?y experiment.
- Ch? t?o audit report m?i trong `outputs/`.

## 8. Notes

- Package path ???c ki?m tra theo c?ng relative path v?i project g?c, v? d? `outputs/example.md` t??ng ?ng `final_submission_package/outputs/example.md`.
- C?c artifact query expansion ???c ??nh d?u risk `medium` khi l? script/result/metric CSV v? ??y l? experiment m? r?ng/prototype, kh?ng thay th? hybrid final.
- Kh?ng ph?t hi?n th?m artifact report/result/figure li?n quan ngo?i danh s?ch task m?i ?? n?u.
