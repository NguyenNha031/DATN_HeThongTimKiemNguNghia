# Guideline gán nhãn Relevance Judgments cho Aquaculture Semantic Search

Generated at: `2026-05-29`

File này mô tả quy tắc gán nhãn relevance judgments cho hệ thống tìm kiếm ngữ nghĩa tài liệu biển - thủy sản. Guideline được viết để phục vụ đánh giá retrieval trong project, có thể đưa vào phụ lục hoặc trích một phần vào Chương 4/5 của báo cáo.

## 1. Mục đích của relevance judgments

Relevance judgments được dùng làm ground truth để tính các chỉ số đánh giá retrieval như P@1, P@5, Recall@5, Recall@10, MRR, nDCG@5, nDCG@10 và MAP. Mỗi judgment là một cặp `query_id` - `doc_id`, phản ánh mức độ phù hợp của một tài liệu với intent thông tin của truy vấn.

Nhãn relevance không đánh giá tài liệu "hay" hay "dở" theo nghĩa tổng quát. Nhãn chỉ trả lời câu hỏi: tài liệu này có đáp ứng đúng nhu cầu thông tin của query hay không. Vì vậy, một tài liệu rất tốt về thủy sản vẫn có thể nhận nhãn 0 nếu sai bệnh, sai loài, sai địa điểm hoặc sai production mode so với query.

Nhãn không được gán dựa vào retrieval score hoặc thứ hạng của hệ thống. Các cột như `score_raw`, `score_normalized`, `final_score`, `vector_score`, `metadata_delta`, `kg_score`, `intent_adjustment` hoặc `rank` chỉ được dùng để tạo candidate pool hoặc truy vết nguồn candidate, không được dùng để quyết định label.

## 2. Thang nhãn 0-1-2

### Nhãn 0 - Không phù hợp

Dùng nhãn 0 khi tài liệu không trả lời intent chính của truy vấn. Trường hợp thường gặp là tài liệu chỉ cùng lĩnh vực thủy sản nhưng sai bệnh, sai loài, sai địa điểm hoặc sai production mode. Một tài liệu cũng được gán 0 nếu chỉ nhắc một từ khóa bề mặt nhưng không có nội dung liên quan thực chất, hoặc quá chung để hỗ trợ người dùng trả lời truy vấn.

Ví dụ: query hỏi AHPND trên tôm nhưng tài liệu chỉ nói về nuôi cá hoặc một bệnh khác không liên quan. Trong dữ liệu core, query `DS_001 - bệnh AHPND trên tôm` với tài liệu `PMC_023 - A review on molecular detection techniques of white spot syndrome virus...` là ví dụ nhãn 0 vì trọng tâm là WSSV, không phải AHPND.

### Nhãn 1 - Phù hợp một phần

Dùng nhãn 1 khi tài liệu liên quan đến một phần intent truy vấn nhưng thiếu một hoặc nhiều điều kiện quan trọng. Tài liệu có thể đúng chủ đề chung nhưng chưa đúng hoàn toàn disease, taxon, location hoặc production mode; đúng disease nhưng thiếu species/location; hoặc đúng species/location nhưng chủ đề chưa trực tiếp.

Nhãn 1 biểu thị tài liệu có thể hữu ích để tham khảo, nhưng không phải kết quả tốt nhất cho query. Ví dụ: query `LO_001 - nuôi tôm hùm ở Khánh Hòa` với tài liệu `FAO_015 - Marine lobsters of the world` là nhãn 1 trong core judgments vì đúng taxon lobster ở mức toàn cầu, nhưng không tập trung vào nuôi tôm hùm tại Khánh Hòa. Với query "lobster Khanh Hoa", một tài liệu chỉ nói về lobster chung hoặc chỉ nói về Khánh Hòa aquaculture nhưng không tập trung vào lobster cũng nên là 1 thay vì 2.

### Nhãn 2 - Rất phù hợp

Dùng nhãn 2 khi tài liệu đáp ứng trực tiếp intent chính của query. Tài liệu cần khớp các thực thể quan trọng như disease, taxon, location và production mode nếu query có các điều kiện này. Title, metadata, snippet hoặc nội dung tài liệu phải cho thấy tài liệu có thể trả lời tốt truy vấn.

Với query disease-specific, tài liệu phải nói rõ disease hoặc pathogen liên quan. Với query species-location, tài liệu nên khớp cả species và location, hoặc có bối cảnh địa phương rất rõ. Với query biosecurity-management, tài liệu phải tập trung vào biosecurity, prevention, health management, disease control hoặc risk management.

Ví dụ: query `DS_001 - bệnh AHPND trên tôm` với `FAO_001 - Shrimp acute hepatopancreatic necrosis disease strategy manual` là nhãn 2 vì tài liệu là manual trọng tâm về AHPND trên tôm. Query `BI_001 - biosecurity trong hatchery tôm thẻ chân trắng` với `FAO_005 - Health management and biosecurity maintenance in white shrimp hatcheries...` cũng là nhãn 2 vì khớp biosecurity, hatchery và tôm thẻ chân trắng.

## 3. Nguyên tắc gán nhãn

- Gán nhãn dựa trên intent truy vấn, không chỉ dựa trên từ khóa.
- Xem xét `query_group`, `primary_intent`, expected entities trong query set, title, metadata, abstract/snippet/source evidence và nội dung tài liệu nếu có.
- Không dùng retrieval score, `final_score`, `vector_score`, `kg_score`, `metadata_delta`, `intent_adjustment` hoặc rank để quyết định nhãn.
- Không thiên vị phương pháp nào tạo ra candidate. Candidate từ BM25, vector, metadata, ontology/KG hoặc hybrid đều được đánh giá bằng cùng một guideline.
- Nếu một tài liệu được lấy từ nhiều baseline, chỉ gán một nhãn duy nhất cho cặp `query_id` - `doc_id`.
- Ưu tiên đúng intent hơn là chỉ trùng từ khóa. Ví dụ, "shrimp" không đủ để phù hợp với query yêu cầu "white shrimp hatchery biosecurity".
- Với query có nhiều điều kiện, cần xét mức độ khớp từng điều kiện: disease, taxon/species, location, production mode, prevention/management topic.
- Nếu không chắc giữa 1 và 2, chọn 1 trừ khi tài liệu khớp trực tiếp và rõ ràng.
- Nếu không chắc giữa 0 và 1, chọn 1 khi tài liệu vẫn có thông tin hữu ích một phần cho người dùng.
- Ontology/KG và metadata có thể giúp nhận diện disease aliases, taxon, location hoặc production mode, nhưng không thay thế phán đoán relevance theo intent.

## 4. Tiêu chí theo nhóm truy vấn

Các nhóm query hiện có trong dữ liệu gồm `biosecurity-management`, `disease-specific`, `hatchery-production-mode`, `local`, `species-location`; extended query set có thêm `generic-mixed`.

### disease-specific

Intent chính: tìm tài liệu về một disease/pathogen cụ thể trong thủy sản, thường gắn với tôm hoặc loài nuôi liên quan.

- Label 2: tài liệu nói trực tiếp về disease/pathogen trong query và liên quan đến thủy sản/taxon phù hợp. Ví dụ AHPND, WSSV, EHP, IMNV, vibriosis phải được nêu rõ hoặc có alias tương đương.
- Label 1: tài liệu nói về bệnh thủy sản chung, disease liên quan gần, hoặc cùng taxon nhưng không tập trung vào disease trong query.
- Label 0: tài liệu không nói về disease, sai disease, hoặc chỉ cùng lĩnh vực nuôi trồng.
- Lỗi dễ gặp: gán 2 chỉ vì title có "shrimp disease" dù disease cụ thể sai; nhầm AHPND/EMS với WSSV/EHP khi query yêu cầu một bệnh cụ thể.

### species-location

Intent chính: tìm tài liệu khớp đồng thời loài/taxon và địa điểm hoặc region trong query.

- Label 2: khớp cả species/taxon và location, hoặc tài liệu có bối cảnh địa phương rất rõ. Ví dụ `tôm hùm Khánh Hòa Vịnh Cam Ranh Vạn Ninh` khớp với tài liệu RIA3 về tôm hùm và Khánh Hòa.
- Label 1: chỉ khớp species hoặc chỉ khớp location; hoặc khớp region rộng nhưng thiếu production/topic chính.
- Label 0: sai cả species và location, hoặc chỉ liên quan rất xa.
- Lỗi dễ gặp: nâng tài liệu catalogue toàn cầu lên 2 dù thiếu địa phương; coi tài liệu về tôm nói chung là phù hợp với query yêu cầu `Penaeus vannamei`, `Penaeus monodon` hoặc lobster.

### local

Intent chính: tìm tài liệu có bối cảnh địa phương rõ, ví dụ Việt Nam, Khánh Hòa, Phú Yên, ĐBSCL/Mekong Delta, Hà Tĩnh hoặc vùng nuôi cụ thể.

- Label 2: tài liệu có địa danh/region đúng hoặc bối cảnh Việt Nam/Khánh Hòa/Mekong Delta rõ, đồng thời khớp chủ đề chính của query.
- Label 1: tài liệu có chủ đề liên quan nhưng location chưa đúng, quá rộng, hoặc chỉ khớp một phần disease/species.
- Label 0: không có bối cảnh địa phương liên quan hoặc sai hoàn toàn chủ đề.
- Lỗi dễ gặp: gán cao cho tài liệu quốc tế chỉ vì cùng taxon; bỏ qua điều kiện địa phương trong query như Khánh Hòa, ĐBSCL hoặc Việt Nam.

### hatchery-production-mode

Intent chính: tìm tài liệu về production mode cụ thể như hatchery, seed production, larval rearing, broodstock/post-larvae hoặc mô hình nuôi được nêu trong query.

- Label 2: tài liệu tập trung vào hatchery/seed production/larval rearing/production mode trong query và khớp taxon nếu query nêu rõ.
- Label 1: tài liệu liên quan aquaculture hoặc disease management chung nhưng không tập trung production mode.
- Label 0: sai bối cảnh sản xuất, ví dụ grow-out pond/farming khi query yêu cầu hatchery.
- Lỗi dễ gặp: coi mọi tài liệu "shrimp farming" là hatchery; không phân biệt hatchery, grow-out, broodstock và post-larvae.

### biosecurity-management

Intent chính: tìm tài liệu về an toàn sinh học, prevention, health management, risk analysis, surveillance, zoning, emergency preparedness hoặc disease control.

- Label 2: tài liệu tập trung vào biosecurity, prevention, risk management, disease control hoặc health management, và khớp taxon/production mode nếu query có yêu cầu.
- Label 1: tài liệu liên quan bệnh hoặc nuôi trồng nhưng biosecurity chỉ là phụ, hoặc thiếu một điều kiện quan trọng như hatchery/species/location.
- Label 0: không liên quan đến management, prevention hoặc biosecurity.
- Lỗi dễ gặp: gán 2 cho tài liệu disease-specific chỉ vì có nhắc prevention; bỏ qua yêu cầu hatchery hoặc species trong query.

### generic-mixed

Intent chính: kiểm tra khả năng retrieval với các truy vấn rộng hoặc pha trộn nhiều chủ đề, ví dụ sustainability, environmental impact, production, taxonomy, genetic resources hoặc diagnostic guide.

- Label 2: tài liệu bao quát đúng topic chính và có đủ ngữ cảnh aquaculture/fisheries được query yêu cầu.
- Label 1: tài liệu liên quan một phần topic nhưng thiếu trọng tâm chính, thiếu domain thủy sản, hoặc chỉ khớp một vài keyword.
- Label 0: tài liệu sai topic chính, sai domain, hoặc quá xa để hỗ trợ người dùng.
- Lỗi dễ gặp: đánh giá quá rộng vì query generic; với nhóm này vẫn cần xác định intent chính trước khi gán nhãn.

## 5. Dataset snapshot

Snapshot được đọc từ các file hiện có trong project, không chạy lại experiment và không chỉnh sửa judgments.

| Split | Query file | Số query | Judgment file | Số judgment | Phân bố label |
|---|---:|---:|---|---:|---|
| Core | `data/eval/final_query_set_core.csv` | 28 | `data/eval/relevance_judgments_core.csv` | 181 | 0: 60, 1: 63, 2: 58 |
| Extended | `data/eval/final_query_set_extended.csv` | 96 | `data/eval/relevance_judgments_extended.csv` | 2727 | 0: 1197, 1: 850, 2: 680 |

Phân bố query group:

| Split | query_group | Số query |
|---|---|---:|
| Core | biosecurity-management | 6 |
| Core | disease-specific | 6 |
| Core | hatchery-production-mode | 4 |
| Core | local | 7 |
| Core | species-location | 5 |
| Extended | biosecurity-management | 16 |
| Extended | disease-specific | 16 |
| Extended | generic-mixed | 16 |
| Extended | hatchery-production-mode | 16 |
| Extended | local | 16 |
| Extended | species-location | 16 |

## 6. Quy trình tạo candidate pool để gán nhãn

Không gán nhãn chỉ trên output của một method. Candidate pool cần được tạo từ nhiều baseline để tránh thiên vị một hệ retrieval cụ thể. Với project hiện tại, các nguồn candidate có sẵn gồm:

| Split | File baseline result | Số dòng |
|---|---|---:|
| Core | `data/eval/results/baseline_lexical_core.csv` | 280 |
| Core | `data/eval/results/baseline_vector_core.csv` | 280 |
| Core | `data/eval/results/baseline_vector_metadata_core.csv` | 280 |
| Core | `data/eval/results/baseline_ontology_sparql_core.csv` | 280 |
| Core | `data/eval/results/baseline_hybrid_core.csv` | 280 |
| Core | `data/eval/results/baseline_hybrid_candidate_fusion_core.csv` | 280 |
| Extended | `data/eval/results/baseline_lexical_extended.csv` | 960 |
| Extended | `data/eval/results/baseline_vector_extended.csv` | 960 |
| Extended | `data/eval/results/baseline_vector_metadata_extended.csv` | 951 |
| Extended | `data/eval/results/baseline_ontology_sparql_extended.csv` | 960 |
| Extended | `data/eval/results/baseline_hybrid_extended.csv` | 951 |
| Extended | `data/eval/results/baseline_hybrid_candidate_fusion_extended.csv` | 960 |

Quy trình đề xuất:

1. Chạy hoặc đọc kết quả từ nhiều baseline: lexical/BM25, vector, vector_metadata, ontology_sparql, hybrid và hybrid_candidate_fusion nếu có.
2. Với mỗi query, lấy top-k candidate từ từng baseline theo `query_id` và `doc_id`.
3. Hợp nhất candidate theo cặp `query_id` - `doc_id`.
4. Loại trùng candidate. Nếu cùng một tài liệu xuất hiện từ nhiều baseline, chỉ giữ một dòng candidate để gán nhãn.
5. Dùng metadata, title, snippet/content, expected entities trong query set và bằng chứng từ ontology/KG để đọc hiểu candidate.
6. Gán nhãn thủ công theo intent và thang 0-1-2.
7. Không dùng score của baseline để quyết định label. Score chỉ giúp truy vết candidate đến từ nguồn nào.

Trong file `baseline_hybrid_candidate_fusion_core.csv`, các cột như `candidate_sources`, `candidate_union_count`, `lexical_rank`, `kg_seed_rank`, `vector_rank`, `vector_score`, `kg_score` và `final_score` hữu ích để mô tả quá trình pool/fusion, nhưng không phải tiêu chí relevance.

## 7. Quy trình rà soát và second annotator

Trong snapshot hiện tại, relevance judgments chủ yếu do một người xây dựng/rà soát. Đây là hạn chế về độ tin cậy học thuật vì chưa kiểm chứng đầy đủ mức độ đồng thuận liên chủ thể.

Nếu có thêm người gán nhãn, nên chọn 20-30% cặp `query_id` - `doc_id` để gán độc lập. Mẫu nên bao phủ đủ các nhóm `disease-specific`, `species-location`, `local`, `hatchery-production-mode`, `biosecurity-management` và `generic-mixed` nếu dùng extended set. Sau đó tính weighted Cohen's Kappa bằng:

```python
from sklearn.metrics import cohen_kappa_score

kappa_quadratic = cohen_kappa_score(labels_annotator_1, labels_annotator_2, weights="quadratic")
kappa_linear = cohen_kappa_score(labels_annotator_1, labels_annotator_2, weights="linear")
```

Diễn giải:

- `kappa < 0.4`: đồng thuận thấp.
- `0.4-0.6`: đồng thuận trung bình.
- `0.6-0.8`: đồng thuận khá.
- `> 0.8`: đồng thuận tốt.

Nếu kappa thấp, cần thảo luận lại guideline và các trường hợp bất đồng, đặc biệt là ranh giới giữa 1 và 2 hoặc giữa 0 và 1. Nếu chưa có second annotator, báo cáo phải ghi rõ đây là hạn chế.

Cách viết trong báo cáo: "Do giới hạn thời gian, bộ relevance judgments hiện tại chủ yếu được xây dựng bởi một annotator theo guideline 0-1-2. Vì chưa có second annotator độc lập, độ tin cậy liên chủ thể chưa được kiểm chứng đầy đủ bằng Cohen's Kappa. Đây được xem là một hạn chế của đánh giá hiện tại và là hướng cần hoàn thiện nếu phát triển đề tài thành nghiên cứu/bài báo."

## 8. Ví dụ gán nhãn từ dữ liệu hiện có

Các ví dụ dưới đây lấy từ `relevance_judgments_core.csv` và `relevance_judgments_extended.csv`. Vì nhãn đã tồn tại trong file judgments, cột loại nhãn được hiểu là `existing_label`, không phải nhãn mới thay thế file chính.

| query_id | query_text | query_group | doc_id | title | existing_label | Giải thích |
|---|---|---|---|---|---:|---|
| DS_001 | bệnh AHPND trên tôm | disease-specific | FAO_001 | Shrimp acute hepatopancreatic necrosis disease strategy manual | 2 | Tài liệu là manual trọng tâm về AHPND trên tôm, khớp disease và taxon chính. |
| LO_001 | nuôi tôm hùm ở Khánh Hòa | local | RIA3_001 | Quy hoạch nuôi tôm hùm đến năm 2020 và định hướng đến 2030 | 2 | Khớp loài tôm hùm, địa phương Khánh Hòa và intent nuôi/quy hoạch. |
| LO_EXT_005 | an toàn sinh học nuôi tôm Việt Nam WSSV EMS IMNV | local | TB_001 | Giải pháp an toàn sinh học trong nuôi tôm | 2 | Tài liệu tiếng Việt về an toàn sinh học trong nuôi tôm, có bối cảnh Việt Nam và disease/prevention liên quan. |
| BI_001 | biosecurity trong hatchery tôm thẻ chân trắng | biosecurity-management | FAO_005 | Health management and biosecurity maintenance in white shrimp hatcheries in Latin America | 2 | Khớp biosecurity, health management, hatchery và tôm thẻ chân trắng. |
| HM_001 | production mode trại giống tôm thẻ chân trắng | hatchery-production-mode | FAO_008 | Low water exchange shrimp farming: improvements in Thailand | 0 | Tài liệu nói về grow-out/pond farming ở Thái Lan, không phải hatchery tôm thẻ. |

File CSV minh họa đi kèm: `outputs/relevance_judgment_guideline_examples.csv`.

## 9. Checklist cho annotator

Trước khi gán nhãn, annotator cần hỏi:

1. Query đang muốn tìm disease, taxon, location, production mode hay topic/practice?
2. Document có khớp intent chính không?
3. Document có khớp các điều kiện phụ không?
4. Title/metadata/snippet có chứng cứ rõ không?
5. Nếu bỏ qua retrieval score, label còn hợp lý không?
6. Label 2 có thật sự trực tiếp không, hay chỉ nên là 1?
7. Label 0 có chắc là không hữu ích không?

## 10. Hạn chế

- Judgments hiện tại vẫn còn quy mô thực nghiệm, phục vụ đánh giá trong phạm vi đồ án.
- Một số nhãn có thể phụ thuộc vào hiểu biết miền của annotator, đặc biệt với bệnh tôm, production mode và địa danh vùng nuôi.
- Extended judgments được tạo theo quy trình có kiểm soát/candidate pooling + metadata nên cần manual review bổ sung nếu dùng như benchmark chính.
- Chưa có second annotator độc lập hoặc file second annotation, nên chưa thể tính Cohen's Kappa cho snapshot hiện tại.
- Relevance judgments không chứng minh toàn bộ tri thức miền đúng tuyệt đối; chúng chỉ phục vụ đánh giá retrieval theo intent truy vấn.
- Với các tài liệu có title/metadata không đủ rõ, annotator nên đọc thêm abstract/snippet hoặc nội dung PDF trước khi nâng nhãn lên 2.

## 11. Đoạn ngắn có thể đưa vào báo cáo

Bộ relevance judgments trong đồ án được xây dựng theo thang nhãn 0-1-2, trong đó 0 là không phù hợp, 1 là phù hợp một phần và 2 là rất phù hợp với intent truy vấn. Mỗi judgment tương ứng với một cặp query-document và được dùng làm ground truth để tính các chỉ số P@k, Recall@k, MRR, nDCG và MAP. Candidate pool không được lấy từ một phương pháp duy nhất mà được hợp nhất từ nhiều baseline, gồm lexical/BM25, vector search, vector kết hợp metadata, ontology/SPARQL, hybrid và hybrid candidate fusion. Sau khi loại trùng theo `query_id` và `doc_id`, từng candidate được gán nhãn dựa trên intent của query, title, metadata, snippet/nội dung tài liệu và các thực thể liên quan như disease, taxon, location hoặc production mode. Các điểm số retrieval như final score, vector score, KG score hoặc rank không được dùng để quyết định nhãn nhằm tránh thiên vị cho một phương pháp cụ thể. Thiết lập core gồm 28 queries được xem là bộ đánh giá chính vì các truy vấn được chọn lọc sát với mục tiêu của hệ thống. Thiết lập extended gồm 96 queries được dùng bổ sung để kiểm tra xu hướng trên phạm vi truy vấn rộng hơn và nhiều nhóm query hơn. Các nhóm truy vấn bao gồm disease-specific, species-location, local, hatchery-production-mode, biosecurity-management và generic-mixed trong extended set. Do giới hạn thời gian, relevance judgments hiện tại chủ yếu được xây dựng/rà soát bởi một annotator theo guideline trên. Vì chưa có second annotator độc lập, độ tin cậy liên chủ thể chưa được kiểm chứng đầy đủ bằng Cohen's Kappa và đây là một hạn chế của đánh giá hiện tại.
