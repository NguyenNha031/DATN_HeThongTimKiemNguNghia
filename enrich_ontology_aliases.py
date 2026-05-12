from __future__ import annotations

import json
import re
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from rdflib import Literal, RDF
from rdflib.namespace import OWL, RDFS, SKOS

import kg_runtime


INPUT_OWL_PATH = Path("data") / "ontology" / "taxon_enriched.owl"
GAP_REPORT_JSON_PATH = Path("outputs") / "ontology_alias_gap_report.json"
OUTPUT_OWL_PATH = Path("data") / "ontology" / "taxon_enriched_aliases.owl"

BACKUP_DIR = Path("data") / "ontology"

ADDED_ALIASES_JSON_PATH = Path("outputs") / "ontology_alias_added.json"


def _reconfigure_stdout_utf8() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stdin.reconfigure(encoding="utf-8")
    except Exception:
        pass


def _contains_vietnamese_diacritics(s: str) -> bool:
    return bool(re.search(r"[à-ỹÀ-Ỹ]", s))


def _detect_lang_for_literal(raw_value: str) -> str:
    return "vi" if _contains_vietnamese_diacritics(raw_value) else "en"


def _iter_label_literals(graph, entity_uri) -> list[tuple[str, str | None]]:
    vals: list[tuple[str, str | None]] = []
    for p in (RDFS.label, SKOS.prefLabel, SKOS.altLabel):
        for o in graph.objects(entity_uri, p):
            try:
                if isinstance(o, Literal):
                    vals.append((str(o), getattr(o, "language", None)))
            except Exception:
                continue
    return vals


def _normalized(s: str) -> str:
    return kg_runtime.normalize_kg_text(s)


def _already_has_alias(graph, entity_uri, alias_value: str) -> bool:
    alias_norm = _normalized(alias_value)
    for (lit_str, _lang) in _iter_label_literals(graph, entity_uri):
        if _normalized(lit_str) == alias_norm:
            return True
    return False


def _entity_exists(graph, entity_uri: str) -> bool:
    from rdflib import URIRef

    u = URIRef(entity_uri)
    # Existence heuristic: subject has any triple OR has rdf:type.
    if any(True for _ in graph.triples((u, None, None))):
        return True
    return False


def _load_gap_report() -> list[dict[str, Any]]:
    if not GAP_REPORT_JSON_PATH.exists():
        raise FileNotFoundError(f"Gap report missing: {GAP_REPORT_JSON_PATH}")
    obj = json.loads(GAP_REPORT_JSON_PATH.read_text(encoding="utf-8"))
    items = obj.get("top_gap_items") or []
    if not isinstance(items, list):
        raise ValueError("Invalid gap report format: top_gap_items must be a list")
    return items


def enrich_aliases() -> None:
    _reconfigure_stdout_utf8()

    print("[ENRICH] Loading base ontology...")
    graph = kg_runtime.load_kg(INPUT_OWL_PATH)

    print("[ENRICH] Loading alias gap report...")
    items = _load_gap_report()

    # Conservative safety filters:
    # - Only add when confidence is explicitly "high"
    # - Only add when suggested_target_entity_uri is present
    # - Never add very generic "shrimp"
    # Avoid adding very generic tokens that would create noisy entity linking.
    forbidden_values = {
        "shrimp",
        "tom",
        "tôm",
        "fish",
        "aquaculture species",
    }
    added: list[dict[str, Any]] = []

    # Sort: high confidence first, then by evidence_source (mapping_report before verification)
    def sort_key(it: dict[str, Any]) -> tuple[int, int]:
        conf = str(it.get("confidence", "low")).lower()
        evidence = str(it.get("evidence_source", "")).lower()
        conf_rank = 3 if conf == "high" else 0
        ev_rank = 1 if "mapping_report" in evidence or evidence.startswith("mapping") else 0
        return (conf_rank, ev_rank)

    items_sorted = sorted(items, key=sort_key, reverse=True)

    from rdflib import URIRef

    for it in items_sorted:
        raw_value = str(it.get("raw_value", "") or "").strip()
        if not raw_value:
            continue
        if raw_value.lower() in forbidden_values:
            continue

        confidence = str(it.get("confidence", "low")).lower()
        if confidence != "high":
            continue

        entity_uri = it.get("suggested_target_entity_uri")
        if not entity_uri:
            continue

        entity_uri = str(entity_uri)
        if not _entity_exists(graph, entity_uri):
            continue

        if _already_has_alias(graph, URIRef(entity_uri), raw_value):
            continue

        lang = _detect_lang_for_literal(raw_value)
        graph.add((URIRef(entity_uri), SKOS.altLabel, Literal(raw_value, lang=lang)))

        added.append(
            {
                "raw_value": raw_value,
                "normalized_value": kg_runtime.normalize_kg_text(raw_value),
                "confidence": confidence,
                "field_type": it.get("field_type"),
                "suggested_target_entity_uri": entity_uri,
                "evidence_source": it.get("evidence_source"),
            }
        )

    # Backup current output if exists
    if OUTPUT_OWL_PATH.exists():
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = BACKUP_DIR / f"{OUTPUT_OWL_PATH.name}.bak_{ts}"
        shutil.copy2(str(OUTPUT_OWL_PATH), str(backup_path))
        print(f"[ENRICH] Backup created: {backup_path}")

    graph.serialize(destination=str(OUTPUT_OWL_PATH), format="xml")
    print(f"[ENRICH] Saved enriched alias ontology: {OUTPUT_OWL_PATH}")

    ADDED_ALIASES_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    ADDED_ALIASES_JSON_PATH.write_text(
        json.dumps(
            {
                "added_count": len(added),
                "added": added,
                "base_owl": str(INPUT_OWL_PATH),
                "gap_report_json": str(GAP_REPORT_JSON_PATH),
                "output_owl": str(OUTPUT_OWL_PATH),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"[ENRICH] Added aliases: {len(added)}")
    print(f"[ENRICH] Added-alias JSON: {ADDED_ALIASES_JSON_PATH}")


if __name__ == "__main__":
    enrich_aliases()

