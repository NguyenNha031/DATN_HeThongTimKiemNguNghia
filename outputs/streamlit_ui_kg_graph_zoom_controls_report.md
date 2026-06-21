# Streamlit UI KG graph zoom controls report

## Status

PASS

## Files changed

- `app_streamlit.py`
- `outputs/streamlit_ui_kg_graph_zoom_controls_report.md`
- `outputs/streamlit_ui_kg_graph_zoom_controls_checklist.csv`

## Scope confirmation

- Did not modify metadata, raw docs, vector store, ontology, KG runtime, scoring, or `final_score`.
- Did not rerun baseline, metrics, or latency.
- KG subgraph, readable tree, relation table, export Excel, and method comparison were preserved.

## Zoom controls

Zoom controls were added directly above the `Mini KG graph` chart inside the `KG subgraph` tab:

- `Zoom in`
- `Zoom out`
- `Reset zoom`

The current value is shown as:

`Graph zoom: <value>x`

## Session state

Zoom is stored in:

`st.session_state["kg_graph_zoom"]`

Settings:

- default: `1.0`
- step: `0.15`
- min: `0.6`
- max: `2.0`

Values are clamped through `clamp_kg_graph_zoom()`.

## Scale method

Graph scale is implemented through Graphviz DOT attributes, not CSS:

- graph `pad`
- graph `nodesep`
- graph `ranksep`
- node `fontsize`
- node `width`
- node `height`
- edge `fontsize`

This means zoom is simulated by re-rendering the DOT graph with larger/smaller text and spacing.

## Tests

- `python -m py_compile app_streamlit.py`: PASS.
- `streamlit run app_streamlit.py --server.port 8519 --server.headless true`: PASS.
- HTTP check `http://localhost:8519`: PASS, status 200.

Smoke queries:

- `AHPND shrimp disease`: KG rows 32, graph edges 10, Excel bytes 6935.
- `lobster Khanh Hoa`: KG rows 23, graph edges 10, Excel bytes 7160.

Zoom verification:

- DOT output changes between `0.6x` and `1.6x`.
- Large zoom reflects increased Graphviz font size and spacing.
- Zoom state update paths for zoom in/out/reset are implemented before DOT render.

## Export

Excel export still works and includes:

`query`, `method`, `rank`, `doc_id`, `title`, `source`, `file_path`, `final_score`, `vector_score`, `metadata_delta`, `kg_score`, `intent_adjustment`, `detected_entities`, `explanation`, `kg_evidence`, `kg_evidence_summary`.

## Screenshot readiness

Screenshot-ready: yes. Use `http://localhost:8519`.
