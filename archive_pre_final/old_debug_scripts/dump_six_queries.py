# -*- coding: utf-8 -*-
"""One-shot dump of 6 priority queries (single model load)."""
import json
from pathlib import Path

import hybrid_search as hs
import kg_runtime

QUERIES = [
    "bệnh AHPND trên tôm",
    "bệnh đốm trắng ở tôm thẻ chân trắng",
    "biosecurity trong hatchery tôm thẻ chân trắng",
    "tài liệu về trại giống tôm sú ở Ấn Độ",
    "infectious myonecrosis",
    "nuôi tôm hùm ở Khánh Hòa",
]


def main() -> None:
    out = Path("outputs/weak_query_fix_after.json")
    model, index, records = hs.load_index()
    df = hs.load_full_metadata(hs.METADATA_PATH)
    ml = hs.build_metadata_lookup(df)
    ti = hs.build_term_index(df)
    hs._init_kg_if_needed()

    rows = []
    for q in QUERIES:
        raw = hs.detect_entities(q, ti)
        kg = kg_runtime.link_query_entities_kg(q, hs._KG_INDEX) if hs._KG_INDEX else {}
        merged = hs._merge_detected_with_kg({k: list(v) for k, v in raw.items()}, kg)
        profile = hs.get_query_profile(merged)
        vec = hs.vector_only_search(q, model, index, records, top_k=hs.FINAL_K)
        _, hybrid = hs.hybrid_search(q, model, index, records, ml, ti)
        v1 = vec[0] if vec else {}
        h1 = hybrid[0] if hybrid else {}
        rows.append(
            {
                "query": q,
                "query_profile": profile,
                "detected_entities_raw": {k: [x["canonical"] for x in v] for k, v in raw.items()},
                "detected_entities_merged": {k: [x["canonical"] for x in v] for k, v in merged.items()},
                "kg_linked_entities": {
                    et: [str(e.get("label") or "") for e in (kg.get(et) or [])]
                    for et in ["disease", "species", "location", "mode"]
                },
                "top1_metadata_delta": float(h1.get("metadata_delta", h1.get("kg_bonus", 0.0)) or 0.0),
                "top1_explanation": h1.get("explanation"),
                "top1_vector": {
                    "doc_id": v1.get("doc_id"),
                    "score": float(v1.get("score", 0.0)),
                    "title": v1.get("title"),
                    "file_path": v1.get("file_path"),
                },
                "top1_hybrid": {
                    "doc_id": h1.get("doc_id"),
                    "final_score": float(h1.get("final_score", 0.0)),
                    "vector_score": float(h1.get("vector_score", 0.0)),
                    "metadata_delta": float(h1.get("metadata_delta", h1.get("kg_bonus", 0.0)) or 0.0),
                    "kg_score": float(h1.get("kg_score", 0.0) or 0.0),
                    "doc_uri_in_kg": h1.get("doc_uri_in_kg"),
                    "profile": h1.get("profile"),
                    "match_disease": h1.get("match_disease"),
                    "match_species": h1.get("match_species"),
                    "match_location": h1.get("match_location"),
                    "match_mode": h1.get("match_mode"),
                    "explanation": h1.get("explanation"),
                    "kg_explanation": h1.get("kg_explanation"),
                },
            }
        )

    payload = {
        "metadata_path": hs.METADATA_PATH,
        "ontology_loaded": str(hs._KG_LOADED_OWL_PATH) if hs._KG_LOADED_OWL_PATH else None,
        "candidate_k": hs.CANDIDATE_K,
        "queries": rows,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
