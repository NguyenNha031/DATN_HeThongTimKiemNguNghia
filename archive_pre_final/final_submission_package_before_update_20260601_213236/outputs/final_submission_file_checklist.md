# Final Submission File Checklist

## Purpose

This checklist separates the frozen final system files from optional experiment/future-work artifacts for the marine-aquaculture semantic search project. It is intended to prevent mixing final runtime/evaluation assets with exploratory outputs when preparing the final submission package.

Status values: `EXISTS` means the file/folder is present in the project snapshot; `MISSING` means it was not found at the checked path.

## Key Final Notes

- Final runtime ontology: `data/ontology/taxon_enriched_facts_v2.owl`.
- Final metadata: `data/metadata/document_metadata_cleaned.xlsx`.
- Final query set: `data/eval/final_query_set_core.csv`.
- Final relevance judgments: `data/eval/relevance_judgments_core.csv`.
- Candidate fusion does not replace `data/eval/results/baseline_hybrid_core.csv`.
- Semantic patch outputs are not the final source of truth.
- `outputs/taxon_enriched_facts_v2_backfilled_runtime.owl` is not the final runtime OWL.
- Do not mix final files and experiment/future-work files in the main submission unless the optional files are clearly labeled as experiments.

## 1. final_system

| file | status | role | submit? |
| --- | --- | --- | --- |
| `app_streamlit.py` | EXISTS | Streamlit UI demo for the final system. | YES |
| `hybrid_search.py` | EXISTS | Main hybrid runtime: vector retrieval, metadata reranking, KG scoring, intent adjustment. | YES |
| `kg_runtime.py` | EXISTS | KG loading, entity linking, document fact extraction, KG scoring/explanation. | YES |
| `vector_search.py` | EXISTS | Vector index loading and vector retrieval. | YES |
| `run_core_baselines.py` | EXISTS | Script used to generate/evaluate core baseline result files. | YES |
| `verify_kg_runtime.py` | EXISTS | KG runtime verification script. | YES |
| `measure_core_baseline_latency.py` | EXISTS | Latency measurement script for core baselines. | YES |
| `compute_core_metrics.py` | EXISTS | Main metric computation script for core evaluation. | YES |
| `data/eval/metrics/compute_core_metrics.py` | EXISTS | Metrics script copy/snapshot under the metrics folder. Include only if preserving evaluation reproducibility layout. | YES |
| `verify_ontology_quality.py` | EXISTS | Ontology quality check script. | YES |
| `verify_ontology_reasoner_consistency.py` | EXISTS | Separate reasoner consistency evaluation script, not runtime retrieval. | YES |
| `evaluate_competency_questions.py` | EXISTS | Competency question evaluation script. | YES |

## 2. final_data_and_runtime_assets

| file/folder | status | role | submit? |
| --- | --- | --- | --- |
| `data/ontology/taxon_enriched_facts_v2.owl` | EXISTS | Frozen final runtime ontology used by KG runtime. | YES |
| `data/metadata/document_metadata_cleaned.xlsx` | EXISTS | Frozen final document metadata. | YES |
| `vector_store/` | EXISTS | Vector index and records used by vector retrieval. | YES |
| `data/eval/final_query_set_core.csv` | EXISTS | Frozen final core query set. | YES |
| `data/eval/relevance_judgments_core.csv` | EXISTS | Frozen final relevance judgments. | YES |
| `data/eval/relevance_guidelines_core.md` | EXISTS | Judgment guidelines for the core evaluation set. | YES |

## 3. final_outputs_and_evaluation

| file | status | role | submit? |
| --- | --- | --- | --- |
| `data/eval/results/baseline_lexical_core.csv` | EXISTS | Final lexical baseline output. | YES |
| `data/eval/results/baseline_vector_core.csv` | EXISTS | Final vector baseline output. | YES |
| `data/eval/results/baseline_vector_metadata_core.csv` | EXISTS | Final vector + metadata baseline output. | YES |
| `data/eval/results/baseline_ontology_sparql_core.csv` | EXISTS | Final ontology/SPARQL baseline output. | YES |
| `data/eval/results/baseline_hybrid_core.csv` | EXISTS | Final hybrid baseline output and main hybrid result file. | YES |
| `data/eval/metrics/baseline_metrics_summary.csv` | EXISTS | Final aggregate metric summary. | YES |
| `data/eval/metrics/baseline_metrics_by_group.csv` | EXISTS | Final metrics grouped by query group. | YES |
| `data/eval/metrics/baseline_metrics_per_query.csv` | EXISTS | Final per-query metric details. | YES |
| `data/eval/metrics/baseline_latency_summary.csv` | EXISTS | Final latency summary. | YES |
| `data/eval/metrics/baseline_latency_per_query.csv` | EXISTS | Final per-query latency output. | YES |
| `outputs/kg_runtime_verification.json` | EXISTS | Final KG runtime verification output. | YES |
| `outputs/final_score_formula_and_runtime_flow.md` | EXISTS | Report note explaining final scoring formula and runtime flow. | YES |
| `outputs/hybrid_vs_vector_metadata_by_group.csv` | EXISTS | CSV comparison of final hybrid vs vector_metadata by query group. | YES |
| `outputs/hybrid_vs_vector_metadata_by_group.md` | EXISTS | Markdown interpretation of final hybrid vs vector_metadata by query group. | YES |
| `outputs/streamlit_demo_notes.md` | EXISTS | Notes for final Streamlit demo usage. | YES |
| `outputs/ontology_quality_check.md` | EXISTS | Ontology quality check report. | YES |
| `outputs/ontology_quality_check.json` | EXISTS | Machine-readable ontology quality output. | YES |
| `outputs/ontology_reasoner_consistency_check.md` | EXISTS | Separate reasoner consistency report. | YES |
| `outputs/ontology_reasoner_consistency_check.json` | EXISTS | Machine-readable reasoner consistency output. | YES |
| `outputs/competency_questions_results.csv` | EXISTS | Competency question evaluation results. | YES |
| `outputs/competency_questions_summary.json` | EXISTS | Competency question evaluation summary. | YES |
| `outputs/evaluation_layers_summary.md` | EXISTS | Summary of evaluation layers. | YES |
| `outputs/evaluation_layers_summary.json` | EXISTS | Machine-readable evaluation layer summary. | YES |

## 4. experiments_future_work_optional

Only include these files if the submission clearly labels them as experiments/future work. They should not be presented as final runtime assets or final baseline replacements.

| file | status | role | submit? |
| --- | --- | --- | --- |
| `data/eval/results/baseline_hybrid_candidate_fusion_core.csv` | EXISTS | Candidate fusion experiment output; does not replace final `baseline_hybrid_core.csv`. | OPTIONAL |
| `outputs/candidate_fusion_experiment_summary.md` | EXISTS | Candidate fusion experiment summary. | OPTIONAL |
| `outputs/candidate_fusion_experiment_summary.csv` | EXISTS | Candidate fusion experiment summary data. | OPTIONAL |
| `outputs/candidate_fusion_experiment_summary.json` | EXISTS | Machine-readable candidate fusion experiment summary. | OPTIONAL |
| `outputs/candidate_fusion_per_query_delta.csv` | EXISTS | Per-query delta analysis for candidate fusion experiment. | OPTIONAL |
| `outputs/semantic_rule_candidate_facts.md` | EXISTS | Semantic rule candidate facts experiment report. | OPTIONAL |
| `outputs/semantic_rule_candidate_facts.csv` | EXISTS | Semantic rule candidate facts data. | OPTIONAL |
| `outputs/semantic_rule_candidate_facts.json` | EXISTS | Machine-readable semantic rule candidate facts output. | OPTIONAL |
| `outputs/semantic_patch_final_assessment.md` | EXISTS | Semantic patch assessment; not the final source of truth. | OPTIONAL |
| `taxon_enriched_semantic.owl` | MISSING | Semantic patch ontology path mentioned as experiment; not final runtime ontology. | OPTIONAL |
| `outputs/taxon_enriched_facts_v2_backfilled_runtime.owl` | EXISTS | Backfilled runtime OWL experiment; not used as final runtime ontology. | OPTIONAL |
| `outputs/document_fact_backfill_report.csv` | EXISTS | Backfill experiment report data. | OPTIONAL |
| `outputs/document_fact_backfill_report.json` | EXISTS | Machine-readable backfill experiment report. | OPTIONAL |
| `data/eval/results/baseline_vector_metadata_kg_no_intent_core.csv` | EXISTS | Ablation/diagnostic result, not one of the final baseline result files. | OPTIONAL |
| `outputs/wilcoxon_hybrid_vs_vector_metadata.md` | EXISTS | Statistical comparison note, optional supporting analysis. | OPTIONAL |
| `outputs/wilcoxon_hybrid_vs_vector_metadata.csv` | EXISTS | Statistical comparison data. | OPTIONAL |
| `outputs/wilcoxon_hybrid_vs_vector_metadata.json` | EXISTS | Machine-readable statistical comparison output. | OPTIONAL |
| `outputs/archive/old_verification/*` | EXISTS | Old KG verification snapshots retained for history; not final submission material. | NO |
| `outputs/archive/old_outputs/*` | EXISTS | Old experiment/verification outputs retained for history; not final submission material. | NO |
| `outputs/archive/old_snapshots/*` | EXISTS | Old metric snapshots retained for history; not final submission material. | NO |

## Submission Guidance

Submit the `final_system`, `final_data_and_runtime_assets`, and `final_outputs_and_evaluation` groups as the main final package. Keep `experiments_future_work_optional` separate, with clear labels, if any of those files are included for discussion of limitations, ablations, or future work.
