# Streamlit UI raw entities color fix report

## Status

PASS

## Files changed

- `app_streamlit.py`
- `outputs/streamlit_ui_raw_entities_color_fix_report.md`
- `outputs/streamlit_ui_raw_entities_color_fix_checklist.csv`

## Scope confirmation

- Did not modify metadata, raw docs, vector store, ontology, KG runtime, scoring, or `final_score`.
- Did not rerun baseline, metrics, or latency.
- Preserved detected entity cards, Raw entities expander, Top-k, Result details, KG evidence/subgraph, Source evidence, Method comparison, and Excel export.

## Root cause

The Raw entities area used Streamlit's JSON viewer, while global widget/CSS rules also targeted `pre`, `code`, JSON viewer and input-like elements. In addition, the entity detail table used `st.dataframe`, which can render a large canvas-like white area under the metric cards.

## Fix

- Replaced Raw entities `st.json(...)` with escaped HTML:

```html
<pre class="raw-json-block">...</pre>
```

- Added scoped CSS for `.raw-json-block`:
  - background: `#f8fafc`
  - text: `#111827`
  - border: `#d0d7de`
  - readable text selection colors
- Replaced the entity detail `st.dataframe` with the existing compact HTML table renderer to avoid the large blank white canvas.

## Tests

- `python -m py_compile app_streamlit.py`: PASS.
- `streamlit run app_streamlit.py --server.port 8522 --server.headless true`: PASS.
- HTTP check `http://localhost:8522`: PASS, status 200.

Smoke queries:

- `lobster Khanh Hoa`: entity rows 2, raw JSON chars 683, results 5, Excel bytes 7159.
- `AHPND shrimp disease`: entity rows 2, raw JSON chars 661, results 5, Excel bytes 6934.
- `shrimp farming Vietnam`: entity rows 2, raw JSON chars 624, results 5, Excel bytes 6939.
- `biosecurity shrimp hatchery`: entity rows 4, raw JSON chars 1039, results 5, Excel bytes 6846.

## Result

- Detected entity cards still render.
- Raw entities is readable and no longer depends on the Streamlit JSON viewer.
- The large blank table/canvas area under entity cards is removed.
- Top-k, Result details, KG subgraph, Method comparison and Export Excel still pass.

## Screenshot readiness

Screenshot-ready: yes. Use `http://localhost:8522`.
