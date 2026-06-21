# Remove RIA3_002/RIA3_003 and rebuild vector store for 138-doc corpus

- Th?i ?i?m report: 2026-05-31 10:44:59
- Ph?m vi ?? th?c hi?n: backup, lo?i 2 doc kh?i metadata/raw_docs, audit metadata/raw 138 docs, ch?n ?o?n KNQG_002. Kh?ng sync KG, kh?ng baseline, kh?ng metrics, kh?ng latency.
- Rebuild vector store 138 docs kh?ng ch?y v? KNQG_002 ch?a c? OCR/text fallback ?? t?t.

## Executive summary

| metric | value |
| --- | --- |
| status | BLOCKED |
| metadata_docs_before | 140 |
| metadata_docs_after | 138 |
| raw_files_before | 140 |
| raw_files_after | 138 |
| removed_docs | RIA3_002; RIA3_003 |
| KNQG_002_fixed_method | NONE - OCR unavailable; manual OCR/text required |
| KNQG_002_final_text_chars | 0 |
| vector_rebuild_138docs | NOT_RUN |
| vector_docs_after_rebuild | NOT_RUN |
| missing_docs_after_rebuild | NOT_RUN |
| can_proceed_to_kg_sync | NO |

## Backups

| type | path | exists | size_bytes | sha256 |
| --- | --- | --- | --- | --- |
| metadata | data\metadata\archive\document_metadata_cleaned_before_remove_RIA3_002_RIA3_003_20260531_104204.xlsx | True | 52044 | b160b38740892a65413f1250741fc806defc1ec3cb113dc8a3460f694bf7c570 |
| raw_excluded | archive_pre_final\excluded_from_final_corpus_20260531_104204\RIA3_002_TBKQ_QTDX_PhuYen_KhanhHoa_17112023.pdf | True | 1670425 | cae763321de8ac031c948345cef3401db8f9bc65b89781e9d8a2b551f16980b3 |
| raw_excluded | archive_pre_final\excluded_from_final_corpus_20260531_104204\RIA3_003_TBKQ_QTMT_DOT14_T6_2025.pdf | True | 1843283 | 0c0e3911f538a7ed149ef9ca20af125d3e8db832b1f386dfcd2069608c888d16 |
| vector_failed_140_backup | vector_store_backup_failed_140docs_missing3_before_138docs_rebuild_20260531_104204\chunks.index | True | 43679277 | 7eaa21cb5c96cda77559abfed98c2ac765c5af5266961ee7ce2c01eb575b602f |
| vector_failed_140_backup | vector_store_backup_failed_140docs_missing3_before_138docs_rebuild_20260531_104204\chunks_meta.pkl | True | 25157380 | f27ffb95aa5b4e4fb00457d5eb657f4202b5f76eb4bcb69b9b0027822d8708cf |
| vector_failed_140_backup | vector_store_backup_failed_140docs_missing3_before_138docs_rebuild_20260531_104204\config.pkl | True | 90 | faa1fcde7ccbb306536a3ecdc1dcbeb173a93b809cc78a419c7f075248777d69 |

## Removed docs

| doc_id | title | old_file_path | archive_path | reason | status | size_bytes |
| --- | --- | --- | --- | --- | --- | --- |
| RIA3_002 | TBKQ - Quan trắc, cảnh báo môi trường vùng nuôi tôm hùm trong và sau mưa lũ tỉnh Phú Yên, Khánh Hòa | data/raw_docs/RIA3_002_TBKQ_QTDX_PhuYen_KhanhHoa_17112023.pdf | archive_pre_final\excluded_from_final_corpus_20260531_104204\RIA3_002_TBKQ_QTDX_PhuYen_KhanhHoa_17112023.pdf | excluded from final corpus by user decision | MOVED_VERIFIED | 1670425 |
| RIA3_003 | Bản tin thông báo kết quả quan trắc (Đợt 14) tại một số tỉnh trọng điểm khu vực Nam Trung Bộ | data/raw_docs/RIA3_003_TBKQ_QTMT_DOT14_T6_2025.pdf | archive_pre_final\excluded_from_final_corpus_20260531_104204\RIA3_003_TBKQ_QTMT_DOT14_T6_2025.pdf | excluded from final corpus by user decision | MOVED_VERIFIED | 1843283 |

## Metadata/raw docs audit after removal

| metric | value | detail |
| --- | --- | --- |
| metadata_rows | 138 |  |
| raw_files | 138 |  |
| unique_doc_id | 138 |  |
| duplicate_doc_id | 0 |  |
| missing_file_path | 0 |  |
| matched_metadata_rows | 138 |  |
| missing_raw_files | 0 |  |
| unreferenced_raw_files | 0 |  |
| duplicate_file_path | 0 |  |
| zero_byte_files | 0 |  |
| suspicious_extension | 0 |  |
| outside_raw_docs_paths | 0 |  |
| required_columns_missing | 0 |  |
| RIA3_002_in_metadata | False |  |
| RIA3_003_in_metadata | False |  |
| result | PASS |  |
| required_columns | doc_id; title; author; publishedYear; source; referenceUrl; docType; file_path; related_taxon; related_disease; related_location; production_mode; keywords; language; note |  |
| missing_raw_doc_ids |  |  |
| unreferenced_raw_files |  |  |

## KNQG_002 extraction/OCR diagnostics

| doc_id | title | file_path | pages | parser_current_chars | pymupdf_chars | pypdf_pdfplumber_chars | ocr_text_path | final_text_chars | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| KNQG_002 | Kỹ thuật nuôi tôm hùm lồng và các biện pháp phòng trị bệnh | data/raw_docs/KNQG_002_ky_thuat_nuoi_tom_hum_long_phong_tri_benh.pdf | 63 | 0 | 0 | N/A - package not installed |  | 0 | NEEDS_MANUAL_TEXT |

## Vector rebuild summary

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

## Smoke test results

| query | status |
| --- | --- |
| k? thu?t nu?i t?m h?m l?ng ph?ng tr? b?nh | NOT_RUN_BLOCKED_NEEDS_MANUAL_TEXT_FOR_KNQG_002 |
| b?nh s?a ?? th?n t?m h?m nu?i l?ng Nam Trung B? | NOT_RUN_BLOCKED_NEEDS_MANUAL_TEXT_FOR_KNQG_002 |
| nu?i c? l?ng b? tr?n bi?n Kh?nh H?a | NOT_RUN_BLOCKED_NEEDS_MANUAL_TEXT_FOR_KNQG_002 |
| EHP t?m th? Qu?ng Ninh Nam ??nh | NOT_RUN_BLOCKED_NEEDS_MANUAL_TEXT_FOR_KNQG_002 |
| AHPND shrimp disease | NOT_RUN_BLOCKED_NEEDS_MANUAL_TEXT_FOR_KNQG_002 |

## Problems / warnings

| severity | issue | detail | suggestion |
| --- | --- | --- | --- |
| CRITICAL | KNQG_002 ch?a c? OCR/text fallback | PDF 63 trang d?ng ?nh; PyMuPDF chars=0; Tesseract/OCR engine kh?ng c? s?n | Cung c?p file text/OCR cho KNQG_002 ho?c c?i OCR engine r?i ch?y l?i rebuild. |
| INFO | RIA3_002/RIA3_003 ?? lo?i kh?i metadata/raw_docs | Metadata/raw audit sau lo?i 2 doc PASS 138/138 | C? th? gi? archive ?? kh?i ph?c n?u c?n. |
| INFO | Vector store 138-doc rebuild ch?a ch?y | D?ng ??ng ?i?u ki?n v? KNQG_002 ch?a c? text ?? t?t | Sau khi c? fallback text, rebuild vector store 138 docs. |

## Next step recommendation

Kh?ng sync KG/baseline cho ??n khi l?i ???c s?a. C?n cung c?p/c?i OCR ?? t?o text fallback ?? d?i cho `KNQG_002`, sau ?? rebuild vector store cho corpus 138 t?i li?u v? ki?m tra l?i consistency/smoke test.

## Output files

- `outputs\remove_ria3_and_fix_knqg002_report.md`
- `outputs\remove_ria3_and_fix_knqg002_summary.csv`
- `outputs\remove_ria3_and_fix_knqg002_metadata_raw_audit.csv`
- `outputs\remove_ria3_and_fix_knqg002_renamed_or_moved_files.csv`
- `outputs\knqg002_ocr_or_text_fallback_diagnostics.csv`
- `outputs\vector_store_rebuild_138docs_report.md`
- `outputs\vector_store_rebuild_138docs_summary.csv`
- `outputs\vector_store_rebuild_138docs_doc_chunk_counts.csv`
- `outputs\vector_store_rebuild_138docs_smoke_tests.csv`
