# Streamlit Offline Baseline Table Render Report

## Status
PASS

## File Changed
- app_streamlit.py

## What Changed
- Offline fallback methods now resolve saved queries through `data/eval/final_query_set_core.csv` first, then `data/eval/final_query_set_extended.csv`.
- When a query match is found, baseline CSV rows are filtered by `query_id` when available, otherwise by query text.
- Offline baseline rows are normalized into table-ready result dictionaries with `rank`, `doc_id`, `title`, `score`, `source`, and `file_path`.
- Offline fallback status is no longer rendered as `OFFLINE_BASELINE:...` in the main UI.
- The UI now shows the compact note: `Using saved offline baseline results from the final 138-doc snapshot.`
- The baseline CSV path is available only inside the small `Show offline source file` expander.

## Match Smoke Tests
- Query: `biosecurity trong hatchery tom the chan trang` equivalent source CSV text `biosecurity trong hatchery tom the chan trang` with Vietnamese diacritics.
- `Ontology/SPARQL`: PASS, table rendered from `data/eval/results/baseline_ontology_sparql_core.csv`.
- `Lexical/BM25`: PASS, table rendered from `data/eval/results/baseline_lexical_core.csv`.

## Non-Match Behavior
- Query: `AHPND shrimp disease`
- `Ontology/SPARQL`: PASS, shows `No matching offline baseline query found. Please use a saved core/extended query or run Hybrid/Vector realtime.`
- `Lexical/BM25`: PASS, shows the same no-match message.
- No crash observed.

## Realtime Regression
- `AHPND shrimp disease` with `Hybrid`: PASS.
- `AHPND shrimp disease` with `Vector`: PASS.
- `AHPND shrimp disease` with `Vector + metadata`: PASS.
- Result sections and custom Top-k tables still render.

## Verification
- `python -m py_compile app_streamlit.py`: PASS.
- `streamlit run app_streamlit.py --server.port 8524`: PASS, server available at `http://localhost:8524`.
- Streamlit AppTest smoke checks: PASS.

## Screenshot Ready
Yes.
