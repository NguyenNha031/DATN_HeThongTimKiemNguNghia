# Baseline Metrics Plus Report

## Purpose

Mục tiêu là bổ sung Recall@10 và MAP cho core evaluation 28 queries mà không thay đổi metric snapshot cũ.

## Outputs

- `data\eval\metrics\baseline_metrics_summary_plus.csv`
- `data\eval\metrics\baseline_metrics_by_query_plus.csv`
- `data\eval\metrics\baseline_metrics_by_group_plus.csv`
- `outputs\baseline_metrics_plus_report.md`

## Metrics summary

| method | P@1 | P@5 | Recall@5 | Recall@10 | MRR | nDCG@5 | nDCG@10 | MAP |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| lexical | 0.3929 | 0.1357 | 0.1962 | 0.2652 | 0.4330 | 0.2715 | 0.2991 | 0.2000 |
| vector | 0.6786 | 0.3357 | 0.4159 | 0.5344 | 0.7691 | 0.5560 | 0.6022 | 0.4016 |
| vector_metadata | 0.7500 | 0.3929 | 0.4888 | 0.6246 | 0.8218 | 0.6143 | 0.6636 | 0.4750 |
| ontology_sparql | 0.5714 | 0.3429 | 0.3885 | 0.5115 | 0.6446 | 0.4091 | 0.4577 | 0.3881 |
| hybrid | 0.8214 | 0.4071 | 0.4980 | 0.6365 | 0.8694 | 0.6695 | 0.7222 | 0.4972 |
| hybrid_candidate_fusion | 0.8571 | 0.4214 | 0.5278 | 0.7061 | 0.9000 | 0.6721 | 0.7345 | 0.5428 |

## Interpretation

- Recall@10 cho biết khả năng đưa tài liệu relevant vào top 10, phù hợp để phân tích candidate pool.
- MAP đánh giá chất lượng xếp hạng trên toàn bộ danh sách relevant retrieved.
- `hybrid_candidate_fusion` cao hơn `hybrid` ở Recall@10 (0.0696) và/hoặc MAP (0.0456), cho thấy candidate fusion có thể giúp mở rộng candidate pool. Tuy nhiên đây vẫn là experiment/extension, không phải baseline final chính.

## Safety confirmation

- Không sửa metric cũ.
- Không sửa runtime/scoring files.
- Không sửa query set core.
- Không sửa relevance judgments core.
- Không sửa baseline result `_core.csv`.
- Missing judgments được xem là relevance_label = 0.
