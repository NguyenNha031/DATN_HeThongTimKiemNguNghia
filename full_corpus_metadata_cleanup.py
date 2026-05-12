from __future__ import annotations

import json
import shutil
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

import hybrid_search
import kg_runtime


META_PATH = Path("data") / "metadata" / "document_metadata_cleaned.xlsx"
RAW_DOCS_DIR = Path("data") / "raw_docs"

OUT_REPORT_JSON = Path("outputs") / "full_corpus_metadata_cleanup_report.json"
OUT_REPORT_CSV = Path("outputs") / "full_corpus_metadata_cleanup_report.csv"
OUT_EFFECT_JSON = Path("outputs") / "full_corpus_metadata_cleanup_effect_summary.json"


TOPIC_LIKE_DISEASE = {
    "biosecurity",
    "health management",
    "disease prevention",
    "disease risk",
    "disease control",
    "fish diseases",
    "aquatic animal diseases",
    "animal diseases",
    "animal health",
    "pathogens",
    "viral disease",
    "viroses",
    "environmental impact",
    "environmental hazards",
    "environmental risk",
    "climate change",
    "pollution",
    "sustainability",
    "sustainable aquaculture",
    "water quality",
}

NON_TAXON_TOPICS = {
    "aquatic environment",
    "marine environment",
    "inland waters",
    "brackishwater species",
    "aquaculture species",
    "coastal species",
    "fisheries",  # ambiguous (mode vs topic) – keep as mode, not taxon
    "seaweed",    # could be taxon-ish but not modeled; keep as topic
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


def _norm(s: Any) -> str:
    return hybrid_search.normalize_text(s)


def _append_keywords(existing: Any, extra_terms: list[str]) -> str:
    base = str(existing or "").strip()
    existing_terms = [t.strip() for t in base.split(";") if t.strip()] if base else []
    seen = {_norm(t) for t in existing_terms if _norm(t)}
    out = list(existing_terms)
    for t in extra_terms:
        tt = str(t or "").strip()
        if not tt:
            continue
        k = _norm(tt)
        if k and k not in seen:
            seen.add(k)
            out.append(tt)
    return "; ".join(out)


def _canonical_location(raw: str) -> str:
    n = _norm(raw)
    mapping = {
        "viet nam": "Vietnam",
        "vietnam": "Vietnam",
        "global": "Global",
    }
    if n in mapping:
        return mapping[n]
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
    }
    if n in mapping:
        return mapping[n]
    return hybrid_search.canonicalize_term("species", raw.strip())


def _canonical_disease(raw: str) -> str:
    n = _norm(raw)
    if n in TOPIC_LIKE_DISEASE:
        return ""
    # Canonicalize common diseases using the same registry semantics as KG bridge.
    candidates = [raw, n, n.replace(" ", "").replace("-", "").replace("_", "")]
    keys = set()
    for c in candidates:
        nn = kg_runtime.normalize_kg_text(c).replace(" ", "").replace("-", "").replace("_", "")
        if nn:
            keys.add(nn)
    for canon, tokens in getattr(kg_runtime, "_DISEASE_CANONICAL_REGISTRY", []):
        if any(k in tokens for k in keys) or any(any(t in k for t in tokens) for k in keys):
            return canon
    return raw.strip()


def _dedupe(vals: list[str]) -> list[str]:
    seen = set()
    out = []
    for v in vals:
        vv = str(v or "").strip()
        if not vv:
            continue
        k = _norm(vv)
        if k and k not in seen:
            seen.add(k)
            out.append(vv)
    return out


def _resolve_duplicate_doc_ids(df: pd.DataFrame) -> tuple[pd.DataFrame, list[dict[str, Any]]]:
    """
    Ensure doc_id is unique:
    - If duplicates point to different file basenames, append a deterministic suffix derived from basename.
      Example: FAO_042 + FAO_042_biosecurity_philippines.pdf -> doc_id becomes "FAO_042_biosecurity_philippines".
    """
    changes = []
    counts = Counter(df["doc_id"].astype(str).str.strip().tolist())
    dup_ids = [d for d, c in counts.items() if d and c > 1]
    if not dup_ids:
        return df, changes

    used = set(df["doc_id"].astype(str).str.strip().tolist())
    for dup in dup_ids:
        rows = df[df["doc_id"].astype(str).str.strip() == dup]
        if len(rows) <= 1:
            continue
        for idx, row in rows.iterrows():
            fp = str(row.get("file_path", "")).strip()
            base = Path(fp).stem if fp else ""
            if base and base != dup:
                new_id = base
                if new_id in used:
                    # Last resort: add short suffix
                    new_id = f"{base}_{idx}"
                if new_id != dup:
                    used.add(new_id)
                    df.at[idx, "doc_id"] = new_id
                    changes.append(
                        {
                            "row_index": int(idx),
                            "old_doc_id": dup,
                            "new_doc_id": new_id,
                            "file_path": fp,
                            "reason": "duplicate doc_id resolved by basename-derived id",
                        }
                    )
    return df, changes


def main() -> None:
    _utf8()
    if not META_PATH.exists():
        raise FileNotFoundError(f"Missing metadata: {META_PATH}")
    if not RAW_DOCS_DIR.exists():
        raise FileNotFoundError(f"Missing raw docs: {RAW_DOCS_DIR}")

    df = pd.read_excel(META_PATH)
    backup = META_PATH.with_suffix(f".xlsx.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    shutil.copy2(str(META_PATH), str(backup))

    changes: list[dict[str, Any]] = []
    moved_disease_terms = Counter()
    moved_taxon_terms = Counter()
    canonicalized = Counter()

    # Resolve duplicate doc_ids first.
    df, dup_changes = _resolve_duplicate_doc_ids(df)
    changes.extend([{"type": "doc_id_fix", **c} for c in dup_changes])

    # Per-row cleanup
    for i, row in df.iterrows():
        before = {
            "related_disease": str(row.get("related_disease", "") or ""),
            "related_taxon": str(row.get("related_taxon", "") or ""),
            "related_location": str(row.get("related_location", "") or ""),
            "production_mode": str(row.get("production_mode", "") or ""),
            "keywords": str(row.get("keywords", "") or ""),
        }

        moved_to_keywords: list[str] = []

        # Disease: remove topics + canonicalize known diseases
        dis_in = _split(row.get("related_disease", ""))
        dis_out = []
        for t in dis_in:
            c = _canonical_disease(t)
            if not c:
                moved_to_keywords.append(t)
                moved_disease_terms[_norm(t)] += 1
                continue
            if c != t.strip():
                canonicalized[f"disease::{t.strip()}=>{c}"] += 1
            dis_out.append(c)

        # Taxon: move obvious topics, canonicalize known scientific aliases
        tax_in = _split(row.get("related_taxon", ""))
        tax_out = []
        for t in tax_in:
            if _norm(t) in NON_TAXON_TOPICS:
                moved_to_keywords.append(t)
                moved_taxon_terms[_norm(t)] += 1
                continue
            c = _canonical_species(t)
            if c != t.strip():
                canonicalized[f"taxon::{t.strip()}=>{c}"] += 1
            tax_out.append(c)

        # Location canonicalization
        loc_in = _split(row.get("related_location", ""))
        loc_out = []
        for t in loc_in:
            c = _canonical_location(t)
            if c != t.strip():
                canonicalized[f"location::{t.strip()}=>{c}"] += 1
            loc_out.append(c)

        # Mode canonicalization
        mode_in = _split(row.get("production_mode", ""))
        mode_out = []
        for t in mode_in:
            c = _canonical_mode(t)
            if c != t.strip():
                canonicalized[f"mode::{t.strip()}=>{c}"] += 1
            mode_out.append(c)

        dis_out = _dedupe(dis_out)
        tax_out = _dedupe(tax_out)
        loc_out = _dedupe(loc_out)
        mode_out = _dedupe(mode_out)

        after = {
            "related_disease": _join(dis_out),
            "related_taxon": _join(tax_out),
            "related_location": _join(loc_out),
            "production_mode": _join(mode_out),
            "keywords": _append_keywords(row.get("keywords", ""), moved_to_keywords),
        }

        if before != after:
            changes.append(
                {
                    "type": "row_cleanup",
                    "row_index": int(i),
                    "doc_id": str(df.at[i, "doc_id"]),
                    "before": before,
                    "after": after,
                    "moved_to_keywords": moved_to_keywords,
                }
            )
            df.at[i, "related_disease"] = after["related_disease"]
            df.at[i, "related_taxon"] = after["related_taxon"]
            df.at[i, "related_location"] = after["related_location"]
            df.at[i, "production_mode"] = after["production_mode"]
            df.at[i, "keywords"] = after["keywords"]

    # Write back in-place (requested)
    df.to_excel(META_PATH, index=False)

    OUT_REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_REPORT_JSON.write_text(
        json.dumps(
            {
                "metadata_file": str(META_PATH),
                "backup": str(backup),
                "changed_items": len(changes),
                "changes_sample": changes[:200],
                "moved_disease_terms": dict(moved_disease_terms.most_common(50)),
                "moved_taxon_terms": dict(moved_taxon_terms.most_common(50)),
                "canonicalized_sample": dict(canonicalized.most_common(80)),
                "notes": [
                    "Generic taxon terms (shrimp/fish/aquatic animals/aquatic species) are kept; runtime downweights them as weak signals.",
                    "Topic-like disease terms are moved from related_disease to keywords (conservative, no information loss).",
                ],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    # Flatten CSV rows
    flat = []
    for ch in changes:
        if ch["type"] == "doc_id_fix":
            flat.append(
                {
                    "type": "doc_id_fix",
                    "row_index": ch["row_index"],
                    "doc_id_before": ch["old_doc_id"],
                    "doc_id_after": ch["new_doc_id"],
                    "field": "doc_id",
                    "moved_to_keywords": "",
                }
            )
        else:
            flat.append(
                {
                    "type": "row_cleanup",
                    "row_index": ch["row_index"],
                    "doc_id_before": "",
                    "doc_id_after": ch["doc_id"],
                    "field": "multi",
                    "moved_to_keywords": "; ".join(ch.get("moved_to_keywords") or []),
                }
            )
    pd.DataFrame(flat).to_csv(OUT_REPORT_CSV, index=False, encoding="utf-8")

    effect = {
        "metadata_file": str(META_PATH),
        "backup": str(backup),
        "changed_rows_or_fixes": len(changes),
        "duplicate_doc_id_fixes": len(dup_changes),
        "moved_disease_terms_total": int(sum(moved_disease_terms.values())),
        "moved_taxon_terms_total": int(sum(moved_taxon_terms.values())),
        "top_moved_disease_terms": dict(moved_disease_terms.most_common(20)),
        "top_moved_taxon_terms": dict(moved_taxon_terms.most_common(20)),
    }
    OUT_EFFECT_JSON.write_text(json.dumps(effect, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[CLEANUP] Backup: {backup}")
    print(f"[CLEANUP] Updated: {META_PATH}")
    print(f"[CLEANUP] Report: {OUT_REPORT_JSON}")
    print(f"[CLEANUP] Report: {OUT_REPORT_CSV}")
    print(f"[CLEANUP] Effect: {OUT_EFFECT_JSON}")


if __name__ == "__main__":
    main()

