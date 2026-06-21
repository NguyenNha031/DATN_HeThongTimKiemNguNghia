from __future__ import annotations

import csv
import json
import math
import statistics
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import run_candidate_fusion_experiment as legacy_fusion
from hybrid_search import METADATA_PATH, build_metadata_lookup, build_term_index, load_full_metadata
from run_core_baselines import OkapiBM25, _normalize_minmax, _tokenize
from vector_search import load_index


CORE_QUERIES = PROJECT_ROOT / "data" / "eval" / "final_query_set_core.csv"
JUDGMENTS = PROJECT_ROOT / "data" / "eval" / "relevance_judgments_core.csv"
RESULTS_DIR = PROJECT_ROOT / "data" / "eval" / "results"
METRICS_DIR = PROJECT_ROOT / "data" / "eval" / "metrics"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

BASELINE_LEXICAL = RESULTS_DIR / "baseline_lexical_core.csv"
BASELINE_VECTOR = RESULTS_DIR / "baseline_vector_core.csv"
BASELINE_ONTOLOGY = RESULTS_DIR / "baseline_ontology_sparql_core.csv"
BASELINE_VECTOR_METADATA = RESULTS_DIR / "baseline_vector_metadata_core.csv"
BASELINE_HYBRID = RESULTS_DIR / "baseline_hybrid_core.csv"
BASELINE_METRICS_SUMMARY = METRICS_DIR / "baseline_metrics_summary.csv"
BASELINE_METRICS_BY_GROUP = METRICS_DIR / "baseline_metrics_by_group.csv"
BASELINE_METRICS_BY_QUERY_CANDIDATES = [
    METRICS_DIR / "baseline_metrics_by_query.csv",
    METRICS_DIR / "baseline_metrics_per_query.csv",
]

EXPERIMENT_RESULT = RESULTS_DIR / "baseline_hybrid_candidate_fusion_core.csv"
SUMMARY_CSV = METRICS_DIR / "hybrid_candidate_fusion_metrics_summary.csv"
BY_QUERY_CSV = METRICS_DIR / "hybrid_candidate_fusion_metrics_by_query.csv"
BY_GROUP_CSV = METRICS_DIR / "hybrid_candidate_fusion_metrics_by_group.csv"
ANALYSIS_MD = OUTPUTS_DIR / "hybrid_candidate_fusion_analysis.md"

TOP_DOCS = 10
LEXICAL_TOP_K = 20
VECTOR_TOP_K = 20
KG_SEED_TOP_K = 20

RESULT_FIELDS = [
    "query_id",
    "query",
    "query_text",
    "query_group",
    "baseline_name",
    "rank",
    "doc_id",
    "title",
    "score_raw",
    "score_normalized",
    "final_score",
    "vector_score",
    "metadata_delta",
    "kg_score",
    "intent_adjustment",
    "lexical_rank",
    "lexical_score",
    "kg_seed_rank",
    "kg_seed_score",
    "vector_rank",
    "candidate_sources",
    "candidate_union_count",
    "retrieval_level",
    "explanation",
    "explanation_short",
    "source_pipeline",
]

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
    "query",
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
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def load_core_queries() -> list[dict[str, str]]:
    return read_csv_rows(CORE_QUERIES)


def load_source_baseline(path: Path, top_k: int) -> dict[str, dict[str, dict[str, Any]]]:
    by_query: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in read_csv_rows(path):
        try:
            rank = int(float(row.get("rank", 0)))
        except ValueError:
            continue
        if rank > top_k:
            continue
        qid = str(row.get("query_id", "")).strip()
        doc_id = str(row.get("doc_id", "")).strip()
        if not qid or not doc_id:
            continue
        by_query[qid][doc_id] = row | {"rank_int": rank}
    return dict(by_query)


def trim_ranked_docs(rows_by_doc: dict[str, dict[str, Any]], rank_key: str, top_k: int) -> dict[str, dict[str, Any]]:
    items = sorted(
        rows_by_doc.items(),
        key=lambda item: int(float(item[1].get(rank_key, 10**9) or 10**9)),
    )
    return dict(items[:top_k])


def build_kg_seed_lookup() -> dict[str, dict[str, dict[str, Any]]]:
    return load_source_baseline(BASELINE_ONTOLOGY, KG_SEED_TOP_K)


def build_fused_candidates_for_query(
    query_id: str,
    query_text: str,
    model: Any,
    index: Any,
    records: list[dict[str, Any]],
    bm25: OkapiBM25,
    metadata_lookup: dict[str, dict[str, Any]],
    term_index: list[dict[str, Any]],
    kg_seed_by_query: dict[str, dict[str, dict[str, Any]]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    detected, kg_entities = legacy_fusion.link_and_merge_entities(query_text, term_index)
    _vector_pool, vector_by_doc_raw, vector_all = legacy_fusion.build_vector_candidates(
        query_text, model, index, records, detected
    )
    _lexical_pool, lexical_by_doc_raw = legacy_fusion.build_lexical_chunk_candidates(query_text, records, bm25)

    vector_by_doc = trim_ranked_docs(vector_by_doc_raw, "vector_rank", VECTOR_TOP_K)
    lexical_by_doc = trim_ranked_docs(lexical_by_doc_raw, "lexical_rank", LEXICAL_TOP_K)
    kg_seed_by_doc = kg_seed_by_query.get(query_id, {})
    vector_all_by_doc = vector_all.get("by_doc") or {}

    candidates_by_doc: dict[str, dict[str, Any]] = {}
    doc_ids = sorted(set(vector_by_doc) | set(lexical_by_doc) | set(kg_seed_by_doc))
    for doc_id in doc_ids:
        vector_row = vector_by_doc.get(doc_id)
        lexical_row = lexical_by_doc.get(doc_id)
        kg_seed_row = kg_seed_by_doc.get(doc_id)
        all_vector_row = vector_all_by_doc.get(doc_id, {})
        base = (vector_row or all_vector_row or lexical_row or kg_seed_row or {}).copy()
        title = (
            base.get("title")
            or all_vector_row.get("title")
            or (lexical_row or {}).get("title")
            or (kg_seed_row or {}).get("title")
            or ""
        )
        sources: list[str] = []
        if vector_row is not None:
            sources.append("vector")
        if lexical_row is not None:
            sources.append("lexical")
        if kg_seed_row is not None:
            sources.append("kg_seed")

        base["doc_id"] = doc_id
        base["title"] = title
        base["came_from_vector"] = vector_row is not None
        base["came_from_lexical"] = lexical_row is not None
        base["came_from_kg_seed"] = kg_seed_row is not None
        base["candidate_sources"] = "|".join(sources)
        base["vector_rank"] = (vector_row or {}).get("vector_rank", "")
        base["lexical_rank"] = (lexical_row or {}).get("lexical_rank", "")
        base["kg_seed_rank"] = (kg_seed_row or {}).get("rank", "")
        base["vector_score"] = float((all_vector_row or vector_row or {}).get("score", 0.0) or 0.0)
        base["lexical_score"] = float((lexical_row or {}).get("lexical_score", 0.0) or 0.0)
        base["kg_seed_score"] = float((kg_seed_row or {}).get("score_raw", 0.0) or 0.0)
        candidates_by_doc[doc_id] = base

    reranked = legacy_fusion.score_fused_candidates(
        query_text,
        candidates_by_doc,
        metadata_lookup,
        detected,
        kg_entities,
    )
    stats = {
        "query_id": query_id,
        "vector_candidate_count": len(vector_by_doc),
        "lexical_candidate_count": len(lexical_by_doc),
        "kg_seed_candidate_count": len(kg_seed_by_doc),
        "union_candidate_count": len(candidates_by_doc),
        "union_larger_than_vector": len(candidates_by_doc) > len(vector_by_doc),
    }
    return reranked[:TOP_DOCS], stats


def make_result_rows(core: list[dict[str, str]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    model, index, records = load_index()
    metadata_df = load_full_metadata(METADATA_PATH)
    metadata_lookup = build_metadata_lookup(metadata_df)
    term_index = build_term_index(metadata_df)
    bm25 = OkapiBM25([_tokenize(str(row.get("text", ""))) for row in records])
    kg_seed_by_query = build_kg_seed_lookup()

    rows: list[dict[str, Any]] = []
    candidate_stats: list[dict[str, Any]] = []
    for query in core:
        query_id = str(query["query_id"])
        query_text = str(query["query_text"])
        top_items, stats = build_fused_candidates_for_query(
            query_id,
            query_text,
            model,
            index,
            records,
            bm25,
            metadata_lookup,
            term_index,
            kg_seed_by_query,
        )
        candidate_stats.append(stats)
        raw_scores = [float(item.get("final_score", 0.0)) for item in top_items]
        normalized = _normalize_minmax(raw_scores)
        for rank, (item, norm_score) in enumerate(zip(top_items, normalized), start=1):
            rows.append(
                {
                    "query_id": query_id,
                    "query": query_text,
                    "query_text": query_text,
                    "query_group": query.get("query_group", ""),
                    "baseline_name": "hybrid_candidate_fusion",
                    "rank": rank,
                    "doc_id": item.get("doc_id", ""),
                    "title": item.get("title", ""),
                    "score_raw": item.get("final_score", 0.0),
                    "score_normalized": norm_score,
                    "final_score": item.get("final_score", 0.0),
                    "vector_score": item.get("vector_score", 0.0),
                    "metadata_delta": item.get("metadata_delta", 0.0),
                    "kg_score": item.get("kg_score", 0.0),
                    "intent_adjustment": item.get("intent_adjustment", 0.0),
                    "lexical_rank": item.get("lexical_rank", ""),
                    "lexical_score": item.get("lexical_score", 0.0),
                    "kg_seed_rank": item.get("kg_seed_rank", ""),
                    "kg_seed_score": item.get("kg_seed_score", 0.0),
                    "vector_rank": item.get("vector_rank", ""),
                    "candidate_sources": item.get("candidate_sources", ""),
                    "candidate_union_count": stats["union_candidate_count"],
                    "retrieval_level": "hybrid_candidate_fusion_doc_pool",
                    "explanation": item.get("explanation", ""),
                    "explanation_short": "BM25 + vector + KG/SPARQL seed candidate union, hybrid scoring rerank",
                    "source_pipeline": (
                        "experiments/run_hybrid_candidate_fusion.py; "
                        f"lexical_top_k={LEXICAL_TOP_K}; vector_top_k={VECTOR_TOP_K}; "
                        f"kg_seed_top_k={KG_SEED_TOP_K}; scoring=vector_score+metadata_delta+kg_score+intent_adjustment; "
                        "not final hybrid"
                    ),
                }
            )
    return rows, candidate_stats


def load_judgments() -> tuple[dict[tuple[str, str], int], dict[str, list[int]]]:
    judgments: dict[tuple[str, str], int] = {}
    labels_by_query: dict[str, list[int]] = defaultdict(list)
    for row in read_csv_rows(JUDGMENTS):
        query_id = str(row["query_id"]).strip()
        doc_id = str(row["doc_id"]).strip()
        label = int(float(row["relevance_label"]))
        judgments[(query_id, doc_id)] = label
        labels_by_query[query_id].append(label)
    return judgments, dict(labels_by_query)


def gain(relevance: int) -> float:
    return float((2 ** max(int(relevance), 0)) - 1)


def dcg(grades: list[int], k: int) -> float:
    padded = grades + [0] * max(0, k - len(grades))
    return sum(gain(padded[i]) / math.log2(i + 2) for i in range(k))


def ndcg_at_k(grades: list[int], ideal: list[int], k: int) -> float:
    ideal_dcg = dcg(ideal, k)
    actual = dcg(grades, k)
    if ideal_dcg <= 0:
        return 1.0 if actual <= 0 else 0.0
    return actual / ideal_dcg


def average_precision(binary_relevance: list[bool], total_relevant: int) -> float:
    if total_relevant <= 0:
        return math.nan
    hits = 0
    precision_sum = 0.0
    for index, is_relevant in enumerate(binary_relevance, start=1):
        if is_relevant:
            hits += 1
            precision_sum += hits / float(index)
    return precision_sum / float(total_relevant)


def compute_query_metrics(
    ranked_docs: list[str],
    query_id: str,
    judgments: dict[tuple[str, str], int],
    labels: list[int],
) -> dict[str, float]:
    grades = [judgments.get((query_id, doc_id), 0) for doc_id in ranked_docs]
    binary = [grade > 0 for grade in grades]
    total_relevant = sum(1 for label in labels if label > 0)
    ideal = sorted(labels, reverse=True)

    def p_at(k: int) -> float:
        return sum(binary[:k]) / float(k)

    def recall_at(k: int) -> float:
        if total_relevant <= 0:
            return math.nan
        return sum(binary[:k]) / float(total_relevant)

    reciprocal_rank = 0.0
    for index, is_relevant in enumerate(binary, start=1):
        if is_relevant:
            reciprocal_rank = 1.0 / float(index)
            break

    return {
        "p_at_1": p_at(1),
        "p_at_3": p_at(3),
        "p_at_5": p_at(5),
        "recall_at_5": recall_at(5),
        "recall_at_10": recall_at(10),
        "mrr": reciprocal_rank,
        "ndcg_at_5": ndcg_at_k(grades, ideal, 5),
        "ndcg_at_10": ndcg_at_k(grades, ideal, 10),
        "map": average_precision(binary, total_relevant),
    }


def rankings_from_rows(rows: list[dict[str, Any]]) -> dict[str, list[str]]:
    by_query: dict[str, list[tuple[int, str]]] = defaultdict(list)
    for row in rows:
        by_query[str(row["query_id"])].append((int(float(row["rank"])), str(row["doc_id"])))
    return {query_id: [doc_id for _rank, doc_id in sorted(items)] for query_id, items in by_query.items()}


def load_ranking(path: Path) -> dict[str, list[str]]:
    return rankings_from_rows(read_csv_rows(path))


def metric_rows_by_query(
    baseline_name: str,
    rankings: dict[str, list[str]],
    core: list[dict[str, str]],
    judgments: dict[tuple[str, str], int],
    labels_by_query: dict[str, list[int]],
) -> list[dict[str, Any]]:
    rows = []
    for query in core:
        query_id = str(query["query_id"])
        metrics = compute_query_metrics(rankings.get(query_id, []), query_id, judgments, labels_by_query.get(query_id, []))
        rows.append(
            {
                "baseline_name": baseline_name,
                "query_id": query_id,
                "query": query.get("query_text", ""),
                "query_group": query.get("query_group", ""),
                **metrics,
            }
        )
    return rows


def mean_metric(rows: list[dict[str, Any]], metric: str) -> float:
    values = []
    for row in rows:
        value = row.get(metric)
        if isinstance(value, float) and math.isnan(value):
            continue
        values.append(float(value))
    return statistics.mean(values) if values else math.nan


def summarize_query_metrics(baseline_name: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {"baseline_name": baseline_name, "num_queries": len(rows)}
    for metric in METRIC_FIELDS[2:]:
        out[metric] = mean_metric(rows, metric)
    return out


def group_metric_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(str(row["baseline_name"]), str(row.get("query_group", "")))].append(row)
    out = []
    for (baseline_name, query_group), group_rows in sorted(grouped.items()):
        item: dict[str, Any] = {
            "baseline_name": baseline_name,
            "query_group": query_group,
            "num_queries": len(group_rows),
        }
        for metric in BY_GROUP_FIELDS[3:]:
            item[metric] = mean_metric(group_rows, metric)
        out.append(item)
    return out


def fmt_metric(value: Any) -> str:
    try:
        if isinstance(value, float) and math.isnan(value):
            return ""
        return f"{float(value):.4f}"
    except Exception:
        return str(value)


def delta_interpretation(delta: float) -> str:
    if delta > 0.01:
        return "improved"
    if delta < -0.01:
        return "decreased"
    return "roughly unchanged"


def load_optional_existing_metric_files() -> list[str]:
    read_files = []
    for path in [BASELINE_METRICS_SUMMARY, BASELINE_METRICS_BY_GROUP, *BASELINE_METRICS_BY_QUERY_CANDIDATES]:
        if path.exists():
            _ = read_csv_rows(path)
            read_files.append(str(path.relative_to(PROJECT_ROOT)))
    return read_files


def write_analysis(
    summary_rows: list[dict[str, Any]],
    group_rows: list[dict[str, Any]],
    by_query_rows: list[dict[str, Any]],
    candidate_stats: list[dict[str, Any]],
    existing_metric_files_read: list[str],
) -> None:
    summary_by_name = {row["baseline_name"]: row for row in summary_rows}
    group_by_name: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in group_rows:
        group_by_name[str(row["baseline_name"])][str(row["query_group"])] = row

    hybrid = summary_by_name["hybrid"]
    fusion = summary_by_name["hybrid_candidate_fusion"]
    delta_ndcg10 = float(fusion["ndcg_at_10"]) - float(hybrid["ndcg_at_10"])
    delta_recall10 = float(fusion["recall_at_10"]) - float(hybrid["recall_at_10"])
    delta_p1 = float(fusion["p_at_1"]) - float(hybrid["p_at_1"])
    delta_mrr = float(fusion["mrr"]) - float(hybrid["mrr"])

    query_delta_rows = []
    hybrid_by_query = {
        (row["query_id"], row["baseline_name"]): row for row in by_query_rows if row["baseline_name"] == "hybrid"
    }
    for row in by_query_rows:
        if row["baseline_name"] != "hybrid_candidate_fusion":
            continue
        base = hybrid_by_query.get((row["query_id"], "hybrid"), {})
        query_delta_rows.append(
            {
                "query_id": row["query_id"],
                "query_group": row["query_group"],
                "delta_ndcg10": float(row["ndcg_at_10"]) - float(base.get("ndcg_at_10", 0.0)),
            }
        )
    improved_groups = []
    decreased_groups = []
    for group, h_row in group_by_name["hybrid"].items():
        f_row = group_by_name["hybrid_candidate_fusion"].get(group)
        if not f_row:
            continue
        delta = float(f_row["ndcg_at_10"]) - float(h_row["ndcg_at_10"])
        if delta > 0.01:
            improved_groups.append(group)
        elif delta < -0.01:
            decreased_groups.append(group)

    mixed = (
        delta_ndcg10 <= 0.01
        or bool(decreased_groups)
        or float(fusion["p_at_5"]) < float(hybrid["p_at_5"]) - 1e-9
        or float(fusion["recall_at_5"]) < float(hybrid["recall_at_5"]) - 1e-9
        or float(fusion["ndcg_at_5"]) < float(hybrid["ndcg_at_5"]) - 1e-9
    )
    recommendation = (
        "B. Ket qua mixed: chi nen dua vao Chuong 5/huong phat trien hoac phu luc ky thuat, khong thay hybrid final."
        if mixed
        else "A. Co the trinh bay o Chuong 4 nhu thu nghiem mo rong candidate generation."
    )

    avg = lambda key: statistics.mean(float(row[key]) for row in candidate_stats) if candidate_stats else 0.0
    lines = [
        "# Hybrid Candidate Fusion Experiment",
        "",
        "## Purpose",
        "",
        "Thí nghiệm này nhằm giảm phụ thuộc vào vector candidate pool ban đầu bằng cách hợp nhất ứng viên từ BM25, vector search và KG/SPARQL seed trước khi rerank. Đây là experiment/extension, không thay baseline `hybrid` final.",
        "",
        "## Method",
        "",
        f"- Lexical candidates: BM25 over vector-store chunk text, aggregated to document level, `lexical_top_k={LEXICAL_TOP_K}`.",
        f"- Vector candidates: FAISS vector search, aggregated to document level, `vector_top_k={VECTOR_TOP_K}`.",
        f"- KG/SPARQL seed candidates: top documents from `baseline_ontology_sparql_core.csv`, `kg_seed_top_k={KG_SEED_TOP_K}`; actual file has top {int(avg('kg_seed_candidate_count')) if candidate_stats else 0} average seeds/query available.",
        "- Candidate pool is deduplicated by `doc_id`; each row keeps `candidate_sources`, source ranks and source scores when available.",
        "- Reranking/scoring reuses current hybrid components through existing functions: `vector_score + metadata_delta + kg_score + intent_adjustment`.",
        "- The experiment does not change the query set, judgments, metadata, ontology, runtime final, or old baseline outputs/metrics.",
        "",
        "Candidate pool statistics:",
        "",
        f"- Average vector candidates/query: {fmt_metric(avg('vector_candidate_count'))}",
        f"- Average lexical candidates/query: {fmt_metric(avg('lexical_candidate_count'))}",
        f"- Average KG seed candidates/query: {fmt_metric(avg('kg_seed_candidate_count'))}",
        f"- Average union candidates/query: {fmt_metric(avg('union_candidate_count'))}",
        "",
        "Existing baseline metric files read for comparison:",
        "",
    ]
    lines.extend([f"- `{path}`" for path in existing_metric_files_read] or ["- No existing metric file was available."])
    lines.extend(
        [
            "",
            "## Outputs",
            "",
            f"- `{EXPERIMENT_RESULT.relative_to(PROJECT_ROOT)}`",
            f"- `{SUMMARY_CSV.relative_to(PROJECT_ROOT)}`",
            f"- `{BY_QUERY_CSV.relative_to(PROJECT_ROOT)}`",
            f"- `{BY_GROUP_CSV.relative_to(PROJECT_ROOT)}`",
            f"- `{ANALYSIS_MD.relative_to(PROJECT_ROOT)}`",
            "",
            "## Metrics summary",
            "",
            "| method | P@1 | P@5 | Recall@5 | Recall@10 | MRR | nDCG@5 | nDCG@10 | MAP |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for name in ["vector_metadata", "hybrid", "hybrid_candidate_fusion"]:
        row = summary_by_name[name]
        lines.append(
            f"| {name} | {fmt_metric(row['p_at_1'])} | {fmt_metric(row['p_at_5'])} | "
            f"{fmt_metric(row['recall_at_5'])} | {fmt_metric(row['recall_at_10'])} | "
            f"{fmt_metric(row['mrr'])} | {fmt_metric(row['ndcg_at_5'])} | "
            f"{fmt_metric(row['ndcg_at_10'])} | {fmt_metric(row['map'])} |"
        )
    lines.extend(
        [
            "",
            "## Group-level analysis",
            "",
            "| query_group | hybrid nDCG@10 | candidate_fusion nDCG@10 | delta | interpretation |",
            "| --- | ---: | ---: | ---: | --- |",
        ]
    )
    for group in sorted(group_by_name["hybrid"]):
        h_row = group_by_name["hybrid"][group]
        f_row = group_by_name["hybrid_candidate_fusion"][group]
        delta = float(f_row["ndcg_at_10"]) - float(h_row["ndcg_at_10"])
        lines.append(
            f"| {group} | {fmt_metric(h_row['ndcg_at_10'])} | {fmt_metric(f_row['ndcg_at_10'])} | "
            f"{fmt_metric(delta)} | {delta_interpretation(delta)} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            f"- Compared with `hybrid`, candidate fusion changes P@1 by {fmt_metric(delta_p1)}, MRR by {fmt_metric(delta_mrr)}, nDCG@10 by {fmt_metric(delta_ndcg10)}, and Recall@10 by {fmt_metric(delta_recall10)}.",
            "- Summary-level metrics improve, but the result is still mixed because some query groups regress.",
            f"- Groups improved by nDCG@10: {', '.join(improved_groups) if improved_groups else 'none'}.",
            f"- Groups decreased by nDCG@10: {', '.join(decreased_groups) if decreased_groups else 'none'}.",
            "- Candidate fusion expands the candidate pool, so it can recover documents from lexical/KG seed sources that are weak in vector ranking.",
            "- Trade-off: adding lexical/KG seed candidates can introduce noise; because the reranker is reused without tuning, some top-5 metrics or group-level nDCG can decrease.",
            "",
            "Largest query-level nDCG@10 changes vs hybrid:",
            "",
        ]
    )
    for row in sorted(query_delta_rows, key=lambda item: item["delta_ndcg10"], reverse=True)[:3]:
        lines.append(f"- `{row['query_id']}` ({row['query_group']}): {fmt_metric(row['delta_ndcg10'])}")
    for row in sorted(query_delta_rows, key=lambda item: item["delta_ndcg10"])[:3]:
        lines.append(f"- `{row['query_id']}` ({row['query_group']}): {fmt_metric(row['delta_ndcg10'])}")
    lines.extend(
        [
            "",
            "## Report recommendation",
            "",
            recommendation,
            "",
            "## Safety note",
            "",
            "- Không sửa `hybrid_search.py`.",
            "- Không sửa `kg_runtime.py`.",
            "- Không sửa `vector_search.py`.",
            "- Không sửa ontology final.",
            "- Không sửa metadata.",
            "- Không sửa query set.",
            "- Không sửa relevance judgments.",
            "- Không sửa baseline metrics cũ.",
            "- Không sửa baseline outputs cũ ngoài output riêng của experiment `baseline_hybrid_candidate_fusion_core.csv`.",
            "",
        ]
    )
    ANALYSIS_MD.parent.mkdir(parents=True, exist_ok=True)
    ANALYSIS_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    core = load_core_queries()
    existing_metric_files_read = load_optional_existing_metric_files()
    result_rows, candidate_stats = make_result_rows(core)
    write_csv(EXPERIMENT_RESULT, result_rows, RESULT_FIELDS)

    judgments, labels_by_query = load_judgments()
    rankings = {
        "vector_metadata": load_ranking(BASELINE_VECTOR_METADATA),
        "hybrid": load_ranking(BASELINE_HYBRID),
        "hybrid_candidate_fusion": rankings_from_rows(result_rows),
    }
    all_by_query_rows: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []
    for baseline_name, ranking in rankings.items():
        rows = metric_rows_by_query(baseline_name, ranking, core, judgments, labels_by_query)
        all_by_query_rows.extend(rows)
        summary_rows.append(summarize_query_metrics(baseline_name, rows))
    group_rows = group_metric_rows(all_by_query_rows)

    write_csv(SUMMARY_CSV, summary_rows, METRIC_FIELDS)
    write_csv(BY_QUERY_CSV, all_by_query_rows, BY_QUERY_FIELDS)
    write_csv(BY_GROUP_CSV, group_rows, BY_GROUP_FIELDS)
    write_analysis(summary_rows, group_rows, all_by_query_rows, candidate_stats, existing_metric_files_read)

    manifest = {
        "experiment": "hybrid_candidate_fusion",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "outputs": [
            str(EXPERIMENT_RESULT.relative_to(PROJECT_ROOT)),
            str(SUMMARY_CSV.relative_to(PROJECT_ROOT)),
            str(BY_QUERY_CSV.relative_to(PROJECT_ROOT)),
            str(BY_GROUP_CSV.relative_to(PROJECT_ROOT)),
            str(ANALYSIS_MD.relative_to(PROJECT_ROOT)),
        ],
        "candidate_config": {
            "lexical_top_k": LEXICAL_TOP_K,
            "vector_top_k": VECTOR_TOP_K,
            "kg_seed_top_k": KG_SEED_TOP_K,
            "dedup_key": "doc_id",
            "rerank_formula": "vector_score + metadata_delta + kg_score + intent_adjustment",
        },
    }
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
