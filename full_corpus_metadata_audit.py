from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import pandas as pd

import hybrid_search


META_PATH = Path("data") / "metadata" / "document_metadata_cleaned.xlsx"
RAW_DOCS_DIR = Path("data") / "raw_docs"

OUT_JSON = Path("outputs") / "full_corpus_metadata_audit.json"
OUT_CSV = Path("outputs") / "full_corpus_metadata_audit_summary.csv"


REQUIRED_COLS = [
    "doc_id",
    "title",
    "file_path",
    "related_taxon",
    "related_disease",
    "related_location",
    "production_mode",
]


NOISE_DISEASE_TOPICS = {
    "biosecurity",
    "health management",
    "disease prevention",
    "disease control",
    "disease risk",
    "pathogens",
    "environmental impact",
    "viral disease",
    "viroses",
    "fish diseases",
    "aquatic animal diseases",
}

GENERIC_TAXON = {"shrimp", "fish", "aquatic animals", "aquatic species", "prawns"}
GENERIC_MODE = {"aquaculture", "fisheries"}


def _utf8() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stdin.reconfigure(encoding="utf-8")
    except Exception:
        pass


def _split(cell: Any) -> list[str]:
    return hybrid_search.split_multi_value(cell)


def _norm(s: Any) -> str:
    return hybrid_search.normalize_text(s)


def _safe_rel(path: Path) -> str:
    try:
        return str(path.relative_to(Path(".")))
    except Exception:
        return str(path)


def main() -> None:
    _utf8()
    if not META_PATH.exists():
        raise FileNotFoundError(f"Missing metadata: {META_PATH}")
    if not RAW_DOCS_DIR.exists():
        raise FileNotFoundError(f"Missing raw docs dir: {RAW_DOCS_DIR}")

    df = pd.read_excel(META_PATH)
    missing_cols = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    # Basic counts
    doc_ids = df["doc_id"].astype(str).str.strip().tolist()
    file_paths = df["file_path"].astype(str).str.strip().tolist()

    doc_id_counts = Counter([d for d in doc_ids if d])
    file_path_counts = Counter([_norm(p) for p in file_paths if p and p.lower() != "nan"])

    dup_doc_ids = sorted([d for d, c in doc_id_counts.items() if c > 1])
    dup_file_paths = sorted([p for p, c in file_path_counts.items() if c > 1])

    # File existence checks (metadata -> pdf)
    missing_pdf_rows = []
    existing_pdf_rows = 0
    for i, row in df.iterrows():
        doc_id = str(row.get("doc_id", "")).strip()
        fp = str(row.get("file_path", "")).strip()
        abs_fp = Path(".") / fp if fp else None
        if not fp or abs_fp is None or not abs_fp.exists():
            missing_pdf_rows.append(
                {
                    "row_index": int(i),
                    "doc_id": doc_id,
                    "file_path": fp,
                    "reason": "missing file_path" if not fp else "file not found",
                }
            )
        else:
            existing_pdf_rows += 1

    # raw_docs -> metadata coverage
    pdfs = sorted([p for p in RAW_DOCS_DIR.glob("*.pdf")])
    pdf_basenames = {p.name: p for p in pdfs}

    # Map metadata rows to raw_docs by basename match if possible.
    meta_basenames = set()
    for fp in file_paths:
        if not fp or fp.lower() == "nan":
            continue
        meta_basenames.add(Path(fp).name)

    pdf_without_metadata = sorted([name for name in pdf_basenames.keys() if name not in meta_basenames])
    metadata_without_pdf = sorted([name for name in meta_basenames if name not in pdf_basenames])

    # Term distributions
    def term_counter(col: str) -> Counter[str]:
        c = Counter()
        for cell in df[col].tolist():
            for t in _split(cell):
                c[t.strip()] += 1
        return c

    disease_terms = term_counter("related_disease")
    taxon_terms = term_counter("related_taxon")
    location_terms = term_counter("related_location")
    mode_terms = term_counter("production_mode")

    # Suspicious/noise values (normalized)
    def top_flagged(counter: Counter[str], flagged_norm: set[str], limit: int = 50) -> list[dict[str, Any]]:
        out = []
        for v, cnt in counter.most_common(limit):
            out.append(
                {
                    "value": v,
                    "count": int(cnt),
                    "flagged": _norm(v) in flagged_norm,
                }
            )
        return out

    noise_disease_present = [
        {"term": t, "count": int(c)}
        for t, c in disease_terms.items()
        if _norm(t) in NOISE_DISEASE_TOPICS
    ]
    noise_disease_present.sort(key=lambda x: -x["count"])

    generic_taxon_present = [
        {"term": t, "count": int(c)}
        for t, c in taxon_terms.items()
        if _norm(t) in GENERIC_TAXON
    ]
    generic_taxon_present.sort(key=lambda x: -x["count"])

    generic_mode_present = [
        {"term": t, "count": int(c)}
        for t, c in mode_terms.items()
        if _norm(t) in GENERIC_MODE
    ]
    generic_mode_present.sort(key=lambda x: -x["count"])

    # Location normalization issues: multiple raw forms with same normalized form
    loc_norm_to_raw = defaultdict(set)
    for t in location_terms.keys():
        loc_norm_to_raw[_norm(t)].add(t)
    loc_variants = [
        {"normalized": n, "variants": sorted(list(v)), "variant_count": len(v)}
        for n, v in loc_norm_to_raw.items()
        if len(v) > 1
    ]
    loc_variants.sort(key=lambda x: (-x["variant_count"], x["normalized"]))

    audit = {
        "metadata_path": str(META_PATH),
        "raw_docs_dir": str(RAW_DOCS_DIR),
        "total_pdf_files_in_raw_docs": len(pdfs),
        "total_metadata_rows": int(len(df)),
        "total_distinct_doc_id": int(len(set([d for d in doc_ids if d]))),
        "dup_doc_id_count": int(len(dup_doc_ids)),
        "dup_doc_ids": dup_doc_ids[:200],
        "dup_file_path_count": int(len(dup_file_paths)),
        "dup_file_paths_norm": dup_file_paths[:200],
        "metadata_rows_with_existing_pdf": int(existing_pdf_rows),
        "metadata_rows_missing_pdf": int(len(missing_pdf_rows)),
        "missing_pdf_rows_sample": missing_pdf_rows[:200],
        "pdf_without_metadata_count": int(len(pdf_without_metadata)),
        "pdf_without_metadata_sample": pdf_without_metadata[:200],
        "metadata_without_pdf_count": int(len(metadata_without_pdf)),
        "metadata_without_pdf_sample": metadata_without_pdf[:200],
        "top_disease_terms": top_flagged(disease_terms, NOISE_DISEASE_TOPICS, limit=40),
        "top_taxon_terms": top_flagged(taxon_terms, GENERIC_TAXON, limit=40),
        "top_location_terms": [{"value": v, "count": int(c)} for v, c in location_terms.most_common(40)],
        "top_mode_terms": top_flagged(mode_terms, GENERIC_MODE, limit=40),
        "noise_disease_terms_present": noise_disease_present[:200],
        "generic_taxon_terms_present": generic_taxon_present[:200],
        "generic_mode_terms_present": generic_mode_present[:200],
        "location_normalization_variants": loc_variants[:200],
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")

    # Summary CSV: one-row + a few key lists serialized
    summary = {
        "total_pdf_files_in_raw_docs": len(pdfs),
        "total_metadata_rows": len(df),
        "total_distinct_doc_id": len(set([d for d in doc_ids if d])),
        "dup_doc_id_count": len(dup_doc_ids),
        "dup_file_path_count": len(dup_file_paths),
        "pdf_without_metadata_count": len(pdf_without_metadata),
        "metadata_without_pdf_count": len(metadata_without_pdf),
        "metadata_rows_missing_pdf": len(missing_pdf_rows),
        "top_noise_disease_terms": "; ".join([f"{x['term']}({x['count']})" for x in noise_disease_present[:20]]),
        "top_generic_taxon_terms": "; ".join([f"{x['term']}({x['count']})" for x in generic_taxon_present[:20]]),
        "top_generic_mode_terms": "; ".join([f"{x['term']}({x['count']})" for x in generic_mode_present[:20]]),
    }
    pd.DataFrame([summary]).to_csv(OUT_CSV, index=False, encoding="utf-8")

    print(f"[AUDIT] Wrote {OUT_JSON}")
    print(f"[AUDIT] Wrote {OUT_CSV}")


if __name__ == "__main__":
    main()

