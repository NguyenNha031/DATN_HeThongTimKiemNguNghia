# Metadata/raw docs audit sau khi th?m t?i li?u m?i

- Th?i ?i?m audit: 2026-05-31 00:35:23
- Metadata: `data\metadata\document_metadata_cleaned.xlsx`
- Raw docs: `data\raw_docs`
- Snapshot ??i chi?u: final_submission_package\data\metadata\document_metadata_cleaned.xlsx (110 d?ng)
- Ph?m vi: ch? ??c metadata/raw docs v? t?o report audit; kh?ng rebuild vector store, kh?ng sync ontology/KG, kh?ng ch?y baseline/metrics/latency.

## Executive summary

| metric | value |
| --- | --- |
| PASS / NEEDS_FIX / BLOCKED | NEEDS_FIX |
| T?ng docs metadata hi?n t?i | 140 |
| T?ng raw files | 140 |
| S? doc m?i so v?i 110 | 30 |
| Doc m?i theo diff package c? | 30 |
| S? l?i nghi?m tr?ng | 6 |
| Warnings | 14 |
| C? th? rebuild vector store ch?a? | CH?A |

## Metadata structure check

- T?ng s? d?ng: **140**
- T?ng s? c?t: **15**
- T?n c?t: `doc_id`, `title`, `author`, `publishedYear`, `source`, `referenceUrl`, `docType`, `file_path`, `related_taxon`, `related_disease`, `related_location`, `production_mode`, `keywords`, `language`, `note`
- S? `doc_id` unique: **140**
- S? d?ng duplicate `doc_id`: **0**
- C?t b?t bu?c b? thi?u: **0**

| column | present | missing_rows | unique_nonempty |
| --- | --- | --- | --- |
| doc_id | YES | 0 | 140 |
| title | YES | 0 | 140 |
| author | YES | 0 | 116 |
| publishedYear | YES | 0 | 29 |
| source | YES | 0 | 45 |
| referenceUrl | YES | 7 | 129 |
| docType | YES | 0 | 31 |
| file_path | YES | 0 | 140 |
| related_taxon | YES | 1 | 72 |
| related_disease | YES | 52 | 49 |
| related_location | YES | 37 | 67 |
| production_mode | YES | 0 | 33 |
| keywords | YES | 0 | 140 |
| language | YES | 0 | 2 |
| note | YES | 1 | 139 |

## Metadata vs raw_docs check

| metric | value |
| --- | --- |
| matched metadata rows | 134 |
| missing raw files | 6 |
| unreferenced raw files | 6 |
| duplicate file_path groups | 0 |
| zero-byte files | 0 |
| suspicious extension | 0 |
| file_path outside data/raw_docs | 0 |

### Raw docs theo extension

| extension | file_count |
| --- | --- |
| .pdf | 140 |

### Raw files kh?ng ???c metadata tham chi?u

| relative_raw_path | size_bytes | extension | reference_count |
| --- | --- | --- | --- |
| MDPI_001_vibrio_ahpnd_mekong_delta.pdf.pdf | 1225850 | .pdf | 0 |
| TCKHTS_002_phong_tri_benh_sua_do_than_tom_hum_nam_trung_bo.pdf.pdf | 838162 | .pdf | 0 |
| TCKHTS_003_cung_cap_con_giong_tom_hum_bong_viet_nam.pdf.pdf | 1937765 | .pdf | 0 |
| TNU_JST_001_doc_luc_vibrio_tom_the_chan_trang.pdf.pdf | 528397 | .pdf | 0 |
| VJAS_001_ehp_tom_the_quang_ninh_nam_dinh.pdf.pdf | 1172666 | .pdf | 0 |
| VJMST_001_hien_trang_ntts_dam_thuy_trieu_cam_lam.pdf.pdf | 2560728 | .pdf | 0 |

### File/path c?n ki?m tra

| severity | doc_id | column | file_path | issue | suggestion |
| --- | --- | --- | --- | --- | --- |
| CRITICAL | VJMST_001 | file_path | data/raw_docs/VJMST_001_hien_trang_ntts_dam_thuy_trieu_cam_lam.pdf | Raw file kh?ng t?n t?i tr?n disk | Ki?m tra t?n file/path ho?c b? sung file raw |
| CRITICAL | TCKHTS_002 | file_path | data/raw_docs/TCKHTS_002_phong_tri_benh_sua_do_than_tom_hum_nam_trung_bo.pdf | Raw file kh?ng t?n t?i tr?n disk | Ki?m tra t?n file/path ho?c b? sung file raw |
| CRITICAL | TCKHTS_003 | file_path | data/raw_docs/TCKHTS_003_cung_cap_con_giong_tom_hum_bong_viet_nam.pdf | Raw file kh?ng t?n t?i tr?n disk | Ki?m tra t?n file/path ho?c b? sung file raw |
| CRITICAL | VJAS_001 | file_path | data/raw_docs/VJAS_001_ehp_tom_the_quang_ninh_nam_dinh.pdf | Raw file kh?ng t?n t?i tr?n disk | Ki?m tra t?n file/path ho?c b? sung file raw |
| CRITICAL | TNU_JST_001 | file_path | data/raw_docs/TNU_JST_001_doc_luc_vibrio_tom_the_chan_trang.pdf | Raw file kh?ng t?n t?i tr?n disk | Ki?m tra t?n file/path ho?c b? sung file raw |
| CRITICAL | MDPI_001 | file_path | data/raw_docs/MDPI_001_vibrio_ahpnd_mekong_delta.pdf | Raw file kh?ng t?n t?i tr?n disk | Ki?m tra t?n file/path ho?c b? sung file raw |

## New docs review

C? **30** doc_id m?i so v?i package c? 110 t?i li?u.

| doc_id | title | file_path | source | docType | related_taxon | related_disease | related_location | production_mode | language | raw_file_exists |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| VJMST_001 | Hiện trạng nuôi trồng và khai thác thủy sản tại đầm Thủy Triều huyện Cam Lâm, tỉnh Khánh Hòa | data/raw_docs/VJMST_001_hien_trang_ntts_dam_thuy_trieu_cam_lam.pdf | Tạp chí Khoa học và Công nghệ Biển | Journal article | thủy sản; aquatic animals |  | đầm Thủy Triều; Cam Lâm; Khánh Hòa; Việt Nam | aquaculture; capture fisheries; coastal lagoon aquaculture | Vietnamese | NO |
| KNQG_001 | Phát triển nuôi cá lồng bè trên biển bền vững, thích ứng biến đổi khí hậu | data/raw_docs/KNQG_001_phat_trien_nuoi_ca_long_be_tren_bien.pdf | Trung tâm Khuyến nông Quốc gia | Technical report | cá biển; cá bớp; marine fish |  | Khánh Hòa; Việt Nam; Nam Trung Bộ | marine aquaculture; cage culture; offshore cage farming | Vietnamese | YES |
| YERSIN_001 | Đánh giá tính bền vững nghề nuôi tôm tại huyện Ninh Hòa - tỉnh Khánh Hòa | data/raw_docs/YERSIN_001_ben_vung_nghe_nuoi_tom_ninh_hoa.pdf | Tạp chí Khoa học Yersin | Journal article | tôm; shrimp |  | Ninh Hòa; Khánh Hòa; Việt Nam | shrimp farming; sustainable aquaculture; aquaculture | Vietnamese | YES |
| JFST_001 | Nuôi cá chẽm (Lates calcarifer, Bloch, 1790) thương phẩm trong hệ thống “sông trong ao” tại Khánh Hòa | data/raw_docs/JFST_001_nuoi_ca_chem_song_trong_ao_khanh_hoa.pdf | Tạp chí Khoa học - Công nghệ Thủy sản | Journal article | cá chẽm; seabass; Lates calcarifer |  | Khánh Hòa; Việt Nam | aquaculture; seabass farming; in pond raceway system; commercial fish culture | Vietnamese | YES |
| CTU_001 | Kỹ thuật sản xuất giống và nuôi giáp xác | data/raw_docs/CTU_001_ky_thuat_san_xuat_giong_va_nuoi_giap_xac.pdf | Nhà xuất bản Đại học Cần Thơ | Textbook | tôm biển; tôm sú; tôm càng xanh; cua biển; crustaceans |  | Việt Nam | hatchery; seed production; crustacean farming; aquaculture | Vietnamese | YES |
| TCKHTS_002 | Mô hình phòng, trị bệnh sữa, bệnh đỏ thân trên tôm hùm nuôi lồng tại các tỉnh Nam Trung Bộ | data/raw_docs/TCKHTS_002_phong_tri_benh_sua_do_than_tom_hum_nam_trung_bo.pdf | Tạp chí Khoa học - Công nghệ Thủy sản | Journal article | tôm hùm; tôm hùm bông; tôm hùm xanh; spiny lobster; Panulirus ornatus; Panulirus homarus | bệnh sữa; bệnh đỏ thân; milk hemolymph disease; red body disease | Bình Định; Phú Yên; Khánh Hòa; Nam Trung Bộ; Việt Nam | marine aquaculture; cage culture; lobster farming | Vietnamese | NO |
| TCTS_002 | Quy trình kiểm soát Rickettsia-like bacteria (RLB) gây bệnh sữa trên tôm hùm (Panulirus spp.) nuôi lồng | data/raw_docs/TCTS_002_quy_trinh_kiem_soat_rlb_benh_sua_tom_hum.pdf | Cục Thủy sản | Technical guideline | tôm hùm; Panulirus spp.; lobster | bệnh sữa; Rickettsia-like bacteria; RLB | Nha Trang; Khánh Hòa; Việt Nam | marine aquaculture; cage culture; lobster farming | Vietnamese | YES |
| HUIB_001 | Khả năng hình thành màng sinh học và tính kháng kháng sinh của Vibrio parahaemolyticus phân lập từ tôm hùm Panulirus spp. nuôi | data/raw_docs/HUIB_001_vibrio_biofilm_khang_khang_sinh_tom_hum.pdf | Hội nghị Công nghệ Sinh học toàn quốc 2020 | Conference paper | tôm hùm; Panulirus spp.; Panulirus homarus; Panulirus ornatus; lobster | Vibrio parahaemolyticus; vibriosis | Bình Ba; Khánh Hòa; Việt Nam | marine aquaculture; cage culture; lobster farming | Vietnamese | YES |
| KKTY_001 | Tỷ lệ nhiễm và mức độ mẫn cảm kháng sinh của vi khuẩn Vibrio parahaemolyticus phân lập từ tôm hùm bông (Panulirus ornatus) nuôi lồng ở vùng biển tỉnh Phú Yên | data/raw_docs/KKTY_001_vibrio_khang_sinh_tom_hum_bong_phu_yen.pdf | Tạp chí Khoa học kỹ thuật Thú y | Journal article | tôm hùm bông; Panulirus ornatus; lobster | Vibrio parahaemolyticus; vibriosis | Cù Mông; Xuân Đài; An Chấn; Phú Yên; Việt Nam | marine aquaculture; cage culture; lobster farming | Vietnamese | YES |
| TCKHTS_003 | Tình hình cung cấp con giống tôm hùm bông (Panulirus ornatus) ở Việt Nam: hiện trạng và trở ngại | data/raw_docs/TCKHTS_003_cung_cap_con_giong_tom_hum_bong_viet_nam.pdf | Tạp chí Khoa học - Công nghệ Thủy sản | Journal article | tôm hùm bông; Panulirus ornatus; puerulus; lobster seed |  | Việt Nam; Khánh Hòa; Nha Trang; Ninh Hòa; Cam Ranh; Phú Yên; Bình Định | marine aquaculture; lobster farming; seed supply; nursery | Vietnamese | NO |
| KNQG_002 | Kỹ thuật nuôi tôm hùm lồng và các biện pháp phòng trị bệnh | data/raw_docs/KNQG_002_ky_thuat_nuoi_tom_hum_long_phong_tri_benh.pdf | Trung tâm Khuyến ngư Quốc gia | Technical manual | tôm hùm; lobster; Panulirus spp. | bệnh tôm hùm; bệnh sữa; bệnh đỏ thân | Việt Nam; Nam Trung Bộ; Khánh Hòa | marine aquaculture; cage culture; lobster farming | Vietnamese | YES |
| CTU_JOURNAL_001 | Phân tích hiệu quả sản xuất các mô hình nuôi tôm thẻ chân trắng và tôm sú thâm canh ở tỉnh Ninh Thuận | data/raw_docs/CTU_JOURNAL_001_hieu_qua_mo_hinh_nuoi_tom_ninh_thuan.pdf | Tạp chí Khoa học Trường Đại học Cần Thơ | Journal article | tôm thẻ chân trắng; white-leg shrimp; tôm sú; black tiger shrimp |  | Ninh Thuận; Việt Nam | shrimp farming; intensive aquaculture; intensive shrimp farming | Vietnamese | YES |
| CTU_JOURNAL_002 | Phân tích hiệu quả kỹ thuật và tài chính của mô hình nuôi tôm thẻ chân trắng ở tỉnh Cà Mau | data/raw_docs/CTU_JOURNAL_002_hieu_qua_ky_thuat_tai_chinh_tom_the_ca_mau.pdf | Tạp chí Khoa học Trường Đại học Cần Thơ | Journal article | tôm thẻ chân trắng; Penaeus vannamei; white-leg shrimp |  | Cà Mau; Việt Nam | shrimp farming; intensive shrimp farming; aquaculture production | Vietnamese | YES |
| TCKHTS_004 | Thực trạng, tiềm năng và giải pháp phát triển nuôi tôm trên cát ở khu vực miền Trung | data/raw_docs/TCKHTS_004_nuoi_tom_tren_cat_mien_trung.pdf | Tạp chí Khoa học - Công nghệ Thủy sản | Journal article | tôm; shrimp | dịch bệnh tôm; shrimp disease risk | miền Trung; Việt Nam; vùng ven biển miền Trung | shrimp farming; coastal aquaculture; sand-based shrimp farming | Vietnamese | YES |
| VAP_001 | Ô nhiễm môi trường trầm tích vùng nuôi và rủi ro đối với hoạt động nuôi lồng bè ven biển Nam Trung Bộ | data/raw_docs/VAP_001_o_nhiem_tram_tich_vung_nuoi_long_be_nam_trung_bo.pdf | Kỷ yếu Hội nghị Nghiên cứu cơ bản trong Khoa học Trái đất và Môi trường | Conference paper | tôm hùm; marine aquaculture species |  | Nam Trung Bộ; Việt Nam; vùng ven biển Nam Trung Bộ | marine aquaculture; cage culture; lobster farming; coastal aquaculture | Vietnamese | YES |
| VAWRE_001 | Nghiên cứu biến động và giải pháp kiểm soát chất lượng môi trường vùng nuôi tôm tập trung tại Quảng Ninh | data/raw_docs/VAWRE_001_chat_luong_moi_truong_vung_nuoi_tom_quang_ninh.pdf | Viện Khoa học Thủy lợi Việt Nam | Thesis | tôm; shrimp |  | Quảng Ninh; Việt Nam | shrimp farming; intensive shrimp farming; aquaculture environmental management | Vietnamese | YES |
| TCKHTS_005 | Tổng quan Decapod iridescent virus 1 (DIV1) gây bệnh ở tôm | data/raw_docs/TCKHTS_005_tong_quan_div1_gay_benh_o_tom.pdf | Tạp chí Khoa học - Công nghệ Thủy sản | Journal article | tôm; shrimp; tôm thẻ chân trắng; Penaeus vannamei; tôm càng xanh; Macrobrachium rosenbergii; giáp xác | Decapod iridescent virus 1; DIV1; bệnh virus trên tôm | Việt Nam; Trung Quốc; Thái Lan; Ấn Độ Dương; Đài Loan | shrimp farming; aquaculture; crustacean aquaculture | Vietnamese | YES |
| VJAS_001 | Nghiên cứu bệnh vi bào tử trùng Enterocytozoon hepatopenaei (EHP) trên tôm thẻ chân trắng nuôi tại Quảng Ninh và Nam Định | data/raw_docs/VJAS_001_ehp_tom_the_quang_ninh_nam_dinh.pdf | Tạp chí Khoa học Nông nghiệp Việt Nam | Journal article | tôm thẻ chân trắng; white-leg shrimp; Penaeus vannamei | EHP; Enterocytozoon hepatopenaei; vi bào tử trùng | Quảng Ninh; Nam Định; miền Bắc Việt Nam; Việt Nam | shrimp farming; white-leg shrimp farming; aquaculture | Vietnamese | NO |
| TNU_JST_001 | Điều tra độc lực của vi khuẩn Vibrio parahaemolyticus gây bệnh trên tôm thẻ chân trắng | data/raw_docs/TNU_JST_001_doc_luc_vibrio_tom_the_chan_trang.pdf | TNU Journal of Science and Technology | Journal article | tôm thẻ chân trắng; white-leg shrimp; Penaeus vannamei | Vibrio parahaemolyticus; vibriosis; AHPND risk | Việt Nam | shrimp farming; white-leg shrimp farming; aquaculture | Vietnamese | NO |
| MDPI_001 | Prevalence of Vibrio parahaemolyticus Causing Acute Hepatopancreatic Necrosis Disease of Shrimp in Shrimp, Molluscan Shellfish and Water Samples in the Mekon... | data/raw_docs/MDPI_001_vibrio_ahpnd_mekong_delta.pdf | Biology | Journal article | shrimp; molluscan shellfish | AHPND; acute hepatopancreatic necrosis disease; Vibrio parahaemolyticus; VpAHPND | Mekong Delta; Vietnam | shrimp farming; aquaculture; pond aquaculture | English | NO |
| AAF_001 | Characteristics and diversity of Vibrio parahaemolyticus causing acute hepatopancreatic necrosis disease in Vietnam | data/raw_docs/AAF_001_vibrio_ahpnd_diversity_vietnam.pdf | Aquaculture and Fisheries | Journal article | shrimp; Penaeus vannamei | AHPND; acute hepatopancreatic necrosis disease; Vibrio parahaemolyticus; VpAHPND | Vietnam | shrimp farming; aquaculture | English | YES |
| DLU_002 | Nghiên cứu sự nhiễm vi rút đốm trắng (WSSV) ở tôm càng (Macrobrachium nipponense) và khả năng lan truyền bệnh sang tôm thẻ chân trắng (Litopenaeus vannamei) | data/raw_docs/DLU_002_wssv_tom_cang_lay_sang_tom_the.pdf | Thư viện số Trường Đại học Đà Lạt | Journal article | tôm càng; Macrobrachium nipponense; tôm thẻ chân trắng; Litopenaeus vannamei; Penaeus vannamei | WSSV; white spot syndrome virus; bệnh đốm trắng | Việt Nam | shrimp farming; aquaculture; disease transmission | Vietnamese | YES |
| VJMST_003 | Đánh giá sức tải môi trường vực nước Thủy Triều - Cam Ranh | data/raw_docs/VJMST_003_suc_tai_moi_truong_thuy_trieu_cam_ranh.pdf | Tạp chí Khoa học và Công nghệ Biển | Journal article | thủy sản; aquatic animals |  | Thủy Triều; Cam Ranh; Khánh Hòa; Việt Nam | aquaculture environmental management; coastal water management | Vietnamese | YES |
| TCKHTS_006 | Phân lập và định danh vi khuẩn Photobacterium damselae gây bệnh trên cá chim vây vàng tại Khánh Hòa bằng phương pháp sinh hóa và phân tử | data/raw_docs/TCKHTS_006_photobacterium_ca_chim_vay_vang_khanh_hoa.pdf | Tạp chí Khoa học - Công nghệ Thủy sản | Journal article | cá chim vây vàng; golden pompano; Trachinotus spp. | Photobacterium damselae; Photobacterium damselae subsp. damselae; nhiễm trùng xuất huyết; lở loét | Khánh Hòa; Việt Nam | marine fish farming; cage culture; aquaculture | Vietnamese | YES |
| TCKHTS_007 | Một số đặc điểm sinh học của vi khuẩn Vibrio harveyi gây bệnh xuất huyết lở loét ở cá chẽm nuôi tại Khánh Hòa | data/raw_docs/TCKHTS_007_vibrio_harveyi_ca_chem_khanh_hoa.pdf | Tạp chí Khoa học - Công nghệ Thủy sản | Journal article | cá chẽm; barramundi; Lates calcarifer | Vibrio harveyi; bệnh xuất huyết lở loét; hemorrhagic ulcerative disease | Vạn Ninh; Khánh Hòa; Việt Nam | marine fish farming; cage culture; aquaculture | Vietnamese | YES |
| CTU_JOURNAL_003 | Hiện trạng nhiễm ký sinh trùng trên cá bớp (Rachycentron canadum) nuôi lồng ở tỉnh Kiên Giang | data/raw_docs/CTU_JOURNAL_003_ky_sinh_trung_ca_bop_kien_giang.pdf | Tạp chí Khoa học Trường Đại học Cần Thơ | Journal article | cá bớp; cobia; Rachycentron canadum | ký sinh trùng; parasitic infection; Amyloodinium ocellatum; Cryptocaryon irritans; Neobenedenia sp.; Pseudorhabdosynochus sp.; Parapetalus sp.; Leptorhynchoi... | Kiên Giang; Phú Quốc; Tiên Hải; Hòn Nghệ; Nam Du; Việt Nam | cage culture; marine fish farming; aquaculture | Vietnamese | YES |
| CTU_002 | Kỹ thuật sản xuất giống và nuôi cá biển | data/raw_docs/CTU_002_ky_thuat_san_xuat_giong_va_nuoi_ca_bien.pdf | Nhà xuất bản Đại học Cần Thơ | Textbook | cá biển; marine fish |  | Việt Nam | marine aquaculture; hatchery; seed production; marine fish farming | Vietnamese | YES |
| VJAS_002 | Tổng quan về bệnh do vi khuẩn Streptococcus iniae gây ra trên cá biển | data/raw_docs/VJAS_002_streptococcus_iniae_benh_ca_bien.pdf | Tạp chí Khoa học Nông nghiệp Việt Nam | Journal article | cá biển; marine fish; cá chim vây vàng; cá chẽm; cá mú; cá dìa; cá giò; cá nâu | Streptococcus iniae; streptococcosis; bệnh do vi khuẩn trên cá biển | Việt Nam | marine fish farming; aquaculture; cage culture | Vietnamese | YES |
| TCKHTS_008 | Bệnh mù mắt do liên cầu khuẩn gây ra ở cá bớp nuôi tại Khánh Hòa | data/raw_docs/TCKHTS_008_streptococcus_iniae_ca_bop_khanh_hoa.pdf | Tạp chí Khoa học - Công nghệ Thủy sản | Journal article | cá bớp; cobia; Rachycentron canadum | Streptococcus iniae; bệnh mù mắt; streptococcosis | Khánh Hòa; Việt Nam | marine fish farming; cage culture; aquaculture | Vietnamese | YES |
| TCKHTS_009 | Nghiên cứu mối quan hệ phát sinh loài của sán lá song chủ ký sinh trên cá chẽm (Lates calcarifer Bloch, 1790) nuôi tại Khánh Hòa | data/raw_docs/TCKHTS_009_san_la_song_chu_ca_chem_khanh_hoa.pdf | Tạp chí Khoa học - Công nghệ Thủy sản | Journal article | cá chẽm; seabass; Lates calcarifer | sán lá song chủ; Digenea; ký sinh trùng cá biển | Khánh Hòa; Việt Nam | marine fish farming; aquaculture | Vietnamese | YES |

## Entity/fact readiness

| field | docs_with_value | docs_missing | coverage_pct |
| --- | --- | --- | --- |
| related_taxon | 139 | 1 | 99.29 |
| related_disease | 88 | 52 | 62.86 |
| related_location | 103 | 37 | 73.57 |
| production_mode | 140 | 0 | 100.0 |
| all_four_fields | 51 | 89 | 36.43 |
| zero_fact_fields | 0 | 140 | 0.0 |

### Field quality summary

#### related_taxon

- S? gi? tr? r?ng: **1**
- Delimiter counts: ;: 120; [none]: 19
- Delimiter kh?ng nh?t qu?n: **False**

| value | count |
| --- | --- |
| Penaeus vannamei; shrimp | 21 |
| shrimp | 11 |
| aquatic animals; fish; shrimp | 7 |
| shrimp; Penaeus vannamei | 5 |
| shrimp; Penaeus monodon; Penaeus vannamei | 4 |
| tôm; shrimp | 4 |
| fish | 3 |
| aquatic species; fish | 3 |
| shrimp; Penaeus vannamei; Penaeus monodon | 2 |
| Penaeus monodon; shrimp | 2 |
| fish; aquatic species | 2 |
| aquatic animals; fish | 2 |
| lobster | 2 |
| aquatic species; fish; shellfish | 2 |
| fish; aquatic animals | 2 |
| aquatic species; fish; shrimp | 2 |
| shrimp; prawns | 2 |
| penaeid shrimp; shrimp | 2 |
| Penaeus vannamei | 2 |
| Penaeus vannamei; larvae; shrimp | 2 |
| Litopenaeus vannamei; tôm thẻ chân trắng | 2 |
| thủy sản; aquatic animals | 2 |
| cá chẽm; seabass; Lates calcarifer | 2 |
| tôm thẻ chân trắng; white-leg shrimp; Penaeus vannamei | 2 |
| cá bớp; cobia; Rachycentron canadum | 2 |
| shrimp; prawns; Penaeus vannamei; Penaeus monodon | 1 |
| shrimp; crustaceans | 1 |
| aquatic animals; fish; crustaceans | 1 |
| shrimp; prawns; Penaeus vannamei | 1 |
| Penaeus vannamei; Penaeus stylirostris; shrimp | 1 |

#### related_disease

- S? gi? tr? r?ng: **52**
- Delimiter counts: [none]: 23; ;: 65
- Delimiter kh?ng nh?t qu?n: **False**

| value | count |
| --- | --- |
| AHPND; vibriosis | 11 |
| vibriosis | 8 |
| WSSV | 7 |
| EHP; Enterocytozoon hepatopenaei | 5 |
| AHPND | 4 |
| IMN | 4 |
| AHPND; EMS | 2 |
| EHP; Ecytonucleospora hepatopenaei | 2 |
| Vibrio spp.; Rickettsia-like bacteria | 2 |
| IMNV; hoại tử cơ truyền nhiễm | 2 |
| Vibrio parahaemolyticus; vibriosis | 2 |
| AHPND; acute hepatopancreatic necrosis disease; Vibrio parahaemolyticus; VpAHPND | 2 |
| WSSV; yellow head virus; IMN; AHPND | 1 |
| WSSV; WSD | 1 |
| AHPND; HPM; EHP | 1 |
| AHPND; WSSV | 1 |
| WSSV; vibriosis | 1 |
| WSSV; TSV; IHHNV; YHV | 1 |
| AHPND; EMS; HPM; EHP | 1 |
| AHPND; EMS; WSSV; IMN | 1 |
| WSSV; AHPND; EHP; bacterial spore | 1 |
| EMS; AHPNS; AHPND | 1 |
| EHP; Enterocytozoon hepatopenaei; HPM | 1 |
| vibriosis; AHPND | 1 |
| IMN; vibriosis | 1 |
| WSSV; HPV; MBV; IHHNV | 1 |
| Las bolitas syndrome; AHPND | 1 |
| EHP; Enterocytozoon hepatopenaei; decapod hepanhamaparvovirus genotype V | 1 |
| vibriosis; AHPND; zoea 2 syndrome | 1 |
| translucent post-larvae disease; TPD; vibriosis | 1 |

#### related_location

- S? gi? tr? r?ng: **37**
- Delimiter counts: [none]: 53; ;: 50
- Delimiter kh?ng nh?t qu?n: **False**

| value | count |
| --- | --- |
| Global | 20 |
| Việt Nam | 6 |
| India | 4 |
| Khánh Hòa; Việt Nam | 4 |
| Philippines | 3 |
| Asia; Pacific | 2 |
| Vietnam | 2 |
| Thailand | 2 |
| Latin America | 2 |
| Vietnam; Asia; Latin America | 1 |
| Latin America; Caribbean | 1 |
| Thailand; Bangkok; Global | 1 |
| Central Asia; Caucasus; Kazakhstan | 1 |
| Thailand; Bangkok | 1 |
| Asia | 1 |
| Bangladesh; Khulna; Satkhira | 1 |
| Canada; China; Global | 1 |
| inland waters; Hungary; Global | 1 |
| Europe | 1 |
| coastal areas; marine environment | 1 |
| Uganda; Africa | 1 |
| Indian Ocean; Southern Africa | 1 |
| Azerbaijan | 1 |
| Bosnia and Herzegovina | 1 |
| Vietnam; Mekong Delta; Bac Lieu; Ben Tre; Ca Mau | 1 |
| India; Bangladesh | 1 |
| Bangladesh | 1 |
| Singapore; Global | 1 |
| Saudi Arabia | 1 |
| Australia; China; India; Indonesia; Malaysia; Philippines; Thailand; Vietnam | 1 |

#### production_mode

- S? gi? tr? r?ng: **0**
- Delimiter counts: [none]: 100; ;: 40
- Delimiter kh?ng nh?t qu?n: **False**

| value | count |
| --- | --- |
| shrimp aquaculture | 64 |
| aquaculture | 20 |
| hatchery aquaculture | 11 |
| inland fisheries; aquaculture | 5 |
| marine aquaculture; cage culture; lobster farming | 5 |
| marine fish farming; cage culture; aquaculture | 3 |
| capture fisheries | 2 |
| aquaculture; fisheries | 2 |
| fisheries; aquaculture | 2 |
| marine aquaculture | 2 |
| shrimp farming; white-leg shrimp farming; aquaculture | 2 |
| coastal aquaculture | 1 |
| marine aquaculture; shrimp aquaculture | 1 |
| aquaculture; capture fisheries; coastal lagoon aquaculture | 1 |
| marine aquaculture; cage culture; offshore cage farming | 1 |
| shrimp farming; sustainable aquaculture; aquaculture | 1 |
| aquaculture; seabass farming; in pond raceway system; commercial fish culture | 1 |
| hatchery; seed production; crustacean farming; aquaculture | 1 |
| marine aquaculture; lobster farming; seed supply; nursery | 1 |
| shrimp farming; intensive aquaculture; intensive shrimp farming | 1 |
| shrimp farming; intensive shrimp farming; aquaculture production | 1 |
| shrimp farming; coastal aquaculture; sand-based shrimp farming | 1 |
| marine aquaculture; cage culture; lobster farming; coastal aquaculture | 1 |
| shrimp farming; intensive shrimp farming; aquaculture environmental management | 1 |
| shrimp farming; aquaculture; crustacean aquaculture | 1 |
| shrimp farming; aquaculture; pond aquaculture | 1 |
| shrimp farming; aquaculture | 1 |
| shrimp farming; aquaculture; disease transmission | 1 |
| aquaculture environmental management; coastal water management | 1 |
| cage culture; marine fish farming; aquaculture | 1 |

#### keywords

- S? gi? tr? r?ng: **0**
- Delimiter counts: ;: 139; ;,: 1
- Delimiter kh?ng nh?t qu?n: **True**

| value | count |
| --- | --- |
| shrimp culture; Penaeus vannamei; Penaeus monodon; bacterial disease; Vibrio parahaemolyticus; diagnosis; disease prevention; therapy; epidemiology; disease ... | 1 |
| Penaeus monodon; shrimp hatchery; hatchery productivity; health management; biosecurity; aquaculture; India | 1 |
| AHPND; acute hepatopancreatic necrosis disease; shrimp; aquaculture; disease prevention; disease surveillance; fishery management | 1 |
| aquaculture; pathogens; health hazards; risk analysis; risk management; biosecurity; surveillance systems; disease outbreaks; disease prevention; disease era... | 1 |
| Penaeus vannamei; biosecurity; shrimp fisheries; Latin America; Caribbean; hatchery; health management | 1 |
| aquaculture; shrimp disease; AHPND; EMS; Vibrio; disease prevention; disease surveillance; biosecurity; fishery management | 1 |
| sustainable fisheries; aquaculture development; fishery data; data collection; safety at work; occupational health; regional planning; CACFish | 1 |
| crustacean culture; water circulation; pond culture; disease control; good practices; Thailand; pathogens | 1 |
| animal diseases; animal health; aquaculture; aquatic animals; Asia; diagnosis; fish diseases | 1 |
| aquaculture; prawns and shrimps; Penaeus vannamei; viroses; aetiology; diagnosis; disease prevention; epidemiology; disease eradication; viral disease | 1 |
| artisanal fisheries; Asia; Bangladesh; fish culture; fisheries; health management; brackishwater species | 1 |
| crustacean culture; animal introduction; Penaeus stylirostris; biodiversity; viroses; fishery production; Penaeus monodon; fish diseases; trade; statistical ... | 1 |
| animal health; aquaculture; disease surveillance; risk assessment; animal diseases | 1 |
| lobster; trade analysis; exports; market trends; fisheries economics; Canada; China; international trade | 1 |
| lobsters; Decapoda; fisheries biology; habitats; identification; geographical distribution; nomenclature; species; taxonomy | 1 |
| aquaculture development; aquatic genetic resources; ex situ conservation; in vitro culture; gene banks; biosecurity; cryopreservation; protocols; seaweed | 1 |
| inland fisheries; fish farms; inland waters; water quality; chemicophysical properties; abiotic factors; biotic factors; meteorology; impact assessment; fish... | 1 |
| water quality; fish health; aquatic environment; toxicology; water pollution; disease risk; environmental stress; fish culture; fish diseases; health | 1 |
| aquaculture; risk analysis; risk factors; environmental impact; pathogens; invasive species; genetic impacts; food safety; sustainability; decision making; d... | 1 |
| aquaculture; risk analysis; biosecurity; disease transmission; pathogen risk; import risk analysis; risk assessment; risk management; risk communication; dis... | 1 |
| sustainable aquaculture; guidelines; communication; stakeholders; digital technology; food security; livelihoods; ecosystem restoration; climate resilience; ... | 1 |
| aquaculture; ecosystem approach; environmental management; sustainability; ecosystem integration; governance; management; policy; sustainable development | 1 |
| aquaculture; environmental impact assessment; monitoring; aquatic environment; sustainability; risk analysis; ecosystem management; environmental policy; imp... | 1 |
| aquaculture; environmental protection; coastal aquaculture; pollution; ecosystem impact; sustainability; environmental management; mitigation; environmental ... | 1 |
| aquaculture; environmental management; environmental impact assessment; EIA; training; sustainability; ecosystem management; policy implementation; environme... | 1 |
| aquaculture; environmental impact assessment; EIA; environmental monitoring; fishery production; food security; fisheries management; action plans; environme... | 1 |
| aquaculture; climate change adaptation; resilience; risk reduction; vulnerability assessment; adaptation strategies; climate resilience; cost-benefit analysi... | 1 |
| aquaculture; fisheries; climate change adaptation; resilience; case studies; mitigation strategies; coastal management; capacity building; climate change; ad... | 1 |
| aquaculture; fisheries; climate change; environmental factors; adaptation; mitigation; climate change adaptation; risk; sustainability; food security; enviro... | 1 |
| aquaculture production; sustainable development; economic development; guidelines; best practices; innovation adoption; knowledge sharing; policy implementation | 1 |

Gi? tr? k? l? / c?n ki?m tra:

| value | flags |
| --- | --- |
| tôm hùm; lobster; quy hoạch; Khánh Hòa; nuôi biển; marine aquaculture; phát triển ngành; định hướng 2030; nuôi trồng thủy sản; ven biển Khánh Hòa; Vịnh Văn P... | mixed_delimiters_in_value |

#### language

- S? gi? tr? r?ng: **0**
- Delimiter counts: [none]: 140
- Delimiter kh?ng nh?t qu?n: **False**
- Language groups: English: 99; Vietnamese: 41
- Language ngo?i expected: kh?ng c?

| value | count |
| --- | --- |
| English | 99 |
| Vietnamese | 41 |

#### docType

- S? gi? tr? r?ng: **0**
- Delimiter counts: [none]: 140
- Delimiter kh?ng nh?t qu?n: **False**

| value | count |
| --- | --- |
| Journal article | 63 |
| Technical study | 12 |
| Technical book | 9 |
| Proceedings paper | 9 |
| Technical report | 8 |
| Technical article | 6 |
| Manual / Guide | 2 |
| Meeting document | 2 |
| Brochure | 2 |
| Other document | 2 |
| Guideline | 2 |
| Magazine article | 2 |
| Textbook | 2 |
| Conference paper | 2 |
| Handbook | 1 |
| Policy brief | 1 |
| Technical brief | 1 |
| Flagship report | 1 |
| Workshop proceedings | 1 |
| Meeting report | 1 |
| Web article | 1 |
| Workshop presentation | 1 |
| News article | 1 |
| Technical workshop report | 1 |
| Factsheet | 1 |
| Planning report | 1 |
| Technical bulletin | 1 |
| Training/technical presentation | 1 |
| Technical guideline | 1 |
| Technical manual | 1 |

#### source

- S? gi? tr? r?ng: **0**
- Delimiter counts: [none]: 140
- Delimiter kh?ng nh?t qu?n: **False**

| value | count |
| --- | --- |
| FAO Open Knowledge Repository | 41 |
| SEAFDEC | 11 |
| Tạp chí Khoa học - Công nghệ Thủy sản | 10 |
| Tép Bạc | 7 |
| Scientific Reports | 6 |
| NACA | 3 |
| International Journal of Molecular Sciences (MDPI) | 3 |
| Biology (MDPI) | 3 |
| PLOS ONE | 3 |
| FAO | 3 |
| Microorganisms (MDPI) | 3 |
| Viện Nghiên cứu Nuôi trồng Thủy sản III | 3 |
| Tạp chí Khoa học Trường Đại học Cần Thơ | 3 |
| Pathogens (MDPI) | 2 |
| Aquaculture International | 2 |
| Veterinary World | 2 |
| PLOS Pathogens | 2 |
| Frontiers in Microbiology | 2 |
| Viruses (MDPI) | 2 |
| Tạp chí Khoa học và Công nghệ Biển | 2 |
| Nhà xuất bản Đại học Cần Thơ | 2 |
| Tạp chí Khoa học Nông nghiệp Việt Nam | 2 |
| Tổng cục Thủy sản | 1 |
| FAO / World Bank / Mississippi State University | 1 |
| BMC Microbiology | 1 |
| Microbiome (BMC) | 1 |
| Aquaculture Nutrition | 1 |
| Marine Drugs (MDPI) | 1 |
| Veterinary Medicine and Science | 1 |
| Environmental Science and Pollution Research | 1 |

### Alias/variant findings c?n c?n nh?c chu?n h?a

| column | alias_cluster | doc_count | doc_ids_sample |
| --- | --- | --- | --- |
| related_taxon | whiteleg shrimp / Penaeus vannamei / Litopenaeus vannamei / t?m th? | 61 | AAF_001; BIOLOGY_001; CTU_JOURNAL_001; CTU_JOURNAL_002; DLU_002; FAO_001; FAO_003; FAO_005; FAO_006; FAO_010; FAO_012; FAO_038; IJMS_001; NACA_002; PMC_003; ... |
| related_taxon | black tiger shrimp / Penaeus monodon / t?m s? | 19 | CTU_001; CTU_JOURNAL_001; FAO_001; FAO_002; FAO_003; FAO_006; PLOS_001; PMC_024; PMC_025; RIA3_003; SEAFDEC_004; SEAFDEC_005; SEAFDEC_006; SEAFDEC_008; TB_00... |
| related_taxon | lobster / t?m h?m | 13 | FAO_014; FAO_015; HUIB_001; KKTY_001; KNQG_002; NACA_003; RIA3_001; RIA3_002; RIA3_003; TCKHTS_002; TCKHTS_003; TCTS_002; VAP_001 |
| related_disease | AHPND / EMS | 32 | AAF_001; FAO_001; FAO_003; FAO_006; FAO_044; MDPI_001; NACA_003; PMC_006; PMC_007; PMC_008; PMC_009; PMC_010; PMC_011; PMC_012; PMC_026; PMC_028; PMC_029; PM... |
| related_disease | WSSV / white spot | 21 | BIOLOGY_001; DLU_002; IJMS_001; NACA_002; NACA_003; PLOS_001; PMC_023; PMC_024; PMC_025; PMC_035; SEAFDEC_002; SEAFDEC_003; SEAFDEC_005; SEAFDEC_009; TB_001;... |
| related_disease | EHP / Enterocytozoon | 15 | PMC_001; PMC_002; PMC_003; PMC_004; PMC_005; PMC_020; PMC_021; PMC_022; PMC_027; PMC_035; SEAFDEC_001; SEAFDEC_008; TB_005; TCKHTS_001; VJAS_001 |
| related_disease | HPM | 3 | PMC_001; SEAFDEC_001; SEAFDEC_008 |
| related_disease | Vibrio / vibriosis | 32 | AAF_001; FAO_006; HUIB_001; KKTY_001; MDPI_001; PMC_006; PMC_007; PMC_008; PMC_009; PMC_010; PMC_011; PMC_012; PMC_014; PMC_015; PMC_016; PMC_017; PMC_018; P... |
| related_location | Vietnam / Viet Nam / Vi?t Nam | 37 | AAF_001; CTU_001; CTU_002; CTU_JOURNAL_001; CTU_JOURNAL_002; CTU_JOURNAL_003; DLU_002; FAO_003; FAO_038; FAO_044; HUIB_001; JFST_001; KKTY_001; KNQG_001; KNQ... |
| related_location | Khanh Hoa / Kh?nh H?a | 17 | HUIB_001; JFST_001; KNQG_001; KNQG_002; RIA3_001; RIA3_002; RIA3_003; TCKHTS_002; TCKHTS_003; TCKHTS_006; TCKHTS_007; TCKHTS_008; TCKHTS_009; TCTS_002; VJMST... |
| related_location | Mekong Delta / ?BSCL | 2 | FAO_038; MDPI_001 |
| production_mode | intensive variants | 3 | CTU_JOURNAL_001; CTU_JOURNAL_002; VAWRE_001 |

### Docs c? nguy c? KG facts y?u

| doc_id | is_new_doc | title | related_taxon | related_disease | related_location | production_mode | risk_reason |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FAO_002 | NO | Improving Penaeus monodon hatchery practices. Manual based on experience in India. | Penaeus monodon; shrimp |  | India | hatchery aquaculture | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng |
| FAO_004 | NO | The Progressive Management Pathway for Aquaculture Biosecurity: Guidelines for application | aquatic animals; fish; shrimp |  | Global | aquaculture | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng; production_mode qu? chung |
| FAO_005 | NO | Health management and biosecurity maintenance in white shrimp (Penaeus vannamei) hatcheries in Latin America | Penaeus vannamei; shrimp |  | Latin America; Caribbean | hatchery aquaculture | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng |
| FAO_007 | NO | Report of the Ninth Session of the Central Asian and Caucasus Regional Fisheries and Aquaculture Commission, Almaty, Kazakhstan, 25–26 November 2025 | fish; aquatic species |  | Central Asia; Caucasus; Kazakhstan | inland fisheries; aquaculture | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng |
| FAO_008 | NO | Low water exchange shrimp farming: improvements in Thailand | shrimp; crustaceans |  | Thailand; Bangkok | shrimp aquaculture | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng |
| FAO_009 | NO | Asia diagnostic guide to aquatic animal diseases | aquatic animals; fish; crustaceans |  | Asia | inland fisheries; aquaculture | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng |
| FAO_011 | NO | Brackishwater Shrimp Culture Demonstration in Bangladesh - BOBP/REP/35 | shrimp |  | Bangladesh; Khulna; Satkhira | aquaculture | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng; production_mode qu? chung |
| FAO_012 | NO | Introductions and movement of Penaeus vannamei and Penaeus stylirostris in Asia and the Pacific | Penaeus vannamei; Penaeus stylirostris; shrimp |  | Asia; Pacific | shrimp aquaculture | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng |
| FAO_013 | NO | Surveillance and zoning for aquatic animal diseases | aquatic animals; fish |  | Global | inland fisheries; aquaculture | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng |
| FAO_015 | NO | FAO species catalogue. Vol.13. Marine lobsters of the world. An annotated and illustrated catalogue of marine lobsters known to date | lobster |  | Global | capture fisheries | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng |
| FAO_016 | NO | Aquaculture development. 13. Guidelines for ex situ in vitro gene banking of aquatic genetic resources | aquatic species; fish; shellfish |  | Global | aquaculture | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng; production_mode qu? chung |
| FAO_017 | NO | Survey and evaluation of water qualities. A field guide for managers of inland fisheries and fish farms | fish; aquatic animals |  | inland waters; Hungary; Global | inland fisheries; aquaculture | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng |
| FAO_018 | NO | Water quality and fish health | fish; aquatic animals |  | Europe | inland fisheries; aquaculture | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng |
| FAO_019 | NO | Understanding and applying risk analysis in aquaculture | aquatic species; fish; shrimp |  | Global | aquaculture | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng; production_mode qu? chung |
| FAO_020 | NO | Risk Analysis for Movements of Live Aquatic Animals. An introductory training course | aquatic animals; fish; shrimp |  | Global | aquaculture | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng; production_mode qu? chung |
| FAO_021 | NO | Guidelines for Sustainable Aquaculture: Communications handbook and toolkit | aquatic animals; fish; shrimp |  | Global | aquaculture | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng; production_mode qu? chung |
| FAO_022 | NO | Aquaculture development. 4. Ecosystem approach to aquaculture | aquatic animals; fish; shrimp |  | Global | aquaculture | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng; production_mode qu? chung |
| FAO_023 | NO | Environmental impact assessment and monitoring in aquaculture. Requirements, practices, effectiveness and improvements | fish |  | Global | aquaculture | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng; production_mode qu? chung |
| FAO_024 | NO | Reducing environmental impacts of coastal aquaculture |  |  | coastal areas; marine environment | aquaculture | thi?u related_taxon; thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng; production_mode qu? chung |
| FAO_025 | NO | Environmental management and environmental impact assessment in aquaculture: Training Workshop for aquaculture managers. Entebbe, Uganda | fish |  | Uganda; Africa | aquaculture | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng; production_mode qu? chung |
| FAO_026 | NO | Aquaculture Environmental Impact Assessment | fish |  | Indian Ocean; Southern Africa | aquaculture | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng; production_mode qu? chung |
| FAO_027 | NO | Aquaculture Adaptation Framework for Climate Change (Aqua-Adapt) | aquatic species; fish; shellfish |  | Global | aquaculture | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng; production_mode qu? chung |
| FAO_028 | NO | Climate Change Adaptation in Fisheries and Aquaculture. Compilation of initial examples | aquatic species; fish |  | Global | aquaculture; fisheries | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng |
| FAO_029 | NO | Impacts of climate change on fisheries and aquaculture. Synthesis of current knowledge, adaptation and mitigation options | aquatic species; fish |  | Global | aquaculture; fisheries | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng |
| FAO_031 | NO | Translating the Guidelines for Sustainable Aquaculture into action. Policy brief | aquatic animals; fish; shrimp |  | Global | aquaculture | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng; production_mode qu? chung |
| FAO_032 | NO | Future pathways for aquaculture and fisheries development in Azerbaijan | aquatic species; fish |  | Azerbaijan | fisheries; aquaculture | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng |
| FAO_033 | NO | FAO Reference Centres for Antimicrobial Resistance and Aquaculture Biosecurity. Combating AMR together: ensuring healthy and safe aquatic foods | aquatic species; fish; shrimp |  | Global | aquaculture | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng; production_mode qu? chung |
| FAO_035 | NO | Health management in Asian aquaculture | aquatic animals; fish; shrimp |  | Asia; Pacific | aquaculture | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng; production_mode qu? chung |
| FAO_036 | NO | Strengthening aquaculture health management in Bosnia and Herzegovina | aquatic animals; fish |  | Bosnia and Herzegovina | aquaculture | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng; production_mode qu? chung |
| FAO_037 | NO | Preventing and managing aquatic animal disease risks in aquaculture through a progressive management pathway | aquatic animals; fish; shrimp |  | Global | aquaculture | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng; production_mode qu? chung |
| FAO_038 | NO | Risk management practices of small intensive shrimp farmers in the Mekong Delta of Viet Nam | shrimp; Penaeus vannamei |  | Vietnam; Mekong Delta; Bac Lieu; Ben Tre; Ca Mau | shrimp aquaculture | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng |
| FAO_039 | NO | Promotion of Small-scale Shrimp and Prawn Hatcheries in India and Bangladesh - BOBP/REP/66 | shrimp; prawns |  | India; Bangladesh | hatchery aquaculture | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng |
| FAO_040 | NO | An assessment of impacts from shrimp aquaculture in Bangladesh and prospects for improvement | shrimp; prawns |  | Bangladesh | coastal aquaculture | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng |
| FAO_041 | NO | Guidelines for Sustainable Aquaculture | aquatic species |  | Global | aquaculture | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng; production_mode qu? chung |
| FAO_042_i3720e | NO | The State of World Fisheries and Aquaculture 2024 – Blue Transformation in action | fish; aquatic species |  | Global | fisheries; aquaculture | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng |
| NACA_001 | NO | Status, technological innovations, and industry development needs of mud crab (Scylla spp.) aquaculture | mud crab; Scylla spp. |  | Singapore; Global | aquaculture | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng; production_mode qu? chung |
| FAO_042_biosecurity_philippines | NO | Biosecurity in Aquaculture: Philippines | shrimp |  | Philippines | shrimp aquaculture | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng |
| FAO_043 | NO | Boosting biosecurity in Peru’s shrimp farming industry for sustainable livelihoods | shrimp |  | Peru | shrimp aquaculture | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng |
| RIA3_001 | NO | Quy hoạch nuôi tôm hùm đến năm 2020 và định hướng đến 2030 | tôm hùm; lobster |  | Khánh Hòa; Việt Nam; ven biển Khánh Hòa; Vịnh Văn Phong; Vạn Ninh; Xuân Tự; Cam Ranh; Vịnh Cam Ranh | marine aquaculture | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng |
| VJMST_001 | YES | Hiện trạng nuôi trồng và khai thác thủy sản tại đầm Thủy Triều huyện Cam Lâm, tỉnh Khánh Hòa | thủy sản; aquatic animals |  | đầm Thủy Triều; Cam Lâm; Khánh Hòa; Việt Nam | aquaculture; capture fisheries; coastal lagoon aquaculture | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng |
| KNQG_001 | YES | Phát triển nuôi cá lồng bè trên biển bền vững, thích ứng biến đổi khí hậu | cá biển; cá bớp; marine fish |  | Khánh Hòa; Việt Nam; Nam Trung Bộ | marine aquaculture; cage culture; offshore cage farming | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng |
| YERSIN_001 | YES | Đánh giá tính bền vững nghề nuôi tôm tại huyện Ninh Hòa - tỉnh Khánh Hòa | tôm; shrimp |  | Ninh Hòa; Khánh Hòa; Việt Nam | shrimp farming; sustainable aquaculture; aquaculture | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng |
| JFST_001 | YES | Nuôi cá chẽm (Lates calcarifer, Bloch, 1790) thương phẩm trong hệ thống “sông trong ao” tại Khánh Hòa | cá chẽm; seabass; Lates calcarifer |  | Khánh Hòa; Việt Nam | aquaculture; seabass farming; in pond raceway system; commercial fish culture | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng |
| CTU_001 | YES | Kỹ thuật sản xuất giống và nuôi giáp xác | tôm biển; tôm sú; tôm càng xanh; cua biển; crustaceans |  | Việt Nam | hatchery; seed production; crustacean farming; aquaculture | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng |
| TCKHTS_003 | YES | Tình hình cung cấp con giống tôm hùm bông (Panulirus ornatus) ở Việt Nam: hiện trạng và trở ngại | tôm hùm bông; Panulirus ornatus; puerulus; lobster seed |  | Việt Nam; Khánh Hòa; Nha Trang; Ninh Hòa; Cam Ranh; Phú Yên; Bình Định | marine aquaculture; lobster farming; seed supply; nursery | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng |
| CTU_JOURNAL_001 | YES | Phân tích hiệu quả sản xuất các mô hình nuôi tôm thẻ chân trắng và tôm sú thâm canh ở tỉnh Ninh Thuận | tôm thẻ chân trắng; white-leg shrimp; tôm sú; black tiger shrimp |  | Ninh Thuận; Việt Nam | shrimp farming; intensive aquaculture; intensive shrimp farming | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng |
| CTU_JOURNAL_002 | YES | Phân tích hiệu quả kỹ thuật và tài chính của mô hình nuôi tôm thẻ chân trắng ở tỉnh Cà Mau | tôm thẻ chân trắng; Penaeus vannamei; white-leg shrimp |  | Cà Mau; Việt Nam | shrimp farming; intensive shrimp farming; aquaculture production | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng |
| VAP_001 | YES | Ô nhiễm môi trường trầm tích vùng nuôi và rủi ro đối với hoạt động nuôi lồng bè ven biển Nam Trung Bộ | tôm hùm; marine aquaculture species |  | Nam Trung Bộ; Việt Nam; vùng ven biển Nam Trung Bộ | marine aquaculture; cage culture; lobster farming; coastal aquaculture | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng |
| VAWRE_001 | YES | Nghiên cứu biến động và giải pháp kiểm soát chất lượng môi trường vùng nuôi tôm tập trung tại Quảng Ninh | tôm; shrimp |  | Quảng Ninh; Việt Nam | shrimp farming; intensive shrimp farming; aquaculture environmental management | thi?u related_disease |
| VJMST_003 | YES | Đánh giá sức tải môi trường vực nước Thủy Triều - Cam Ranh | thủy sản; aquatic animals |  | Thủy Triều; Cam Ranh; Khánh Hòa; Việt Nam | aquaculture environmental management; coastal water management | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng |
| CTU_002 | YES | Kỹ thuật sản xuất giống và nuôi cá biển | cá biển; marine fish |  | Việt Nam | marine aquaculture; hatchery; seed production; marine fish farming | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng |

## Kh? n?ng ??a v?o vector store

| doc_id | file_path | extension | size_bytes | estimated_chars | note |
| --- | --- | --- | --- | --- | --- |
| FAO_001 | data/raw_docs/FAO_001_cb2119en.pdf | .pdf | 2837382 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| FAO_002 | data/raw_docs/FAO_002_a1152e.pdf | .pdf | 3581648 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| FAO_003 | data/raw_docs/FAO_003_ca2976en.pdf | .pdf | 6691426 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| FAO_004 | data/raw_docs/FAO_004_cc6858en.pdf | .pdf | 34677269 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| FAO_005 | data/raw_docs/FAO_005_y5040e.pdf | .pdf | 392844 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| FAO_006 | data/raw_docs/FAO_006_bt131e.pdf | .pdf | 2438802 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| FAO_007 | data/raw_docs/FAO_007_cd8164en.pdf | .pdf | 1235572 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| FAO_008 | data/raw_docs/FAO_008_cb8926en.pdf | .pdf | 3368163 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| FAO_009 | data/raw_docs/FAO_009_y1679e.pdf | .pdf | 3475127 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| FAO_010 | data/raw_docs/FAO_010_ca6052en.pdf | .pdf | 2857806 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| FAO_011 | data/raw_docs/FAO_011_ad824e.pdf | .pdf | 238076 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| FAO_012 | data/raw_docs/FAO_012_ad505e.pdf | .pdf | 672185 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| FAO_013 | data/raw_docs/FAO_013_y5325e.pdf | .pdf | 538879 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| FAO_014 | data/raw_docs/FAO_014_cd8658en.pdf | .pdf | 409149 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| FAO_015 | data/raw_docs/FAO_015_t0411e.pdf | .pdf | 534703 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| FAO_016 | data/raw_docs/FAO_016_cd7559en.pdf | .pdf | 2637352 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| FAO_017 | data/raw_docs/FAO_017_ca7588en.pdf | .pdf | 34994958 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| FAO_018 | data/raw_docs/FAO_018_t1623e.pdf | .pdf | 870732 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| FAO_019 | data/raw_docs/FAO_019_i0490e.pdf | .pdf | 4521107 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| FAO_020 | data/raw_docs/FAO_020_i2571e.pdf | .pdf | 4048265 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| FAO_021 | data/raw_docs/FAO_021_cd8667en.pdf | .pdf | 1976309 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| FAO_022 | data/raw_docs/FAO_022_i1750e.pdf | .pdf | 1804971 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| FAO_023 | data/raw_docs/FAO_023_i0970e.pdf | .pdf | 7120652 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| FAO_024 | data/raw_docs/FAO_024_u3100e.pdf | .pdf | 335212 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| FAO_025 | data/raw_docs/FAO_025_a0366e.pdf | .pdf | 1078825 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| FAO_026 | data/raw_docs/FAO_026_br813e.pdf | .pdf | 366409 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| FAO_027 | data/raw_docs/FAO_027_cd6476en.pdf | .pdf | 1950755 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| FAO_028 | data/raw_docs/FAO_028_i3569e.pdf | .pdf | 2583818 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| FAO_029 | data/raw_docs/FAO_029_i9705en.pdf | .pdf | 16659485 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| FAO_031 | data/raw_docs/FAO_031_cd8563en.pdf | .pdf | 9202961 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| FAO_032 | data/raw_docs/FAO_032_cd8633en.pdf | .pdf | 430307 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| FAO_033 | data/raw_docs/FAO_033_cc6625en.pdf | .pdf | 5923373 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| FAO_034 | data/raw_docs/FAO_034_ca2705en.pdf | .pdf | 555647 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| FAO_035 | data/raw_docs/FAO_035_w3594e.pdf | .pdf | 526773 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| FAO_036 | data/raw_docs/FAO_036_i1137e.pdf | .pdf | 1713567 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| FAO_037 | data/raw_docs/FAO_037_na265en.pdf | .pdf | 683985 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| FAO_038 | data/raw_docs/FAO_038_ca6702en.pdf | .pdf | 861870 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| FAO_039 | data/raw_docs/FAO_039_ad893e.pdf | .pdf | 633135 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| FAO_040 | data/raw_docs/FAO_040_i8064en.pdf | .pdf | 3778749 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| FAO_041 | data/raw_docs/FAO_041_cd3785en.pdf | .pdf | 2206169 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| FAO_042_i3720e | data/raw_docs/FAO_042_i3720e.pdf | .pdf | 8839521 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| NACA_001 | data/raw_docs/NACA_001_1737869839.pdf | .pdf | 56312263 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| NACA_002 | data/raw_docs/NACA_002_1749824700.pdf | .pdf | 1162852 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| NACA_003 | data/raw_docs/NACA_003_1494554353.pdf | .pdf | 2425728 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| TCTS_001 | data/raw_docs/TCTS_001_024286.pdf | .pdf | 710724 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| IJMS_001 | data/raw_docs/IJMS_001_ijms26178478.pdf | .pdf | 4165432 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| BIOLOGY_001 | data/raw_docs/BIOLOGY_001_biology13100758.pdf | .pdf | 3656901 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| PLOS_001 | data/raw_docs/PLOS_001_pone.0091930.pdf | .pdf | 1783090 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| SEAFDEC_001 | data/raw_docs/SEAFDEC_001_DharAK2021.pdf | .pdf | 1734398 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| SEAFDEC_002 | data/raw_docs/SEAFDEC_002_Wong2016.pdf | .pdf | 230067 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| SEAFDEC_003 | data/raw_docs/SEAFDEC_003_Yuasa2016.pdf | .pdf | 252706 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| SEAFDEC_004 | data/raw_docs/SEAFDEC_004_sp15-3.pdf | .pdf | 449077 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| SEAFDEC_005 | data/raw_docs/SEAFDEC_005_WahSLP2016.pdf | .pdf | 235457 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| SEAFDEC_006 | data/raw_docs/SEAFDEC_006_Apostol2016.pdf | .pdf | 435532 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| SEAFDEC_007 | data/raw_docs/SEAFDEC_007_Penir2019.pdf | .pdf | 113485 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| SEAFDEC_008 | data/raw_docs/SEAFDEC_008_Putth2016.pdf | .pdf | 584977 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| SEAFDEC_009 | data/raw_docs/SEAFDEC_009_Hastuti2016.pdf | .pdf | 264524 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| SEAFDEC_010 | data/raw_docs/SEAFDEC_010_Hirono2016.pdf | .pdf | 401561 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| SEAFDEC_011 | data/raw_docs/SEAFDEC_011_Kua2016.pdf | .pdf | 335696 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| FAO_042_biosecurity_philippines | data/raw_docs/FAO_042_biosecurity_philippines.pdf | .pdf | 4655063 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| FAO_043 | data/raw_docs/FAO_043_boosting_biosecurity_peru.pdf | .pdf | 614195 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| TCKHTS_001 | data/raw_docs/TCKHTS_001.pdf | .pdf | 910982 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| FAO_044 | data/raw_docs/FAO_044_i2734e03i.pdf | .pdf | 4882582 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| FAO_045 | data/raw_docs/FAO_045_ca6163en.pdf | .pdf | 520499 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| PMC_001 | data/raw_docs/PMC_001_PMC10820212.pdf | .pdf | 825771 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| PMC_002 | data/raw_docs/PMC_002_PMC6963587.pdf | .pdf | 198189 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| PMC_003 | data/raw_docs/PMC_003_PMC11657822.pdf | .pdf | 3666087 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| PMC_004 | data/raw_docs/PMC_004_PMC12128546.pdf | .pdf | 3692281 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| PMC_005 | data/raw_docs/PMC_005_PMC12552485.pdf | .pdf | 2695289 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| PMC_006 | data/raw_docs/PMC_006_PMC8042889.pdf | .pdf | 2332238 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| PMC_007 | data/raw_docs/PMC_007_PMC8067269.pdf | .pdf | 2962901 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| PMC_008 | data/raw_docs/PMC_008_PMC11611405.pdf | .pdf | 3250959 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| PMC_009 | data/raw_docs/PMC_009_PMC12030750.pdf | .pdf | 2350238 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| PMC_010 | data/raw_docs/PMC_010_PMC7409025.pdf | .pdf | 1592624 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| PMC_011 | data/raw_docs/PMC_011_PMC5742833.pdf | .pdf | 4873671 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| PMC_012 | data/raw_docs/PMC_012_PMC7223513.pdf | .pdf | 518367 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| PMC_013 | data/raw_docs/PMC_013_PMC12825151.pdf | .pdf | 1384168 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| PMC_014 | data/raw_docs/PMC_014_PMC9531857.pdf | .pdf | 1479014 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| PMC_015 | data/raw_docs/PMC_015_PMC12006376.pdf | .pdf | 2713899 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| PMC_016 | data/raw_docs/PMC_016_PMC4815145.pdf | .pdf | 1733261 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| PMC_017 | data/raw_docs/PMC_017_PMC11223889.pdf | .pdf | 4207087 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| PMC_018 | data/raw_docs/PMC_018_PMC12008197.pdf | .pdf | 3776158 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| PMC_019 | data/raw_docs/PMC_019_PMC6797625.pdf | .pdf | 1688443 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| PMC_020 | data/raw_docs/PMC_020_PMC10701378.pdf | .pdf | 5632033 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| PMC_021 | data/raw_docs/PMC_021_PMC9427843.pdf | .pdf | 7470050 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| PMC_022 | data/raw_docs/PMC_022_PMC11081493.pdf | .pdf | 2595651 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| PMC_023 | data/raw_docs/PMC_023_PMC10229113.pdf | .pdf | 1442350 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| PMC_024 | data/raw_docs/PMC_024_PMC9139878.pdf | .pdf | 1883191 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| PMC_025 | data/raw_docs/PMC_025_PMC4510448.pdf | .pdf | 227195 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| PMC_026 | data/raw_docs/PMC_026_PMC11205452.pdf | .pdf | 3812393 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| PMC_027 | data/raw_docs/PMC_027_PMC12745081.pdf | .pdf | 1780141 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| PMC_028 | data/raw_docs/PMC_028_PMC5603525.pdf | .pdf | 4179909 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| PMC_029 | data/raw_docs/PMC_029_PMC6955853.pdf | .pdf | 17528305 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| PMC_030 | data/raw_docs/PMC_030_PMC10476614.pdf | .pdf | 2727978 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| PMC_031 | data/raw_docs/PMC_031_PMC91383.pdf | .pdf | 129405 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| PMC_032 | data/raw_docs/PMC_032_PMC12435696.pdf | .pdf | 2374633 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| PMC_033 | data/raw_docs/PMC_033_PMC8339124.pdf | .pdf | 3148392 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| PMC_034 | data/raw_docs/PMC_034_PMC10141217.pdf | .pdf | 22251326 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| PMC_035 | data/raw_docs/PMC_035_PMC11861540.pdf | .pdf | 12708855 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| PMC_036 | data/raw_docs/PMC_036_PMC9125206.pdf | .pdf | 5285910 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| RIA3_001 | data/raw_docs/RIA3_001_quy_hoach_nuoi_tom_hum_2030.pdf | .pdf | 2533358 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| RIA3_002 | data/raw_docs/RIA3_002_TBKQ_QTDX_PhuYen_KhanhHoa_17112023.pdf | .pdf | 1670425 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| RIA3_003 | data/raw_docs/RIA3_003_TBKQ_QTMT_DOT14_T6_2025.pdf | .pdf | 1843283 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| TB_001 | data/raw_docs/TB_001_NyanTawCRSDCaMau.pdf | .pdf | 8173752 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| TB_002 | data/raw_docs/TB_002_cong_nghe_gen_va_chon_giong_tom_khang_benh.pdf | .pdf | 311117 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| TB_003 | data/raw_docs/TB_003_co_che_co_ban_cua_nhiem_don_le_va_dong_nhiem_DIV1_va_WSSV_o_tom_the_chan_trang.pdf | .pdf | 431191 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| TB_004 | data/raw_docs/TB_004_hoai_tu_co_o_tom_the_chan_trang.pdf | .pdf | 227871 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| TB_005 | data/raw_docs/TB_005_su_hien_dien_cua_benh_dom_trang_va_EHP_va_AHPND_tai_DBSCL_2022_2024.pdf | .pdf | 233937 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| TB_006 | data/raw_docs/TB_006_hoai_tu_co_IMNV_tren_tom_va_chien_luoc_kiem_soat.pdf | .pdf | 969292 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| TB_007 | data/raw_docs/TB_007_benh_dom_trang_o_tom_nuoi_va_cong_nghe_nuoi_tom_nham_phong_benh_dom_trang.pdf | .pdf | 6218939 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| VJMST_001 | data/raw_docs/VJMST_001_hien_trang_ntts_dam_thuy_trieu_cam_lam.pdf | .pdf |  |  | missing |
| KNQG_001 | data/raw_docs/KNQG_001_phat_trien_nuoi_ca_long_be_tren_bien.pdf | .pdf | 3304923 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| YERSIN_001 | data/raw_docs/YERSIN_001_ben_vung_nghe_nuoi_tom_ninh_hoa.pdf | .pdf | 534715 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| JFST_001 | data/raw_docs/JFST_001_nuoi_ca_chem_song_trong_ao_khanh_hoa.pdf | .pdf | 1279500 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| CTU_001 | data/raw_docs/CTU_001_ky_thuat_san_xuat_giong_va_nuoi_giap_xac.pdf | .pdf | 7052189 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| TCKHTS_002 | data/raw_docs/TCKHTS_002_phong_tri_benh_sua_do_than_tom_hum_nam_trung_bo.pdf | .pdf |  |  | missing |
| TCTS_002 | data/raw_docs/TCTS_002_quy_trinh_kiem_soat_rlb_benh_sua_tom_hum.pdf | .pdf | 1049405 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| HUIB_001 | data/raw_docs/HUIB_001_vibrio_biofilm_khang_khang_sinh_tom_hum.pdf | .pdf | 589145 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| KKTY_001 | data/raw_docs/KKTY_001_vibrio_khang_sinh_tom_hum_bong_phu_yen.pdf | .pdf | 706171 |  | c?n parser ph? h?p; PDF scan c? th? c?n OCR |
| TCKHTS_003 | data/raw_docs/TCKHTS_003_cung_cap_con_giong_tom_hum_bong_viet_nam.pdf | .pdf |  |  | missing |

Script li?n quan ch? ???c nh?n di?n t?n, kh?ng ch?y: `vector_search.py`, `hybrid_search.py`, `run_core_baselines.py`, `measure_core_baseline_latency.py`, `sync_metadata_to_owl.py`, `verify_kg_runtime.py`.

## ?nh h??ng ??n evaluation

- Metadata hi?n t?i c? 140 docs, l?n h?n snapshot c? 110 n?n evaluation c? kh?ng c?n l? final snapshot cho corpus hi?n t?i.
- N?u doc m?i xu?t hi?n trong Top-k, relevance judgments c? th? c?n c?p nh?t.

## Problems to fix before rebuild

| severity | doc_id | column | file_path | issue | suggestion |
| --- | --- | --- | --- | --- | --- |
| CRITICAL | MDPI_001 | file_path | data/raw_docs/MDPI_001_vibrio_ahpnd_mekong_delta.pdf | Raw file kh?ng t?n t?i tr?n disk | Ki?m tra t?n file/path ho?c b? sung file raw |
| CRITICAL | TCKHTS_002 | file_path | data/raw_docs/TCKHTS_002_phong_tri_benh_sua_do_than_tom_hum_nam_trung_bo.pdf | Raw file kh?ng t?n t?i tr?n disk | Ki?m tra t?n file/path ho?c b? sung file raw |
| CRITICAL | TCKHTS_003 | file_path | data/raw_docs/TCKHTS_003_cung_cap_con_giong_tom_hum_bong_viet_nam.pdf | Raw file kh?ng t?n t?i tr?n disk | Ki?m tra t?n file/path ho?c b? sung file raw |
| CRITICAL | TNU_JST_001 | file_path | data/raw_docs/TNU_JST_001_doc_luc_vibrio_tom_the_chan_trang.pdf | Raw file kh?ng t?n t?i tr?n disk | Ki?m tra t?n file/path ho?c b? sung file raw |
| CRITICAL | VJAS_001 | file_path | data/raw_docs/VJAS_001_ehp_tom_the_quang_ninh_nam_dinh.pdf | Raw file kh?ng t?n t?i tr?n disk | Ki?m tra t?n file/path ho?c b? sung file raw |
| CRITICAL | VJMST_001 | file_path | data/raw_docs/VJMST_001_hien_trang_ntts_dam_thuy_trieu_cam_lam.pdf | Raw file kh?ng t?n t?i tr?n disk | Ki?m tra t?n file/path ho?c b? sung file raw |
| WARNING |  | keywords |  | Delimiter kh?ng nh?t qu?n trong c?t | Ch?n delimiter chu?n cho multi-value fields |
| WARNING |  | keywords |  | Gi? tr? k? l?: mixed_delimiters_in_value | Ki?m tra v? chu?n h?a n?u c?n |
| WARNING | CTU_001 | KG facts | data/raw_docs/CTU_001_ky_thuat_san_xuat_giong_va_nuoi_giap_xac.pdf | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng | B? sung/chu?n h?a entity fields n?u doc thu?c final corpus |
| WARNING | CTU_002 | KG facts | data/raw_docs/CTU_002_ky_thuat_san_xuat_giong_va_nuoi_ca_bien.pdf | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng | B? sung/chu?n h?a entity fields n?u doc thu?c final corpus |
| WARNING | CTU_JOURNAL_001 | KG facts | data/raw_docs/CTU_JOURNAL_001_hieu_qua_mo_hinh_nuoi_tom_ninh_thuan.pdf | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng | B? sung/chu?n h?a entity fields n?u doc thu?c final corpus |
| WARNING | CTU_JOURNAL_002 | KG facts | data/raw_docs/CTU_JOURNAL_002_hieu_qua_ky_thuat_tai_chinh_tom_the_ca_mau.pdf | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng | B? sung/chu?n h?a entity fields n?u doc thu?c final corpus |
| WARNING | JFST_001 | KG facts | data/raw_docs/JFST_001_nuoi_ca_chem_song_trong_ao_khanh_hoa.pdf | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng | B? sung/chu?n h?a entity fields n?u doc thu?c final corpus |
| WARNING | KNQG_001 | KG facts | data/raw_docs/KNQG_001_phat_trien_nuoi_ca_long_be_tren_bien.pdf | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng | B? sung/chu?n h?a entity fields n?u doc thu?c final corpus |
| WARNING | TCKHTS_003 | KG facts | data/raw_docs/TCKHTS_003_cung_cap_con_giong_tom_hum_bong_viet_nam.pdf | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng | B? sung/chu?n h?a entity fields n?u doc thu?c final corpus |
| WARNING | VAP_001 | KG facts | data/raw_docs/VAP_001_o_nhiem_tram_tich_vung_nuoi_long_be_nam_trung_bo.pdf | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng | B? sung/chu?n h?a entity fields n?u doc thu?c final corpus |
| WARNING | VAWRE_001 | KG facts | data/raw_docs/VAWRE_001_chat_luong_moi_truong_vung_nuoi_tom_quang_ninh.pdf | thi?u related_disease | B? sung/chu?n h?a entity fields n?u doc thu?c final corpus |
| WARNING | VJMST_001 | KG facts | data/raw_docs/VJMST_001_hien_trang_ntts_dam_thuy_trieu_cam_lam.pdf | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng | B? sung/chu?n h?a entity fields n?u doc thu?c final corpus |
| WARNING | VJMST_003 | KG facts | data/raw_docs/VJMST_003_suc_tai_moi_truong_thuy_trieu_cam_ranh.pdf | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng | B? sung/chu?n h?a entity fields n?u doc thu?c final corpus |
| WARNING | YERSIN_001 | KG facts | data/raw_docs/YERSIN_001_ben_vung_nghe_nuoi_tom_ninh_hoa.pdf | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng | B? sung/chu?n h?a entity fields n?u doc thu?c final corpus |
| INFO |  | raw_docs | MDPI_001_vibrio_ahpnd_mekong_delta.pdf.pdf | Raw file kh?ng ???c khai b?o trong metadata | N?u l? corpus final th? th?m metadata; n?u kh?ng th? x?c nh?n lo?i kh?i final corpus |
| INFO |  | raw_docs | TCKHTS_002_phong_tri_benh_sua_do_than_tom_hum_nam_trung_bo.pdf.pdf | Raw file kh?ng ???c khai b?o trong metadata | N?u l? corpus final th? th?m metadata; n?u kh?ng th? x?c nh?n lo?i kh?i final corpus |
| INFO |  | raw_docs | TCKHTS_003_cung_cap_con_giong_tom_hum_bong_viet_nam.pdf.pdf | Raw file kh?ng ???c khai b?o trong metadata | N?u l? corpus final th? th?m metadata; n?u kh?ng th? x?c nh?n lo?i kh?i final corpus |
| INFO |  | raw_docs | TNU_JST_001_doc_luc_vibrio_tom_the_chan_trang.pdf.pdf | Raw file kh?ng ???c khai b?o trong metadata | N?u l? corpus final th? th?m metadata; n?u kh?ng th? x?c nh?n lo?i kh?i final corpus |
| INFO |  | raw_docs | VJAS_001_ehp_tom_the_quang_ninh_nam_dinh.pdf.pdf | Raw file kh?ng ???c khai b?o trong metadata | N?u l? corpus final th? th?m metadata; n?u kh?ng th? x?c nh?n lo?i kh?i final corpus |
| INFO |  | raw_docs | VJMST_001_hien_trang_ntts_dam_thuy_trieu_cam_lam.pdf.pdf | Raw file kh?ng ???c khai b?o trong metadata | N?u l? corpus final th? th?m metadata; n?u kh?ng th? x?c nh?n lo?i kh?i final corpus |
| INFO | FAO_002 | KG facts | data/raw_docs/FAO_002_a1152e.pdf | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng | B? sung/chu?n h?a entity fields n?u doc thu?c final corpus |
| INFO | FAO_004 | KG facts | data/raw_docs/FAO_004_cc6858en.pdf | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng; production_mode qu? chung | B? sung/chu?n h?a entity fields n?u doc thu?c final corpus |
| INFO | FAO_005 | KG facts | data/raw_docs/FAO_005_y5040e.pdf | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng | B? sung/chu?n h?a entity fields n?u doc thu?c final corpus |
| INFO | FAO_007 | KG facts | data/raw_docs/FAO_007_cd8164en.pdf | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng | B? sung/chu?n h?a entity fields n?u doc thu?c final corpus |
| INFO | FAO_008 | KG facts | data/raw_docs/FAO_008_cb8926en.pdf | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng | B? sung/chu?n h?a entity fields n?u doc thu?c final corpus |
| INFO | FAO_009 | KG facts | data/raw_docs/FAO_009_y1679e.pdf | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng | B? sung/chu?n h?a entity fields n?u doc thu?c final corpus |
| INFO | FAO_011 | KG facts | data/raw_docs/FAO_011_ad824e.pdf | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng; production_mode qu? chung | B? sung/chu?n h?a entity fields n?u doc thu?c final corpus |
| INFO | FAO_012 | KG facts | data/raw_docs/FAO_012_ad505e.pdf | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng | B? sung/chu?n h?a entity fields n?u doc thu?c final corpus |
| INFO | FAO_013 | KG facts | data/raw_docs/FAO_013_y5325e.pdf | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng | B? sung/chu?n h?a entity fields n?u doc thu?c final corpus |
| INFO | FAO_015 | KG facts | data/raw_docs/FAO_015_t0411e.pdf | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng | B? sung/chu?n h?a entity fields n?u doc thu?c final corpus |
| INFO | FAO_016 | KG facts | data/raw_docs/FAO_016_cd7559en.pdf | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng; production_mode qu? chung | B? sung/chu?n h?a entity fields n?u doc thu?c final corpus |
| INFO | FAO_017 | KG facts | data/raw_docs/FAO_017_ca7588en.pdf | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng | B? sung/chu?n h?a entity fields n?u doc thu?c final corpus |
| INFO | FAO_018 | KG facts | data/raw_docs/FAO_018_t1623e.pdf | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng | B? sung/chu?n h?a entity fields n?u doc thu?c final corpus |
| INFO | FAO_019 | KG facts | data/raw_docs/FAO_019_i0490e.pdf | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng; production_mode qu? chung | B? sung/chu?n h?a entity fields n?u doc thu?c final corpus |
| INFO | FAO_020 | KG facts | data/raw_docs/FAO_020_i2571e.pdf | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng; production_mode qu? chung | B? sung/chu?n h?a entity fields n?u doc thu?c final corpus |
| INFO | FAO_021 | KG facts | data/raw_docs/FAO_021_cd8667en.pdf | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng; production_mode qu? chung | B? sung/chu?n h?a entity fields n?u doc thu?c final corpus |
| INFO | FAO_022 | KG facts | data/raw_docs/FAO_022_i1750e.pdf | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng; production_mode qu? chung | B? sung/chu?n h?a entity fields n?u doc thu?c final corpus |
| INFO | FAO_023 | KG facts | data/raw_docs/FAO_023_i0970e.pdf | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng; production_mode qu? chung | B? sung/chu?n h?a entity fields n?u doc thu?c final corpus |
| INFO | FAO_024 | KG facts | data/raw_docs/FAO_024_u3100e.pdf | thi?u related_taxon; thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng; production_mode qu? chung | B? sung/chu?n h?a entity fields n?u doc thu?c final corpus |
| INFO | FAO_025 | KG facts | data/raw_docs/FAO_025_a0366e.pdf | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng; production_mode qu? chung | B? sung/chu?n h?a entity fields n?u doc thu?c final corpus |
| INFO | FAO_026 | KG facts | data/raw_docs/FAO_026_br813e.pdf | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng; production_mode qu? chung | B? sung/chu?n h?a entity fields n?u doc thu?c final corpus |
| INFO | FAO_027 | KG facts | data/raw_docs/FAO_027_cd6476en.pdf | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng; production_mode qu? chung | B? sung/chu?n h?a entity fields n?u doc thu?c final corpus |
| INFO | FAO_028 | KG facts | data/raw_docs/FAO_028_i3569e.pdf | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng | B? sung/chu?n h?a entity fields n?u doc thu?c final corpus |
| INFO | FAO_029 | KG facts | data/raw_docs/FAO_029_i9705en.pdf | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng | B? sung/chu?n h?a entity fields n?u doc thu?c final corpus |
| INFO | FAO_031 | KG facts | data/raw_docs/FAO_031_cd8563en.pdf | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng; production_mode qu? chung | B? sung/chu?n h?a entity fields n?u doc thu?c final corpus |
| INFO | FAO_032 | KG facts | data/raw_docs/FAO_032_cd8633en.pdf | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng | B? sung/chu?n h?a entity fields n?u doc thu?c final corpus |
| INFO | FAO_033 | KG facts | data/raw_docs/FAO_033_cc6625en.pdf | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng; production_mode qu? chung | B? sung/chu?n h?a entity fields n?u doc thu?c final corpus |
| INFO | FAO_035 | KG facts | data/raw_docs/FAO_035_w3594e.pdf | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng; production_mode qu? chung | B? sung/chu?n h?a entity fields n?u doc thu?c final corpus |
| INFO | FAO_036 | KG facts | data/raw_docs/FAO_036_i1137e.pdf | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng; production_mode qu? chung | B? sung/chu?n h?a entity fields n?u doc thu?c final corpus |
| INFO | FAO_037 | KG facts | data/raw_docs/FAO_037_na265en.pdf | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng; production_mode qu? chung | B? sung/chu?n h?a entity fields n?u doc thu?c final corpus |
| INFO | FAO_038 | KG facts | data/raw_docs/FAO_038_ca6702en.pdf | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng | B? sung/chu?n h?a entity fields n?u doc thu?c final corpus |
| INFO | FAO_039 | KG facts | data/raw_docs/FAO_039_ad893e.pdf | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng | B? sung/chu?n h?a entity fields n?u doc thu?c final corpus |
| INFO | FAO_040 | KG facts | data/raw_docs/FAO_040_i8064en.pdf | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng | B? sung/chu?n h?a entity fields n?u doc thu?c final corpus |
| INFO | FAO_041 | KG facts | data/raw_docs/FAO_041_cd3785en.pdf | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng; production_mode qu? chung | B? sung/chu?n h?a entity fields n?u doc thu?c final corpus |
| INFO | FAO_042_biosecurity_philippines | KG facts | data/raw_docs/FAO_042_biosecurity_philippines.pdf | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng | B? sung/chu?n h?a entity fields n?u doc thu?c final corpus |
| INFO | FAO_042_i3720e | KG facts | data/raw_docs/FAO_042_i3720e.pdf | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng | B? sung/chu?n h?a entity fields n?u doc thu?c final corpus |
| INFO | FAO_043 | KG facts | data/raw_docs/FAO_043_boosting_biosecurity_peru.pdf | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng | B? sung/chu?n h?a entity fields n?u doc thu?c final corpus |
| INFO | NACA_001 | KG facts | data/raw_docs/NACA_001_1737869839.pdf | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng; production_mode qu? chung | B? sung/chu?n h?a entity fields n?u doc thu?c final corpus |
| INFO | RIA3_001 | KG facts | data/raw_docs/RIA3_001_quy_hoach_nuoi_tom_hum_2030.pdf | thi?u related_disease; title/keywords c? d?u hi?u disease nh?ng related_disease tr?ng | B? sung/chu?n h?a entity fields n?u doc thu?c final corpus |

## Next steps after audit

1. S?a c?c CRITICAL/WARNING trong report tr??c.
2. Ki?m tra l?i metadata v? raw docs sau khi s?a.
3. Ch? rebuild vector store/KG khi audit pass ho?c warning ?? ???c ch?p nh?n c? l? do.
4. Sau khi data s?ch: backup vector_store/ontology/results/metrics, rebuild vector store, sync/update ontology/KG facts, verify KG runtime, rerun baselines, c?p nh?t relevance judgments n?u doc m?i v?o Top-k, recompute metrics/latency/figures/topic distribution/KG diagnostics, update report.

## Output files

- `outputs\metadata_rawdocs_audit_after_new_docs.md`
- `outputs\metadata_rawdocs_audit_after_new_docs.csv`
- `outputs\metadata_rawdocs_missing_or_problematic_files.csv`
- `outputs\metadata_rawdocs_new_docs_review.csv`
