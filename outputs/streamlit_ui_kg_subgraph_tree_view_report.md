# Streamlit UI KG subgraph tree view report

## Status

PASS

## Files changed

- `app_streamlit.py`
- `outputs/streamlit_ui_kg_subgraph_tree_view_report.md`
- `outputs/streamlit_ui_kg_subgraph_tree_view_checklist.csv`

## Scope confirmation

- Did not modify metadata, raw docs, vector store, ontology, KG runtime, scoring, or `final_score`.
- Did not rerun baseline, metrics, or latency.
- Relations are shown only from runtime document facts, metadata facts, detected entities, or parsed explanation text.
- Parsed explanation rows keep `evidence_type=parsed_from_explanation`.

## UI changes

- Added `shorten_kg_label(value)`:
  - URI values are shortened to the local label after `#` or the final `/`.
  - Entity underscores are replaced with spaces.
  - Document IDs such as `SEAFDEC_008`, `FAO_006`, and `KNQG_002` are preserved.
- The main KG relation table now shows shortened labels, not raw URI strings.
- Raw rows remain available only inside `Raw KG triples`.

## Readable KG tree

The `KG subgraph` tab now starts with `Readable KG tree`, shown as a compact code block:

```text
Document <doc_id>
├── aboutDisease: ...
├── aboutTaxon: ...
├── aboutLocation: ...
├── documentProductionMode: ...
└── KG relation/context
    └── subject → predicate → object
```

If no explicit relation/context edge is available, the tree still shows document facts and adds:

`No explicit relation path was returned; showing document-level KG facts.`

## Mini KG graph

- Added `Mini KG graph` using `st.graphviz_chart`.
- The graph is limited to up to 10 prioritized edges.
- Fallback message is shown if Graphviz rendering is unavailable.
- The graph only uses the small query/document evidence set, not the full ontology.

## Edge priority

Default rows are limited to 12 prioritized edges:

1. `aboutDisease`
2. `aboutTaxon`
3. `aboutLocation`
4. `documentProductionMode`
5. `pathogen` / `causedBy`
6. `affectsTaxon`
7. `isFoundIn`
8. `recommendedPrevention` / `recommendedTreatment`

Extra rows are available in `Show all KG evidence rows`.

## Tests

- `python -m py_compile app_streamlit.py`: PASS.
- `streamlit run app_streamlit.py --server.port 8516 --server.headless true`: PASS.
- HTTP check `http://localhost:8516`: PASS, status 200.

Smoke queries:

- `AHPND shrimp disease`: KG rows 32, featured rows 12, graph edges 10, Excel bytes 6935.
- `lobster Khanh Hoa`: KG rows 23, featured rows 12, graph edges 10, Excel bytes 7160.
- `shrimp farming Vietnam`: KG rows 19, featured rows 12, graph edges 10, Excel bytes 6940.
- `biosecurity shrimp hatchery`: KG rows 32, featured rows 12, graph edges 10, Excel bytes 6847.

For each smoke query:

- KG subgraph tab data is not blank.
- Featured relation rows contain no raw `http://` or `https://` URI.
- Readable KG tree includes document facts.
- Mini Graphviz DOT is generated.
- Export Excel still includes `kg_evidence` and `kg_evidence_summary`.

## Demo recommendation

- Use `AHPND shrimp disease` to show disease/taxon/KG relation/context.
- Use `lobster Khanh Hoa` to show document facts for taxon, location, and production mode.
- Use `biosecurity shrimp hatchery` as a backup query with rich KG evidence.

## Screenshot readiness

Screenshot-ready: yes. Streamlit is available at `http://localhost:8516`.
