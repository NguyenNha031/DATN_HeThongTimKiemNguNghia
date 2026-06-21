# Baseline results generation (step 3)

## Already run
- Script: `run_core_baselines.py` (project root).
- Query: `data/eval/final_query_set_core.csv` (28 query).
- Metadata titles: `data/metadata/document_metadata_cleaned.xlsx`.
- Vector index: `vector_store/chunks.index` + config; chunks list BM25: `vector_store/chunks_meta.pkl` (must match corpus build).

## Lexical
- **BM25 Okapi** on tokenized, normalized text (no ontology/KG).
- Each query: BM25 on **every** chunk, then **max-pool** per doc (doc score = max chunk score in doc), sort doc by pool score, take top 10. **Do not** cut early at top-N chunk (avoid putting all top chunk into few long documents).
- `retrieval_level`: `chunk_to_doc`.

## Vector
- `vector_search.search` — embedding `paraphrase-multilingual-MiniLM-L12-v2`, FAISS `IndexFlatIP`, vector L2-normalized.
- Each query: `top_k = ntotal` (number of vectors in index, usually equals number of chunks), same similarity formula; then max-pool per doc like lexical, top 10.
- No metadata, no KG.

## Vector + metadata
- Same pool candidates vector with hybrid at **CANDIDATE_K** chunk + optional domain-specific query expansion.
- Score = `vector_score + metadata_delta` with `compute_match_features` + `compute_hybrid_delta` from `hybrid_search`.
- **Do not** call `link_query_entities_kg` / **no** merge KG entities — only `detect_entities(term_index)` (regex + dictionary metadata).
- Intent penalty for aquaculture: copy logic `_narrow_local_aquaculture_intent` + penalty capture/market when doc aquaculture in pool.

## Ontology / SPARQL
- Load graph like hybrid (`hybrid_search._init_kg_if_needed`).
- `kg_runtime.link_query_entities_kg` → set of URI; SPARQL `COUNT DISTINCT ?p` with `?doc ?p ?target` and `?p` ∈ {aboutDisease, aboutTaxon, aboutLocation, documentProductionMode}.
- `score_raw` = `kg_score` ( `score_doc_with_kg` ) + small boost 0.001 × (SPARQL hit count) to break ties; `retrieval_level`: `kg_structured`.
- Query not catching entity: still rank all corpus by `kg_score` (usually low / negative).

## Hybrid
- `hybrid_search.hybrid_search`. Runtime temporarily set `FINAL_K=10` and `CANDIDATE_K=150` (default repo `FINAL_K=5`, `CANDIDATE_K=10`) to pool chunk enough diverse doc when output top-10; restore after running.
- `final_score = vector_score + metadata_delta + kg_score + intent_adjustment`; `intent_adjustment` is a tight guardrail (very narrow), see `hybrid_search._intent_narrow_final_adjustment`.

## score_normalized
- On the **top doc of each query**, min–max on `score_raw` → [0,1] (best doc ~1). If all scores equal → all 1.

## Limits
- Hybrid / vector_metadata considers doc in pool up to **2×CANDIDATE_K** chunk (this run `CANDIDATE_K=150` temporarily); still can be <10 doc if corpus/index has few chunk/doc diverse.
- Lexical / vector: already used **all chunk** for points before max-pool → each query has enough **10 doc** if only index has ≥10 `doc_id` different (current corpus achieves).
- Ontology: query natural not matching alias KG → SPARQL empty, rank mainly from `kg_score` / mapping URI.

## Metrics
- **Not yet** computed P@k, Recall, MRR, nDCG (step 4).
