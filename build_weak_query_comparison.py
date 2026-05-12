# -*- coding: utf-8 -*-
import json
from pathlib import Path


def main() -> None:
    before = json.loads(Path("outputs/weak_query_fix_before.json").read_text(encoding="utf-8"))
    after = json.loads(Path("outputs/weak_query_fix_after.json").read_text(encoding="utf-8"))
    bq = {x["query"]: x for x in before["queries"]}
    aq = {x["query"]: x for x in after["queries"]}
    out = []
    for q, b in bq.items():
        a = aq[q]
        hb, ha = b.get("top1_hybrid") or {}, a.get("top1_hybrid") or {}
        vb, va = b.get("top1_vector") or {}, a.get("top1_vector") or {}
        kg_up = float(ha.get("kg_score", 0) or 0) > float(hb.get("kg_score", 0) or 0)
        doc_changed = ha.get("doc_id") != hb.get("doc_id")
        score_close = abs(float(ha.get("final_score", 0) or 0) - float(hb.get("final_score", 0) or 0)) < 1e-4
        if q == "infectious myonecrosis":
            improved = kg_up
            reason = "KG disease node IMN + aboutDisease on IMN docs; KG links query phrase to ontology; kg_score 0 -> positive on top1"
            trade = None
        elif q == "nuôi tôm hùm ở Khánh Hòa":
            improved = kg_up and doc_changed
            reason = "KG scoring: aboutTaxon Tôm hùm bông + isFoundIn Ven biển Khánh Hòa synergy; CANDIDATE_K=20 surfaces FAO_014"
            trade = None
        elif q == "tài liệu về trại giống tôm sú ở Ấn Độ":
            trade = "top1_hybrid doc_id changed FAO_039 -> FAO_002 (higher KG alignment on taxon+location); both India hatchery–related"
            improved = False
            reason = "Trade-off: ranking change from wider candidate rerank + stronger KG on FAO_002"
        else:
            trade = None
            improved = (not doc_changed) and score_close
            reason = "No regression vs baseline (same top1 hybrid and final_score)" if improved else "Unexpected drift vs baseline; inspect"

        out.append(
            {
                "query": q,
                "query_profile_before": b.get("query_profile"),
                "query_profile_after": a.get("query_profile"),
                "detected_entities_merged_before": b.get("detected_entities_merged"),
                "detected_entities_merged_after": a.get("detected_entities_merged"),
                "kg_linked_entities_before": b.get("kg_linked_entities"),
                "kg_linked_entities_after": a.get("kg_linked_entities"),
                "top1_vector_before": vb,
                "top1_vector_after": va,
                "top1_hybrid_before": hb,
                "top1_hybrid_after": ha,
                "metadata_delta_before": hb.get("metadata_delta"),
                "metadata_delta_after": ha.get("metadata_delta"),
                "kg_score_before": hb.get("kg_score"),
                "kg_score_after": ha.get("kg_score"),
                "explanation_before": hb.get("explanation"),
                "explanation_after": ha.get("explanation"),
                "improved": improved,
                "improvement_reason": reason,
                "remaining_issue": (
                    "Top1 FAO_014 is GLOBEFISH lobster market brief (not Khánh Hòa nuôi manual); metadata still no species/location match"
                    if q == "nuôi tôm hùm ở Khánh Hòa"
                    else (
                        "IMN also asserted on SEAFDEC_009 (transboundary list); watch borderline rankings"
                        if q == "infectious myonecrosis"
                        else (
                            trade
                            if q == "tài liệu về trại giống tôm sú ở Ấn Độ"
                            else None
                        )
                    )
                ),
                "trade_off_note": trade,
            }
        )
    Path("outputs/weak_query_fix_comparison.json").write_text(
        json.dumps({"comparisons": out}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print("Wrote outputs/weak_query_fix_comparison.json")


if __name__ == "__main__":
    main()
