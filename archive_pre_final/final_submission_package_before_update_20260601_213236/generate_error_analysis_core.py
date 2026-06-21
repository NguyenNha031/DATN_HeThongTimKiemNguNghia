from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

import pandas as pd


OUT_CSV = Path("outputs") / "error_analysis_core.csv"
OUT_JSON = Path("outputs") / "error_analysis_summary.json"

FIELDS = [
    "query_id",
    "query_text",
    "query_group",
    "expected_behavior",
    "observed_behavior",
    "top1_doc_id",
    "top1_title",
    "relevant_doc_examples",
    "error_type",
    "reason",
    "suggested_fix",
    "evidence_source",
]


CASES = [
    {
        "query_id": "LO_005",
        "expected_behavior": "Ưu tiên FAO_038 về risk management practices of small intensive shrimp farmers in the Mekong Delta.",
        "error_type": "missing_location_fact",
        "reason": "Hybrid xếp FAO_038 ở rank 7; KG fact của FAO_038 chỉ có Vietnam, trong khi metadata có Mekong Delta/Bac Lieu/Ben Tre/Ca Mau. Tín hiệu địa phương hẹp không đủ mạnh.",
        "suggested_fix": "Bổ sung/chuẩn hóa entity location Mekong Delta và các tỉnh liên quan trong KG facts; thêm alias tiếng Việt cho Đồng bằng sông Cửu Long.",
        "evidence_source": "baseline_hybrid_core.csv; relevance_judgments_core.csv; document_metadata_cleaned.xlsx; kg_runtime document facts",
    },
    {
        "query_id": "DS_007",
        "expected_behavior": "Ưu tiên tài liệu Vibrio parahaemolyticus/AHPND trên Penaeus vannamei như PMC_007, PMC_029, SEAFDEC_010.",
        "error_type": "missing_disease_fact",
        "reason": "Query pathogen-centered; hybrid top1 là TCTS_001 (WSSV/general shrimp disease). Pathogen Vibrio parahaemolyticus không được dùng trong metadata_delta, nên các tài liệu AHPND/Vibrio chỉ lên rank 6-9.",
        "suggested_fix": "Mở rộng scoring metadata/KG cho pathogen-centered intent hoặc bridge Vibrio parahaemolyticus -> AHPND/vibriosis trong reranking.",
        "evidence_source": "baseline_hybrid_core.csv; relevance_judgments_core.csv; kg_runtime causedBy facts",
    },
    {
        "query_id": "DS_006",
        "expected_behavior": "Ưu tiên tài liệu EHP/HPM trọng tâm như TB_005, SEAFDEC_001 hoặc PMC_001.",
        "error_type": "not_error_but_baseline_limitation",
        "reason": "Top1 PMC_003 nói trực tiếp về EHP nhưng không nằm trong relevance judgments; metric coi unjudged là 0. Đây là hạn chế của judgment pool hơn là lỗi retrieval rõ ràng.",
        "suggested_fix": "Rà soát mở rộng judgment pool cho các tài liệu EHP trực tiếp như PMC_003 nếu muốn đánh giá đầy đủ hơn.",
        "evidence_source": "baseline_hybrid_core.csv; baseline_metrics_per_query.csv; relevance_judgments_core.csv",
    },
    {
        "query_id": "SL_001",
        "expected_behavior": "Ưu tiên tài liệu Bangladesh shrimp/hatchery như FAO_039, FAO_040, FAO_011.",
        "error_type": "scoring_or_intent_issue",
        "reason": "Hybrid top1 là FAO_006 về AHPND workshop ở Thailand; location Bangladesh và production/hatchery intent không thắng được tín hiệu disease/taxon rộng.",
        "suggested_fix": "Thêm intent/location guardrail cho species-location queries có country cụ thể, hoặc tăng penalty cho document sai quốc gia khi có country match trong pool.",
        "evidence_source": "baseline_hybrid_core.csv; baseline_vector_core.csv; relevance_judgments_core.csv",
    },
    {
        "query_id": "BI_007",
        "expected_behavior": "Ưu tiên tài liệu emergency preparedness/response như FAO_034.",
        "error_type": "missing_alias",
        "reason": "Hybrid top1 là FAO_004 generic biosecurity pathway; FAO_034 đứng rank 2. Các cụm 'ứng phó khẩn cấp', 'emergency response', 'EPR' chưa có intent/alias đủ rõ để đẩy FAO_034 lên đầu.",
        "suggested_fix": "Bổ sung alias/topic cho emergency preparedness, emergency response, EPR và liên kết với tài liệu FAO_034.",
        "evidence_source": "baseline_hybrid_core.csv; document_metadata_cleaned.xlsx; relevance_judgments_core.csv",
    },
    {
        "query_id": "HM_001",
        "expected_behavior": "Top1 FAO_005 đúng; top-5 nên giữ thêm tài liệu hatchery vannamei như PMC_026/PMC_030/PMC_036.",
        "error_type": "weak_candidate_pool",
        "reason": "Hybrid lấy đúng top1 nhưng P@5 thấp; nhiều tài liệu hatchery vannamei rel=2 không xuất hiện top5. Candidate/rerank còn bị hút bởi AHPND/shrimp aquaculture rộng.",
        "suggested_fix": "Tăng recall candidate cho hatchery-larvae/post-larvae terms hoặc thêm field-aware matching cho hatchery stage.",
        "evidence_source": "baseline_hybrid_core.csv; relevance_judgments_core.csv; document_metadata_cleaned.xlsx",
    },
    {
        "query_id": "LO_001",
        "expected_behavior": "Ngoài RIA3_001, nên đưa RIA3_002/RIA3_003 lên cao cho truy vấn tôm hùm Khánh Hòa.",
        "error_type": "weak_candidate_pool",
        "reason": "Hybrid top1 đúng nhưng RIA3_002/RIA3_003 không xuất hiện top10 hybrid; ontology_sparql xếp chúng top2/top3. Hai doc này có KG facts nhưng không có trong vector_store chunks_meta hiện tại.",
        "suggested_fix": "Rebuild vector store sau khi metadata/corpus đã đủ 110 docs; xác minh RIA3_002/RIA3_003 được index.",
        "evidence_source": "baseline_hybrid_core.csv; baseline_ontology_sparql_core.csv; vector_store/chunks_meta.pkl; kg_runtime facts",
    },
    {
        "query_id": "SL_004",
        "expected_behavior": "Ưu tiên FAO_008 về low water exchange shrimp farming in Thailand.",
        "error_type": "not_error_but_baseline_limitation",
        "reason": "Hybrid đã đúng top1 nhờ intent guardrail; ontology_sparql chỉ đưa FAO_008 rank 8 vì KG không mô hình hóa practice 'low water exchange' như structured relation.",
        "suggested_fix": "Nếu cần KG tự trả lời practice-level query, thêm concept/practice relation cho low-water-exchange thay vì chỉ dựa vào title/intent heuristic.",
        "evidence_source": "baseline_hybrid_core.csv; baseline_ontology_sparql_core.csv; hybrid_search intent adjustment",
    },
    {
        "query_id": "LO_003",
        "expected_behavior": "Ưu tiên tài liệu địa phương Thạch Hà/Cẩm Xuyên/Nghi Xuân và các bệnh môi trường liên quan.",
        "error_type": "missing_location_fact",
        "reason": "Hybrid top1 đúng TCKHTS_001 nhưng KG facts của document này không có aboutLocation, nên structured KG không hỗ trợ tốt truy vấn địa phương chi tiết.",
        "suggested_fix": "Backfill/chuẩn hóa location entities cho Hà Tĩnh, Thạch Hà, Cẩm Xuyên, Nghi Xuân nếu muốn tăng KG support cho local queries.",
        "evidence_source": "baseline_hybrid_core.csv; kg_runtime document facts; document_metadata_cleaned.xlsx",
    },
    {
        "query_id": "HM_010",
        "expected_behavior": "Ưu tiên nhóm hatchery larvae/post-larvae Penaeus vannamei như PMC_036, PMC_030, PMC_031, PMC_032, PMC_009.",
        "error_type": "metadata_incomplete",
        "reason": "Hybrid top1 đúng nhưng một số tài liệu rel=2 nằm thấp hơn top5; ontology_sparql gần như trả các tài liệu generic đầu corpus vì stage terms broodstock/larvae/post-larvae chưa được mô hình hóa nhất quán.",
        "suggested_fix": "Chuẩn hóa metadata/KG cho life-stage terms (broodstock, larvae, post-larvae) và thêm aliases liên quan hatchery tank survival.",
        "evidence_source": "baseline_hybrid_core.csv; baseline_ontology_sparql_core.csv; relevance_judgments_core.csv; document_metadata_cleaned.xlsx",
    },
]


def _relevant_examples(jud: pd.DataFrame, qid: str) -> str:
    rows = jud[(jud["query_id"] == qid) & (jud["relevance_label"] > 0)].copy()
    rows = rows.sort_values(["relevance_label", "doc_id"], ascending=[False, True])
    return "; ".join(f"{r.doc_id}({int(r.relevance_label)})" for _, r in rows.head(6).iterrows())


def main() -> None:
    queries = pd.read_csv("data/eval/final_query_set_core.csv", encoding="utf-8-sig")
    judgments = pd.read_csv("data/eval/relevance_judgments_core.csv", encoding="utf-8-sig")
    hybrid = pd.read_csv("data/eval/results/baseline_hybrid_core.csv", encoding="utf-8-sig")

    rows = []
    for case in CASES:
        qid = case["query_id"]
        qrow = queries[queries["query_id"] == qid].iloc[0]
        top = hybrid[hybrid["query_id"] == qid].sort_values("rank").iloc[0]
        ranked = hybrid[hybrid["query_id"] == qid].sort_values("rank")
        relevant_set = set(judgments[(judgments["query_id"] == qid) & (judgments["relevance_label"] > 0)]["doc_id"])
        rel_in_top10 = [r.doc_id for _, r in ranked.iterrows() if r.doc_id in relevant_set]
        observed = (
            f"Hybrid top1={top.doc_id}; relevant docs in hybrid top10="
            f"{';'.join(rel_in_top10) if rel_in_top10 else 'none'}."
        )
        rows.append(
            {
                "query_id": qid,
                "query_text": qrow["query_text"],
                "query_group": qrow["query_group"],
                "expected_behavior": case["expected_behavior"],
                "observed_behavior": observed,
                "top1_doc_id": top.doc_id,
                "top1_title": top.title,
                "relevant_doc_examples": _relevant_examples(judgments, qid),
                "error_type": case["error_type"],
                "reason": case["reason"],
                "suggested_fix": case["suggested_fix"],
                "evidence_source": case["evidence_source"],
            }
        )

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_CSV, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    counts = Counter(r["error_type"] for r in rows)
    summary = {
        "total_cases": len(rows),
        "count_by_error_type": dict(sorted(counts.items())),
        "notes": [
            "Curated retrieval error-analysis cases for thesis discussion.",
            "Cases are selected from existing core-query results and do not modify retrieval outputs.",
            "Some rows are classified as not_error_but_baseline_limitation where the metric/judgment setup or baseline scope explains the behavior.",
        ],
    }
    OUT_JSON.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] Wrote {OUT_CSV} and {OUT_JSON}")


if __name__ == "__main__":
    main()
