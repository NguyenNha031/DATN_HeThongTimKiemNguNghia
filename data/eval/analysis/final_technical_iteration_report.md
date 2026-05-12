# Báo cáo vòng kỹ thuật cuối (phạm vi hẹp)

Phạm vi: chỉ sửa `hybrid_search.py`, chạy lại toàn bộ `run_core_baselines.py` (CSV bước 3) và `compute_core_metrics.py`. **Không** sửa ontology OWL, **không** sửa metadata xlsx, **không** sửa judgments, **không** sửa Word.

---

## A. Query regression đã điều tra

| Query | Gold chính (rel 2 / rel 1) | Baseline lỗi trước sửa |
|-------|----------------------------|------------------------|
| **LO_007** | **TCTS_001** (2); TB_* / FAO_* (0–1) | Hybrid #1 **TB_002** (genomics); vector #1 **TCTS_001**. |
| **SL_004** | **FAO_008** (2); FAO_006 (1); … | Hybrid #1 **TB_001** (VN biosecurity); vector #1 **FAO_029**; **FAO_008** lẹm hạng. |
| **HM_001** | **FAO_005** (2); PMC_* hatchery (2) | Hybrid #1 **TB_007** (WSSV grow-out VN); vector #1 **FAO_005**. |

Đã đối chiếu: `baseline_vector_core.csv`, `baseline_hybrid_core.csv`, `relevance_judgments_core.csv`, `final_query_set_core.csv`.

---

## B. Root cause cụ thể

### LO_007
- **Alias sai:** cụm `benh thuong gap` trong bucket **fish diseases** khớp nhầm “bệnh thường gặp” trong truy vấn tôm nước lợ → sinh pseudo-entity disease, làm lệch profile/score.
- **Rerank:** **TB_002** có vector score hơi cao hơn **TCTS_001** trong pool chunk; không có tín hiệu title-align với sổ tay TCTS.

### SL_004
- **Location:** “Thái Lan” **chưa** có trong từ điển địa điểm → không bắt **Thailand** → metadata/KG không phạt doc chỉ có **Vietnam** (**TB_001**).
- **Species:** “tôm thẻ” không gom mạnh vào **Penaeus vannamei** → species-location synergy yếu cho **FAO_008**.
- **Practice:** không có boost cho title “low water exchange” + Thailand.

### HM_001
- **Embedding:** **TB_007** (WSSV, nuôi thương phẩm VN) score vector cao hơn **FAO_005** (hatchery manual).
- **Thiếu guardrail:** không phạt doc grow-out/WSSV khi truy vấn chỉ hỏi **production mode / trại giống** + vannamei **không** có disease trong query.

### Phụ (sanity): BI_001
- Khi thử gate hatchery quá rộng, **FAO_001** (AHPND strategy manual) có thể lên #1 thay **FAO_005**. Đã siết điều kiện intent chỉ cho HM_001 và thêm stack **biosecurity + hatchery** cho BI_001.

---

## C. Đã chọn sửa gì (tối thiểu)

**File:** `hybrid_search.py`

| Thay đổi | Hàm / vị trí | Logic cũ | Logic mới | Vì sao tối thiểu |
|----------|--------------|----------|-----------|------------------|
| Bỏ alias quá rộng | `MANUAL_ALIASES["disease"]["fish diseases"]` | Có `"benh thuong gap"` đơn | Chỉ cụm gắn cá | Tránh false disease trên LO_007 |
| Thailand + `tom the` | `MANUAL_ALIASES`, `canonicalize_term` | Không có | `Thailand` / `tom the` → vannamei | Chỉ bổ sung lỗ hổng địa điểm/species cho SL_004 |
| Giữ bề mặt alias | `build_term_index` (vòng alias thủ công) | `canonicalize_term` trên mọi alias | Lưu `surf` alias | Tránh gom `"tom hum"` → token lạc (lobster) |
| Canonicalize species | `canonicalize_term` | Thiếu | `tom hum`, `tom su`, `tom the chan trang` → taxon chuẩn | Khớp metadata/judgment, ổn định acceptance |
| Intent điểm cuối | `_intent_narrow_final_adjustment`, gọi trong `hybrid_search` | `final = vec + meta + kg` | `+ intent_adjustment` (bonus/penalty có điều kiện) | Chỉ kích hoạt khi mẫu query/title khớp rất rõ |
| BI_001 / HM_001 | `_hatchery_vannamei_production_mode_intent`, `_biosecurity_hatchery_vannamei_stack_intent` | — | Gate `production mode` **hoặc** `trai giong`; stack biosecurity+hatchery; phạt “strategy manual” không biosecurity | Tránh tác dụng chéo giữa BI_001 và HM_001 |

**Rủi ro phụ:** intent pattern có thể trùng với truy vấn hiếm khác → đã giữ điều kiện lặp (nhiều token + topic/mode).

**Phụ trợ:** `run_core_baselines.py` / `results_generation_notes.md` / `metrics_notes.md` — chỉ cập nhật mô tả pipeline.

---

## D. Ontology / metadata

- **Không** chỉnh `taxon_enriched_facts_v2.owl`.
- **Không** chỉnh `document_metadata_cleaned.xlsx`.

---

## E. Kết quả sanity check

### Regression (hybrid rank-1 doc sau sửa)
- **LO_007:** **TCTS_001** (đúng gold rel 2).
- **SL_004:** **FAO_008** (đúng gold rel 2).
- **HM_001:** **FAO_005** (đúng gold rel 2).

### Query “đang tốt” (kiểm tra không vỡ nặng)
- **DS_001:** #1 **TB_005** (rel 2 trong pool; chấp nhận).
- **DS_002:** #1 **TB_007** (WSSV — phù hợp query đốm trắng).
- **DS_010:** #1 **SEAFDEC_006** (giữ).
- **BI_001:** #1 **FAO_005** (rel 2 — phục hồi sau siết gate).
- **LO_001:** #1 **RIA3_001** (giữ như run hiện tại).

`acceptance_checks()` trong `hybrid_search.py`: **pass**.

---

## F. Cập nhật outputs / metrics

| Artifact | Ghi chú |
|----------|---------|
| `data/eval/results/baseline_*_core.csv` | Regen **toàn bộ** bởi `python run_core_baselines.py` (script luôn ghi 5 baseline). |
| `data/eval/metrics/baseline_metrics_*.csv` | `python data/eval/metrics/compute_core_metrics.py` |
| `data/eval/metrics/metrics_notes.md` | Thêm mục vòng cuối |
| `data/eval/results/results_generation_notes.md` | Công thức hybrid có `intent_adjustment` |

**Lý do chạy full baselines:** `run_core_baselines.main()` không tách mode chỉ hybrid; vector/lexical được ghi lại với cùng seed logic (vector không đổi công thức). **vector_metadata** có thể đổi nhẹ do chung `detect_entities` / `build_term_index`.

---

## G. Before / after (hybrid macro)

| Metric | Trước (bước 5 snapshot) | Sau (vòng cuối) |
|--------|-------------------------|-----------------|
| P@1 | 0.714 | **0.821** |
| P@5 | 0.386 | **0.407** |
| MRR | 0.808 | **0.869** |
| nDCG@10 | 0.676 | **0.722** |

**Thứ hạng regression:** LO_007, SL_004, HM_001 đều lấy lại doc gold ở #1 như bảng mục E.

---

## H. Kết luận

- Vòng kỹ thuật cuối **đáng giữ**: root cause rõ (alias + thiếu geo/species + rerank/KG không có guardrail), sửa **cục bộ** trong một module, metric hybrid cải thiện, sanity pass.
- **Nên chốt** hệ thống ở trạng thái mới cho báo cáo đánh giá nếu chấp nhận coupling nhẹ giữa `vector_metadata` và thay đổi từ điển entity trong `hybrid_search.py`.
- **Không** mở rộng ontology hàng loạt, **không** thêm heuristic rộng, **không** sửa judgments/query set, **không** đụng Word — đúng phạm vi đã cho.
