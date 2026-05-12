# Baseline results generation (bước 3)

## Đã chạy
- Script: `run_core_baselines.py` (project root).
- Query: `data/eval/final_query_set_core.csv` (28 query).
- Metadata titles: `data/metadata/document_metadata_cleaned.xlsx`.
- Vector index: `vector_store/chunks.index` + config; chunks list BM25: `vector_store/chunks_meta.pkl` (phải cùng corpus build).

## Lexical
- **BM25 Okapi** trên token sau `hybrid_search.normalize_text`, corpus = toàn bộ chunk text.
- Mỗi query: tính BM25 cho **mọi** chunk, rồi **max-pool** theo `doc_id` (điểm doc = max điểm chunk thuộc doc), sắp xếp doc theo điểm sau pool, lấy top 10. **Không** cắt trước ở top-N chunk (tránh dồn hết top chunk vào vài tài liệu dài).
- `retrieval_level`: `chunk_to_doc`.

## Vector
- `vector_search.search` — embedding `paraphrase-multilingual-MiniLM-L12-v2`, FAISS `IndexFlatIP`, vector L2-normalized.
- Mỗi query: `top_k = ntotal` (số vector trong index, thường bằng số chunk), cùng công thức similarity; sau đó max-pool theo doc như lexical, top 10.
- Không metadata, không KG.

## Vector + metadata
- Cùng pool ứng viên vector với hybrid ở mức **CANDIDATE_K** chunk + optional lobster English boost query (copy logic `hybrid_search`).
- Điểm = `vector_score + metadata_delta` với `compute_match_features` + `compute_hybrid_delta` từ `hybrid_search`.
- **Không** gọi `link_query_entities_kg` / **không** merge KG entities — chỉ `detect_entities(term_index)` (regex + từ điển metadata).
- Intent penalty nuôi địa phương: copy logic `_narrow_local_aquaculture_intent` + phạt capture/market khi có doc aquaculture trong pool.

## Ontology / SPARQL
- Nạp đồ thị như hybrid (`hybrid_search._init_kg_if_needed`).
- `kg_runtime.link_query_entities_kg` → tập URI; SPARQL `COUNT DISTINCT ?p` với `?doc ?p ?target` và `?p` ∈ {aboutDisease, aboutTaxon, aboutLocation, documentProductionMode}.
- `score_raw` = `kg_score` ( `score_doc_with_kg` ) + boost nhỏ 0.001 × (SPARQL hit count) để phá hòa; `retrieval_level`: `kg_structured`.
- Query không bắt được entity: vẫn xếp toàn corpus theo `kg_score` (thường thấp / âm).

## Hybrid
- `hybrid_search.hybrid_search`. Runtime tạm set `FINAL_K=10` và `CANDIDATE_K=150` (mặc định repo `FINAL_K=5`, `CANDIDATE_K=10`) để pool chunk đủ đa dạng doc khi xuất top-10; khôi phục sau chạy.
- `final_score = vector_score + metadata_delta + kg_score + intent_adjustment`; `intent_adjustment` là lớp guardrail cực hẹp (vòng kỹ thuật cuối), xem `hybrid_search._intent_narrow_final_adjustment`.

## score_normalized
- Trên tập **top doc đã xuất của từng query**, min–max trên `score_raw` → [0,1] (doc tốt nhất ~1). Nếu mọi điểm bằng nhau → toàn 1.

## Giới hạn
- Hybrid / vector_metadata xét doc trong pool tới **2×CANDIDATE_K** chunk (run này `CANDIDATE_K=150` tạm thời); vẫn có thể <10 doc nếu corpus/index ít chunk/doc đa dạng.
- Lexical / vector: đã dùng **toàn bộ chunk** cho điểm trước max-pool → mỗi query có đủ **10 doc** miễn là chỉ mục có ≥10 `doc_id` khác nhau (corpus hiện tại đạt).
- Ontology: query tự nhiên không khớp alias KG → SPARQL rỗng, xếp hạng chủ yếu từ `kg_score` / mapping URI.

## Metric
- **Chưa** tính P@k, Recall, MRR, nDCG (bước 4).
