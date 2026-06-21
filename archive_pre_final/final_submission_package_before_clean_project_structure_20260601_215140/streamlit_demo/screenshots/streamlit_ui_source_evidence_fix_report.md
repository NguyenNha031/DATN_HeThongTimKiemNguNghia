# Streamlit Source Evidence Fix Report

## Executive Summary

| item | value |
| --- | --- |
| status | PASS |
| file modified | `app_streamlit.py` |
| runtime/scoring/data modified | No |
| baseline/metrics/latency modified | No |
| Source evidence tab | Fixed |
| blank box remaining | No known blank source-evidence box |
| compile | PASS |
| Streamlit start | PASS on port 8514 |
| export Excel | PASS |

This pass only updates the Streamlit UI rendering for the `Source evidence` tab in `Result details`.

## Root Cause

The `Source evidence` tab still rendered the source metadata block with:

```python
st.dataframe(pd.DataFrame(source_rows), use_container_width=True, hide_index=True)
```

With the current CSS-heavy UI, that dataframe rendered as a large blank box above the visible snippet text.

## Fix Applied

- Added `source_evidence_rows(...)` to collect available result/source fields safely.
- Added `render_source_evidence(...)` to render source evidence without `st.dataframe`.
- The tab now shows the snippet directly when one is returned.
- If no snippet is returned, the tab shows:

`No source snippet was returned for this result.`

- The tab still renders available source metadata in a small HTML table:
  - `doc_id`
  - `title`
  - `source`
  - `file_path`
  - `referenceUrl`
  - `page`
  - `chunk`
  - `snippet/source_evidence`

No source evidence is fabricated.

## Smoke Tests

| query | top-1 source rows | snippet | source | file_path | export bytes | status |
| --- | ---: | --- | --- | --- | ---: | --- |
| `AHPND shrimp disease` | 7 | True | True | True | 6842 | PASS |
| `lobster Khanh Hoa` | 7 | True | True | True | 7062 | PASS |
| `shrimp farming Vietnam` | 7 | True | True | True | 6880 | PASS |
| `biosecurity shrimp hatchery` | 7 | True | True | True | 6752 | PASS |

## Tests Run

| test | status |
| --- | --- |
| `python -m py_compile app_streamlit.py` | PASS |
| `streamlit run app_streamlit.py --server.port 8514` | PASS |
| Hybrid smoke on 4 screenshot queries | PASS |
| Source evidence Top-1 nonblank check | PASS |
| Export Excel bytes check | PASS |

## Output Files

- `outputs/streamlit_ui_source_evidence_fix_report.md`
- `outputs/streamlit_ui_source_evidence_fix_checklist.csv`
