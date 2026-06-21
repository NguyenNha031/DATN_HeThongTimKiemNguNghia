# Corpus topic distribution report

Generated at: `2026-05-29`

## 1. Mục tiêu

Report này thống kê corpus theo nhóm chủ đề để kiểm tra dữ liệu có bị lệch quá nhiều về một nhóm hay không. Mục tiêu là cung cấp bằng chứng định lượng cho phần mô tả dữ liệu trong báo cáo đồ án, đồng thời chỉ ra các nhóm còn mỏng để đưa vào hạn chế/hướng phát triển.

## 2. Dữ liệu đầu vào

- Metadata file: `data/metadata/document_metadata_cleaned.xlsx`
- Tổng số tài liệu: **110**
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
| aquatic_disease | 90 | 81.82 | multi-label count; total across topics can exceed corpus size |
| marine_aquaculture | 7 | 6.36 | multi-label count; total across topics can exceed corpus size |
| hatchery_seed_production | 18 | 16.36 | multi-label count; total across topics can exceed corpus size |
| biosecurity_management | 54 | 49.09 | multi-label count; total across topics can exceed corpus size |
| environment_water_quality | 22 | 20.00 | multi-label count; total across topics can exceed corpus size |
| local_vietnam_khanhhoa | 11 | 10.00 | multi-label count; total across topics can exceed corpus size |
| species_taxon_specific | 109 | 99.09 | multi-label count; total across topics can exceed corpus size |
| general_policy_technical | 0 | 0.00 | multi-label count; total across topics can exceed corpus size |
| uncategorized | 0 | 0.00 | documents not matched by topic rules; inspect manually |

Số tài liệu multi-label: **107/110**. Số tài liệu chưa phân loại được: **0**.

## 5. Phân bố theo nguồn tài liệu

Phân bố theo source group:

| source | n_documents | percentage |
| --- | --- | --- |
| FAO | 45 | 40.91 |
| PMC/journal | 39 | 35.45 |
| SEAFDEC | 11 | 10.00 |
| TB | 7 | 6.36 |
| NACA | 3 | 2.73 |
| RIA3 | 3 | 2.73 |
| TCTS | 1 | 0.91 |
| Vietnamese journal | 1 | 0.91 |

Phân bố source-topic chi tiết được lưu tại `outputs/corpus_topic_distribution_by_source.csv`. Nhìn chung, source group lớn nhất là **FAO** với **45** tài liệu. Corpus cũng có nhóm tài liệu từ journal/PMC-style, SEAFDEC, NACA, RIA3 và tài liệu tiếng Việt như TB/TCTS nếu metadata có nguồn tương ứng.

Doc type phổ biến:

| doc_type | n_documents | percentage |
| --- | --- | --- |
| Journal article | 41 | 37.27 |
| Technical study | 12 | 10.91 |
| Technical book | 9 | 8.18 |
| Proceedings paper | 9 | 8.18 |
| Technical report | 7 | 6.36 |
| Technical article | 6 | 5.45 |
| Manual / Guide | 2 | 1.82 |
| Meeting document | 2 | 1.82 |
| Brochure | 2 | 1.82 |
| Other document | 2 | 1.82 |
| Guideline | 2 | 1.82 |
| Magazine article | 2 | 1.82 |

Language:

| language | n_documents | percentage |
| --- | --- | --- |
| English | 97 | 88.18 |
| Vietnamese | 13 | 11.82 |

## 6. Phân bố tài liệu địa phương

Số tài liệu thuộc nhóm `local_vietnam_khanhhoa`: **11**. Bảng location/top region:

| location_or_region | n_documents | notes |
| --- | --- | --- |
| Global | 24 | from related_location metadata |
| Vietnam/local-related | 11 | derived local flag |
| India | 7 | from related_location metadata |
| Thailand | 6 | from related_location metadata |
| Latin America | 5 | from related_location metadata |
| Vietnam | 5 | from related_location metadata |
| Asia | 4 | from related_location metadata |
| Philippines | 4 | from related_location metadata |
| Bangladesh | 3 | from related_location metadata |
| China | 3 | from related_location metadata |
| Indonesia | 3 | from related_location metadata |
| Khánh Hòa | 3 | from related_location metadata |
| Bangkok | 2 | from related_location metadata |
| Ecuador | 2 | from related_location metadata |
| Malaysia | 2 | from related_location metadata |
| Mexico | 2 | from related_location metadata |
| Pacific | 2 | from related_location metadata |
| Phú Yên | 2 | from related_location metadata |
| Singapore | 2 | from related_location metadata |
| Southeast Asia | 2 | from related_location metadata |

File đầy đủ: `outputs/corpus_topic_distribution_by_location.csv`.

## 7. Nhận xét về độ cân bằng dữ liệu

Corpus có bao phủ nhiều nhóm chủ đề khác nhau, đặc biệt các nhóm nổi bật là species_taxon_specific (109 tài liệu, 99.09%), aquatic_disease (90 tài liệu, 81.82%), biosecurity_management (54 tài liệu, 49.09%), environment_water_quality (22 tài liệu, 20.0%), hatchery_seed_production (18 tài liệu, 16.36%). Nhóm nhiều nhất là **species_taxon_specific** với **109** tài liệu, phản ánh trọng tâm của corpus vào các tài liệu có taxon/loài cụ thể và tài liệu bệnh/quản lý sức khỏe thủy sản. Nhóm ít nhất trong các nhóm có tài liệu là **marine_aquaculture** với **7** tài liệu.

Không nên diễn giải corpus là hoàn toàn cân bằng, vì phân bố vẫn chịu ảnh hưởng bởi nguồn thu thập và trọng tâm bài toán shrimp disease/biosecurity. Tuy vậy, thống kê multi-label cho thấy dữ liệu không chỉ tập trung vào một nhóm duy nhất mà có độ phủ qua disease, hatchery, management, environment, local và species/taxon. Các nhóm có số lượng thấp hơn nên được xem là hạn chế và hướng bổ sung dữ liệu nếu phát triển hệ thống quy mô lớn hơn.

## 8. Đoạn có thể chèn vào báo cáo

Corpus cuối cùng của đề tài gồm **110** tài liệu, được thống kê theo các nhóm chủ đề chính bằng phương pháp multi-label dựa trên metadata và keyword trong title/notes. Kết quả cho thấy các nhóm có số lượng nổi bật gồm species_taxon_specific (109 tài liệu, 99.09%), aquatic_disease (90 tài liệu, 81.82%), biosecurity_management (54 tài liệu, 49.09%), environment_water_quality (22 tài liệu, 20.0%), hatchery_seed_production (18 tài liệu, 16.36%). Nhóm `local_vietnam_khanhhoa` có **11** tài liệu, phản ánh sự hiện diện của tài liệu Việt Nam/Khánh Hòa/ĐBSCL và các vùng nuôi liên quan. Do cách phân loại là multi-label, một tài liệu có thể thuộc nhiều nhóm nên tổng số count theo nhóm có thể lớn hơn **110**. Thống kê này cho thấy corpus không bị lệch hoàn toàn vào một nhóm duy nhất, mà có độ bao phủ nhất định giữa bệnh thủy sản, nuôi/trại giống, quản lý an toàn sinh học, môi trường và tài liệu địa phương. Tuy nhiên, phân bố chưa thể xem là cân bằng tuyệt đối; các nhóm có số lượng thấp hơn cần được bổ sung nếu mở rộng đề tài thành hệ thống retrieval chuyên sâu hơn.

## 9. Bảng gợi ý đưa vào báo cáo

| Nhóm chủ đề | Số tài liệu | Tỷ lệ (%) | Ý nghĩa trong đánh giá |
| --- | --- | --- | --- |
| aquatic_disease | 90 | 81.82 | Đánh giá truy vấn bệnh, pathogen, diagnosis và disease control. |
| marine_aquaculture | 7 | 6.36 | Đánh giá truy vấn nuôi biển, lobster/coastal aquaculture. |
| hatchery_seed_production | 18 | 16.36 | Đánh giá truy vấn hatchery, seed, larvae, broodstock. |
| biosecurity_management | 54 | 49.09 | Đánh giá truy vấn biosecurity, prevention, risk và health management. |
| environment_water_quality | 22 | 20.00 | Đánh giá truy vấn môi trường, quan trắc và water quality. |
| local_vietnam_khanhhoa | 11 | 10.00 | Đánh giá truy vấn địa phương Việt Nam/Khánh Hòa/ĐBSCL. |
| species_taxon_specific | 109 | 99.09 | Đánh giá truy vấn theo loài/taxon như shrimp, lobster, Penaeus. |
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
