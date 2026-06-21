# KG Ablation Analysis

## Purpose

Mục tiêu là kiểm tra đóng góp riêng của direct fact evidence, relation/context evidence, full KG và intent adjustment trong hybrid search.

## Scope and caution

- Đây là diagnostic ablation, không thay đổi hybrid final.
- Candidate pool được cố định theo top-10 rows của `baseline_hybrid_core.csv` để so sánh các công thức score trên cùng tập candidate.
- Direct/relation scores được lấy từ `outputs/kg_score_component_analysis.csv`; vì baseline result không log component gốc, đây là diagnostic approximation.

## Configurations

| configuration | score formula | meaning |
| --- | --- | --- |
| vector_metadata | `hybrid_score_raw - kg_score - intent_adjustment` | Vector + metadata approximation on the fixed hybrid top-10 candidate pool. |
| kg_direct_only | `vector_metadata_score + kg_direct_fact_score_diagnostic` | Adds only direct document fact evidence such as aboutDisease/aboutTaxon/aboutLocation/documentProductionMode. |
| kg_relation_only | `vector_metadata_score + kg_relation_score_diagnostic` | Adds relation/context evidence such as affectsTaxon, causedBy, isFoundIn, prevention/pathogen context. |
| full_kg_no_intent | `vector_metadata_score + kg_score` | Adds full KG score but excludes final intent adjustment. |
| full_hybrid | `hybrid_score_raw` | Current hybrid ranking with vector, metadata, KG and intent adjustment. |

## Metrics summary

| method | P@1 | P@5 | Recall@5 | Recall@10 | MRR | nDCG@5 | nDCG@10 | MAP |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| vector_metadata | 0.7143 | 0.4071 | 0.5007 | 0.6365 | 0.8033 | 0.6056 | 0.6617 | 0.4663 |
| kg_direct_only | 0.7143 | 0.4143 | 0.5078 | 0.6365 | 0.8063 | 0.6351 | 0.6853 | 0.4754 |
| kg_relation_only | 0.7500 | 0.3857 | 0.4790 | 0.6365 | 0.8200 | 0.6048 | 0.6713 | 0.4684 |
| full_kg_no_intent | 0.7500 | 0.3929 | 0.4861 | 0.6365 | 0.8230 | 0.6234 | 0.6843 | 0.4759 |
| full_hybrid | 0.8214 | 0.4071 | 0.4980 | 0.6365 | 0.8694 | 0.6695 | 0.7222 | 0.4972 |

## By-group analysis

| query_group | best_config | nDCG@10 best | direct_only nDCG@10 | relation_only nDCG@10 | full_kg_no_intent nDCG@10 | full_hybrid nDCG@10 | interpretation |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| biosecurity-management | vector_metadata | 0.7850 | 0.7850 | 0.7626 | 0.7626 | 0.7794 | KG components do not improve this fixed-pool ranking |
| disease-specific | full_kg_no_intent | 0.6450 | 0.6274 | 0.6271 | 0.6450 | 0.6450 | combined KG is useful before intent adjustment |
| hatchery-production-mode | full_hybrid | 0.6891 | 0.5984 | 0.6001 | 0.5984 | 0.6891 | full hybrid scoring is strongest |
| local | full_hybrid | 0.7334 | 0.6987 | 0.6942 | 0.6987 | 0.7334 | full hybrid scoring is strongest |
| species-location | full_hybrid | 0.7571 | 0.6859 | 0.6398 | 0.6859 | 0.7571 | full hybrid scoring is strongest |

## Interpretation

- Direct-only nDCG@10 delta vs vector_metadata: 0.0236.
- Relation-only nDCG@10 delta vs vector_metadata: 0.0096.
- Trong fixed hybrid candidate pool này, `direct facts` tạo cải thiện nDCG@10 lớn hơn.
- Full KG no intent delta vs vector_metadata: 0.0226.
- Intent adjustment delta full_hybrid vs full_kg_no_intent: 0.0379.
- Nếu full_hybrid thấp hơn full_kg_no_intent ở một metric, điều đó không nhất thiết phủ định intent guardrail; đây là fixed-pool diagnostic và intent adjustment chủ yếu xử lý một số case hẹp.

## Limitations

- Vì baseline result không lưu component gốc, direct/relation score là diagnostic approximation từ `kg_score_component_analysis.csv`.
- Candidate pool cố định theo top-10 hybrid rows, nên kết quả không phải production baseline mới.
- Không chứng minh mọi KG fact đúng chuyên ngành.
- Không thay thế final hybrid.
- Cần instrumentation sâu hơn trong future work nếu muốn log chính xác component score ở runtime.

## Report recommendation

Có thể đưa vào báo cáo như `Phân tích ablation mở rộng KG runtime`, kèm caveat rõ rằng đây là diagnostic trên fixed candidate pool và direct/relation scores là approximation.

## Safety confirmation

- Không sửa runtime/scoring files.
- Không sửa ontology.
- Không sửa metadata.
- Không sửa query set.
- Không sửa relevance judgments.
- Không sửa baseline outputs/metrics cũ.

## Outputs

- `data\eval\results\kg_ablation_results_core.csv`
- `data\eval\metrics\kg_ablation_metrics_summary.csv`
- `data\eval\metrics\kg_ablation_metrics_by_query.csv`
- `data\eval\metrics\kg_ablation_metrics_by_group.csv`
- `outputs\kg_ablation_analysis.md`
- `outputs\figures\fig_kg_ablation_summary.png`