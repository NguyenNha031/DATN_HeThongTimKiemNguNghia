# KG Score Component Diagnostic Analysis

## Purpose

Mục tiêu là tách `kg_score` thành các nhóm diagnostic để làm rõ KG đóng góp qua direct document facts, relation/context evidence, explanation và penalty/guardrail. Đây là diagnostic decomposition, không thay đổi scoring final và không thay thế công thức `final_score = vector_score + metadata_delta + kg_score + intent_adjustment`.

## Data used

- `data\eval\results\baseline_hybrid_core.csv`
- `data\eval\final_query_set_core.csv`
- `data\eval\relevance_judgments_core.csv`
- `data\metadata\document_metadata_cleaned.xlsx`
- `data\ontology\taxon_enriched_facts_v2.owl`
- `outputs\kg_runtime_verification.json`
- `outputs\document_fact_coverage_audit.json`
- `outputs\query_understanding_profiles.csv`

## Method

- `baseline_hybrid_core.csv` không lưu `kg_score`/KG explanation chi tiết, nên script tái tính KG cho từng cặp query-doc bằng `kg_runtime.score_doc_with_kg()` và mapping KG hiện có.
- Direct fact evidence nhận diện `aboutDisease`, `aboutTaxon`, `aboutLocation`, `documentProductionMode`, `mentions`.
- Relation/context evidence nhận diện `affectsTaxon`, `causedBy`, `isFoundIn`, `hasSymptom`, `recommendedPrevention`, `recommendedTreatment`, `pathogen`, `symptom`, `prevention`, `treatment`, `relation match`.
- Explanation evidence là việc runtime trả về `kg_explanation`; score diagnostic visibility dùng `min(0.05, kg_score * 0.1)` khi `kg_score > 0`.
- Penalty/guardrail gồm penalty trong `kg_penalty_breakdown` và `abs(intent_adjustment)` nếu intent adjustment âm.
- `kg_unclassified_score_diagnostic` giữ phần dương của `kg_score` chưa được phân loại vào direct hoặc relation/context. Các component là approximation phục vụ phân tích, không phải điểm final.

## Overall KG usage

| metric | value |
| --- | ---: |
| total_result_rows | 280.0000 |
| results_with_kg_score | 172.0000 |
| pct_results_with_kg_score | 0.6143 |
| queries_with_kg_score | 21.0000 |
| total_queries | 28.0000 |
| pct_queries_with_kg_score | 0.7500 |
| mean_kg_score_topk | 0.2151 |
| mean_kg_score_top1 | 0.2871 |

## Component distribution

| component metric | value |
| --- | ---: |
| n_rows | 280.0000 |
| results_with_direct_fact_evidence | 169.0000 |
| pct_results_with_direct_fact_evidence | 0.6036 |
| results_with_relation_evidence | 89.0000 |
| pct_results_with_relation_evidence | 0.3179 |
| results_with_explanation_evidence | 172.0000 |
| pct_results_with_explanation_evidence | 0.6143 |
| sum_kg_direct_fact_score_diagnostic | 43.7300 |
| mean_kg_direct_fact_score_diagnostic | 0.1562 |
| sum_kg_relation_score_diagnostic | 16.5000 |
| mean_kg_relation_score_diagnostic | 0.0589 |
| sum_kg_explanation_score_diagnostic | 5.1450 |
| mean_kg_explanation_score_diagnostic | 0.0184 |
| sum_kg_penalty_diagnostic | 1.0100 |
| mean_kg_penalty_diagnostic | 0.0036 |
| sum_kg_unclassified_score_diagnostic | 0.0000 |
| mean_kg_unclassified_score_diagnostic | 0.0000 |

## By-query-group analysis

| query_group | n_queries | n_results | mean_kg_score | top1_mean_kg_score | pct_kg_score | pct_direct_fact | pct_relation | pct_explanation | interpretation |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| biosecurity-management | 6 | 60 | 0.0767 | 0.0667 | 0.5000 | 0.5000 | 0.2000 | 0.5000 | KG contribution moderate |
| disease-specific | 6 | 60 | 0.3508 | 0.3950 | 0.8833 | 0.8333 | 0.7167 | 0.8833 | KG contribution strong |
| hatchery-production-mode | 4 | 40 | 0.0875 | 0.1750 | 0.5000 | 0.5000 | 0.0000 | 0.5000 | KG contribution moderate |
| local | 7 | 70 | 0.3191 | 0.4729 | 0.5286 | 0.5286 | 0.4857 | 0.5286 | KG contribution strong |
| species-location | 5 | 50 | 0.1748 | 0.2520 | 0.6400 | 0.6400 | 0.0000 | 0.6400 | KG contribution strong |

## Evidence type counts

| evidence_type | count |
| --- | ---: |
| aboutDisease | 174 |
| aboutTaxon | 264 |
| aboutLocation | 68 |
| documentProductionMode | 40 |
| affectsTaxon | 164 |
| causedBy | 146 |
| isFoundIn | 28 |
| hasSymptom | 0 |
| recommendedPrevention | 12 |
| recommendedTreatment | 0 |

## Interpretation for report

KG không chỉ là một điểm tổng: trong diagnostic này, đóng góp chủ yếu nghiêng về `direct facts`. Direct document facts như `aboutDisease`, `aboutTaxon`, `aboutLocation`, `documentProductionMode` cho biết tài liệu khớp trực tiếp với entity/query. Relation/context evidence như disease-taxon, disease-pathogen, taxon-location, prevention/treatment/symptom giúp bổ sung ngữ cảnh chuyên ngành khi tài liệu không chỉ khớp từ khóa bề mặt.

Explanation evidence giúp làm rõ vì sao tài liệu được ưu tiên trong hybrid search. Tuy nhiên decomposition này là diagnostic, dựa trên explanation/runtime result được tái tính, không thay thế công thức scoring final.

Nhóm có KG contribution mạnh nhất theo mean `kg_score` là `disease-specific`; nhóm yếu nhất là `biosecurity-management`. Các chiều disease/location có thể còn yếu nếu evidence trong ontology ít hơn taxon/production mode hoặc nếu query không được entity linking rõ.

## Limitations

- `baseline_hybrid_core.csv` không lưu đầy đủ từng component gốc, nên script phải tái tính KG bằng runtime hiện có.
- Component score là rule-based approximation và diagnostic visibility score, không phải điểm final.
- Phân tích này không chứng minh mọi fact là đúng chuyên ngành.
- Không thay đổi kết quả hybrid final.
- Future work nên instrument runtime để log chính xác từng component score ngay lúc search.

## Safety confirmation

- Không sửa `hybrid_search.py`.
- Không sửa `kg_runtime.py`.
- Không sửa ontology.
- Không sửa metadata.
- Không sửa query set.
- Không sửa relevance judgments.
- Không sửa baseline outputs/metrics cũ.

## Outputs

- `outputs\kg_score_component_analysis.csv`
- `outputs\kg_score_component_analysis.md`
- `outputs\figures\fig_kg_score_components.png`