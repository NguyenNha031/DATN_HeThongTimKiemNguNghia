# Streamlit UI top export button report

## Status

PASS

## Files changed

- `app_streamlit.py`
- `outputs/streamlit_ui_top_export_button_report.md`
- `outputs/streamlit_ui_top_export_button_checklist.csv`

## Scope confirmation

- Did not modify metadata, raw docs, vector store, ontology, KG runtime, scoring, or `final_score`.
- Did not rerun baseline, metrics, or latency.
- Existing search, KG evidence, KG subgraph, method comparison, and Excel export logic were preserved.

## Export button placement

- The Excel download button is now in the top/header area, in the right column next to the `Aquaculture Semantic Search Demo` header.
- Button label: `Export results`.
- Button is compact with `use_container_width=False`.
- The header uses `st.columns([4, 1])`, with no hard-coded pixel width.

## Visibility behavior

- Before search: no export button is rendered in the header.
- After search results exist: the header placeholder is filled with the `Export results` download button.
- The old bottom `6. Export results` section was removed to avoid duplicate export buttons.

## Export columns

Export still includes:

`query`, `method`, `rank`, `doc_id`, `title`, `source`, `file_path`, `final_score`, `vector_score`, `metadata_delta`, `kg_score`, `intent_adjustment`, `detected_entities`, `explanation`, `kg_evidence`, `kg_evidence_summary`.

## Tests

- `python -m py_compile app_streamlit.py`: PASS.
- `streamlit run app_streamlit.py --server.port 8518 --server.headless true`: PASS.
- HTTP check `http://localhost:8518`: PASS, status 200.

Smoke queries:

- `AHPND shrimp disease`: 5 results, Excel bytes 6935.
- `lobster Khanh Hoa`: 5 results, Excel bytes 7160.
- `shrimp farming Vietnam`: 5 results, Excel bytes 6940.
- `biosecurity shrimp hatchery`: 5 results, Excel bytes 6847.

## Layout check

- Single-column order remains: Query input -> Detected entities -> Top-k results -> Result details -> Method comparison.
- Sidebar remains collapsible/responsive; no fixed sidebar width was added.
- Header export button is only shown after results are available.

## Screenshot readiness

Screenshot-ready: yes. Use `http://localhost:8518`.
