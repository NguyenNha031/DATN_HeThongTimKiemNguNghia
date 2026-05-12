# Bộ truy vấn đánh giá (bước 1 — đã siết)

## Source of truth

| File | Vai trò |
|------|---------|
| `data/eval/final_query_set_core.csv` | **Official** — evaluation chính thức (~28 query) |
| `data/eval/final_query_set_extended.csv` | Stress-test / mở rộng (~24 query) |
| `data/eval/final_query_set.csv` | **Union** 52 query = core ∪ extended (cùng schema, có `query_family`, đã sửa `query_group`); tiện grep toàn bộ |

Phiên bản trước (52 query một file, chưa tách core/extended, chưa `query_family`) được thay bằng bộ ba file trên.

## Metadata gốc đang active

- **Đường dẫn:** `data/metadata/document_metadata_cleaned.xlsx`
- **Căn cứ:** 110 dòng, 15 cột (`doc_id`, `title`, `related_taxon`, `related_disease`, `related_location`, `production_mode`, …) — khớp quy mô 110 tài liệu đã map KG.
- **Đã rà thêm:** `data/metadata/document_metadata.xlsx` chỉ **41** dòng → coi là **bản không đầy đủ / legacy**, không dùng làm chuẩn rà soát query.
- **Đã tìm:** thư mục `data/metadata/`, so sánh số dòng hai file `.xlsx`.

## Nguyên tắc `query_group`

- **disease-specific:** bệnh / pathogen / hội chứng là trung tâm; loài có thể kèm nhưng không chiếm vai trò “địa lý + loài” thuần.
- **species-location:** phải có **cả** loài (hoặc nhóm taxon rõ) **và** địa lý/quốc gia/vùng rõ trong ý truy vấn; không dùng nhóm này cho câu chỉ nhấn hatchery kỹ thuật mà thiếu location trong lời hỏi.
- **hatchery-production-mode:** trọng tâm **trại giống / giai đoạn PL–broodstock / production mode** (ương, trại giống, gene bank như một *mode* tài liệu); không dùng cho thâm canh ao nuôi thương phẩm thuần (câu đó chuyển sang **biosecurity-management** nếu trọng tâm là quản lý rủi ro nông hộ).
- **biosecurity-management:** an toàn sinh học, giám sát, phân vùng, PMP, rủi ro, ứng phó khẩn cấp, AMR, EIA/môi trường nuôi, sổ tay chẩn đoán — tức **quản lý / chính sách / phòng dịch** hơn là cặp loài–địa đơn thuần.
- **local:** bối cảnh **Việt Nam / địa phương** (tỉnh, ĐBSCL, văn bản tiếng Việt mang intent địa phương); không gán **local** cho báo cáo khu vực châu Á thuần (chuyển **biosecurity-management** hoặc **species-location** tùy trọng tâm).

## Nguyên tắc core vs extended

- **Core:** intent rõ, dễ gán relevance hơn, bám trực tiếp metadata (title/location/disease/mode) của nhiều doc; phân bố đủ 5 nhóm.
- **Extended:** paraphrase/alias khó, query rộng (climate, prevention generic), stress-test KG (cá bớp), EIA/AMR, địa danh mờ, hoặc **cùng chủ đề với core** nhưng mức khó/độ mơ hồ cao hơn.

## `query_family`

- Cột **gom chủ đề** (ví dụ `ahpnd`, `wssv`, `lobster_khanh_hoa`, `shrimp_bangladesh`) để kiểm soát trùng ý và stratify khi báo cáo.
- Một `query_family` có thể có nhiều `query_id`; khi tính metric sau này có thể aggregate theo family hoặc chỉ dùng core.

## Định dạng CSV

- UTF-8 BOM, entity nhiều giá trị trong một ô: dấu **`;`**
- Cột bắt buộc: `query_id`, `query_text`, `query_group`, `query_family`, `primary_intent`, các `expected_entities_*`, `difficulty_level`, `reason_for_inclusion`

## Ràng buộc vòng này

- Không relevance labels, không chạy retrieval/metric, không đổi code hay ontology.
