from __future__ import annotations

import csv
import math
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
QUERY_SET = PROJECT_ROOT / "data" / "eval" / "final_query_set_core.csv"
JUDGMENTS = PROJECT_ROOT / "data" / "eval" / "relevance_judgments_core.csv"
HYBRID_RESULTS = PROJECT_ROOT / "data" / "eval" / "results" / "baseline_hybrid_core.csv"
VECTOR_METADATA_RESULTS = PROJECT_ROOT / "data" / "eval" / "results" / "baseline_vector_metadata_core.csv"
KG_COMPONENTS = PROJECT_ROOT / "outputs" / "kg_score_component_analysis.csv"

RESULTS_OUT = PROJECT_ROOT / "data" / "eval" / "results" / "kg_ablation_results_core.csv"
SUMMARY_OUT = PROJECT_ROOT / "data" / "eval" / "metrics" / "kg_ablation_metrics_summary.csv"
BY_QUERY_OUT = PROJECT_ROOT / "data" / "eval" / "metrics" / "kg_ablation_metrics_by_query.csv"
BY_GROUP_OUT = PROJECT_ROOT / "data" / "eval" / "metrics" / "kg_ablation_metrics_by_group.csv"
REPORT_OUT = PROJECT_ROOT / "outputs" / "kg_ablation_analysis.md"
FIGURE_OUT = PROJECT_ROOT / "outputs" / "figures" / "fig_kg_ablation_summary.png"

CONFIGS = [
    {
        "name": "vector_metadata",
        "label": "Vector + metadata",
        "formula": "hybrid_score_raw - kg_score - intent_adjustment",
        "meaning": "Vector + metadata approximation on the fixed hybrid top-10 candidate pool.",
    },
    {
        "name": "kg_direct_only",
        "label": "+ KG direct facts",
        "formula": "vector_metadata_score + kg_direct_fact_score_diagnostic",
        "meaning": "Adds only direct document fact evidence such as aboutDisease/aboutTaxon/aboutLocation/documentProductionMode.",
    },
    {
        "name": "kg_relation_only",
        "label": "+ KG relation evidence",
        "formula": "vector_metadata_score + kg_relation_score_diagnostic",
        "meaning": "Adds relation/context evidence such as affectsTaxon, causedBy, isFoundIn, prevention/pathogen context.",
    },
    {
        "name": "full_kg_no_intent",
        "label": "+ Full KG, no intent",
        "formula": "vector_metadata_score + kg_score",
        "meaning": "Adds full KG score but excludes final intent adjustment.",
    },
    {
        "name": "full_hybrid",
        "label": "Full hybrid",
        "formula": "hybrid_score_raw",
        "meaning": "Current hybrid ranking with vector, metadata, KG and intent adjustment.",
    },
]

METRIC_FIELDS = [
    "method",
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
    "method",
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
    "method",
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
RESULT_FIELDS = [
    "method",
    "query_id",
    "query_text",
    "query_group",
    "rank",
    "doc_id",
    "title",
    "score",
    "base_vector_metadata_score",
    "kg_score",
    "kg_direct_fact_score_diagnostic",
    "kg_relation_score_diagnostic",
    "intent_adjustment",
    "source_note",
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


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default


def build_candidate_rows() -> list[dict[str, Any]]:
    queries = pd.read_csv(QUERY_SET, encoding="utf-8-sig")
    query_info = queries.set_index("query_id").to_dict(orient="index")
    hybrid = pd.read_csv(HYBRID_RESULTS, encoding="utf-8-sig")
    components = pd.read_csv(KG_COMPONENTS, encoding="utf-8-sig")
    component_cols = [
        "query_id",
        "doc_id",
        "kg_score",
        "intent_adjustment",
        "kg_direct_fact_score_diagnostic",
        "kg_relation_score_diagnostic",
        "kg_explanation_score_diagnostic",
        "kg_penalty_diagnostic",
        "kg_unclassified_score_diagnostic",
    ]
    merged = hybrid.merge(components[component_cols], on=["query_id", "doc_id"], how="left")

    rows: list[dict[str, Any]] = []
    for _, row in merged.iterrows():
        query_id = str(row["query_id"])
        final_score = safe_float(row.get("score_raw"))
        kg_score = safe_float(row.get("kg_score"))
        intent_adjustment = safe_float(row.get("intent_adjustment"))
        base_score = final_score - kg_score - intent_adjustment
        direct_score = safe_float(row.get("kg_direct_fact_score_diagnostic"))
        relation_score = safe_float(row.get("kg_relation_score_diagnostic"))
        info = query_info.get(query_id, {})
        rows.append(
            {
                "query_id": query_id,
                "query_text": str(row.get("query_text") or info.get("query_text") or ""),
                "query_group": str(info.get("query_group", "")),
                "doc_id": str(row.get("doc_id", "")),
                "title": str(row.get("title", "")),
                "hybrid_rank": int(float(row.get("rank", 0))),
                "hybrid_score_raw": final_score,
                "base_vector_metadata_score": base_score,
                "kg_score": kg_score,
                "kg_direct_fact_score_diagnostic": direct_score,
                "kg_relation_score_diagnostic": relation_score,
                "intent_adjustment": intent_adjustment,
            }
        )
    return rows


def score_for_config(row: dict[str, Any], config_name: str) -> float:
    base = float(row["base_vector_metadata_score"])
    if config_name == "vector_metadata":
        return base
    if config_name == "kg_direct_only":
        return base + float(row["kg_direct_fact_score_diagnostic"])
    if config_name == "kg_relation_only":
        return base + float(row["kg_relation_score_diagnostic"])
    if config_name == "full_kg_no_intent":
        return base + float(row["kg_score"])
    if config_name == "full_hybrid":
        return float(row["hybrid_score_raw"])
    raise ValueError(f"Unknown config: {config_name}")


def build_ablation_results(candidate_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_query: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in candidate_rows:
        by_query[str(row["query_id"])].append(row)

    out: list[dict[str, Any]] = []
    for config in CONFIGS:
        name = config["name"]
        for query_id, rows in by_query.items():
            scored = []
            for row in rows:
                scored.append((score_for_config(row, name), row))
            scored.sort(key=lambda item: (item[0], -float(item[1]["hybrid_rank"])), reverse=True)
            for rank, (score, row) in enumerate(scored[:10], start=1):
                out.append(
                    {
                        "method": name,
                        "query_id": query_id,
                        "query_text": row["query_text"],
                        "query_group": row["query_group"],
                        "rank": rank,
                        "doc_id": row["doc_id"],
                        "title": row["title"],
                        "score": score,
                        "base_vector_metadata_score": row["base_vector_metadata_score"],
                        "kg_score": row["kg_score"],
                        "kg_direct_fact_score_diagnostic": row["kg_direct_fact_score_diagnostic"],
                        "kg_relation_score_diagnostic": row["kg_relation_score_diagnostic"],
                        "intent_adjustment": row["intent_adjustment"],
                        "source_note": "Diagnostic ablation on fixed baseline_hybrid_core top-10 candidate rows; direct/relation from kg_score_component_analysis.csv.",
                    }
                )
    return out


def load_judgments() -> tuple[dict[tuple[str, str], int], dict[str, list[int]]]:
    labels: dict[tuple[str, str], int] = {}
    labels_by_query: dict[str, list[int]] = defaultdict(list)
    for row in read_csv_rows(JUDGMENTS):
        query_id = str(row["query_id"])
        doc_id = str(row["doc_id"])
        label = int(float(row["relevance_label"]))
        labels[(query_id, doc_id)] = label
        labels_by_query[query_id].append(label)
    return labels, dict(labels_by_query)


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


def average_precision(binary: list[bool], total_relevant: int) -> float:
    if total_relevant <= 0:
        return math.nan
    hits = 0
    precision_sum = 0.0
    for rank, is_relevant in enumerate(binary, start=1):
        if is_relevant:
            hits += 1
            precision_sum += hits / float(rank)
    return precision_sum / float(total_relevant)


def compute_query_metrics(
    ranked_docs: list[str],
    query_id: str,
    judgments: dict[tuple[str, str], int],
    labels: list[int],
) -> dict[str, float]:
    grades = [judgments.get((query_id, doc_id), 0) for doc_id in ranked_docs[:10]]
    binary = [grade > 0 for grade in grades]
    total_relevant = sum(1 for label in labels if label > 0)
    ideal = sorted(labels, reverse=True)

    def p_at(k: int) -> float:
        return sum(binary[:k]) / float(k)

    def recall_at(k: int) -> float:
        return math.nan if total_relevant <= 0 else sum(binary[:k]) / float(total_relevant)

    rr = 0.0
    for rank, ok in enumerate(binary, start=1):
        if ok:
            rr = 1.0 / float(rank)
            break
    return {
        "p_at_1": p_at(1),
        "p_at_3": p_at(3),
        "p_at_5": p_at(5),
        "recall_at_5": recall_at(5),
        "recall_at_10": recall_at(10),
        "mrr": rr,
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


def compute_metrics(result_rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    queries = read_csv_rows(QUERY_SET)
    judgments, labels_by_query = load_judgments()
    by_method_query: dict[tuple[str, str], list[tuple[int, str]]] = defaultdict(list)
    for row in result_rows:
        by_method_query[(str(row["method"]), str(row["query_id"]))].append((int(row["rank"]), str(row["doc_id"])))

    by_query_rows: list[dict[str, Any]] = []
    for config in CONFIGS:
        method = config["name"]
        for query in queries:
            query_id = str(query["query_id"])
            ranked = [doc_id for _rank, doc_id in sorted(by_method_query[(method, query_id)])]
            metrics = compute_query_metrics(ranked, query_id, judgments, labels_by_query.get(query_id, []))
            by_query_rows.append(
                {
                    "method": method,
                    "query_id": query_id,
                    "query_text": query.get("query_text", ""),
                    "query_group": query.get("query_group", ""),
                    **metrics,
                }
            )

    summary_rows: list[dict[str, Any]] = []
    for config in CONFIGS:
        method = config["name"]
        rows = [row for row in by_query_rows if row["method"] == method]
        summary = {"method": method, "num_queries": len(rows)}
        for metric in METRIC_FIELDS[2:]:
            summary[metric] = mean_metric(rows, metric)
        summary_rows.append(summary)

    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in by_query_rows:
        grouped[(str(row["method"]), str(row["query_group"]))].append(row)
    by_group_rows: list[dict[str, Any]] = []
    for (method, group), rows in sorted(grouped.items()):
        item = {"method": method, "query_group": group, "num_queries": len(rows)}
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


def config_label(name: str) -> str:
    for config in CONFIGS:
        if config["name"] == name:
            return config["label"]
    return name


def write_figure(summary_rows: list[dict[str, Any]]) -> None:
    FIGURE_OUT.parent.mkdir(parents=True, exist_ok=True)
    metrics = [
        ("P@1", "p_at_1"),
        ("Recall@10", "recall_at_10"),
        ("MRR", "mrr"),
        ("nDCG@10", "ndcg_at_10"),
        ("MAP", "map"),
    ]
    methods = [config["name"] for config in CONFIGS]
    by_method = {row["method"]: row for row in summary_rows}
    values = np.array([[float(by_method[method][metric]) for _label, metric in metrics] for method in methods])
    colors = ["#6b7280", "#2563eb", "#16a34a", "#7c3aed", "#dc2626"]

    plt.rcParams.update({
        "font.size": 10.5,
        "axes.titlesize": 14,
        "axes.labelsize": 11,
        "xtick.labelsize": 10,
        "ytick.labelsize": 9.5,
        "legend.fontsize": 9.2,
    })
    fig, ax = plt.subplots(figsize=(13.2, 6.8), facecolor="white")
    x = np.arange(len(metrics))
    width = 0.15
    for idx, method in enumerate(methods):
        offset = (idx - 2) * width
        bars = ax.bar(x + offset, values[idx], width, label=config_label(method), color=colors[idx], edgecolor="white", linewidth=0.8)
        for metric_idx, bar in enumerate(bars):
            height = float(values[idx, metric_idx])
            ax.text(bar.get_x() + bar.get_width() / 2, height + 0.012, f"{height:.3f}", ha="center", va="bottom", fontsize=7.8)
    ax.set_title("KG ablation on core queries")
    ax.set_ylabel("Metric value")
    ax.set_xlabel("Metric")
    ax.set_xticks(x)
    ax.set_xticklabels([label for label, _metric in metrics])
    ax.set_ylim(0, 1.05)
    ax.grid(axis="y", color="#e5e7eb", linewidth=0.9)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=3, frameon=False)
    fig.text(
        0.5,
        0.012,
        "Hình 4.x. Ablation mở rộng các nhóm evidence của KG runtime trong hybrid search",
        ha="center",
        va="bottom",
        fontsize=9.5,
        color="#374151",
    )
    fig.tight_layout(rect=(0.02, 0.09, 0.98, 0.98))
    fig.savefig(FIGURE_OUT, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def write_report(
    summary_rows: list[dict[str, Any]],
    by_group_rows: list[dict[str, Any]],
) -> None:
    summary_by_method = {row["method"]: row for row in summary_rows}
    group_lookup = {(row["method"], row["query_group"]): row for row in by_group_rows}
    groups = sorted({row["query_group"] for row in by_group_rows})
    methods = [config["name"] for config in CONFIGS]

    direct = summary_by_method["kg_direct_only"]
    relation = summary_by_method["kg_relation_only"]
    vm = summary_by_method["vector_metadata"]
    full_no_intent = summary_by_method["full_kg_no_intent"]
    full = summary_by_method["full_hybrid"]

    direct_delta = float(direct["ndcg_at_10"]) - float(vm["ndcg_at_10"])
    relation_delta = float(relation["ndcg_at_10"]) - float(vm["ndcg_at_10"])
    full_kg_delta = float(full_no_intent["ndcg_at_10"]) - float(vm["ndcg_at_10"])
    intent_delta = float(full["ndcg_at_10"]) - float(full_no_intent["ndcg_at_10"])

    lines = [
        "# KG Ablation Analysis",
        "",
        "## Purpose",
        "",
        "Mục tiêu là kiểm tra đóng góp riêng của direct fact evidence, relation/context evidence, full KG và intent adjustment trong hybrid search.",
        "",
        "## Scope and caution",
        "",
        "- Đây là diagnostic ablation, không thay đổi hybrid final.",
        "- Candidate pool được cố định theo top-10 rows của `baseline_hybrid_core.csv` để so sánh các công thức score trên cùng tập candidate.",
        "- Direct/relation scores được lấy từ `outputs/kg_score_component_analysis.csv`; vì baseline result không log component gốc, đây là diagnostic approximation.",
        "",
        "## Configurations",
        "",
        "| configuration | score formula | meaning |",
        "| --- | --- | --- |",
    ]
    for config in CONFIGS:
        lines.append(f"| {config['name']} | `{config['formula']}` | {config['meaning']} |")

    lines.extend(
        [
            "",
            "## Metrics summary",
            "",
            "| method | P@1 | P@5 | Recall@5 | Recall@10 | MRR | nDCG@5 | nDCG@10 | MAP |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for method in methods:
        row = summary_by_method[method]
        lines.append(
            f"| {method} | {fmt(row['p_at_1'])} | {fmt(row['p_at_5'])} | {fmt(row['recall_at_5'])} | "
            f"{fmt(row['recall_at_10'])} | {fmt(row['mrr'])} | {fmt(row['ndcg_at_5'])} | "
            f"{fmt(row['ndcg_at_10'])} | {fmt(row['map'])} |"
        )

    lines.extend(
        [
            "",
            "## By-group analysis",
            "",
            "| query_group | best_config | nDCG@10 best | direct_only nDCG@10 | relation_only nDCG@10 | full_kg_no_intent nDCG@10 | full_hybrid nDCG@10 | interpretation |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for group in groups:
        best_method = max(methods, key=lambda method: float(group_lookup[(method, group)]["ndcg_at_10"]))
        best_value = float(group_lookup[(best_method, group)]["ndcg_at_10"])
        direct_value = float(group_lookup[("kg_direct_only", group)]["ndcg_at_10"])
        relation_value = float(group_lookup[("kg_relation_only", group)]["ndcg_at_10"])
        no_intent_value = float(group_lookup[("full_kg_no_intent", group)]["ndcg_at_10"])
        hybrid_value = float(group_lookup[("full_hybrid", group)]["ndcg_at_10"])
        if best_method == "kg_relation_only":
            interpretation = "relation/context evidence is most useful in this group"
        elif best_method == "kg_direct_only":
            interpretation = "direct KG facts dominate this group"
        elif best_method == "full_kg_no_intent":
            interpretation = "combined KG is useful before intent adjustment"
        elif best_method == "full_hybrid":
            interpretation = "full hybrid scoring is strongest"
        else:
            interpretation = "KG components do not improve this fixed-pool ranking"
        lines.append(
            f"| {group} | {best_method} | {fmt(best_value)} | {fmt(direct_value)} | {fmt(relation_value)} | "
            f"{fmt(no_intent_value)} | {fmt(hybrid_value)} | {interpretation} |"
        )

    dominant = "direct facts" if direct_delta >= relation_delta else "relation/context evidence"
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            f"- Direct-only nDCG@10 delta vs vector_metadata: {fmt(direct_delta)}.",
            f"- Relation-only nDCG@10 delta vs vector_metadata: {fmt(relation_delta)}.",
            f"- Trong fixed hybrid candidate pool này, `{dominant}` tạo cải thiện nDCG@10 lớn hơn.",
            f"- Full KG no intent delta vs vector_metadata: {fmt(full_kg_delta)}.",
            f"- Intent adjustment delta full_hybrid vs full_kg_no_intent: {fmt(intent_delta)}.",
            "- Nếu full_hybrid thấp hơn full_kg_no_intent ở một metric, điều đó không nhất thiết phủ định intent guardrail; đây là fixed-pool diagnostic và intent adjustment chủ yếu xử lý một số case hẹp.",
            "",
            "## Limitations",
            "",
            "- Vì baseline result không lưu component gốc, direct/relation score là diagnostic approximation từ `kg_score_component_analysis.csv`.",
            "- Candidate pool cố định theo top-10 hybrid rows, nên kết quả không phải production baseline mới.",
            "- Không chứng minh mọi KG fact đúng chuyên ngành.",
            "- Không thay thế final hybrid.",
            "- Cần instrumentation sâu hơn trong future work nếu muốn log chính xác component score ở runtime.",
            "",
            "## Report recommendation",
            "",
            "Có thể đưa vào báo cáo như `Phân tích ablation mở rộng KG runtime`, kèm caveat rõ rằng đây là diagnostic trên fixed candidate pool và direct/relation scores là approximation.",
            "",
            "## Safety confirmation",
            "",
            "- Không sửa runtime/scoring files.",
            "- Không sửa ontology.",
            "- Không sửa metadata.",
            "- Không sửa query set.",
            "- Không sửa relevance judgments.",
            "- Không sửa baseline outputs/metrics cũ.",
            "",
            "## Outputs",
            "",
            f"- `{RESULTS_OUT.relative_to(PROJECT_ROOT)}`",
            f"- `{SUMMARY_OUT.relative_to(PROJECT_ROOT)}`",
            f"- `{BY_QUERY_OUT.relative_to(PROJECT_ROOT)}`",
            f"- `{BY_GROUP_OUT.relative_to(PROJECT_ROOT)}`",
            f"- `{REPORT_OUT.relative_to(PROJECT_ROOT)}`",
            f"- `{FIGURE_OUT.relative_to(PROJECT_ROOT)}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    candidate_rows = build_candidate_rows()
    result_rows = build_ablation_results(candidate_rows)
    summary_rows, by_query_rows, by_group_rows = compute_metrics(result_rows)
    write_csv(RESULTS_OUT, result_rows, RESULT_FIELDS)
    write_csv(SUMMARY_OUT, summary_rows, METRIC_FIELDS)
    write_csv(BY_QUERY_OUT, by_query_rows, BY_QUERY_FIELDS)
    write_csv(BY_GROUP_OUT, by_group_rows, BY_GROUP_FIELDS)
    write_figure(summary_rows)
    write_report(summary_rows, by_group_rows)
    print(f"[OK] Wrote {SUMMARY_OUT.relative_to(PROJECT_ROOT)}")
    print(f"[OK] Wrote {BY_QUERY_OUT.relative_to(PROJECT_ROOT)}")
    print(f"[OK] Wrote {BY_GROUP_OUT.relative_to(PROJECT_ROOT)}")
    print(f"[OK] Wrote {REPORT_OUT.relative_to(PROJECT_ROOT)}")
    print(f"[OK] Wrote {FIGURE_OUT.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
