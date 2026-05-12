from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import pandas as pd

import hybrid_search
import kg_runtime


OUT_DIR = Path("outputs")
META_PATH = Path("data") / "metadata" / "document_metadata.xlsx"

OUT_JSON = OUT_DIR / "alias_metadata_noise_audit.json"
OUT_CSV = OUT_DIR / "alias_metadata_noise_audit_top_terms.csv"


FIELDS = [
    ("disease", "related_disease"),
    ("species", "related_taxon"),
    ("location", "related_location"),
    ("mode", "production_mode"),
]


TOPIC_LIKE_TERMS = {
    "health management",
    "biosecurity",
    "disease prevention",
    "disease risk",
    "disease control",
    "fish diseases",
    "aquatic animal diseases",
    "pathogens",
    "environmental impact",
    "climate change",
}


def _utf8() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stdin.reconfigure(encoding="utf-8")
    except Exception:
        pass


def _split(cell: Any) -> list[str]:
    return hybrid_search.split_multi_value(cell)


def _write_json(p: Path, obj: Any) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def audit_metadata(df: pd.DataFrame) -> dict[str, Any]:
    per_field = {}
    for et, col in FIELDS:
        cnt = Counter()
        norm_cnt = Counter()
        examples = defaultdict(list)
        for cell in df.get(col, []).tolist():
            for v in _split(cell):
                v = str(v).strip()
                if not v:
                    continue
                cnt[v] += 1
                n = hybrid_search.normalize_text(v)
                norm_cnt[n] += 1
                if len(examples[n]) < 5:
                    examples[n].append(v)

        top_raw = [{"value": v, "count": c, "is_topic_like": hybrid_search.normalize_text(v) in TOPIC_LIKE_TERMS} for v, c in cnt.most_common(50)]
        top_norm = [{"normalized": n, "count": c, "examples": examples[n]} for n, c in norm_cnt.most_common(50)]

        per_field[et] = {
            "column": col,
            "distinct_raw": len(cnt),
            "distinct_normalized": len(norm_cnt),
            "top_raw": top_raw,
            "top_normalized": top_norm,
        }
    return per_field


def audit_manual_aliases() -> dict[str, Any]:
    out = {}
    for et, mapping in hybrid_search.MANUAL_ALIASES.items():
        alias_to_canon = defaultdict(set)
        for canon, aliases in mapping.items():
            canon_n = hybrid_search.normalize_text(hybrid_search.canonicalize_term(et, canon))
            alias_to_canon[canon_n].add(canon)
            for a in aliases:
                a_n = hybrid_search.normalize_text(hybrid_search.canonicalize_term(et, a))
                if a_n:
                    alias_to_canon[a_n].add(canon)

        ambiguous = [
            {"alias_norm": a, "canonicals": sorted(list(cs)), "count": len(cs)}
            for a, cs in alias_to_canon.items()
            if len(cs) > 1
        ]
        ambiguous.sort(key=lambda x: (-x["count"], x["alias_norm"]))

        too_generic = []
        for a, cs in alias_to_canon.items():
            if a in TOPIC_LIKE_TERMS or a in {"shrimp", "fish", "aquatic animals", "aquatic species", "pathogens"}:
                too_generic.append({"alias_norm": a, "canonicals": sorted(list(cs))})

        out[et] = {
            "alias_count_norm": len(alias_to_canon),
            "ambiguous_aliases": ambiguous[:50],
            "generic_or_topic_aliases": too_generic[:50],
        }
    return out


def audit_kg_alias_ambiguity() -> dict[str, Any]:
    # Use runtime preferred ontology.
    g, loaded, _src = kg_runtime.load_kg_prefer_facts_then_alias_enriched(
        hybrid_search.KG_FACT_ENRICHED_PATH,
        hybrid_search.KG_ALIAS_ENRICHED_PATH,
        hybrid_search.KG_ENRICHED_PATH,
        hybrid_search.KG_FALLBACK_PATH,
    )
    idx = kg_runtime.build_kg_index(g)
    l2e = idx.get("label_to_entities") or {}

    ambiguous_by_type = defaultdict(list)
    for alias_norm, ents in l2e.items():
        by_type = defaultdict(set)
        for e in ents:
            by_type[e.get("entity_type")].add(e.get("uri"))
        for et, uris in by_type.items():
            if et in {"disease", "species", "location", "mode"} and len(uris) > 1:
                ambiguous_by_type[et].append(
                    {"alias_norm": alias_norm, "uris": sorted(list(uris)), "count": len(uris)}
                )

    for et in ambiguous_by_type.keys():
        ambiguous_by_type[et].sort(key=lambda x: (-x["count"], x["alias_norm"]))

    return {
        "ontology_loaded": loaded,
        "ambiguous_aliases": {et: ambiguous_by_type[et][:50] for et in ambiguous_by_type.keys()},
    }


def main() -> None:
    _utf8()
    if not META_PATH.exists():
        raise FileNotFoundError(f"Missing metadata file: {META_PATH}")

    df = pd.read_excel(META_PATH)
    meta_cols = list(df.columns)

    meta_audit = audit_metadata(df)
    manual_audit = audit_manual_aliases()
    kg_audit = audit_kg_alias_ambiguity()

    out = {
        "metadata_path": str(META_PATH),
        "metadata_columns": meta_cols,
        "metadata_audit": meta_audit,
        "manual_alias_audit": manual_audit,
        "kg_alias_ambiguity_audit": kg_audit,
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    _write_json(OUT_JSON, out)

    # Small CSV for quick scanning: top raw values per field.
    rows = []
    for et, info in meta_audit.items():
        for r in info["top_raw"]:
            rows.append(
                {
                    "entity_type": et,
                    "column": info["column"],
                    "raw_value": r["value"],
                    "count": r["count"],
                    "is_topic_like": r["is_topic_like"],
                }
            )
    pd.DataFrame(rows).to_csv(OUT_CSV, index=False, encoding="utf-8")
    print(f"[AUDIT] Wrote: {OUT_JSON}")
    print(f"[AUDIT] Wrote: {OUT_CSV}")


if __name__ == "__main__":
    main()

