## Semantic normalization + conservative backfill — final assessment

### What the patch fixed

- **added_triples**: see `outputs/document_fact_backfill_report.csv` (added rows exist; total added was observed as 53).

- **docs_with_zero_core_facts**: 1 -> 0

- **aboutTaxon coverage ratio**: 0.2439 -> 0.9756

- **documentProductionMode coverage ratio**: 0.9268 -> 1.0000

### What the patch did NOT fix

- **aboutDisease coverage** stayed flat by design (topic/management/pathogen terms were denied; no coercion into Disease facts).

### Coverage gain vs retrieval gain

- This patch **materially improves data completeness** (facts coverage), but **query-level retrieval gain may be limited** for disease-focused queries because `aboutDisease` did not increase.

- See expanded verification summary in `outputs/kg_runtime_verification_semantic_patch_summary.json`.

### False positive risk review

- Verdict: **NEEDS_TIGHTENING** (details in `outputs/semantic_backfill_false_positive_review.json`).

- Suspicious cases were detected; review recommended.

### Should we keep this patch?

- Recommendation: **KEEP, but monitor** generic entity usage in queries like 'fish disease'/'aquatic animals'.

### Next best step

- If you want KG reranking to improve for disease/topic-heavy metadata, you need a controlled approach to represent **topics vs diseases** in ontology (e.g., Topic class) or enrich disease entities where truly applicable.
