# Corpus topic distribution report

Generated at: `2026-05-29`

## 1. Mục tiêu

Report này thống kê corpus theo nhóm chủ đề để kiểm tra dữ liệu có bị lệch quá nhiều về một nhóm hay không. Mục tiêu là cung cấp bằng chứng định lượng cho phần mô tả dữ liệu trong báo cáo đồ án, đồng thời chỉ ra các nhóm còn mỏng để đưa vào hạn chế/hướng phát triển.

## 2. Dữ liệu đầu vào

- Metadata file: `data/metadata/document_metadata_cleaned.xlsx`
- Tổng số tài liệu: **138**
- Số cột metadata phát hiện: **15**
- Các cột metadata: `doc_id, title, author, publishedYear, source, referenceUrl, docType, file_path, related_taxon, related_disease, related_location, production_mode, keywords, language, note`

Mapping cột được dùng:

| field | detected_column |
| --- | --- |
| doc_id | doc_id |
| title | title |
| source | source |
| year | publishedYear |
| doc_type | docType |
| taxon | related_taxon |
| disease | related_disease |
| pathogen | MISSING |
| symptom | MISSING |
| prevention | MISSING |
| treatment | MISSING |
| production_mode | production_mode |
| location | related_location |
| country | MISSING |
| region | MISSING |
| language | language |
| summary | MISSING |
| keywords | keywords |
| notes | note |
| file_path | file_path |
| url | referenceUrl |

Cột thiếu/không có trong metadata hiện tại: pathogen, symptom, prevention, treatment, country, region, summary

## 3. Phương pháp phân loại topic

Phân loại được thực hiện theo hướng multi-label: một tài liệu có thể thuộc nhiều nhóm chủ đề cùng lúc. Ví dụ một manual về AHPND trong hatchery tôm có thể đồng thời thuộc `aquatic_disease`, `hatchery_seed_production`, `biosecurity_management` và `species_taxon_specific`.

Topic group được xác định bằng cách kết hợp metadata fields (`related_taxon`, `related_disease`, `related_location`, `production_mode`, `keywords`, `docType`, `language`) và keyword trong title/note/keywords. Đây là thống kê hỗ trợ báo cáo, không phải annotation chủ đề hoàn hảo. Tổng count theo topic vì vậy có thể lớn hơn tổng số tài liệu.

## 4. Kết quả tổng thể theo topic group

| topic_group | n_documents | percentage_of_corpus | notes |
| --- | --- | --- | --- |
| aquatic_disease | 106 | 76.81 | multi-label count; total across topics can exceed corpus size |
| marine_aquaculture | 23 | 16.67 | multi-label count; total across topics can exceed corpus size |
| hatchery_seed_production | 21 | 15.22 | multi-label count; total across topics can exceed corpus size |
| biosecurity_management | 63 | 45.65 | multi-label count; total across topics can exceed corpus size |
| environment_water_quality | 28 | 20.29 | multi-label count; total across topics can exceed corpus size |
| local_vietnam_khanhhoa | 39 | 28.26 | multi-label count; total across topics can exceed corpus size |
| species_taxon_specific | 137 | 99.28 | multi-label count; total across topics can exceed corpus size |
| general_policy_technical | 0 | 0.00 | multi-label count; total across topics can exceed corpus size |
| uncategorized | 0 | 0.00 | documents not matched by topic rules; inspect manually |

Số tài liệu multi-label: **135/138**. Số tài liệu chưa phân loại được: **0**.

## 5. Phân bố theo nguồn tài liệu

Phân bố theo source group:

| source | n_documents | percentage |
| --- | --- | --- |
| FAO | 45 | 32.61 |
| PMC/journal | 40 | 28.99 |
| Vietnamese journal | 19 | 13.77 |
| SEAFDEC | 11 | 7.97 |
| TB | 7 | 5.07 |
| NACA | 3 | 2.17 |
| TCTS | 2 | 1.45 |
| Nhà xuất bản Đại học Cần Thơ | 2 | 1.45 |
| RIA3 | 1 | 0.72 |
| Trung tâm Khuyến nông Quốc gia | 1 | 0.72 |
| Hội nghị Công nghệ Sinh học toàn quốc 2020 | 1 | 0.72 |
| Trung tâm Khuyến ngư Quốc gia | 1 | 0.72 |
| Kỷ yếu Hội nghị Nghiên cứu cơ bản trong Khoa học Trái đất và Môi trường | 1 | 0.72 |
| Viện Khoa học Thủy lợi Việt Nam | 1 | 0.72 |
| TNU Journal of Science and Technology | 1 | 0.72 |
| Aquaculture and Fisheries | 1 | 0.72 |
| Thư viện số Trường Đại học Đà Lạt | 1 | 0.72 |

Phân bố source-topic chi tiết được lưu tại `outputs/corpus_topic_distribution_by_source.csv`. Nhìn chung, source group lớn nhất là **FAO** với **45** tài liệu. Corpus cũng có nhóm tài liệu từ journal/PMC-style, SEAFDEC, NACA, RIA3 và tài liệu tiếng Việt như TB/TCTS nếu metadata có nguồn tương ứng.

Doc type phổ biến:

| doc_type | n_documents | percentage |
| --- | --- | --- |
| Journal article | 63 | 45.65 |
| Technical study | 12 | 8.70 |
| Technical book | 9 | 6.52 |
| Proceedings paper | 9 | 6.52 |
| Technical report | 7 | 5.07 |
| Technical article | 6 | 4.35 |
| Manual / Guide | 2 | 1.45 |
| Meeting document | 2 | 1.45 |
| Brochure | 2 | 1.45 |
| Other document | 2 | 1.45 |
| Guideline | 2 | 1.45 |
| Magazine article | 2 | 1.45 |

Language:

| language | n_documents | percentage |
| --- | --- | --- |
| English | 99 | 71.74 |
| Vietnamese | 39 | 28.26 |

## 6. Phân bố tài liệu địa phương

Số tài liệu thuộc nhóm `local_vietnam_khanhhoa`: **39**. Bảng location/top region:

| location_or_region | n_documents | notes |
| --- | --- | --- |
| Vietnam/local-related | 39 | derived local flag |
| Việt Nam | 30 | from related_location metadata |
| Global | 24 | from related_location metadata |
| Khánh Hòa | 15 | from related_location metadata |
| India | 7 | from related_location metadata |
| Vietnam | 7 | from related_location metadata |
| Thailand | 6 | from related_location metadata |
| Latin America | 5 | from related_location metadata |
| Asia | 4 | from related_location metadata |
| Nam Trung Bộ | 4 | from related_location metadata |
| Philippines | 4 | from related_location metadata |
| Bangladesh | 3 | from related_location metadata |
| Cam Ranh | 3 | from related_location metadata |
| China | 3 | from related_location metadata |
| Indonesia | 3 | from related_location metadata |
| Phú Yên | 3 | from related_location metadata |
| Bangkok | 2 | from related_location metadata |
| Bình Định | 2 | from related_location metadata |
| Ecuador | 2 | from related_location metadata |
| Malaysia | 2 | from related_location metadata |

File đầy đủ: `outputs/corpus_topic_distribution_by_location.csv`.

## 7. Nhận xét về độ cân bằng dữ liệu

Corpus có bao phủ nhiều nhóm chủ đề khác nhau, đặc biệt các nhóm nổi bật là species_taxon_specific (137 tài liệu, 99.28%), aquatic_disease (106 tài liệu, 76.81%), biosecurity_management (63 tài liệu, 45.65%), local_vietnam_khanhhoa (39 tài liệu, 28.26%), environment_water_quality (28 tài liệu, 20.29%). Nhóm nhiều nhất là **species_taxon_specific** với **137** tài liệu, phản ánh trọng tâm của corpus vào các tài liệu có taxon/loài cụ thể và tài liệu bệnh/quản lý sức khỏe thủy sản. Nhóm ít nhất trong các nhóm có tài liệu là **hatchery_seed_production** với **21** tài liệu.

Không nên diễn giải corpus là hoàn toàn cân bằng, vì phân bố vẫn chịu ảnh hưởng bởi nguồn thu thập và trọng tâm bài toán shrimp disease/biosecurity. Tuy vậy, thống kê multi-label cho thấy dữ liệu không chỉ tập trung vào một nhóm duy nhất mà có độ phủ qua disease, hatchery, management, environment, local và species/taxon. Các nhóm có số lượng thấp hơn nên được xem là hạn chế và hướng bổ sung dữ liệu nếu phát triển hệ thống quy mô lớn hơn.

## 8. Đoạn có thể chèn vào báo cáo

Corpus cuối cùng của đề tài gồm **138** tài liệu, được thống kê theo các nhóm chủ đề chính bằng phương pháp multi-label dựa trên metadata và keyword trong title/notes. Kết quả cho thấy các nhóm có số lượng nổi bật gồm species_taxon_specific (137 tài liệu, 99.28%), aquatic_disease (106 tài liệu, 76.81%), biosecurity_management (63 tài liệu, 45.65%), local_vietnam_khanhhoa (39 tài liệu, 28.26%), environment_water_quality (28 tài liệu, 20.29%). Nhóm `local_vietnam_khanhhoa` có **39** tài liệu, phản ánh sự hiện diện của tài liệu Việt Nam/Khánh Hòa/ĐBSCL và các vùng nuôi liên quan. Do cách phân loại là multi-label, một tài liệu có thể thuộc nhiều nhóm nên tổng số count theo nhóm có thể lớn hơn **138**. Thống kê này cho thấy corpus không bị lệch hoàn toàn vào một nhóm duy nhất, mà có độ bao phủ nhất định giữa bệnh thủy sản, nuôi/trại giống, quản lý an toàn sinh học, môi trường và tài liệu địa phương. Tuy nhiên, phân bố chưa thể xem là cân bằng tuyệt đối; các nhóm có số lượng thấp hơn cần được bổ sung nếu mở rộng đề tài thành hệ thống retrieval chuyên sâu hơn.

## 9. Bảng gợi ý đưa vào báo cáo

| Nhóm chủ đề | Số tài liệu | Tỷ lệ (%) | Ý nghĩa trong đánh giá |
| --- | --- | --- | --- |
| aquatic_disease | 106 | 76.81 | Đánh giá truy vấn bệnh, pathogen, diagnosis và disease control. |
| marine_aquaculture | 23 | 16.67 | Đánh giá truy vấn nuôi biển, lobster/coastal aquaculture. |
| hatchery_seed_production | 21 | 15.22 | Đánh giá truy vấn hatchery, seed, larvae, broodstock. |
| biosecurity_management | 63 | 45.65 | Đánh giá truy vấn biosecurity, prevention, risk và health management. |
| environment_water_quality | 28 | 20.29 | Đánh giá truy vấn môi trường, quan trắc và water quality. |
| local_vietnam_khanhhoa | 39 | 28.26 | Đánh giá truy vấn địa phương Việt Nam/Khánh Hòa/ĐBSCL. |
| species_taxon_specific | 137 | 99.28 | Đánh giá truy vấn theo loài/taxon như shrimp, lobster, Penaeus. |
| general_policy_technical | 0 | 0.00 | Bổ sung tài liệu chính sách/kỹ thuật/tổng quan. |

## 10. Hạn chế

- Thống kê dựa trên metadata/keyword nên có thể chưa hoàn hảo.
- Một số tài liệu có thể bị thiếu hoặc dư topic label nếu metadata chưa đầy đủ hoặc title quá chung.
- `general_policy_technical` chỉ được gán khi tài liệu không rơi rõ vào các nhóm chuyên đề khác.
- Nếu muốn dùng phân bố chủ đề như benchmark học thuật, cần kiểm tra thủ công hoặc gán topic label riêng bởi annotator.
- Vì là multi-label, tổng count theo topic không tương ứng với số tài liệu duy nhất.

## 11. Safety confirmation

- Không sửa metadata gốc.
- Không sửa ontology/runtime/scoring.
- Không sửa query set/relevance judgments/baseline results/metrics.
- Chỉ tạo output thống kê mới trong `outputs/`, `outputs/figures/` và script trong `experiments/`.

## 12. Outputs

- `outputs/corpus_topic_distribution.csv`
- `outputs/corpus_topic_distribution_by_source.csv`
- `outputs/corpus_topic_distribution_by_location.csv`
- `outputs/corpus_topic_distribution_document_labels.csv`
- `outputs/corpus_topic_distribution_report.md`
- `outputs/figures/fig_corpus_topic_distribution.png`
