from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import hybrid_search
import kg_runtime
from vector_search import load_index


OUT_DIR = Path("outputs")
OUT_JSON = OUT_DIR / "full_corpus_query_verification.json"


QUERIES = [
    "bệnh AHPND trên tôm",
    "bệnh đốm trắng ở tôm thẻ chân trắng",
    "infectious myonecrosis",
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


def _canon_list(detected: dict[str, Any], key: str) -> list[str]:
    out = []
    for m in (detected.get(key) or []):
        c = m.get("canonical")
        if c:
            out.append(c)
    return out


def _label_list(kg_entities: dict[str, Any], key: str) -> list[str]:
    out = []
    for e in (kg_entities.get(key) or []):
        lbl = e.get("label")
        if lbl:
            out.append(lbl)
    return out


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

        vector_candidates = hybrid_search.vector_only_search(q, model=model, index=index, records=records, top_k=5)

        _, hybrid_results = hybrid_search.hybrid_search(
            query=q,
            model=model,
            index=index,
            records=records,
            metadata_lookup=metadata_lookup,
            term_index=term_index,
        )

        top1_vector = None
        if vector_candidates:
            r = vector_candidates[0]
            top1_vector = {
                "doc_id": r.get("doc_id"),
                "score": r.get("score"),
                "title": r.get("title"),
                "file_path": r.get("file_path"),
            }

        top1_hybrid = None
        if hybrid_results:
            r = hybrid_results[0]
            top1_hybrid = {
                "doc_id": r.get("doc_id"),
                "final_score": r.get("final_score"),
                "vector_score": r.get("vector_score"),
                "metadata_delta": r.get("metadata_delta"),
                "kg_score": r.get("kg_score"),
                "doc_uri_in_kg": r.get("doc_uri_in_kg"),
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

        out["queries"].append(
            {
                "query": q,
                "query_profile": profile,
                "detected_entities_raw": {k: _canon_list(detected_raw, k) for k in ["disease", "species", "location", "mode"]},
                "detected_entities_merged": {k: _canon_list(detected, k) for k in ["disease", "species", "location", "mode"]},
                "kg_linked_entities": {k: _label_list(kg_entities, k) for k in ["disease", "species", "location", "mode"]},
                "top1_vector": top1_vector,
                "top1_hybrid": top1_hybrid,
                "verdict": (
                    "unknown"
                    if top1_hybrid is None
                    else ("good" if (top1_hybrid.get("metadata_delta", 0) or 0) > 0 or (top1_hybrid.get("kg_score", 0) or 0) > 0 else "needs_review")
                ),
            }
        )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[VERIFY] Saved: {OUT_JSON}")


if __name__ == "__main__":
    main()

