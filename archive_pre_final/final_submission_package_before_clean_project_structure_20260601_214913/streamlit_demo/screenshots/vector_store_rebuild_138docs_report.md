# Vector store rebuild 138-docs report

- Th?i ?i?m report: 2026-05-31 10:44:59
- Status: BLOCKED. Rebuild kh?ng ch?y v? `KNQG_002` ch?a c? OCR/text fallback.

## Executive summary

| metric | value |
| --- | --- |
| status | BLOCKED |
| reason | KNQG_002 is image-based PDF and OCR/text fallback is unavailable |
| metadata_docs_after_removal | 138 |
| raw_files_after_removal | 138 |
| old_chunks_before_138_step | 28437 |
| new_chunks_after_138_rebuild | NOT_RUN |
| current_vector_docs | 137 |
| expected_vector_docs_after_rebuild | 138 |
| current_missing_docs_vs_138_metadata | KNQG_002 |
| current_extra_docs_vs_138_metadata |  |
| KNQG_002_chunk_count | 0 |
| RIA3_002_in_chunks_meta | False |
| RIA3_003_in_chunks_meta | False |
| index_ntotal_current | 28437 |
| chunks_meta_rows_current | 28437 |
| index_chunks_meta_match_current | True |
| config_model | sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 |
| can_proceed_to_kg_sync | NO |

## Current vector/metadata consistency before 138-doc rebuild

| check | value | expected | status |
| --- | --- | --- | --- |
| metadata docs | 138 | 138 | PASS |
| raw files | 138 | 138 | PASS |
| current vector docs | 137 | 138 after rebuild | FAIL_CURRENT_MISSING_KNQG_002 |
| KNQG_002 chunk count | 0 | >0 | FAIL |
| index.ntotal vs chunks_meta | 28437 vs 28437 | match | PASS |

## Docs with 0 chunks / missing currently

| doc_id | title |
| --- | --- |
| KNQG_002 | Kỹ thuật nuôi tôm hùm lồng và các biện pháp phòng trị bệnh |

## Smoke test results

Not run because rebuild was blocked before vector search smoke test.

## Next step recommendation

Kh?ng sync KG/baseline cho ??n khi l?i ???c s?a. Sau khi c? text fallback/OCR cho `KNQG_002`, rebuild vector store 138 docs b?ng model c? v? ch?y l?i consistency/smoke tests.

## Output files

- `outputs\vector_store_rebuild_138docs_report.md`
- `outputs\vector_store_rebuild_138docs_summary.csv`
- `outputs\vector_store_rebuild_138docs_doc_chunk_counts.csv`
- `outputs\vector_store_rebuild_138docs_smoke_tests.csv`
