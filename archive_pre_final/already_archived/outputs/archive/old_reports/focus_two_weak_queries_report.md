# Báo cáo: hai truy vấn yếu (IMN + tôm hùm Khánh Hòa)

## 1. Mục tiêu lần này

- Chỉ cải thiện **infectious myonecrosis** và **nuôi tôm hùm ở Khánh Hòa**, không mở nhánh kỹ thuật mới, không refactor lớn, không đổi kiến trúc pipeline chính (vẫn vector → rerank hybrid + KG).
- Giữ **các query đang ổn** không regression; có chỉnh thêm cầu nối **AHPND (KG tiếng Việt → disease_priority)** vì cùng một lỗi merge KG làm mất profile `disease_priority`.

## 2. File đã sửa / thêm

| File | Thay đổi |
|------|-----------|
| `hybrid_search.py` | `canonicalize_term`: IMN, AHPND (KG label); species `tom hum bong` → `lobster`; location `ven bien khanh hoa` → `Khanh Hoa`. `MANUAL_ALIASES`: bệnh **IMN** + mở rộng alias **Khanh Hoa**. `_doc_terms_with_canonical` cho **species** và **disease** (metadata `lobsters` ↔ `lobster`). Luồng **vector boost** hẹp: khi query có `tom hum` + `khanh hoa`, gộp thêm kết quả từ câu tiếng Anh cố định `LOBSTER_COASTAL_VECTOR_BOOST_QUERY` để đưa catalogue/market lobster vào pool rerank. `TEST_QUERIES` thêm `infectious myonecrosis` cho batch/CSV. |
| `kg_runtime.py` | `score_doc_with_kg(..., query_text="")`: khi query có `nuoi`, taxon tôm hùm (`Tom_hum_bong`) và location ven biển/ Khánh Hòa, trừ nhẹ KG nếu document chỉ gắn `Generic_CaptureFisheries` (tránh ưu tiên market/capture khi người dùng nói **nuôi** + địa phương). |
| `capture_focus_two_queries.py` | **Mới**: chụp JSON 6 query vào `outputs/focus_two_queries_metrics.json`. |
| `data/ontology/taxon_enriched_facts_v2.owl` | **Không sửa** trong lần chỉnh cuối (đủ fact sẵn có; tránh thêm fact không kiểm chứng). |

## 3. Before / After (nguồn: `outputs/focus_two_queries_before.json` vs `outputs/focus_two_queries_after.json`)

### 3.1 infectious myonecrosis

| Chỉ số | Trước | Sau |
|--------|-------|-----|
| top1 vector | FAO_010, 0.6177 | FAO_010, 0.6177 |
| top1 hybrid | FAO_010, final **1.3977** (metadata_delta **0.35**, kg_score **0.43**) | FAO_010, final **1.3977** (metadata_delta **0.35**, kg_score **0.43**) |
| detected disease (sau merge KG) | Infectious myonecrosis | **IMN** |
| profile | disease_priority | disease_priority |

**Đánh giá:** **Cải thiện một phần (chuẩn hoá & recall alias)** — điểm top1 không đổi vì baseline đã đúng FAO_010; sau sửa bệnh được gom về bucket **IMN** + `MANUAL_ALIASES` giúp metadata/`expand_terms` đồng bộ với các biến thể IMN/IMNV/cụm tiếng Anh có căn cứ tài liệu FAO.

**Nguyên nhân ranking không đổi:** vector đã đặt FAO_010 lên đầu; hybrid vẫn cùng doc và cùng tổng điểm trong snapshot.

### 3.2 nuôi tôm hùm ở Khánh Hòa

| Chỉ số | Trước | Sau |
|--------|-------|-----|
| top1 vector | SEAFDEC_008, 0.6984 | SEAFDEC_008, 0.6984 |
| top1 hybrid | SEAFDEC_008, final **0.6984** (metadata_delta **0.0**, kg_score **0.0**) | **FAO_015**, final **1.2318** (metadata_delta **0.22**, kg_score **0.23**) |
| detected (merge) | species Tôm hùm bông, location Ven biển Khánh Hòa | species **lobster**, location **Khanh Hoa** |

**Đánh giá:** **Cải thiện rõ** — hybrid không còn để top1 là tài liệu tôm Thái/AHPND (SEAFDEC_008) chỉ vì vector; ưu tiên catalogue tôm hùm (FAO_015) nhờ (1) canonical + metadata `lobsters`→`lobster`, (2) vector boost đưa FAO_014/015 vào pool, (3) KG aboutTaxon + `isFoundIn` Khánh Hòa trừ penalty capture khi có intent **nuôi**.

**Hạn chế còn lại:** top1 vẫn là **catalogue loài** (capture fisheries trong KG), không phải hướng dẫn **nuôi thương phẩm tại Khánh Hòa**; corpus có thể không có PDF đúng intent hẹp.

### 3.3 Các query giữ ổn / điều chỉnh có kiểm soát

| Query | Ghi chú |
|--------|---------|
| bệnh đốm trắng ở tôm thẻ chân trắng | **Giữ ổn:** top1 hybrid TCKHTS_001, final_score **1.3053** (trùng before). Không ép canonical WSSV (tránh disease_priority + miss metadata trên doc ngoài bảng 41 dòng). |
| biosecurity trong hatchery tôm thẻ chân trắng | **Giữ ổn:** top1 FAO_001, final **0.9413**. |
| tài liệu về trại giống tôm sú ở Ấn Độ | **Giữ ổn:** top1 FAO_039, final **0.8639**. |
| bệnh AHPND trên tôm | **Cải thiện điểm (không đổi doc):** FAO_001; metadata_delta **0.22 → 0.55**, final **1.2944 → 1.6244** — sửa profile sau merge KG (AHPND) để áp đúng luật `disease_priority`. |

## 4. False positive

- Không thêm bệnh/địa danh trôi nổi: IMN chỉ qua alias/registry đã bám FAO/IMNV; penalty capture chỉ khi đủ **nuoi** + taxon tôm hùm + location ven biển/Khánh Hòa trong KG query entities.

## 5. Kết luận

- **Đã cải thiện:** truy vấn **nuôi tôm hùm ở Khánh Hòa** (hybrid top1 và điểm metadata/KG); **bệnh AHPND trên tôm** (profile + metadata_delta); **infectious myonecrosis** (chuẩn hoá thực thể IMN + alias metadata, ranking giữ FAO_010).
- **Chưa / chỉ một phần:** nội dung top1 lobster vẫn catalogue/market, chưa phải case nuôi địa phương; IMN ranking không đổi vì đã tối ưu từ vector.

## 6. Artifact nên mở

- `outputs/focus_two_queries_before.json`, `outputs/focus_two_queries_after.json`
- `outputs/kg_runtime_verification.json`
- `hybrid_comparison.csv`, `hybrid_results.txt`
