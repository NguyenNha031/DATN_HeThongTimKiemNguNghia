# Streamlit UI mini KG graph size control report

## Status

PASS

## Files changed

- `app_streamlit.py`
- `outputs/streamlit_ui_mini_kg_graph_size_control_report.md`
- `outputs/streamlit_ui_mini_kg_graph_size_control_checklist.csv`

## Scope confirmation

- Did not modify metadata, raw docs, vector store, ontology, KG runtime, scoring, or `final_score`.
- Did not rerun baseline, metrics, or latency.
- Preserved KG subgraph tab, readable tree, mini graph, key relation rows, show-all rows, export Excel, and method comparison.

## UI change

- Removed the three large buttons: `Zoom in`, `Zoom out`, `Reset zoom`.
- Replaced them with a compact `Graph size` selectbox above `Mini KG graph`.
- Options:
  - `Compact`
  - `Normal`
  - `Large`
- Default: `Normal`.
- Added helper caption: `Use the fullscreen icon for a larger view.`

## Graph rendering

Graph size is implemented with Graphviz DOT attributes, not CSS:

- node font size
- edge font size
- `nodesep`
- `ranksep`
- node width
- node height
- `ratio=compress`
- `rankdir=LR`

Default edge limits:

- Compact: 6 prioritized edges.
- Normal: 7 prioritized edges.
- Large: 8 prioritized edges.

Priority remains focused on:

1. `aboutDisease`
2. `aboutTaxon`
3. `aboutLocation`
4. `documentProductionMode`
5. `pathogen` / `causedBy`
6. `affectsTaxon` / `isFoundIn`

Extra evidence rows remain available in `Show all KG evidence rows`.

## Readable tree

- `Readable KG tree` remains the primary easy-to-read representation.
- Tree rows are capped to 8 prioritized KG rows to avoid showing too many aliases/entities at once.
- Raw URI values are still hidden from the main display and remain available only in `Raw KG triples`.

## Tests

- `python -m py_compile app_streamlit.py`: PASS.
- `streamlit run app_streamlit.py --server.port 8521 --server.headless true`: PASS.
- HTTP check `http://localhost:8521`: PASS, status 200.

Smoke queries:

- `AHPND shrimp disease`: KG rows 32, tree lines 10, graph edges Compact/Normal/Large = 6/7/8, Excel bytes 6934.
- `lobster Khanh Hoa`: KG rows 23, tree lines 10, graph edges Compact/Normal/Large = 6/7/8, Excel bytes 7159.
- `shrimp farming Vietnam`: KG rows 19, tree lines 10, graph edges Compact/Normal/Large = 6/7/8, Excel bytes 6939.
- `biosecurity shrimp hatchery`: KG rows 32, tree lines 10, graph edges Compact/Normal/Large = 6/7/8, Excel bytes 6846.

## Export

Excel export still works and includes:

`query`, `method`, `rank`, `doc_id`, `title`, `source`, `file_path`, `final_score`, `vector_score`, `metadata_delta`, `kg_score`, `intent_adjustment`, `detected_entities`, `explanation`, `kg_evidence`, `kg_evidence_summary`.

## Screenshot readiness

Screenshot-ready: yes. Use `http://localhost:8521`.
