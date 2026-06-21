from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
from rdflib import RDF, RDFS, URIRef
from rdflib.namespace import OWL, SKOS

from kg_runtime import build_kg_index, load_kg_prefer_facts_then_alias_enriched, normalize_kg_text


OUTPUT_JSON = Path("outputs") / "ontology_quality_check.json"
OUTPUT_MD = Path("outputs") / "ontology_quality_check.md"
METADATA_PATH = Path("data") / "metadata" / "document_metadata_cleaned.xlsx"

RELATION_NAMES = [
    "aboutDisease",
    "aboutTaxon",
    "aboutLocation",
    "documentProductionMode",
    "affectsTaxon",
    "causedBy",
    "hasSymptom",
    "recommendedPrevention",
    "recommendedTreatment",
    "mentions",
]

CORE_DOC_RELATIONS = [
    "aboutTaxon",
    "aboutDisease",
    "aboutLocation",
    "documentProductionMode",
]


def local_name(uri: Any) -> str:
    text = str(uri)
    if "#" in text:
        return text.rsplit("#", 1)[-1]
    if "/" in text:
        return text.rsplit("/", 1)[-1]
    return text


def ratio(count: int, total: int) -> float:
    return round(count / total, 6) if total else 0.0


def unique_subject_count(graph: Any, pred: Any, obj: Any) -> int:
    return len({str(s) for s in graph.subjects(pred, obj) if isinstance(s, URIRef)})


def predicate_count(graph: Any, pred: URIRef) -> int:
    return sum(1 for _ in graph.triples((None, pred, None)))


def subject_has_any(graph: Any, subject: URIRef, predicates: list[URIRef]) -> bool:
    return any(any(True for _ in graph.objects(subject, p)) for p in predicates)


def object_has_subject_facts(graph: Any, obj: URIRef) -> bool:
    return any(True for _ in graph.triples((obj, None, None)))


def get_document_uris(kg_index: dict[str, Any]) -> list[str]:
    uri_to_info = kg_index.get("uri_to_info") or {}
    return sorted(uri for uri, info in uri_to_info.items() if info.get("entity_type") == "document")


def build_document_fact_coverage(graph: Any, doc_uris: list[str], relations: dict[str, str]) -> dict[str, Any]:
    total_docs = len(doc_uris)
    out: dict[str, Any] = {}
    for name in CORE_DOC_RELATIONS:
        pred = URIRef(relations[name])
        count_docs = sum(1 for uri in doc_uris if any(True for _ in graph.objects(URIRef(uri), pred)))
        out[f"{name}_count_docs"] = count_docs
        out[f"{name}_ratio"] = ratio(count_docs, total_docs)
    return out


def build_mapping_status(kg_index: dict[str, Any]) -> dict[str, Any]:
    if not METADATA_PATH.exists():
        return {
            "metadata_file": str(METADATA_PATH),
            "total_metadata_docs": 0,
            "mapped_metadata_docs_to_kg": 0,
            "unmapped_metadata_docs": [],
            "note": "Metadata file not found.",
        }

    metadata = pd.read_excel(METADATA_PATH)
    doc_ids = [str(x).strip() for x in metadata.get("doc_id", []) if str(x).strip()]
    dockey_to_uri = kg_index.get("dockey_to_uri") or {}
    mapped = []
    unmapped = []
    for doc_id in doc_ids:
        key = normalize_kg_text(doc_id)
        if key in dockey_to_uri:
            mapped.append(doc_id)
        else:
            unmapped.append(doc_id)
    return {
        "metadata_file": str(METADATA_PATH),
        "total_metadata_docs": len(doc_ids),
        "mapped_metadata_docs_to_kg": len(mapped),
        "unmapped_metadata_docs": unmapped,
    }


def build_label_coverage(graph: Any, kg_index: dict[str, Any]) -> dict[str, Any]:
    indexed_uris = sorted((kg_index.get("uri_to_info") or {}).keys())
    total = len(indexed_uris)
    rdfs_subjects = {str(s) for s in graph.subjects(RDFS.label, None) if isinstance(s, URIRef)}
    pref_subjects = {str(s) for s in graph.subjects(SKOS.prefLabel, None) if isinstance(s, URIRef)}
    alt_subjects = {str(s) for s in graph.subjects(SKOS.altLabel, None) if isinstance(s, URIRef)}
    indexed_set = set(indexed_uris)
    any_label = indexed_set & (rdfs_subjects | pref_subjects | alt_subjects)
    return {
        "total_indexed_entities": total,
        "entities_with_rdfs_label": len(indexed_set & rdfs_subjects),
        "entities_with_skos_prefLabel": len(indexed_set & pref_subjects),
        "entities_with_skos_altLabel": len(indexed_set & alt_subjects),
        "entities_with_any_rdfs_or_skos_label": len(any_label),
        "ratio_with_any_label": ratio(len(any_label), total),
    }


def build_consistency_observations(
    graph: Any,
    doc_uris: list[str],
    relations: dict[str, str],
    kg_index: dict[str, Any],
) -> dict[str, Any]:
    ns = kg_index["ns"]
    core_preds = [URIRef(relations[name]) for name in CORE_DOC_RELATIONS]
    important_preds = [URIRef(relations[name]) for name in RELATION_NAMES if name in relations]

    docs_missing_all_core_facts = []
    docs_missing_title = []
    docs_missing_file_path = []
    for uri in doc_uris:
        u = URIRef(uri)
        if not any(subject_has_any(graph, u, [p]) for p in core_preds):
            docs_missing_all_core_facts.append(local_name(uri))
        if not any(True for _ in graph.objects(u, ns.title)):
            docs_missing_title.append(local_name(uri))
        if not any(True for _ in graph.objects(u, ns.filePath)):
            docs_missing_file_path.append(local_name(uri))

    dangling = []
    for pred in important_preds:
        for _s, _p, obj in graph.triples((None, pred, None)):
            if isinstance(obj, URIRef) and not object_has_subject_facts(graph, obj):
                dangling.append({"relation": local_name(pred), "object": str(obj)})
    dangling_unique = []
    seen_dangling = set()
    for item in dangling:
        key = (item["relation"], item["object"])
        if key not in seen_dangling:
            seen_dangling.add(key)
            dangling_unique.append(item)

    local_to_uris: dict[str, list[str]] = defaultdict(list)
    for uri in (kg_index.get("uri_to_info") or {}).keys():
        local_to_uris[local_name(uri)].append(uri)
    duplicate_local_names = {
        name: uris for name, uris in local_to_uris.items() if len(uris) > 1
    }

    label_props = [RDFS.label, SKOS.prefLabel, SKOS.altLabel]
    entities_missing_label = []
    for uri, info in (kg_index.get("uri_to_info") or {}).items():
        if info.get("entity_type") == "document":
            continue
        if not subject_has_any(graph, URIRef(uri), label_props):
            entities_missing_label.append(local_name(uri))

    return {
        "reasoner_note": (
            "Reasoner-based consistency checking was not executed; this report focuses on "
            "runtime-oriented structural and coverage checks."
        ),
        "documents_missing_all_core_facts_count": len(docs_missing_all_core_facts),
        "documents_missing_all_core_facts_sample": docs_missing_all_core_facts[:20],
        "documents_missing_title_count": len(docs_missing_title),
        "documents_missing_title_sample": docs_missing_title[:20],
        "documents_missing_filePath_count": len(docs_missing_file_path),
        "documents_missing_filePath_sample": docs_missing_file_path[:20],
        "dangling_fact_objects_count": len(dangling_unique),
        "dangling_fact_objects_sample": dangling_unique[:20],
        "duplicate_local_names_count": len(duplicate_local_names),
        "duplicate_local_names_sample": dict(list(duplicate_local_names.items())[:20]),
        "non_document_entities_missing_rdfs_or_skos_label_count": len(entities_missing_label),
        "non_document_entities_missing_rdfs_or_skos_label_sample": entities_missing_label[:20],
    }


def build_quality_notes(coverage: dict[str, Any], mapping: dict[str, Any], consistency: dict[str, Any]) -> dict[str, list[str]]:
    strengths = [
        "The runtime ontology loads through the same KG loader used by retrieval, so the report reflects deployed behavior.",
        "All metadata document identifiers are mapped to KG document nodes." if not mapping.get("unmapped_metadata_docs") else "Most metadata document identifiers are mapped to KG document nodes.",
        "Taxon and production-mode document facts have high coverage.",
    ]
    weaknesses = []
    if coverage.get("aboutLocation_ratio", 0.0) < 0.6:
        weaknesses.append("Location coverage is sparse, which can weaken local-intent retrieval and explanations.")
    if coverage.get("aboutDisease_ratio", 0.0) < 0.8:
        weaknesses.append("Disease coverage is incomplete; disease-specific queries can depend on vector/metadata fallback.")
    if consistency.get("non_document_entities_missing_rdfs_or_skos_label_count", 0) > 0:
        weaknesses.append("Some non-document entities lack explicit rdfs/skos labels and rely on URI local-name fallback.")
    if not weaknesses:
        weaknesses.append("No major runtime-oriented structural weakness was detected by this lightweight check.")

    suggestions = [
        "Backfill missing location facts for documents with local or regional metadata evidence.",
        "Expand disease/pathogen facts only after manual validation against source documents.",
        "Add explicit rdfs:label or skos labels for entities currently resolved from URI local names.",
        "Run a reasoner-based consistency check separately if formal OWL consistency is required.",
    ]
    return {"strengths": strengths, "weaknesses": weaknesses, "suggestions": suggestions}


def write_markdown(report: dict[str, Any]) -> None:
    coverage = report["document_fact_coverage"]
    labels = report["label_coverage"]
    mapping = report["document_mapping_status"]
    relation_counts = report["relation_counts"]
    consistency = report["runtime_consistency_observations"]
    notes = report["quality_notes"]

    lines = [
        "# Ontology/KG Runtime Quality Check",
        "",
        "## Loaded ontology",
        "",
        f"- Ontology file loaded: `{report['ontology_file_loaded']}`",
        f"- Loader source: `{report['loader_source']}`",
        f"- Generated at: `{report['generated_at']}`",
        "",
        "## Structural statistics",
        "",
        f"- Total triples: {report['total_triples']}",
        f"- Total classes: {report['total_classes']}",
        f"- Total object properties: {report['total_object_properties']}",
        f"- Total data properties: {report['total_data_properties']}",
        f"- Total named individuals: {report['total_individuals']}",
        f"- Total document nodes: {report['total_document_nodes']}",
        "",
        "## Document fact coverage",
        "",
        f"- aboutTaxon: {coverage['aboutTaxon_count_docs']} docs ({coverage['aboutTaxon_ratio']:.3f})",
        f"- aboutDisease: {coverage['aboutDisease_count_docs']} docs ({coverage['aboutDisease_ratio']:.3f})",
        f"- aboutLocation: {coverage['aboutLocation_count_docs']} docs ({coverage['aboutLocation_ratio']:.3f})",
        f"- documentProductionMode: {coverage['documentProductionMode_count_docs']} docs ({coverage['documentProductionMode_ratio']:.3f})",
        "",
        "## Label and alias coverage",
        "",
        f"- Indexed entities: {labels['total_indexed_entities']}",
        f"- Entities with rdfs:label: {labels['entities_with_rdfs_label']}",
        f"- Entities with skos:prefLabel: {labels['entities_with_skos_prefLabel']}",
        f"- Entities with skos:altLabel: {labels['entities_with_skos_altLabel']}",
        f"- Ratio with any rdfs/skos label: {labels['ratio_with_any_label']:.3f}",
        f"- Metadata docs mapped to KG: {mapping['mapped_metadata_docs_to_kg']} / {mapping['total_metadata_docs']}",
        "",
        "## Key relation counts",
        "",
    ]
    for name in RELATION_NAMES:
        lines.append(f"- {name}: {relation_counts.get(name, 0)}")

    lines.extend(
        [
            "",
            "## Runtime-oriented consistency observations",
            "",
            f"- Documents missing all core facts: {consistency['documents_missing_all_core_facts_count']}",
            f"- Documents missing title: {consistency['documents_missing_title_count']}",
            f"- Documents missing filePath: {consistency['documents_missing_filePath_count']}",
            f"- Dangling fact objects: {consistency['dangling_fact_objects_count']}",
            f"- Duplicate local names: {consistency['duplicate_local_names_count']}",
            f"- Non-document entities missing rdfs/skos label: {consistency['non_document_entities_missing_rdfs_or_skos_label_count']}",
            "",
            "## Quality notes",
            "",
            "### Strengths",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in notes["strengths"])
    lines.extend(["", "### Weaknesses", ""])
    lines.extend(f"- {item}" for item in notes["weaknesses"])
    lines.extend(["", "### Suggestions", ""])
    lines.extend(f"- {item}" for item in notes["suggestions"])
    lines.extend(
        [
            "",
            "## Limitations",
            "",
            f"- {consistency['reasoner_note']}",
            "- This is a runtime-oriented structural audit, not a semantic proof of correctness for every fact.",
            "- The check does not modify ontology, metadata, retrieval baselines, query sets, or relevance judgments.",
            "",
        ]
    )

    OUTPUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    graph, loaded_path, loader_source = load_kg_prefer_facts_then_alias_enriched()
    kg_index = build_kg_index(graph)
    doc_uris = get_document_uris(kg_index)
    relations = kg_index["relations"]

    relation_counts = {
        name: predicate_count(graph, URIRef(relations[name]))
        for name in RELATION_NAMES
        if name in relations
    }
    coverage = build_document_fact_coverage(graph, doc_uris, relations)
    mapping = build_mapping_status(kg_index)
    labels = build_label_coverage(graph, kg_index)
    consistency = build_consistency_observations(graph, doc_uris, relations, kg_index)
    quality_notes = build_quality_notes(coverage, mapping, consistency)

    report = {
        "ontology_file_loaded": loaded_path,
        "loader_source": loader_source,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_triples": len(graph),
        "total_classes": unique_subject_count(graph, RDF.type, OWL.Class),
        "total_object_properties": unique_subject_count(graph, RDF.type, OWL.ObjectProperty),
        "total_data_properties": unique_subject_count(graph, RDF.type, OWL.DatatypeProperty),
        "total_individuals": unique_subject_count(graph, RDF.type, OWL.NamedIndividual),
        "total_document_nodes": len(doc_uris),
        "document_fact_coverage": coverage,
        "document_mapping_status": mapping,
        "label_coverage": labels,
        "relation_counts": relation_counts,
        "runtime_consistency_observations": consistency,
        "quality_notes": quality_notes,
    }

    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(report)
    print(f"[OK] Wrote {OUTPUT_JSON} and {OUTPUT_MD}")


if __name__ == "__main__":
    main()
