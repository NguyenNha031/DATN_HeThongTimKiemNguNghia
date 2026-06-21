# K?t qu? s?a l?i raw file path

- Th?i ?i?m ki?m tra: 2026-05-31 00:39:56
- Ph?m vi: ch? rename 6 raw files b? d? `.pdf` v? audit nh? metadata/raw_docs; kh?ng rebuild vector store, kh?ng sync KG, kh?ng ch?y baseline/metrics/latency.

## 1. Files renamed

| old_path | new_path | status | size_bytes |
| --- | --- | --- | --- |
| data/raw_docs/VJMST_001_hien_trang_ntts_dam_thuy_trieu_cam_lam.pdf.pdf | data/raw_docs/VJMST_001_hien_trang_ntts_dam_thuy_trieu_cam_lam.pdf | RENAMED_VERIFIED | 2560728 |
| data/raw_docs/TCKHTS_002_phong_tri_benh_sua_do_than_tom_hum_nam_trung_bo.pdf.pdf | data/raw_docs/TCKHTS_002_phong_tri_benh_sua_do_than_tom_hum_nam_trung_bo.pdf | RENAMED_VERIFIED | 838162 |
| data/raw_docs/TCKHTS_003_cung_cap_con_giong_tom_hum_bong_viet_nam.pdf.pdf | data/raw_docs/TCKHTS_003_cung_cap_con_giong_tom_hum_bong_viet_nam.pdf | RENAMED_VERIFIED | 1937765 |
| data/raw_docs/VJAS_001_ehp_tom_the_quang_ninh_nam_dinh.pdf.pdf | data/raw_docs/VJAS_001_ehp_tom_the_quang_ninh_nam_dinh.pdf | RENAMED_VERIFIED | 1172666 |
| data/raw_docs/TNU_JST_001_doc_luc_vibrio_tom_the_chan_trang.pdf.pdf | data/raw_docs/TNU_JST_001_doc_luc_vibrio_tom_the_chan_trang.pdf | RENAMED_VERIFIED | 528397 |
| data/raw_docs/MDPI_001_vibrio_ahpnd_mekong_delta.pdf.pdf | data/raw_docs/MDPI_001_vibrio_ahpnd_mekong_delta.pdf | RENAMED_VERIFIED | 1225850 |

## 2. Post-fix audit summary

| metric | value |
| --- | --- |
| metadata rows | 140 |
| raw files | 140 |
| unique doc_id | 140 |
| duplicate doc_id | 0 |
| missing file_path | 0 |
| matched metadata rows | 140 |
| missing raw files | 0 |
| unreferenced raw files | 0 |
| duplicate file_path | 0 |
| zero-byte files | 0 |
| suspicious extension | 0 |
| result | PASS |

## 3. C? ???c qua b??c rebuild ch?a?

C? th? chuy?n sang b??c backup + rebuild vector store, nh?ng ch?a ???c sync KG/baseline cho ??n khi ng??i d?ng x?c nh?n.

## 4. Output files

- `outputs\rawdocs_pdf_suffix_fix_post_audit.md`
- `outputs\rawdocs_pdf_suffix_fix_post_audit.csv`
- `outputs\rawdocs_pdf_suffix_fix_renamed_files.csv`
