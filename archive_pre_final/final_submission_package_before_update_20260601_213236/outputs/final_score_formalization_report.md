# Final score formalization report

Generated at: `2026-05-29`

Report này formal hóa công thức `final_score` và cách diễn giải `kg_score`/KG evidence trong hybrid search của project Aquaculture Semantic Search. Nội dung dưới đây chỉ dựa trên code và output hiện có; không chạy lại experiment, không tạo metric mới và không chỉnh runtime/scoring.

## 1. Files inspected

Các file đã đọc/kiểm tra:

- `hybrid_search.py`
- `kg_runtime.py`
- `vector_search.py`
- `run_core_baselines.py`
- `app_streamlit.py`
- `outputs/final_score_formula_and_runtime_flow.md`
- `outputs/kg_score_component_analysis.md`
- `outputs/kg_ablation_analysis.md`
- `outputs/kg_score_component_analysis.csv`
- `outputs/wilcoxon_hybrid_vs_vector_metadata.md`
- `data/eval/results/baseline_hybrid_core.csv`
- `data/eval/results/kg_ablation_results_core.csv`
- `data/eval/results/baseline_vector_metadata_kg_no_intent_core.csv`

File trace đi kèm được tạo mới:

- `outputs/final_score_component_trace.csv`

## 2. Runtime scoring components found

### `vector_score`

`vector_score` bắt nguồn từ `vector_search.search()` trong `vector_search.py`. Query được encode bằng SentenceTransformer với `normalize_embeddings=True`; FAISS dùng `IndexFlatIP`, nên score là inner product giữa embedding đã normalize, tương đương cosine similarity trong thiết lập này. Trong `hybrid_search.hybrid_search()`, giá trị `item["score"]` từ vector candidate được copy sang `new_item["vector_score"]`.

Vị trí chính:

- `vector_search.py:194-209`: encode query, gọi `index.search()`, ghi `rec["score"]`.
- `hybrid_search.py:1205` và `1217`: đọc `item["score"]` thành `vector_score`.

Trong Streamlit demo, component này có hiển thị ở bảng Top-k và score boxes (`app_streamlit.py:164-168`, `270-276`). Trong `baseline_hybrid_core.csv`, component này không được lưu riêng; nó chỉ được gộp vào `score_raw`.

### `metadata_delta`

`metadata_delta` là điểm cộng/trừ từ metadata matching. Trong code, hàm `compute_hybrid_delta()` trả về key tên `kg_delta`, nhưng trong runtime item nó được ghi thành `metadata_delta` và `kg_bonus` vì lịch sử đặt tên. Về mặt báo cáo, nên gọi là `metadata_delta`, không gọi là KG score.

Vị trí chính:

- `hybrid_search.py:731-789`: `compute_match_features()` so khớp query entities với metadata document.
- `hybrid_search.py:792-888`: `compute_hybrid_delta()` tính delta theo query profile.
- `hybrid_search.py:1206`, `1218-1219`: đọc `delta_info["kg_delta"]`, ghi `metadata_delta` và legacy `kg_bonus`.

Trong Streamlit demo, `metadata_delta` được hiển thị. Trong `baseline_hybrid_core.csv`, component này không được lưu riêng; nó chỉ được gộp vào `score_raw`.

### `kg_score`

`kg_score` là điểm KG runtime thực sự được dùng trong ranking. Trong `hybrid_search.py`, mỗi `doc_id` được map sang KG document URI nếu có, lấy document facts bằng `kg_runtime.get_document_facts()`, rồi tính điểm bằng `kg_runtime.score_doc_with_kg()`.

Vị trí chính:

- `hybrid_search.py:1187-1197`: lấy document facts và gọi `score_doc_with_kg()`.
- `kg_runtime.py:776-960`: tính `kg_direct`, `kg_rel`, `kg_ctx`, penalty/guardrail và trả về `kg_score`.
- `hybrid_search.py:1207`, `1220`: đọc và lưu `kg_score` vào runtime item.

Runtime helper có trả thêm `kg_direct_match`, `kg_relation_match`, `kg_context_match`, `kg_bonus_breakdown`, `kg_penalty_breakdown` và `kg_explanation`. Tuy nhiên, `baseline_hybrid_core.csv` không persist các component này; file baseline chỉ lưu `score_raw` và `score_normalized`.

### `intent_adjustment`

`intent_adjustment` là điều chỉnh hẹp theo intent, nằm trong `_intent_narrow_final_adjustment()`. Đây không phải model học máy mà là guardrail rule-based cho một số pattern rõ, ví dụ biosecurity + hatchery + vannamei, low water exchange + Thailand, hatchery vannamei production mode hoặc manual bệnh tôm nước lợ.

Vị trí chính:

- `hybrid_search.py:1063-1112`: `_intent_narrow_final_adjustment()`.
- `hybrid_search.py:1209-1222`: tính và lưu `intent_adjustment`.

Caveat quan trọng: ngoài `intent_adjustment` ở trên, `hybrid_search.py:1271-1281` còn có một guardrail muộn cho truy vấn local aquaculture hẹp. Nếu trong candidate pool có tài liệu aquaculture, các tài liệu capture/market có thể bị trừ `0.12` trực tiếp vào `final_score`. Penalty muộn này không được ghi vào field `intent_adjustment`; nó chỉ xuất hiện trong `final_score` và explanation.

### `final_score`

Trong runtime hybrid search, công thức lõi được tính tại `hybrid_search.py:1212`:

```text
final_score = vector_score + metadata_delta + kg_score + intent_adjustment
```

Sau đó, hệ thống giữ chunk có `final_score` cao nhất cho mỗi document (`best_by_doc`) và sort theo `final_score` giảm dần. Nếu một chunk khác cùng `doc_id` có score bằng hoặc thấp hơn score đã giữ, code bỏ qua chunk đó (`hybrid_search.py:1213-1215`). Vì vậy, tie trong cùng document giữ candidate xuất hiện trước trong vector candidate list.

Trong `run_core_baselines.py`, `hybrid_rows()` gọi trực tiếp `hybrid_search.hybrid_search()`, rồi ghi `score_raw = r["final_score"]` và `score_normalized` là min-max normalization trên top results của từng query. Do đó:

- Trong runtime item: tên là `final_score`.
- Trong `baseline_hybrid_core.csv`: tên xuất ra là `score_raw`.
- `score_normalized` chỉ dùng để report/evaluation output, không phải score ranking gốc.

## 3. Official final_score formula for report

Công thức scoring chính có thể viết trong báo cáo như sau:

```text
final_score(d, q) = vector_score(d, q)
                  + metadata_delta(d, q)
                  + kg_score(d, q)
                  + intent_adjustment(d, q)
```

Trong đó:

- `d` là tài liệu candidate.
- `q` là truy vấn.
- `vector_score(d, q)` là điểm tương đồng ngữ nghĩa giữa truy vấn và chunk/tài liệu từ vector retrieval.
- `metadata_delta(d, q)` là điểm cộng/trừ từ việc khớp metadata như disease, taxon/species, location và production mode.
- `kg_score(d, q)` là điểm đóng góp từ KG runtime, dựa trên document facts, relation/context evidence và explanation evidence nếu có.
- `intent_adjustment(d, q)` là điểm điều chỉnh nhằm ưu tiên tài liệu đúng intent và hạn chế tài liệu gần nghĩa nhưng lệch disease/taxon/location/production mode.

Để mô tả chính xác tuyệt đối với code, nên thêm một footnote/caveat:

```text
Trong một số truy vấn local aquaculture hẹp, runtime có thể áp dụng thêm late intent penalty vào final_score sau bước tính tổng trên. Penalty này là guardrail intent nhưng không được lưu vào field intent_adjustment trong output runtime item.
```

Nếu formal hóa đầy đủ hơn:

```text
final_score_runtime(d, q) =
    vector_score(d, q)
  + metadata_delta(d, q)
  + kg_score(d, q)
  + intent_adjustment(d, q)
  + late_intent_penalty(d, q)
```

Trong đó `late_intent_penalty(d, q)` thường bằng `0`; với local aquaculture intent hẹp, tài liệu capture/market có thể bị trừ `0.12` nếu trong pool đã có tài liệu aquaculture phù hợp.

## 4. Metadata_delta interpretation

`metadata_delta` được tính theo hai bước: phát hiện entity trong query và so khớp với metadata của document.

Các trường metadata chính được dùng:

- `disease`
- `species` / taxon
- `location`
- `production_mode`

Code dùng `compute_match_features()` để tạo cờ match cho bốn nhóm entity trên. Với disease và species, code có canonicalization/alias expansion để gom các biến thể như AHPND/acute hepatopancreatic necrosis disease, WSSV/white spot disease, IMN/IMNV hoặc lobster/tôm hùm. Với location, code có parent mapping trong một số trường hợp, ví dụ query địa phương hẹp có thể match metadata cấp rộng hơn nếu được định nghĩa.

`compute_hybrid_delta()` chia query thành các profile:

- `disease_priority`: query có disease cụ thể hoặc KG-linked disease entity.
- `species_priority`: query có species/taxon nhưng không thuộc disease_priority.
- `generic`: query không có disease/species rõ, chủ yếu dùng location/mode nếu có.

Nguyên tắc scoring:

- Với `disease_priority`, disease match có trọng số cao nhất. Thiếu disease evidence bị trừ điểm. Species/location/mode có thể cộng điểm phụ. Nếu khớp cả disease và species thì có synergy bonus.
- Với `species_priority`, species match là trọng tâm; location và mode là điều kiện phụ. Nếu khớp đồng thời species-location thì có synergy bonus.
- Với `generic`, chỉ cộng nhẹ cho location/mode match vì intent ít ràng buộc hơn.

Các trọng số cụ thể trong code hiện tại gồm ví dụ: disease match `+0.35`, miss disease `-0.18`, disease-species synergy `+0.08`, species match trong species_priority `+0.22`, species-location synergy `+0.05`. Không cần đưa toàn bộ trọng số vào báo cáo chính nếu không cần; điều quan trọng là mô tả `metadata_delta` như một rule-based reranking delta dựa trên mức khớp entity/metadata và query profile.

## 5. KG_score interpretation

Cần phân biệt hai lớp diễn giải:

### A. `kg_score` trong runtime

Đây là score thực sự được cộng vào `final_score`. Runtime tính trong `kg_runtime.score_doc_with_kg()`:

```text
kg_score = kg_direct + kg_rel + kg_ctx
```

Trong đó:

- `kg_direct`: direct fact match giữa query entities và document facts.
- `kg_rel`: relation match qua quan hệ KG, ví dụ disease affects taxon, disease caused by pathogen, taxon found in location.
- `kg_ctx`: context match như symptom, prevention, treatment hoặc pathogen.

Penalty trong KG được áp dụng bằng cách giảm trực tiếp một trong các thành phần runtime, ví dụ disease-specific query không có disease evidence có thể bị downweight non-disease evidence và trừ `0.18`; local aquaculture/lobster query gặp capture fisheries mode có thể bị trừ `0.09` trong KG.

### B. Diagnostic decomposition của `kg_score`

`outputs/kg_score_component_analysis.md` và `outputs/kg_score_component_analysis.csv` là phân tích hậu nghiệm. Report này ghi rõ `baseline_hybrid_core.csv` không lưu đầy đủ `kg_score`/KG explanation component gốc, nên script đã tái tính KG cho từng cặp query-doc bằng `kg_runtime.score_doc_with_kg()`.

Vì vậy, không nên trình bày diagnostic decomposition như công thức runtime chính thức mới. Cách viết đúng là:

```text
Trong phân tích diagnostic, kg_score được tách tương đối thành các nhóm evidence gồm direct fact evidence, relation/context evidence, explanation evidence và penalty. Đây là decomposition dùng để diễn giải đóng góp của KG, không phải log component gốc được lưu trực tiếp trong baseline output.
```

## 6. Diagnostic KG_score decomposition

Công thức diễn giải có thể dùng trong phần analysis/ablation:

```text
kg_score_diagnostic(d, q)
  ≈ direct_fact_score(d, q)
  + relation_score(d, q)
  + explanation_score(d, q)
  - penalty(d, q)
```

Diễn giải:

- `direct_fact_score`: bằng chứng trực tiếp từ document facts như `aboutDisease`, `aboutTaxon`, `aboutLocation`, `documentProductionMode`, `mentions`.
- `relation_score`: bằng chứng quan hệ/context như `affectsTaxon`, `causedBy`, `isFoundIn`, `recommendedPrevention`, `recommendedTreatment`, pathogen/symptom/prevention/treatment.
- `explanation_score`: evidence có thể dùng để sinh explanation hoặc visibility của KG trong explanation.
- `penalty`: điểm trừ/guardrail khi tài liệu lệch intent hoặc evidence yếu/sai ngữ cảnh.

Các con số diagnostic hiện có trong `outputs/kg_score_component_analysis.md`:

- Total rows analyzed: `280`.
- Rows with `kg_score > 0`: `158/280`, tương đương `56.43%`.
- Rows with direct fact evidence: `154/280`, tương đương `55.00%`.
- Rows with relation/context evidence: `82/280`, tương đương `29.29%`.
- Rows with explanation evidence: `158/280`, tương đương `56.43%`.
- Theo mean `kg_score`, nhóm `disease-specific` có KG contribution mạnh nhất trong phân tích này.

Các con số diagnostic trong `outputs/kg_ablation_analysis.md`:

- `full_hybrid` có P@1 `0.8214`, MRR `0.8694`, nDCG@5 `0.6695`, nDCG@10 `0.7222` trên fixed hybrid top-10 candidate pool.
- `intent_adjustment` cải thiện nDCG@10 của `full_hybrid` so với `full_kg_no_intent` khoảng `0.0379` trong diagnostic ablation.
- `direct-only` tăng nDCG@10 so với vector_metadata khoảng `0.0236`; `relation-only` tăng khoảng `0.0096`.

Các số này không phải metric mới trong lượt làm việc này; chúng được đọc lại từ output hiện có.

## 7. Suggested report text — Chapter 3

Trong hệ thống hybrid search, vector retrieval được dùng trước để tạo tập candidate từ các chunk tài liệu có độ tương đồng ngữ nghĩa cao với truy vấn. Sau đó, các candidate được rerank bằng công thức `final_score(d, q) = vector_score(d, q) + metadata_delta(d, q) + kg_score(d, q) + intent_adjustment(d, q)`. Thành phần `vector_score` biểu diễn độ tương đồng embedding giữa truy vấn và chunk tài liệu. Thành phần `metadata_delta` bổ sung tín hiệu khớp metadata như bệnh, taxon/loài, địa điểm và production mode. Thành phần `kg_score` bổ sung bằng chứng từ Knowledge Graph, gồm fact trực tiếp của tài liệu và các quan hệ ngữ cảnh giữa disease, taxon, pathogen, location hoặc biện pháp phòng trị. Cuối cùng, `intent_adjustment` là điều chỉnh rule-based hẹp nhằm giảm các trường hợp tài liệu gần nghĩa nhưng lệch intent chính của truy vấn. Công thức này là cơ chế reranking rule-based của prototype, không phải mô hình học máy được huấn luyện end-to-end.

Nếu cần chính xác hơn với code, có thể thêm câu: "Trong một số intent địa phương hẹp, runtime có thể áp dụng thêm một guardrail muộn trực tiếp lên `final_score`; guardrail này vẫn thuộc nhóm điều chỉnh intent nhưng không luôn được lưu thành field `intent_adjustment` riêng trong output."

## 8. Suggested report text — Chapter 4 / Ablation

Trong phân tích đóng góp của KG, cần phân biệt `kg_score` runtime và decomposition diagnostic. Ở runtime, `kg_score` là điểm tổng được cộng trực tiếp vào `final_score` trong hybrid search. File `baseline_hybrid_core.csv` chỉ lưu `score_raw` và `score_normalized`, không lưu đầy đủ log các component nhỏ như direct fact, relation/context hoặc explanation evidence. Vì vậy, phân tích `kg_score_component_analysis` đã tái tính KG cho các cặp query-document và tách tương đối `kg_score` thành các nhóm direct fact evidence, relation/context evidence, explanation evidence và penalty/guardrail. Direct fact evidence phản ánh các fact như `aboutDisease`, `aboutTaxon`, `aboutLocation` và `documentProductionMode`; relation/context evidence phản ánh các quan hệ như `affectsTaxon`, `causedBy`, `isFoundIn` hoặc prevention/pathogen context. Kết quả diagnostic cho thấy KG có đóng góp rõ nhất ở nhóm `disease-specific`, trong khi ablation trên fixed candidate pool cho thấy `full_hybrid` đạt nDCG@10 cao hơn `full_kg_no_intent` nhờ các điều chỉnh intent hẹp. Phân tích này dùng để diễn giải đóng góp của KG và guardrail, không phải công thức scoring mới thay thế runtime.

## 9. Suggested tables for report

### Bảng. Các thành phần của final_score trong hybrid search

| Thành phần | Ý nghĩa | Nguồn tín hiệu | Vai trò trong ranking | Ghi chú/caveat |
|---|---|---|---|---|
| `vector_score` | Điểm tương đồng ngữ nghĩa ban đầu giữa query và chunk/document | SentenceTransformer embedding + FAISS `IndexFlatIP` trên normalized embeddings | Tạo candidate pool và là nền score chính | Trong runtime gốc là `item["score"]`; baseline hybrid không lưu riêng, chỉ gộp vào `score_raw`. |
| `metadata_delta` | Điểm cộng/trừ từ metadata entity matching | Metadata disease, species/taxon, location, production_mode; alias/canonicalization | Rerank candidate theo mức khớp intent/entity | Trong `compute_hybrid_delta()` key trả về là `kg_delta`, nhưng nên gọi là `metadata_delta` trong báo cáo. |
| `kg_score` | Điểm đóng góp từ KG runtime | Document facts, KG relations, context evidence, KG penalty | Bổ sung bằng chứng semantic/structured cho reranking | Baseline hybrid không lưu component nhỏ; diagnostic analysis tái tính để diễn giải. |
| `intent_adjustment` | Điều chỉnh hẹp theo intent | Query/title pattern và guardrail rule-based | Hạn chế tài liệu gần nghĩa nhưng lệch intent chính | Có thêm late local-aquaculture penalty trừ trực tiếp vào `final_score` và không luôn nằm trong field này. |
| `final_score` | Điểm cuối cùng dùng để sort kết quả hybrid | Tổng vector + metadata + KG + intent, có thể có late penalty | Xếp hạng final Top-k | Trong `baseline_hybrid_core.csv`, được lưu là `score_raw`; `score_normalized` là min-max sau ranking. |

### Bảng. Nhóm evidence trong diagnostic decomposition của KG_score

| Nhóm evidence | Ví dụ property/fact | Ý nghĩa | Lưu ý |
|---|---|---|---|
| Direct fact evidence | `aboutDisease`, `aboutTaxon`, `aboutLocation`, `documentProductionMode`, `mentions` | Tài liệu có fact trực tiếp khớp với disease/taxon/location/mode của query | Gần nhất với bằng chứng document-level; phụ thuộc fact coverage. |
| Relation/context evidence | `affectsTaxon`, `causedBy`, `isFoundIn`, `recommendedPrevention`, `recommendedTreatment`, pathogen, symptom, prevention, treatment | KG cung cấp ngữ cảnh chuyên ngành giữa các thực thể, kể cả khi title không trùng keyword bề mặt | Trong diagnostic report, relation và context được gom tương đối để diễn giải. |
| Explanation evidence | `kg_explanation`, bonus/penalty breakdown | Cho biết vì sao KG đóng góp hoặc phạt một document | Đây là visibility/explainability signal, không phải component ranking độc lập trong baseline output. |
| Penalty/guardrail | Missing disease evidence, aquaculture intent vs capture fisheries mode, negative intent adjustment | Giảm điểm khi tài liệu lệch disease/taxon/location/production mode hoặc sai production context | Penalty runtime có thể được fold vào `kg_direct` hoặc trừ trực tiếp `final_score`; diagnostic penalty là approximation. |

## 10. Caveats and wording constraints

Cần ghi thận trọng:

- Hybrid score là rule-based/reranking formula trong prototype, không phải mô hình học máy được train end-to-end.
- `metadata_delta` và `kg_score` phụ thuộc vào chất lượng metadata, alias, entity linking và fact coverage trong ontology/KG.
- `baseline_hybrid_core.csv` không lưu riêng `vector_score`, `metadata_delta`, `kg_score`, `intent_adjustment`; nó lưu `score_raw`, tức final score đã được gộp.
- KG diagnostic decomposition là phân tích hậu nghiệm/rule-based approximation nếu không có log component gốc đầy đủ trong baseline output.
- Wilcoxon hybrid vs vector_metadata chưa significant ở mức `0.05`; p-value nhỏ nhất trong file hiện có là nDCG@10 `p=0.0884`, nên không được viết rằng hybrid cải thiện có ý nghĩa thống kê.
- Candidate fusion/query expansion là extension/prototype, không nên gọi là baseline final nếu phần đánh giá chính đang dựa trên `baseline_hybrid_core.csv`.
- Không nên viết "KG chứng minh tài liệu đúng tuyệt đối"; chỉ nên viết "KG cung cấp structured evidence hỗ trợ reranking và explanation".
- Không nên viết "final_score luôn bằng đúng tổng bốn cột trong mọi output"; cần caveat về late local-aquaculture penalty và việc baseline CSV không lưu component riêng.

Câu nên dùng:

- "Công thức lõi trong runtime là `vector_score + metadata_delta + kg_score + intent_adjustment`."
- "Một số guardrail hẹp có thể được áp dụng trực tiếp lên `final_score` sau bước tính tổng để xử lý lệch intent rõ ràng."
- "Diagnostic decomposition dùng để diễn giải đóng góp của KG, không phải công thức scoring mới."

Câu nên tránh:

- "Hybrid là mô hình học máy đã học trọng số tối ưu."
- "KG làm hệ thống cải thiện có ý nghĩa thống kê so với vector_metadata."
- "Direct/relation/explanation/penalty là các cột component gốc được lưu đầy đủ trong `baseline_hybrid_core.csv`."
- "Candidate fusion là baseline final chính" nếu không đang dùng nó làm thiết lập đánh giá chính.

## 11. Summary for user

Đã tạo mới:

- `outputs/final_score_formalization_report.md`
- `outputs/final_score_component_trace.csv`

Kết luận chính:

- Công thức lõi trong runtime được xác nhận tại `hybrid_search.py`: `final_score = vector_score + metadata_delta + kg_score + intent_adjustment`.
- Có caveat về late local-aquaculture guardrail: một penalty hẹp có thể được trừ trực tiếp vào `final_score` sau công thức lõi và không được lưu vào field `intent_adjustment`.
- `kg_score` runtime có subcomponents nội bộ `kg_direct_match`, `kg_relation_match`, `kg_context_match`, nhưng `baseline_hybrid_core.csv` không lưu các component này.
- Diagnostic KG decomposition trong `kg_score_component_analysis` là phân tích hậu nghiệm/tái tính để diễn giải đóng góp KG, không phải công thức scoring mới.
- Không cần chạy lại metric để đưa nội dung này vào báo cáo.
- Không sửa runtime/scoring, ontology, metadata, query set, relevance judgments, baseline results hoặc metrics cũ.
