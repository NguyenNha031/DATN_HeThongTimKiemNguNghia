# Hybrid vs Vector Metadata by Query Group

## Purpose

This table compares the final `hybrid` baseline against `vector_metadata` by query group. It helps show where the full hybrid pipeline adds value beyond vector retrieval plus metadata matching.

The data is read from:

```text
data/eval/metrics/baseline_metrics_by_group.csv
```

No baseline was rerun and no metric file was modified.

## Comparison Table

| query_group | n_queries | hybrid nDCG@10 | vector_metadata nDCG@10 | delta | better_method | interpretation |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| biosecurity-management | 6 | 0.779406 | 0.782709 | -0.003303 | vector_metadata | Vector+metadata is slightly higher on nDCG@10; hybrid ties P@1 and MRR. |
| disease-specific | 6 | 0.644979 | 0.544094 | 0.100885 | hybrid | Hybrid improves disease-specific ranking, consistent with added KG disease evidence and guardrails. |
| hatchery-production-mode | 4 | 0.689110 | 0.567382 | 0.121728 | hybrid | Hybrid improves hatchery/production-mode queries, likely from KG and intent-sensitive reranking. |
| local | 7 | 0.733369 | 0.668572 | 0.064797 | hybrid | Hybrid improves local queries overall, though exact lexical/local signals remain important. |
| species-location | 5 | 0.757070 | 0.734143 | 0.022927 | hybrid | Hybrid has higher nDCG@10, but vector_metadata has stronger P@1/MRR for this group. |

## Notes

- This is a grouped interpretation of existing final metrics.
- It does not replace the overall metric summary.
- It does not imply every query improves; group-level gains can hide individual regressions.
- Candidate fusion and semantic rule prototypes are not included here because they are experiments/future work, not final baselines.
