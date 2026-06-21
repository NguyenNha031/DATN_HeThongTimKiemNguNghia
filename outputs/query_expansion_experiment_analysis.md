# Query expansion experiment analysis

Generated at: `2026-05-29`

## 1. Mục tiêu

Thí nghiệm này đánh giá ontology-based query expansion như một cấu hình mở rộng tên `hybrid_query_expansion`. Cấu hình này chỉ dùng để kiểm tra tiềm năng của query expansion trên core evaluation, không thay thế hybrid final và không chỉnh sửa runtime/scoring hiện có.

## 2. Dữ liệu và phương pháp

- Query set: `data/eval/final_query_set_core.csv` với 28 queries.
- Relevance judgments: `data/eval/relevance_judgments_core.csv`.
- Baseline so sánh: `vector_metadata`, `hybrid`, và `hybrid_query_expansion`; nếu có file hiện hữu thì report cũng tính thêm `hybrid_candidate_fusion`.
- Expansion source: `outputs/query_expansion_examples.csv` với các ví dụ alias/entity expansion hiện có.
- Cách tạo query: **Cách A** - `expanded_query = original_query + selected_expansion_terms`.
- Re-rank: wrapper gọi `hybrid_search.hybrid_search()` với expanded query, dùng runtime scoring hiện có. Script chỉ tạm set `FINAL_K=10` và `CANDIDATE_K>=150` trong process đang chạy, rồi restore lại; không sửa source code.
- Output Top-10 được ghi vào `data/eval/results/baseline_hybrid_query_expansion_core.csv`.

Số query có ít nhất một expansion term được dùng: **26/28**. Tổng số expansion terms được dùng: **113**.

## 3. Expansion rules

Expansion được chọn theo rule có kiểm soát:

- Disease -> dùng alias, pathogen, symptom, prevention/treatment nếu query có disease/entity liên quan.
- Taxon -> dùng scientific name, common name hoặc Vietnamese alias nếu query có taxon/species liên quan.
- Location -> dùng alias hoặc parent location, nhưng lọc location quá rộng nếu query không có local intent.
- Production mode/topic -> dùng hatchery, larval rearing, biosecurity, farming system nếu query có mode/topic tương ứng.

Giới hạn: disease tối đa 4, taxon tối đa 3, location tối đa 3, production/topic tối đa 3, tổng tối đa 8 terms/query. Các term quá chung như `aquaculture`, `fisheries`, `disease`, `shrimp` bị lọc để giảm query drift.

## 4. Metrics summary

| method | n_queries | P@1 | P@5 | Recall@5 | Recall@10 | MRR | nDCG@5 | nDCG@10 | MAP |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| vector_metadata | 28 | 0.7500 | 0.3929 | 0.4888 | 0.6246 | 0.8218 | 0.6143 | 0.6636 | 0.4750 |
| hybrid | 28 | 0.8214 | 0.4071 | 0.4980 | 0.6365 | 0.8694 | 0.6695 | 0.7222 | 0.4972 |
| hybrid_candidate_fusion | 28 | 0.8571 | 0.4214 | 0.5278 | 0.7061 | 0.9000 | 0.6721 | 0.7345 | 0.5428 |
| hybrid_query_expansion | 28 | 0.5714 | 0.3429 | 0.4242 | 0.5436 | 0.6798 | 0.5198 | 0.5657 | 0.4061 |

So với hybrid, `hybrid_query_expansion` có delta nDCG@10 = **-0.1565**. Query expansion làm giảm nDCG@10 trung bình so với hybrid trong cấu hình thử nghiệm này; nên giữ như future work và cần lọc/tuning thêm.

## 5. Results by query group

| query_group | hybrid_nDCG@10 | query_expansion_nDCG@10 | delta_nDCG@10 | hybrid_MAP | query_expansion_MAP |
| --- | --- | --- | --- | --- | --- |
| biosecurity-management | 0.7794 | 0.4447 | -0.3347 | 0.4855 | 0.2326 |
| disease-specific | 0.6450 | 0.5735 | -0.0715 | 0.4835 | 0.4138 |
| hatchery-production-mode | 0.6891 | 0.6688 | -0.0203 | 0.4380 | 0.4799 |
| local | 0.7334 | 0.6545 | -0.0789 | 0.5378 | 0.5063 |
| species-location | 0.7571 | 0.4948 | -0.2623 | 0.5183 | 0.4058 |

Nhóm có cải thiện/giảm được diễn giải theo delta nDCG@10 ở bảng trên. Vì expansion được áp dụng theo rule và query gốc khác nhau về entity coverage, kết quả theo group có thể không đồng đều.

## 6. Query-level examples

Query cải thiện nhiều nhất theo nDCG@10:

| query_id | query_text | query_group | hybrid | hybrid_query_expansion | delta |
| --- | --- | --- | --- | --- | --- |
| HM_001 | production mode trại giống tôm thẻ chân trắng | hatchery-production-mode | 0.3717 | 0.7662 | 0.3946 |
| LO_002 | hiện diện bệnh đốm trắng AHPND và EHP trên tôm ĐBSCL 2022–2024 | local | 0.8790 | 1.0000 | 0.1210 |
| LO_005 | rủi ro quản lý nông dân nuôi tôm càng quy mô nhỏ Đồng bằng sông Cửu Long | local | 0.2421 | 0.3631 | 0.1210 |

Query giảm nhiều nhất theo nDCG@10:

| query_id | query_text | query_group | hybrid | hybrid_query_expansion | delta |
| --- | --- | --- | --- | --- | --- |
| BI_004 | Progressive Management Pathway nuôi trồng an toàn sinh học FAO | biosecurity-management | 0.8651 | 0.0000 | -0.8651 |
| BI_001 | biosecurity trong hatchery tôm thẻ chân trắng | biosecurity-management | 0.8042 | 0.0000 | -0.8042 |
| LO_007 | các bệnh thường gặp tôm nước lợ và biện pháp phòng chống hiệu quả | local | 0.7673 | 0.0000 | -0.7673 |

Query không đổi:

| query_id | query_text | query_group | hybrid | hybrid_query_expansion | delta |
| --- | --- | --- | --- | --- | --- |
| BI_007 | ứng phó khẩn cấp dịch bệnh thủy sản hệ thống quốc gia | biosecurity-management | 0.4880 | 0.4880 | 0.0000 |
| BI_010 | sổ tay chẩn đoán bệnh thủy sản châu Á | biosecurity-management | 0.8888 | 0.8888 | 0.0000 |

Các query cải thiện thường là trường hợp expansion giúp nối alias/entity như disease alias, scientific name hoặc location/mode term. Các query giảm thường là dấu hiệu query drift: term mở rộng làm tăng trọng số cho tài liệu gần nghĩa nhưng lệch intent gốc.

## 7. Error analysis

- Expansion quá chung có thể kéo candidate về tài liệu tổng quan thay vì tài liệu đúng intent. Script đã lọc các term như `aquaculture`, `fisheries`, `disease`, `shrimp`, nhưng vẫn có thể còn term rộng như prevention/surveillance.
- Disease expansion có thể kéo sang tài liệu bệnh rộng hơn hoặc pathogen-focused nếu pathogen có mặt trong nhiều bệnh khác nhau.
- Location parent như Vietnam có thể làm mất độ cụ thể của query địa phương nếu dùng không kiểm soát.
- Production/topic expansion như hatchery/biosecurity có thể làm nhiễu nếu query thật ra tập trung disease hoặc location.
- Vì Cách A nối term vào query text, expanded query có thể dài hơn và làm thay đổi embedding direction. Multi-query pooling có thể là hướng an toàn hơn cho future work.

## 8. Kết luận

Query expansion làm giảm nDCG@10 trung bình so với hybrid trong cấu hình thử nghiệm này; nên giữ như future work và cần lọc/tuning thêm. Cấu hình này nên được trình bày như experiment/prototype hoặc future work, không nên thay thế hybrid final trong báo cáo chính. Để đưa query expansion thành đóng góp chính, cần tuning rule, kiểm soát weight của term mở rộng, và đánh giá ổn định hơn trên nhiều query hơn.

## 9. Đoạn có thể chèn vào báo cáo

Đề tài bổ sung một thí nghiệm mở rộng nhằm đánh giá ontology-based query expansion trên 28 truy vấn core. Với mỗi truy vấn, hệ thống chọn một số expansion terms có kiểm soát từ các alias/entity/fact hiện có, sau đó tạo expanded query và gọi lại hybrid runtime để lấy Top-10. Kết quả được so sánh với `vector_metadata` và `hybrid` bằng các metric P@1, P@5, Recall@5, Recall@10, MRR, nDCG@5, nDCG@10 và MAP. Trên thiết lập này, `hybrid_query_expansion` đạt nDCG@10 = 0.5657, so với hybrid = 0.7222. Kết quả cho thấy query expansion có hiệu ứng tiêu cực/mixed ở mức trung bình, nhưng vẫn có query cải thiện và query suy giảm riêng lẻ. Vì vậy, query expansion được xem là cấu hình experimental/future work, không thay thế hybrid final. Nguyên nhân chính là expansion có thể giúp tăng coverage alias/entity, nhưng cũng có nguy cơ query drift nếu term mở rộng quá rộng hoặc lệch intent.

## 10. Caveats

- Đây là thí nghiệm mở rộng, không thay hybrid final.
- Expansion rules vẫn cần manual review và tuning thêm.
- Query expansion có thể gây query drift.
- Cấu hình hiện tại dùng expanded query text; multi-query candidate pooling có thể ổn định hơn nhưng chưa được đưa vào final runtime.
- Chưa có kiểm định thống kê riêng cho query expansion.
- Không được viết rằng ontology expansion luôn tốt hơn query gốc.

## 11. Safety confirmation

- Không sửa runtime/scoring.
- Không sửa `hybrid_search.py`, `kg_runtime.py`, `vector_search.py`, `run_core_baselines.py`.
- Không sửa `app_streamlit.py`.
- Không sửa ontology/metadata.
- Không sửa query set/relevance judgments.
- Không sửa baseline results/metrics cũ.
- Chỉ tạo output mới cho experiment.

## 12. Outputs

- `experiments/run_query_expansion_experiment.py`
- `data/eval/results/baseline_hybrid_query_expansion_core.csv`
- `data/eval/metrics/query_expansion_metrics_summary.csv`
- `data/eval/metrics/query_expansion_metrics_by_query.csv`
- `data/eval/metrics/query_expansion_metrics_by_group.csv`
- `outputs/query_expansion_experiment_analysis.md`
- `outputs/query_expansion_applied_terms.csv`
- `outputs/figures/fig_query_expansion_experiment_summary.png`

## 13. Warnings

Không có warning nghiêm trọng.
