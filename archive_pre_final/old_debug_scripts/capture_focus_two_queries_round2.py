"""
Round-2 snapshot for the required before/after artifacts.

Usage:
  python capture_focus_two_queries_round2.py outputs/focus_two_queries_round2_before.json
  python capture_focus_two_queries_round2.py outputs/focus_two_queries_round2_after.json

Notes:
- Keeps the same fixed query set used in prior evaluation.
- Writes a single JSON file with top1 vector + top1 hybrid metrics per query.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from vector_search import load_index

import hybrid_search as h


QUERIES = [
    "bệnh AHPND trên tôm",
    "bệnh đốm trắng ở tôm thẻ chân trắng",
    "biosecurity trong hatchery tôm thẻ chân trắng",
    "tài liệu về trại giống tôm sú ở Ấn Độ",
    "infectious myonecrosis",
    "nuôi tôm hùm ở Khánh Hòa",
]


def _top1_vector(model, index, records, query: str) -> dict:
    r = h.vector_only_search(query, model, index, records, top_k=1)
    if not r:
        return {}
    x = r[0]
    return {
        "doc_id": x.get("doc_id"),
        "score": round(float(x.get("score", 0.0)), 4),
        "title": (x.get("title") or "")[:120],
    }


def _top1_hybrid(hy: list[dict]) -> dict:
    if not hy:
        return {}
    x = hy[0]
    return {
        "doc_id": x.get("doc_id"),
        "vector_score": round(float(x.get("vector_score", 0.0)), 4),
        "metadata_delta": round(float(x.get("metadata_delta", 0.0)), 4),
        "kg_score": round(float(x.get("kg_score", 0.0)), 4),
        "final_score": round(float(x.get("final_score", 0.0)), 4),
        "title": (x.get("title") or "")[:120],
    }


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    out_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("outputs") / "focus_two_queries_round2_before.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    model, index, records = load_index()
    df = h.load_full_metadata(h.METADATA_PATH)
    meta = h.build_metadata_lookup(df)
    ti = h.build_term_index(df)
    h._init_kg_if_needed()

    rows = []
    for query in QUERIES:
        v1 = _top1_vector(model, index, records, query)
        detected, hy = h.hybrid_search(query, model, index, records, meta, ti)
        h1 = _top1_hybrid(hy)
        rows.append(
            {
                "query": query,
                "detected": {k: [m["canonical"] for m in v] for k, v in detected.items()},
                "profile": h.get_query_profile(detected),
                "top1_vector": v1,
                "top1_hybrid": h1,
            }
        )

    out_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] wrote {out_path}")


if __name__ == "__main__":
    main()

