# Explanation quality diagnostic report

Generated at: `2026-05-29`

## 1. Mục tiêu

Đánh giá này là automatic explanation diagnostic cho hệ thống hybrid search trong project Aquaculture Semantic Search. Mục tiêu là đo coverage của explanation và các loại evidence xuất hiện trong kết quả Top-k, gồm entity match, metadata evidence và KG evidence. Đây không phải user study, không phải đánh giá chuyên gia thủ công, và không thay thế các metric retrieval như P@k, Recall@k, MRR, nDCG hoặc MAP.

## 2. Dữ liệu và phương pháp

- Query set: `data/eval/final_query_set_core.csv`.
- Số query core: `28`.
- Top-k: `10`.
- Relevance judgments: `data/eval/relevance_judgments_core.csv` (Đã join relevance judgments theo query_id + doc_id.)
- KG diagnostic input nếu có: `outputs/kg_score_component_analysis.csv`.
- Query understanding profile nếu có: `outputs/query_understanding_profiles.csv`.
- Source mode: `runtime_recomputed`.

Script `experiments/evaluate_explanation_quality.py` ưu tiên tái chạy nhẹ `hybrid_search.hybrid_search()` trên 28 core queries để lấy runtime fields như `explanation`, `metadata_delta`, `kg_score`, `intent_adjustment`, `bonus_breakdown`, `kg_explanation` và match flags. Việc tái chạy này chỉ phục vụ explanation diagnostic, không overwrite `baseline_hybrid_core.csv`, không tạo baseline metric mới và không sửa runtime/scoring. Nếu runtime import hoặc recomputation lỗi, script fallback sang `baseline_hybrid_core.csv` kết hợp `kg_score_component_analysis.csv`.

Cách xác định evidence:

- `has_explanation`: explanation text hoặc KG explanation không rỗng.
- `has_entity_match`: có match flag disease/species/location/mode, metadata/KG evidence, hoặc explanation nhắc entity/fact/relation.
- `has_metadata_evidence`: `metadata_delta > 0`, có `bonus_breakdown`, hoặc explanation nhắc metadata/entity match.
- `has_kg_evidence`: `kg_score > 0`, `kg_explanation` không rỗng, hoặc KG diagnostic cho thấy direct/relation/context/explanation evidence.
- `has_kg_relation_or_fact`: ưu tiên cột direct/relation evidence trong `kg_score_component_analysis.csv`; nếu thiếu thì suy từ KG explanation/fact/relation keywords.

## 3. Chỉ số diagnostic

- `has_explanation_rate`: tỷ lệ result rows có explanation text.
- `top1_has_explanation_rate`: tỷ lệ Top-1 của mỗi query có explanation.
- `query_has_any_explanation_rate`: tỷ lệ query có ít nhất một result trong Top-k có explanation.
- `has_entity_match_rate`: tỷ lệ result rows có entity match hoặc evidence cho entity match.
- `has_metadata_evidence_rate`: tỷ lệ result rows có metadata evidence.
- `has_kg_evidence_rate`: tỷ lệ result rows có KG evidence.
- `has_kg_relation_or_fact_rate`: tỷ lệ result rows có KG fact hoặc relation/context evidence.
- `mean_explanation_length`: độ dài trung bình của explanation text ở các row có explanation.
- `mean_evidence_count`: số mảnh evidence trung bình tách từ explanation/breakdown theo dấu `;`, newline hoặc `|`.

## 4. Kết quả tổng thể

| scope | n_queries | n_rows | top_k | has_explanation_rate | top1_has_explanation_rate | query_has_any_explanation_rate | has_entity_match_rate | has_metadata_evidence_rate | has_kg_evidence_rate | has_kg_relation_or_fact_rate | mean_explanation_length | mean_evidence_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| core_hybrid_top10 | 28 | 280 | 10 | 1.000 | 1.000 | 1.000 | 0.707 | 0.707 | 0.564 | 0.564 | 192.514 | 9.729 |

Relevance-aware diagnostic:

| label | n_rows | has_explanation_rate | has_metadata_evidence_rate | has_kg_evidence_rate |
| --- | --- | --- | --- | --- |
| 0 | 14 | 1.000 | 0.643 | 0.500 |
| 1 | 27 | 1.000 | 0.815 | 0.630 |
| 2 | 48 | 1.000 | 0.875 | 0.729 |

## 5. Kết quả theo nhóm truy vấn

| query_group | n_queries | n_rows | has_explanation_rate | top1_has_explanation_rate | query_has_any_explanation_rate | has_entity_match_rate | has_metadata_evidence_rate | has_kg_evidence_rate | has_kg_relation_or_fact_rate | mean_explanation_length |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| biosecurity-management | 6 | 60 | 1.000 | 1.000 | 1.000 | 0.500 | 0.500 | 0.500 | 0.500 | 94.850 |
| disease-specific | 6 | 60 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.900 | 0.900 | 290.500 |
| hatchery-production-mode | 4 | 40 | 1.000 | 1.000 | 1.000 | 0.825 | 0.825 | 0.500 | 0.500 | 152.925 |
| local | 7 | 70 | 1.000 | 1.000 | 1.000 | 0.457 | 0.457 | 0.371 | 0.371 | 236.086 |
| species-location | 5 | 50 | 1.000 | 1.000 | 1.000 | 0.860 | 0.860 | 0.560 | 0.560 | 162.800 |

Nhận xét theo dữ liệu thực tế: Tất cả nhóm truy vấn đều đạt `has_explanation_rate=1.000` trong diagnostic này. Nhóm có `has_kg_evidence_rate` cao nhất là `disease-specific` với giá trị `0.900`. Các khác biệt này phản ánh mức độ KG/metadata evidence có sẵn trong runtime hiện tại, không phải đánh giá cuối cùng về chất lượng ngôn ngữ của explanation.

## 6. Ví dụ explanation tiêu biểu

- `good` | `DS_001` | query: bệnh AHPND trên tôm | doc: `TB_005` - Sự hiện diện của bệnh đốm trắng, hoại tử gan tụy cấp và vi bào tử trùng trên tôm giống và tôm nuôi thương phẩm tại một số tỉnh khu vực ĐBSCL từ năm 2022-2024 | label: 2
  Evidence: metadata: match disease query=AHPND with doc_term=AHPND (+0.35); KG: KG direct match: document aboutDisease=Bệnh hoại tử gan tụy cấp; KG relation match: Bệnh hoại tử gan tụy cấp affectsTaxon Tôm sú, and document aboutTaxon=Tôm sú; KG relation match: Bệnh hoại tử gan tụy cấp causedBy Vi khuẩn Vibrio parahaemolyticus, and document has pathogen=Vi khuẩn Vibrio parahaemolyticus; KG direct match: document aboutDisease=Bệnh hoại tử gan tụy cấp
  Explanation: metadata: match disease query=AHPND with doc_term=AHPND (+0.35); KG: KG direct match: document aboutDisease=Bệnh hoại tử gan tụy cấp; KG relation match: Bệnh hoại tử gan tụy cấp affectsTaxon Tôm sú, and document aboutTaxon=Tôm sú; KG relation match: Bệnh hoại tử gan tụy cấp causedBy Vi khuẩn Vibrio parahaemolyticus, and document has pathogen=Vi khuẩn Vibrio parahaemolyticus
- `good` | `DS_001` | query: bệnh AHPND trên tôm | doc: `FAO_001` - Shrimp acute hepatopancreatic necrosis disease strategy manual | label: 2
  Evidence: metadata: match disease query=AHPND with doc_term=AHPND (+0.35); KG: KG direct match: document aboutDisease=Bệnh hoại tử gan tụy cấp; KG relation match: Bệnh hoại tử gan tụy cấp affectsTaxon Tôm sú, and document aboutTaxon=Tôm sú; KG relation match: Bệnh hoại tử gan tụy cấp causedBy Vi khuẩn Vibrio parahaemolyticus, and document has pathogen=Vi khuẩn Vibrio parahaemolyticus; KG direct match: document aboutDisease=Bệnh hoại tử gan tụy cấp
  Explanation: metadata: match disease query=AHPND with doc_term=AHPND (+0.35); KG: KG direct match: document aboutDisease=Bệnh hoại tử gan tụy cấp; KG relation match: Bệnh hoại tử gan tụy cấp affectsTaxon Tôm sú, and document aboutTaxon=Tôm sú; KG relation match: Bệnh hoại tử gan tụy cấp causedBy Vi khuẩn Vibrio parahaemolyticus, and document has pathogen=Vi khuẩn Vibrio parahaemolyticus
- `good` | `LO_001` | query: nuôi tôm hùm ở Khánh Hòa | doc: `RIA3_001` - Quy hoạch nuôi tôm hùm đến năm 2020 và định hướng đến 2030 | label: 2
  Evidence: metadata: match species query=lobster with doc_term=lobster (+0.22); match location query=Khanh Hoa with doc_term=Khánh Hòa (+0.08); species-location synergy (+0.05); KG: KG direct match: document aboutTaxon=Tôm hùm bông; KG direct match: document aboutLocation=Ven biển Khánh Hòa
  Explanation: metadata: match species query=lobster with doc_term=lobster (+0.22); match location query=Khanh Hoa with doc_term=Khánh Hòa (+0.08); species-location synergy (+0.05); KG: KG direct match: document aboutTaxon=Tôm hùm bông; KG direct match: document aboutLocation=Ven biển Khánh Hòa; KG relation match: Tôm hùm bông isFoundIn Ven biển Khánh Hòa, query location matches species range
- `good` | `LO_001` | query: nuôi tôm hùm ở Khánh Hòa | doc: `FAO_015` - FAO species catalogue. Vol.13. Marine lobsters of the world. An annotated and illustrated catalogue of marine lobsters known to date | label: 1
  Evidence: metadata: match species query=lobster with doc_term=lobster (+0.22); KG: KG direct match: document aboutTaxon=Tôm hùm bông; KG relation match: Tôm hùm bông isFoundIn Ven biển Khánh Hòa, query location matches species range; KG penalty: query expresses aquaculture (nuoi) in a regional site; document production mode is capture/market fisheries (Generic_CaptureFisheries)
  Explanation: metadata: match species query=lobster with doc_term=lobster (+0.22); KG: KG direct match: document aboutTaxon=Tôm hùm bông; KG relation match: Tôm hùm bông isFoundIn Ven biển Khánh Hòa, query location matches species range; KG penalty: query expresses aquaculture (nuoi) in a regional site; document production mode is capture/market fisheries (Generic_CaptureFisheries); intent penalty: local aquaculture query vs ca...
- `good` | `LO_004` | query: quy hoạch phát triển nuôi tôm hùm Khánh Hòa đến 2030 | doc: `RIA3_001` - Quy hoạch nuôi tôm hùm đến năm 2020 và định hướng đến 2030 | label: 2
  Evidence: metadata: match species query=lobster with doc_term=lobster (+0.22); match location query=Khanh Hoa with doc_term=Khánh Hòa (+0.08); species-location synergy (+0.05); KG: KG direct match: document aboutTaxon=Tôm hùm bông; KG direct match: document aboutLocation=Ven biển Khánh Hòa
  Explanation: metadata: match species query=lobster with doc_term=lobster (+0.22); match location query=Khanh Hoa with doc_term=Khánh Hòa (+0.08); species-location synergy (+0.05); KG: KG direct match: document aboutTaxon=Tôm hùm bông; KG direct match: document aboutLocation=Ven biển Khánh Hòa; KG relation match: Tôm hùm bông isFoundIn Ven biển Khánh Hòa, query location matches species range

File ví dụ đầy đủ: `outputs/explanation_quality_examples.csv`.

## 7. Hạn chế

- Đây là đánh giá tự động/rule-based, chưa có người dùng hoặc chuyên gia chấm explanation theo thang 1-5.
- Explanation coverage không đồng nghĩa explanation luôn đúng hoàn toàn.
- Chất lượng explanation phụ thuộc vào metadata, KG fact coverage, alias coverage, entity linking và runtime evidence.
- Nếu baseline CSV không lưu full component thì một số evidence được tái tính hoặc suy ra từ runtime hiện tại.
- Chưa đánh giá sâu tính dễ hiểu, tính thuyết phục hoặc khả năng hỗ trợ ra quyết định bằng human evaluation.
- Các chỉ số ở đây không phải retrieval metrics mới và không thay thế kết quả evaluation chính.

## 8. Đoạn có thể chèn vào báo cáo

Để bổ sung đánh giá khả năng giải thích của hệ thống, đề tài thực hiện một automatic explanation diagnostic trên 28 truy vấn core và kết quả hybrid Top-10. Đánh giá này đo tỷ lệ kết quả có explanation, có entity match, có metadata evidence, có KG evidence và có KG fact/relation evidence. Kết quả tổng thể cho thấy `has_explanation_rate` đạt `1.000`, `top1_has_explanation_rate` đạt `1.000`, và `query_has_any_explanation_rate` đạt `1.000`. Tỷ lệ metadata evidence là `0.707`, trong khi tỷ lệ KG evidence là `0.564` và KG fact/relation evidence là `0.564`. Các kết quả này cho thấy explanation có thể minh họa vai trò của metadata và Knowledge Graph trong quá trình reranking của hybrid search. Tuy nhiên, đây chỉ là đánh giá tự động dựa trên rule và runtime evidence, không phải user study hoặc đánh giá chuyên gia. Vì vậy, kết quả chỉ nên được dùng như phân tích bổ trợ trong Chương 4; nếu phát triển thành nghiên cứu lớn hơn, cần bổ sung human evaluation về tính đúng, dễ hiểu và hữu ích của explanation.

## 9. Caption hình đề xuất

Hình 4.x. Đánh giá diagnostic khả năng explanation của hệ thống hybrid search.

Figure path: `outputs/figures/fig_explanation_quality_summary.png`.

## 10. Safety confirmation

- Không sửa runtime/scoring.
- Không sửa `hybrid_search.py`, `kg_runtime.py`, `vector_search.py`, `run_core_baselines.py`.
- Không sửa `app_streamlit.py`.
- Không sửa ontology/metadata/query set/relevance judgments.
- Không sửa baseline results hoặc metrics cũ.
- Không overwrite baseline CSV cũ.
- Output mới chỉ là diagnostic explanation report.

## 11. Script warnings

Không có warning nghiêm trọng.
