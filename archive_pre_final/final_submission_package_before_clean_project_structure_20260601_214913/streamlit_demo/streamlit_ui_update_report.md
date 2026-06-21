# Streamlit UI update report

## Executive summary

| Item | Value |
| --- | --- |
| Status | PASS |
| File modified | `app_streamlit.py` |
| Sections added/reorganized | Input query; detected entities; Top-k results; result details tabs; method comparison; export results; KG evidence |
| Export Excel added | YES |
| Method comparison added | PARTIAL: Hybrid, Vector, Vector + metadata enabled; Ontology/SPARQL and Lexical/BM25 shown as unavailable for realtime UI |
| KG evidence added | YES: available KG fields only, no fake triples |
| Compile status | PASS |
| Streamlit start status | PASS |
| Ready for screenshot | YES |
| Compare retrieval methods blank output fix | PASS |

This UI update did not modify metadata, raw docs, vector store, ontology/KG files, retrieval scoring, baseline scripts, metrics, or latency outputs.

## Before / after summary

### Before

- Sidebar contained search controls, Top-k selector, Search button, example queries, and optional filters.
- Main area showed title, query input, detected entities, raw entity expander, Top-k table, and result cards.
- Result details were shown as repeated cards with score metrics, explanation, source evidence, and detailed score fields.
- There was no clearly separated export block, method-comparison block, or KG evidence tab.

### After

- Header now states the retrieval stack: vector retrieval, metadata matching, ontology/KG evidence, and hybrid reranking.
- Snapshot metrics are visible: corpus documents, vector chunks, KG docs, and core evaluation query count.
- Section 1: input query, selected method, and Top-k.
- Section 2: detected query entities, with cards for taxon/species, disease, location, production mode, and intent/type, plus raw entities in an expander.
- Section 3: compact Top-k table with rank, doc_id, title, final score, KG score, and source.
- Section 4: result details are split into tabs: Score breakdown, Explanation, KG evidence, and Source evidence.
- Section 5: method comparison is available through a method selector. Hybrid, Vector, and Vector + metadata run from runtime functions. Ontology/SPARQL and Lexical/BM25 are not run in realtime in this safe UI pass.
- Section 6: export results uses `st.download_button` and creates an Excel file in memory.

## Tests

| Test | Status | Detail |
| --- | --- | --- |
| `python -m py_compile app_streamlit.py` | PASS | Compile completed without syntax errors. |
| `streamlit run app_streamlit.py` | PASS | App started on port 8510 and was stopped after verification. |
| Query smoke: `AHPND shrimp disease` | PASS | Hybrid returned results and Excel export bytes were generated. |
| Query smoke: `shrimp farming Vietnam` | PASS | Hybrid returned results and Excel export bytes were generated. |
| Query smoke: Vietnamese lobster disease query | PASS | Hybrid returned results and did not crash. |
| Query smoke: Vietnamese EHP location query | PASS | Hybrid returned results and did not crash. |
| Export Excel | PASS | `aquaculture_search_results_<method>.xlsx` is generated in memory from current results. |
| Method comparison | PARTIAL | Hybrid, Vector, and Vector + metadata run. Ontology/SPARQL and Lexical/BM25 are intentionally disabled for realtime UI. |
| KG evidence tab | PASS | Displays `kg_score`, direct match, relation/context match, KG explanation, and KG URI fields when present. |
| Comparison blank output fix | PASS | Hybrid, Vector, Vector + metadata now render a guarded table or explicit info message. |

## Limitations

- Realtime method comparison currently supports `Hybrid`, `Vector`, and `Vector + metadata`.
- `Ontology/SPARQL` and `Lexical/BM25` remain visible in the UI as method options, but the app shows an info message instead of running them. This avoids introducing new realtime behavior or relying on stale baseline CSVs.
- KG evidence displays fields already returned by the runtime result object. It does not draw a full ontology graph and does not invent relation triples if the runtime does not provide them.
- Optional filters are post-result filters only. They hide displayed rows after retrieval and do not change hybrid scoring.

## Compare retrieval methods blank output fix

### Root cause

The enabled methods were not failing retrieval. `Hybrid`, `Vector`, and `Vector + metadata` could return non-empty rows in smoke tests. The blank box came from the comparison section rendering those rows only through `st.dataframe(...)` inside the current CSS-heavy Streamlit layout, so the enabled branches could appear as a white dataframe area with no visible table. Disabled methods used `st.info()`, so they were still visible.

No baseline CSVs were used and no scoring/retrieval logic was changed.

### Fix applied

- Added guarded `render_comparison_table(...)`.
- Added `df.empty` checks before rendering.
- Switched comparison output to the same HTML table style used by the Top-k table, avoiding the blank dataframe canvas.
- Hybrid comparison now reuses the current displayed Top-k results instead of rerunning Hybrid.
- Vector and Vector + metadata comparisons render method-specific columns when realtime rows are available.
- Empty/unavailable branches now show explicit `st.info()` messages.
- Disabled methods now show: `This method is documented in the interface but realtime execution is disabled in this safe demo pass. Official results are available in offline evaluation outputs.`
- Search results are also stored in `st.session_state["last_query"]`, `st.session_state["last_method"]`, `st.session_state["last_results"]`, and `st.session_state["last_detected"]`.

### Post-fix comparison checks

| Method | Status | Detail |
| --- | --- | --- |
| Hybrid | PASS | Reuses current displayed Top-k results; smoke test returned visible rows. |
| Vector | PASS | Realtime vector comparison returned visible rows; otherwise an info message is shown. |
| Vector + metadata | PASS | Realtime vector+metadata comparison returned visible rows; otherwise an info message is shown. |
| Ontology/SPARQL | PASS | Shows explicit disabled message, no blank output. |
| Lexical/BM25 | PASS | Shows explicit disabled message, no blank output. |
| Vietnamese lobster query | PASS | Hybrid comparison returned rows and did not crash. |

### Additional tests after fix

| Test | Status | Detail |
| --- | --- | --- |
| `python -m py_compile app_streamlit.py` | PASS | Compile completed after comparison fix. |
| Streamlit start | PASS | App started on port 8511 and was stopped after verification. |
| Runtime smoke: `AHPND shrimp disease` | PASS | Hybrid 5 rows; Vector 5 rows; Vector + metadata 5 rows. |
| Runtime smoke: `kỹ thuật nuôi tôm hùm lồng phòng trị bệnh` | PASS | Hybrid returned rows and comparison rows were generated. |

## Next recommendation

For report screenshots, use the updated UI with:

- `AHPND shrimp disease`
- `shrimp farming Vietnam`
- `kỹ thuật nuôi tôm hùm lồng phòng trị bệnh`
- `biosecurity shrimp hatchery`

Use Hybrid for the main screenshot, then optionally show the method-comparison panel with Vector or Vector + metadata selected.

## Output files

- `outputs/streamlit_ui_update_report.md`
- `outputs/streamlit_ui_update_checklist.csv`
