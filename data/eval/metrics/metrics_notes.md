# Metric evaluation — bước 4 (core set)

## Source of truth

| Vai trò           | File                                                 |
| ----------------- | ---------------------------------------------------- |
| Query & nhóm      | `data/eval/final_query_set_core.csv` (28 query)      |
| Nhãn relevance    | `data/eval/relevance_judgments_core.csv`             |
| Kết quả retrieval | `data/eval/results/baseline_*_core.csv` (5 baseline) |
| Script tính       | `data/eval/metrics/compute_core_metrics.py`          |

Không chỉnh sửa các file nguồn trên trong bước 4; chỉ đọc và xuất metric.

## Join key

- **Khóa ghép nhãn:** `(query_id, doc_id)` — kiểu chuỗi sau `strip`.
- **Ranking:** lấy từ cột `rank` trong mỗi file baseline; sort tăng dần `rank` để có thứ tự doc.

## Xử lý doc chưa có trong judgments (unjudged)

**Phương án A (đã chọn):** doc có trong kết quả retrieval nhưng **không** có cặp `(query_id, doc_id)` trong `relevance_judgments_core.csv` được coi **`relevance_label = 0`** (not relevant).

**Lý do:** Baseline đã chuẩn hóa top‑k doc/query; judgments core đã mở rộng cho đánh giá top‑k nhưng retrieval vẫn có thể trả doc ngoài tập đã chấm — gán 0 tránh overestimate và nhất quán với “không có nhãn trong judgment thì coi như không relevant”.

**Thống kê (tổng số cặp query–doc trong output, có trùng query):** nhiều dòng retrieval là doc **chưa được chấm** cho query đó (unjudged → 0). Ví dụ kiểm tra nhanh: lexical ~247/280 cặp là doc không nằm trong judgment cho query tương ứng — **điều này làm Precision/MRR của lexical rất thấp** vì top‑10 chủ yếu là 0 theo quy ước; không phải lỗi join.

## Quy ước relevance cho từng metric

| Metric            | Quy ước                                                                                                                                                                                                                                                                                                                                                                                                                  |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Precision@k**   | Nhị phân: doc **relevant** iff `relevance_label > 0`. \(P@k = \frac{1}{k}\sum\_{i=1}^{k} \mathbb{1}[\text{rel}_i > 0]\). Nếu ít hơn `k` doc trong danh sách, vẫn chia cho **k** (vị trí thiếu = không relevant).                                                                                                                                                                                                         |
| **Recall@5**      | \(R =\) số doc có nhãn `> 0` trong **toàn bộ** judgment của query. \(\text{Recall@5} = (\#\text{ relevant trong top-5}) / R\) khi **R > 0**. Khi **R = 0**: metric **không định nghĩa** — ghi **`NaN`** trong CSV per-query; **không** đưa query đó vào macro trung bình Recall@5 (summary và by-group cũng chỉ trung bình trên query có R > 0). Cách cũ (gán 1.0 khi R=0) đã **bỏ** vì làm đẹp số liệu sai phương pháp. |
| **MRR (summary)** | Trung bình **RR** theo query: \(\text{RR} = 1/\text{rank}\) của doc **đầu tiên** có `relevance_label > 0` (partially + very đều tính là “hit”); nếu không có doc nào >0 trong ranking → RR = 0.                                                                                                                                                                                                                          |
| **nDCG@k**        | Graded: nhãn **0, 1, 2** trực tiếp; gain \((2^{\text{rel}} - 1)\). DCG trên ranking retrieval (unjudged = 0). IDCG@k: lấy đa tập nhãn của query từ judgments, sort giảm dần, lấy **top k** nhãn làm ranking lý tưởng. Nếu IDCG = 0 → nDCG = **1.0** nếu DCG = 0, else **0.0**.                                                                                                                                           |

## Latency (bước 7 — đo riêng)

### Script

- `measure_core_baseline_latency.py` (project root): gọi trực tiếp các hàm `run_core_baselines.lexical_bm25_rows`, `vector_rows`, `vector_metadata_rows`, `ontology_sparql_rows`, `hybrid_rows` — **cùng pipeline** với bước 3, **không** ghi đè `baseline_*_core.csv`.

### Quy ước đo

| Hạng mục                              | Cách làm                                                                                                                                                                                                                                                                                                                       |
| ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Phạm vi (latency_scope)**           | Wall-clock **một lần gọi** builder cho một `query_id`: từ bắt đầu hàm đến khi trả về danh sách ~10 dòng kết quả (BM25 toàn chunk / FAISS+pool / KG+SPARQL+hybrid tùy baseline). **Không** tính: đọc CSV query, load SentenceTransformer, load FAISS index, parse OWL / `build_kg_index`, build BM25 corpus, đọc metadata xlsx. |
| **Warm-up**                           | Mỗi baseline: **1** lần gọi builder với **query đầu tiên** trong core set (không vào thống kê).                                                                                                                                                                                                                                |
| **Lặp**                               | Mỗi query: **5** lần đo; lấy **mean** → `mean_latency_ms` cho query đó.                                                                                                                                                                                                                                                        |
| **Tổng hợp baseline**                 | `mean_query_latency_ms` = trung bình các mean theo query; `median_query_latency_ms` = median của các mean theo query; min/max = trên tập mean-per-query.                                                                                                                                                                       |
| **Môi trường**                        | Một tiến trình Python; `stdout` của builder bị suppress khi đo để giảm nhiễu I/O. Ghi chú trong CSV: Windows, CPU (mặc định không ép GPU cho đoạn timing này trừ khi thư viện tự dùng).                                                                                                                                        |
| **Cấu hình hybrid / vector_metadata** | Giống `run_core_baselines.main`: tạm `FINAL_K=10`, `CANDIDATE_K=150`, khôi phục sau đo.                                                                                                                                                                                                                                        |

### So sánh vector vs vector_metadata (độ trễ)

- **vector**: `top_k = ntotal` (gần như toàn bộ chunk) → embedding + FAISS lớn.
- **vector_metadata** / **hybrid**: pool **150** chunk + rerank → thường **nhanh hơn vector thuần** trên cùng máy; đây là hệ quả đúng của pipeline, không phải lỗi đo.

### File đầu ra

- `baseline_latency_summary.csv`: một dòng / baseline + cột `latency_scope`, `runs_per_query`, v.v.
- `baseline_latency_per_query.csv`: mean và độ lệch chuẩn (5 run) theo từng `query_id`.

### Giới hạn

- Số tuyệt đối phụ thuộc máy, hệ điều hành, CPU/GPU, tải nền; chỉ nên so **tương đối** giữa baseline trên **cùng một lần chạy script**.
- Không đo latency mạng (chỉ local index).
- Bước 3 **vẫn không** ghi timing vào CSV baseline; timing chỉ nằm trong các file metrics ở trên.

## Kiểm tra R (số relevant trong judgment pool)

- Với mỗi `query_id` core: \(R = |\{doc : \text{judgment}(q,d) > 0\}|\).
- Đã kiểm tra trên `relevance_judgments_core.csv` trong repo (lần siết này): **không có** query core nào \(R=0\) — mỗi query đều có ít nhất một nhãn 1 hoặc 2. Nếu sau này có \(R=0\), `compute_core_metrics.py` in `[WARN]` khi chạy và Recall@5 macro chỉ trên query còn lại.

## Hạn chế

- **Macro-average (P@k, MRR, nDCG):** trung bình cộng theo **đủ 28** query.
- **Macro-average Recall@5:** chỉ trên query có **R > 0**; cột `notes` trong summary ghi `Recall@5 macro trên k/28 query (loại R=0: m)`.
- **vector_metadata:** một số query có **< 10** dòng trong CSV gốc; **Precision@k** vẫn chia cho **k** cố định (vị trí không có doc = không relevant).
- **Recall@5** phụ thuộc \(R\) trong pool đã chấm; pool nhỏ → recall dao động; **IDCG toàn 0** (mọi nhãn judgment = 0) vẫn xử lý nDCG như trước (khác với Recall).

## Vòng kỹ thuật cuối (chỉ hybrid + alias/entity trong `hybrid_search.py`)

- **Không** sửa ontology file, **không** sửa metadata xlsx, **không** sửa judgments.
- Hybrid: thêm `_intent_narrow_final_adjustment` (điều chỉnh điểm cuối cực hẹp theo intent) + siết alias (`fish diseases`, Thailand, `tom the`, canonicalize species/location).
- **vector_metadata** trong CSV baseline có thể đổi nhẹ vì cùng `detect_entities` / `build_term_index` với bước 3; lexical/vector không đổi công thức.

## Bước tiếp theo
