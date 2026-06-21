# Ontology Reasoner-based Consistency Check

## Purpose

This report checks the official runtime ontology with an OWL reasoner when the local environment supports it.
It is distinct from the existing runtime-oriented quality check.

## Ontology

- Ontology file: `data\ontology\taxon_enriched_facts_v2.owl`
- Check time: `2026-05-23T16:07:27.500805+00:00`
- Python: `3.13.3 (tags/v3.13.3:6280bb5, Apr  8 2025, 14:47:33)`
- Owlready2: `0.50`
- pip install attempted in this task: `True`

## Tooling Attempted

- `java`: available - java version "17.0.12" 2024-07-16 LTS Java(TM) SE Runtime Environment (build 17.0.12+8-LTS-286) Java HotSpot(TM) 64-Bit Server VM (build 17.0.12+8-LTS-286, mixed mode, sharing)
- `external_hermit_or_pellet_jar_search`: not_available - No HermiT/Pellet jar found in project root, tools/, lib/, reasoners/, or bin/.
- `owlready2_pellet`: failed - OwlReadyJavaError: Java error message is: Exception in thread "main" java.lang.UnsupportedClassVersionError: org/apache/jena/riot/lang/LangRDFXML has been compiled by a more recent version of the Java Runtime (class file version 69.0), this version of the Java ... (full details in JSON)
- `owlready2_hermit`: completed - Reasoner completed.

## Result

- Check status: `completed`
- Reasoner used: `owlready2_hermit`
- is_consistent: `True`
- Unsatisfiable classes count: 0
- No unsatisfiable classes detected.

## Warnings and Notes

- This report is separate from the runtime-oriented ontology quality/coverage check.
- Runtime-oriented checks inspect structural statistics, document mapping, fact coverage, and dangling objects.
- Reasoner-based checks evaluate OWL logical consistency/class satisfiability when a reasoner can run.

## Difference from Runtime-oriented Quality Check

- The previous runtime-oriented quality check reports structural statistics, document mapping, fact coverage, dangling fact objects, duplicate local names, and label coverage.
- This reasoner-based check attempts to evaluate OWL logical consistency and class satisfiability using a reasoner.
- A successful structural/coverage check does not prove OWL consistency.
- A failed or unavailable reasoner check must not be interpreted as proof that the ontology is consistent.

## Limitations

- No ontology, metadata, query set, relevance judgments, baseline outputs, or metric files are modified.
- If no reasoner completes, this report must not be used as proof of consistency.
- If a reasoner completes, the result is scoped to the loaded ontology file and the selected reasoner/tool behavior.
- This report does not replace runtime-oriented coverage checks or competency-question evaluation.

## Conclusion

Ontology is consistent under owlready2_hermit. No unsatisfiable classes detected.
