# Streamlit UI export button near search report

## Status

PASS

## Files changed

- `app_streamlit.py`
- `outputs/streamlit_ui_export_button_near_search_report.md`
- `outputs/streamlit_ui_export_button_near_search_checklist.csv`

## Scope confirmation

- Did not modify metadata, raw docs, vector store, ontology, KG runtime, scoring, or `final_score`.
- Did not rerun baseline, metrics, or latency.
- Existing search, KG subgraph, method comparison, one-column layout, and Excel export were preserved.

## Export button placement

- Moved `Export results` from the header/top-right area to section `1. Query input`.
- The button now appears beside `Search query` using responsive Streamlit columns.
- Removed the header `st.columns([4, 1])` export placement.
- No bottom export section is rendered, so there is only one export button.

## Visibility behavior

- Before search: no `Export results` button is rendered.
- After search results exist: `Export results` appears near `Search query`.
- The button remains compact with `use_container_width=False`.

## Export columns

Export still includes:

`query`, `method`, `rank`, `doc_id`, `title`, `source`, `file_path`, `final_score`, `vector_score`, `metadata_delta`, `kg_score`, `intent_adjustment`, `detected_entities`, `explanation`, `kg_evidence`, `kg_evidence_summary`.

## Tests

- `python -m py_compile app_streamlit.py`: PASS.
- `streamlit run app_streamlit.py --server.port 8520 --server.headless true`: PASS.
- HTTP check `http://localhost:8520`: PASS, status 200.

Smoke queries:

- `AHPND shrimp disease`: 5 results, Excel bytes 6934.
- `lobster Khanh Hoa`: 5 results, Excel bytes 7159.
- `shrimp farming Vietnam`: 5 results, Excel bytes 6939.
- `biosecurity shrimp hatchery`: 5 results, Excel bytes 6846.

## Layout check

- Header no longer has an export button.
- Export button is near `Search query`.
- Main layout remains one-column: Query input -> Detected entities -> Top-k results -> Result details -> Method comparison.
- Sidebar remains collapsible/responsive; no fixed positioning or absolute CSS was added.

## Screenshot readiness

Screenshot-ready: yes. Use `http://localhost:8520`.
