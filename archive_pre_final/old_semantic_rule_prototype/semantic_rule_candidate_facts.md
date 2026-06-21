# Semantic Rule Candidate Facts Prototype

## Purpose

This prototype generates candidate semantic-rule evidence from existing ontology/KG facts and metadata.
It does not assert new triples, does not modify the ontology, and does not change retrieval baselines or hybrid scoring.

## Inputs Read

- `data\ontology\taxon_enriched_facts_v2.owl`
- `data\metadata\document_metadata_cleaned.xlsx`
- `outputs\query_understanding_profiles.csv`
- `outputs\error_analysis_core.csv`
- `outputs\ontology_quality_check.json`
- `outputs\semantic_rules_and_label_strategy.md`

## Rule Groups Checked

1. Disease-pathogen-symptom-prevention-treatment.
2. Taxon-location-production mode.
3. Document-level safe facts / safe evidence.

## Candidate Evidence Summary

- Total candidate evidence rows: 889
- All `should_assert` values are false: `True`

### By Rule Group

| rule_group | count |
| --- | --- |
| disease-pathogen-symptom-prevention-treatment | 19 |
| document-level safe facts / safe evidence | 458 |
| taxon-location-production mode | 412 |

### By Rule Name

| rule_name | count |
| --- | --- |
| disease_has_pathogen_context | 3 |
| disease_has_symptom_context | 7 |
| disease_has_prevention_context | 5 |
| disease_has_treatment_context | 4 |
| document_inherits_pathogen_context_from_aboutDisease | 57 |
| document_inherits_symptom_context_from_aboutDisease | 153 |
| document_inherits_prevention_context_from_aboutDisease | 105 |
| document_inherits_treatment_context_from_aboutDisease | 96 |
| taxon_isFoundIn_location_context | 11 |
| document_taxon_production_mode_context | 200 |
| document_taxon_location_context | 99 |
| document_taxon_location_production_mode_context | 102 |
| metadata_location_matches_kg_location_evidence | 47 |

## Representative Examples

| id | group | rule | subject | predicate | object | source evidence |
| --- | --- | --- | --- | --- | --- | --- |
| SRC_0001 | disease-pathogen-symptom-prevention-treatment | disease_has_pathogen_context | Infectious myonecrosis | hasPathogenContext | Infectious myonecrosis virus | IMN causedBy IMNV |
| SRC_0004 | disease-pathogen-symptom-prevention-treatment | disease_has_symptom_context | Infectious myonecrosis | hasSymptomContext | Lờ đờ | IMN hasSymptom Letargy |
| SRC_0011 | disease-pathogen-symptom-prevention-treatment | disease_has_prevention_context | Infectious myonecrosis | hasPreventionContext | An toàn sinh học | IMN recommendedPrevention Biosecurity |
| SRC_0016 | disease-pathogen-symptom-prevention-treatment | disease_has_treatment_context | Bệnh hoại tử gan tụy cấp | hasTreatmentContext | Tăng sục khí | AHPND recommendedTreatment ImproveAeration |
| SRC_0020 | document-level safe facts / safe evidence | document_inherits_pathogen_context_from_aboutDisease | BIOLOGY_001 | candidateHasPathogenContext | Virus đốm trắng (WSSV) | BIOLOGY_001 aboutDisease WhiteSpotDisease; WhiteSpotDisease causedBy WSSV |
| SRC_0444 | taxon-location-production mode | document_taxon_location_context | FAO_001 | candidateHasTaxonLocationContext | shrimp | Toàn cầu | FAO_001 aboutTaxon Generic_Shrimp; FAO_001 aboutLocation Global |
| SRC_0442 | taxon-location-production mode | document_taxon_production_mode_context | BIOLOGY_001 | candidateHasTaxonProductionModeContext | Tôm thẻ chân trắng | Nuôi trồng | BIOLOGY_001 aboutTaxon Tom_the_chan_trang; BIOLOGY_001 documentProductionMode Aquaculture |
| SRC_0446 | taxon-location-production mode | document_taxon_location_production_mode_context | FAO_001 | candidateHasTaxonLocationModeContext | shrimp | Toàn cầu | Nuôi trồng | FAO_001 aboutTaxon Generic_Shrimp; FAO_001 aboutLocation Global; FAO_001 documentProductionMode Aquaculture |
| SRC_0843 | document-level safe facts / safe evidence | metadata_location_matches_kg_location_evidence | FAO_001 | candidateHasSafeLocationEvidence | Toàn cầu | metadata.related_location=Global; KG aboutLocation=Global |

## Missing or Sparse Rule Support

- Sparse `causedBy` relations: 3 triples.
- Sparse `recommendedTreatment` relations: 4 triples.
- No explicit location hierarchy relation such as partOf/isLocatedIn was found; only direct locations and isFoundIn can be used.

## Potential KG Scoring Opportunities

- Opportunity rows generated: 7
| opportunity_id | query_id | weak_signal | potential_use | recommendation |
| --- | --- | --- | --- | --- |
| OPP_001 | LO_005 | Local query depends on sparse or missing structured location facts. | Boost documents with direct or metadata-backed location evidence for local queries. | Keep exact local evidence stronger than broad country evidence. |
| OPP_002 | DS_007 | Pathogen-centered disease query lacks strong pathogen bridge. | Add low-weight pathogen-context evidence when query mentions pathogen and doc is about linked disease. | Use as soft scoring evidence only after manual validation. |
| OPP_003 | BI_007 | Topic alias is missing or weak. | Improve entity detection before using KG scoring. | Add aliases only after manual review; do not auto-assert triples. |
| OPP_004 | HM_001 | Hatchery/taxon/life-stage context is incomplete or weak. | Add field-aware soft boost for taxon+production-mode matches. | Tune only after adding reviewed hatchery/life-stage aliases. |
| OPP_005 | LO_001 | Local/taxon document is weakly represented in the candidate pool. | Use KG/SPARQL-side evidence as a recall backstop when vector candidates miss local documents. | Treat as retrieval architecture future work; verify corpus/index coverage before scoring changes. |
| OPP_006 | LO_003 | Local query depends on sparse or missing structured location facts. | Boost documents with direct or metadata-backed location evidence for local queries. | Keep exact local evidence stronger than broad country evidence. |
| OPP_007 | HM_010 | Hatchery/taxon/life-stage context is incomplete or weak. | Add field-aware soft boost for taxon+production-mode matches. | Tune only after adding reviewed hatchery/life-stage aliases. |

## Limitations

- These rows are candidate evidence, not asserted ontology facts.
- `should_assert` is false for every row; manual review is required before any ontology update.
- This prototype does not prove ranking improvement because no scoring experiment is run here.
- It does not replace reasoner consistency checking, competency questions, or retrieval evaluation.
- Some rule groups are limited by sparse KG facts, especially explicit location hierarchy and some disease-context relations.

## Conclusion

This prototype is useful as an academic/future-work artifact for controlled semantic-rule design. It should not be moved into runtime scoring until candidate evidence is reviewed and a separate retrieval experiment validates the effect.

Generated at: `2026-05-23T16:40:58.015226+00:00`
