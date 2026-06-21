# Streamlit KG Evidence And Method Compare Fix

## Executive Summary

| item | value |
| --- | --- |
| status | PASS_WITH_OFFLINE_FALLBACK |
| file modified | `app_streamlit.py` |
| runtime/scoring/data modified | No |
| KG evidence tab | Fixed |
| method comparison | Hybrid, Vector, Vector + metadata realtime; Lexical/BM25 and Ontology/SPARQL offline CSV fallback |
| export Excel | PASS |
| compile | PASS |
| Streamlit start | PASS |
| ready for screenshot | YES |

This pass only updates the Streamlit UI layer. It does not change metadata, raw documents, vector store, ontology/KG files, final scoring formula, baseline official outputs, metrics, or latency files.

## KG Evidence Tab Fix

The KG evidence tab no longer depends on `st.dataframe` for its primary display, avoiding the blank-box behavior seen in the current CSS-heavy UI. It now renders visible HTML tables and message blocks.

The tab shows:

- `kg_score`
- `kg_direct_match`
- `kg_relation_match`
- `kg_context_match`
- `kg_bonus_breakdown`
- `kg_penalty_breakdown`
- `doc_uri_in_kg`
- KG explanation text when returned by runtime
- document facts derived from current metadata fields:
  - `related_disease` as `aboutDisease`
  - `related_taxon` as `aboutTaxon`
  - `related_location` as `aboutLocation`
  - `production_mode` as `documentProductionMode`
- detected query entities

If detailed subject-predicate-object relation rows are not returned by runtime, the tab explicitly shows that no relation rows were returned instead of rendering blank. Parsed explanation evidence is marked as `parsed_from_explanation` and is not treated as a source KG fact.

## Method Comparison Support

| method | support mode | behavior |
| --- | --- | --- |
| Hybrid | realtime | Reuses the existing `hybrid_search.hybrid_search` path and unchanged scoring. |
| Vector | realtime | Uses existing vector runtime and aggregates chunk hits to docs. |
| Vector + metadata | realtime | Uses existing metadata delta helpers without KG. |
| Lexical/BM25 | offline fallback | Reads latest 138-doc baseline CSV if query text or query_id matches. |
| Ontology/SPARQL | offline fallback | Reads latest 138-doc baseline CSV if query text or query_id matches. |

For offline fallback methods, the UI shows:

`Offline baseline result from latest 138-doc snapshot.`

If no saved query matches the user's input, the UI shows:

`No matching offline baseline query found. Please use one of the core/extended query texts or run Hybrid/Vector realtime.`

No fake results are generated.

## Export Excel

Export still works through `st.download_button` and now includes `kg_evidence_summary`.

Expected export columns include:

- `query`
- `method`
- `rank`
- `doc_id`
- `title`
- `source`
- `file_path`
- `final_score`
- `vector_score`
- `metadata_delta`
- `kg_score`
- `intent_adjustment`
- `detected_entities`
- `explanation`
- `kg_evidence_summary`

## Smoke Tests

| query | hybrid results | KG evidence rows on selected top result | export bytes | status |
| --- | ---: | ---: | ---: | --- |
| `AHPND shrimp disease` | 5 | 18 | 6841 | PASS |
| `lobster Khanh Hoa` | 5 | 18 | 7061 | PASS |
| `shrimp farming Vietnam` | 5 | 14 | 6879 | PASS |
| `biosecurity shrimp hatchery` | 5 | 17 | 6751 | PASS |

Method comparison smoke check:

| method | result |
| --- | --- |
| Hybrid | PASS, realtime results |
| Vector | PASS, realtime results |
| Vector + metadata | PASS, realtime results |
| Lexical/BM25 | PASS_WITH_OFFLINE_FALLBACK, explicit no-match message for non-saved query text |
| Ontology/SPARQL | PASS_WITH_OFFLINE_FALLBACK, explicit no-match message for non-saved query text |

## Tests Run

| test | status |
| --- | --- |
| `python -m py_compile app_streamlit.py` | PASS |
| `streamlit run app_streamlit.py --server.port 8513` | PASS |
| Hybrid smoke on 4 screenshot queries | PASS |
| KG evidence nonblank check | PASS |
| Export Excel bytes check | PASS |
| Method comparison nonblank check | PASS |

## Limitations

- Lexical/BM25 and Ontology/SPARQL are not realtime in the Streamlit UI. They use offline fallback from the latest 138-doc baseline CSVs only when the typed query matches a saved core or extended query text/query_id.
- The KG evidence tab shows available runtime fields and metadata-derived document facts. It does not draw a full ontology graph.
- Parsed relation names from KG explanation text are labeled `parsed_from_explanation`, not as native KG triples.

## Output Files

- `outputs/streamlit_ui_kg_evidence_and_method_compare_fix_report.md`
- `outputs/streamlit_ui_kg_evidence_and_method_compare_fix_checklist.csv`
