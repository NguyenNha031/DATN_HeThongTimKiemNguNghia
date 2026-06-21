from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import hybrid_search
import kg_runtime
from hybrid_search import (
    METADATA_PATH,
    build_term_index,
    detect_entities,
    get_query_profile,
    load_full_metadata,
    normalize_text,
)


CORE_QUERIES = Path("data") / "eval" / "final_query_set_core.csv"
ERROR_ANALYSIS = Path("outputs") / "error_analysis_core.csv"
OUTPUT_CSV = Path("outputs") / "query_understanding_profiles.csv"
OUTPUT_JSON = Path("outputs") / "query_understanding_profiles.json"
OUTPUT_MD = Path("outputs") / "query_understanding_profiles.md"

CSV_FIELDS = [
    "query_id",
    "query_text",
    "query_group",
    "detected_profile",
    "inferred_profile",
    "detected_disease_entities",
    "detected_taxon_entities",
    "detected_location_entities",
    "detected_production_mode_entities",
    "detected_topic_or_management_entities",
    "alias_matches",
    "canonical_entities",
    "uses_disease_priority",
    "uses_species_priority",
    "uses_location_guardrail",
    "uses_production_mode_guardrail",
    "recommended_signal_priority",
    "note",
]

PROFILE_PRIORITY = {
    "disease-specific": "KG disease facts + metadata disease + vector; disease evidence should dominate.",
    "species-location": "metadata species/location + vector; KG location/taxon facts and intent guardrails are secondary.",
    "local": "location metadata/KG + lexical exact terms + vector; guardrails should protect local aquaculture intent.",
    "hatchery-production-mode": "production_mode metadata + species + vector; KG mode and hatchery intent guardrails are important.",
    "biosecurity-management": "vector semantics + topic/management/prevention aliases; KG prevention/management context is supporting evidence.",
    "generic": "vector first, metadata/KG only if entities are detected.",
}

PROFILE_RISK = {
    "disease-specific": "Missing disease aliases can let species/vector similarity outrank disease-specific evidence.",
    "species-location": "Location or species miss can cause broad shrimp/aquaculture documents to outrank country-specific documents.",
    "local": "Sparse location facts or missing local aliases can make exact local documents depend on lexical/vector luck.",
    "hatchery-production-mode": "Hatchery/life-stage misses can mix grow-out, disease, and hatchery documents.",
    "biosecurity-management": "Topic aliases are sparse; generic biosecurity documents may outrank emergency or management-specific documents.",
    "generic": "No strong entity signal means ranking relies mostly on vector similarity.",
}


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in fields})


def serialize_entities(detected: dict[str, list[dict[str, Any]]], entity_type: str) -> str:
    vals = []
    for m in detected.get(entity_type, []) or []:
        canon = str(m.get("canonical", "")).strip()
        if canon and canon not in vals:
            vals.append(canon)
    return "; ".join(vals)


def serialize_aliases(detected: dict[str, list[dict[str, Any]]]) -> str:
    vals = []
    for entity_type, matches in detected.items():
        for m in matches or []:
            alias = str(m.get("alias", "")).strip()
            canon = str(m.get("canonical", "")).strip()
            kg = "kg" if m.get("kg_uri") else "term"
            if alias or canon:
                vals.append(f"{entity_type}:{alias or canon}->{canon} [{kg}]")
    return "; ".join(vals)


def canonical_map(detected: dict[str, list[dict[str, Any]]]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for entity_type, matches in detected.items():
        seen = []
        for m in matches or []:
            canon = str(m.get("canonical", "")).strip()
            if canon and canon not in seen:
                seen.append(canon)
        if seen:
            out[entity_type] = seen
    return out


def query_level_guardrails(query: str, detected: dict[str, Any]) -> dict[str, bool]:
    qn = normalize_text(query)
    location_guardrail = False
    production_guardrail = False
    try:
        location_guardrail = bool(
            hybrid_search._narrow_local_aquaculture_intent(query, detected)
            or hybrid_search._lobster_coastal_vietnam_boost_intent(query, detected)
            or hybrid_search._thailand_low_water_exchange_intent(qn)
        )
    except Exception:
        location_guardrail = bool(detected.get("location"))
    try:
        production_guardrail = bool(
            hybrid_search._hatchery_vannamei_production_mode_intent(qn, detected)
            or hybrid_search._biosecurity_hatchery_vannamei_stack_intent(detected, qn)
        )
    except Exception:
        production_guardrail = bool(detected.get("mode"))
    return {
        "uses_location_guardrail": location_guardrail,
        "uses_production_mode_guardrail": production_guardrail,
    }


def runtime_detect(query: str, term_index: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any]]:
    detected = detect_entities(query, term_index)
    kg_entities = {"disease": [], "species": [], "location": [], "mode": [], "prevention": []}
    try:
        hybrid_search._init_kg_if_needed()
        if hybrid_search._kg_enabled():
            linked = kg_runtime.link_query_entities_kg(query, hybrid_search._KG_INDEX)
            kg_entities = {
                "disease": linked.get("disease") or [],
                "species": linked.get("species") or [],
                "location": linked.get("location") or [],
                "mode": linked.get("mode") or [],
                "prevention": linked.get("prevention") or [],
            }
            detected = hybrid_search._merge_detected_with_kg(detected, kg_entities)
    except Exception:
        pass
    return detected, kg_entities


def infer_profile(query_group: str, runtime_profile: str, detected: dict[str, Any]) -> str:
    if query_group:
        return query_group
    if runtime_profile == "disease_priority":
        return "disease-specific"
    if detected.get("mode"):
        return "hatchery-production-mode"
    if detected.get("location") and detected.get("species"):
        return "species-location"
    if detected.get("location"):
        return "local"
    if detected.get("topic") or detected.get("management") or detected.get("prevention"):
        return "biosecurity-management"
    return "generic"


def recommended_signal_priority(inferred_profile: str, detected: dict[str, Any]) -> str:
    base = PROFILE_PRIORITY.get(inferred_profile, PROFILE_PRIORITY["generic"])
    extras = []
    if detected.get("disease"):
        extras.append("disease_priority")
    if detected.get("species"):
        extras.append("species_priority")
    if detected.get("location"):
        extras.append("location-sensitive")
    if detected.get("mode"):
        extras.append("mode-sensitive")
    if detected.get("topic") or detected.get("management") or detected.get("prevention"):
        extras.append("topic/management context")
    return base + (" Runtime flags: " + ", ".join(extras) + "." if extras else "")


def build_note(query_id: str, inferred_profile: str, runtime_profile: str, detected: dict[str, Any], error_notes: dict[str, str]) -> str:
    parts = []
    if inferred_profile == "disease-specific" and not detected.get("disease"):
        parts.append("Expected disease-specific intent but runtime disease entity is missing.")
    if inferred_profile in {"local", "species-location"} and not detected.get("location"):
        parts.append("Location-sensitive query with no runtime location entity.")
    if inferred_profile == "hatchery-production-mode" and not detected.get("mode"):
        parts.append("Production-mode query with no runtime mode entity.")
    if runtime_profile == "generic" and inferred_profile != "biosecurity-management":
        parts.append("Runtime scoring profile is generic despite a more specific query-group label.")
    if query_id in error_notes:
        parts.append(f"Linked error-analysis note: {error_notes[query_id]}")
    return " ".join(parts) if parts else "OK"


def load_error_notes() -> dict[str, str]:
    if not ERROR_ANALYSIS.exists():
        return {}
    out = {}
    for r in read_csv_rows(ERROR_ANALYSIS):
        qid = str(r.get("query_id", "")).strip()
        if qid:
            out[qid] = str(r.get("error_type", "")).strip()
    return out


def analyze() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    metadata_df = load_full_metadata(METADATA_PATH)
    term_index = build_term_index(metadata_df)
    query_rows = read_csv_rows(CORE_QUERIES)
    error_notes = load_error_notes()

    rows: list[dict[str, Any]] = []
    for q in query_rows:
        qid = str(q["query_id"]).strip()
        query_text = str(q["query_text"]).strip()
        query_group = str(q.get("query_group", "")).strip()
        detected, kg_entities = runtime_detect(query_text, term_index)
        runtime_profile = get_query_profile(detected)
        inferred = infer_profile(query_group, runtime_profile, detected)
        guardrails = query_level_guardrails(query_text, detected)
        topic_entities = []
        for et in ["topic", "management", "prevention"]:
            val = serialize_entities(detected, et)
            if val:
                topic_entities.append(f"{et}: {val}")

        row = {
            "query_id": qid,
            "query_text": query_text,
            "query_group": query_group,
            "detected_profile": runtime_profile,
            "inferred_profile": inferred,
            "detected_disease_entities": serialize_entities(detected, "disease"),
            "detected_taxon_entities": serialize_entities(detected, "species"),
            "detected_location_entities": serialize_entities(detected, "location"),
            "detected_production_mode_entities": serialize_entities(detected, "mode"),
            "detected_topic_or_management_entities": "; ".join(topic_entities),
            "alias_matches": serialize_aliases(detected),
            "canonical_entities": json.dumps(canonical_map(detected), ensure_ascii=False),
            "uses_disease_priority": runtime_profile == "disease_priority",
            "uses_species_priority": runtime_profile == "species_priority",
            "uses_location_guardrail": guardrails["uses_location_guardrail"],
            "uses_production_mode_guardrail": guardrails["uses_production_mode_guardrail"],
            "recommended_signal_priority": recommended_signal_priority(inferred, detected),
            "note": build_note(qid, inferred, runtime_profile, detected, error_notes),
            "_kg_entities": kg_entities,
        }
        rows.append(row)

    summary = build_summary(rows)
    return rows, summary


def build_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    profile_counts = Counter(r["inferred_profile"] for r in rows)
    runtime_profile_counts = Counter(r["detected_profile"] for r in rows)
    entity_counts = {
        "disease": sum(1 for r in rows if r["detected_disease_entities"]),
        "taxon_species": sum(1 for r in rows if r["detected_taxon_entities"]),
        "location": sum(1 for r in rows if r["detected_location_entities"]),
        "production_mode": sum(1 for r in rows if r["detected_production_mode_entities"]),
        "topic_management_prevention": sum(1 for r in rows if r["detected_topic_or_management_entities"]),
    }
    multi_context = []
    for r in rows:
        dims = []
        if r["detected_disease_entities"]:
            dims.append("disease")
        if r["detected_taxon_entities"]:
            dims.append("taxon")
        if r["detected_location_entities"]:
            dims.append("location")
        if r["detected_production_mode_entities"]:
            dims.append("production_mode")
        if r["detected_topic_or_management_entities"]:
            dims.append("topic/management")
        if len(dims) >= 2:
            multi_context.append({"query_id": r["query_id"], "query_group": r["query_group"], "dimensions": dims})

    profile_table = []
    for profile, count in sorted(profile_counts.items()):
        ex = next((r["query_id"] for r in rows if r["inferred_profile"] == profile), "")
        profile_table.append(
            {
                "profile": profile,
                "n_queries": count,
                "main_signal_priority": PROFILE_PRIORITY.get(profile, PROFILE_PRIORITY["generic"]),
                "risk_if_misclassified": PROFILE_RISK.get(profile, PROFILE_RISK["generic"]),
                "example_query_id": ex,
            }
        )

    ambiguous = [
        {
            "query_id": r["query_id"],
            "query_group": r["query_group"],
            "detected_profile": r["detected_profile"],
            "note": r["note"],
        }
        for r in rows
        if r["note"] != "OK"
    ]

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "num_queries": len(rows),
        "profile_counts": dict(profile_counts),
        "runtime_profile_counts": dict(runtime_profile_counts),
        "entity_detection_counts": entity_counts,
        "multi_context_queries": multi_context,
        "profile_summary_table": profile_table,
        "ambiguous_or_uncertain_queries": ambiguous,
        "runtime_functions_reused": [
            "hybrid_search.load_full_metadata",
            "hybrid_search.build_term_index",
            "hybrid_search.detect_entities",
            "kg_runtime.link_query_entities_kg",
            "hybrid_search._merge_detected_with_kg",
            "hybrid_search.get_query_profile",
            "hybrid_search._narrow_local_aquaculture_intent",
            "hybrid_search._lobster_coastal_vietnam_boost_intent",
            "hybrid_search._hatchery_vannamei_production_mode_intent",
            "hybrid_search._biosecurity_hatchery_vannamei_stack_intent",
            "hybrid_search._thailand_low_water_exchange_intent",
        ],
        "input_files_read": [
            str(CORE_QUERIES),
            METADATA_PATH,
            "data/ontology/taxon_enriched_facts_v2.owl via kg_runtime loader",
            str(ERROR_ANALYSIS) if ERROR_ANALYSIS.exists() else "",
        ],
    }


def md_table(headers: list[str], rows: list[list[Any]]) -> list[str]:
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        out.append("| " + " | ".join(str(x) for x in row) + " |")
    return out


def write_markdown(rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    lines = [
        "# Query Understanding Profiles",
        "",
        "## Purpose",
        "",
        "This report explains how the system understands the 28 core queries before scoring and reranking.",
        "It is a read-only technical analysis. It does not modify the ontology, metadata, query set, relevance judgments, baseline outputs, metrics, `hybrid_search.py`, or `kg_runtime.py`.",
        "",
        "## Input Files and Runtime Functions",
        "",
    ]
    for p in summary["input_files_read"]:
        if p:
            lines.append(f"- `{p}`")
    lines.extend(["", "Runtime functions reused:"])
    for fn in summary["runtime_functions_reused"]:
        lines.append(f"- `{fn}`")

    lines.extend(
        [
            "",
            "## How Profiles Are Determined",
            "",
            "- `detected_profile` comes from the runtime `hybrid_search.get_query_profile()` after dictionary detection and KG entity merge.",
            "- `inferred_profile` uses the query-set `query_group` when available, because the benchmark groups are thesis-facing categories.",
            "- Entity detection uses metadata-derived terms, manual aliases, KG labels/aliases, and overlap suppression from the runtime.",
            "- Signal priority is explanatory: it maps the detected/query-set profile to the scoring layers that should matter most.",
            "",
            "## Query Count by Profile",
            "",
        ]
    )
    profile_rows = []
    for item in summary["profile_summary_table"]:
        profile_rows.append(
            [
                item["profile"],
                item["n_queries"],
                item["main_signal_priority"],
                item["risk_if_misclassified"],
                item["example_query_id"],
            ]
        )
    lines.extend(md_table(["profile", "n_queries", "main_signal_priority", "risk_if_misclassified", "example_query_id"], profile_rows))

    lines.extend(["", "## Runtime Profile Counts", ""])
    lines.extend(md_table(["runtime_profile", "n_queries"], [[k, v] for k, v in sorted(summary["runtime_profile_counts"].items())]))

    lines.extend(["", "## Entity Detection Summary", ""])
    lines.extend(md_table(["entity type", "queries with entity"], [[k, v] for k, v in summary["entity_detection_counts"].items()]))

    lines.extend(["", "## Multi-context Queries", ""])
    multi_rows = [[x["query_id"], x["query_group"], ", ".join(x["dimensions"])] for x in summary["multi_context_queries"]]
    lines.extend(md_table(["query_id", "query_group", "detected dimensions"], multi_rows))

    lines.extend(["", "## Illustrative Cases", ""])
    example_profiles = ["disease-specific", "species-location", "hatchery-production-mode", "biosecurity-management", "local"]
    for profile in example_profiles:
        case = next((r for r in rows if r["inferred_profile"] == profile), None)
        if not case:
            continue
        lines.extend(
            [
                f"### {profile}: `{case['query_id']}`",
                "",
                f"- Query: {case['query_text']}",
                f"- Runtime profile: `{case['detected_profile']}`",
                f"- Disease: {case['detected_disease_entities'] or '-'}",
                f"- Taxon/species: {case['detected_taxon_entities'] or '-'}",
                f"- Location: {case['detected_location_entities'] or '-'}",
                f"- Production mode: {case['detected_production_mode_entities'] or '-'}",
                f"- Topic/management/prevention: {case['detected_topic_or_management_entities'] or '-'}",
                f"- Signal priority: {case['recommended_signal_priority']}",
                f"- Why this profile is reasonable: query-set group is `{case['query_group']}`, and runtime entities provide the scoring context shown above.",
                "",
            ]
        )

    lines.extend(["## Ambiguous or Uncertain Queries", ""])
    if summary["ambiguous_or_uncertain_queries"]:
        amb_rows = [
            [x["query_id"], x["query_group"], x["detected_profile"], x["note"]]
            for x in summary["ambiguous_or_uncertain_queries"]
        ]
        lines.extend(md_table(["query_id", "query_group", "runtime_profile", "note"], amb_rows))
    else:
        lines.append("- None flagged by this analyzer.")

    lines.extend(
        [
            "",
            "## Limitations",
            "",
            "- Query understanding depends on aliases, metadata values, and KG labels available in the current snapshot.",
            "- Missing aliases can cause entity linking to miss disease, location, production mode, or management concepts.",
            "- `detected_profile` is a runtime scoring profile, not a ground-truth semantic label.",
            "- `inferred_profile` follows the query-set group when available, so it is useful for thesis explanation but not a learned classifier.",
            "- Topic/management/prevention coverage is intentionally limited and should not be overclaimed as full intent understanding.",
            "",
            f"Generated at: `{summary['generated_at']}`",
            "",
        ]
    )
    OUTPUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    rows, summary = analyze()
    public_rows = [{k: v for k, v in r.items() if not k.startswith("_")} for r in rows]
    write_csv(OUTPUT_CSV, public_rows, CSV_FIELDS)
    OUTPUT_JSON.write_text(
        json.dumps(
            {
                "summary": summary,
                "queries": public_rows,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    write_markdown(public_rows, summary)
    print(f"[OK] Wrote {OUTPUT_CSV}, {OUTPUT_JSON}, {OUTPUT_MD}")


if __name__ == "__main__":
    main()
