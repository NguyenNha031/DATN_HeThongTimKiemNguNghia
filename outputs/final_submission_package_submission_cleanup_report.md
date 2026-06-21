# Final submission package cleanup report

- Status: PASS
- Package path: `final_submission_package`
- Package files: 251
- Package size bytes: 625801659
- Raw docs: COPIED, count=138, size_bytes=548339646
- README exists: True
- requirements.txt exists: True
- outputs/figures files: 16
- outputs/final_reports files: 33
- Critical missing files: 0
- Forbidden backup/cache/archive hits: 0
- RIA3_002/RIA3_003 hits: 0

## Checklist

- PASS: README exists - README.md exists
- PASS: requirements.txt exists - requirements.txt exists
- PASS: app_streamlit.py exists - app_streamlit.py exists
- PASS: ontology runtime exists - runtime ontology exists
- PASS: metadata cleaned exists - cleaned metadata exists
- PASS: vector store exists - vector store artifacts exist
- PASS: query set core/extended exists - core/extended query sets exist
- PASS: relevance judgments core/extended exists - core/extended judgments exist
- PASS: baseline results final exists - core baseline results exist
- PASS: metrics final exists - metrics exist
- PASS: raw docs included - raw docs status=COPIED; count=138
- PASS: raw docs expected count - raw docs count=138; expected 138
- PASS: no backup/archive/cache in package - forbidden count=0
- PASS: no old figures/pre-138 figures - bad figures count=0
- PASS: no RIA3_002/RIA3_003 - RIA hits count=0
- PASS: outputs cleaned - outputs contains figures/ and final_reports/ only
- PASS: MANIFEST regenerated - manifest exists and matches files
- PASS: package ready - ready to submit

## Outputs retained

- `outputs/figures/`: only final `*_138docs` figure PNG/PDF files.
- `outputs/final_reports/`: final snapshot/evaluation reports and CSV summaries.

## Outputs removed from package

- UI polish/fix checklist and report files.
- Run logs and auxiliary UI/debug output files.
- Backup/archive/cache artifacts.
- Query expansion quantitative files if present in package eval outputs.

## Missing/Warnings

- None
