"""
Capture hybrid-search snapshots for priority evaluation queries.
Usage: python capture_weak_queries.py outputs/weak_query_fix_before.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import kg_runtime

import hybrid_search as hs

PRIORITY_QUERIES = [
    "bệnh AHPND trên tôm",
    "bệnh đốm trắng ở tôm thẻ chân trắng",
    "biosecurity trong hatchery tôm thẻ chân trắng",
    "tài liệu về trại giống tôm sú ở Ấn Độ",
    "infectious myonecrosis",
    "nuôi tôm hùm ở Khánh Hòa",
]


def _top_vector(vec: list[dict]) -> dict:
    if not vec:
        return {}
    r = vec[0]
    return {
        "doc_id": r.get("doc_id"),
        "score": float(r.get("score", 0.0)),
        "title": r.get("title"),
        "file_path": r.get("file_path"),
    }


def _top_hybrid(h: list[dict]) -> dict:
    if not h:
        return {}
    r = h[0]
    return {
        "doc_id": r.get("doc_id"),
        "final_score": float(r.get("final_score", 0.0)),
        "vector_score": float(r.get("vector_score", 0.0)),
        "metadata_delta": float(r.get("metadata_delta", r.get("kg_bonus", 0.0))),
        "kg_score": float(r.get("kg_score", 0.0)),
        "doc_uri_in_kg": r.get("doc_uri_in_kg"),
        "profile": r.get("profile"),
        "match_disease": r.get("match_disease"),
        "match_species": r.get("match_species"),
        "match_location": r.get("match_location"),
        "match_mode": r.get("match_mode"),
        "explanation": r.get("explanation"),
        "kg_explanation": r.get("kg_explanation"),
    }


def _entity_lists(detected: dict) -> dict[str, list[str]]:
    return {k: [x.get("canonical", "") for x in (detected.get(k) or [])] for k in detected}


def _kg_labels(kg_entities: dict) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for et in ["disease", "species", "location", "mode"]:
        out[et] = []
        for e in kg_entities.get(et) or []:
            out[et].append(str(e.get("label") or ""))
    return out


def capture_one(
    query: str,
    model,
    index,
    records,
    metadata_lookup: dict,
    term_index: list,
) -> dict:
    hs._init_kg_if_needed()
    detected_raw = hs.detect_entities(query, term_index)
    kg_entities: dict = {"disease": [], "species": [], "location": [], "mode": []}
    if hs._kg_enabled() and hs._KG_INDEX is not None:
        kg_entities = kg_runtime.link_query_entities_kg(query, hs._KG_INDEX)

    merged = hs._merge_detected_with_kg(
        {k: list(v) for k, v in detected_raw.items()},
        kg_entities,
    )
    profile = hs.get_query_profile(merged)

    vec = hs.vector_only_search(query, model, index, records, top_k=hs.FINAL_K)
    _, hybrid = hs.hybrid_search(query, model, index, records, metadata_lookup, term_index)
    h1 = _top_hybrid(hybrid)

    return {
        "query": query,
        "query_profile": profile,
        "detected_entities_raw": _entity_lists(detected_raw),
        "detected_entities_merged": _entity_lists(merged),
        "kg_linked_entities": _kg_labels(kg_entities),
        "top1_metadata_delta": h1.get("metadata_delta"),
        "top1_explanation": h1.get("explanation"),
        "top1_vector": _top_vector(vec),
        "top1_hybrid": h1,
        "ontology_loaded": str(hs._KG_LOADED_OWL_PATH) if hs._KG_LOADED_OWL_PATH else None,
        "metadata_path": hs.METADATA_PATH,
    }


def main() -> None:
    out_path = Path(sys.argv[1] if len(sys.argv) > 1 else "outputs/weak_query_fix_snapshot.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    model, index, records = hs.load_index()
    df = hs.load_full_metadata(hs.METADATA_PATH)
    metadata_lookup = hs.build_metadata_lookup(df)
    term_index = hs.build_term_index(df)

    payload = {
        "queries": [capture_one(q, model, index, records, metadata_lookup, term_index) for q in PRIORITY_QUERIES],
    }
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] Wrote {out_path}")


if __name__ == "__main__":
    main()
