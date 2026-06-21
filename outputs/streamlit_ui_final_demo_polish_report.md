# Streamlit UI final demo polish report

## Status

PASS_WITH_OFFLINE_FALLBACK

## Files changed

- `app_streamlit.py`
- `outputs/streamlit_ui_final_demo_polish_report.md`
- `outputs/streamlit_ui_final_demo_polish_checklist.csv`

## Scope confirmation

- Did not modify metadata, raw docs, vector store, ontology, KG runtime, scoring, or `final_score`.
- Did not rerun baseline, metrics, or latency.
- Only UI/export logic and this output report/checklist were updated.

## UI polish

- Sidebar is labeled `1. Query input / control panel`.
- Main page keeps clear sections:
  - `1. Query input`
  - `2. Detected query entities`
  - `3. Top-k results`
  - `4. Result details`
  - `5. Method comparison`
  - `6. Export results`
- The existing compact Top-k table, score boxes, KG evidence, source evidence, and comparison view were preserved.

## KG subgraph

- Added a dedicated `KG subgraph` tab inside `Result details`.
- Display type: compact relation table plus optional text tree view.
- Table columns:
  - `subject`
  - `predicate`
  - `object`
  - `evidence_type`
  - `source`
- Evidence sources used:
  - `kg_runtime.get_document_facts` when document URI/KG graph is available.
  - Metadata document facts: `related_disease`, `related_taxon`, `related_location`, `production_mode`.
  - Query-side detected entities.
  - Parsed KG explanation relation hints with `evidence_type=parsed_from_explanation`.
- If explicit KG relation rows are unavailable, the UI shows: `No explicit KG relation rows were returned for this result; showing document-level KG/metadata facts instead.`
- The KG subgraph section is not blank in the tested queries.

## Excel export

Excel export still works and now includes both:

- `kg_evidence`
- `kg_evidence_summary`

Required export columns checked:

`query`, `method`, `rank`, `doc_id`, `title`, `source`, `file_path`, `final_score`, `vector_score`, `metadata_delta`, `kg_score`, `intent_adjustment`, `detected_entities`, `explanation`, `kg_evidence`, `kg_evidence_summary`.

## Method comparison

- Hybrid: realtime.
- Vector: realtime.
- Vector + metadata: realtime.
- Lexical/BM25: offline CSV fallback if the query exactly matches a saved core/extended query.
- Ontology/SPARQL: offline CSV fallback if the query exactly matches a saved core/extended query.

For non-matching offline queries, the UI displays:

`No matching offline baseline query found. Please use a saved core/extended query or run Hybrid/Vector realtime.`

The four requested English demo queries do not exactly match the current saved offline baseline query text, so they are best used for realtime Hybrid/Vector/Vector+metadata demo. To demo all 5 methods, use a saved core/extended query from the baseline CSV, for example:

- `biosecurity trong hatchery tôm thẻ chân trắng`
- `surveillance và phân vùng dịch bệnh động vật thủy sản`

## Smoke test

Commands/tests run:

- `python -m py_compile app_streamlit.py`: PASS.
- `streamlit run app_streamlit.py --server.port 8515 --server.headless true`: PASS.
- HTTP check `http://localhost:8515`: PASS, status 200.

Smoke queries:

- `AHPND shrimp disease`: Hybrid Top-5 PASS, KG rows 32, Excel bytes 6933.
- `lobster Khanh Hoa`: Hybrid Top-5 PASS, KG rows 23, Excel bytes 7158.
- `shrimp farming Vietnam`: Hybrid Top-5 PASS, KG rows 19, Excel bytes 6939.
- `biosecurity shrimp hatchery`: Hybrid Top-5 PASS, KG rows 32, Excel bytes 6846.

For each query:

- Hybrid returned Top-5.
- Detected entities were present.
- Top-k table data was available.
- Score breakdown data was available.
- KG evidence was not blank.
- KG subgraph/table was not blank.
- Source evidence was not blank.
- Export Excel bytes were generated and include `kg_evidence`.
- Compare methods were not blank for realtime methods; offline fallback showed the required no-match message where applicable.

## Recommended defense queries

- Use `AHPND shrimp disease` to show disease/taxon/KG evidence.
- Use `lobster Khanh Hoa` to show taxon/location/document facts.
- Use `shrimp farming Vietnam` or `biosecurity shrimp hatchery` as backup realtime demos.
- Use a saved Vietnamese core/extended query when you need all 5 methods including BM25 and Ontology/SPARQL offline fallback.

## Screenshot readiness

Screenshot-ready: yes. Streamlit is currently available at `http://localhost:8515`.

## Remaining limitations

- The four requested English demo queries do not exactly match offline baseline CSV query text, so BM25/Ontology fallback displays the explicit no-match message for those queries.
- KG relation rows are shown only when they can be read from runtime document facts, metadata, detected entities, or parsed explanation text. Parsed explanation rows are labeled `parsed_from_explanation`.
