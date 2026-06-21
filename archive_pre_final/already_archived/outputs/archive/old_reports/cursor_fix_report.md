# Cursor fix report — weak query hardening (facts / aliases / KG scoring)

## A. Mục tiêu lần này

- Làm chắc hai ca yếu: **infectious myonecrosis** và **nuôi tôm hùm ở Khánh Hòa** theo hướng giảng viên: tăng **fact coverage**, **alias coverage**, **entity linking**, và tận dụng KG trong scoring — **không** mở rộng tính năng lan man.
- Giữ ổn các truy vấn đang tốt (AHPND, đốm trắng, biosecurity hatchery, trại giống tôm sú Ấn Độ) hoặc ghi rõ trade-off nếu có.

## B. Những file đã đọc (tối thiểu)

- `hybrid_search.py`, `kg_runtime.py`, `verify_kg_runtime.py`, `full_corpus_query_verification.py`
- `outputs/full_corpus_query_verification.json`, `outputs/kg_runtime_verification.json`
- `data/ontology/taxon_enriched_facts_v2.owl` (ontology runtime chính)

## C. Những file đã sửa

| File | Thay đổi |
|------|----------|
| `data/ontology/taxon_enriched_facts_v2.owl` | Thêm cá thể bệnh **IMN** + virus **IMNV**; `aboutDisease` IMN cho FAO_010, PMC_013, FAO_034, FAO_045; thêm IMN vào SEAFDEC_009 (danh mục bệnh xuyên biên giới); mở rộng alias **Tôm hùm bông** và **Ven biển Khánh Hòa** |
| `kg_runtime.py` | Thêm điểm quan hệ **taxon `isFoundIn` location** khi query có taxon+location và tài liệu `aboutTaxon` khớp taxon đó |
| `hybrid_search.py` | `CANDIDATE_K = 20`; alias **lobster** / **Khanh Hoa** bổ sung; làm rõ chuỗi giải thích khi **metadata_delta=0** (tránh nhầm “no KG match”) |
| `dump_six_queries.py`, `build_weak_query_comparison.py`, `capture_weak_queries.py` | Tiện ích đo snapshot / so sánh (hỗ trợ bằng chứng before/after) |

## D. Các output đã cập nhật

- `outputs/weak_query_fix_before.json` — baseline (trích cấu trúc từ `full_corpus_query_verification.json` trước chỉnh OWL/score; cùng pipeline đo lường).
- `outputs/weak_query_fix_after.json` — sau chỉnh (chạy `dump_six_queries.py`).
- `outputs/weak_query_fix_comparison.json` — so sánh theo từng query.
- `outputs/kg_runtime_verification.json` — chạy lại `verify_kg_runtime.py`.
- `outputs/full_corpus_query_verification.json` — chạy lại `full_corpus_query_verification.py`.
- `hybrid_comparison.csv`, `hybrid_results.txt` — `python hybrid_search.py export_csv` và `all`.

**Runtime ontology:** `data/ontology/taxon_enriched_facts_v2.owl` (`used_source=facts_v2`).

**Script pipeline ontology khác** (`sync_metadata_to_owl.py`, `audit_document_fact_coverage.py`, …) **không** chạy lại vì sửa trực tiếp `taxon_enriched_facts_v2.owl` và logic KG/hybrid — đủ để output phản ánh thay đổi.

## E. Chẩn đoán trước sửa (theo query ưu tiên)

| Query | Vấn đề chính |
|--------|----------------|
| **infectious myonecrosis** | Metadata + alias cục bộ đã bắt **IMN**, nhưng **không có disease individual** trong OWL → `link_query_entities_kg` trả rỗng; tài liệu **không có** `aboutDisease` trỏ URI bệnh → `kg_score` luôn 0 dù `doc_uri_in_kg` có. |
| **nuôi tôm hùm ở Khánh Hòa** | KG đã link **Tôm hùm bông** + **Ven biển Khánh Hòa**, nhưng **không có** luật nối `isFoundIn` với điểm tài liệu; top vector (SEAFDEC_008) **không** khớp taxon/location trong metadata → `metadata_delta=0`, `kg_score=0`. Ứng viên vector hẹp (K=10) khiến tài liệu có `aboutTaxon` tôm hùm khó vào vòng rerank. |
| **AHPND / đốm trắng / biosecurity / Ấn Độ** | Đã tốt; kiểm tra hồi quy sau chỉnh. |

## F. Alias / fact / metadata / logic đã chỉnh

- **Fact OWL:** `IMN`, `IMNV`; `aboutDisease` IMN trên các tài liệu IMN rõ ràng; IMN thêm vào SEAFDEC_009 vì đề cập bệnh trong bối cảnh bệnh xuyên biên giới.
- **Alias OWL:** tôm hùm (mud spiny lobster, v.v.); Khánh Hòa (coastal khanh hoa).
- **Logic KG:** cộng điểm quan hệ khi document `aboutTaxon` = taxon query và taxon đó `isFoundIn` đúng location URI của query.
- **Hybrid:** `CANDIDATE_K=20`; alias bổ sung trong `MANUAL_ALIASES`; text giải thích metadata rõ nghĩa hơn.

## G. Kết quả before/after (tóm tắt)

Chi tiết số liệu: `outputs/weak_query_fix_comparison.json` và `outputs/weak_query_fix_after.json`.

- **IMN:** `kg_linked_entities.disease` từ `[]` → `["Infectious myonecrosis"]`; `kg_score` top1 từ `0` → `0.43`; `final_score` top1 tăng; top1 vẫn **FAO_010** (đúng hướng).
- **Tôm hùm Khánh Hòa:** top1 hybrid từ **SEAFDEC_008** (tôm thẻ/AHPND Thái Lan) → **FAO_014** (lobster); `kg_score` từ `0` → `0.32`; vector-only top1 vẫn SEAFDEC_008 nhưng hybrid đã chỉnh.

## H. Query cải thiện rõ

- **infectious myonecrosis** — linking KG + fact + điểm KG trên top1.
- **nuôi tôm hùm ở Khánh Hòa** — top hybrid chuyển sang tài liệu gắn taxon tôm hùm; có đóng góp KG dương.

## I. Query vẫn chưa “cải thiện” theo nghĩa trade-off / còn hạn chế

- **tài liệu về trại giống tôm sú ở Ấn Độ** — top1 hybrid đổi **FAO_039 → FAO_002** (cùng chủ đề Ấn Độ + trại giống tôm sú; FAO_002 khớp monodon hatchery India rất sát). Đánh dấu **trade-off** nếu team muốn giữ nguyên đúng doc_id cũ.

## J. Nguyên nhân cụ thể nếu vẫn yếu / hạn chế

| Query | entity linking | alias | fact (OWL/doc) | metadata | scoring | dữ liệu thiếu |
|--------|----------------|-------|----------------|----------|---------|----------------|
| IMN | Đã mạnh hơn | Đã có trên node | Đã bổ sung | Giữ IMN trong sheet | KG + disease_priority | — |
| Tôm hùm KH | Đã OK | Đã mở | `isFoundIn` có sẵn | Vẫn không khớp cột metadata cho FAO_014 | Cần pool ứng viên + quan hệ | Ít tài liệu “nuôi tôm hùm Khánh Hòa” đúng nghĩa hẹp |

## K. False positive risk & kiểm soát

- **SEAFDEC_009** có thêm **IMN** trong `aboutDisease`: có thể tăng xuất hiện khi hỏi chung về bệnh tôm; mức độ chấp nhận vì bài nói transboundary shrimp diseases.
- **CANDIDATE_K=20:** tăng chi phí tính toán nhẹ; có thể thay đổi thứ hạng một số query — đã kiểm tra bốn query “ổn” vẫn cùng top1/final trong snapshot sau (trừ Ấn Độ như mục I).
- **FAO_014** top1 cho “nuôi tôm hùm ở Khánh Hòa:** là báo cáo thị trường lobster (GLOBEFISH), không phải sổ tay nuôi địa phương — **rủi ro ngữ nghĩa**; kiểm soát bằng nhận diện trong báo cáo và bước tiếp theo (metadata/fact theo production mode).

## L. Kết luận ngắn

- **Mạnh hơn:** IMN có **URI bệnh + fact document + KG score**; truy vấn tôm hùm + Khánh Hòa có **điểm KG từ taxon–location** và top hybrid **đúng nhóm loài** hơn trước.
- **Còn yếu / cần tiếp:** tài liệu “nuôi” địa phương có thể vẫn thiếu trong corpus; giải thích chuỗi “metadata: …” khi `metadata_delta=0` đã rõ hơn nhưng vẫn nên map thêm metadata `related_taxon`/`related_location` nếu muốn điểm metadata dương.
- **Bước tiếp theo hợp lý:** (1) bổ sung metadata sạch cho 1–2 tài liệu nuôi tôm hùm VN nếu có trong corpus; (2) tinh chỉnh B2 (ví dụ giảm điểm nếu `documentProductionMode` chỉ capture fisheries) nếu FAO_014 vẫn chưa đạt ý định “nuôi”.
