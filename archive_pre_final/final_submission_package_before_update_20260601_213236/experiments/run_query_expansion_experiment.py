from __future__ import annotations

import csv
import math
import re
import sys
import traceback
import unicodedata
from collections import defaultdict
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

CORE_QUERY_PATH = PROJECT_ROOT / "data" / "eval" / "final_query_set_core.csv"
JUDGMENT_PATH = PROJECT_ROOT / "data" / "eval" / "relevance_judgments_core.csv"
HYBRID_BASELINE_PATH = PROJECT_ROOT / "data" / "eval" / "results" / "baseline_hybrid_core.csv"
VECTOR_METADATA_BASELINE_PATH = PROJECT_ROOT / "data" / "eval" / "results" / "baseline_vector_metadata_core.csv"
CANDIDATE_FUSION_BASELINE_PATH = PROJECT_ROOT / "data" / "eval" / "results" / "baseline_hybrid_candidate_fusion_core.csv"
METADATA_PATH = PROJECT_ROOT / "data" / "metadata" / "document_metadata_cleaned.xlsx"
EXPANSION_EXAMPLES_PATH = PROJECT_ROOT / "outputs" / "query_expansion_examples.csv"
QUERY_PROFILES_PATH = PROJECT_ROOT / "outputs" / "query_understanding_profiles.csv"

RESULT_PATH = PROJECT_ROOT / "data" / "eval" / "results" / "baseline_hybrid_query_expansion_core.csv"
SUMMARY_PATH = PROJECT_ROOT / "data" / "eval" / "metrics" / "query_expansion_metrics_summary.csv"
BY_QUERY_PATH = PROJECT_ROOT / "data" / "eval" / "metrics" / "query_expansion_metrics_by_query.csv"
BY_GROUP_PATH = PROJECT_ROOT / "data" / "eval" / "metrics" / "query_expansion_metrics_by_group.csv"
APPLIED_TERMS_PATH = PROJECT_ROOT / "outputs" / "query_expansion_applied_terms.csv"
REPORT_PATH = PROJECT_ROOT / "outputs" / "query_expansion_experiment_analysis.md"
FIGURE_PATH = PROJECT_ROOT / "outputs" / "figures" / "fig_query_expansion_experiment_summary.png"

TOP_K = 10
DISEASE_MAX_TERMS = 4
TAXON_MAX_TERMS = 3
LOCATION_MAX_TERMS = 3
MODE_MAX_TERMS = 3
TOTAL_MAX_TERMS = 8

METHOD_FILES = {
    "vector_metadata": VECTOR_METADATA_BASELINE_PATH,
    "hybrid": HYBRID_BASELINE_PATH,
    "hybrid_candidate_fusion": CANDIDATE_FUSION_BASELINE_PATH,
    "hybrid_query_expansion": RESULT_PATH,
}

METRIC_COLUMNS = ["P@1", "P@5", "Recall@5", "Recall@10", "MRR", "nDCG@5", "nDCG@10", "MAP"]


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and pd.isna(value):
        return ""
    text = str(value).lower().strip()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.replace("đ", "d")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def clean(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and pd.isna(value):
        return ""
    return str(value).strip()


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        text = str(value).strip()
        if not text:
            return default
        return float(text)
    except Exception:
        return default


def split_terms(value: Any) -> list[str]:
    text = clean(value)
    if not text:
        return []
    parts = re.split(r";|\||,", text)
    return [p.strip() for p in parts if p and p.strip()]


def token_match(needle: str, haystack: str) -> bool:
    n = normalize_text(needle)
    h = normalize_text(haystack)
    if not n or not h:
        return False
    return bool(re.search(rf"(?<![a-z0-9]){re.escape(n)}(?![a-z0-9])", f" {h} "))


def phrase_overlap(a: str, b: str) -> bool:
    an = normalize_text(a)
    bn = normalize_text(b)
    if not an or not bn:
        return False
    if token_match(an, bn) or token_match(bn, an):
        return True
    a_tokens = {t for t in an.split() if len(t) > 2}
    b_tokens = {t for t in bn.split() if len(t) > 2}
    if not a_tokens or not b_tokens:
        return False
    overlap = a_tokens & b_tokens
    return len(overlap) >= min(2, len(a_tokens), len(b_tokens))


def is_generic_or_risky(term: str, entity_type: str, query_text: str) -> bool:
    n = normalize_text(term)
    q = normalize_text(query_text)
    very_generic = {
        "aquaculture",
        "fisheries",
        "fishery",
        "disease",
        "shrimp",
        "fish",
        "health",
        "risk",
        "control",
        "monitoring",
        "global",
        "asia",
    }
    if n in very_generic:
        return True
    if n == "vibrio" and "vibrio" not in q and "vibriosis" not in q and "ahpnd" not in q:
        return True
    if n in {"biosecurity", "disease prevention", "disease control", "surveillance"}:
        return not any(x in q for x in ["biosecurity", "an toan sinh hoc", "phong", "prevention", "control", "surveillance", "ahpnd", "ems"])
    if entity_type == "location" and n in {"vietnam", "viet nam"}:
        return not any(x in q for x in ["vietnam", "viet nam", "khanh hoa", "dbscl", "mekong", "phu yen"])
    return False


def expansion_bucket(entity_type: str, expansion_type: str) -> str:
    et = normalize_text(entity_type)
    xt = normalize_text(expansion_type)
    if "disease" in et or "pathogen" in xt or "symptom" in xt or "prevention" in xt or "treatment" in xt:
        return "disease"
    if "taxon" in et or "species" in et:
        return "taxon"
    if "location" in et:
        return "location"
    return "mode"


def bucket_limit(bucket: str) -> int:
    return {
        "disease": DISEASE_MAX_TERMS,
        "taxon": TAXON_MAX_TERMS,
        "location": LOCATION_MAX_TERMS,
        "mode": MODE_MAX_TERMS,
    }.get(bucket, MODE_MAX_TERMS)


def query_matches_expansion_row(query_text: str, row: dict[str, Any]) -> tuple[bool, str]:
    detected = clean(row.get("detected_entity"))
    terms = split_terms(row.get("expansion_terms"))
    if token_match(detected, query_text):
        return True, f"detected_entity matched query: {detected}"
    matched_terms = [t for t in terms if token_match(t, query_text)]
    if matched_terms:
        return True, f"expansion term already present as alias: {matched_terms[0]}"
    return False, "no entity/alias overlap with query"


def expansion_row_allowed(row: dict[str, Any]) -> tuple[bool, str]:
    entity_type = normalize_text(row.get("entity_type"))
    expansion_type = normalize_text(row.get("expansion_type"))
    # These rows are useful as design examples, but they are too broad for a controlled retrieval experiment.
    if expansion_type == "location_parent" and entity_type != "location":
        return False, "skip taxon/topic to location-parent expansion to reduce drift"
    if "disease_to_prevention" in expansion_type and entity_type not in {"disease"}:
        return False, "skip topic-to-disease prevention expansion to reduce drift"
    return True, "allowed"


def select_expansion_terms(query: dict[str, Any], examples: pd.DataFrame) -> tuple[list[str], list[dict[str, Any]]]:
    query_id = clean(query.get("query_id"))
    query_text = clean(query.get("query_text"))
    query_group = clean(query.get("query_group"))
    q_norm = normalize_text(query_text)
    used_terms: list[str] = []
    audit_rows: list[dict[str, Any]] = []
    bucket_counts: defaultdict[str, int] = defaultdict(int)
    seen_norm: set[str] = set()

    candidates: list[tuple[int, dict[str, Any], str]] = []
    exact_rows = examples[examples["query_id"].astype(str) == query_id] if "query_id" in examples.columns else pd.DataFrame()
    source_iter = exact_rows.iterrows() if not exact_rows.empty else examples.iterrows()
    for _, erow in source_iter:
        row = erow.to_dict()
        allowed, allow_reason = expansion_row_allowed(row)
        if not allowed:
            continue
        if not exact_rows.empty:
            matched, reason = True, f"exact expansion row for query_id {query_id}"
        else:
            matched, reason = query_matches_expansion_row(query_text, row)
        if not matched:
            continue
        bucket = expansion_bucket(clean(row.get("entity_type")), clean(row.get("expansion_type")))
        priority = 0
        exp_type = normalize_text(row.get("expansion_type"))
        if "alias" in exp_type or "scientific" in exp_type:
            priority -= 10
        if "pathogen" in exp_type:
            priority -= 6
        if "prevention" in exp_type or "symptom" in exp_type or "treatment" in exp_type:
            priority -= 3
        if clean(row.get("query_group")) == query_group:
            priority -= 4
        candidates.append((priority, row, reason))

    for _, row, match_reason in sorted(candidates, key=lambda x: (x[0], clean(x[1].get("query_id")))):
        bucket = expansion_bucket(clean(row.get("entity_type")), clean(row.get("expansion_type")))
        for term in split_terms(row.get("expansion_terms")):
            term_norm = normalize_text(term)
            if not term_norm or term_norm in seen_norm:
                continue
            source_field = clean(row.get("expansion_source"))
            expansion_type = clean(row.get("expansion_type"))
            if term_norm in q_norm:
                used = False
                reason = "term already present in query"
            elif is_generic_or_risky(term, clean(row.get("entity_type")), query_text):
                used = False
                reason = "filtered generic/risky term"
            elif bucket_counts[bucket] >= bucket_limit(bucket):
                used = False
                reason = f"bucket limit reached for {bucket}"
            elif len(used_terms) >= TOTAL_MAX_TERMS:
                used = False
                reason = "total expansion limit reached"
            else:
                used = True
                reason = match_reason
                used_terms.append(term)
                seen_norm.add(term_norm)
                bucket_counts[bucket] += 1
            audit_rows.append(
                {
                    "query_id": query_id,
                    "query_text": query_text,
                    "query_group": query_group,
                    "detected_entity_or_intent": clean(row.get("detected_entity")),
                    "expansion_term": term,
                    "expansion_type": expansion_type,
                    "source_field": source_field,
                    "used": str(used).lower(),
                    "reason": reason,
                }
            )
            if len(used_terms) >= TOTAL_MAX_TERMS:
                # Continue audit for already considered candidates is not necessary for this lightweight experiment.
                break
        if len(used_terms) >= TOTAL_MAX_TERMS:
            break

    if not audit_rows:
        audit_rows.append(
            {
                "query_id": query_id,
                "query_text": query_text,
                "query_group": query_group,
                "detected_entity_or_intent": "",
                "expansion_term": "",
                "expansion_type": "",
                "source_field": "",
                "used": "false",
                "reason": "no matching expansion rule",
            }
        )

    return used_terms, audit_rows


def minmax(values: list[float]) -> list[float]:
    if not values:
        return []
    lo = min(values)
    hi = max(values)
    if hi == lo:
        return [1.0 for _ in values]
    return [(v - lo) / (hi - lo) for v in values]


def run_expanded_hybrid(core_queries: pd.DataFrame, examples: pd.DataFrame) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    warnings: list[str] = []
    try:
        import hybrid_search
        from vector_search import load_index

        model, index, records = load_index()
        metadata_df = hybrid_search.load_full_metadata(str(METADATA_PATH))
        metadata_lookup = hybrid_search.build_metadata_lookup(metadata_df)
        term_index = hybrid_search.build_term_index(metadata_df)

        old_final_k = getattr(hybrid_search, "FINAL_K", None)
        old_candidate_k = getattr(hybrid_search, "CANDIDATE_K", None)
        hybrid_search.FINAL_K = TOP_K
        hybrid_search.CANDIDATE_K = max(int(old_candidate_k or TOP_K), 150)

        result_rows: list[dict[str, Any]] = []
        audit_rows: list[dict[str, Any]] = []
        try:
            for _, qrow in core_queries.iterrows():
                q = qrow.to_dict()
                query_id = clean(q.get("query_id"))
                query_text = clean(q.get("query_text"))
                query_group = clean(q.get("query_group"))
                terms, audit = select_expansion_terms(q, examples)
                audit_rows.extend(audit)
                expanded_query = query_text if not terms else f"{query_text} {' '.join(terms)}"
                _, results = hybrid_search.hybrid_search(
                    query=expanded_query,
                    model=model,
                    index=index,
                    records=records,
                    metadata_lookup=metadata_lookup,
                    term_index=term_index,
                )
                raw_scores = [safe_float(r.get("final_score", r.get("score"))) for r in results[:TOP_K]]
                norms = minmax(raw_scores)
                for rank, (item, norm) in enumerate(zip(results[:TOP_K], norms), start=1):
                    result_rows.append(
                        {
                            "query_id": query_id,
                            "query_text": query_text,
                            "query_group": query_group,
                            "baseline_name": "hybrid_query_expansion",
                            "rank": rank,
                            "doc_id": clean(item.get("doc_id")),
                            "title": clean(item.get("title")),
                            "score_raw": safe_float(item.get("final_score", item.get("score"))),
                            "score_normalized": norm,
                            "vector_score": safe_float(item.get("vector_score", item.get("score"))),
                            "metadata_delta": safe_float(item.get("metadata_delta", item.get("kg_bonus"))),
                            "kg_score": safe_float(item.get("kg_score")),
                            "intent_adjustment": safe_float(item.get("intent_adjustment")),
                            "expansion_terms": "; ".join(terms),
                            "expanded_query": expanded_query,
                            "expansion_source": "outputs/query_expansion_examples.csv",
                            "notes": "experimental wrapper; original runtime unchanged",
                        }
                    )
        finally:
            if old_final_k is not None:
                hybrid_search.FINAL_K = old_final_k
            if old_candidate_k is not None:
                hybrid_search.CANDIDATE_K = old_candidate_k

        return result_rows, audit_rows, warnings
    except Exception as exc:
        warnings.append(f"Failed to run expanded hybrid: {exc}")
        warnings.append(traceback.format_exc(limit=5))
        return [], [], warnings


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        fieldnames = []
        for row in rows:
            for key in row:
                if key not in fieldnames:
                    fieldnames.append(key)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})


def load_judgments() -> dict[str, dict[str, int]]:
    df = pd.read_csv(JUDGMENT_PATH)
    out: dict[str, dict[str, int]] = defaultdict(dict)
    for _, row in df.iterrows():
        out[clean(row.get("query_id"))][clean(row.get("doc_id"))] = int(safe_float(row.get("relevance_label"), 0))
    return out


def load_results(path: Path, method: str, query_group_lookup: dict[str, str]) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    df = pd.read_csv(path)
    rows = []
    for _, row in df.iterrows():
        rows.append(
            {
                "method": method,
                "query_id": clean(row.get("query_id")),
                "query_text": clean(row.get("query_text") or row.get("query")),
                "query_group": clean(row.get("query_group")) or query_group_lookup.get(clean(row.get("query_id")), ""),
                "rank": int(safe_float(row.get("rank"), 999)),
                "doc_id": clean(row.get("doc_id")),
                "title": clean(row.get("title")),
                "score": safe_float(row.get("score_raw", row.get("final_score", row.get("score", 0.0)))),
            }
        )
    rows.sort(key=lambda r: (r["query_id"], r["rank"]))
    return rows


def dcg(labels: list[int], k: int) -> float:
    score = 0.0
    for i, rel in enumerate(labels[:k], start=1):
        gain = (2 ** rel) - 1
        score += gain / math.log2(i + 1)
    return score


def average_precision(binary_labels: list[int], total_relevant: int) -> float:
    if total_relevant <= 0:
        return 0.0
    hits = 0
    score = 0.0
    for idx, rel in enumerate(binary_labels, start=1):
        if rel > 0:
            hits += 1
            score += hits / idx
    return score / total_relevant


def query_metrics(rows: list[dict[str, Any]], judgments: dict[str, dict[str, int]], query_id: str) -> dict[str, float]:
    qrels = judgments.get(query_id, {})
    ranked = sorted(rows, key=lambda r: int(r["rank"]))[:TOP_K]
    labels = [int(qrels.get(r["doc_id"], 0)) for r in ranked]
    binary = [1 if rel > 0 else 0 for rel in labels]
    relevant_docs = [doc for doc, rel in qrels.items() if rel > 0]
    total_rel = len(relevant_docs)
    ideal_labels = sorted(qrels.values(), reverse=True)

    p1 = sum(binary[:1]) / 1 if ranked else 0.0
    p5 = sum(binary[:5]) / 5 if ranked else 0.0
    recall5 = sum(binary[:5]) / total_rel if total_rel else 0.0
    recall10 = sum(binary[:10]) / total_rel if total_rel else 0.0
    mrr = 0.0
    for i, rel in enumerate(binary, start=1):
        if rel > 0:
            mrr = 1.0 / i
            break
    ndcg5 = dcg(labels, 5) / dcg(ideal_labels, 5) if dcg(ideal_labels, 5) > 0 else 0.0
    ndcg10 = dcg(labels, 10) / dcg(ideal_labels, 10) if dcg(ideal_labels, 10) > 0 else 0.0
    ap = average_precision(binary, total_rel)
    return {
        "P@1": p1,
        "P@5": p5,
        "Recall@5": recall5,
        "Recall@10": recall10,
        "MRR": mrr,
        "nDCG@5": ndcg5,
        "nDCG@10": ndcg10,
        "MAP": ap,
    }


def compute_all_metrics(method_results: dict[str, list[dict[str, Any]]], core_queries: pd.DataFrame) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    judgments = load_judgments()
    query_meta = {
        clean(row.get("query_id")): {
            "query_text": clean(row.get("query_text")),
            "query_group": clean(row.get("query_group")),
        }
        for _, row in core_queries.iterrows()
    }
    by_query_rows: list[dict[str, Any]] = []
    for method, rows in method_results.items():
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in rows:
            grouped[row["query_id"]].append(row)
        for qid, meta in query_meta.items():
            metrics = query_metrics(grouped.get(qid, []), judgments, qid)
            by_query_rows.append(
                {
                    "method": method,
                    "query_id": qid,
                    "query_text": meta["query_text"],
                    "query_group": meta["query_group"],
                    **metrics,
                }
            )

    summary_rows: list[dict[str, Any]] = []
    by_group_rows: list[dict[str, Any]] = []
    for method in method_results.keys():
        m_rows = [r for r in by_query_rows if r["method"] == method]
        summary_rows.append({"method": method, "n_queries": len(m_rows), **mean_metrics(m_rows)})
        groups = sorted({r["query_group"] for r in m_rows})
        for group in groups:
            g_rows = [r for r in m_rows if r["query_group"] == group]
            by_group_rows.append({"method": method, "query_group": group, "n_queries": len(g_rows), **mean_metrics(g_rows)})
    return summary_rows, by_query_rows, by_group_rows


def mean_metrics(rows: list[dict[str, Any]]) -> dict[str, float]:
    out = {}
    for metric in METRIC_COLUMNS:
        vals = [safe_float(r.get(metric)) for r in rows]
        out[metric] = sum(vals) / len(vals) if vals else 0.0
    return out


def metric_delta(by_query_rows: list[dict[str, Any]], metric: str = "nDCG@10") -> list[dict[str, Any]]:
    by_q: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in by_query_rows:
        by_q[row["query_id"]][row["method"]] = row
    deltas = []
    for qid, methods in by_q.items():
        if "hybrid" not in methods or "hybrid_query_expansion" not in methods:
            continue
        h = methods["hybrid"]
        qe = methods["hybrid_query_expansion"]
        deltas.append(
            {
                "query_id": qid,
                "query_text": qe["query_text"],
                "query_group": qe["query_group"],
                "hybrid": safe_float(h.get(metric)),
                "hybrid_query_expansion": safe_float(qe.get(metric)),
                "delta": safe_float(qe.get(metric)) - safe_float(h.get(metric)),
            }
        )
    return sorted(deltas, key=lambda r: r["delta"], reverse=True)


def create_figure(summary_rows: list[dict[str, Any]]) -> None:
    FIGURE_PATH.parent.mkdir(parents=True, exist_ok=True)
    methods = [m for m in ["vector_metadata", "hybrid", "hybrid_query_expansion"] if any(r["method"] == m for r in summary_rows)]
    metrics = ["P@1", "Recall@10", "MRR", "nDCG@10", "MAP"]
    lookup = {r["method"]: r for r in summary_rows}
    x = list(range(len(metrics)))
    width = 0.24
    colors = {"vector_metadata": "#6b7280", "hybrid": "#2563eb", "hybrid_query_expansion": "#d97706"}
    plt.figure(figsize=(10, 5.5))
    for idx, method in enumerate(methods):
        offset = (idx - (len(methods) - 1) / 2) * width
        values = [safe_float(lookup[method].get(metric)) for metric in metrics]
        bars = plt.bar([i + offset for i in x], values, width=width, label=method, color=colors.get(method, None))
        for bar, value in zip(bars, values):
            plt.text(bar.get_x() + bar.get_width() / 2, value + 0.015, f"{value:.3f}", ha="center", va="bottom", fontsize=8, rotation=90)
    plt.xticks(x, metrics)
    plt.ylim(0, 1.05)
    plt.ylabel("Metric value")
    plt.title("Ontology-based query expansion experiment")
    plt.grid(axis="y", alpha=0.25)
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURE_PATH, dpi=200)
    plt.close()


def md_table(rows: list[dict[str, Any]], columns: list[str], max_rows: int | None = None) -> str:
    rows = rows[:max_rows] if max_rows else rows
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for row in rows:
        vals = []
        for col in columns:
            value = row.get(col, "")
            if isinstance(value, float):
                value = f"{value:.4f}"
            vals.append(str(value).replace("|", "/").replace("\n", " "))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def write_report(
    summary_rows: list[dict[str, Any]],
    by_group_rows: list[dict[str, Any]],
    by_query_rows: list[dict[str, Any]],
    audit_rows: list[dict[str, Any]],
    warnings: list[str],
) -> None:
    lookup = {r["method"]: r for r in summary_rows}
    hybrid = lookup.get("hybrid", {})
    qe = lookup.get("hybrid_query_expansion", {})
    deltas = metric_delta(by_query_rows, "nDCG@10")
    improved = [d for d in deltas if d["delta"] > 1e-9]
    worsened = [d for d in deltas if d["delta"] < -1e-9]
    unchanged = [d for d in deltas if abs(d["delta"]) <= 1e-9]
    used_terms = [r for r in audit_rows if clean(r.get("used")) == "true"]
    used_term_count = len(used_terms)
    queries_with_terms = len({r["query_id"] for r in used_terms})
    qe_better = safe_float(qe.get("nDCG@10")) - safe_float(hybrid.get("nDCG@10"))
    if qe_better > 0.005:
        conclusion = "Query expansion có cải thiện trung bình nhẹ trên nDCG@10 so với hybrid trong cấu hình thử nghiệm này, nhưng vẫn cần xem by-query vì hiệu ứng không đồng đều."
    elif qe_better < -0.005:
        conclusion = "Query expansion làm giảm nDCG@10 trung bình so với hybrid trong cấu hình thử nghiệm này; nên giữ như future work và cần lọc/tuning thêm."
    else:
        conclusion = "Query expansion cho kết quả gần tương đương hybrid về trung bình, nhưng hiệu ứng theo query/group có thể mixed."

    group_compare = []
    for group in sorted({r["query_group"] for r in by_group_rows}):
        h = next((r for r in by_group_rows if r["method"] == "hybrid" and r["query_group"] == group), None)
        q = next((r for r in by_group_rows if r["method"] == "hybrid_query_expansion" and r["query_group"] == group), None)
        if h and q:
            group_compare.append(
                {
                    "query_group": group,
                    "hybrid_nDCG@10": safe_float(h.get("nDCG@10")),
                    "query_expansion_nDCG@10": safe_float(q.get("nDCG@10")),
                    "delta_nDCG@10": safe_float(q.get("nDCG@10")) - safe_float(h.get("nDCG@10")),
                    "hybrid_MAP": safe_float(h.get("MAP")),
                    "query_expansion_MAP": safe_float(q.get("MAP")),
                }
            )

    report = f"""# Query expansion experiment analysis

Generated at: `2026-05-29`

## 1. Mục tiêu

Thí nghiệm này đánh giá ontology-based query expansion như một cấu hình mở rộng tên `hybrid_query_expansion`. Cấu hình này chỉ dùng để kiểm tra tiềm năng của query expansion trên core evaluation, không thay thế hybrid final và không chỉnh sửa runtime/scoring hiện có.

## 2. Dữ liệu và phương pháp

- Query set: `data/eval/final_query_set_core.csv` với 28 queries.
- Relevance judgments: `data/eval/relevance_judgments_core.csv`.
- Baseline so sánh: `vector_metadata`, `hybrid`, và `hybrid_query_expansion`; nếu có file hiện hữu thì report cũng tính thêm `hybrid_candidate_fusion`.
- Expansion source: `outputs/query_expansion_examples.csv` với các ví dụ alias/entity expansion hiện có.
- Cách tạo query: **Cách A** - `expanded_query = original_query + selected_expansion_terms`.
- Re-rank: wrapper gọi `hybrid_search.hybrid_search()` với expanded query, dùng runtime scoring hiện có. Script chỉ tạm set `FINAL_K=10` và `CANDIDATE_K>=150` trong process đang chạy, rồi restore lại; không sửa source code.
- Output Top-10 được ghi vào `data/eval/results/baseline_hybrid_query_expansion_core.csv`.

Số query có ít nhất một expansion term được dùng: **{queries_with_terms}/28**. Tổng số expansion terms được dùng: **{used_term_count}**.

## 3. Expansion rules

Expansion được chọn theo rule có kiểm soát:

- Disease -> dùng alias, pathogen, symptom, prevention/treatment nếu query có disease/entity liên quan.
- Taxon -> dùng scientific name, common name hoặc Vietnamese alias nếu query có taxon/species liên quan.
- Location -> dùng alias hoặc parent location, nhưng lọc location quá rộng nếu query không có local intent.
- Production mode/topic -> dùng hatchery, larval rearing, biosecurity, farming system nếu query có mode/topic tương ứng.

Giới hạn: disease tối đa {DISEASE_MAX_TERMS}, taxon tối đa {TAXON_MAX_TERMS}, location tối đa {LOCATION_MAX_TERMS}, production/topic tối đa {MODE_MAX_TERMS}, tổng tối đa {TOTAL_MAX_TERMS} terms/query. Các term quá chung như `aquaculture`, `fisheries`, `disease`, `shrimp` bị lọc để giảm query drift.

## 4. Metrics summary

{md_table(summary_rows, ["method", "n_queries", *METRIC_COLUMNS])}

So với hybrid, `hybrid_query_expansion` có delta nDCG@10 = **{qe_better:.4f}**. {conclusion}

## 5. Results by query group

{md_table(group_compare, ["query_group", "hybrid_nDCG@10", "query_expansion_nDCG@10", "delta_nDCG@10", "hybrid_MAP", "query_expansion_MAP"])}

Nhóm có cải thiện/giảm được diễn giải theo delta nDCG@10 ở bảng trên. Vì expansion được áp dụng theo rule và query gốc khác nhau về entity coverage, kết quả theo group có thể không đồng đều.

## 6. Query-level examples

Query cải thiện nhiều nhất theo nDCG@10:

{md_table(improved[:3], ["query_id", "query_text", "query_group", "hybrid", "hybrid_query_expansion", "delta"]) if improved else "Không có query cải thiện theo nDCG@10."}

Query giảm nhiều nhất theo nDCG@10:

{md_table(list(reversed(worsened[-3:])), ["query_id", "query_text", "query_group", "hybrid", "hybrid_query_expansion", "delta"]) if worsened else "Không có query giảm theo nDCG@10."}

Query không đổi:

{md_table(unchanged[:2], ["query_id", "query_text", "query_group", "hybrid", "hybrid_query_expansion", "delta"]) if unchanged else "Không có query không đổi tuyệt đối theo nDCG@10."}

Các query cải thiện thường là trường hợp expansion giúp nối alias/entity như disease alias, scientific name hoặc location/mode term. Các query giảm thường là dấu hiệu query drift: term mở rộng làm tăng trọng số cho tài liệu gần nghĩa nhưng lệch intent gốc.

## 7. Error analysis

- Expansion quá chung có thể kéo candidate về tài liệu tổng quan thay vì tài liệu đúng intent. Script đã lọc các term như `aquaculture`, `fisheries`, `disease`, `shrimp`, nhưng vẫn có thể còn term rộng như prevention/surveillance.
- Disease expansion có thể kéo sang tài liệu bệnh rộng hơn hoặc pathogen-focused nếu pathogen có mặt trong nhiều bệnh khác nhau.
- Location parent như Vietnam có thể làm mất độ cụ thể của query địa phương nếu dùng không kiểm soát.
- Production/topic expansion như hatchery/biosecurity có thể làm nhiễu nếu query thật ra tập trung disease hoặc location.
- Vì Cách A nối term vào query text, expanded query có thể dài hơn và làm thay đổi embedding direction. Multi-query pooling có thể là hướng an toàn hơn cho future work.

## 8. Kết luận

{conclusion} Cấu hình này nên được trình bày như experiment/prototype hoặc future work, không nên thay thế hybrid final trong báo cáo chính. Để đưa query expansion thành đóng góp chính, cần tuning rule, kiểm soát weight của term mở rộng, và đánh giá ổn định hơn trên nhiều query hơn.

## 9. Đoạn có thể chèn vào báo cáo

Đề tài bổ sung một thí nghiệm mở rộng nhằm đánh giá ontology-based query expansion trên 28 truy vấn core. Với mỗi truy vấn, hệ thống chọn một số expansion terms có kiểm soát từ các alias/entity/fact hiện có, sau đó tạo expanded query và gọi lại hybrid runtime để lấy Top-10. Kết quả được so sánh với `vector_metadata` và `hybrid` bằng các metric P@1, P@5, Recall@5, Recall@10, MRR, nDCG@5, nDCG@10 và MAP. Trên thiết lập này, `hybrid_query_expansion` đạt nDCG@10 = {safe_float(qe.get("nDCG@10")):.4f}, so với hybrid = {safe_float(hybrid.get("nDCG@10")):.4f}. Kết quả cho thấy query expansion có hiệu ứng {("tích cực nhẹ" if qe_better > 0.005 else "tiêu cực/mixed" if qe_better < -0.005 else "gần tương đương")} ở mức trung bình, nhưng vẫn có query cải thiện và query suy giảm riêng lẻ. Vì vậy, query expansion được xem là cấu hình experimental/future work, không thay thế hybrid final. Nguyên nhân chính là expansion có thể giúp tăng coverage alias/entity, nhưng cũng có nguy cơ query drift nếu term mở rộng quá rộng hoặc lệch intent.

## 10. Caveats

- Đây là thí nghiệm mở rộng, không thay hybrid final.
- Expansion rules vẫn cần manual review và tuning thêm.
- Query expansion có thể gây query drift.
- Cấu hình hiện tại dùng expanded query text; multi-query candidate pooling có thể ổn định hơn nhưng chưa được đưa vào final runtime.
- Chưa có kiểm định thống kê riêng cho query expansion.
- Không được viết rằng ontology expansion luôn tốt hơn query gốc.

## 11. Safety confirmation

- Không sửa runtime/scoring.
- Không sửa `hybrid_search.py`, `kg_runtime.py`, `vector_search.py`, `run_core_baselines.py`.
- Không sửa `app_streamlit.py`.
- Không sửa ontology/metadata.
- Không sửa query set/relevance judgments.
- Không sửa baseline results/metrics cũ.
- Chỉ tạo output mới cho experiment.

## 12. Outputs

- `experiments/run_query_expansion_experiment.py`
- `data/eval/results/baseline_hybrid_query_expansion_core.csv`
- `data/eval/metrics/query_expansion_metrics_summary.csv`
- `data/eval/metrics/query_expansion_metrics_by_query.csv`
- `data/eval/metrics/query_expansion_metrics_by_group.csv`
- `outputs/query_expansion_experiment_analysis.md`
- `outputs/query_expansion_applied_terms.csv`
- `outputs/figures/fig_query_expansion_experiment_summary.png`

## 13. Warnings

{warnings_md(warnings)}
"""
    REPORT_PATH.write_text(report, encoding="utf-8")


def warnings_md(warnings: list[str]) -> str:
    if not warnings:
        return "Không có warning nghiêm trọng."
    return "\n".join(f"- {w.replace(chr(10), ' ')}" for w in warnings[:8])


def main() -> None:
    core_queries = pd.read_csv(CORE_QUERY_PATH)
    examples = pd.read_csv(EXPANSION_EXAMPLES_PATH)
    query_group_lookup = {clean(r.get("query_id")): clean(r.get("query_group")) for _, r in core_queries.iterrows()}

    result_rows, audit_rows, warnings = run_expanded_hybrid(core_queries, examples)
    if not result_rows:
        raise RuntimeError("hybrid_query_expansion produced no rows; aborting without writing metrics.")

    result_fields = [
        "query_id", "query_text", "query_group", "baseline_name", "rank", "doc_id", "title",
        "score_raw", "score_normalized", "vector_score", "metadata_delta", "kg_score",
        "intent_adjustment", "expansion_terms", "expanded_query", "expansion_source", "notes",
    ]
    audit_fields = [
        "query_id", "query_text", "query_group", "detected_entity_or_intent", "expansion_term",
        "expansion_type", "source_field", "used", "reason",
    ]
    write_csv(RESULT_PATH, result_rows, result_fields)
    write_csv(APPLIED_TERMS_PATH, audit_rows, audit_fields)

    method_results = {}
    for method, path in METHOD_FILES.items():
        rows = load_results(path, method, query_group_lookup)
        if rows:
            method_results[method] = rows

    summary_rows, by_query_rows, by_group_rows = compute_all_metrics(method_results, core_queries)
    write_csv(SUMMARY_PATH, summary_rows, ["method", "n_queries", *METRIC_COLUMNS])
    write_csv(BY_QUERY_PATH, by_query_rows, ["method", "query_id", "query_text", "query_group", *METRIC_COLUMNS])
    write_csv(BY_GROUP_PATH, by_group_rows, ["method", "query_group", "n_queries", *METRIC_COLUMNS])
    create_figure(summary_rows)
    write_report(summary_rows, by_group_rows, by_query_rows, audit_rows, warnings)

    used_terms = [r for r in audit_rows if clean(r.get("used")) == "true"]
    print(f"[OK] queries={len(core_queries)}")
    print(f"[OK] result_rows={len(result_rows)}")
    print(f"[OK] used_expansion_terms={len(used_terms)}")
    print(f"[OK] wrote {RESULT_PATH.relative_to(PROJECT_ROOT)}")
    print(f"[OK] wrote {SUMMARY_PATH.relative_to(PROJECT_ROOT)}")
    print(f"[OK] wrote {BY_QUERY_PATH.relative_to(PROJECT_ROOT)}")
    print(f"[OK] wrote {BY_GROUP_PATH.relative_to(PROJECT_ROOT)}")
    print(f"[OK] wrote {APPLIED_TERMS_PATH.relative_to(PROJECT_ROOT)}")
    print(f"[OK] wrote {REPORT_PATH.relative_to(PROJECT_ROOT)}")
    print(f"[OK] wrote {FIGURE_PATH.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
