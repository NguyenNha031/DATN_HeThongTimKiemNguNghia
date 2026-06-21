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
| 0 | 1197 |
| 1 | 850 |
| 2 | 680 |

| query_group | n_queries | n_judgments | n_label_2 | n_label_1 |
| --- | ---: | ---: | ---: | ---: |
| biosecurity-management | 16 | 439 | 85 | 119 |
| disease-specific | 16 | 431 | 155 | 119 |
| generic-mixed | 16 | 429 | 212 | 176 |
| hatchery-production-mode | 16 | 499 | 149 | 176 |
| local | 16 | 469 | 33 | 155 |
| species-location | 16 | 460 | 46 | 105 |

## Metrics summary

| method | P@1 | P@5 | Recall@5 | Recall@10 | MRR | nDCG@5 | nDCG@10 | MAP |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| lexical | 0.7708 | 0.6042 | 0.2067 | 0.3392 | 0.8060 | 0.5884 | 0.5838 | 0.2949 |
| vector | 0.8438 | 0.6354 | 0.2717 | 0.4159 | 0.8945 | 0.6331 | 0.6404 | 0.3476 |
| vector_metadata | 0.9167 | 0.7167 | 0.3143 | 0.4758 | 0.9376 | 0.7164 | 0.7177 | 0.4110 |
| ontology_sparql | 0.7812 | 0.6833 | 0.2805 | 0.4348 | 0.8299 | 0.5418 | 0.5725 | 0.3766 |
| hybrid | 0.9375 | 0.7188 | 0.3169 | 0.4814 | 0.9515 | 0.7251 | 0.7346 | 0.4187 |
| hybrid_candidate_fusion | 0.9479 | 0.7479 | 0.3430 | 0.5272 | 0.9622 | 0.7484 | 0.7658 | 0.4526 |

## Comparison with core evaluation

- Best overall method on extended nDCG@10: `hybrid_candidate_fusion`.
- Hybrid remains a strong baseline, but the ranking should be interpreted cautiously because the extended judgments are generated automatically from metadata/candidate pools.
- Vector_metadata remains close to hybrid on several precision metrics but loses KG/intent evidence used by hybrid.
- Ontology_sparql is useful when entities are explicit, but can be weaker for broad/generic information needs.
- Candidate fusion nDCG@10 delta vs hybrid: 0.0312.

## Group-level analysis

| query_group | best_method | best_nDCG@10 | hybrid_nDCG@10 | vector_metadata_nDCG@10 | candidate_fusion_nDCG@10 | interpretation |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| biosecurity-management | hybrid_candidate_fusion | 0.7653 | 0.7599 | 0.7638 | 0.7653 | candidate fusion benefits this group by expanding candidate coverage |
| disease-specific | hybrid_candidate_fusion | 0.7843 | 0.7768 | 0.7317 | 0.7843 | candidate fusion benefits this group by expanding candidate coverage |
| generic-mixed | hybrid_candidate_fusion | 0.8358 | 0.8051 | 0.8097 | 0.8358 | candidate fusion benefits this group by expanding candidate coverage |
| hatchery-production-mode | hybrid | 0.6790 | 0.6790 | 0.6593 | 0.6732 | hybrid scoring remains strongest |
| local | hybrid_candidate_fusion | 0.8213 | 0.7122 | 0.6718 | 0.8213 | candidate fusion benefits this group by expanding candidate coverage |
| species-location | hybrid_candidate_fusion | 0.7151 | 0.6747 | 0.6701 | 0.7151 | candidate fusion benefits this group by expanding candidate coverage |

## Statistical check

Wilcoxon signed-rank test for hybrid vs vector_metadata on per-query metrics:

| metric | statistic | p_value |
| --- | ---: | ---: |
| p_at_1 | 2.5000 | 0.3173 |
| mrr | 4.0000 | 0.3430 |
| ndcg_at_10 | 276.0000 | 0.3705 |

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

<!-- wilcoxon_json: {"p_at_1": {"statistic": 2.5, "p_value": 0.31731050786291415}, "mrr": {"statistic": 4.0, "p_value": 0.34302782731118187}, "ndcg_at_10": {"statistic": 276.0, "p_value": 0.3705183851760585}} -->