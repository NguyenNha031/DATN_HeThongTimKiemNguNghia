# Vector store rebuild report for 140-doc corpus

- Th?i ?i?m report: 2026-05-31 10:33:59
- Ph?m vi: backup + rebuild vector store + ki?m tra vector store; kh?ng sync KG, kh?ng baseline, kh?ng metrics, kh?ng latency.

## Executive summary

| metric | value |
| --- | --- |
| status | NEEDS_FIX |
| metadata_docs | 140 |
| raw_files | 140 |
| old_chunks | 25555 |
| new_chunks | 28437 |
| old_vector_docs | 108 |
| new_vector_docs | 137 |
| missing_docs_in_vector_store | 3 |
| missing_doc_ids | KNQG_002; RIA3_002; RIA3_003 |
| extra_docs_in_vector_store | 0 |
| index_ntotal | 28437 |
| chunks_meta_rows | 28437 |
| index_dimension | 384 |
| backup_path | vector_store_backup_before_140docs_20260531_101107 |
| build_log | outputs\vector_store_rebuild_140docs_build_log_20260531_101209.txt |

## Backup summary

| backup_path | file | exists | size_bytes | sha256 |
| --- | --- | --- | --- | --- |
| vector_store_backup_before_140docs_20260531_101107 | chunks.index | True | 39252525 | 86e8f1ae0342e507a36bed9b3e9e4d8748349f216a33f85ea2df06b5fee56268 |
| vector_store_backup_before_140docs_20260531_101107 | chunks_meta.pkl | True | 22144185 | 2afecd1517c8724b3c819cd4dbb5e5e10920532988f6f8d95d491c9406951db9 |
| vector_store_backup_before_140docs_20260531_101107 | config.pkl | True | 90 | faa1fcde7ccbb306536a3ecdc1dcbeb173a93b809cc78a419c7f075248777d69 |

## Rebuild details

| item | value |
| --- | --- |
| script/function used | vector_search.build_pipeline() |
| metadata path | data/metadata/document_metadata_cleaned.xlsx |
| raw docs path | data/raw_docs/ |
| embedding model | sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 |
| chunk size | 800 |
| chunk overlap | 150 |
| parse [ERROR] count | 0 |
| [WARN] count | 0 |
| empty text / skipped docs | None |
| build log | outputs\vector_store_rebuild_140docs_build_log_20260531_101209.txt |

## Consistency checks

| check | value | expected | status |
| --- | --- | --- | --- |
| metadata docs | 140 | 140 | PASS |
| raw files | 140 | 140 | PASS |
| unique doc_id in chunks_meta | 137 | 140 | FAIL |
| missing metadata docs in chunks_meta | 3 | 0 | FAIL |
| extra chunks_meta docs not in metadata | 0 | 0 | PASS |
| chunks_meta rows | 28437 | index.ntotal | PASS |
| FAISS index.ntotal | 28437 | 28437 | PASS |
| FAISS index dimension | 384 | 384 | PASS |
| doc chunk count min/median/max | 5/80/3390 | informational | INFO |

### Docs with zero chunks / missing in vector store

| doc_id | title | file_path |
| --- | --- | --- |
| KNQG_002 | Kỹ thuật nuôi tôm hùm lồng và các biện pháp phòng trị bệnh | data/raw_docs/KNQG_002_ky_thuat_nuoi_tom_hum_long_phong_tri_benh.pdf |
| RIA3_002 | TBKQ - Quan trắc, cảnh báo môi trường vùng nuôi tôm hùm trong và sau mưa lũ tỉnh Phú Yên, Khánh Hòa | data/raw_docs/RIA3_002_TBKQ_QTDX_PhuYen_KhanhHoa_17112023.pdf |
| RIA3_003 | Bản tin thông báo kết quả quan trắc (Đợt 14) tại một số tỉnh trọng điểm khu vực Nam Trung Bộ | data/raw_docs/RIA3_003_TBKQ_QTMT_DOT14_T6_2025.pdf |

### Suspiciously low chunk count docs

| doc_id | chunk_count |
| --- | --- |
| TB_005 | 5 |

## Smoke test results

| query | rank | doc_id | title | score | file_path |
| --- | --- | --- | --- | --- | --- |
| AHPND shrimp disease | 1 | PMC_029 | Selection of Lactic Acid Bacteria (LAB) Antagonizing Vibrio parahaemolyticus: The Pathogen of Acute Hepatopancreatic Necrosis Disease (AHPND) in Whiteleg Shrimp (Penaeus vannamei) | 0.8789482712745667 | data/raw_docs/PMC_029_PMC6955853.pdf |
| AHPND shrimp disease | 2 | SEAFDEC_008 | Current status and impact of early mortality syndrome (EMS)/acute hepatopancreatic necrosis disease (AHPND) and hepatopancreatic microsporidiosis (HPM) outbreaks on Thailand’s s... | 0.8407975435256958 | data/raw_docs/SEAFDEC_008_Putth2016.pdf |
| AHPND shrimp disease | 3 | FAO_006 | FAO Second International Technical Seminar/Workshop on Acute hepatopancreatic necrosis disease (AHPND), Bangkok, Thailand 23–25 June 2016 | 0.8256773948669434 | data/raw_docs/FAO_006_bt131e.pdf |
| AHPND shrimp disease | 4 | FAO_001 | Shrimp acute hepatopancreatic necrosis disease strategy manual | 0.8200538158416748 | data/raw_docs/FAO_001_cb2119en.pdf |
| AHPND shrimp disease | 5 | PMC_010 | A Review of the Functional Annotations of Important Genes in the AHPND-Causing pVA1 Plasmid | 0.8019028306007385 | data/raw_docs/PMC_010_PMC7409025.pdf |
| nu?i t?m h?m Kh?nh H?a | 1 | RIA3_001 | Quy hoạch nuôi tôm hùm đến năm 2020 và định hướng đến 2030 | 0.6385906934738159 | data/raw_docs/RIA3_001_quy_hoach_nuoi_tom_hum_2030.pdf |
| nu?i t?m h?m Kh?nh H?a | 2 | RIA3_001 | Quy hoạch nuôi tôm hùm đến năm 2020 và định hướng đến 2030 | 0.6370664238929749 | data/raw_docs/RIA3_001_quy_hoach_nuoi_tom_hum_2030.pdf |
| nu?i t?m h?m Kh?nh H?a | 3 | RIA3_001 | Quy hoạch nuôi tôm hùm đến năm 2020 và định hướng đến 2030 | 0.6274980306625366 | data/raw_docs/RIA3_001_quy_hoach_nuoi_tom_hum_2030.pdf |
| nu?i t?m h?m Kh?nh H?a | 4 | RIA3_001 | Quy hoạch nuôi tôm hùm đến năm 2020 và định hướng đến 2030 | 0.6262221932411194 | data/raw_docs/RIA3_001_quy_hoach_nuoi_tom_hum_2030.pdf |
| nu?i t?m h?m Kh?nh H?a | 5 | RIA3_001 | Quy hoạch nuôi tôm hùm đến năm 2020 và định hướng đến 2030 | 0.6235935091972351 | data/raw_docs/RIA3_001_quy_hoach_nuoi_tom_hum_2030.pdf |
| EHP t?m th? Qu?ng Ninh Nam ??nh | 1 | RIA3_001 | Quy hoạch nuôi tôm hùm đến năm 2020 và định hướng đến 2030 | 0.784915566444397 | data/raw_docs/RIA3_001_quy_hoach_nuoi_tom_hum_2030.pdf |
| EHP t?m th? Qu?ng Ninh Nam ??nh | 2 | RIA3_001 | Quy hoạch nuôi tôm hùm đến năm 2020 và định hướng đến 2030 | 0.7819572687149048 | data/raw_docs/RIA3_001_quy_hoach_nuoi_tom_hum_2030.pdf |
| EHP t?m th? Qu?ng Ninh Nam ??nh | 3 | KKTY_001 | Tỷ lệ nhiễm và mức độ mẫn cảm kháng sinh của vi khuẩn Vibrio parahaemolyticus phân lập từ tôm hùm bông (Panulirus ornatus) nuôi lồng ở vùng biển tỉnh Phú Yên | 0.7477661371231079 | data/raw_docs/KKTY_001_vibrio_khang_sinh_tom_hum_bong_phu_yen.pdf |
| EHP t?m th? Qu?ng Ninh Nam ??nh | 4 | RIA3_001 | Quy hoạch nuôi tôm hùm đến năm 2020 và định hướng đến 2030 | 0.7397353649139404 | data/raw_docs/RIA3_001_quy_hoach_nuoi_tom_hum_2030.pdf |
| EHP t?m th? Qu?ng Ninh Nam ??nh | 5 | RIA3_001 | Quy hoạch nuôi tôm hùm đến năm 2020 và định hướng đến 2030 | 0.7391479015350342 | data/raw_docs/RIA3_001_quy_hoach_nuoi_tom_hum_2030.pdf |
| Vibrio parahaemolyticus t?m h?m | 1 | HUIB_001 | Khả năng hình thành màng sinh học và tính kháng kháng sinh của Vibrio parahaemolyticus phân lập từ tôm hùm Panulirus spp. nuôi | 0.8246646523475647 | data/raw_docs/HUIB_001_vibrio_biofilm_khang_khang_sinh_tom_hum.pdf |
| Vibrio parahaemolyticus t?m h?m | 2 | PMC_026 | Las bolitas Syndrome in Penaeus vannamei Hatcheries in Latin America | 0.7813066244125366 | data/raw_docs/PMC_026_PMC11205452.pdf |
| Vibrio parahaemolyticus t?m h?m | 3 | FAO_044 | Report of the FAO/MARD Technical Workshop on Early Mortality Syndrome (EMS) or Acute Hepatopancreatic Necrosis Syndrome (AHPNS) of Cultured Shrimp | 0.7658872008323669 | data/raw_docs/FAO_044_i2734e03i.pdf |
| Vibrio parahaemolyticus t?m h?m | 4 | TCTS_001 | Các bệnh thường gặp trên tôm nước lợ và biện pháp phòng chống hiệu quả | 0.7634848356246948 | data/raw_docs/TCTS_001_024286.pdf |
| Vibrio parahaemolyticus t?m h?m | 5 | TNU_JST_001 | Điều tra độc lực của vi khuẩn Vibrio parahaemolyticus gây bệnh trên tôm thẻ chân trắng | 0.7537679672241211 | data/raw_docs/TNU_JST_001_doc_luc_vibrio_tom_the_chan_trang.pdf |
| nu?i c? bi?n l?ng b? Kh?nh H?a | 1 | FAO_003 | Special Publication on Acute Hepatopancreatic Necrosis Disease (AHPND) | 0.5483015775680542 | data/raw_docs/FAO_003_ca2976en.pdf |
| nu?i c? bi?n l?ng b? Kh?nh H?a | 2 | FAO_003 | Special Publication on Acute Hepatopancreatic Necrosis Disease (AHPND) | 0.5448846817016602 | data/raw_docs/FAO_003_ca2976en.pdf |
| nu?i c? bi?n l?ng b? Kh?nh H?a | 3 | FAO_004 | The Progressive Management Pathway for Aquaculture Biosecurity: Guidelines for application | 0.5404773950576782 | data/raw_docs/FAO_004_cc6858en.pdf |
| nu?i c? bi?n l?ng b? Kh?nh H?a | 4 | VJAS_001 | Nghiên cứu bệnh vi bào tử trùng Enterocytozoon hepatopenaei (EHP) trên tôm thẻ chân trắng nuôi tại Quảng Ninh và Nam Định | 0.5345961451530457 | data/raw_docs/VJAS_001_ehp_tom_the_quang_ninh_nam_dinh.pdf |
| nu?i c? bi?n l?ng b? Kh?nh H?a | 5 | RIA3_001 | Quy hoạch nuôi tôm hùm đến năm 2020 và định hướng đến 2030 | 0.5329691767692566 | data/raw_docs/RIA3_001_quy_hoach_nuoi_tom_hum_2030.pdf |

### Manual smoke checks

| check | query | expected_doc_ids | top5_doc_ids | hit |
| --- | --- | --- | --- | --- |
| EHP Qu?ng Ninh/Nam ??nh c? VJAS_001 | EHP t?m th? Qu?ng Ninh Nam ??nh | VJAS_001 | RIA3_001; RIA3_001; KKTY_001; RIA3_001; RIA3_001 | NO |
| Vibrio/t?m h?m c? HUIB_001 ho?c KKTY_001 | Vibrio parahaemolyticus t?m h?m | HUIB_001; KKTY_001 | HUIB_001; PMC_026; FAO_044; TCTS_001; TNU_JST_001 | YES |
| C? bi?n/l?ng b? Kh?nh H?a c? KNQG_001/JFST_001 ho?c marine fish docs | nu?i c? bi?n l?ng b? Kh?nh H?a | KNQG_001; JFST_001; CTU_002; TCKHTS_006; TCKHTS_007; CTU_JOURNAL_003; VJAS_002; TCKHTS_008; TCKHTS_009 | FAO_003; FAO_003; FAO_004; VJAS_001; RIA3_001 | NO |

## Problems / warnings

| severity | issue | detail | suggestion |
| --- | --- | --- | --- |
| CRITICAL | Metadata doc_id kh?ng xu?t hi?n trong chunks_meta | KNQG_002; RIA3_002; RIA3_003 | C?n OCR/convert ho?c x? l? parser cho c?c PDF kh?ng tr?ch xu?t ???c text r?i rebuild l?i. |
| WARNING | Smoke test warning | EHP Qu?ng Ninh/Nam ??nh c? VJAS_001: expected one of ['VJAS_001'], top5=['RIA3_001', 'RIA3_001', 'KKTY_001', 'RIA3_001', 'RIA3_001'] | Review retrieval sau khi vector store ?? 140 docs. |
| WARNING | Smoke test warning | C? bi?n/l?ng b? Kh?nh H?a c? KNQG_001/JFST_001 ho?c marine fish docs: expected one of ['KNQG_001', 'JFST_001', 'CTU_002', 'TCKHTS_006', 'TCKHTS_007', 'CTU_JOURNAL_003', 'VJAS_00... | Review retrieval sau khi vector store ?? 140 docs. |
| INFO | Docs c? chunk count r?t th?p <= 5 | TB_005=5 | Ki?m tra n?u n?i dung qu? ng?n b?t th??ng. |

## Next step recommendation

Kh?ng sync KG/baseline cho ??n khi s?a l?i vector store. C?n x? l? c?c t?i li?u b? 0 chunks/missing, th??ng b?ng OCR/convert PDF ho?c thay raw doc ??c ???c, r?i rebuild l?i vector store.

## Output files

- `outputs\vector_store_rebuild_140docs_report.md`
- `outputs\vector_store_rebuild_140docs_summary.csv`
- `outputs\vector_store_rebuild_140docs_doc_chunk_counts.csv`
- `outputs\vector_store_rebuild_140docs_smoke_tests.csv`
- `outputs\vector_store_rebuild_140docs_build_log_20260531_101209.txt`
