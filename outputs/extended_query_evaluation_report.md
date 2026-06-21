# Extended Query Evaluation Report

## Purpose

Mục tiêu là mở rộng query set từ 28 core queries lên khoảng 90-100 queries để kiểm tra độ ổn định của các baseline trên tập truy vấn lớn hơn.

## Scope and caution

- Đây là evaluation extension, không thay thế core evaluation final ngay.
- Core evaluation 28 queries vẫn là snapshot chính nếu báo cáo chưa thay hoàn toàn.
- Extended judgments được tạo theo quy trình có kiểm soát dựa trên metadata và candidate pooling, nhưng vẫn cần manual review nếu dùng làm kết luận chính thức.

## Extended query set

| query_group | n_queries |
| --- | ---: |
| biosecurity-management | 16 |
| disease-specific | 16 |
| generic-mixed | 16 |
| hatchery-production-mode | 16 |
| local | 16 |
| species-location | 16 |

## Judgment statistics

| label | count |
| ---: | ---: |
| 0 | 1114 |
| 1 | 880 |
| 2 | 736 |

| query_group | n_queries | n_judgments | n_label_2 | n_label_1 |
| --- | ---: | ---: | ---: | ---: |
| biosecurity-management | 16 | 452 | 83 | 129 |
| disease-specific | 16 | 435 | 161 | 113 |
| generic-mixed | 16 | 439 | 223 | 192 |
| hatchery-production-mode | 16 | 499 | 147 | 176 |
| local | 16 | 433 | 67 | 137 |
| species-location | 16 | 472 | 55 | 133 |

## Metrics summary

| method | P@1 | P@5 | Recall@5 | Recall@10 | MRR | nDCG@5 | nDCG@10 | MAP |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| lexical | 0.7917 | 0.6354 | 0.2113 | 0.3297 | 0.8082 | 0.6194 | 0.5946 | 0.3016 |
| vector | 0.8438 | 0.6750 | 0.2785 | 0.4122 | 0.8886 | 0.6534 | 0.6410 | 0.3521 |
| vector_metadata | 0.8854 | 0.7583 | 0.3140 | 0.4796 | 0.9179 | 0.7304 | 0.7226 | 0.4080 |
| ontology_sparql | 0.7708 | 0.6958 | 0.2624 | 0.4311 | 0.8247 | 0.5562 | 0.5805 | 0.3672 |
| hybrid | 0.9375 | 0.7625 | 0.3232 | 0.4972 | 0.9546 | 0.7634 | 0.7570 | 0.4292 |
| hybrid_candidate_fusion | 0.9062 | 0.7542 | 0.3115 | 0.4957 | 0.9366 | 0.7478 | 0.7547 | 0.4261 |

## Comparison with core evaluation

- Best overall method on extended nDCG@10: `hybrid`.
- Hybrid remains a strong baseline, but the ranking should be interpreted cautiously because the extended judgments are generated automatically from metadata/candidate pools.
- Vector_metadata remains close to hybrid on several precision metrics but loses KG/intent evidence used by hybrid.
- Ontology_sparql is useful when entities are explicit, but can be weaker for broad/generic information needs.
- Candidate fusion nDCG@10 delta vs hybrid: -0.0023.

## Group-level analysis

| query_group | best_method | best_nDCG@10 | hybrid_nDCG@10 | vector_metadata_nDCG@10 | candidate_fusion_nDCG@10 | interpretation |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| biosecurity-management | hybrid | 0.7534 | 0.7534 | 0.7471 | 0.6946 | hybrid scoring remains strongest |
| disease-specific | hybrid_candidate_fusion | 0.7825 | 0.7709 | 0.7319 | 0.7825 | candidate fusion benefits this group by expanding candidate coverage |
| generic-mixed | hybrid_candidate_fusion | 0.8485 | 0.8268 | 0.8349 | 0.8485 | candidate fusion benefits this group by expanding candidate coverage |
| hatchery-production-mode | hybrid | 0.6761 | 0.6761 | 0.6354 | 0.6693 | hybrid scoring remains strongest |
| local | hybrid_candidate_fusion | 0.8237 | 0.8032 | 0.6940 | 0.8237 | candidate fusion benefits this group by expanding candidate coverage |
| species-location | hybrid | 0.7118 | 0.7118 | 0.6920 | 0.7097 | hybrid scoring remains strongest |

## Statistical check

Wilcoxon signed-rank test for hybrid vs vector_metadata on per-query metrics:

| metric | statistic | p_value |
| --- | ---: | ---: |
| p_at_1 | 0.0000 | 0.0253 |
| mrr | 4.0000 | 0.0497 |
| ndcg_at_10 | 366.0000 | 0.0873 |

## Limitations

- Extended relevance judgments cần manual review thêm.
- Một số query có thể còn judgment pool chưa đầy đủ dù đã dùng nhiều nguồn candidate.
- Extended set giúp tăng độ phủ đánh giá nhưng chưa thay thế hoàn toàn đánh giá core nếu chưa được giảng viên hoặc đánh giá viên kiểm chứng.

## Recommendation for report

A. Có thể đưa vào Chương 4 như `Đánh giá mở rộng trên query set extended`, nhưng vẫn nên ghi chú judgments cần manual review.

## Outputs

- `data\eval\final_query_set_extended.csv`
- `data\eval\relevance_judgments_extended.csv`
- `data\eval\results\baseline_lexical_extended.csv`
- `data\eval\results\baseline_vector_extended.csv`
- `data\eval\results\baseline_vector_metadata_extended.csv`
- `data\eval\results\baseline_ontology_sparql_extended.csv`
- `data\eval\results\baseline_hybrid_extended.csv`
- `data\eval\results\baseline_hybrid_candidate_fusion_extended.csv`
- `data\eval\metrics\baseline_metrics_summary_extended.csv`
- `data\eval\metrics\baseline_metrics_by_query_extended.csv`
- `data\eval\metrics\baseline_metrics_by_group_extended.csv`
- `outputs\extended_query_judgment_audit.md`
- `outputs\extended_query_evaluation_report.md`

<!-- wilcoxon_json: {"p_at_1": {"statistic": 0.0, "p_value": 0.025347318677468252}, "mrr": {"statistic": 4.0, "p_value": 0.04966953589289581}, "ndcg_at_10": {"statistic": 366.0, "p_value": 0.08725150624170767}} -->