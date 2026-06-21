from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
from rdflib import URIRef

import kg_runtime
from kg_runtime import get_document_facts, get_entity_neighbors


ONTOLOGY_PATH = Path("data") / "ontology" / "taxon_enriched_facts_v2.owl"
METADATA_PATH = Path("data") / "metadata" / "document_metadata_cleaned.xlsx"
QUERY_PROFILES = Path("outputs") / "query_understanding_profiles.csv"
ERROR_ANALYSIS = Path("outputs") / "error_analysis_core.csv"
QUALITY_CHECK = Path("outputs") / "ontology_quality_check.json"
LABEL_STRATEGY = Path("outputs") / "semantic_rules_and_label_strategy.md"

OUTPUT_CSV = Path("outputs") / "semantic_rule_candidate_facts.csv"
OUTPUT_JSON = Path("outputs") / "semantic_rule_candidate_facts.json"
OUTPUT_MD = Path("outputs") / "semantic_rule_candidate_facts.md"
OPPORTUNITIES_CSV = Path("outputs") / "semantic_rule_scoring_opportunities.csv"

CANDIDATE_FIELDS = [
    "candidate_id",
    "rule_group",
    "rule_name",
    "subject_type",
    "subject_id",
    "predicate",
    "object_type",
    "object_id",
    "source_evidence",
    "confidence_level",
    "should_assert",
    "reason_not_asserted",
    "example_query_ids_if_relevant",
    "note",
]

OPPORTUNITY_FIELDS = [
    "opportunity_id",
    "related_query_id",
    "query_group",
    "missing_or_weak_signal",
    "candidate_rule_evidence",
    "potential_scoring_use",
    "risk",
    "recommendation",
]


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in fields})


def local_name(uri: Any) -> str:
    text = str(uri)
    if "#" in text:
        return text.rsplit("#", 1)[-1]
    if "/" in text:
        return text.rsplit("/", 1)[-1]
    return text


def label(uri: str, kg_index: dict[str, Any]) -> str:
    info = (kg_index.get("uri_to_info") or {}).get(str(uri), {})
    return str(info.get("label") or local_name(uri))


def entity_type(uri: str, kg_index: dict[str, Any]) -> str:
    info = (kg_index.get("uri_to_info") or {}).get(str(uri), {})
    return str(info.get("entity_type") or "entity")


def make_candidate(
    candidate_id: str,
    rule_group: str,
    rule_name: str,
    subject_type: str,
    subject_id: str,
    predicate: str,
    object_type: str,
    object_id: str,
    source_evidence: str,
    confidence_level: str,
    example_query_ids_if_relevant: str = "",
    note: str = "",
) -> dict[str, Any]:
    return {
        "candidate_id": candidate_id,
        "rule_group": rule_group,
        "rule_name": rule_name,
        "subject_type": subject_type,
        "subject_id": subject_id,
        "predicate": predicate,
        "object_type": object_type,
        "object_id": object_id,
        "source_evidence": source_evidence,
        "confidence_level": confidence_level,
        "should_assert": "false",
        "reason_not_asserted": "candidate only; manual review required",
        "example_query_ids_if_relevant": example_query_ids_if_relevant,
        "note": note,
    }


def build_query_index() -> dict[str, list[str]]:
    out: dict[str, list[str]] = defaultdict(list)
    for row in read_csv_rows(QUERY_PROFILES):
        qid = row.get("query_id", "")
        blob = " ".join(
            [
                row.get("detected_disease_entities", ""),
                row.get("detected_taxon_entities", ""),
                row.get("detected_location_entities", ""),
                row.get("detected_production_mode_entities", ""),
                row.get("detected_topic_or_management_entities", ""),
                row.get("canonical_entities", ""),
                row.get("query_text", ""),
            ]
        )
        for token in [
            "AHPND",
            "WSSV",
            "IMN",
            "Vibrio",
            "Penaeus vannamei",
            "Penaeus monodon",
            "lobster",
            "Khanh Hoa",
            "Bangladesh",
            "Thailand",
            "hatchery",
            "biosecurity",
        ]:
            if kg_runtime.normalize_kg_text(token) in kg_runtime.normalize_kg_text(blob):
                out[token].append(qid)
    return out


def relevant_queries_for_labels(labels: list[str], query_index: dict[str, list[str]]) -> str:
    found: list[str] = []
    for key, qids in query_index.items():
        key_norm = kg_runtime.normalize_kg_text(key)
        if any(key_norm and key_norm in kg_runtime.normalize_kg_text(x) for x in labels):
            for qid in qids:
                if qid not in found:
                    found.append(qid)
    return ";".join(found[:8])


def doc_id_from_uri(uri: str) -> str:
    return local_name(uri)


def metadata_by_doc() -> dict[str, dict[str, Any]]:
    if not METADATA_PATH.exists():
        return {}
    df = pd.read_excel(METADATA_PATH)
    out: dict[str, dict[str, Any]] = {}
    for _, row in df.iterrows():
        did = str(row.get("doc_id", "")).strip()
        if did:
            out[did] = row.to_dict()
    return out


def generate_candidates() -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    graph, loaded_path, source = kg_runtime.load_kg_prefer_facts_then_alias_enriched()
    kg_index = kg_runtime.build_kg_index(graph)
    relations = kg_index["relations"]
    uri_to_info = kg_index["uri_to_info"]
    query_index = build_query_index()
    meta = metadata_by_doc()

    candidates: list[dict[str, Any]] = []
    cid = 1

    def add(**kwargs: Any) -> None:
        nonlocal cid
        candidates.append(make_candidate(candidate_id=f"SRC_{cid:04d}", **kwargs))
        cid += 1

    # Group 1: disease-pathogen-symptom-prevention-treatment.
    disease_context_rels = [
        ("causedBy", "disease_has_pathogen_context", "pathogen", "hasPathogenContext"),
        ("hasSymptom", "disease_has_symptom_context", "symptom", "hasSymptomContext"),
        ("recommendedPrevention", "disease_has_prevention_context", "prevention", "hasPreventionContext"),
        ("recommendedTreatment", "disease_has_treatment_context", "treatment", "hasTreatmentContext"),
    ]
    disease_context: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    for rel_name, rule_name, obj_type, predicate in disease_context_rels:
        pred = URIRef(relations[rel_name])
        for s, _p, o in graph.triples((None, pred, None)):
            if not isinstance(s, URIRef) or not isinstance(o, URIRef):
                continue
            s_uri, o_uri = str(s), str(o)
            disease_context[s_uri].append((rel_name, obj_type, o_uri))
            add(
                rule_group="disease-pathogen-symptom-prevention-treatment",
                rule_name=rule_name,
                subject_type="disease",
                subject_id=label(s_uri, kg_index),
                predicate=predicate,
                object_type=obj_type,
                object_id=label(o_uri, kg_index),
                source_evidence=f"{local_name(s_uri)} {rel_name} {local_name(o_uri)}",
                confidence_level="high",
                example_query_ids_if_relevant=relevant_queries_for_labels([label(s_uri, kg_index), label(o_uri, kg_index)], query_index),
                note="Direct disease-level KG relation; candidate evidence only.",
            )

    doc_uris = sorted([u for u, info in uri_to_info.items() if info.get("entity_type") == "document"])
    for doc_uri in doc_uris:
        facts = get_document_facts(graph, doc_uri)
        doc_label = label(doc_uri, kg_index)
        for disease_uri in facts.get("disease", []):
            for rel_name, obj_type, obj_uri in disease_context.get(disease_uri, []):
                add(
                    rule_group="document-level safe facts / safe evidence",
                    rule_name=f"document_inherits_{obj_type}_context_from_aboutDisease",
                    subject_type="document",
                    subject_id=doc_id_from_uri(doc_uri),
                    predicate=f"candidateHas{obj_type.title()}Context",
                    object_type=obj_type,
                    object_id=label(obj_uri, kg_index),
                    source_evidence=(
                        f"{doc_id_from_uri(doc_uri)} aboutDisease {local_name(disease_uri)}; "
                        f"{local_name(disease_uri)} {rel_name} {local_name(obj_uri)}"
                    ),
                    confidence_level="medium",
                    example_query_ids_if_relevant=relevant_queries_for_labels([doc_label, label(disease_uri, kg_index), label(obj_uri, kg_index)], query_index),
                    note="Safe contextual evidence derived from direct document disease fact; not asserted as document fact.",
                )

    # Group 2: taxon-location-production mode.
    for s, _p, o in graph.triples((None, URIRef(relations["isFoundIn"]), None)):
        if isinstance(s, URIRef) and isinstance(o, URIRef):
            add(
                rule_group="taxon-location-production mode",
                rule_name="taxon_isFoundIn_location_context",
                subject_type="taxon",
                subject_id=label(str(s), kg_index),
                predicate="hasLocationRangeContext",
                object_type="location",
                object_id=label(str(o), kg_index),
                source_evidence=f"{local_name(s)} isFoundIn {local_name(o)}",
                confidence_level="high",
                example_query_ids_if_relevant=relevant_queries_for_labels([label(str(s), kg_index), label(str(o), kg_index)], query_index),
                note="Direct taxon-location KG relation.",
            )

    for doc_uri in doc_uris:
        facts = get_document_facts(graph, doc_uri)
        doc_id = doc_id_from_uri(doc_uri)
        for taxon_uri in facts.get("species", []):
            for loc_uri in facts.get("location", []):
                add(
                    rule_group="taxon-location-production mode",
                    rule_name="document_taxon_location_context",
                    subject_type="document",
                    subject_id=doc_id,
                    predicate="candidateHasTaxonLocationContext",
                    object_type="taxon_location_pair",
                    object_id=f"{label(taxon_uri, kg_index)} | {label(loc_uri, kg_index)}",
                    source_evidence=f"{doc_id} aboutTaxon {local_name(taxon_uri)}; {doc_id} aboutLocation {local_name(loc_uri)}",
                    confidence_level="high",
                    example_query_ids_if_relevant=relevant_queries_for_labels([label(taxon_uri, kg_index), label(loc_uri, kg_index)], query_index),
                    note="Direct document-level taxon and location facts.",
                )
            for mode_uri in facts.get("mode", []):
                add(
                    rule_group="taxon-location-production mode",
                    rule_name="document_taxon_production_mode_context",
                    subject_type="document",
                    subject_id=doc_id,
                    predicate="candidateHasTaxonProductionModeContext",
                    object_type="taxon_mode_pair",
                    object_id=f"{label(taxon_uri, kg_index)} | {label(mode_uri, kg_index)}",
                    source_evidence=f"{doc_id} aboutTaxon {local_name(taxon_uri)}; {doc_id} documentProductionMode {local_name(mode_uri)}",
                    confidence_level="high",
                    example_query_ids_if_relevant=relevant_queries_for_labels([label(taxon_uri, kg_index), label(mode_uri, kg_index)], query_index),
                    note="Direct document-level taxon and production mode facts.",
                )
            for loc_uri in facts.get("location", []):
                for mode_uri in facts.get("mode", []):
                    add(
                        rule_group="taxon-location-production mode",
                        rule_name="document_taxon_location_production_mode_context",
                        subject_type="document",
                        subject_id=doc_id,
                        predicate="candidateHasTaxonLocationModeContext",
                        object_type="taxon_location_mode_tuple",
                        object_id=f"{label(taxon_uri, kg_index)} | {label(loc_uri, kg_index)} | {label(mode_uri, kg_index)}",
                        source_evidence=(
                            f"{doc_id} aboutTaxon {local_name(taxon_uri)}; "
                            f"{doc_id} aboutLocation {local_name(loc_uri)}; "
                            f"{doc_id} documentProductionMode {local_name(mode_uri)}"
                        ),
                        confidence_level="high",
                        example_query_ids_if_relevant=relevant_queries_for_labels(
                            [label(taxon_uri, kg_index), label(loc_uri, kg_index), label(mode_uri, kg_index)],
                            query_index,
                        ),
                        note="Direct document-level combined context.",
                    )

    # Group 3: metadata-backed safe evidence.
    for doc_uri in doc_uris:
        doc_id = doc_id_from_uri(doc_uri)
        if doc_id not in meta:
            continue
        facts = get_document_facts(graph, doc_uri)
        row = meta[doc_id]
        metadata_location = str(row.get("related_location", "") or "").strip()
        if metadata_location and facts.get("location"):
            add(
                rule_group="document-level safe facts / safe evidence",
                rule_name="metadata_location_matches_kg_location_evidence",
                subject_type="document",
                subject_id=doc_id,
                predicate="candidateHasSafeLocationEvidence",
                object_type="location",
                object_id="; ".join(label(x, kg_index) for x in facts.get("location", [])),
                source_evidence=f"metadata.related_location={metadata_location}; KG aboutLocation={'; '.join(local_name(x) for x in facts.get('location', []))}",
                confidence_level="high",
                example_query_ids_if_relevant=relevant_queries_for_labels([metadata_location] + [label(x, kg_index) for x in facts.get("location", [])], query_index),
                note="Evidence is backed by existing metadata and KG fact; candidate only.",
            )

    opportunities = build_opportunities(candidates)
    metadata = {
        "ontology_file_loaded": loaded_path,
        "ontology_source": source,
        "total_candidates": len(candidates),
        "input_files_read": [
            str(ONTOLOGY_PATH),
            str(METADATA_PATH),
            str(QUERY_PROFILES),
            str(ERROR_ANALYSIS),
            str(QUALITY_CHECK),
            str(LABEL_STRATEGY),
        ],
        "missing_or_sparse_rule_support": detect_missing_rule_support(graph, kg_index),
    }
    return candidates, opportunities, metadata


def detect_missing_rule_support(graph: Any, kg_index: dict[str, Any]) -> list[str]:
    rels = kg_index["relations"]
    notes = []
    for name in ["causedBy", "hasSymptom", "recommendedPrevention", "recommendedTreatment", "isFoundIn"]:
        count = sum(1 for _ in graph.triples((None, URIRef(rels[name]), None)))
        if count == 0:
            notes.append(f"No `{name}` relations found.")
        elif count < 5 and name != "isFoundIn":
            notes.append(f"Sparse `{name}` relations: {count} triples.")
    hierarchy_terms = ["partOf", "isLocatedIn", "locatedIn", "hasParentLocation"]
    found_hierarchy = []
    for _s, p, _o in graph.triples((None, None, None)):
        if local_name(p) in hierarchy_terms:
            found_hierarchy.append(local_name(p))
    if not found_hierarchy:
        notes.append("No explicit location hierarchy relation such as partOf/isLocatedIn was found; only direct locations and isFoundIn can be used.")
    return notes


def build_opportunities(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    errors = read_csv_rows(ERROR_ANALYSIS)
    rows: list[dict[str, Any]] = []
    oid = 1

    def has_rule(rule_name_part: str) -> bool:
        return any(rule_name_part in c["rule_name"] for c in candidates)

    for e in errors:
        qid = e.get("query_id", "")
        error_type = e.get("error_type", "")
        qgroup = e.get("query_group", "")
        if error_type == "missing_disease_fact" and has_rule("pathogen"):
            rows.append(
                {
                    "opportunity_id": f"OPP_{oid:03d}",
                    "related_query_id": qid,
                    "query_group": qgroup,
                    "missing_or_weak_signal": "Pathogen-centered disease query lacks strong pathogen bridge.",
                    "candidate_rule_evidence": "Disease causedBy pathogen and document aboutDisease inherited pathogen context.",
                    "potential_scoring_use": "Add low-weight pathogen-context evidence when query mentions pathogen and doc is about linked disease.",
                    "risk": "Can over-rank general disease documents if pathogen evidence is not explicit.",
                    "recommendation": "Use as soft scoring evidence only after manual validation.",
                }
            )
            oid += 1
        elif error_type == "missing_location_fact":
            rows.append(
                {
                    "opportunity_id": f"OPP_{oid:03d}",
                    "related_query_id": qid,
                    "query_group": qgroup,
                    "missing_or_weak_signal": "Local query depends on sparse or missing structured location facts.",
                    "candidate_rule_evidence": "Document taxon-location context and metadata-backed safe location evidence.",
                    "potential_scoring_use": "Boost documents with direct or metadata-backed location evidence for local queries.",
                    "risk": "Parent/broad location can overtake specific province/district evidence.",
                    "recommendation": "Keep exact local evidence stronger than broad country evidence.",
                }
            )
            oid += 1
        elif error_type == "weak_candidate_pool" and qgroup == "local":
            rows.append(
                {
                    "opportunity_id": f"OPP_{oid:03d}",
                    "related_query_id": qid,
                    "query_group": qgroup,
                    "missing_or_weak_signal": "Local/taxon document is weakly represented in the candidate pool.",
                    "candidate_rule_evidence": "Taxon-location context and direct document location/taxon evidence.",
                    "potential_scoring_use": "Use KG/SPARQL-side evidence as a recall backstop when vector candidates miss local documents.",
                    "risk": "Does not help if the target document is absent from the vector index used by the runtime candidate pool.",
                    "recommendation": "Treat as retrieval architecture future work; verify corpus/index coverage before scoring changes.",
                }
            )
            oid += 1
        elif error_type in {"metadata_incomplete", "weak_candidate_pool"} and has_rule("production_mode"):
            rows.append(
                {
                    "opportunity_id": f"OPP_{oid:03d}",
                    "related_query_id": qid,
                    "query_group": qgroup,
                    "missing_or_weak_signal": "Hatchery/taxon/life-stage context is incomplete or weak.",
                    "candidate_rule_evidence": "Document taxon-production-mode and taxon-location-mode contexts.",
                    "potential_scoring_use": "Add field-aware soft boost for taxon+production-mode matches.",
                    "risk": "May blur hatchery and grow-out/aquaculture contexts if mode hierarchy is too broad.",
                    "recommendation": "Tune only after adding reviewed hatchery/life-stage aliases.",
                }
            )
            oid += 1
        elif error_type == "missing_alias":
            rows.append(
                {
                    "opportunity_id": f"OPP_{oid:03d}",
                    "related_query_id": qid,
                    "query_group": qgroup,
                    "missing_or_weak_signal": "Topic alias is missing or weak.",
                    "candidate_rule_evidence": "No new asserted fact; use semantic label strategy to add reviewed aliases.",
                    "potential_scoring_use": "Improve entity detection before using KG scoring.",
                    "risk": "Adding broad aliases can produce false positives.",
                    "recommendation": "Add aliases only after manual review; do not auto-assert triples.",
                }
            )
            oid += 1
    return rows


def summarize(candidates: list[dict[str, Any]], opportunities: list[dict[str, Any]], metadata: dict[str, Any]) -> dict[str, Any]:
    by_group = Counter(c["rule_group"] for c in candidates)
    by_rule = Counter(c["rule_name"] for c in candidates)
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        **metadata,
        "candidate_count_by_rule_group": dict(by_group),
        "candidate_count_by_rule_name": dict(by_rule),
        "scoring_opportunities_count": len(opportunities),
        "all_should_assert_false": all(str(c.get("should_assert")).lower() == "false" for c in candidates),
        "examples": candidates[:10],
    }


def md_table(headers: list[str], rows: list[list[Any]]) -> list[str]:
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        out.append("| " + " | ".join(str(x) for x in row) + " |")
    return out


def write_markdown(candidates: list[dict[str, Any]], opportunities: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    lines = [
        "# Semantic Rule Candidate Facts Prototype",
        "",
        "## Purpose",
        "",
        "This prototype generates candidate semantic-rule evidence from existing ontology/KG facts and metadata.",
        "It does not assert new triples, does not modify the ontology, and does not change retrieval baselines or hybrid scoring.",
        "",
        "## Inputs Read",
        "",
    ]
    for path in summary["input_files_read"]:
        lines.append(f"- `{path}`")

    lines.extend(
        [
            "",
            "## Rule Groups Checked",
            "",
            "1. Disease-pathogen-symptom-prevention-treatment.",
            "2. Taxon-location-production mode.",
            "3. Document-level safe facts / safe evidence.",
            "",
            "## Candidate Evidence Summary",
            "",
            f"- Total candidate evidence rows: {summary['total_candidates']}",
            f"- All `should_assert` values are false: `{summary['all_should_assert_false']}`",
            "",
            "### By Rule Group",
            "",
        ]
    )
    lines.extend(md_table(["rule_group", "count"], [[k, v] for k, v in summary["candidate_count_by_rule_group"].items()]))
    lines.extend(["", "### By Rule Name", ""])
    lines.extend(md_table(["rule_name", "count"], [[k, v] for k, v in summary["candidate_count_by_rule_name"].items()]))

    preferred_examples = [
        "disease_has_pathogen_context",
        "disease_has_symptom_context",
        "disease_has_prevention_context",
        "disease_has_treatment_context",
        "document_inherits_pathogen_context_from_aboutDisease",
        "document_taxon_location_context",
        "document_taxon_production_mode_context",
        "document_taxon_location_production_mode_context",
        "metadata_location_matches_kg_location_evidence",
    ]
    example_rows = []
    for rule in preferred_examples:
        ex = next((c for c in candidates if c["rule_name"] == rule), None)
        if ex:
            example_rows.append(
                [
                    ex["candidate_id"],
                    ex["rule_group"],
                    ex["rule_name"],
                    ex["subject_id"],
                    ex["predicate"],
                    ex["object_id"],
                    ex["source_evidence"],
                ]
            )
    lines.extend(["", "## Representative Examples", ""])
    lines.extend(md_table(["id", "group", "rule", "subject", "predicate", "object", "source evidence"], example_rows))

    lines.extend(["", "## Missing or Sparse Rule Support", ""])
    for note in summary["missing_or_sparse_rule_support"]:
        lines.append(f"- {note}")

    lines.extend(["", "## Potential KG Scoring Opportunities", ""])
    lines.append(f"- Opportunity rows generated: {len(opportunities)}")
    if opportunities:
        lines.extend(
            md_table(
                ["opportunity_id", "query_id", "weak_signal", "potential_use", "recommendation"],
                [
                    [
                        o["opportunity_id"],
                        o["related_query_id"],
                        o["missing_or_weak_signal"],
                        o["potential_scoring_use"],
                        o["recommendation"],
                    ]
                    for o in opportunities[:10]
                ],
            )
        )

    lines.extend(
        [
            "",
            "## Limitations",
            "",
            "- These rows are candidate evidence, not asserted ontology facts.",
            "- `should_assert` is false for every row; manual review is required before any ontology update.",
            "- This prototype does not prove ranking improvement because no scoring experiment is run here.",
            "- It does not replace reasoner consistency checking, competency questions, or retrieval evaluation.",
            "- Some rule groups are limited by sparse KG facts, especially explicit location hierarchy and some disease-context relations.",
            "",
            "## Conclusion",
            "",
            "This prototype is useful as an academic/future-work artifact for controlled semantic-rule design. It should not be moved into runtime scoring until candidate evidence is reviewed and a separate retrieval experiment validates the effect.",
            "",
            f"Generated at: `{summary['generated_at']}`",
            "",
        ]
    )
    OUTPUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    candidates, opportunities, metadata = generate_candidates()
    summary = summarize(candidates, opportunities, metadata)
    write_csv(OUTPUT_CSV, candidates, CANDIDATE_FIELDS)
    write_csv(OPPORTUNITIES_CSV, opportunities, OPPORTUNITY_FIELDS)
    OUTPUT_JSON.write_text(
        json.dumps(
            {
                "summary": summary,
                "candidate_facts": candidates,
                "scoring_opportunities": opportunities,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    write_markdown(candidates, opportunities, summary)
    print(f"[OK] Wrote {OUTPUT_CSV}, {OUTPUT_JSON}, {OUTPUT_MD}")
    print(f"[OK] Wrote {OPPORTUNITIES_CSV}")


if __name__ == "__main__":
    main()
