# Final submission package update report

- Status: PARTIAL
- Package: $pkgRel
- Backup status: CREATED
- Backup path: $backupRel
- Package file count: 150
- Package size bytes: 84719841
- Raw PDFs included: No
- Vector store included: Yes, under ector_store_info/vector_store/

## Copied groups

- data_metadata: 12 file
- evaluation: 38 file
- figures: 20 file
- ontology: 7 file
- outputs_reports: 1 file
- package_root: 1 file
- report: 2 file
- source_code: 15 file
- streamlit_demo: 44 file
- vector_store_info: 9 file

## Checklist

- PASS - final_submission_package exists: final_submission_package
- PASS - Latest Word report copied into report/: Word report found one level above project and copied.
- PASS - All *_138docs figures copied: All required figure files present.
- PASS - No query expansion figure used as final evidence: Query expansion figures excluded from final figures.
- PASS - Core metrics final copied: Core metric files present.
- PASS - Supplementary metrics 138 docs copied: Supplementary metric files present.
- PASS - Ontology runtime final copied: Final runtime ontology.
- PASS - Streamlit UI fix reports copied: KG/source evidence/method compare fix reports.
- PASS - README.md created: Vietnamese package README.
- PASS - MANIFEST.csv created: Full package manifest with SHA256.
- PASS - No confusing old pre-138 figures in package figures root: No old fig_* or query expansion figures in figures root.
- PASS - If files are missing, they are recorded without crash: Missing count: 2
- PASS - Query expansion not copied as final evaluation evidence: No query expansion files under evaluation/.

## Missing files

- [report] Final report PDF: PDF_NOT_FOUND; no PDF generated.
- [evaluation] data/eval/metrics/baseline_metrics_by_query.csv: Requested file not found in project. Copied baseline_metrics_per_query.csv as closest available existing file.

## Notes

- Không rerun baseline/metrics/latency.
- Không sửa metadata/raw docs/vector store/ontology/KG/scoring/runtime.
- Query expansion không được copy như final evidence.
- Candidate fusion và extended evaluation được đặt trong nhóm supplementary/supporting evidence.
- File aseline_metrics_per_query.csv đã được copy như bản per-query hiện có, nhưng filename yêu cầu aseline_metrics_by_query.csv không tồn tại trong project.
