# Ontology/KG Runtime Quality Check

## Loaded ontology

- Ontology file loaded: `data\ontology\taxon_enriched_facts_v2.owl`
- Loader source: `facts_v2`
- Generated at: `2026-05-21T13:02:15.380845+00:00`

## Structural statistics
- Total triples: 1324
- Total classes: 32
- Total object properties: 14
- Total data properties: 13
- Total named individuals: 55
- Total document nodes: 110

## Document fact coverage
- aboutTaxon: 108 docs (0.982)
- aboutDisease: 68 docs (0.618)
- aboutLocation: 47 docs (0.427)
- documentProductionMode: 109 docs (0.991)

## Label and alias coverage
- Indexed entities: 227
- Entities with rdfs:label: 5
- Entities with skos:prefLabel: 55
- Entities with skos:altLabel: 59
- Ratio with any rdfs/skos label: 0.264
- Metadata docs mapped to KG: 110 / 110

## Runtime-oriented consistency observations
- Documents missing all core facts: 0
- Documents missing title: 0
- Documents missing filePath: 0
- Dangling fact objects: 0
- Duplicate local names: 0
- Non-document entities missing rdfs/skos label: 62
## Key relation counts
- aboutDisease: 95
- aboutTaxon: 191
- aboutLocation: 55
- documentProductionMode: 114
- affectsTaxon: 5
- causedBy: 3
- hasSymptom: 7
- recommendedPrevention: 5
- recommendedTreatment: 4
- mentions: 4

## Quality notes

### Strengths

- The runtime ontology loads through the same KG loader used by retrieval, so the report reflects deployed behavior.
- All metadata document identifiers are mapped to KG document nodes.
- Taxon and production-mode document facts have high coverage.

### Weaknesses

- Location coverage is sparse, which can weaken local-intent retrieval and explanations.
- Disease coverage is incomplete; disease-specific queries can depend on vector/metadata fallback.
- Some non-document entities lack explicit rdfs/skos labels and rely on URI local-name fallback.

### Suggestions

- Backfill missing location facts for documents with local or regional metadata evidence.
- Expand disease/pathogen facts only after manual validation against source documents.
- Add explicit rdfs:label or skos labels for entities currently resolved from URI local names.
- Run a reasoner-based consistency check separately if formal OWL consistency is required.

## Limitations

- Reasoner-based consistency checking was not executed; this report focuses on runtime-oriented structural and coverage checks.
- This is a runtime-oriented structural audit, not a semantic proof of correctness for every fact.
- The check does not modify ontology, metadata, retrieval baselines, query sets, or relevance judgments.
