from __future__ import annotations

import csv
import json
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

import kg_runtime
from rdflib import URIRef
from rdflib.namespace import RDFS, SKOS


CQ_PATH = Path("data") / "eval" / "competency_questions_core.csv"
RESULTS_PATH = Path("outputs") / "competency_questions_results.csv"
SUMMARY_PATH = Path("outputs") / "competency_questions_summary.json"

CSV_FIELDS = [
    "cq_id",
    "question",
    "cq_group",
    "sparql_intent",
    "expected_answer",
    "actual_result",
    "matched_expected",
    "status",
    "required_relations",
    "note",
]


def _utf8() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stdin.reconfigure(encoding="utf-8")
    except Exception:
        pass


def _local_name(uri: Any) -> str:
    s = str(uri)
    if "#" in s:
        return s.rsplit("#", 1)[-1]
    if "/" in s:
        return s.rsplit("/", 1)[-1]
    return s


def _norm(text: Any) -> str:
    return kg_runtime.normalize_kg_text(text).replace(" ", "").replace("-", "").replace("_", "")


def _entity_uri(alias: str, expected_type: str, kg_index: dict[str, Any]) -> str | None:
    ents = kg_index.get("label_to_entities", {}).get(kg_runtime.normalize_kg_text(alias), [])
    for ent in ents:
        if ent.get("entity_type") == expected_type and ent.get("uri"):
            return str(ent["uri"])
    # Fallback: allow explicit local URI fragment in competency CSV.
    ns = str(kg_index["ns"])
    candidate = ns + alias
    if candidate in (kg_index.get("uri_to_info") or {}):
        return candidate
    return None


def _doc_uri(doc_id: str, kg_index: dict[str, Any]) -> str | None:
    key = kg_runtime.normalize_kg_text(doc_id)
    return (kg_index.get("dockey_to_uri") or {}).get(key)


def _display(uri: Any, label: Any = None) -> str:
    local = _local_name(uri)
    lab = str(label).strip() if label is not None else ""
    return f"{local}|{lab}" if lab and lab != local else local


def _query_labels(graph, ns, uri_var: str = "x") -> str:
    return f"""
    OPTIONAL {{ ?{uri_var} <{RDFS.label}> ?rdfsLabel . }}
    OPTIONAL {{ ?{uri_var} <{SKOS.prefLabel}> ?prefLabel . }}
    OPTIONAL {{ ?{uri_var} <{ns.title}> ?title . }}
    BIND(COALESCE(?title, ?prefLabel, ?rdfsLabel, STRAFTER(STR(?{uri_var}), "#")) AS ?label)
    """


def _run_entity_query(graph, ns, select_var: str, where_body: str) -> list[str]:
    q = f"""
    SELECT DISTINCT ?{select_var} ?label
    WHERE {{
      {where_body}
      {_query_labels(graph, ns, select_var)}
    }}
    ORDER BY ?{select_var}
    """
    out: list[str] = []
    for row in graph.query(q):
        out.append(_display(row[0], row[1]))
    return out


def _docs_about_disease(graph, ns, disease_uri: str) -> list[str]:
    return _run_entity_query(graph, ns, "doc", f"?doc <{ns.aboutDisease}> <{disease_uri}> .")


def _docs_about_taxon(graph, ns, taxon_uri: str) -> list[str]:
    return _run_entity_query(graph, ns, "doc", f"?doc <{ns.aboutTaxon}> <{taxon_uri}> .")


def _docs_by_mode(graph, ns, mode_uri: str) -> list[str]:
    return _run_entity_query(graph, ns, "doc", f"?doc <{ns.documentProductionMode}> <{mode_uri}> .")


def _diseases_for_taxon(graph, ns, taxon_uri: str) -> list[str]:
    body = f"""
    {{
      <{taxon_uri}> <{ns.hasDisease}> ?x .
    }}
    UNION
    {{
      ?x <{ns.affectsTaxon}> <{taxon_uri}> .
    }}
    """
    return _run_entity_query(graph, ns, "x", body)


def _taxa_affected_by_disease(graph, ns, disease_uri: str) -> list[str]:
    return _run_entity_query(graph, ns, "x", f"<{disease_uri}> <{ns.affectsTaxon}> ?x .")


def _pathogens_for_disease(graph, ns, disease_uri: str) -> list[str]:
    return _run_entity_query(graph, ns, "x", f"<{disease_uri}> <{ns.causedBy}> ?x .")


def _symptoms_for_disease(graph, ns, disease_uri: str) -> list[str]:
    return _run_entity_query(graph, ns, "x", f"<{disease_uri}> <{ns.hasSymptom}> ?x .")


def _docs_mention_entity(graph, ns, entity_uri: str) -> list[str]:
    return _run_entity_query(graph, ns, "doc", f"?doc <{ns.mentions}> <{entity_uri}> .")


def _docs_about_disease_and_taxon(graph, ns, disease_uri: str, taxon_uri: str) -> list[str]:
    body = f"""
    ?doc <{ns.aboutDisease}> <{disease_uri}> .
    ?doc <{ns.aboutTaxon}> <{taxon_uri}> .
    """
    return _run_entity_query(graph, ns, "doc", body)


def _explain_doc_match(graph, ns, doc_uri: str, disease_uri: str, taxon_uri: str) -> list[str]:
    q = f"""
    SELECT DISTINCT ?p ?o ?label
    WHERE {{
      VALUES ?p {{
        <{ns.aboutDisease}>
        <{ns.aboutTaxon}>
        <{ns.documentProductionMode}>
        <{ns.mentions}>
      }}
      <{doc_uri}> ?p ?o .
      OPTIONAL {{ ?o <{RDFS.label}> ?rdfsLabel . }}
      OPTIONAL {{ ?o <{SKOS.prefLabel}> ?prefLabel . }}
      BIND(COALESCE(?prefLabel, ?rdfsLabel, STRAFTER(STR(?o), "#")) AS ?label)
    }}
    ORDER BY ?p ?o
    """
    evidence = []
    for p, o, label in graph.query(q):
        evidence.append(f"{_local_name(p)}={_display(o, label)}")
    required = {
        f"aboutDisease={_local_name(disease_uri)}",
        f"aboutTaxon={_local_name(taxon_uri)}",
    }
    compact = []
    for item in evidence:
        rel, val = item.split("=", 1)
        local = val.split("|", 1)[0]
        compact.append(f"{rel}={local}")
    return sorted(set(compact)) or evidence


def run_intent(intent: str, graph, kg_index: dict[str, Any]) -> list[str]:
    ns = kg_index["ns"]
    name, _, args = intent.partition(":")
    parts = args.split("|") if args else []

    if name == "docs_about_disease":
        u = _entity_uri(parts[0], "disease", kg_index)
        return _docs_about_disease(graph, ns, u) if u else []
    if name == "docs_about_taxon":
        u = _entity_uri(parts[0], "species", kg_index)
        return _docs_about_taxon(graph, ns, u) if u else []
    if name == "docs_by_mode":
        u = _entity_uri(parts[0], "mode", kg_index)
        return _docs_by_mode(graph, ns, u) if u else []
    if name == "diseases_for_taxon":
        u = _entity_uri(parts[0], "species", kg_index)
        return _diseases_for_taxon(graph, ns, u) if u else []
    if name == "taxa_affected_by_disease":
        u = _entity_uri(parts[0], "disease", kg_index)
        return _taxa_affected_by_disease(graph, ns, u) if u else []
    if name == "pathogens_for_disease":
        u = _entity_uri(parts[0], "disease", kg_index)
        return _pathogens_for_disease(graph, ns, u) if u else []
    if name == "symptoms_for_disease":
        u = _entity_uri(parts[0], "disease", kg_index)
        return _symptoms_for_disease(graph, ns, u) if u else []
    if name == "docs_mention_entity":
        u = _entity_uri(parts[0], "disease", kg_index)
        return _docs_mention_entity(graph, ns, u) if u else []
    if name == "docs_about_disease_and_taxon":
        disease = _entity_uri(parts[0], "disease", kg_index)
        taxon = _entity_uri(parts[1], "species", kg_index)
        return _docs_about_disease_and_taxon(graph, ns, disease, taxon) if disease and taxon else []
    if name == "explain_doc_match":
        doc = _doc_uri(parts[0], kg_index)
        disease = _entity_uri(parts[1], "disease", kg_index)
        taxon = _entity_uri(parts[2], "species", kg_index)
        return _explain_doc_match(graph, ns, doc, disease, taxon) if doc and disease and taxon else []

    raise ValueError(f"Unsupported sparql_intent: {intent}")


def compare_expected(expected_answer: str, actual: list[str]) -> tuple[str, list[str]]:
    expected = [x.strip() for x in str(expected_answer or "").split(";") if x.strip()]
    actual_blob = " ; ".join(actual)
    matched = []
    for exp in expected:
        exp_norm = _norm(exp)
        if not exp_norm:
            continue
        if any(exp_norm in _norm(a) for a in actual):
            matched.append(exp)
    if expected and len(matched) == len(expected):
        return "correct", matched
    if matched or (actual and expected):
        return "partial", matched
    return "incorrect", matched


def main() -> None:
    _utf8()
    graph, loaded_path, used_source = kg_runtime.load_kg_prefer_facts_then_alias_enriched()
    kg_index = kg_runtime.build_kg_index(graph)

    rows: list[dict[str, str]] = []
    by_group: dict[str, dict[str, int]] = defaultdict(lambda: {"total": 0, "correct": 0, "partial": 0, "incorrect": 0})

    with open(CQ_PATH, encoding="utf-8-sig", newline="") as f:
        for cq in csv.DictReader(f):
            actual = run_intent(cq["sparql_intent"], graph, kg_index)
            status, matched = compare_expected(cq["expected_answer"], actual)
            group = cq["cq_group"]
            by_group[group]["total"] += 1
            by_group[group][status] += 1
            rows.append(
                {
                    "cq_id": cq["cq_id"],
                    "question": cq["question"],
                    "cq_group": group,
                    "sparql_intent": cq["sparql_intent"],
                    "expected_answer": cq["expected_answer"],
                    "actual_result": "; ".join(actual),
                    "matched_expected": "; ".join(matched),
                    "status": status,
                    "required_relations": cq["required_relations"],
                    "note": cq.get("note", ""),
                }
            )

    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_PATH, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        w.writeheader()
        w.writerows(rows)

    total = len(rows)
    correct = sum(1 for r in rows if r["status"] == "correct")
    partial = sum(1 for r in rows if r["status"] == "partial")
    incorrect = sum(1 for r in rows if r["status"] == "incorrect")
    summary = {
        "ontology_file_loaded": loaded_path,
        "ontology_source": used_source,
        "total_cq": total,
        "correct": correct,
        "partial": partial,
        "incorrect": incorrect,
        "accuracy_like_ratio": round(correct / total, 6) if total else 0.0,
        "by_group": dict(by_group),
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "notes": [
            "Standalone competency-question evaluation for structured KG/SPARQL layer.",
            "Does not modify ontology, metadata, retrieval baselines, relevance judgments, or core query set.",
            "Expected answers are matched by normalized local-name/label substring against SPARQL results.",
        ],
    }
    SUMMARY_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] Wrote {RESULTS_PATH} and {SUMMARY_PATH}")


if __name__ == "__main__":
    main()
