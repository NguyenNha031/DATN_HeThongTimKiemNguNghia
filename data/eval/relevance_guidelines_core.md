# Hướng dẫn gán nhãn relevance — CORE set

## Source of truth

- **Bộ query:** `data/eval/final_query_set_core.csv` (28 query).
- **Corpus / mô tả tài liệu:** `data/metadata/document_metadata_cleaned.xlsx` (110 doc).
- **Judgments:** `data/eval/relevance_judgments_core.csv` — mỗi dòng một cặp `(query_id, doc_id)` đã xét.

Không sử dụng `final_query_set_extended.csv` để tạo nhãn trong vòng này.

## Thang điểm (bắt buộc)

| `relevance_label` | `relevance_label_text` | Ý nghĩa |
|-------------------|------------------------|---------|
| 2 | very_relevant | Bám đúng intent chính; khớp các thực thể trọng tâm; không lệch ngữ cảnh. |
| 1 | partially_relevant | Liên quan nhưng thiếu/không khớp một điều kiện quan trọng (địa lý, loài, mode, trọng tâm bệnh…). |
| 0 | not_relevant | Sai intent, sai bệnh/loài/địa/mode chính, hoặc chỉ trùng từ khóa bề mặt. |

Không dùng score retrieval để quyết định nhãn; score chỉ có thể gợi ý **danh sách ứng viên** ở bước sau.

## Nguyên tắc theo `query_group`

### disease-specific

- **2:** Tài liệu lấy **đúng bệnh** trong query làm trục (manual, review, khảo sát dịch tễ có bệnh đó trung tâm). Nếu query chỉ nêu “tôm” mà doc là AHPND/WSSV rõ trên penaeid → có thể 2 nếu bệnh khớp.
- **1:** Đúng họ tôm / nuôi tôm nhưng **trọng tâm bệnh khác** (ví dụ query WSSV mà manual AHPND); hoặc đúng bệnh nhưng **sai vùng** mà query gợn vùng (DS_010 Philippines vs Malaysia).
- **0:** Bệnh khác hẳn (WSSV vs AHPND) hoặc không phải tài liệu bệnh học tôm.

### species-location

- **2:** Khớp **cả** loài (hoặc nhóm taxon trong metadata) **và** địa lý / khu vực trong intent; nếu query nhấn **hatchery + quốc gia** thì `production_mode` và `related_location` phải củng cố.
- **1:** Đúng quốc gia nhưng **mode sai** (ví dụ tác động môi trường grow-out thay vì trại giống); hoặc đúng chủ đề khu vực nhưng **không** đúng tiểu đề kỹ thuật (di chuyển giống vs AHPND).
- **0:** Sai quốc gia / sai loài chính.

### hatchery-production-mode

- **2:** `production_mode` hoặc title/keywords thể hiện **trại giống / PL / broodstock** khớp loài trong query.
- **1:** Cùng loài và biosecurity/hatchery nhưng **không** khớp probiotic/broodstock nếu query hỏi hẹp; hoặc đúng hatchery nhưng **khác khu vực** không được hỏi nhưng vẫn kỹ thuật gần.
- **0:** Grow-out ao, tài liệu cá hoặc **sai loài** (monodon vs vannamei).

### biosecurity-management

- **2:** Trọng tâm **biosecurity, surveillance, PMP, risk, EPR, diagnostic atlas** khớp sub-intent của query.
- **1:** Cùng “sức khỏe thủy sản” nhưng **chuyên môn hẹp hơn/rộng hơn** (manual một bệnh vs surveillance toàn cục).
- **0:** Không đụng tới quản lý dịch / biosecurity / chẩn đoán theo intent.

### local

- **2:** Metadata **Việt Nam / tỉnh / ĐBSCL / địa danh** trong title hoặc `related_location` **khớp** local intent; nội dung không chỉ “châu Á” chung.
- **1:** Cùng bệnh hoặc tôm VN nhưng **sai vùng** (Hà Tĩnh vs ĐBSCL); hoặc cùng loài địa phương nhưng **catalogue/thị trường** thay vì nuôi/quy hoạch.
- **0:** Không địa bàn VN khi query hỏi địa phương; hoặc hoàn toàn khác chủ đề.

## Case dễ nhầm (2 vs 1)

| Tình huống | Hướng xử lý |
|------------|-------------|
| Đúng topic, **sai location** | Ưu tiên **1** nếu vẫn cùng bệnh/loài; **0** nếu location là điều kiện cốt lõi (ví dụ Philippines vs query không hỏi vùng vẫn có thể 2 cho generic disease). |
| Đúng disease, **sai species** trong metadata | **1** nếu vẫn penaeid và cùng bệnh; **0** nếu query ép loài (thẻ vs sú) mà doc chỉ monodon. |
| Đúng species + location, **sai mode** | **1** (ví dụ hatchery query vs tài liệu đánh giá môi trường ao). |
| **Lobster** catalogue / **capture fisheries** vs nuôi địa phương | Catalogue/thị trường: **1** hoặc **0** tùy mức “nuôi Khánh Hòa” trong query; FAO_015 kiểu taxonomy → thường **1** hoặc **0**, không 2. |
| Biosecurity **chung** vs **hatchery + species** cụ thể | FAO PMP rộng → **1** so với query chỉ hatchery thẻ nếu không đủ chi tiết trại giống. |
| Query **pathogen-centered** + ép **tôm thẻ** (ví dụ DS_007) | Manual/review đúng pathogen + AHPND nhưng KG/hybrid thường gắn `aboutTaxon` lệch (ví dụ nhấn Tôm sú) so với thí nghiệm vannamei rõ ràng → có thể **1** (near-miss species emphasis), không tự động 2 chỉ vì title “AHPND strategy”. |

## Hard negative và near-miss (phục vụ P@5 / nDCG@5)

**Near-miss** (thường nhãn **1**): trùng bệnh, loài lân cận, hoặc cùng “họ” tài liệu (surveillance, hatchery, lobster) nhưng **lệch một điều kiện trung tâm** — địa bàn (tỉnh vs xã), mode (grow-out vs hatchery), trọng tâm bệnh trong doc (AHPND vs WSSV), hoặc nguồn/extension khác framework (TCTS vs Tép Bạc).

**Hard negative** (thường nhãn **0**): bề mặt có từ khóa chung (tôm, hatchery, biosecurity) nhưng **sai quốc gia**, **sai loài chính**, **sai production mode**, hoặc **sai cấp địa lý** (ví dụ ĐBSCL thay vì Hà Tĩnh cát; Latin thay vì Ấn–Bangladesh). Ưu tiên thêm các cặp này khi corpus có doc “gần giống” để tránh bộ judgment toàn nhãn 2.

**Ưu tiên nhóm dễ nhầm:** `local` (địa danh hẹp), `disease-specific` cùng taxon (AHPND vs WSSV, pathogen vs loài), `hatchery-production-mode` (quốc gia / loài / quy mô), `biosecurity-management` (PMP vs AMR brochure vs EIA), `lobster_khanh_hoa`, `shrimp_bangladesh`, `hatchery_larval_microbiome`.

## Bằng chứng bổ trợ cho query khó

- Với các cặp nhạy cảm **2 vs 1**, ngoài metadata nên ghi trong `judged_using_fields` nếu đã đối chiếu: `hybrid_comparison.csv`, `hybrid_results.txt`, `outputs/kg_runtime_verification.json` (chuỗi entity / rank hybrid giúp giảm quyết định chỉ dựa tiêu đề ngắn).
- `judgment_reason` cần nêu **điều kiện nào thiếu hoặc lệch** (location, mode, species, intent), không chỉ “liên quan một phần”.

## Query khó / mơ hồ

- Ghi rõ trong `judgment_reason` *vì sao* 1 thay vì 2 (thiếu điều kiện nào).
- Ưu tiên **phân tán** nhãn 0/1/2 trong cùng query để bước sau không chỉ có toàn 2.

## Trường metadata ưu tiên khi xét

`title`, `related_taxon`, `related_disease`, `related_location`, `production_mode`, `keywords`, `language`, `source` (đối chiếu nguồn TCTS vs Tép Bạc khi query local).

Không đọc full-text PDF trong file judgments này; nếu bước sau cần, có thể tinh chỉnh nhãn theo chunk.
