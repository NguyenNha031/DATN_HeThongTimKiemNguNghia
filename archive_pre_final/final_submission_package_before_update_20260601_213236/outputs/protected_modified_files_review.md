# Protected Modified Files Review

Generated at: `2026-05-27T22:30:00`

Scope: only read git status and diffs for the four requested protected files. No file was edited, reverted, moved, deleted, or regenerated. No experiment was run.

## Executive Summary

All four files exist and are marked modified (`M`) in git status. The diffs are additive only: `35 insertions(+)`, `0 deletions(-)`.

Overall assessment: the changes look like intentional final/supporting additions, mainly adding the `vector_metadata_kg_no_intent` diagnostic/baseline variant to metric CSVs and wiring the lobster coastal Vietnam boost helper into `run_core_baselines.py`. Because these files are protected source-of-truth/evaluation artifacts, confirm before committing or treating the modified CSVs as official final metrics.

## Git Status

```text
 M data/eval/metrics/baseline_metrics_by_group.csv
 M data/eval/metrics/baseline_metrics_per_query.csv
 M data/eval/metrics/baseline_metrics_summary.csv
 M run_core_baselines.py
```

## Diff Stat

```text
 data/eval/metrics/baseline_metrics_by_group.csv  |  5 +++++
 data/eval/metrics/baseline_metrics_per_query.csv | 28 ++++++++++++++++++++++++
 data/eval/metrics/baseline_metrics_summary.csv   |  1 +
 run_core_baselines.py                            |  1 +
 4 files changed, 35 insertions(+)
```

## Numstat

```text
5	0	data/eval/metrics/baseline_metrics_by_group.csv
28	0	data/eval/metrics/baseline_metrics_per_query.csv
1	0	data/eval/metrics/baseline_metrics_summary.csv
1	0	run_core_baselines.py
```

## File Review

| file | exists | git status | diff summary | review |
|---|---:|---|---|---|
| `run_core_baselines.py` | True | `M` | `+1/-0`; adds `from hybrid_search import _lobster_coastal_vietnam_boost_intent as _lobster_boost`. The imported helper is referenced later in the file at the `_lobster_boost(query_text, detected)` check. | Looks intentional and not an unused import. Likely valid final runtime/evaluation wiring if the lobster/coastal Vietnam boost is part of the final baseline logic. Because this is protected source code, ask/confirm before committing. |
| `data/eval/metrics/baseline_metrics_summary.csv` | True | `M` | `+1/-0`; adds one summary row for `vector_metadata_kg_no_intent`. Existing baseline rows are not changed by this diff. | Looks like an intentional diagnostic/supporting metric addition. Confirm whether `baseline_metrics_summary.csv` should include this extra variant, or whether it should live only in a supporting/ablation metrics file. |
| `data/eval/metrics/baseline_metrics_by_group.csv` | True | `M` | `+5/-0`; adds `vector_metadata_kg_no_intent` rows for five query groups: `biosecurity-management`, `disease-specific`, `hatchery-production-mode`, `local`, and `species-location`. Existing rows are not changed by this diff. | Looks consistent with the summary-row addition and likely useful for KG/no-intent diagnostic discussion. Confirm before treating as official final baseline metrics because this CSV is protected. |
| `data/eval/metrics/baseline_metrics_per_query.csv` | True | `M` | `+28/-0`; adds per-query rows for `vector_metadata_kg_no_intent` across the 28 core queries. Existing rows are not changed by this diff. | Looks internally consistent: one added row per core query. Likely valid if `baseline_vector_metadata_kg_no_intent_core.csv` is part of the supporting diagnostic package. Confirm before finalizing because this file is part of the protected core metrics set. |

## Recommendation

Do not revert automatically. The modifications look coherent and additive, but they touch protected final metric/source files. Recommended decision point: confirm whether `vector_metadata_kg_no_intent` should be included in the official `baseline_metrics_*` CSVs or separated into supporting diagnostic outputs.
