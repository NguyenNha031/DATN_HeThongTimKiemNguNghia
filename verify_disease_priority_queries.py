from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import hybrid_search
import kg_runtime
from vector_search import load_index


OUT_DIR = Path("outputs")
OUT_JSON = OUT_DIR / "disease_priority_queries_verification.json"

QUERIES = [
    "bệnh AHPND trên tôm",
    "infectious myonecrosis",
    "shrimp disease",
    "biosecurity trong hatchery tôm thẻ chân trắng",
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

    # Load KG index once for reporting linked disease entities.
    hybrid_search._init_kg_if_needed()
    kg_graph = getattr(hybrid_search, "_KG_GRAPH", None)
    kg_idx = getattr(hybrid_search, "_KG_INDEX", None)

    out: dict[str, Any] = {
        "ontology_loaded": str(getattr(hybrid_search, "_KG_LOADED_OWL_PATH", None)),
        "queries": [],
    }

    for q in QUERIES:
        detected = hybrid_search.detect_entities(q, term_index)
        kg_entities = {"disease": [], "species": [], "location": [], "mode": []}
        if kg_graph is not None and kg_idx is not None:
            try:
                kg_entities = kg_runtime.link_query_entities_kg(q, kg_idx)
            except Exception:
                kg_entities = {"disease": [], "species": [], "location": [], "mode": []}

        merged = hybrid_search._merge_detected_with_kg(detected, kg_entities)
        profile = hybrid_search.get_query_profile(merged)

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
                    "doc_uri_in_kg": r.get("doc_uri_in_kg"),
                    "profile": r.get("profile"),
                    "match_disease": r.get("match_disease"),
                    "match_species": r.get("match_species"),
                    "explanation": r.get("explanation"),
                    "kg_explanation": r.get("kg_explanation"),
                    "kg_penalty_breakdown": r.get("kg_penalty_breakdown"),
                }
            )

        out["queries"].append(
            {
                "query": q,
                "query_profile": profile,
                "detected_metadata_disease": [m.get("canonical") for m in (detected.get("disease") or [])],
                "detected_kg_disease": [e.get("label") for e in (kg_entities.get("disease") or [])],
                "top3": top3,
            }
        )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[VERIFY] Saved: {OUT_JSON}")


if __name__ == "__main__":
    main()

