# Query Understanding Profiles

## Purpose

This report explains how the system understands the 28 core queries before scoring and reranking.
It is a read-only technical analysis. It does not modify the ontology, metadata, query set, relevance judgments, baseline outputs, metrics, `hybrid_search.py`, or `kg_runtime.py`.

## Input Files and Runtime Functions

- `data\eval\final_query_set_core.csv`
- `data/metadata/document_metadata_cleaned.xlsx`
- `data/ontology/taxon_enriched_facts_v2.owl via kg_runtime loader`
- `outputs\error_analysis_core.csv`

Runtime functions reused:
- `hybrid_search.load_full_metadata`
- `hybrid_search.build_term_index`
- `hybrid_search.detect_entities`
- `kg_runtime.link_query_entities_kg`
- `hybrid_search._merge_detected_with_kg`
- `hybrid_search.get_query_profile`
- `hybrid_search._narrow_local_aquaculture_intent`
- `hybrid_search._lobster_coastal_vietnam_boost_intent`
- `hybrid_search._hatchery_vannamei_production_mode_intent`
- `hybrid_search._biosecurity_hatchery_vannamei_stack_intent`
- `hybrid_search._thailand_low_water_exchange_intent`

## How Profiles Are Determined

- `detected_profile` comes from the runtime `hybrid_search.get_query_profile()` after dictionary detection and KG entity merge.
- `inferred_profile` uses the query-set `query_group` when available, because the benchmark groups are thesis-facing categories.
- Entity detection uses metadata-derived terms, manual aliases, KG labels/aliases, and overlap suppression from the runtime.
- Signal priority is explanatory: it maps the detected/query-set profile to the scoring layers that should matter most.

## Query Count by Profile

| profile | n_queries | main_signal_priority | risk_if_misclassified | example_query_id |
| --- | --- | --- | --- | --- |
| biosecurity-management | 6 | vector semantics + topic/management/prevention aliases; KG prevention/management context is supporting evidence. | Topic aliases are sparse; generic biosecurity documents may outrank emergency or management-specific documents. | BI_001 |
| disease-specific | 6 | KG disease facts + metadata disease + vector; disease evidence should dominate. | Missing disease aliases can let species/vector similarity outrank disease-specific evidence. | DS_001 |
| hatchery-production-mode | 4 | production_mode metadata + species + vector; KG mode and hatchery intent guardrails are important. | Hatchery/life-stage misses can mix grow-out, disease, and hatchery documents. | HM_001 |
| local | 7 | location metadata/KG + lexical exact terms + vector; guardrails should protect local aquaculture intent. | Sparse location facts or missing local aliases can make exact local documents depend on lexical/vector luck. | LO_001 |
| species-location | 5 | metadata species/location + vector; KG location/taxon facts and intent guardrails are secondary. | Location or species miss can cause broad shrimp/aquaculture documents to outrank country-specific documents. | SL_001 |

## Runtime Profile Counts

| runtime_profile | n_queries |
| --- | --- |
| disease_priority | 7 |
| generic | 5 |
| species_priority | 16 |

## Entity Detection Summary

| entity type | queries with entity |
| --- | --- |
| disease | 7 |
| taxon_species | 22 |
| location | 12 |
| production_mode | 10 |
| topic_management_prevention | 2 |

## Multi-context Queries

| query_id | query_group | detected dimensions |
| --- | --- | --- |
| BI_001 | biosecurity-management | taxon, production_mode, topic/management |
| BI_004 | biosecurity-management | production_mode, topic/management |
| DS_001 | disease-specific | disease, taxon |
| DS_002 | disease-specific | disease, taxon |
| DS_006 | disease-specific | disease, taxon |
| DS_010 | disease-specific | disease, taxon, location |
| HM_001 | hatchery-production-mode | taxon, production_mode |
| HM_002 | hatchery-production-mode | taxon, location, production_mode |
| HM_007 | hatchery-production-mode | taxon, location, production_mode |
| HM_010 | hatchery-production-mode | taxon, production_mode |
| LO_001 | local | taxon, location |
| LO_002 | local | disease, taxon, location |
| LO_003 | local | taxon, location |
| LO_004 | local | taxon, location |
| LO_005 | local | taxon, location |
| LO_006 | local | disease, taxon |
| SL_001 | species-location | taxon, location, production_mode |
| SL_004 | species-location | taxon, location |
| SL_006 | species-location | taxon, location, production_mode |
| SL_007 | species-location | taxon, location, production_mode |

## Illustrative Cases

### disease-specific: `DS_001`

- Query: bệnh AHPND trên tôm
- Runtime profile: `disease_priority`
- Disease: AHPND
- Taxon/species: tôm
- Location: -
- Production mode: -
- Topic/management/prevention: -
- Signal priority: KG disease facts + metadata disease + vector; disease evidence should dominate. Runtime flags: disease_priority, species_priority.
- Why this profile is reasonable: query-set group is `disease-specific`, and runtime entities provide the scoring context shown above.

### species-location: `SL_001`

- Query: nuôi tôm sú và trại giống tại Bangladesh
- Runtime profile: `species_priority`
- Disease: -
- Taxon/species: Penaeus monodon
- Location: Bangladesh
- Production mode: hatchery aquaculture
- Topic/management/prevention: -
- Signal priority: metadata species/location + vector; KG location/taxon facts and intent guardrails are secondary. Runtime flags: species_priority, location-sensitive, mode-sensitive.
- Why this profile is reasonable: query-set group is `species-location`, and runtime entities provide the scoring context shown above.

### hatchery-production-mode: `HM_001`

- Query: production mode trại giống tôm thẻ chân trắng
- Runtime profile: `species_priority`
- Disease: -
- Taxon/species: Penaeus vannamei
- Location: -
- Production mode: hatchery aquaculture
- Topic/management/prevention: -
- Signal priority: production_mode metadata + species + vector; KG mode and hatchery intent guardrails are important. Runtime flags: species_priority, mode-sensitive.
- Why this profile is reasonable: query-set group is `hatchery-production-mode`, and runtime entities provide the scoring context shown above.

### biosecurity-management: `BI_001`

- Query: biosecurity trong hatchery tôm thẻ chân trắng
- Runtime profile: `species_priority`
- Disease: -
- Taxon/species: Penaeus vannamei
- Location: -
- Production mode: hatchery aquaculture
- Topic/management/prevention: topic: biosecurity; prevention: An toàn sinh học
- Signal priority: vector semantics + topic/management/prevention aliases; KG prevention/management context is supporting evidence. Runtime flags: species_priority, mode-sensitive, topic/management context.
- Why this profile is reasonable: query-set group is `biosecurity-management`, and runtime entities provide the scoring context shown above.

### local: `LO_001`

- Query: nuôi tôm hùm ở Khánh Hòa
- Runtime profile: `species_priority`
- Disease: -
- Taxon/species: lobster
- Location: Khanh Hoa
- Production mode: -
- Topic/management/prevention: -
- Signal priority: location metadata/KG + lexical exact terms + vector; guardrails should protect local aquaculture intent. Runtime flags: species_priority, location-sensitive.
- Why this profile is reasonable: query-set group is `local`, and runtime entities provide the scoring context shown above.

## Ambiguous or Uncertain Queries

| query_id | query_group | runtime_profile | note |
| --- | --- | --- | --- |
| BI_007 | biosecurity-management | generic | Linked error-analysis note: missing_alias |
| DS_006 | disease-specific | disease_priority | Linked error-analysis note: not_error_but_baseline_limitation |
| DS_007 | disease-specific | species_priority | Expected disease-specific intent but runtime disease entity is missing. Linked error-analysis note: missing_disease_fact |
| HM_001 | hatchery-production-mode | species_priority | Linked error-analysis note: weak_candidate_pool |
| HM_010 | hatchery-production-mode | species_priority | Linked error-analysis note: metadata_incomplete |
| LO_001 | local | species_priority | Linked error-analysis note: weak_candidate_pool |
| LO_003 | local | species_priority | Linked error-analysis note: missing_location_fact |
| LO_005 | local | species_priority | Linked error-analysis note: missing_location_fact |
| LO_006 | local | disease_priority | Location-sensitive query with no runtime location entity. |
| LO_007 | local | species_priority | Location-sensitive query with no runtime location entity. |
| SL_001 | species-location | species_priority | Linked error-analysis note: scoring_or_intent_issue |
| SL_002 | species-location | species_priority | Location-sensitive query with no runtime location entity. |
| SL_004 | species-location | species_priority | Linked error-analysis note: not_error_but_baseline_limitation |

## Limitations

- Query understanding depends on aliases, metadata values, and KG labels available in the current snapshot.
- Missing aliases can cause entity linking to miss disease, location, production mode, or management concepts.
- `detected_profile` is a runtime scoring profile, not a ground-truth semantic label.
- `inferred_profile` follows the query-set group when available, so it is useful for thesis explanation but not a learned classifier.
- Topic/management/prevention coverage is intentionally limited and should not be overclaimed as full intent understanding.

Generated at: `2026-05-23T16:31:44.668591+00:00`
