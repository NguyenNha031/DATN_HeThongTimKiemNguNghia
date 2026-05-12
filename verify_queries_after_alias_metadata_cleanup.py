from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import hybrid_search
import kg_runtime
from vector_search import load_index


OUT_DIR = Path("outputs")
OUT_JSON = OUT_DIR / "alias_metadata_cleanup_query_verification.json"

QUERIES = [
    "bệnh AHPND trên tôm",
    "infectious myonecrosis",
    "shrimp disease",
    "biosecurity trong hatchery tôm thẻ chân trắng",
    "nuôi tôm hùm ở Khánh Hòa",
    "tài liệu về trại giống tôm sú ở Ấn Độ",
]


def _utf8() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stdin.reconfigure(encoding="utf-8")
    except Exception:
        pass


def main() -> None:
    _utf8()
    model, index, records = load_index()
    df = hybrid_search.load_full_metadata(hybrid_search.METADATA_PATH)
    metadata_lookup = hybrid_search.build_metadata_lookup(df)
    term_index = hybrid_search.build_term_index(df)

    hybrid_search._init_kg_if_needed()
    kg_graph = getattr(hybrid_search, "_KG_GRAPH", None)
    kg_idx = getattr(hybrid_search, "_KG_INDEX", None)

    out: dict[str, Any] = {
        "metadata_path_used": hybrid_search.METADATA_PATH,
        "ontology_loaded": str(getattr(hybrid_search, "_KG_LOADED_OWL_PATH", None)),
        "queries": [],
    }

    for q in QUERIES:
        detected_raw = hybrid_search.detect_entities(q, term_index)
        kg_entities = {"disease": [], "species": [], "location": [], "mode": []}
        if kg_graph is not None and kg_idx is not None:
            try:
                kg_entities = kg_runtime.link_query_entities_kg(q, kg_idx)
            except Exception:
                kg_entities = {"disease": [], "species": [], "location": [], "mode": []}

        detected = hybrid_search._merge_detected_with_kg(detected_raw, kg_entities)
        profile = hybrid_search.get_query_profile(detected)

        _, results = hybrid_search.hybrid_search(
            query=q,
            model=model,
            index=index,
            records=records,
            metadata_lookup=metadata_lookup,
            term_index=term_index,
        )

        top3 = []
        for r in results[:3]:
            top3.append(
                {
                    "doc_id": r.get("doc_id"),
                    "final_score": r.get("final_score"),
                    "vector_score": r.get("vector_score"),
                    "metadata_delta": r.get("metadata_delta"),
                    "kg_score": r.get("kg_score"),
                    "profile": r.get("profile"),
                    "match_disease": r.get("match_disease"),
                    "match_species": r.get("match_species"),
                    "match_location": r.get("match_location"),
                    "match_mode": r.get("match_mode"),
                    "penalty_breakdown": r.get("penalty_breakdown"),
                    "kg_penalty_breakdown": r.get("kg_penalty_breakdown"),
                    "explanation": r.get("explanation"),
                    "kg_explanation": r.get("kg_explanation"),
                }
            )

        out["queries"].append(
            {
                "query": q,
                "query_profile": profile,
                "detected_entities_raw": {
                    k: [m.get("canonical") for m in (detected_raw.get(k) or [])] for k in ["disease", "species", "location", "mode"]
                },
                "detected_entities_merged": {
                    k: [m.get("canonical") for m in (detected.get(k) or [])] for k in ["disease", "species", "location", "mode"]
                },
                "kg_linked_entities": {
                    k: [e.get("label") for e in (kg_entities.get(k) or [])] for k in ["disease", "species", "location", "mode"]
                },
                "top3": top3,
            }
        )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[VERIFY] Saved: {OUT_JSON}")


if __name__ == "__main__":
    main()

