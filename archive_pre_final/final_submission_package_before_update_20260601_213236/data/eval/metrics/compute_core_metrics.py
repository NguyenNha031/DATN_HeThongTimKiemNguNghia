"""
Bước 4: tính metric trên core query set — chỉ đọc CSV, không sửa nguồn.
Chạy từ thư mục project: python data/eval/metrics/compute_core_metrics.py
"""
from __future__ import annotations

import csv
import math
import statistics
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]

CORE_QUERIES = PROJECT_ROOT / "data" / "eval" / "final_query_set_core.csv"
JUDGMENTS = PROJECT_ROOT / "data" / "eval" / "relevance_judgments_core.csv"
RESULTS_DIR = PROJECT_ROOT / "data" / "eval" / "results"
METRICS_DIR = PROJECT_ROOT / "data" / "eval" / "metrics"

BASELINE_FILES = {
    "lexical": RESULTS_DIR / "baseline_lexical_core.csv",
    "vector": RESULTS_DIR / "baseline_vector_core.csv",
    "vector_metadata": RESULTS_DIR / "baseline_vector_metadata_core.csv",
    "vector_metadata_kg_no_intent": RESULTS_DIR / "baseline_vector_metadata_kg_no_intent_core.csv",
    "ontology_sparql": RESULTS_DIR / "baseline_ontology_sparql_core.csv",
    "hybrid": RESULTS_DIR / "baseline_hybrid_core.csv",
}


def gain(rel: int) -> float:
    """Gain cho nDCG; graded 0,1,2 -> (2^rel - 1)."""
    rel = int(rel)
    if rel < 0:
        return 0.0
    return float((2**rel) - 1)


def dcg_from_grades(grades: list[int], k: int) -> float:
    """grades[i] là relevance tại rank i+1; chỉ dùng tối đa k vị trí."""
    s = 0.0
    for i in range(k):
        g = int(grades[i]) if i < len(grades) else 0
        s += gain(g) / math.log2(i + 2)
    return s


def ndcg_at_k(retrieved_grades: list[int], ideal_sorted_grades: list[int], k: int) -> float:
    """
    retrieved_grades: độ dài ≥ k (pad 0); ideal_sorted_grades: toàn bộ nhãn judgment của query,
    đã sort giảm dần; IDCG lấy top k của ideal.
    """
    rel_k = (retrieved_grades + [0] * k)[:k]
    dcg = dcg_from_grades(rel_k, k)
    ideal_top = (ideal_sorted_grades + [0] * k)[:k]
    idcg = dcg_from_grades(ideal_top, k)
    if idcg <= 0.0:
        return 1.0 if dcg <= 0.0 else 0.0
    return dcg / idcg


def precision_at_k(binary_flags: list[bool], k: int) -> float:
    """binary_flags[i] = relevant (>0) tại rank i+1."""
    if k <= 0:
        return 0.0
    top = binary_flags[:k]
    if len(top) < k:
        hits = sum(top)
        return hits / float(k)
    return sum(top) / float(k)


def recall_at_5(binary_flags: list[bool], total_relevant_in_pool: int) -> float:
    """
    Recall@5 = (# relevant trong top-5 retrieval) / R, với R = số doc có nhãn >0 trong judgment pool.
    Nếu R = 0: **không định nghĩa** (trả math.nan) — không coi là 1.0.
    """
    if total_relevant_in_pool <= 0:
        return math.nan
    hits_top5 = sum(binary_flags[:5])
    return hits_top5 / float(total_relevant_in_pool)


def reciprocal_rank(binary_flags: list[bool]) -> float:
    for i, ok in enumerate(binary_flags):
        if ok:
            return 1.0 / float(i + 1)
    return 0.0


def load_core_queries() -> dict[str, dict]:
    out = {}
    with open(CORE_QUERIES, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            qid = str(r["query_id"]).strip()
            out[qid] = {
                "query_text": str(r.get("query_text", "")),
                "query_group": str(r.get("query_group", "")),
            }
    return out


def load_judgments() -> tuple[dict[tuple[str, str], int], dict[str, list[int]]]:
    """(query_id, doc_id) -> relevance_label; query_id -> list of all labels for that query."""
    jud = {}
    by_q: dict[str, list[int]] = defaultdict(list)
    with open(JUDGMENTS, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            qid = str(r["query_id"]).strip()
            did = str(r["doc_id"]).strip()
            lab = int(float(r["relevance_label"]))
            jud[(qid, did)] = lab
            by_q[qid].append(lab)
    return jud, dict(by_q)


def load_retrieval_ranking(path: Path) -> dict[str, list[str]]:
    """query_id -> doc_id list sorted by rank ascending."""
    rows_by_q: dict[str, list[tuple[int, str]]] = defaultdict(list)
    with open(path, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            qid = str(r["query_id"]).strip()
            rid = int(float(r["rank"]))
            did = str(r["doc_id"]).strip()
            rows_by_q[qid].append((rid, did))
    out: dict[str, list[str]] = {}
    for qid, pairs in rows_by_q.items():
        pairs.sort(key=lambda x: x[0])
        out[qid] = [d for _, d in pairs]
    return out


def compute_one_query(
    qid: str,
    ranked_docs: list[str],
    jud_map: dict[tuple[str, str], int],
    labels_for_query: list[int],
) -> dict:
    """Unjudged doc trong ranking coi relevance = 0."""
    grades = []
    for d in ranked_docs:
        grades.append(jud_map.get((qid, d), 0))
    binary = [g > 0 for g in grades]

    total_rel = sum(1 for lab in labels_for_query if lab > 0)

    ideal_sorted = sorted(labels_for_query, reverse=True)

    max_len = max(10, len(ranked_docs))
    grades_pad = grades + [0] * max_len

    return {
        "p_at_1": precision_at_k(binary, 1),
        "p_at_3": precision_at_k(binary, 3),
        "p_at_5": precision_at_k(binary, 5),
        "recall_at_5": recall_at_5(binary, total_rel),
        "rr": reciprocal_rank(binary),
        "ndcg_at_5": ndcg_at_k(grades_pad, ideal_sorted, 5),
        "ndcg_at_10": ndcg_at_k(grades_pad, ideal_sorted, 10),
        "num_retrieved": len(ranked_docs),
        "num_judged_hits": sum(1 for d in ranked_docs if (qid, d) in jud_map),
        "total_relevant_pool": total_rel,
    }


def _fmt_recall(v: float) -> str:
    if isinstance(v, float) and math.isnan(v):
        return "NaN"
    return str(round(v, 6))


def _mean_skip_nan(values: list[float]) -> float:
    xs = [v for v in values if not (isinstance(v, float) and math.isnan(v))]
    if not xs:
        return math.nan
    return statistics.mean(xs)


def main() -> None:
    METRICS_DIR.mkdir(parents=True, exist_ok=True)

    core = load_core_queries()
    jud_map, labels_by_q = load_judgments()

    core_ids = list(core.keys())
    assert len(core_ids) == 28, f"expected 28 core queries, got {len(core_ids)}"

    # Kiểm tra mọi core query có trong judgments
    missing_j = [q for q in core_ids if q not in labels_by_q]
    if missing_j:
        raise SystemExit(f"Core queries missing from judgments: {missing_j}")

    r_zero = [
        q
        for q in core_ids
        if sum(1 for lab in labels_by_q[q] if lab > 0) == 0
    ]
    if r_zero:
        print(f"[WARN] Core queries with R=0 (no rel>0 in judgment pool): {r_zero}")
    else:
        print("[INFO] No core query has R=0; all have at least one judged relevant doc.")

    per_query_rows: list[dict] = []
    summary_rows: list[dict] = []
    by_group_accum: dict[tuple[str, str], list[dict]] = defaultdict(list)

    for baseline_key, path in BASELINE_FILES.items():
        if not path.exists():
            raise FileNotFoundError(path)
        rankings = load_retrieval_ranking(path)

        pq_metrics: list[dict] = []
        for qid in core_ids:
            ranked = rankings.get(qid, [])
            if not ranked:
                raise RuntimeError(f"{baseline_key}: empty ranking for {qid}")

            m = compute_one_query(qid, ranked, jud_map, labels_by_q[qid])
            pq_metrics.append(m)

            notes_parts: list[str] = []
            if m["num_judged_hits"] < len(ranked):
                notes_parts.append(
                    f"unjudged_in_ranking={len(ranked) - m['num_judged_hits']} treated as rel=0"
                )
            if m["total_relevant_pool"] <= 0:
                notes_parts.append("recall_at_5=NaN (judgment pool has R=0 relevant); excluded from macro Recall@5")

            per_query_rows.append(
                {
                    "baseline_name": baseline_key,
                    "query_id": qid,
                    "query_text": core[qid]["query_text"],
                    "query_group": core[qid]["query_group"],
                    "p_at_1": round(m["p_at_1"], 6),
                    "p_at_3": round(m["p_at_3"], 6),
                    "p_at_5": round(m["p_at_5"], 6),
                    "recall_at_5": _fmt_recall(m["recall_at_5"]),
                    "rr": round(m["rr"], 6),
                    "ndcg_at_5": round(m["ndcg_at_5"], 6),
                    "ndcg_at_10": round(m["ndcg_at_10"], 6),
                    "num_retrieved": m["num_retrieved"],
                    "num_judged_hits": m["num_judged_hits"],
                    "notes": "; ".join(notes_parts),
                }
            )

            by_group_accum[(baseline_key, core[qid]["query_group"])].append(m)

        n = len(pq_metrics)
        recall_vals = [x["recall_at_5"] for x in pq_metrics]
        recall_mean = _mean_skip_nan(recall_vals)
        n_skip_r0 = sum(1 for v in recall_vals if isinstance(v, float) and math.isnan(v))
        n_recall = len(recall_vals) - n_skip_r0
        sum_notes = (
            f"Recall@5 macro trên {n_recall}/{n} query (loại R=0: {n_skip_r0}). "
            "latency không có trong CSV baseline bước 3; để trống"
        )
        summary_rows.append(
            {
                "baseline_name": baseline_key,
                "num_queries": n,
                "p_at_1": round(statistics.mean(x["p_at_1"] for x in pq_metrics), 6),
                "p_at_3": round(statistics.mean(x["p_at_3"] for x in pq_metrics), 6),
                "p_at_5": round(statistics.mean(x["p_at_5"] for x in pq_metrics), 6),
                "recall_at_5": _fmt_recall(recall_mean),
                "mrr": round(statistics.mean(x["rr"] for x in pq_metrics), 6),
                "ndcg_at_5": round(statistics.mean(x["ndcg_at_5"] for x in pq_metrics), 6),
                "ndcg_at_10": round(statistics.mean(x["ndcg_at_10"] for x in pq_metrics), 6),
                "mean_query_latency_ms": "",
                "notes": sum_notes,
            }
        )

    # by group
    by_group_rows: list[dict] = []
    for (baseline_name, qgroup), mlist in sorted(by_group_accum.items()):
        recall_g = _mean_skip_nan([x["recall_at_5"] for x in mlist])
        by_group_rows.append(
            {
                "baseline_name": baseline_name,
                "query_group": qgroup,
                "num_queries": len(mlist),
                "p_at_1": round(statistics.mean(x["p_at_1"] for x in mlist), 6),
                "p_at_3": round(statistics.mean(x["p_at_3"] for x in mlist), 6),
                "p_at_5": round(statistics.mean(x["p_at_5"] for x in mlist), 6),
                "recall_at_5": _fmt_recall(recall_g),
                "mrr": round(statistics.mean(x["rr"] for x in mlist), 6),
                "ndcg_at_5": round(statistics.mean(x["ndcg_at_5"] for x in mlist), 6),
                "ndcg_at_10": round(statistics.mean(x["ndcg_at_10"] for x in mlist), 6),
            }
        )

    # Write CSVs
    sum_path = METRICS_DIR / "baseline_metrics_summary.csv"
    with open(sum_path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "baseline_name",
                "num_queries",
                "p_at_1",
                "p_at_3",
                "p_at_5",
                "recall_at_5",
                "mrr",
                "ndcg_at_5",
                "ndcg_at_10",
                "mean_query_latency_ms",
                "notes",
            ],
        )
        w.writeheader()
        w.writerows(summary_rows)

    pq_path = METRICS_DIR / "baseline_metrics_per_query.csv"
    with open(pq_path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "baseline_name",
                "query_id",
                "query_text",
                "query_group",
                "p_at_1",
                "p_at_3",
                "p_at_5",
                "recall_at_5",
                "rr",
                "ndcg_at_5",
                "ndcg_at_10",
                "num_retrieved",
                "num_judged_hits",
                "notes",
            ],
        )
        w.writeheader()
        w.writerows(per_query_rows)

    bg_path = METRICS_DIR / "baseline_metrics_by_group.csv"
    with open(bg_path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "baseline_name",
                "query_group",
                "num_queries",
                "p_at_1",
                "p_at_3",
                "p_at_5",
                "recall_at_5",
                "mrr",
                "ndcg_at_5",
                "ndcg_at_10",
            ],
        )
        w.writeheader()
        w.writerows(by_group_rows)

    # Latency is measured by measure_core_baseline_latency.py; keep existing latency CSV intact.
    print(f"[OK] Wrote {sum_path.name}, {pq_path.name}, {bg_path.name}")
    return

    lat_path = METRICS_DIR / "baseline_latency_summary.csv"
    with open(lat_path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["baseline_name", "mean_query_latency_ms", "notes"],
        )
        w.writeheader()
        for b in BASELINE_FILES:
            w.writerow(
                {
                    "baseline_name": b,
                    "mean_query_latency_ms": "",
                    "notes": "Không đo trong bước 3; cần instrumentation retrieval riêng",
                }
            )

    print(f"[OK] Wrote {sum_path.name}, {pq_path.name}, {bg_path.name}, {lat_path.name}")


if __name__ == "__main__":
    main()
