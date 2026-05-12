# Bước 5 — Phân tích lỗi và kế hoạch cải thiện cuối (chỉ đọc dữ liệu, không sửa pipeline)

Phân tích dựa trên metric bước 4, output retrieval bước 3, và judgments core. **Không** chạy lại retrieval, **không** sửa scoring/ontology/metadata/judgments/baseline CSV trong vòng này.

---

## 1. Input sources used

| Vai trò | Đường dẫn |
|---------|-----------|
| Query set (28) | `data/eval/final_query_set_core.csv` |
| Judgments + hướng dẫn | `data/eval/relevance_judgments_core.csv`, `data/eval/relevance_guidelines_core.md` |
| Retrieval | `data/eval/results/baseline_lexical_core.csv`, `baseline_vector_core.csv`, `baseline_vector_metadata_core.csv`, `baseline_ontology_sparql_core.csv`, `baseline_hybrid_core.csv` |
| Ghi chú sinh kết quả | `data/eval/results/results_generation_notes.md` |
| Metric | `data/eval/metrics/baseline_metrics_summary.csv`, `baseline_metrics_per_query.csv`, `baseline_metrics_by_group.csv`, `metrics_notes.md` |
| Ngữ cảnh (chỉ tham chiếu, không sửa) | `data/metadata/document_metadata_cleaned.xlsx`, `data/ontology/taxon_enriched_facts_v2.owl` |
| Bảng tổng hợp phụ (do bước 5 tạo) | `data/eval/analysis/baseline_strengths_by_group.csv`, `data/eval/analysis/query_failure_buckets.csv` |

Quy ước metric quan trọng: doc retrieval nhưng không có trong judgment → **rel = 0**; Recall@5 macro loại query \(R=0\) (không áp dụng core hiện tại vì mọi query đều \(R>0\)).

---

## 2. Overall metric reading

**Tổng thể (28 query, `baseline_metrics_summary.csv`):**

| Baseline | P@5 | Recall@5 | MRR | nDCG@10 |
|----------|-----|----------|-----|---------|
| lexical | 0.136 | 0.196 | 0.433 | 0.299 |
| vector | 0.336 | 0.416 | 0.769 | 0.602 |
| vector_metadata | 0.364 | 0.453 | 0.798 | 0.641 |
| ontology_sparql | 0.343 | 0.389 | 0.645 | 0.458 |
| **hybrid** | **0.386** | **0.473** | **0.808** | **0.676** |

**Nhận định ngắn:**

- **Hybrid** là baseline **mạnh nhất toàn cục** trên P@5, Recall@5, MRR, nDCG@10 trong snapshot này.
- **vector_metadata** đứng thứ hai, chênh hybrid vừa phải — hybrid chủ yếu “cộng thêm” tín hiệu KG/rerank trên nền embedding + metadata.
- **Ontology/SPARQL** trung bình thấp hơn embedding nhưng **nhóm disease-specific** (theo by-group) lại **cao nhất về nDCG@10**.
- **Lexical** bị penalize mạnh do **unjudged → 0**: nhiều doc top-10 không nằm trong pool judgment, nên P/MRR macro không phản ánh đúng “chất lượng BM25 thuần” so với embedding; vẫn hữu ích khi so **nhóm local** (xem mục 4).

**Hybrid so với vector / vector_metadata:**

- Macro: hybrid > vector_metadata > vector trên hầu hết cột; khoảng cách hybrid–vector_metadata nhỏ hơn hybrid–vector → **phần lớn lợi thế đến từ embedding + metadata**, KG/rerank là **lớp tinh chỉnh**.
- Per-query: có vài query hybrid **kém hơn vector** (ví dụ **LO_007**, **SL_004**, **HM_001**) — cần xem là **rerank/KG đẩy sai doc đầu bảng** hoặc **khớp metadata lệch intent**.

---

## 3. Baseline-by-baseline analysis

### 3.1 Lexical (BM25)

- **Mạnh:** Nhóm **local** — macro nDCG@10 lexical **0.746** cao hơn hybrid **0.699** và vector **0.673** (`baseline_metrics_by_group.csv`). Token tiếng Việt, địa danh, cụm cố định trong query khớp literal tốt; ví dụ **LO_007** có P@1=1, nDCG@10 cao với lexical.
- **Yếu:** **biosecurity-management** (nDCG gần 0), **hatchery-production-mode** (toàn 0 macro) — từ khóa tiếng Anh/tổng quát hoặc doc top không nằm trong judgment pool làm điểm sụt; **species-location** trung bình thấp.
- **Nguyên nhân kỹ thuật:** (1) **candidate pool + unjudged** làm precision macro nghiệt ngã; (2) query **ngắn/không trùng từ vựng** title; (3) **đa ngôn ngữ** — query Việt vs doc tiếng Anh.

### 3.2 Vector (dense)

- **Mạnh:** Ổn định đa nhóm; **semantic paraphrase** (surveillance/zoning, disease alias tiếng Anh) tốt hơn lexical khi không trùng từ.
- **Yếu:** **Fine-grained constraints** — quốc gia (**Philippines** vs manual AHPND toàn cầu), **mode** (broodstock/hatchery vs grow-out manual), **Latin America hatchery** khi embedding nhầm sang monodon/Ấn Độ.
- **Ví dụ:** **DS_010** rank-1 **FAO_001** (rel 1 — đúng bệnh, thiếu sâu Philippines); **HM_010** rank-1 **FAO_002** monodon Ấn Độ (lệch loài/intent); **SL_007** nDCG@10 rất thấp do ranking sai **FAO_005** (gold).

### 3.3 Vector + metadata (`vector_metadata`)

- **Thêm được so với vector:** Rerank theo **metadata_delta** giúp các query cần **location, production_mode, taxon** trong sheet — ví dụ **SL_007** đưa **FAO_005** lên rank-1 (trùng judgment rel 2); **HM_010** cải thiện mạnh P@1 và nDCG so với vector thuần.
- **Hạn chế:** Khi metadata **không lột tả intent** (ví dụ “low water exchange Thailand” vs doc AHPND Thailand), vector+metadata vẫn **không thay thế** được nhãn very_relevant đúng (**FAO_008** cho **SL_004**).

### 3.4 Ontology / SPARQL

- **Mạnh:** Query **disease-centric** có entity bệnh/taxon/location khớp KG — nhóm **disease-specific** nDCG@10 **0.663** (cao nhất trong nhóm đó). **DS_010:** rank-1 **SEAFDEC_006** (rel 2) — đúng Philippines + AHPND.
- **Yếu:** Query **quản lý/surveillance/PMP** không map sang fact density trong KG — **BI_003:** nhiều doc **score_raw = 0**, thứ tự gần **lexicographic/doc-id**, rank-1 **FAO_001** (rel 0). **LO_007:** ontology gần như không hit (MRR ~0 trong per-query).
- **Nguyên nhân:** **SPARQL sparsity**; entity linking lệch sang **disease default** (AHPND chain) thay vì **management concepts**; thiếu **document-level facts** cho chủ đề governance.

### 3.5 Hybrid (embedding + metadata + KG rerank)

- **Thật sự hơn vector/vector_metadata khi:** KG **phạt/ghi điểm** đúng trục — **DS_010** đẩy **SEAFDEC_006** lên #1; **HM_010** đẩy **PMC_031** (broodstock/PL/probiotic) lên #1; **LO_002** đẩy **TB_005** (ĐBSCL surveillance) lên #1 thay vì **TCKHTS_001** (Hà Tĩnh) ở vector.
- **Gần vector_metadata khi:** Cùng top doc và thứ tự — **BI_003** metric **y hệt** vector và vector_metadata (nDCG@10 = 0.797); **SL_007** cùng **FAO_005** #1 với VM; điểm hybrid chỉ khác nhẹ do cộng hưởng score.
- **Rủi ro:** Rerank **đảo top sai** — **LO_007** vector #1 **TCTS_001** (rel 2) → hybrid #1 **TB_002** (không phải gold theo judgment); **HM_001** vector P@1=1, hybrid P@1=0; **SL_004** vector nDCG@10 **0.528** > hybrid **0.363**.

---

## 4. Query-group analysis

Tóm tắt từ `baseline_metrics_by_group.csv` và bảng phụ `baseline_strengths_by_group.csv`.

| Nhóm | n | Tốt nhất (nDCG@10) | Hybrid (nDCG@10) | Hybrid có thắng rõ nhóm? | Nguyên nhân kỹ thuật chính |
|------|---|-------------------|------------------|---------------------------|----------------------------|
| **disease-specific** | 6 | **ontology_sparql** (0.663) | 0.616 | Không (ontology hơn hybrid) | KG khớp **bệnh + vùng** tốt; embedding đôi khi **ưu tiên manual chung** hơn **báo cáo quốc gia** |
| **species-location** | 5 | **vector_metadata** (0.707) | 0.702 (gần tie) | Gần tie | **Metadata** (region, mode, taxon) cứu vector; vẫn lỗi khi **practice keyword** (low water exchange) không khớp metadata |
| **hatchery-production-mode** | 4 | **hybrid** (0.627) | 0.627 | Có (tie VM sát) | **HM_010** hybrid/VM cứu được query khó; lexical = 0 |
| **biosecurity-management** | 6 | **hybrid** (0.719) | 0.719 | Nhẹ vs vector (0.712) | Embedding dominant; ontology **rất yếu** (0.144) |
| **local** | 7 | **lexical** (0.746) | 0.699 | Không (lexical > hybrid macro nhóm) | **Tiếng Việt + địa danh**; rerank đôi khi **phá** top đúng (LO_007) |

---

## 5. Representative query cases

### 5.1 Nhóm **hybrid thắng rõ** (so với vector, căn cứ retrieval + per-query metric)

| Query | Diễn giải ngắn | Vector (điểm yếu) | Hybrid (cải thiện) | Judgment |
|-------|----------------|-------------------|-------------------|----------|
| **DS_010** | AHPND + Philippines | #1 **FAO_001** (rel 1) | #1 **SEAFDEC_006** (rel 2) | Country status > generic manual |
| **HM_010** | Broodstock, PL, probiotics | #1 **FAO_002** monodon Ấn Độ | #1 **PMC_031** (rel 2) | Đúng vannamei + hatchery + probiotic |
| **LO_002** | WSSV/AHPND/EHP ĐBSCL | #1 **TCKHTS_001** Hà Tĩnh (rel 1) | #1 **TB_005** (rel 2) | Đúng vùng ĐBSCL + khảo sát |
| **SL_007** | Latin America white shrimp hatchery | Top không có **FAO_005** sớm / nDCG thấp | #1 **FAO_005** (rel 2), giống VM | Metadata + rerank cứu region+hatchery |

*(Chỉ số: **DS_010** nDCG@10 vector 0.388 → hybrid 0.719; **HM_010** 0.197 → 0.583; **SL_007** 0.161 → 0.788 — từ `baseline_metrics_per_query.csv`.)*

### 5.2 Nhóm **hybrid chỉ giữ ổn / gần vector_metadata**

| Query | Ghi chú |
|-------|---------|
| **BI_003** | Vector/hybrid/VM **cùng** top **FAO_013** (rel 2); ontology baseline **không** tận dụng được (rank-1 rel 0). Hybrid không thêm gain số học. |

### 5.3 Nhóm **hybrid chưa tạo gain / tệ hơn vector**

| Query | Hiện tượng | Giải thích kỹ thuật |
|-------|------------|---------------------|
| **LO_007** | Vector #1 **TCTS_001** (gold); hybrid #1 **TB_002** | Rerank/entity **ưu tiên sai** nguồn/extension vs sổ tay TCTS |
| **SL_004** | nDCG@10 vector **0.528** > hybrid **0.363** | **Intent** “low water exchange Thailand” (**FAO_008**) bị **AHPND Thailand** và doc khác chen; KG/metadata không cứu, có thể làm lệch thêm |
| **HM_001** | Vector P@1=1; hybrid P@1=0 | Query “production mode hatchery” đơn giản — **rerank làm mất hit đầu** |

---

## 6. Error buckets / failure modes

| Bucket | Mô tả | Ví dụ / dấu hiệu |
|--------|--------|------------------|
| **A. Candidate pool / unjudged** | Top retrieval là doc **ngoài judgment** → rel 0; làm sụt precision macro, đặc biệt lexical | Nhiều dòng `unjudged_in_ranking` trong per-query; lexical bio ~0 |
| **B. Semantic gần nhưng sai ràng buộc** | Embedding khớp **bệnh/ tôm** nhưng sai **quốc gia, mode, loài** | DS_010 vector; HM_010 vector; SL_007 vector |
| **C. Metadata đủ/không đủ** | VM/hybrid tốt khi sheet có **location/mode/taxon**; hạn chế khi intent là **kỹ thuật ao** chưa có cột | SL_007 (đủ); SL_004 (thiếu/không lấy đúng FAO_008) |
| **D. Ontology: có entity, thiếu fact / sai intent** | KG mạnh **disease chain**, yếu **surveillance, PMP, risk framework** | BI_003 ontology top FAO_001 vs gold FAO_013 |
| **E. SPARQL sparsity / tie-break** | `score_raw` 0 hoặc tie, ranking gần arbitrary | BI_003 ontology (0.0 scores) |
| **F. Location / alias** | Philippines, ĐBSCL, Latin America — cần **cả** embedding và KG; khi một kênh sai thì phải nhờ kênh kia | DS_010, LO_002, SL_007 |
| **G. Hatchery / PL / probiotic** | Từ khóa hẹp, nhiều paper AHPND generic; **PMC** vs **FAO manual** | HM_010 |
| **H. Query intent ambiguity / judgment sắc** | “Đúng nguồn TCTS” vs “đúng chủ đề khuyến nông” — rerank không biết trọng số nguồn | LO_007 |
| **I. Hybrid rerank regression** | KG/metadata **overweight** làm **đảo** top đúng của vector | LO_007, HM_001, SL_004 |

Chi tiết map query → bucket: `data/eval/analysis/query_failure_buckets.csv`.

---

## 7. Final prioritized improvement plan

### Ưu tiên 1 — Nên làm **sớm**, tương đối **an toàn** (sau bước 6, khi được phép sửa code/pipeline)

1. **Kiểm soát rerank hybrid** khi vector đã có **hit rel 2 cực cao** ở #1 (ví dụ near-duplicate title với query): tránh case **LO_007**; có thể **cap** độ lệch score hoặc **trust vector top-1** nếu margin lớn.
2. **Giám sát per-query regression tests** (DS_010, HM_010, LO_002, SL_007 positive; LO_007, HM_001, SL_004 negative) trước khi đổi trọng số.
3. **Mở rộng / kiểm tra judgment pool** cho lexical top-doc (không sửa trong vòng này) — hiểu đúng giới hạn metric; tránh quyết định chỉ từ macro P@k khi unjudged cao.
4. **Document-level coverage notes** cho doc “trụ cột” (SEAFDEC Philippines, FAO_008 Thailand, TB_005): đảm bảo KG hoặc chunk index **có fact** khớp query (khi được phép sửa ontology/metadata).

### Ưu tiên 2 — Có ích nhưng **cần cẩn trọng**

1. **Tinh chỉnh entity linking** cho intent **management** (surveillance, zoning) vs **disease** — giảm BI_003-style ontology noise; tránh boost AHPND mặc định.
2. **Location token map** có kiểm soát (Philippines, Thailand practices, Latin America) — bổ sung alias/fact **có validation** để tránh false positive vùng.
3. **Ontology/SPARQL path** cho query **structured disease+geo**: giữ làm **kênh phụ** hoặc **feature** trong hybrid thay vì baseline độc lập nếu UX cần đơn giản.
4. **vector_metadata** gần hybrid trên nhiều query — mọi thay đổi KG nên đo **cả** VM và hybrid để tránh “chỉ win trên một graph”.

### Ưu tiên 3 — **Chưa nên** hoặc rủi ro cao / ROI thấp

1. **Heuristic mạnh tay** boost theo từ khóa đơn (ví dụ chỉ “Philippines”) — dễ **false positive** trên doc đa quốc gia.
2. **Thay đổi lớn ontology** chỉ để sửa vài query **surveillance** nếu chưa có tài liệu học thuật map — dễ drift semantic.
3. **Coi lexical macro thấp = BM25 vô dụng** — nhóm local cho thấy lexical vẫn **competitive**; quyết định loại bỏ BM25 là **sớm**.
4. **Tối ưu chỉ Recall@5** khi pool judgment nhỏ — metric nhạy nhiễu; ưu tiên **nDCG graded** + case studies.

---

## 8. What should be changed next vs what should not be changed yet

| Nên làm tiếp (bước 6+, khi được phép) | Chưa nên đụng vội |
|----------------------------------------|-------------------|
| Điều chỉnh **trọng số rerank / fusion** có kiểm chứng regression | Đổi **ontology** lớn không có baseline ablation |
| **Instrument latency** nếu báo cáo cần | Sửa **judgments** để “đẹp số” macro |
| **Feature flags** cho KG path theo loại query (disease vs management) | Heuristic từ khóa cứng tràn lan |
| Bổ sung **evaluation notes** vào báo cáo (không thay Word trong bước 5) | Xóa lexical khỏi pipeline chỉ vì macro thấp |

---

## Độ đủ của phân tích

Phân tích này **đủ để chốt hướng cải thiện cuối** ở mức **ưu tiên và rủi ro**, dựa trên metric chính thức, by-group, và đối chiếu retrieval + judgment trên các query tiêu biểu. Triển khai cụ thể (code, trọng số, ontology patch) thuộc **bước 6** — **chưa thực hiện trong vòng này**.

**Xác nhận phạm vi vòng 5:** **CHƯA** sửa ontology, **CHƯA** sửa metadata, **CHƯA** sửa scoring, **CHƯA** sửa judgments, **CHƯA** chạy lại retrieval, **CHƯA** chỉnh báo cáo Word — chỉ đọc, phân tích, và xuất file trong `data/eval/analysis/`.
