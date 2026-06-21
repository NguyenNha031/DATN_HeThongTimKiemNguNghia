from __future__ import annotations

import csv
import math
import re
import sys
import traceback
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
BASELINE_HYBRID_PATH = PROJECT_ROOT / "data" / "eval" / "results" / "baseline_hybrid_core.csv"
METADATA_PATH = PROJECT_ROOT / "data" / "metadata" / "document_metadata_cleaned.xlsx"
KG_COMPONENT_PATH = PROJECT_ROOT / "outputs" / "kg_score_component_analysis.csv"
KG_COMPONENT_MD_PATH = PROJECT_ROOT / "outputs" / "kg_score_component_analysis.md"
QUERY_PROFILE_PATH = PROJECT_ROOT / "outputs" / "query_understanding_profiles.csv"

OUT_DIR = PROJECT_ROOT / "outputs"
FIG_DIR = OUT_DIR / "figures"
SUMMARY_PATH = OUT_DIR / "explanation_quality_summary.csv"
BY_GROUP_PATH = OUT_DIR / "explanation_quality_by_group.csv"
BY_QUERY_PATH = OUT_DIR / "explanation_quality_by_query.csv"
EXAMPLES_PATH = OUT_DIR / "explanation_quality_examples.csv"
REPORT_PATH = OUT_DIR / "explanation_quality_report.md"
FIGURE_PATH = FIG_DIR / "fig_explanation_quality_summary.png"

TOP_K = 10


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        if isinstance(value, float) and math.isnan(value):
            return default
        text = str(value).strip()
        if not text:
            return default
        return float(text)
    except Exception:
        return default


def safe_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    text = str(value).strip().lower()
    return text in {"true", "1", "yes", "y"}


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and math.isnan(value):
        return ""
    return str(value).strip()


def first_nonempty(row: dict[str, Any], keys: list[str]) -> str:
    for key in keys:
        value = clean_text(row.get(key))
        if value:
            return value
    return ""


def read_csv_if_exists(path: Path) -> pd.DataFrame:
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def load_relevance_lookup() -> dict[tuple[str, str], str]:
    df = read_csv_if_exists(JUDGMENT_PATH)
    if df.empty:
        return {}
    label_col = None
    for candidate in ["relevance_label", "label", "relevance", "rel"]:
        if candidate in df.columns:
            label_col = candidate
            break
    if not label_col or "query_id" not in df.columns or "doc_id" not in df.columns:
        return {}
    return {
        (str(row["query_id"]), str(row["doc_id"])): clean_text(row[label_col])
        for _, row in df.iterrows()
    }


def load_kg_component_lookup() -> dict[tuple[str, str], dict[str, Any]]:
    df = read_csv_if_exists(KG_COMPONENT_PATH)
    if df.empty or "query_id" not in df.columns or "doc_id" not in df.columns:
        return {}
    return {
        (str(row["query_id"]), str(row["doc_id"])): row.to_dict()
        for _, row in df.iterrows()
    }


def split_evidence_parts(text: str) -> list[str]:
    if not text:
        return []
    parts = re.split(r";|\n|\|", text)
    return [p.strip() for p in parts if p and p.strip()]


def contains_any(text: str, patterns: list[str]) -> bool:
    low = text.lower()
    return any(p.lower() in low for p in patterns)


def runtime_rows(core_queries: pd.DataFrame) -> tuple[list[dict[str, Any]], str, list[str]]:
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

        rows: list[dict[str, Any]] = []
        try:
            for _, qrow in core_queries.iterrows():
                query_id = clean_text(qrow.get("query_id"))
                query_text = clean_text(qrow.get("query_text"))
                query_group = clean_text(qrow.get("query_group"))
                detected, results = hybrid_search.hybrid_search(
                    query=query_text,
                    model=model,
                    index=index,
                    records=records,
                    metadata_lookup=metadata_lookup,
                    term_index=term_index,
                )
                detected_summary = {
                    key: [clean_text(item.get("canonical") or item.get("label") or item) for item in (vals or [])]
                    for key, vals in (detected or {}).items()
                }
                for rank, item in enumerate(results[:TOP_K], start=1):
                    explanation_text = first_nonempty(
                        item,
                        ["explanation", "kg_explanation", "score_explanation", "explanation_short"],
                    )
                    rows.append(
                        {
                            "source_mode": "runtime_recomputed",
                            "query_id": query_id,
                            "query_text": query_text,
                            "query_group": query_group,
                            "rank": rank,
                            "doc_id": clean_text(item.get("doc_id")),
                            "title": clean_text(item.get("title")),
                            "final_score": safe_float(item.get("final_score", item.get("score"))),
                            "vector_score": safe_float(item.get("vector_score", item.get("score"))),
                            "metadata_delta": safe_float(item.get("metadata_delta", item.get("kg_bonus"))),
                            "kg_score": safe_float(item.get("kg_score")),
                            "intent_adjustment": safe_float(item.get("intent_adjustment")),
                            "explanation_text": explanation_text,
                            "kg_explanation": clean_text(item.get("kg_explanation")),
                            "bonus_breakdown": clean_text(item.get("bonus_breakdown")),
                            "penalty_breakdown": clean_text(item.get("penalty_breakdown")),
                            "kg_bonus_breakdown": clean_text(item.get("kg_bonus_breakdown")),
                            "kg_penalty_breakdown": clean_text(item.get("kg_penalty_breakdown")),
                            "match_disease": bool(item.get("match_disease", False)),
                            "match_species": bool(item.get("match_species", False)),
                            "match_location": bool(item.get("match_location", False)),
                            "match_mode": bool(item.get("match_mode", False)),
                            "matched_entities": clean_text(item.get("matched_entities")),
                            "kg_direct_match": safe_float(item.get("kg_direct_match")),
                            "kg_relation_match": safe_float(item.get("kg_relation_match")),
                            "kg_context_match": safe_float(item.get("kg_context_match")),
                            "detected_entities": clean_text(detected_summary),
                        }
                    )
        finally:
            if old_final_k is not None:
                hybrid_search.FINAL_K = old_final_k
            if old_candidate_k is not None:
                hybrid_search.CANDIDATE_K = old_candidate_k

        return rows, "runtime_recomputed", warnings
    except Exception as exc:
        warnings.append(f"Runtime recomputation failed; fallback to baseline/diagnostic CSV. Error: {exc}")
        warnings.append(traceback.format_exc(limit=3))
        return [], "runtime_failed", warnings


def fallback_rows(core_queries: pd.DataFrame, kg_lookup: dict[tuple[str, str], dict[str, Any]]) -> list[dict[str, Any]]:
    baseline = read_csv_if_exists(BASELINE_HYBRID_PATH)
    if baseline.empty:
        return []
    q_lookup = {
        clean_text(row.get("query_id")): row.to_dict()
        for _, row in core_queries.iterrows()
    }
    rows: list[dict[str, Any]] = []
    for _, brow in baseline.iterrows():
        qid = clean_text(brow.get("query_id"))
        doc_id = clean_text(brow.get("doc_id"))
        qrow = q_lookup.get(qid, {})
        kg = kg_lookup.get((qid, doc_id), {})
        explanation_text = first_nonempty(
            kg,
            ["kg_explanation_evidence", "explanation", "kg_component_notes"],
        )
        rows.append(
            {
                "source_mode": "baseline_plus_kg_diagnostic_fallback",
                "query_id": qid,
                "query_text": clean_text(brow.get("query_text") or qrow.get("query_text")),
                "query_group": clean_text(qrow.get("query_group")),
                "rank": int(safe_float(brow.get("rank"), 0)),
                "doc_id": doc_id,
                "title": clean_text(brow.get("title")),
                "final_score": safe_float(brow.get("score_raw")),
                "vector_score": "",
                "metadata_delta": "",
                "kg_score": safe_float(kg.get("kg_score")),
                "intent_adjustment": safe_float(kg.get("intent_adjustment")),
                "explanation_text": explanation_text,
                "kg_explanation": clean_text(kg.get("kg_explanation_evidence")),
                "bonus_breakdown": "",
                "penalty_breakdown": "",
                "kg_bonus_breakdown": "",
                "kg_penalty_breakdown": "",
                "match_disease": False,
                "match_species": False,
                "match_location": False,
                "match_mode": False,
                "matched_entities": "",
                "kg_direct_match": safe_float(kg.get("kg_direct_fact_score_diagnostic")),
                "kg_relation_match": safe_float(kg.get("kg_relation_score_diagnostic")),
                "kg_context_match": "",
                "detected_entities": "",
            }
        )
    return rows


def augment_and_flag_rows(
    rows: list[dict[str, Any]],
    relevance: dict[tuple[str, str], str],
    kg_lookup: dict[tuple[str, str], dict[str, Any]],
) -> list[dict[str, Any]]:
    entity_patterns = [
        "match disease",
        "match species",
        "match location",
        "match mode",
        "aboutDisease",
        "aboutTaxon",
        "aboutLocation",
        "documentProductionMode",
        "affectsTaxon",
        "causedBy",
        "isFoundIn",
        "recommendedPrevention",
        "recommendedTreatment",
        "pathogen",
        "prevention",
        "treatment",
        "symptom",
    ]
    metadata_patterns = [
        "metadata:",
        "match disease",
        "match species",
        "match location",
        "match mode",
        "disease-species synergy",
        "species-location synergy",
    ]
    kg_patterns = [
        "kg direct match",
        "kg relation match",
        "kg context match",
        "aboutDisease",
        "aboutTaxon",
        "aboutLocation",
        "documentProductionMode",
        "affectsTaxon",
        "causedBy",
        "isFoundIn",
        "recommendedPrevention",
        "recommendedTreatment",
        "pathogen",
    ]
    fact_relation_patterns = [
        "aboutDisease",
        "aboutTaxon",
        "aboutLocation",
        "documentProductionMode",
        "affectsTaxon",
        "causedBy",
        "isFoundIn",
        "recommendedPrevention",
        "recommendedTreatment",
    ]

    for row in rows:
        key = (clean_text(row.get("query_id")), clean_text(row.get("doc_id")))
        kg = kg_lookup.get(key, {})
        row["relevance_label"] = relevance.get(key, "")
        row["kg_diag_has_direct_fact_evidence"] = safe_bool(kg.get("has_direct_fact_evidence"))
        row["kg_diag_has_relation_evidence"] = safe_bool(kg.get("has_relation_evidence"))
        row["kg_diag_has_explanation_evidence"] = safe_bool(kg.get("has_explanation_evidence"))
        row["kg_direct_fact_evidence"] = clean_text(kg.get("kg_direct_fact_evidence"))
        row["kg_relation_evidence"] = clean_text(kg.get("kg_relation_evidence"))
        row["kg_explanation_evidence"] = clean_text(kg.get("kg_explanation_evidence"))

        text_blob = " ; ".join(
            clean_text(row.get(k))
            for k in [
                "explanation_text",
                "kg_explanation",
                "bonus_breakdown",
                "penalty_breakdown",
                "kg_bonus_breakdown",
                "kg_penalty_breakdown",
                "kg_direct_fact_evidence",
                "kg_relation_evidence",
                "kg_explanation_evidence",
                "matched_entities",
            ]
        )
        evidence_parts = split_evidence_parts(text_blob)
        metadata_delta = safe_float(row.get("metadata_delta"))
        kg_score = safe_float(row.get("kg_score"))
        kg_direct = safe_float(row.get("kg_direct_match")) or safe_float(kg.get("kg_direct_fact_score_diagnostic"))
        kg_relation = safe_float(row.get("kg_relation_match")) or safe_float(kg.get("kg_relation_score_diagnostic"))
        kg_context = safe_float(row.get("kg_context_match"))

        has_explanation = bool(clean_text(row.get("explanation_text")) or clean_text(row.get("kg_explanation")))
        has_metadata_evidence = (
            metadata_delta > 0
            or bool(clean_text(row.get("bonus_breakdown")))
            or contains_any(text_blob, metadata_patterns)
        )
        has_kg_evidence = (
            kg_score > 0
            or kg_direct > 0
            or kg_relation > 0
            or kg_context > 0
            or bool(clean_text(row.get("kg_explanation")))
            or row["kg_diag_has_explanation_evidence"]
            or contains_any(text_blob, kg_patterns)
        )
        has_kg_relation_or_fact = (
            kg_direct > 0
            or kg_relation > 0
            or row["kg_diag_has_direct_fact_evidence"]
            or row["kg_diag_has_relation_evidence"]
            or contains_any(text_blob, fact_relation_patterns)
        )
        has_entity_match = (
            bool(row.get("match_disease"))
            or bool(row.get("match_species"))
            or bool(row.get("match_location"))
            or bool(row.get("match_mode"))
            or has_metadata_evidence
            or has_kg_relation_or_fact
            or contains_any(text_blob, entity_patterns)
        )

        row["has_explanation"] = has_explanation
        row["has_entity_match"] = has_entity_match
        row["has_metadata_evidence"] = has_metadata_evidence
        row["has_kg_evidence"] = has_kg_evidence
        row["has_kg_relation_or_fact"] = has_kg_relation_or_fact
        row["explanation_length"] = len(clean_text(row.get("explanation_text")))
        row["evidence_count"] = len(evidence_parts)
        row["evidence_summary"] = "; ".join(evidence_parts[:5])
    return rows


def rate(values: list[Any]) -> float:
    if not values:
        return 0.0
    return float(sum(1 for v in values if bool(v)) / len(values))


def mean(values: list[Any]) -> float:
    nums = [safe_float(v) for v in values if v != "" and v is not None]
    if not nums:
        return 0.0
    return float(sum(nums) / len(nums))


def aggregate_scope(rows: list[dict[str, Any]], scope: str, top_k: int, notes: str) -> dict[str, Any]:
    by_query: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_query[clean_text(row.get("query_id"))].append(row)
    top1_rows = [sorted(qrows, key=lambda x: int(safe_float(x.get("rank"), 999)))[0] for qrows in by_query.values() if qrows]
    return {
        "scope": scope,
        "n_queries": len(by_query),
        "n_rows": len(rows),
        "top_k": top_k,
        "has_explanation_rate": rate([r["has_explanation"] for r in rows]),
        "top1_has_explanation_rate": rate([r["has_explanation"] for r in top1_rows]),
        "query_has_any_explanation_rate": rate([any(r["has_explanation"] for r in qrows) for qrows in by_query.values()]),
        "has_entity_match_rate": rate([r["has_entity_match"] for r in rows]),
        "has_metadata_evidence_rate": rate([r["has_metadata_evidence"] for r in rows]),
        "has_kg_evidence_rate": rate([r["has_kg_evidence"] for r in rows]),
        "has_kg_relation_or_fact_rate": rate([r["has_kg_relation_or_fact"] for r in rows]),
        "mean_explanation_length": mean([r["explanation_length"] for r in rows if r["has_explanation"]]),
        "mean_evidence_count": mean([r["evidence_count"] for r in rows if r["has_explanation"]]),
        "notes": notes,
    }


def aggregate_by_group(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[clean_text(row.get("query_group"))].append(row)
    out = []
    for group, grows in sorted(grouped.items()):
        summary = aggregate_scope(grows, group, TOP_K, "")
        out.append(
            {
                "query_group": group,
                "n_queries": summary["n_queries"],
                "n_rows": summary["n_rows"],
                "has_explanation_rate": summary["has_explanation_rate"],
                "top1_has_explanation_rate": summary["top1_has_explanation_rate"],
                "query_has_any_explanation_rate": summary["query_has_any_explanation_rate"],
                "has_entity_match_rate": summary["has_entity_match_rate"],
                "has_metadata_evidence_rate": summary["has_metadata_evidence_rate"],
                "has_kg_evidence_rate": summary["has_kg_evidence_rate"],
                "has_kg_relation_or_fact_rate": summary["has_kg_relation_or_fact_rate"],
                "mean_explanation_length": summary["mean_explanation_length"],
            }
        )
    return out


def aggregate_by_query(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[clean_text(row.get("query_id"))].append(row)
    out = []
    for qid, qrows in sorted(grouped.items()):
        sorted_rows = sorted(qrows, key=lambda x: int(safe_float(x.get("rank"), 999)))
        top1 = sorted_rows[0]
        out.append(
            {
                "query_id": qid,
                "query_text": clean_text(top1.get("query_text")),
                "query_group": clean_text(top1.get("query_group")),
                "n_rows": len(sorted_rows),
                "top1_doc_id": clean_text(top1.get("doc_id")),
                "top1_title": clean_text(top1.get("title")),
                "top1_has_explanation": bool(top1.get("has_explanation")),
                "top1_has_metadata_evidence": bool(top1.get("has_metadata_evidence")),
                "top1_has_kg_evidence": bool(top1.get("has_kg_evidence")),
                "top1_has_entity_match": bool(top1.get("has_entity_match")),
                "n_results_with_explanation": sum(1 for r in sorted_rows if r["has_explanation"]),
                "n_results_with_kg_evidence": sum(1 for r in sorted_rows if r["has_kg_evidence"]),
                "n_results_with_metadata_evidence": sum(1 for r in sorted_rows if r["has_metadata_evidence"]),
                "notes": "",
            }
        )
    return out


def relevance_aware_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        label = clean_text(row.get("relevance_label"))
        if label != "":
            grouped[label].append(row)
    out = []
    for label, lrows in sorted(grouped.items()):
        out.append(
            {
                "label": label,
                "n_rows": len(lrows),
                "has_explanation_rate": rate([r["has_explanation"] for r in lrows]),
                "has_metadata_evidence_rate": rate([r["has_metadata_evidence"] for r in lrows]),
                "has_kg_evidence_rate": rate([r["has_kg_evidence"] for r in lrows]),
            }
        )
    return out


def select_examples(rows: list[dict[str, Any]], limit: int = 12) -> list[dict[str, Any]]:
    priority_queries = ["DS_001", "LO_001", "LO_004", "BI_001", "HM_001", "SL_007"]
    good_candidates = [
        r
        for r in rows
        if r["has_explanation"] and r["has_entity_match"] and (r["has_metadata_evidence"] or r["has_kg_evidence"])
    ]
    partial_candidates = [
        r for r in rows if r["has_explanation"] and not (r["has_metadata_evidence"] and r["has_kg_evidence"])
    ]
    weak_candidates = [r for r in rows if not r["has_explanation"] or not r["has_entity_match"]]

    def sort_key(row: dict[str, Any]) -> tuple[int, int, float]:
        qid = clean_text(row.get("query_id"))
        priority = priority_queries.index(qid) if qid in priority_queries else len(priority_queries)
        return (priority, int(safe_float(row.get("rank"), 999)), -safe_float(row.get("final_score")))

    examples: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()

    def add_from(candidates: list[dict[str, Any]], case_type: str, n: int, why: str, max_per_query: int = 2) -> None:
        nonlocal examples
        per_query: dict[str, int] = defaultdict(int)
        for row in sorted(candidates, key=sort_key):
            key = (clean_text(row.get("query_id")), clean_text(row.get("doc_id")))
            qid = clean_text(row.get("query_id"))
            if key in seen:
                continue
            if per_query[qid] >= max_per_query:
                continue
            seen.add(key)
            per_query[qid] += 1
            examples.append(make_example(row, case_type, why))
            if sum(1 for e in examples if e["case_type"] == case_type) >= n:
                break

    add_from(good_candidates, "good", 6, "Có explanation và evidence rõ từ metadata/KG/entity match.", max_per_query=2)
    add_from(partial_candidates, "partial", 3, "Có explanation nhưng chỉ có một phần evidence hoặc thiếu một nhóm metadata/KG.", max_per_query=1)
    add_from(weak_candidates, "weak", 3, "Thiếu explanation rõ hoặc không phát hiện được entity/evidence match chắc chắn.", max_per_query=1)

    return examples[:limit]


def make_example(row: dict[str, Any], case_type: str, why: str) -> dict[str, Any]:
    return {
        "case_type": case_type,
        "query_id": clean_text(row.get("query_id")),
        "query_text": clean_text(row.get("query_text")),
        "query_group": clean_text(row.get("query_group")),
        "rank": int(safe_float(row.get("rank"), 0)),
        "doc_id": clean_text(row.get("doc_id")),
        "title": clean_text(row.get("title")),
        "relevance_label": clean_text(row.get("relevance_label")),
        "final_score": safe_float(row.get("final_score")),
        "vector_score": row.get("vector_score", ""),
        "metadata_delta": row.get("metadata_delta", ""),
        "kg_score": row.get("kg_score", ""),
        "intent_adjustment": row.get("intent_adjustment", ""),
        "explanation_text": clean_text(row.get("explanation_text")),
        "evidence_summary": clean_text(row.get("evidence_summary")),
        "why_selected": why,
    }


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not fieldnames:
        keys: list[str] = []
        for row in rows:
            for key in row.keys():
                if key not in keys:
                    keys.append(key)
        fieldnames = keys
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def format_rate(x: Any) -> str:
    return f"{safe_float(x):.3f}"


def markdown_table(rows: list[dict[str, Any]], columns: list[str], max_rows: int | None = None) -> str:
    rows = rows[:max_rows] if max_rows else rows
    out = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for row in rows:
        values = []
        for col in columns:
            value = row.get(col, "")
            if isinstance(value, float):
                value = f"{value:.3f}"
            values.append(str(value).replace("\n", " ").replace("|", "/"))
        out.append("| " + " | ".join(values) + " |")
    return "\n".join(out)


def create_figure(summary: dict[str, Any]) -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    metrics = [
        "has_explanation_rate",
        "top1_has_explanation_rate",
        "query_has_any_explanation_rate",
        "has_entity_match_rate",
        "has_metadata_evidence_rate",
        "has_kg_evidence_rate",
        "has_kg_relation_or_fact_rate",
    ]
    labels = [
        "Explanation",
        "Top-1 expl.",
        "Query any",
        "Entity match",
        "Metadata",
        "KG",
        "KG fact/rel.",
    ]
    values = [safe_float(summary.get(m)) for m in metrics]

    plt.figure(figsize=(10, 5.5))
    bars = plt.bar(labels, values, color="#3b6ea8", edgecolor="#1f2d3d", linewidth=0.7)
    plt.ylim(0, 1.05)
    plt.ylabel("Rate")
    plt.title("Explanation quality diagnostic")
    plt.grid(axis="y", alpha=0.25)
    plt.xticks(rotation=25, ha="right")
    for bar, value in zip(bars, values):
        plt.text(bar.get_x() + bar.get_width() / 2, value + 0.02, f"{value:.3f}", ha="center", va="bottom", fontsize=9)
    plt.tight_layout()
    plt.savefig(FIGURE_PATH, dpi=200)
    plt.close()


def write_report(
    summary_rows: list[dict[str, Any]],
    by_group: list[dict[str, Any]],
    by_query: list[dict[str, Any]],
    examples: list[dict[str, Any]],
    relevance_rows: list[dict[str, Any]],
    source_mode: str,
    warnings: list[str],
) -> None:
    summary = summary_rows[0]
    strongest = max(by_group, key=lambda r: safe_float(r.get("has_kg_evidence_rate"))) if by_group else {}
    weakest = min(by_group, key=lambda r: safe_float(r.get("has_explanation_rate"))) if by_group else {}
    expl_values = [safe_float(r.get("has_explanation_rate")) for r in by_group]
    if expl_values and min(expl_values) == max(expl_values):
        group_observation = (
            f"Tất cả nhóm truy vấn đều đạt `has_explanation_rate={expl_values[0]:.3f}` trong diagnostic này. "
            f"Nhóm có `has_kg_evidence_rate` cao nhất là `{strongest.get('query_group', 'N/A')}` "
            f"với giá trị `{format_rate(strongest.get('has_kg_evidence_rate', 0))}`."
        )
    else:
        group_observation = (
            f"Nhóm có `has_kg_evidence_rate` cao nhất là `{strongest.get('query_group', 'N/A')}` "
            f"với giá trị `{format_rate(strongest.get('has_kg_evidence_rate', 0))}`. "
            f"Nhóm có `has_explanation_rate` thấp nhất là `{weakest.get('query_group', 'N/A')}` "
            f"với giá trị `{format_rate(weakest.get('has_explanation_rate', 0))}`."
        )
    rel_note = "Không join được relevance judgments." if not relevance_rows else "Đã join relevance judgments theo query_id + doc_id."

    report = f"""# Explanation quality diagnostic report

Generated at: `2026-05-29`

## 1. Mục tiêu

Đánh giá này là automatic explanation diagnostic cho hệ thống hybrid search trong project Aquaculture Semantic Search. Mục tiêu là đo coverage của explanation và các loại evidence xuất hiện trong kết quả Top-k, gồm entity match, metadata evidence và KG evidence. Đây không phải user study, không phải đánh giá chuyên gia thủ công, và không thay thế các metric retrieval như P@k, Recall@k, MRR, nDCG hoặc MAP.

## 2. Dữ liệu và phương pháp

- Query set: `data/eval/final_query_set_core.csv`.
- Số query core: `{summary.get("n_queries")}`.
- Top-k: `{summary.get("top_k")}`.
- Relevance judgments: `data/eval/relevance_judgments_core.csv` ({rel_note})
- KG diagnostic input nếu có: `outputs/kg_score_component_analysis.csv`.
- Query understanding profile nếu có: `outputs/query_understanding_profiles.csv`.
- Source mode: `{source_mode}`.

Script `experiments/evaluate_explanation_quality.py` ưu tiên tái chạy nhẹ `hybrid_search.hybrid_search()` trên 28 core queries để lấy runtime fields như `explanation`, `metadata_delta`, `kg_score`, `intent_adjustment`, `bonus_breakdown`, `kg_explanation` và match flags. Việc tái chạy này chỉ phục vụ explanation diagnostic, không overwrite `baseline_hybrid_core.csv`, không tạo baseline metric mới và không sửa runtime/scoring. Nếu runtime import hoặc recomputation lỗi, script fallback sang `baseline_hybrid_core.csv` kết hợp `kg_score_component_analysis.csv`.

Cách xác định evidence:

- `has_explanation`: explanation text hoặc KG explanation không rỗng.
- `has_entity_match`: có match flag disease/species/location/mode, metadata/KG evidence, hoặc explanation nhắc entity/fact/relation.
- `has_metadata_evidence`: `metadata_delta > 0`, có `bonus_breakdown`, hoặc explanation nhắc metadata/entity match.
- `has_kg_evidence`: `kg_score > 0`, `kg_explanation` không rỗng, hoặc KG diagnostic cho thấy direct/relation/context/explanation evidence.
- `has_kg_relation_or_fact`: ưu tiên cột direct/relation evidence trong `kg_score_component_analysis.csv`; nếu thiếu thì suy từ KG explanation/fact/relation keywords.

## 3. Chỉ số diagnostic

- `has_explanation_rate`: tỷ lệ result rows có explanation text.
- `top1_has_explanation_rate`: tỷ lệ Top-1 của mỗi query có explanation.
- `query_has_any_explanation_rate`: tỷ lệ query có ít nhất một result trong Top-k có explanation.
- `has_entity_match_rate`: tỷ lệ result rows có entity match hoặc evidence cho entity match.
- `has_metadata_evidence_rate`: tỷ lệ result rows có metadata evidence.
- `has_kg_evidence_rate`: tỷ lệ result rows có KG evidence.
- `has_kg_relation_or_fact_rate`: tỷ lệ result rows có KG fact hoặc relation/context evidence.
- `mean_explanation_length`: độ dài trung bình của explanation text ở các row có explanation.
- `mean_evidence_count`: số mảnh evidence trung bình tách từ explanation/breakdown theo dấu `;`, newline hoặc `|`.

## 4. Kết quả tổng thể

{markdown_table(summary_rows, ["scope", "n_queries", "n_rows", "top_k", "has_explanation_rate", "top1_has_explanation_rate", "query_has_any_explanation_rate", "has_entity_match_rate", "has_metadata_evidence_rate", "has_kg_evidence_rate", "has_kg_relation_or_fact_rate", "mean_explanation_length", "mean_evidence_count"])}

Relevance-aware diagnostic:

{markdown_table(relevance_rows, ["label", "n_rows", "has_explanation_rate", "has_metadata_evidence_rate", "has_kg_evidence_rate"]) if relevance_rows else "Không có đủ relevance label để tạo bảng relevance-aware."}

## 5. Kết quả theo nhóm truy vấn

{markdown_table(by_group, ["query_group", "n_queries", "n_rows", "has_explanation_rate", "top1_has_explanation_rate", "query_has_any_explanation_rate", "has_entity_match_rate", "has_metadata_evidence_rate", "has_kg_evidence_rate", "has_kg_relation_or_fact_rate", "mean_explanation_length"])}

Nhận xét theo dữ liệu thực tế: {group_observation} Các khác biệt này phản ánh mức độ KG/metadata evidence có sẵn trong runtime hiện tại, không phải đánh giá cuối cùng về chất lượng ngôn ngữ của explanation.

## 6. Ví dụ explanation tiêu biểu

{examples_markdown(examples)}

File ví dụ đầy đủ: `outputs/explanation_quality_examples.csv`.

## 7. Hạn chế

- Đây là đánh giá tự động/rule-based, chưa có người dùng hoặc chuyên gia chấm explanation theo thang 1-5.
- Explanation coverage không đồng nghĩa explanation luôn đúng hoàn toàn.
- Chất lượng explanation phụ thuộc vào metadata, KG fact coverage, alias coverage, entity linking và runtime evidence.
- Nếu baseline CSV không lưu full component thì một số evidence được tái tính hoặc suy ra từ runtime hiện tại.
- Chưa đánh giá sâu tính dễ hiểu, tính thuyết phục hoặc khả năng hỗ trợ ra quyết định bằng human evaluation.
- Các chỉ số ở đây không phải retrieval metrics mới và không thay thế kết quả evaluation chính.

## 8. Đoạn có thể chèn vào báo cáo

Để bổ sung đánh giá khả năng giải thích của hệ thống, đề tài thực hiện một automatic explanation diagnostic trên 28 truy vấn core và kết quả hybrid Top-{summary.get("top_k")}. Đánh giá này đo tỷ lệ kết quả có explanation, có entity match, có metadata evidence, có KG evidence và có KG fact/relation evidence. Kết quả tổng thể cho thấy `has_explanation_rate` đạt `{format_rate(summary.get("has_explanation_rate"))}`, `top1_has_explanation_rate` đạt `{format_rate(summary.get("top1_has_explanation_rate"))}`, và `query_has_any_explanation_rate` đạt `{format_rate(summary.get("query_has_any_explanation_rate"))}`. Tỷ lệ metadata evidence là `{format_rate(summary.get("has_metadata_evidence_rate"))}`, trong khi tỷ lệ KG evidence là `{format_rate(summary.get("has_kg_evidence_rate"))}` và KG fact/relation evidence là `{format_rate(summary.get("has_kg_relation_or_fact_rate"))}`. Các kết quả này cho thấy explanation có thể minh họa vai trò của metadata và Knowledge Graph trong quá trình reranking của hybrid search. Tuy nhiên, đây chỉ là đánh giá tự động dựa trên rule và runtime evidence, không phải user study hoặc đánh giá chuyên gia. Vì vậy, kết quả chỉ nên được dùng như phân tích bổ trợ trong Chương 4; nếu phát triển thành nghiên cứu lớn hơn, cần bổ sung human evaluation về tính đúng, dễ hiểu và hữu ích của explanation.

## 9. Caption hình đề xuất

Hình 4.x. Đánh giá diagnostic khả năng explanation của hệ thống hybrid search.

Figure path: `outputs/figures/fig_explanation_quality_summary.png`.

## 10. Safety confirmation

- Không sửa runtime/scoring.
- Không sửa `hybrid_search.py`, `kg_runtime.py`, `vector_search.py`, `run_core_baselines.py`.
- Không sửa `app_streamlit.py`.
- Không sửa ontology/metadata/query set/relevance judgments.
- Không sửa baseline results hoặc metrics cũ.
- Không overwrite baseline CSV cũ.
- Output mới chỉ là diagnostic explanation report.

## 11. Script warnings

{warnings_markdown(warnings)}
"""
    REPORT_PATH.write_text(report, encoding="utf-8")


def examples_markdown(examples: list[dict[str, Any]]) -> str:
    if not examples:
        return "Không chọn được ví dụ explanation."
    lines = []
    for ex in examples[:5]:
        explanation = clean_text(ex.get("explanation_text"))
        if len(explanation) > 420:
            explanation = explanation[:417] + "..."
        lines.append(
            f"- `{ex.get('case_type')}` | `{ex.get('query_id')}` | query: {ex.get('query_text')} | "
            f"doc: `{ex.get('doc_id')}` - {ex.get('title')} | label: {ex.get('relevance_label') or 'N/A'}\n"
            f"  Evidence: {clean_text(ex.get('evidence_summary')) or 'N/A'}\n"
            f"  Explanation: {explanation or 'N/A'}"
        )
    return "\n".join(lines)


def warnings_markdown(warnings: list[str]) -> str:
    if not warnings:
        return "Không có warning nghiêm trọng."
    return "\n".join(f"- {w.replace(chr(10), ' ')}" for w in warnings[:8])


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    core_queries = read_csv_if_exists(CORE_QUERY_PATH)
    if core_queries.empty:
        raise FileNotFoundError(f"Missing or empty core query set: {CORE_QUERY_PATH}")

    relevance = load_relevance_lookup()
    kg_lookup = load_kg_component_lookup()

    rows, source_mode, warnings = runtime_rows(core_queries)
    if not rows:
        rows = fallback_rows(core_queries, kg_lookup)
        source_mode = "baseline_plus_kg_diagnostic_fallback"
    if not rows:
        raise RuntimeError("No rows available for explanation diagnostic.")

    rows = augment_and_flag_rows(rows, relevance, kg_lookup)
    notes = (
        "Explanation diagnostic; runtime recomputed for core queries; no baseline overwrite."
        if source_mode == "runtime_recomputed"
        else "Fallback from baseline_hybrid_core plus KG diagnostic; explanation may be incomplete."
    )
    summary_rows = [aggregate_scope(rows, "core_hybrid_top10", TOP_K, notes)]
    by_group = aggregate_by_group(rows)
    by_query = aggregate_by_query(rows)
    examples = select_examples(rows)
    relevance_rows = relevance_aware_rows(rows)

    write_csv(SUMMARY_PATH, summary_rows)
    write_csv(BY_GROUP_PATH, by_group)
    write_csv(BY_QUERY_PATH, by_query)
    write_csv(EXAMPLES_PATH, examples)
    create_figure(summary_rows[0])
    write_report(summary_rows, by_group, by_query, examples, relevance_rows, source_mode, warnings)

    print(f"[OK] source_mode={source_mode}")
    print(f"[OK] rows={len(rows)} queries={summary_rows[0]['n_queries']}")
    print(f"[OK] wrote {SUMMARY_PATH.relative_to(PROJECT_ROOT)}")
    print(f"[OK] wrote {BY_GROUP_PATH.relative_to(PROJECT_ROOT)}")
    print(f"[OK] wrote {BY_QUERY_PATH.relative_to(PROJECT_ROOT)}")
    print(f"[OK] wrote {EXAMPLES_PATH.relative_to(PROJECT_ROOT)}")
    print(f"[OK] wrote {REPORT_PATH.relative_to(PROJECT_ROOT)}")
    print(f"[OK] wrote {FIGURE_PATH.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
