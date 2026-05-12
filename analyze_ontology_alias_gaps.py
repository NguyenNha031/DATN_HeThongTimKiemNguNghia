from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

import kg_runtime


INPUT_OWL_PATH = Path("data") / "ontology" / "taxon_enriched.owl"
MAPPING_REPORT_PATH = Path("data") / "ontology" / "mapping_report.csv"
VERIFICATION_JSON_PATH = Path("outputs") / "kg_runtime_verification.json"
METADATA_XLSX_PATH = Path("data") / "metadata" / "document_metadata.xlsx"

OUTPUT_JSON_PATH = Path("outputs") / "ontology_alias_gap_report.json"
OUTPUT_CSV_PATH = Path("outputs") / "ontology_alias_gap_report.csv"


TEST_QUERY_TERMS = [
    # species synonyms
    ("species", "tôm hùm", "lobster"),
    ("species", "lobster", "tôm hùm"),
    # location synonyms
    ("location", "Khánh Hòa", "Khanh Hoa"),
    ("location", "Khanh Hoa", "Khánh Hòa"),
    # mode synonyms
    ("mode", "trại giống", "hatchery"),
    ("mode", "hatchery", "trại giống"),
]


def _reconfigure_stdout_utf8() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stdin.reconfigure(encoding="utf-8")
    except Exception:
        pass


def _safe_json_dump(obj: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def _normalize_for_grouping(text: Any) -> str:
    return kg_runtime.normalize_kg_text(text)


@dataclass
class GapItem:
    field_type: str
    raw_value: str
    normalized_value: str
    occurrence_count: int
    currently_mapped: bool
    suggested_target_entity_uri: str | None
    suggested_target_label: str | None
    confidence: str
    evidence_source: str


def _build_ontology_alias_lookup(kg_index: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    # alias_norm -> list of entity dicts
    return kg_index.get("label_to_entities") or {}


def _infer_target_from_near_match(
    field_type: str,
    term_norm: str,
    kg_index: dict[str, Any],
) -> tuple[str | None, str | None, str]:
    """
    Infer a likely target entity URI for a missing alias using conservative near-match:
    - prefer exact alias_norm match in label_to_entities (even though caller uses unmapped typically)
    - otherwise prefer substring overlap between term_norm and any known alias_norm for entities of field_type
    """
    label_to_entities = kg_index.get("label_to_entities") or {}
    uri_to_info = kg_index.get("uri_to_info") or {}

    # exact alias match
    if term_norm in label_to_entities:
        candidates = [e for e in label_to_entities[term_norm] if e.get("entity_type") == field_type]
        if candidates:
            e0 = candidates[0]
            label = (e0.get("label") or uri_to_info.get(e0.get("uri"), {}).get("label")) or None
            return e0.get("uri"), label, "medium"

    # substring match: pick best scoring based on character containment ratio
    best_uri: str | None = None
    best_label: str | None = None
    best_score = 0.0

    aliases = list(label_to_entities.keys())
    for a in aliases:
        if not a:
            continue
        if a == term_norm:
            continue
        if field_type not in {"disease", "species", "location", "mode"}:
            continue
        if not (a in term_norm or term_norm in a):
            continue
        ents = [e for e in label_to_entities.get(a, []) if e.get("entity_type") == field_type]
        if not ents:
            continue
        # score by relative length containment
        denom = max(len(term_norm), 1)
        ratio = min(len(a), len(term_norm)) / denom
        if ratio > best_score:
            best_score = ratio
            e0 = ents[0]
            best_uri = e0.get("uri")
            best_label = e0.get("label")

    if best_uri:
        # Substring-based inference:
        # - very strong containment => high confidence
        # - moderate => medium
        # - weak => low
        if best_score >= 0.85:
            return best_uri, best_label, "high"
        if best_score >= 0.5:
            return best_uri, best_label, "medium"
        return best_uri, best_label, "low"

    return None, None, "low"


def analyze() -> None:
    _reconfigure_stdout_utf8()

    # Load ontology + index
    print("[ALIAS-GAP] Loading ontology for analysis...")
    graph = kg_runtime.load_kg(INPUT_OWL_PATH)
    kg_index = kg_runtime.build_kg_index(graph)

    # Load metadata (for completeness + counts)
    print("[ALIAS-GAP] Loading metadata Excel...")
    df_meta = pd.read_excel(METADATA_XLSX_PATH)

    # Load metadata mapping report
    print("[ALIAS-GAP] Loading mapping_report.csv...")
    df = pd.read_csv(MAPPING_REPORT_PATH)

    field_type_map = {
        "aboutDisease": "disease",
        "aboutTaxon": "species",
        "aboutLocation": "location",
        "documentProductionMode": "mode",
    }

    target_fields = set(field_type_map.values())

    # Determine unmapped/weak terms from mapping_report
    df["status"] = df["status"].astype(str)
    df["raw_value"] = df["raw_value"].astype(str)
    df["normalized_value"] = df["raw_value"].map(_normalize_for_grouping)

    filtered = df[df["field_name"].isin(field_type_map.keys())].copy()
    filtered["field_type"] = filtered["field_name"].map(field_type_map)

    # currently_mapped: mapped => true; mapped_manual/unmapped => false
    def currently_mapped(status: str) -> bool:
        s = status.lower()
        return "mapped" in s and ("manual" not in s)

    filtered["currently_mapped"] = filtered["status"].map(currently_mapped)

    # Group occurrence counts among unmapped/weak (mapped_manual or unmapped)
    weak_mask = filtered["status"].str.contains("unmapped", case=False, na=False) | filtered["status"].str.contains(
        "mapped_manual", case=False, na=False
    )
    weak = filtered[weak_mask].copy()

    # Count occurrences and keep one mapped_uri_or_reason sample
    agg = (
        weak.groupby(["field_type", "raw_value", "normalized_value"], dropna=False)
        .agg(
            occurrence_count=("status", "size"),
            status_sample=("status", "first"),
            mapped_uri_or_reason=("mapped_uri_or_reason", "first"),
        )
        .reset_index()
    )
    group_counts = agg.rename(columns={"occurrence_count": "occurrence_count"})

    # Load verification JSON to add query-failure evidence
    verification_obj: dict[str, Any] = {}
    if VERIFICATION_JSON_PATH.exists():
        verification_obj = json.loads(VERIFICATION_JSON_PATH.read_text(encoding="utf-8"))

    per_query = verification_obj.get("per_query_verification_details") or []
    verification_failure_values: dict[str, Counter[str]] = {k: Counter() for k in target_fields}

    for qd in per_query:
        detected_metadata = qd.get("detected_metadata_entities") or {}
        detected_kg = qd.get("detected_kg_linked_entities") or {}
        # If KG linked entities empty for a field, count the metadata detected terms as "gap evidence".
        for ft in ["disease", "species", "location", "mode"]:
            md_list = detected_metadata.get(ft) or []
            kg_list = detected_kg.get(ft) or []
            if len(md_list) > 0 and len(kg_list) == 0:
                for md_item in md_list:
                    md_item = md_item or {}
                    canon = md_item.get("canonical") or ""
                    alias = md_item.get("alias") or ""
                    # Use both canonical and matched alias text as gap evidence.
                    if canon:
                        verification_failure_values[ft][_normalize_for_grouping(canon)] += 1
                    if alias:
                        verification_failure_values[ft][_normalize_for_grouping(alias)] += 1

    # Build suggestions for top gaps
    gap_items: list[GapItem] = []

    label_to_entities = _build_ontology_alias_lookup(kg_index)
    uri_to_info = kg_index.get("uri_to_info") or {}

    # Limit analysis size: top terms per field by occurrence_count (plus failures)
    for ft in ["species", "disease", "location", "mode"]:
        sub = group_counts[group_counts["field_type"] == ft].copy()
        if sub.empty:
            continue
        sub = sub.sort_values(["occurrence_count"], ascending=False).head(30)

        for _, row in sub.iterrows():
            raw = str(row["raw_value"])
            norm = str(row["normalized_value"])
            occ = int(row["occurrence_count"])
            status_sample = str(row.get("status_sample", ""))
            mapped_uri_or_reason = str(row.get("mapped_uri_or_reason", "") or "")

            # Prefer mapped_manual mapped URI when available (grounded).
            suggested_uri: str | None = None
            suggested_label: str | None = None
            conf: str = "low"

            if "mapped_manual" in status_sample.lower() and mapped_uri_or_reason.startswith("http"):
                suggested_uri = mapped_uri_or_reason
                suggested_label = (uri_to_info.get(suggested_uri) or {}).get("label")
                conf = "high"
            else:
                suggested_uri, suggested_label, conf = _infer_target_from_near_match(ft, norm, kg_index)

            gap_items.append(
                GapItem(
                    field_type=ft,
                    raw_value=raw,
                    normalized_value=norm,
                    occurrence_count=occ,
                    currently_mapped=False,
                    suggested_target_entity_uri=suggested_uri,
                    suggested_target_label=suggested_label,
                    confidence=conf if suggested_uri else "low",
                    evidence_source="mapping_report",
                )
            )

    # Add explicit query-failure terms even if not in mapping_report unmapped list
    # (e.g. "tôm hùm", "Khánh Hòa")
    for ft in ["species", "location", "mode", "disease"]:
        c = verification_failure_values.get(ft) or Counter()
        if not c:
            continue
        for norm_val, cnt in c.most_common(15):
            # try to get a readable raw_value from norm
            raw_value = norm_val
            suggested_uri, suggested_label, conf = _infer_target_from_near_match(ft, norm_val, kg_index)
            if suggested_uri and conf == "medium":
                # For near-match substring that strongly contains the missing term,
                # upgrade to high confidence for conservative alias enrichment.
                label = suggested_label or ""
                if label:
                    a = kg_runtime.normalize_kg_text(label)
                    if norm_val in a or a in norm_val:
                        conf = "high"
            gap_items.append(
                GapItem(
                    field_type=ft,
                    raw_value=raw_value,
                    normalized_value=norm_val,
                    occurrence_count=int(cnt),
                    currently_mapped=False,
                    suggested_target_entity_uri=suggested_uri,
                    suggested_target_label=suggested_label,
                    confidence=conf,
                    evidence_source="verification",
                )
            )

    # De-dupe by (field_type, normalized_value, suggested_target_entity_uri)
    seen = set()
    deduped: list[GapItem] = []
    for it in sorted(gap_items, key=lambda x: (-x.occurrence_count, x.field_type)):
        key = (it.field_type, it.normalized_value, it.suggested_target_entity_uri)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(it)

    # Sort final: high occurrence first, medium confidence ahead of low
    conf_rank = {"high": 3, "medium": 2, "low": 1}
    deduped.sort(key=lambda x: (-x.occurrence_count, -conf_rank.get(x.confidence, 1), x.field_type, x.normalized_value))

    # Save outputs
    json_out = {
        "ontology_owl_analyzed": str(INPUT_OWL_PATH),
        "metadata_rows": int(len(df_meta)),
        "mapping_report_rows": int(len(df)),
        "top_gap_items": [it.__dict__ for it in deduped[:200]],
    }
    _safe_json_dump(json_out, OUTPUT_JSON_PATH)

    # CSV
    OUTPUT_CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([it.__dict__ for it in deduped]).to_csv(OUTPUT_CSV_PATH, index=False, encoding="utf-8-sig")

    print("[ALIAS-GAP] Done.")
    print(f"[ALIAS-GAP] JSON: {OUTPUT_JSON_PATH}")
    print(f"[ALIAS-GAP] CSV:  {OUTPUT_CSV_PATH}")


if __name__ == "__main__":
    analyze()

