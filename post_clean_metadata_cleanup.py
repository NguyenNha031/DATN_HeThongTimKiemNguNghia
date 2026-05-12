from __future__ import annotations

import json
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

import hybrid_search


META_PATH = Path("data") / "metadata" / "document_metadata_cleaned.xlsx"
REPORT_JSON = Path("outputs") / "post_clean_metadata_cleanup_report.json"

MOVE_FROM_DISEASE_TO_KEYWORDS = {"viral disease", "viroses"}


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


def _append_keywords(existing: Any, extra: list[str]) -> str:
    base = str(existing or "").strip()
    out = [t.strip() for t in base.split(";") if t.strip()] if base else []
    seen = {_norm(t) for t in out if _norm(t)}
    for t in extra:
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
    if not META_PATH.exists():
        raise FileNotFoundError(f"Missing: {META_PATH}")

    df = pd.read_excel(META_PATH)
    if "related_disease" not in df.columns or "keywords" not in df.columns:
        raise ValueError("Expected columns related_disease and keywords in cleaned metadata.")

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = META_PATH.with_suffix(f".xlsx.bak_{ts}")
    shutil.copy2(str(META_PATH), str(backup))

    changed_cells = 0
    moved_terms_counter: dict[str, int] = {k: 0 for k in MOVE_FROM_DISEASE_TO_KEYWORDS}
    examples = []

    for i, row in df.iterrows():
        dis_in = _split(row.get("related_disease", ""))
        if not dis_in:
            continue
        kept = []
        moved = []
        for t in dis_in:
            if _norm(t) in MOVE_FROM_DISEASE_TO_KEYWORDS:
                moved.append(t)
                moved_terms_counter[_norm(t)] += 1
            else:
                kept.append(t)
        if moved:
            changed_cells += 1
            df.at[i, "related_disease"] = _join(kept)
            df.at[i, "keywords"] = _append_keywords(row.get("keywords", ""), moved)
            if len(examples) < 10:
                examples.append(
                    {
                        "row_index": int(i),
                        "doc_id": str(row.get("doc_id", "")).strip(),
                        "moved_terms": moved,
                    }
                )

    df.to_excel(META_PATH, index=False)
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(
        json.dumps(
            {
                "file": str(META_PATH),
                "backup": str(backup),
                "changed_cells_related_disease": changed_cells,
                "moved_terms_counts": moved_terms_counter,
                "examples": examples,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"[POST-CLEAN] backup: {backup}")
    print(f"[POST-CLEAN] changed_cells_related_disease: {changed_cells}")
    print(f"[POST-CLEAN] report: {REPORT_JSON}")


if __name__ == "__main__":
    main()

