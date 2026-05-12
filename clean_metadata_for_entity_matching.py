from __future__ import annotations

import json
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

import hybrid_search
import kg_runtime


META_IN = Path("data") / "metadata" / "document_metadata.xlsx"
META_OUT = Path("data") / "metadata" / "document_metadata_cleaned.xlsx"
REPORT_JSON = Path("outputs") / "metadata_cleanup_report.json"
REPORT_CSV = Path("outputs") / "metadata_cleanup_report.csv"


TOPIC_LIKE = {
    "health management",
    "biosecurity",
    "disease prevention",
    "disease risk",
    "disease control",
    "fish diseases",
    "aquatic animal diseases",
    "animal diseases",
    "animal health",
    "health",
    "pathogens",
    "pathogen introduction",
    "pathogen spread",
    "disease surveillance",
    "environmental impact",
    "environmental hazards",
    "environmental risk",
    "ecosystem effects",
    "ecosystem management",
    "climate change",
    "pollution",
    "socio-economic impact",
    "production risk",
    "adaptation",
    "sustainability",
    "sustainable aquaculture",
    "water quality",
    "mangroves",
    "antimicrobial resistance",
    "amr",
}

NON_TAXON_TOPICS = {
    "aquatic environment",
    "marine environment",
    "inland waters",
    "brackishwater species",
    "aquaculture species",
    "coastal species",
    "fisheries",
    "seaweed",
    "decapoda",
}


def _utf8() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stdin.reconfigure(encoding="utf-8")
    except Exception:
        pass


def _split(cell: Any) -> list[str]:
    return hybrid_search.split_multi_value(cell)


def _join(vals: list[str]) -> str:
    return "; ".join(vals)


def _norm(s: str) -> str:
    return hybrid_search.normalize_text(s)


def _canonical_location(raw: str) -> str:
    n = _norm(raw)
    # stable title-case mapping for common values
    mapping = {
        "viet nam": "Vietnam",
        "vietnam": "Vietnam",
        "global": "Global",
        "khanh hoa": "Khanh Hoa",
        "an do": "India",
        "india": "India",
    }
    if n in mapping:
        return mapping[n]
    # keep original casing if already looks like proper noun; otherwise title-case
    return raw.strip()


def _canonical_mode(raw: str) -> str:
    n = _norm(raw)
    mapping = {
        "nuoi tom": "shrimp aquaculture",
        "nuôi tôm": "shrimp aquaculture",
        "trai giong": "hatchery aquaculture",
        "trại giống": "hatchery aquaculture",
    }
    return mapping.get(n, raw.strip())


def _canonical_species(raw: str) -> str:
    n = _norm(raw)
    mapping = {
        "litopenaeus vannamei": "Penaeus vannamei",
        "white shrimp": "Penaeus vannamei",
        "whiteleg shrimp": "Penaeus vannamei",
        "cultured shrimp": "shrimp",
        # "prawns" is generic; keep as-is to avoid forcing species.
    }
    if n in mapping:
        return mapping[n]
    # Keep canonicalization already used by runtime.
    return hybrid_search.canonicalize_term("species", raw.strip())


def _canonical_disease(raw: str) -> str:
    n = _norm(raw)
    # First: topic-like => return empty (we will move to keywords)
    if n in TOPIC_LIKE:
        return ""
    # Use KG registry (same as disease bridge), so acronym/EN/VI can converge.
    # Here we don't have URI, so map based on string tokens.
    candidates = [raw, n, n.replace(" ", "").replace("-", "").replace("_", "")]
    # Build a temporary fake "info" and run registry check via direct token match.
    # (We reuse kg_runtime registry semantics but avoid needing an ontology URI.)
    keys = set()
    for c in candidates:
        nn = kg_runtime.normalize_kg_text(c).replace(" ", "").replace("-", "").replace("_", "")
        if nn:
            keys.add(nn)
    for canon, tokens in getattr(kg_runtime, "_DISEASE_CANONICAL_REGISTRY", []):
        if any(k in tokens for k in keys) or any(any(t in k for t in tokens) for k in keys):
            return canon
    # Keep original (trim) if not mapped
    return raw.strip()


def _append_keywords(existing: Any, extra_terms: list[str]) -> str:
    base = str(existing or "").strip()
    existing_terms = [t.strip() for t in base.split(";") if t.strip()] if base else []
    seen = { _norm(t) for t in existing_terms if _norm(t) }
    out = list(existing_terms)
    for t in extra_terms:
        tt = t.strip()
        if not tt:
            continue
        k = _norm(tt)
        if k and k not in seen:
            seen.add(k)
            out.append(tt)
    return "; ".join(out)


def main() -> None:
    _utf8()
    if not META_IN.exists():
        raise FileNotFoundError(f"Missing: {META_IN}")

    df = pd.read_excel(META_IN)
    required_cols = {"doc_id", "title", "file_path", "related_taxon", "related_disease", "related_location", "production_mode"}
    missing = sorted([c for c in required_cols if c not in df.columns])
    if missing:
        raise ValueError(f"Missing required metadata columns: {missing}")

    # Backup original before writing any cleaned file.
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = META_IN.with_suffix(f".xlsx.bak_{ts}")
    shutil.copy2(str(META_IN), str(backup_path))

    changes: list[dict[str, Any]] = []
    for i, row in df.iterrows():
        doc_id = str(row.get("doc_id", "")).strip()

        moved_to_keywords: list[str] = []

        # Disease cleanup
        disease_in = _split(row.get("related_disease", ""))
        disease_out: list[str] = []
        for t in disease_in:
            canon = _canonical_disease(t)
            if not canon:
                moved_to_keywords.append(t)
                continue
            disease_out.append(canon)

        # Species cleanup
        tax_in = _split(row.get("related_taxon", ""))
        tax_out: list[str] = []
        for t in tax_in:
            n = _norm(t)
            if n in NON_TAXON_TOPICS:
                moved_to_keywords.append(t)
                continue
            tax_out.append(_canonical_species(t))

        # Location cleanup
        loc_in = _split(row.get("related_location", ""))
        loc_out: list[str] = []
        for t in loc_in:
            loc_out.append(_canonical_location(t))

        # Mode cleanup
        mode_in = _split(row.get("production_mode", ""))
        mode_out: list[str] = []
        for t in mode_in:
            mode_out.append(_canonical_mode(t))

        # De-dupe (normalized)
        def dedupe(vals: list[str]) -> list[str]:
            seen = set()
            out2 = []
            for v in vals:
                k = _norm(v)
                if k and k not in seen:
                    seen.add(k)
                    out2.append(v)
            return out2

        disease_out = dedupe(disease_out)
        tax_out = dedupe(tax_out)
        loc_out = dedupe(loc_out)
        mode_out = dedupe(mode_out)

        before = {
            "related_disease": _join(disease_in),
            "related_taxon": _join(tax_in),
            "related_location": _join(loc_in),
            "production_mode": _join(mode_in),
            "keywords": str(row.get("keywords", "") or ""),
        }
        after = {
            "related_disease": _join(disease_out),
            "related_taxon": _join(tax_out),
            "related_location": _join(loc_out),
            "production_mode": _join(mode_out),
            "keywords": _append_keywords(row.get("keywords", ""), moved_to_keywords),
        }

        # Write back to dataframe
        df.at[i, "related_disease"] = after["related_disease"]
        df.at[i, "related_taxon"] = after["related_taxon"]
        df.at[i, "related_location"] = after["related_location"]
        df.at[i, "production_mode"] = after["production_mode"]
        df.at[i, "keywords"] = after["keywords"]

        if before != after:
            changes.append(
                {
                    "row_index": int(i),
                    "doc_id": doc_id,
                    "before": before,
                    "after": after,
                    "moved_to_keywords": moved_to_keywords,
                }
            )

    META_OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(META_OUT, index=False)

    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(
        json.dumps(
            {
                "input": str(META_IN),
                "backup": str(backup_path),
                "output": str(META_OUT),
                "changed_rows": len(changes),
                "changes": changes,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    # Flatten CSV for quick scan
    rows = []
    for ch in changes:
        rows.append(
            {
                "row_index": ch["row_index"],
                "doc_id": ch["doc_id"],
                "related_disease_before": ch["before"]["related_disease"],
                "related_disease_after": ch["after"]["related_disease"],
                "related_taxon_before": ch["before"]["related_taxon"],
                "related_taxon_after": ch["after"]["related_taxon"],
                "related_location_before": ch["before"]["related_location"],
                "related_location_after": ch["after"]["related_location"],
                "production_mode_before": ch["before"]["production_mode"],
                "production_mode_after": ch["after"]["production_mode"],
                "moved_to_keywords": "; ".join(ch["moved_to_keywords"]),
            }
        )
    pd.DataFrame(rows).to_csv(REPORT_CSV, index=False, encoding="utf-8")

    print(f"[CLEAN] Backup: {backup_path}")
    print(f"[CLEAN] Output: {META_OUT}")
    print(f"[CLEAN] Report: {REPORT_JSON}")
    print(f"[CLEAN] Report: {REPORT_CSV}")


if __name__ == "__main__":
    main()

