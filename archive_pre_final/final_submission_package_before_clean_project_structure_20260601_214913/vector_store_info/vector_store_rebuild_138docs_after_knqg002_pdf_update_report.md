# Vector store rebuild after KNQG_002 PDF text update

- Th?i ?i?m report: 2026-05-31 13:06:54
- Ph?m vi: ki?m tra KNQG_002, backup vector store, rebuild vector store 138 docs, ki?m tra vector-only. Kh?ng sync KG, kh?ng baseline, kh?ng metrics, kh?ng latency.

## Executive summary

| metric | value |
| --- | --- |
| status | PASS |
| metadata_docs | 138 |
| raw_files | 138 |
| KNQG_002_text_chars | 69586 |
| backup_path | vector_store_backup_before_138docs_rebuild_after_knqg002_text_20260531_121735 |
| old_chunks | 28437 |
| new_chunks | 28542 |
| old_vector_docs | 137 |
| vector_docs | 138 |
| missing_docs |  |
| extra_docs |  |
| KNQG_002_chunk_count | 105 |
| RIA3_002_in_chunks_meta | False |
| RIA3_003_in_chunks_meta | False |
| index_ntotal | 28542 |
| chunks_meta_rows | 28542 |
| index_chunks_meta_match | True |
| config_model | sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 |
| build_log | outputs\vector_store_rebuild_138docs_after_knqg002_pdf_update_build_log_20260531_124915.txt |

## Metadata/raw audit

| metric | value |
| --- | --- |
| metadata_rows | 138 |
| raw_files | 138 |
| unique_doc_id | 138 |
| duplicate_doc_id | 0 |
| missing_file_path | 0 |
| missing_raw_files | 0 |
| unreferenced_raw_files | 0 |
| duplicate_file_path | 0 |
| zero_byte_files | 0 |
| suspicious_extension | 0 |
| outside_raw_docs_paths | 0 |
| RIA3_002_in_metadata | False |
| RIA3_003_in_metadata | False |
| KNQG_002_in_metadata | True |

## KNQG_002 extraction check

| metric | value |
| --- | --- |
| doc_id | KNQG_002 |
| file_path | data/raw_docs/KNQG_002_ky_thuat_nuoi_tom_hum_long_phong_tri_benh.pdf |
| size_bytes | 60773248 |
| pages | 63 |
| project_parser_chars | 69586 |
| pymupdf_chars | 69586 |
| selected_text_chars | 69586 |
| keyword_hit_count | 9 |
| keyword_checks | tôm hùm=True; nuôi lồng=True; phòng trị bệnh=True; bệnh sữa=False; đỏ thân=True; thức ăn=True; lồng nuôi=True; môi trường=True; Khánh Hòa=True; Nam Trung Bộ=True |
| head_1000 | BỘ THỦY SẢN <br>wy TRUNG TAM KHUYEN NGU QUOC GIA <br>NU0IT0MIHÙM LũŨNG <br>VÀ CAC BIEN PHAP PHONG TRI BENH <br>oo <br>x ~~ ¬%: <br>S. <br>: <br>Vem Lili 2 <br>là La XS <br>& <br>` s <br>a y3»; <br>... |

### Text sample head

```text
BỘ THỦY SẢN 
wy TRUNG TAM KHUYEN NGU QUOC GIA 
NU0IT0MIHÙM LũŨNG 
VÀ CAC BIEN PHAP PHONG TRI BENH 
oo 
x ~~ ¬%: 
S. 
: 
Vem Lili 2 
là La XS 
& 
` s 
a y3»; 
<- bn sient 
n 
Co 
eG eae 
i 
`... 
—_ 
ie OS eo | 
i 
zeal 
Mes) = 
= lauli 
k 
Leer 
iO NHÀ XUẤT 
BANNONGNGHIER yàu-2#6<== ˆ. — 
:

BỘ THỦY SẢN 
TRUNG TÂM KHUYẾN NGƯ QUỐC GIA 
Biên soạn: ThS. VÕ VĂN NHA 
KỸ THUẬT NUÔI TÔM HÙM LỒNG 
VÀ CÁC BIỆN PHÁP PHÒNG TRỊ BỆNH 
NHÀ XUẤT BẢN NÔNG NGHIỆP 
HÀ NỘI - 2006

Chương 1: Giới thiệu chung. 
Chương 2: Vài nét về tình hình nuôi và một số yếu tố 
môi trường vàng phân bố tôm him. 
Chương 3: Biện pháp phòng bệnh tổng hợp ở tôm 
hùm nuôi lông. 
Chương 4: Một số bệnh thường gặp ở tôm him nuôi 
lông và biện pháp phòng trị. 
Trong quá trình biên soạn, mặc dù đã hết sức cố 
sáng song sẽ không tránh khỏi thiếu sót, rất mong nhận 
được ý kiến đóng góp, phê bình của bạn đọc để cuốn 
sách hoàn thiện hon trong những lần xuất bản sau. 
Tác giả 
4

Chương I 
GIỚI THIỆU CHUNG 
1. VỊ TRÍ PHÂN LOẠI TÔM HÙ
```

### Text sample tail

```text
vùng phân bố tom him 
20 
Chương 3. BIỆN PHÁP PHÒNG BỆNH TỔNG HỢP Ở 
TÔM HÙM NUÔI LỒNG 
24 
1. Quản lý môi trường nuôi 
25 
2. Tăng cường sức đề kháng của tôm hùm 
27 
3. Tiêu diệt và kìm hãm sự phát triển của tác nhân 
gây bệnh 
33 
Chương 4. MỘT SỐ BỆNH THƯỜNG GẶP Ở TÔM HÙM 
NUÔI LỒNG VÀ BIỆN PHÁP PHÒNG TRỊ 
37 
1. Một số bệnh thường gặp ở tôm hùm nuôi lông 
37 
2. Cách tính lượng thuốc dùng trong phòng, trị bệnh 
tôm hùm 
53 
Tai liệu tham khảo 
56 
50

Chịu trách nhiệm xuất bản 
NGUYÊN CAO DOANH 
Phụ trách bản thảo 
LẠI THỊ THANH TRÀ 
Trình bày bìa 
TOÀN LINH 
NHÀ XUẤT BẢN NÔNG NGHIỆP 
6/167 - Phương Mai - Đống Đa - Hà Nội 
DT: (04) 8524504 - 8521940 FAX: (04) 5760748 
E-mail: nxbnn@hn.vnn.vn 
CHI NHANH NXB NONG NGHIEP 
58 Nguyễn Binh Khiêm - Q.1 Tp. Hồ Chí Minh 
DT: (08) 8297157 - 8299521 
FAX: (08) 9101036 
In 516 bản khổ (15 x 21)cm tai Công ty Cổ phân in 15. Giấy chấp 
nhận DKDT số 850-2006/CXB/35-170/NN do Cục xuất bản cấp ngày 
14/11/2006. In xong và nộp lưu chiểu quý 1/2007.
```

## Backup summary

| backup_path | file | backup_exists | backup_size | sha256 |
| --- | --- | --- | --- | --- |
| vector_store_backup_before_138docs_rebuild_after_knqg002_text_20260531_121735 | chunks.index | True | 43679277 | 7eaa21cb5c96cda77559abfed98c2ac765c5af5266961ee7ce2c01eb575b602f |
| vector_store_backup_before_138docs_rebuild_after_knqg002_text_20260531_121735 | chunks_meta.pkl | True | 25157380 | f27ffb95aa5b4e4fb00457d5eb657f4202b5f76eb4bcb69b9b0027822d8708cf |
| vector_store_backup_before_138docs_rebuild_after_knqg002_text_20260531_121735 | config.pkl | True | 90 | faa1fcde7ccbb306536a3ecdc1dcbeb173a93b809cc78a419c7f075248777d69 |

## Vector rebuild summary

| item | value |
| --- | --- |
| script/function used | vector_search.build_pipeline() |
| embedding model | sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 |
| chunk size | 800 |
| chunk overlap | 150 |
| parse [WARN] count | 0 |
| parse [ERROR] count | 0 |
| KNQG_002 processed in log | False |
| build log | outputs\vector_store_rebuild_138docs_after_knqg002_pdf_update_build_log_20260531_124915.txt |

| metric | value |
| --- | --- |
| old_chunks | 28437 |
| new_chunks | 28542 |
| old_vector_docs | 137 |
| vector_docs | 138 |
| missing_docs |  |
| extra_docs |  |
| KNQG_002_chunk_count | 105 |
| RIA3_002_in_chunks_meta | False |
| RIA3_003_in_chunks_meta | False |
| index_ntotal | 28542 |
| chunks_meta_rows | 28542 |
| index_chunks_meta_match | True |
| config_model | sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 |

## Chunk statistics

| metric | value |
| --- | --- |
| chunk_count_min | 5 |
| chunk_count_median | 80.5 |
| chunk_count_max | 3390 |
| KNQG_002_chunk_count | 105 |

### Lowest chunk count docs

| doc_id | title | chunk_count | file_path |
| --- | --- | --- | --- |
| TB_005 | Sự hiện diện của bệnh đốm trắng, hoại tử gan tụy cấp và vi bào tử trùng trên tôm giống và tôm nuôi thương phẩm tại một số tỉnh khu vực ĐBSCL từ năm 2022-2024 | 5 | data/raw_docs/TB_005_su_hien_dien_cua_benh_dom_trang_va_EHP_va_AHPND_tai_DBSCL_2022_2024.pdf |
| FAO_045 | Strengthening Capacity for Dealing with Shrimp Infectious Myonecrosis Virus Disease - TCP/INT/3501 | 7 | data/raw_docs/FAO_045_ca6163en.pdf |
| FAO_015 | FAO species catalogue. Vol.13. Marine lobsters of the world. An annotated and illustrated catalogue of marine lobsters known to date | 8 | data/raw_docs/FAO_015_t0411e.pdf |
| TB_002 | Công nghệ gen và chọn giống tôm kháng bệnh, tiềm năng và thách thức | 9 | data/raw_docs/TB_002_cong_nghe_gen_va_chon_giong_tom_khang_benh.pdf |
| FAO_043 | Boosting biosecurity in Peru’s shrimp farming industry for sustainable livelihoods | 10 | data/raw_docs/FAO_043_boosting_biosecurity_peru.pdf |
| FAO_033 | FAO Reference Centres for Antimicrobial Resistance and Aquaculture Biosecurity. Combating AMR together: ensuring healthy and safe aquatic foods | 11 | data/raw_docs/FAO_033_cc6625en.pdf |
| SEAFDEC_007 | Draft genome sequence of Vibrio parahaemolyticus strain PH1339, which causes acute hepatopancreatic necrosis disease in shrimp in the Philippines | 11 | data/raw_docs/SEAFDEC_007_Penir2019.pdf |
| NACA_002 | Shrimp farm biosecurity in Saudi Arabia: A journey from past practices to future vision | 15 | data/raw_docs/NACA_002_1749824700.pdf |
| TCTS_002 | Quy trình kiểm soát Rickettsia-like bacteria (RLB) gây bệnh sữa trên tôm hùm (Panulirus spp.) nuôi lồng | 15 | data/raw_docs/TCTS_002_quy_trinh_kiem_soat_rlb_benh_sua_tom_hum.pdf |
| TB_006 | Hoại tử cơ (IMNV) trên tôm và chiến lược kiểm soát | 16 | data/raw_docs/TB_006_hoai_tu_co_IMNV_tren_tom_va_chien_luoc_kiem_soat.pdf |

## Smoke test results

| query | rank | doc_id | title | score | file_path |
| --- | --- | --- | --- | --- | --- |
| kỹ thuật nuôi tôm hùm lồng phòng trị bệnh | 1 | TCKHTS_002 | Mô hình phòng, trị bệnh sữa, bệnh đỏ thân trên tôm hùm nuôi lồng tại các tỉnh Nam Trung Bộ | 0.7633653879165649 | data/raw_docs/TCKHTS_002_phong_tri_benh_sua_do_than_tom_hum_nam_trung_bo.pdf |
| kỹ thuật nuôi tôm hùm lồng phòng trị bệnh | 2 | RIA3_001 | Quy hoạch nuôi tôm hùm đến năm 2020 và định hướng đến 2030 | 0.7494176030158997 | data/raw_docs/RIA3_001_quy_hoach_nuoi_tom_hum_2030.pdf |
| kỹ thuật nuôi tôm hùm lồng phòng trị bệnh | 3 | KNQG_002 | Kỹ thuật nuôi tôm hùm lồng và các biện pháp phòng trị bệnh | 0.7422624230384827 | data/raw_docs/KNQG_002_ky_thuat_nuoi_tom_hum_long_phong_tri_benh.pdf |
| kỹ thuật nuôi tôm hùm lồng phòng trị bệnh | 4 | RIA3_001 | Quy hoạch nuôi tôm hùm đến năm 2020 và định hướng đến 2030 | 0.7329429388046265 | data/raw_docs/RIA3_001_quy_hoach_nuoi_tom_hum_2030.pdf |
| kỹ thuật nuôi tôm hùm lồng phòng trị bệnh | 5 | RIA3_001 | Quy hoạch nuôi tôm hùm đến năm 2020 và định hướng đến 2030 | 0.7252839803695679 | data/raw_docs/RIA3_001_quy_hoach_nuoi_tom_hum_2030.pdf |
| bệnh sữa đỏ thân tôm hùm nuôi lồng Nam Trung Bộ | 1 | RIA3_001 | Quy hoạch nuôi tôm hùm đến năm 2020 và định hướng đến 2030 | 0.7647292613983154 | data/raw_docs/RIA3_001_quy_hoach_nuoi_tom_hum_2030.pdf |
| bệnh sữa đỏ thân tôm hùm nuôi lồng Nam Trung Bộ | 2 | TCKHTS_002 | Mô hình phòng, trị bệnh sữa, bệnh đỏ thân trên tôm hùm nuôi lồng tại các tỉnh Nam Trung Bộ | 0.7638168931007385 | data/raw_docs/TCKHTS_002_phong_tri_benh_sua_do_than_tom_hum_nam_trung_bo.pdf |
| bệnh sữa đỏ thân tôm hùm nuôi lồng Nam Trung Bộ | 3 | KNQG_002 | Kỹ thuật nuôi tôm hùm lồng và các biện pháp phòng trị bệnh | 0.7614257335662842 | data/raw_docs/KNQG_002_ky_thuat_nuoi_tom_hum_long_phong_tri_benh.pdf |
| bệnh sữa đỏ thân tôm hùm nuôi lồng Nam Trung Bộ | 4 | TCKHTS_002 | Mô hình phòng, trị bệnh sữa, bệnh đỏ thân trên tôm hùm nuôi lồng tại các tỉnh Nam Trung Bộ | 0.7417072057723999 | data/raw_docs/TCKHTS_002_phong_tri_benh_sua_do_than_tom_hum_nam_trung_bo.pdf |
| bệnh sữa đỏ thân tôm hùm nuôi lồng Nam Trung Bộ | 5 | TCKHTS_002 | Mô hình phòng, trị bệnh sữa, bệnh đỏ thân trên tôm hùm nuôi lồng tại các tỉnh Nam Trung Bộ | 0.7101368308067322 | data/raw_docs/TCKHTS_002_phong_tri_benh_sua_do_than_tom_hum_nam_trung_bo.pdf |
| nuôi cá lồng bè trên biển Khánh Hòa | 1 | VJAS_002 | Tổng quan về bệnh do vi khuẩn Streptococcus iniae gây ra trên cá biển | 0.8101930618286133 | data/raw_docs/VJAS_002_streptococcus_iniae_benh_ca_bien.pdf |
| nuôi cá lồng bè trên biển Khánh Hòa | 2 | CTU_002 | Kỹ thuật sản xuất giống và nuôi cá biển | 0.7945906519889832 | data/raw_docs/CTU_002_ky_thuat_san_xuat_giong_va_nuoi_ca_bien.pdf |
| nuôi cá lồng bè trên biển Khánh Hòa | 3 | CTU_002 | Kỹ thuật sản xuất giống và nuôi cá biển | 0.7806572914123535 | data/raw_docs/CTU_002_ky_thuat_san_xuat_giong_va_nuoi_ca_bien.pdf |
| nuôi cá lồng bè trên biển Khánh Hòa | 4 | KNQG_001 | Phát triển nuôi cá lồng bè trên biển bền vững, thích ứng biến đổi khí hậu | 0.7742005586624146 | data/raw_docs/KNQG_001_phat_trien_nuoi_ca_long_be_tren_bien.pdf |
| nuôi cá lồng bè trên biển Khánh Hòa | 5 | NACA_001 | Status, technological innovations, and industry development needs of mud crab (Scylla spp.) aquaculture | 0.7657663226127625 | data/raw_docs/NACA_001_1737869839.pdf |
| EHP tôm thẻ Quảng Ninh Nam Định | 1 | TCKHTS_002 | Mô hình phòng, trị bệnh sữa, bệnh đỏ thân trên tôm hùm nuôi lồng tại các tỉnh Nam Trung Bộ | 0.6851251125335693 | data/raw_docs/TCKHTS_002_phong_tri_benh_sua_do_than_tom_hum_nam_trung_bo.pdf |
| EHP tôm thẻ Quảng Ninh Nam Định | 2 | VJAS_001 | Nghiên cứu bệnh vi bào tử trùng Enterocytozoon hepatopenaei (EHP) trên tôm thẻ chân trắng nuôi tại Quảng Ninh và Nam Định | 0.6780955791473389 | data/raw_docs/VJAS_001_ehp_tom_the_quang_ninh_nam_dinh.pdf |
| EHP tôm thẻ Quảng Ninh Nam Định | 3 | RIA3_001 | Quy hoạch nuôi tôm hùm đến năm 2020 và định hướng đến 2030 | 0.6613268256187439 | data/raw_docs/RIA3_001_quy_hoach_nuoi_tom_hum_2030.pdf |
| EHP tôm thẻ Quảng Ninh Nam Định | 4 | KKTY_001 | Tỷ lệ nhiễm và mức độ mẫn cảm kháng sinh của vi khuẩn Vibrio parahaemolyticus phân lập từ tôm hùm bông (Panulirus ornatus) nuôi lồng ở vùng biển tỉnh Phú Yên | 0.6387704014778137 | data/raw_docs/KKTY_001_vibrio_khang_sinh_tom_hum_bong_phu_yen.pdf |
| EHP tôm thẻ Quảng Ninh Nam Định | 5 | RIA3_001 | Quy hoạch nuôi tôm hùm đến năm 2020 và định hướng đến 2030 | 0.6265558004379272 | data/raw_docs/RIA3_001_quy_hoach_nuoi_tom_hum_2030.pdf |
| AHPND shrimp disease | 1 | PMC_029 | Selection of Lactic Acid Bacteria (LAB) Antagonizing Vibrio parahaemolyticus: The Pathogen of Acute Hepatopancreatic Necrosis Disease (AHPND) in Whiteleg Shrimp (Penaeus vannamei) | 0.8789482712745667 | data/raw_docs/PMC_029_PMC6955853.pdf |
| AHPND shrimp disease | 2 | SEAFDEC_008 | Current status and impact of early mortality syndrome (EMS)/acute hepatopancreatic necrosis disease (AHPND) and hepatopancreatic microsporidiosis (HPM) outbreaks on Thailand’s shrimp farming | 0.8407975435256958 | data/raw_docs/SEAFDEC_008_Putth2016.pdf |
| AHPND shrimp disease | 3 | FAO_006 | FAO Second International Technical Seminar/Workshop on Acute hepatopancreatic necrosis disease (AHPND), Bangkok, Thailand 23–25 June 2016 | 0.8256773948669434 | data/raw_docs/FAO_006_bt131e.pdf |
| AHPND shrimp disease | 4 | FAO_001 | Shrimp acute hepatopancreatic necrosis disease strategy manual | 0.8200538158416748 | data/raw_docs/FAO_001_cb2119en.pdf |
| AHPND shrimp disease | 5 | PMC_010 | A Review of the Functional Annotations of Important Genes in the AHPND-Causing pVA1 Plasmid | 0.8019028306007385 | data/raw_docs/PMC_010_PMC7409025.pdf |

### Manual smoke checks

| check | expected | top5_doc_ids | hit |
| --- | --- | --- | --- |
| Query 1 th?y KNQG_002 | KNQG_002 | TCKHTS_002; RIA3_001; KNQG_002; RIA3_001; RIA3_001 | YES |
| Query 2 th?y TCKHTS_002 ho?c KNQG_002 | TCKHTS_002; KNQG_002 | RIA3_001; TCKHTS_002; KNQG_002; TCKHTS_002; TCKHTS_002 | YES |
| Query 3 th?y KNQG_001 ho?c c? bi?n/l?ng b? li?n quan | KNQG_001; JFST_001; CTU_002; TCKHTS_006; TCKHTS_007; CTU_JOURNAL_003; VJAS_002; TCKHTS_008; TCKHTS_009 | VJAS_002; CTU_002; CTU_002; KNQG_001; NACA_001 | YES |
| Query 4 th?y VJAS_001 ho?c EHP docs | VJAS_001; PMC_003; PMC_008; PMC_011; PMC_027; DLU_002 | TCKHTS_002; VJAS_001; RIA3_001; KKTY_001; RIA3_001 | YES |
| Query 5 th?y AHPND docs | FAO_001; FAO_006; MDPI_001; AAF_001; PMC_007; PMC_029; SEAFDEC_006 | PMC_029; SEAFDEC_008; FAO_006; FAO_001; PMC_010 | YES |

## Problems / warnings

Kh?ng ph?t hi?n v?n ??.

## Next step recommendation

C? th? chuy?n sang b??c sync/update ontology/KG facts cho corpus 138 t?i li?u, sau ?? verify KG runtime.

## Output files

- `outputs\knqg002_text_extraction_after_pdf_update_report.md`
- `outputs\knqg002_text_extraction_after_pdf_update_summary.csv`
- `outputs\vector_store_rebuild_138docs_after_knqg002_pdf_update_report.md`
- `outputs\vector_store_rebuild_138docs_after_knqg002_pdf_update_summary.csv`
- `outputs\vector_store_rebuild_138docs_after_knqg002_pdf_update_doc_chunk_counts.csv`
- `outputs\vector_store_rebuild_138docs_after_knqg002_pdf_update_smoke_tests.csv`
- `outputs\vector_store_rebuild_138docs_after_knqg002_pdf_update_build_log_20260531_124915.txt`
