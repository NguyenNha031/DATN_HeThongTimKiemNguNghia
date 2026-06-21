from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


OUTPUT_MD = Path("outputs") / "evaluation_layers_summary.md"
OUTPUT_JSON = Path("outputs") / "evaluation_layers_summary.json"

EXPECTED_FILES = [
    "data/eval/final_query_set_core.csv",
    "data/eval/relevance_judgments_core.csv",
    "data/eval/results/baseline_lexical_core.csv",
    "data/eval/results/baseline_vector_core.csv",
    "data/eval/results/baseline_vector_metadata_core.csv",
    "data/eval/results/baseline_ontology_sparql_core.csv",
    "data/eval/results/baseline_hybrid_core.csv",
    "data/eval/results/baseline_vector_metadata_kg_no_intent_core.csv",
    "data/eval/metrics/baseline_metrics_summary.csv",
    "data/eval/metrics/baseline_metrics_by_group.csv",
    "data/eval/metrics/baseline_latency_summary.csv",
    "outputs/competency_questions_results.csv",
    "outputs/competency_questions_summary.json",
    "outputs/ontology_quality_check.md",
    "outputs/ontology_quality_check.json",
    "outputs/ontology_reasoner_consistency_check.md",
    "outputs/ontology_reasoner_consistency_check.json",
    "outputs/wilcoxon_hybrid_vs_vector_metadata.csv",
    "outputs/wilcoxon_hybrid_vs_vector_metadata.json",
    "outputs/error_analysis_core.csv",
    "outputs/error_analysis_summary.json",
]

PRIMARY_METRICS = ["p_at_1", "p_at_3", "p_at_5", "recall_at_5", "mrr", "ndcg_at_5", "ndcg_at_10"]
ABLATION_BASELINES = ["vector", "vector_metadata", "vector_metadata_kg_no_intent", "hybrid"]


def read_csv_rows(path: str) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def read_json(path: str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def fnum(value: Any, digits: int = 4) -> str:
    if value is None or value == "":
        return ""
    try:
        return f"{float(value):.{digits}f}"
    except Exception:
        return str(value)


def metric_value(row: dict[str, Any], metric: str) -> float | None:
    try:
        return float(row.get(metric, ""))
    except Exception:
        return None


def md_table(headers: list[str], rows: list[list[Any]]) -> list[str]:
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        out.append("| " + " | ".join(str(x) for x in row) + " |")
    return out


def best_by_metric(metrics_rows: list[dict[str, str]]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for metric in PRIMARY_METRICS:
        candidates = []
        for row in metrics_rows:
            v = metric_value(row, metric)
            if v is not None:
                candidates.append((v, row["baseline_name"]))
        if candidates:
            value, name = max(candidates, key=lambda x: x[0])
            out[metric] = {"baseline_name": name, "value": value}
    return out


def summarize_group_findings(by_group_rows: list[dict[str, str]]) -> dict[str, Any]:
    groups = sorted({row["query_group"] for row in by_group_rows})
    out: dict[str, Any] = {}
    for group in groups:
        group_rows = [r for r in by_group_rows if r["query_group"] == group]
        out[group] = best_by_metric(group_rows)
    return out


def load_inputs() -> dict[str, Any]:
    files_read = [f for f in EXPECTED_FILES if Path(f).exists()]
    files_missing = [f for f in EXPECTED_FILES if not Path(f).exists()]

    data: dict[str, Any] = {
        "files_read": files_read,
        "files_missing": files_missing,
    }

    if Path("data/eval/final_query_set_core.csv").exists():
        data["query_rows"] = read_csv_rows("data/eval/final_query_set_core.csv")
    if Path("data/eval/relevance_judgments_core.csv").exists():
        data["judgment_rows"] = read_csv_rows("data/eval/relevance_judgments_core.csv")
    if Path("data/eval/metrics/baseline_metrics_summary.csv").exists():
        data["metrics_summary_rows"] = read_csv_rows("data/eval/metrics/baseline_metrics_summary.csv")
    if Path("data/eval/metrics/baseline_metrics_by_group.csv").exists():
        data["metrics_by_group_rows"] = read_csv_rows("data/eval/metrics/baseline_metrics_by_group.csv")
    if Path("data/eval/metrics/baseline_latency_summary.csv").exists():
        data["latency_rows"] = read_csv_rows("data/eval/metrics/baseline_latency_summary.csv")

    json_files = {
        "competency_questions_summary": "outputs/competency_questions_summary.json",
        "ontology_quality_check": "outputs/ontology_quality_check.json",
        "ontology_reasoner_consistency_check": "outputs/ontology_reasoner_consistency_check.json",
        "wilcoxon": "outputs/wilcoxon_hybrid_vs_vector_metadata.json",
        "error_analysis_summary": "outputs/error_analysis_summary.json",
    }
    for key, path in json_files.items():
        if Path(path).exists():
            data[key] = read_json(path)
    return data


def build_summary(data: dict[str, Any]) -> dict[str, Any]:
    metrics_rows = data.get("metrics_summary_rows", [])
    by_group_rows = data.get("metrics_by_group_rows", [])
    latency_rows = data.get("latency_rows", [])

    metrics_by_baseline = {row["baseline_name"]: row for row in metrics_rows}
    latency_by_baseline = {row["baseline_name"]: row for row in latency_rows}
    best_overall = best_by_metric(metrics_rows)
    best_by_group = summarize_group_findings(by_group_rows)

    ablation = []
    for name in ABLATION_BASELINES:
        row = metrics_by_baseline.get(name, {})
        ablation.append(
            {
                "baseline_name": name,
                "p_at_1": metric_value(row, "p_at_1"),
                "p_at_5": metric_value(row, "p_at_5"),
                "mrr": metric_value(row, "mrr"),
                "ndcg_at_10": metric_value(row, "ndcg_at_10"),
            }
        )

    cq = data.get("competency_questions_summary", {})
    quality = data.get("ontology_quality_check", {})
    reasoner = data.get("ontology_reasoner_consistency_check", {})
    wilcoxon_results = data.get("wilcoxon", {}).get("results", [])
    wilcoxon_main = {
        r.get("metric"): {
            "n_queries": r.get("n_queries"),
            "mean_hybrid": r.get("mean_hybrid"),
            "mean_vector_metadata": r.get("mean_vector_metadata"),
            "p_value": r.get("p_value"),
            "significant_at_0_05": r.get("significant_at_0_05"),
        }
        for r in wilcoxon_results
        if r.get("metric") in {"P@1", "MRR", "nDCG@10"}
    }

    error_summary = data.get("error_analysis_summary", {})

    return {
        "layer_1_retrieval_evaluation": {
            "num_queries": len(data.get("query_rows", [])) or None,
            "num_relevance_judgments": len(data.get("judgment_rows", [])) or None,
            "baselines": list(metrics_by_baseline.keys()),
            "metrics": PRIMARY_METRICS,
            "metrics_by_baseline": metrics_by_baseline,
            "best_overall_by_metric": best_overall,
            "best_by_query_group": best_by_group,
            "latency_by_baseline": latency_by_baseline,
        },
        "layer_2_ontology_kg_evaluation": {
            "competency_questions": cq,
            "ontology_quality_check": quality,
            "reasoner_consistency_check": reasoner,
        },
        "layer_3_full_system_contribution_analysis": {
            "ablation_metrics": ablation,
            "wilcoxon_hybrid_vs_vector_metadata": wilcoxon_main,
            "error_analysis": error_summary,
        },
        "cross_layer_notes": [
            "Retrieval metrics evaluate ranking quality over judged query-document pairs.",
            "Competency questions and reasoner checks evaluate the structured ontology/KG layer, not ranking quality.",
            "Ablation isolates contribution of vector, metadata, KG, and intent-adjustment signals in the full system.",
        ],
        "files_read": data["files_read"],
        "files_missing": data["files_missing"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def write_markdown(summary: dict[str, Any]) -> None:
    layer1 = summary["layer_1_retrieval_evaluation"]
    layer2 = summary["layer_2_ontology_kg_evaluation"]
    layer3 = summary["layer_3_full_system_contribution_analysis"]
    cq = layer2.get("competency_questions") or {}
    quality = layer2.get("ontology_quality_check") or {}
    coverage = quality.get("document_fact_coverage") or {}
    mapping = quality.get("document_mapping_status") or {}
    consistency = quality.get("runtime_consistency_observations") or {}
    reasoner = layer2.get("reasoner_consistency_check") or {}
    wilcoxon = layer3.get("wilcoxon_hybrid_vs_vector_metadata") or {}
    error_analysis = layer3.get("error_analysis") or {}

    metrics_rows = list((layer1.get("metrics_by_baseline") or {}).values())
    latency_rows = layer1.get("latency_by_baseline") or {}

    lines: list[str] = [
        "# Evaluation Layers Summary",
        "",
        "## 1. Purpose",
        "",
        "This artifact separates three evaluation layers of the project so that retrieval metrics, ontology/KG evaluation, and full-system contribution analysis are not mixed together.",
        "It is a summary artifact only. It does not modify ontology files, metadata, query sets, relevance judgments, baseline outputs, metric outputs, or runtime retrieval code.",
        "",
        "## 2. Layer 1 - Retrieval evaluation",
        "",
        "Layer 1 evaluates search and ranking quality over the 28-query core retrieval benchmark.",
        "",
        "**Input files**",
        "",
        "- Query set: `data/eval/final_query_set_core.csv`",
        "- Relevance judgments: `data/eval/relevance_judgments_core.csv`",
        "- Baseline result files: lexical, vector, vector_metadata, ontology_sparql, hybrid, and vector_metadata_kg_no_intent.",
        "",
        "**Baselines**",
        "",
        "- `lexical`: BM25-style lexical retrieval.",
        "- `vector`: FAISS + SentenceTransformer vector retrieval.",
        "- `vector_metadata`: vector score plus metadata reranking.",
        "- `ontology_sparql`: structured ontology/SPARQL baseline.",
        "- `hybrid`: full hybrid retrieval.",
        "",
        "**Metrics**",
        "",
        "- P@1, P@3, P@5, Recall@5, MRR, nDCG@5, nDCG@10.",
        "- Latency is reported separately when `baseline_latency_summary.csv` is available.",
        "",
        "**Main outputs**",
        "",
        "- `data/eval/metrics/baseline_metrics_summary.csv`",
        "- `data/eval/metrics/baseline_metrics_by_group.csv`",
        "- `data/eval/metrics/baseline_latency_summary.csv`",
        "",
        "**Overall retrieval metrics**",
        "",
    ]

    metric_table_rows = []
    for row in metrics_rows:
        metric_table_rows.append(
            [
                row.get("baseline_name", ""),
                row.get("num_queries", ""),
                fnum(row.get("p_at_1")),
                fnum(row.get("p_at_5")),
                fnum(row.get("recall_at_5")),
                fnum(row.get("mrr")),
                fnum(row.get("ndcg_at_10")),
            ]
        )
    lines.extend(md_table(["baseline", "queries", "P@1", "P@5", "Recall@5", "MRR", "nDCG@10"], metric_table_rows))

    lines.extend(["", "**Latency summary**", ""])
    latency_table_rows = []
    for name, row in latency_rows.items():
        latency_table_rows.append(
            [
                name,
                row.get("runs_per_query", ""),
                row.get("warmup_done", ""),
                fnum(row.get("mean_query_latency_ms"), 3),
                fnum(row.get("median_query_latency_ms"), 3),
            ]
        )
    lines.extend(md_table(["baseline", "runs/query", "warmup", "mean ms", "median ms"], latency_table_rows))

    best = layer1.get("best_overall_by_metric") or {}
    hybrid_best = all((best.get(m) or {}).get("baseline_name") == "hybrid" for m in PRIMARY_METRICS if m in best)
    lines.extend(
        [
            "",
            "**Key result summary**",
            "",
            f"- Hybrid is the highest overall baseline across the primary summary metrics in this snapshot: `{hybrid_best}`.",
            "- `vector_metadata` is close to hybrid on several metrics, especially P@1 and MRR.",
            "- `ontology_sparql` is not the best overall ranking baseline, but it is strong for structured/entity-heavy groups such as disease-specific queries.",
            "- Lexical retrieval remains competitive in the local group; in `baseline_metrics_by_group.csv`, lexical leads or ties some local metrics such as P@1/MRR/nDCG@10.",
            "- This is retrieval ranking evaluation, not competency-question evaluation.",
            "",
            "## 3. Layer 2 - Ontology/KG evaluation",
            "",
            "Layer 2 evaluates the ontology/KG as a structured knowledge layer. It does not measure end-to-end ranking quality.",
            "",
            "**Competency questions**",
            "",
            f"- Total CQ: {cq.get('total_cq')}",
            f"- Correct: {cq.get('correct')}",
            f"- Partial: {cq.get('partial')}",
            f"- Incorrect: {cq.get('incorrect')}",
            f"- Accuracy-like ratio: {fnum(cq.get('accuracy_like_ratio'))}",
            "",
        ]
    )
    cq_group_rows = []
    for group, stats in (cq.get("by_group") or {}).items():
        cq_group_rows.append([group, stats.get("total"), stats.get("correct"), stats.get("partial"), stats.get("incorrect")])
    lines.extend(md_table(["CQ group", "total", "correct", "partial", "incorrect"], cq_group_rows))

    lines.extend(
        [
            "",
            "**SPARQL / structured query role**",
            "",
            "- Competency questions and the `ontology_sparql` baseline test whether structured relations/facts can be queried and used as evidence.",
            "- This checks KG fact usability; it does not replace judged retrieval ranking metrics.",
            "",
            "**Runtime-oriented ontology quality**",
            "",
            f"- Ontology file: `{quality.get('ontology_file_loaded')}`",
            f"- Total triples: {quality.get('total_triples')}",
            f"- Document nodes: {quality.get('total_document_nodes')}",
            f"- Metadata docs mapped to KG: {mapping.get('mapped_metadata_docs_to_kg')} / {mapping.get('total_metadata_docs')}",
            f"- aboutTaxon coverage: {coverage.get('aboutTaxon_count_docs')} docs ({fnum(coverage.get('aboutTaxon_ratio'))})",
            f"- aboutDisease coverage: {coverage.get('aboutDisease_count_docs')} docs ({fnum(coverage.get('aboutDisease_ratio'))})",
            f"- aboutLocation coverage: {coverage.get('aboutLocation_count_docs')} docs ({fnum(coverage.get('aboutLocation_ratio'))})",
            f"- documentProductionMode coverage: {coverage.get('documentProductionMode_count_docs')} docs ({fnum(coverage.get('documentProductionMode_ratio'))})",
            f"- Dangling fact objects: {consistency.get('dangling_fact_objects_count')}",
            "",
            "**Reasoner-based consistency check**",
            "",
            f"- Reasoner used: `{reasoner.get('reasoner_used')}`",
            f"- Check status: `{reasoner.get('check_status')}`",
            f"- is_consistent: `{reasoner.get('is_consistent')}`",
            f"- Unsatisfiable classes count: {reasoner.get('unsatisfiable_classes_count')}",
            "- Limitation: reasoner consistency does not prove that every asserted fact is correct in the aquaculture domain.",
            "- Competency questions and reasoner checks do not replace retrieval metrics.",
            "",
            "## 4. Layer 3 - Full-system contribution analysis",
            "",
            "Layer 3 analyzes how each signal layer contributes to the full hybrid system.",
            "",
            "**Ablation configurations**",
            "",
            "- `vector`: score = vector_score.",
            "- `vector_metadata`: score = vector_score + metadata_delta.",
            "- `vector_metadata_kg_no_intent`: score = vector_score + metadata_delta + kg_score.",
            "- `hybrid`: score = vector_score + metadata_delta + kg_score + intent_adjustment.",
            "",
            "**Ablation metric summary**",
            "",
        ]
    )
    ablation_rows = []
    for row in layer3.get("ablation_metrics") or []:
        ablation_rows.append(
            [
                row.get("baseline_name"),
                fnum(row.get("p_at_1")),
                fnum(row.get("p_at_5")),
                fnum(row.get("mrr")),
                fnum(row.get("ndcg_at_10")),
            ]
        )
    lines.extend(md_table(["configuration", "P@1", "P@5", "MRR", "nDCG@10"], ablation_rows))

    lines.extend(["", "**Wilcoxon hybrid vs vector_metadata**", ""])
    wilcoxon_rows = []
    for metric in ["P@1", "MRR", "nDCG@10"]:
        row = wilcoxon.get(metric) or {}
        wilcoxon_rows.append(
            [
                metric,
                row.get("n_queries", ""),
                fnum(row.get("mean_hybrid")),
                fnum(row.get("mean_vector_metadata")),
                fnum(row.get("p_value")),
                row.get("significant_at_0_05", ""),
            ]
        )
    lines.extend(md_table(["metric", "n", "mean hybrid", "mean vector_metadata", "p-value", "significant @0.05"], wilcoxon_rows))

    lines.extend(
        [
            "",
            "- The Wilcoxon result should be interpreted cautiously: hybrid has higher means on the main metrics, but the tested differences are not significant at p < 0.05 in the current 28-query core set.",
            "",
            "**Error analysis**",
            "",
            f"- Total curated cases: {error_analysis.get('total_cases')}",
        ]
    )
    for error_type, count in (error_analysis.get("count_by_error_type") or {}).items():
        lines.append(f"- {error_type}: {count}")

    lines.extend(
        [
            "",
            "- Ablation is not the same as the overall baseline comparison; it isolates contribution of signal layers inside the hybrid design.",
            "",
            "## 5. Cross-layer interpretation",
            "",
            "- Retrieval evaluation answers: which method retrieves and ranks judged documents better?",
            "- Ontology/KG evaluation answers: can the ontology/KG expose structured knowledge, answer competency questions, and remain logically consistent under a reasoner?",
            "- Contribution analysis answers: how do metadata, KG scoring, and intent adjustment contribute to the full hybrid score?",
            "- Retrieval metrics are not competency questions. Competency questions/reasoner checks are not retrieval ranking. Ablation is not the overall baseline comparison.",
            "",
            "## 6. Files checklist",
            "",
            "**Files read**",
            "",
        ]
    )
    for path in summary.get("files_read") or []:
        lines.append(f"- `{path}`")
    lines.extend(["", "**Missing or not found**", ""])
    missing = summary.get("files_missing") or []
    if missing:
        for path in missing:
            lines.append(f"- `{path}`")
    else:
        lines.append("- None from the expected file list.")

    lines.extend(["", f"Generated at: `{summary.get('generated_at')}`", ""])
    OUTPUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    data = load_inputs()
    summary = build_summary(data)
    OUTPUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(summary)
    print(f"[OK] Wrote {OUTPUT_MD} and {OUTPUT_JSON}")


if __name__ == "__main__":
    main()
