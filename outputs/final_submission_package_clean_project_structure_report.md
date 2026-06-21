# Final submission package clean project structure report

- Status: PASS_WITH_RAW_DOCS_OMITTED
- Package path: `final_submission_package`
- Backup path: `archive_pre_final/final_submission_package_before_clean_project_structure_20260601_215140`
- Package file count: 120
- Package size bytes: 77460115
- Raw docs copied: False
- Vector store copied: True
- Missing/optional entries recorded: 6
- Critical missing entries: 0
- Forbidden backup/archive/cache paths: 0

## Checklist

- PASS: project_like_structure - Package giu cau truc project-like
- PASS: no_artificial_dirs - Khong co thu muc nhan tao cu
- PASS: root_main_code_present - Root co code chinh
- PASS: metadata_present - Co metadata final
- PASS: ontology_runtime_present - Co ontology runtime final
- PASS: eval_results_metrics_present - Co results va metrics final
- PASS: vector_store_present - Co FAISS index, chunks_meta va config
- PASS: figures_only_138docs - outputs/figures chi co bo *_138docs
- PASS: final_outputs_present - Co report/csv final 138 docs
- PASS: no_backup_archive_cache - Khong co backup/archive/cache trong package
- PASS: no_excluded_ria_raw_docs - Khong co RIA3_002/RIA3_003 trong package filenames
- PASS: readme_manifest_present - README va MANIFEST co trong root package
- PASS: missing_files_recorded_info - 6 missing/optional entries recorded; non-blocking unless critical

## Missing files / INFO

- dependency: `requirements.txt` - INFO: dependency file not present in project root
- dependency: `environment.yml` - INFO: dependency file not present in project root
- dependency: `pyproject.toml` - INFO: dependency file not present in project root
- dependency: `poetry.lock` - INFO: dependency file not present in project root
- dependency: `conda.yml` - INFO: dependency file not present in project root
- eval_metrics: `data\eval\metrics\baseline_metrics_by_query.csv` - final/supplementary metric

## Notes

- Raw docs were intentionally omitted per user request.
- No baseline/metrics/latency rerun was executed by this packaging script.
- Source metadata, ontology, vector store, KG runtime and scoring files were copied only; originals were not modified.
