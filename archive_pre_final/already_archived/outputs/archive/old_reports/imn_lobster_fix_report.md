# Báo cáo vá IMN + tôm hùm Khánh Hòa (ontology / KG / hybrid)

## A. Mục tiêu lần này

- Tăng **fact + alias coverage** cho hai nhóm truy vấn yếu: **infectious myonecrosis (IMN/IMNV)** và **nuôi tôm hùm ở Khánh Hòa**, trong phạm vi **ontology + KG runtime + hybrid_search** (không mở nhánh intent/query understanding mới, không refactor lớn).
- **Đối chiếu before/after** trên **bộ query lõi** (6 câu), lưu JSON và giải thích nguyên nhân cải thiện / chưa cải thiện.

## B. Những file đã đọc (tối thiểu theo yêu cầu)

- `hybrid_search.py`, `kg_runtime.py`, `vector_search.py` (tham chiếu luồng vector), `capture_weak_queries.py`, `build_weak_query_comparison.py`
- `data/ontology/taxon_enriched_facts_v2.owl` (ontology runtime đang load)
- `data/metadata/document_metadata_cleaned.xlsx` (qua pandas khi kiểm tra FAO_014)
- `outputs/weak_query_fix_before.json`, `outputs/kg_runtime_verification.json`, `outputs/imn_lobster_before.json` / `after` / `comparison`

*(Các script `sync_metadata_to_owl.py`, `audit_document_fact_coverage.py`, … không chạy vì không thay metadata nguồn hay tái sinh ontology từ pipeline đó trong lần sửa này.)*

## C. Những file đã sửa / thêm

| File | Thay đổi |
|------|-----------|
| `hybrid_search.py` | Chuẩn hoá `canonicalize_term` (species: `tom hum bong` → `lobster`; location: `ven bien khanh hoa` → `Khanh Hoa`); mở rộng alias `Khanh Hoa`; thêm alias bệnh `shrimp infectious myonecrosis` cho IMN; **không** map `tom hum` → `lobster` trong `canonicalize_term` để tránh làm vỡ alias surface trong `build_term_index`. |
| `kg_runtime.py` | Mở rộng `_DISEASE_CANONICAL_REGISTRY` cho IMN (token cụm dài, bám corpus). |
| `data/ontology/taxon_enriched_facts_v2.owl` | Thêm `skos:altLabel` **shrimp infectious myonecrosis** cho individual **IMN**. |
| `build_imn_lobster_comparison.py` | **Mới**: sinh `outputs/imn_lobster_comparison.json`. |

## D. Alias đã bổ sung / siết lại

- **IMN (disease)**: `shrimp infectious myonecrosis` trong `MANUAL_ALIASES` + `skos:altLabel` trên `#IMN` trong OWL.
- **Chuẩn hoá registry** (`kg_runtime`): thêm token dạng compact cho cụm dài (bệnh IMN/IMNV trong tiêu đề tài liệu).
- **Địa điểm**: `ven bien khanh hoa` trong alias của `Khanh Hoa` (và trong `canonicalize_term`) để khớp prefLabel/alias node **Ven biển Khánh Hòa** với metadata.
- **Taxon**: chỉ map **`tom hum bong`** (từ nhãn KG “Tôm hùm bông”) → bucket metadata **`lobster`**; giữ nguyên alias nền `tom hum` / `tôm hùm` cho matching cụm tiếng Việt.

## E. Fact đã bổ sung / cập nhật

- **Không thêm** `aboutDisease` / `aboutTaxon` / `aboutLocation` mới trên Document: không có căn cứ PDF/metadata bổ sung trong phạm vi lần này (tránh dữ liệu giả).
- Cải thiện chính là **cầu nối nhãn KG ↔ cột metadata** (canonicalize + alias), tận dụng fact sẵn có (`Tom_hum_bong` `isFoundIn` `Ven_bien_Khanh_Hoa`, `FAO_014` `aboutTaxon`).

## F. Kết quả before/after (tóm tắt từ `imn_lobster_comparison.json`)

| Query | Top1 hybrid (before → after) | metadata_delta | kg_score | Ghi chú |
|-------|-------------------------------|----------------|----------|---------|
| bệnh AHPND trên tôm | FAO_001 → FAO_001 | 0.63 → 0.63 | 0.43 → 0.43 | Giữ ổn |
| bệnh đốm trắng ở tôm thẻ chân trắng | TCKHTS_001 → TCKHTS_001 | 0.45 → 0.45 | 0.63 → 0.63 | Giữ ổn |
| biosecurity trong hatchery tôm thẻ chân trắng | FAO_001 → FAO_001 | 0.08 → 0.08 | 0.25 → 0.25 | Giữ ổn |
| tài liệu về trại giống tôm sú ở Ấn Độ | FAO_002 → FAO_002 | 0.08 → 0.08 | 0.30 → 0.30 | Giữ ổn |
| infectious myonecrosis | FAO_010 → FAO_010 | 0.45 → 0.45 | 0.43 → 0.43 | Ranking không đổi; alias/registry mạnh hơn |
| nuôi tôm hùm ở Khánh Hòa | FAO_014 → FAO_014 | **0.0 → 0.22** | 0.32 → 0.32 | **+metadata**; final_score **0.944 → 1.164** |

**Lưu ý baseline**: `imn_lobster_before.json` được chụp trên workspace hiện tại: top1 hybrid cho câu tôm hùm đã là **FAO_014** (không còn **SEAFDEC_008** như snapshot cũ `weak_query_fix_before.json`). Phần cải thiện lần này là **metadata_delta** và **final_score**, không đổi doc_id top1.

## G. Infectious myonecrosis

- **Trước**: Đã nhận **IMN**, KG link **Infectious myonecrosis**, top1 **FAO_010**, `kg_score` 0.43 (aboutDisease + quan hệ affectsTaxon + pathogen IMNV).
- **Sau**: Cùng ranking/score; bổ sung **alias + registry** cho cụm dài / biến thể (vd. “shrimp infectious myonecrosis”) để **alias coverage** tốt hơn khi truy vấn đổi cách diễn đạt.
- **Chưa làm**: Không gắn thêm fact giả trên tài liệu khác; **SEAFDEC_009** vẫn có IMN trong danh sách bệnh giao cảnh — nếu cần tinh chỉnh ranking sẽ là bước sau (ngoài phạm vi “chỉ vá alias/fact có căn cứ”).

## H. Nuôi tôm hùm ở Khánh Hòa

- **Nguyên nhân yếu (đã chẩn đoán)**: Sau merge KG, canonical species là **Tôm hùm bông** và location **Ven biển Khánh Hòa**; metadata **FAO_014** dùng **lobster** + location **Global/Canada/China** → `term_match` **không** khớp → `metadata_delta = 0` dù KG đã cho **+0.32** (aboutTaxon + `isFoundIn`).
- **Sau sửa**: `canonicalize_term` map **`tom hum bong` → `lobster`**, **`ven bien khanh hoa` → `Khanh Hoa`** → metadata match species **+0.22**; KG giữ nguyên **+0.32**.
- **Hạn chế còn lại**: Top1 vẫn **FAO_014** (GLOBEFISH lobster analysis — thị trường, không phải hướng dẫn nuôi tại Khánh Hòa); **corpus có thể không có** tài liệu chuyên sâu “nuôi tôm hùm Khánh Hòa”.

## I. Query giữ ổn (không phá top1 hybrid lõi)

- **bệnh AHPND trên tôm**, **bệnh đốm trắng ở tôm thẻ chân trắng**, **biosecurity trong hatchery tôm thẻ chân trắng**, **tài liệu về trại giống tôm sú ở Ấn Độ**: cùng `doc_id` top1 hybrid và cùng `final_score` (sai số < 1e-3).

## J. Query vẫn còn hạn chế (theo nghĩa “chưa đạt ngữ nghĩa đầy đủ”)

- **nuôi tôm hùm ở Khánh Hòa**: điểm và căn cứ KG tốt hơn, nhưng **nội dung top1** vẫn có thể chưa đúng “case nuôi địa phương”.
- **infectious myonecrosis**: **ranking** không đổi nếu baseline đã đúng; cải thiện chủ yếu ở **alias coverage** / biến thể truy vấn.

## K. Nguyên nhân cụ thể (query còn yếu / giới hạn)

| Yếu tố | Ghi chú |
|--------|---------|
| Alias coverage | Đã vá IMN + Khánh Hòa; giữ `tom hum` không bị nuốt bởi canonicalize. |
| Fact coverage | Không thêm fact Document mới (không có căn cứ mới). |
| Entity linking | Merge KG + canonicalize để khớp metadata — đây là điểm nghẽn chính đã xử lý cho tôm hùm. |
| Metadata | FAO_014 có **lobster** nhưng không có **Khanh Hoa**; chỉ match species sau canonicalize. |
| Dữ liệu thiếu | Có thể thiếu tài liệu “nuôi tôm hùm tại Khánh Hòa” trong corpus. |

## L. Rủi ro false positive & kiểm soát

- **Không** thêm alias disease quá rộng (chỉ cụm bám tiêu đề/manual IMN).
- **Không** map `tom hum` → `lobster` trong `canonicalize_term` (đã gây collapse alias trong `build_term_index` và nhận nhầm **shrimp** từ `tom` trong quá khứ — đã kiểm soát bằng test `acceptance_checks()`).
- Location **Ven biển Khánh Hòa** map về **Khanh Hoa** — chỉ dùng trong luồng chuẩn hoá đã có sẵn node ontology tương ứng.

## M. Kết luận ngắn

- **Mạnh hơn**: Cầu nối **nhãn KG (tiếng Việt / địa danh ven biển) ↔ metadata (lobster / Khanh Hoa)**; hybrid cho câu tôm hùm + Khánh Hòa có **metadata_delta dương** cộng hưởng với KG.
- **Còn yếu**: Độ **đúng chủ đề nội dung** top1 cho “nuôi tại Khánh Hòa” phụ thuộc corpus; IMN **ranking** đã tốt — bổ sung chủ yếu **recall alias**.
- **Bước tiếp theo hợp lý**: Nếu có nguồn đáng tin (metadata/abstract), bổ sung **aboutLocation** hoặc tài liệu địa phương vào ontology; hoặc tăng `CANDIDATE_K` có kiểm soát nếu tài liệu đúng nằm ngoài top vector.

---

**Artifact**

- Before: `outputs/imn_lobster_before.json`
- After: `outputs/imn_lobster_after.json`
- So sánh: `outputs/imn_lobster_comparison.json`
- Verify: `python verify_kg_runtime.py` → `outputs/kg_runtime_verification.json`
- CSV / log: `hybrid_comparison.csv`, `hybrid_results.txt`
