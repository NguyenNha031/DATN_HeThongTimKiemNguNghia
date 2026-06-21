# Streamlit Demo Notes

## Purpose

This demo UI shows the project as an executable semantic search system. It lets a user enter an aquaculture/marine-fisheries query and inspect ranked hybrid-search results with score components and explanations.

## Main App File

- `app_streamlit.py`

## How To Run

```bash
streamlit run app_streamlit.py
```

If Streamlit is not installed:

```bash
python -m pip install streamlit
```

## Suggested Screenshot Queries

- `AHPND shrimp disease`
- `lobster Khanh Hoa`
- `whiteleg shrimp hatchery`
- `shrimp farming Vietnam`

## UI Components

- Search box: `Search query`
- Top-k selector: `3`, `5`, `10`
- Result table with `rank`, `doc_id`, `title`, `final_score`, `vector_score`, `metadata_delta`, `kg_score`, and `intent_adjustment`
- Result cards for easier screenshots
- Expandable `Score details and explanation`
- Sidebar instructions and example queries
- Optional post-result filters for disease, species/taxon, and location

## Runtime Safety

The app calls the existing `hybrid_search.hybrid_search()` runtime. It does not change the scoring formula, ontology, metadata, query set, relevance judgments, baseline outputs, or metric files.

The final runtime ontology remains:

```text
data/ontology/taxon_enriched_facts_v2.owl
```

The app does not use experiment ontology files such as `outputs/taxon_enriched_facts_v2_backfilled_runtime.owl` or semantic patch outputs.
