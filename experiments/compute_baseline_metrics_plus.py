from __future__ import annotations

import csv
import math
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
QUERY_SET = PROJECT_ROOT / "data" / "eval" / "final_query_set_core.csv"
JUDGMENTS = PROJECT_ROOT / "data" / "eval" / "relevance_judgments_core.csv"
RESULTS_DIR = PROJECT_ROOT / "data" / "eval" / "results"
METRICS_DIR = PROJECT_ROOT / "data" / "eval" / "metrics"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

RESULT_FILES = {
    "lexical": RESULTS_DIR / "baseline_lexical_core.csv",
    "vector": RESULTS_DIR / "baseline_vector_core.csv",
    "vector_metadata": RESULTS_DIR / "baseline_vector_metadata_core.csv",
    "ontology_sparql": RESULTS_DIR / "baseline_ontology_sparql_core.csv",
    "hybrid": RESULTS_DIR / "baseline_hybrid_core.csv",
}
CANDIDATE_FUSION_RESULT = RESULTS_DIR / "baseline_hybrid_candidate_fusion_core.csv"

SUMMARY_OUT = METRICS_DIR / "baseline_metrics_summary_plus.csv"
BY_QUERY_OUT = METRICS_DIR / "baseline_metrics_by_query_plus.csv"
BY_GROUP_OUT = METRICS_DIR / "baseline_metrics_by_group_plus.csv"
REPORT_OUT = OUTPUTS_DIR / "baseline_metrics_plus_report.md"

METRIC_FIELDS = [
    "baseline_name",
    "num_queries",
    "p_at_1",
    "p_at_3",
    "p_at_5",
    "recall_at_5",
    "recall_at_10",
    "mrr",
    "ndcg_at_5",
    "ndcg_at_10",
    "map",
]
BY_QUERY_FIELDS = [
    "baseline_name",
    "query_id",
    "query_text",
    "query_group",
    "p_at_1",
    "p_at_3",
    "p_at_5",
    "recall_at_5",
    "recall_at_10",
    "mrr",
    "ndcg_at_5",
    "ndcg_at_10",
    "map",
]
BY_GROUP_FIELDS = [
    "baseline_name",
    "query_group",
    "num_queries",
    "p_at_1",
    "p_at_3",
    "p_at_5",
    "recall_at_5",
    "recall_at_10",
    "mrr",
    "ndcg_at_5",
    "ndcg_at_10",
    "map",
]


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def load_queries() -> list[dict[str, str]]:
    return read_csv_rows(QUERY_SET)


def load_judgments() -> tuple[dict[tuple[str, str], int], dict[str, list[int]]]:
    labels: dict[tuple[str, str], int] = {}
    labels_by_query: dict[str, list[int]] = defaultdict(list)
    for row in read_csv_rows(JUDGMENTS):
        query_id = str(row["query_id"]).strip()
        doc_id = str(row["doc_id"]).strip()
        label = int(float(row["relevance_label"]))
        labels[(query_id, doc_id)] = label
        labels_by_query[query_id].append(label)
    return labels, dict(labels_by_query)


def load_ranking(path: Path) -> dict[str, list[str]]:
    by_query: dict[str, list[tuple[int, str]]] = defaultdict(list)
    for row in read_csv_rows(path):
        query_id = str(row["query_id"]).strip()
        doc_id = str(row["doc_id"]).strip()
        if not query_id or not doc_id:
            continue
        by_query[query_id].append((int(float(row["rank"])), doc_id))
    return {query_id: [doc_id for _rank, doc_id in sorted(rows)] for query_id, rows in by_query.items()}


def gain(label: int) -> float:
    return float((2 ** max(int(label), 0)) - 1)


def dcg(labels: list[int], k: int) -> float:
    padded = labels + [0] * max(0, k - len(labels))
    return sum(gain(padded[index]) / math.log2(index + 2) for index in range(k))


def ndcg_at(labels: list[int], ideal: list[int], k: int) -> float:
    ideal_dcg = dcg(ideal, k)
    actual_dcg = dcg(labels, k)
    if ideal_dcg <= 0:
        return 1.0 if actual_dcg <= 0 else 0.0
    return actual_dcg / ideal_dcg


def average_precision(binary_relevance: list[bool], total_relevant: int) -> float:
    if total_relevant <= 0:
        return math.nan
    hits = 0
    precision_sum = 0.0
    for rank, is_relevant in enumerate(binary_relevance, start=1):
        if is_relevant:
            hits += 1
            precision_sum += hits / float(rank)
    return precision_sum / float(total_relevant)


def compute_query_metrics(
    ranked_docs: list[str],
    query_id: str,
    judgments: dict[tuple[str, str], int],
    judged_labels: list[int],
) -> dict[str, float]:
    ranked_top10 = ranked_docs[:10]
    grades = [judgments.get((query_id, doc_id), 0) for doc_id in ranked_top10]
    binary = [grade > 0 for grade in grades]
    total_relevant = sum(1 for label in judged_labels if label > 0)
    ideal = sorted(judged_labels, reverse=True)

    def p_at(k: int) -> float:
        return sum(binary[:k]) / float(k)

    def recall_at(k: int) -> float:
        return math.nan if total_relevant <= 0 else sum(binary[:k]) / float(total_relevant)

    reciprocal_rank = 0.0
    for rank, is_relevant in enumerate(binary, start=1):
        if is_relevant:
            reciprocal_rank = 1.0 / float(rank)
            break

    return {
        "p_at_1": p_at(1),
        "p_at_3": p_at(3),
        "p_at_5": p_at(5),
        "recall_at_5": recall_at(5),
        "recall_at_10": recall_at(10),
        "mrr": reciprocal_rank,
        "ndcg_at_5": ndcg_at(grades, ideal, 5),
        "ndcg_at_10": ndcg_at(grades, ideal, 10),
        "map": average_precision(binary, total_relevant),
    }


def mean_metric(rows: list[dict[str, Any]], metric: str) -> float:
    values = []
    for row in rows:
        value = row.get(metric)
        if isinstance(value, float) and math.isnan(value):
            continue
        values.append(float(value))
    return statistics.mean(values) if values else math.nan


def compute_all_metrics(methods: dict[str, Path]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    queries = load_queries()
    judgments, labels_by_query = load_judgments()

    by_query_rows: list[dict[str, Any]] = []
    for method, path in methods.items():
        ranking = load_ranking(path)
        for query in queries:
            query_id = str(query["query_id"])
            metrics = compute_query_metrics(
                ranking.get(query_id, []),
                query_id,
                judgments,
                labels_by_query.get(query_id, []),
            )
            by_query_rows.append(
                {
                    "baseline_name": method,
                    "query_id": query_id,
                    "query_text": query.get("query_text", ""),
                    "query_group": query.get("query_group", ""),
                    **metrics,
                }
            )

    summary_rows: list[dict[str, Any]] = []
    for method in methods:
        rows = [row for row in by_query_rows if row["baseline_name"] == method]
        summary = {"baseline_name": method, "num_queries": len(rows)}
        for metric in METRIC_FIELDS[2:]:
            summary[metric] = mean_metric(rows, metric)
        summary_rows.append(summary)

    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in by_query_rows:
        grouped[(str(row["baseline_name"]), str(row["query_group"]))].append(row)

    by_group_rows: list[dict[str, Any]] = []
    for (method, group), rows in sorted(grouped.items()):
        item = {"baseline_name": method, "query_group": group, "num_queries": len(rows)}
        for metric in BY_GROUP_FIELDS[3:]:
            item[metric] = mean_metric(rows, metric)
        by_group_rows.append(item)
    return summary_rows, by_query_rows, by_group_rows


def fmt(value: Any) -> str:
    try:
        if isinstance(value, float) and math.isnan(value):
            return ""
        return f"{float(value):.4f}"
    except Exception:
        return str(value)


def write_report(summary_rows: list[dict[str, Any]], methods: dict[str, Path]) -> None:
    summary_by_method = {row["baseline_name"]: row for row in summary_rows}
    fusion_note = ""
    if "hybrid_candidate_fusion" in summary_by_method:
        hybrid = summary_by_method["hybrid"]
        fusion_row = summary_by_method["hybrid_candidate_fusion"]
        recall_delta = float(fusion_row["recall_at_10"]) - float(hybrid["recall_at_10"])
        map_delta = float(fusion_row["map"]) - float(hybrid["map"])
        if recall_delta > 0 or map_delta > 0:
            fusion_note = (
                f"- `hybrid_candidate_fusion` cao hơn `hybrid` ở Recall@10 ({fmt(recall_delta)}) "
                f"và/hoặc MAP ({fmt(map_delta)}), cho thấy candidate fusion có thể giúp mở rộng candidate pool. "
                "Tuy nhiên đây vẫn là experiment/extension, không phải baseline final chính."
            )
        else:
            fusion_note = (
                "- `hybrid_candidate_fusion` được tính kèm như experiment/extension; kết quả không nên xem là thay thế baseline final."
            )

    lines = [
        "# Baseline Metrics Plus Report",
        "",
        "## Purpose",
        "",
        "Mục tiêu là bổ sung Recall@10 và MAP cho core evaluation 28 queries mà không thay đổi metric snapshot cũ.",
        "",
        "## Outputs",
        "",
        f"- `{SUMMARY_OUT.relative_to(PROJECT_ROOT)}`",
        f"- `{BY_QUERY_OUT.relative_to(PROJECT_ROOT)}`",
        f"- `{BY_GROUP_OUT.relative_to(PROJECT_ROOT)}`",
        f"- `{REPORT_OUT.relative_to(PROJECT_ROOT)}`",
        "",
        "## Metrics summary",
        "",
        "| method | P@1 | P@5 | Recall@5 | Recall@10 | MRR | nDCG@5 | nDCG@10 | MAP |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for method in methods:
        row = summary_by_method[method]
        lines.append(
            f"| {method} | {fmt(row['p_at_1'])} | {fmt(row['p_at_5'])} | "
            f"{fmt(row['recall_at_5'])} | {fmt(row['recall_at_10'])} | "
            f"{fmt(row['mrr'])} | {fmt(row['ndcg_at_5'])} | "
            f"{fmt(row['ndcg_at_10'])} | {fmt(row['map'])} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Recall@10 cho biết khả năng đưa tài liệu relevant vào top 10, phù hợp để phân tích candidate pool.",
            "- MAP đánh giá chất lượng xếp hạng trên toàn bộ danh sách relevant retrieved.",
        ]
    )
    if fusion_note:
        lines.append(fusion_note)
    lines.extend(
        [
            "",
            "## Safety confirmation",
            "",
            "- Không sửa metric cũ.",
            "- Không sửa runtime/scoring files.",
            "- Không sửa query set core.",
            "- Không sửa relevance judgments core.",
            "- Không sửa baseline result `_core.csv`.",
            "- Missing judgments được xem là relevance_label = 0.",
            "",
        ]
    )
    REPORT_OUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    methods = dict(RESULT_FILES)
    if CANDIDATE_FUSION_RESULT.exists():
        methods["hybrid_candidate_fusion"] = CANDIDATE_FUSION_RESULT

    missing = [str(path.relative_to(PROJECT_ROOT)) for path in methods.values() if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing result files: {missing}")

    summary_rows, by_query_rows, by_group_rows = compute_all_metrics(methods)
    write_csv(SUMMARY_OUT, summary_rows, METRIC_FIELDS)
    write_csv(BY_QUERY_OUT, by_query_rows, BY_QUERY_FIELDS)
    write_csv(BY_GROUP_OUT, by_group_rows, BY_GROUP_FIELDS)
    write_report(summary_rows, methods)

    print(f"[OK] Wrote {SUMMARY_OUT.relative_to(PROJECT_ROOT)}")
    print(f"[OK] Wrote {BY_QUERY_OUT.relative_to(PROJECT_ROOT)}")
    print(f"[OK] Wrote {BY_GROUP_OUT.relative_to(PROJECT_ROOT)}")
    print(f"[OK] Wrote {REPORT_OUT.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
