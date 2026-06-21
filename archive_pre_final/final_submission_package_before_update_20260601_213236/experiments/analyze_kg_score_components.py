from __future__ import annotations

import csv
import math
import re
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import hybrid_search
import kg_runtime
from hybrid_search import (
    METADATA_PATH,
    build_metadata_lookup,
    build_term_index,
    compute_match_features,
    detect_entities,
    load_full_metadata,
)


QUERY_SET = PROJECT_ROOT / "data" / "eval" / "final_query_set_core.csv"
JUDGMENTS = PROJECT_ROOT / "data" / "eval" / "relevance_judgments_core.csv"
HYBRID_RESULTS = PROJECT_ROOT / "data" / "eval" / "results" / "baseline_hybrid_core.csv"
RUNTIME_VERIFICATION = PROJECT_ROOT / "outputs" / "kg_runtime_verification.json"
FACT_COVERAGE_JSON = PROJECT_ROOT / "outputs" / "document_fact_coverage_audit.json"
QUERY_PROFILES_CSV = PROJECT_ROOT / "outputs" / "query_understanding_profiles.csv"

OUTPUT_CSV = PROJECT_ROOT / "outputs" / "kg_score_component_analysis.csv"
OUTPUT_MD = PROJECT_ROOT / "outputs" / "kg_score_component_analysis.md"
OUTPUT_FIG = PROJECT_ROOT / "outputs" / "figures" / "fig_kg_score_components.png"

DIRECT_PATTERNS = [
    "aboutDisease",
    "aboutTaxon",
    "aboutLocation",
    "documentProductionMode",
    "mentions",
]
RELATION_PATTERNS = [
    "affectsTaxon",
    "causedBy",
    "hasSymptom",
    "recommendedPrevention",
    "recommendedTreatment",
    "isFoundIn",
    "disease-taxon",
    "disease-pathogen",
    "taxon-location",
    "pathogen",
    "symptom",
    "prevention",
    "treatment",
    "relation match",
    "KG relation",
]
EVIDENCE_TYPES = [
    "aboutDisease",
    "aboutTaxon",
    "aboutLocation",
    "documentProductionMode",
    "affectsTaxon",
    "causedBy",
    "isFoundIn",
    "hasSymptom",
    "recommendedPrevention",
    "recommendedTreatment",
]

CSV_FIELDS = [
    "query_id",
    "query",
    "query_group",
    "rank",
    "doc_id",
    "title",
    "kg_score",
    "intent_adjustment",
    "explanation",
    "kg_direct_fact_score_diagnostic",
    "kg_relation_score_diagnostic",
    "kg_explanation_score_diagnostic",
    "kg_penalty_diagnostic",
    "kg_unclassified_score_diagnostic",
    "has_kg_score",
    "has_direct_fact_evidence",
    "has_relation_evidence",
    "has_explanation_evidence",
    "kg_direct_fact_evidence",
    "kg_relation_evidence",
    "kg_explanation_evidence",
    "kg_component_notes",
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


def contains_any(text: str, patterns: list[str]) -> bool:
    lower = text.lower()
    return any(pattern.lower() in lower for pattern in patterns)


def evidence_matches(text: str, patterns: list[str]) -> list[str]:
    lower = text.lower()
    return [pattern for pattern in patterns if pattern.lower() in lower]


def parse_negative_amounts(text: str) -> float:
    total = 0.0
    for match in re.finditer(r"\(-\s*([0-9]*\.?[0-9]+)\)", text or ""):
        total += float(match.group(1))
    return total


def link_and_merge_entities(query: str, term_index: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any]]:
    detected = detect_entities(query, term_index)
    hybrid_search._init_kg_if_needed()
    linked = {"disease": [], "species": [], "location": [], "mode": [], "prevention": []}
    if hybrid_search._KG_INDEX:
        try:
            raw = kg_runtime.link_query_entities_kg(query, hybrid_search._KG_INDEX)
            linked = {
                "disease": raw.get("disease") or [],
                "species": raw.get("species") or [],
                "location": raw.get("location") or [],
                "mode": raw.get("mode") or [],
                "prevention": raw.get("prevention") or [],
                "pathogen": raw.get("pathogen") or [],
                "symptom": raw.get("symptom") or [],
                "treatment": raw.get("treatment") or [],
            }
        except Exception:
            pass
    return hybrid_search._merge_detected_with_kg(detected, linked), linked


def score_kg_for_doc(
    query: str,
    doc_id: str,
    metadata_lookup: dict[str, dict[str, Any]],
    term_index: list[dict[str, Any]],
) -> dict[str, Any]:
    detected, kg_entities = link_and_merge_entities(query, term_index)
    row = metadata_lookup.get(doc_id, {})
    kg_info: dict[str, Any] = {
        "kg_score": 0.0,
        "kg_direct_match": 0.0,
        "kg_relation_match": 0.0,
        "kg_context_match": 0.0,
        "kg_bonus_breakdown": "",
        "kg_penalty_breakdown": "",
        "kg_explanation": [],
        "doc_uri_in_kg": None,
    }
    if hybrid_search._KG_GRAPH is not None and hybrid_search._KG_INDEX is not None:
        try:
            doc_uri = hybrid_search._map_doc_to_kg_uri(doc_id, row)
            kg_info["doc_uri_in_kg"] = doc_uri
            if doc_uri:
                doc_facts = kg_runtime.get_document_facts(hybrid_search._KG_GRAPH, doc_uri)
                kg_info.update(
                    kg_runtime.score_doc_with_kg(
                        query_entities=kg_entities,
                        doc_facts=doc_facts,
                        kg_index=hybrid_search._KG_INDEX,
                        graph=hybrid_search._KG_GRAPH,
                        query_text=query,
                    )
                )
        except Exception as exc:
            kg_info["kg_explanation"] = [f"KG diagnostic scoring failed: {exc}"]

    intent_adjustment, intent_explanation = hybrid_search._intent_narrow_final_adjustment(
        query, detected, row, str(row.get("title", ""))
    )
    kg_info["intent_adjustment"] = float(intent_adjustment)
    kg_info["intent_explanation"] = intent_explanation
    return kg_info


def diagnostic_decompose(kg_info: dict[str, Any]) -> dict[str, Any]:
    kg_score = safe_float(kg_info.get("kg_score"))
    direct_raw = safe_float(kg_info.get("kg_direct_match"))
    relation_raw = safe_float(kg_info.get("kg_relation_match"))
    context_raw = safe_float(kg_info.get("kg_context_match"))
    intent_adjustment = safe_float(kg_info.get("intent_adjustment"))
    explanation_list = kg_info.get("kg_explanation") or []
    if isinstance(explanation_list, str):
        explanation_text = explanation_list
    else:
        explanation_text = "; ".join(str(item) for item in explanation_list)
    bonus = str(kg_info.get("kg_bonus_breakdown") or "")
    penalty_breakdown = str(kg_info.get("kg_penalty_breakdown") or "")
    intent_explanation = str(kg_info.get("intent_explanation") or "")
    evidence_text = " ; ".join([explanation_text, bonus, penalty_breakdown, intent_explanation])

    direct_evidence = evidence_matches(evidence_text, DIRECT_PATTERNS)
    relation_evidence = evidence_matches(evidence_text, RELATION_PATTERNS)
    has_direct = bool(direct_evidence) or direct_raw > 0
    has_relation = bool(relation_evidence) or relation_raw > 0 or context_raw > 0
    has_explanation = bool(explanation_text.strip())

    direct_score = max(0.0, direct_raw) if has_direct else 0.0
    relation_score = max(0.0, relation_raw) + max(0.0, context_raw) if has_relation else 0.0
    explanation_score = min(0.05, max(kg_score, 0.0) * 0.10) if has_explanation and kg_score > 0 else 0.0
    kg_internal_penalty = parse_negative_amounts(penalty_breakdown)
    guardrail_penalty = abs(intent_adjustment) if intent_adjustment < 0 else 0.0
    penalty_score = kg_internal_penalty + guardrail_penalty

    classified = direct_score + relation_score
    unclassified = max(0.0, kg_score - classified) if kg_score > 0 else 0.0
    if kg_score > 0 and classified <= 0:
        unclassified = kg_score

    notes = [
        "diagnostic approximation; final hybrid scoring unchanged",
        f"runtime_direct={direct_raw:.4f}",
        f"runtime_relation={relation_raw:.4f}",
        f"runtime_context={context_raw:.4f}",
    ]
    if kg_internal_penalty:
        notes.append(f"internal_kg_penalty_abs={kg_internal_penalty:.4f}")
    if guardrail_penalty:
        notes.append(f"intent_guardrail_penalty_abs={guardrail_penalty:.4f}")

    return {
        "kg_score": kg_score,
        "intent_adjustment": intent_adjustment,
        "explanation": evidence_text,
        "kg_direct_fact_score_diagnostic": direct_score,
        "kg_relation_score_diagnostic": relation_score,
        "kg_explanation_score_diagnostic": explanation_score,
        "kg_penalty_diagnostic": penalty_score,
        "kg_unclassified_score_diagnostic": unclassified,
        "has_kg_score": kg_score > 0,
        "has_direct_fact_evidence": has_direct,
        "has_relation_evidence": has_relation,
        "has_explanation_evidence": has_explanation,
        "kg_direct_fact_evidence": "; ".join(direct_evidence),
        "kg_relation_evidence": "; ".join(relation_evidence),
        "kg_explanation_evidence": explanation_text,
        "kg_component_notes": "; ".join(notes),
    }


def build_analysis_rows() -> list[dict[str, Any]]:
    hybrid_rows = read_csv_rows(HYBRID_RESULTS)
    queries = read_csv_rows(QUERY_SET)
    query_by_id = {row["query_id"]: row for row in queries}
    metadata_df = load_full_metadata(str(METADATA_PATH))
    metadata_lookup = build_metadata_lookup(metadata_df)
    term_index = build_term_index(metadata_df)

    hybrid_search._init_kg_if_needed()
    output_rows: list[dict[str, Any]] = []
    for row in hybrid_rows:
        query_id = str(row.get("query_id", ""))
        query_info = query_by_id.get(query_id, {})
        query = str(row.get("query_text") or query_info.get("query_text") or "")
        doc_id = str(row.get("doc_id", ""))
        kg_info = score_kg_for_doc(query, doc_id, metadata_lookup, term_index)
        diagnostic = diagnostic_decompose(kg_info)
        output_rows.append(
            {
                "query_id": query_id,
                "query": query,
                "query_group": query_info.get("query_group", ""),
                "rank": row.get("rank", ""),
                "doc_id": doc_id,
                "title": row.get("title", ""),
                **diagnostic,
            }
        )
    return output_rows


def pct(numerator: int | float, denominator: int | float) -> float:
    return 0.0 if denominator == 0 else float(numerator) / float(denominator)


def mean(values: list[float]) -> float:
    return statistics.mean(values) if values else 0.0


def summarize_overall(rows: list[dict[str, Any]]) -> dict[str, Any]:
    query_ids = sorted({str(row["query_id"]) for row in rows})
    queries_with_kg = sorted({str(row["query_id"]) for row in rows if row["has_kg_score"]})
    top1 = [row for row in rows if int(float(row["rank"])) == 1]
    return {
        "total_result_rows": len(rows),
        "results_with_kg_score": sum(1 for row in rows if row["has_kg_score"]),
        "pct_results_with_kg_score": pct(sum(1 for row in rows if row["has_kg_score"]), len(rows)),
        "queries_with_kg_score": len(queries_with_kg),
        "total_queries": len(query_ids),
        "pct_queries_with_kg_score": pct(len(queries_with_kg), len(query_ids)),
        "mean_kg_score_topk": mean([float(row["kg_score"]) for row in rows]),
        "mean_kg_score_top1": mean([float(row["kg_score"]) for row in top1]),
    }


def summarize_components(rows: list[dict[str, Any]]) -> dict[str, Any]:
    n = len(rows)
    fields = [
        "kg_direct_fact_score_diagnostic",
        "kg_relation_score_diagnostic",
        "kg_explanation_score_diagnostic",
        "kg_penalty_diagnostic",
        "kg_unclassified_score_diagnostic",
    ]
    out: dict[str, Any] = {
        "n_rows": n,
        "results_with_direct_fact_evidence": sum(1 for row in rows if row["has_direct_fact_evidence"]),
        "pct_results_with_direct_fact_evidence": pct(sum(1 for row in rows if row["has_direct_fact_evidence"]), n),
        "results_with_relation_evidence": sum(1 for row in rows if row["has_relation_evidence"]),
        "pct_results_with_relation_evidence": pct(sum(1 for row in rows if row["has_relation_evidence"]), n),
        "results_with_explanation_evidence": sum(1 for row in rows if row["has_explanation_evidence"]),
        "pct_results_with_explanation_evidence": pct(sum(1 for row in rows if row["has_explanation_evidence"]), n),
    }
    for field in fields:
        values = [float(row[field]) for row in rows]
        out[f"sum_{field}"] = sum(values)
        out[f"mean_{field}"] = mean(values)
    return out


def summarize_by_group(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row["query_group"])].append(row)
    out = []
    for group, group_rows in sorted(grouped.items()):
        top1 = [row for row in group_rows if int(float(row["rank"])) == 1]
        query_count = len({row["query_id"] for row in group_rows})
        mean_kg = mean([float(row["kg_score"]) for row in group_rows])
        direct_pct = pct(sum(1 for row in group_rows if row["has_direct_fact_evidence"]), len(group_rows))
        relation_pct = pct(sum(1 for row in group_rows if row["has_relation_evidence"]), len(group_rows))
        if mean_kg >= 0.15:
            interpretation = "KG contribution strong"
        elif mean_kg >= 0.05:
            interpretation = "KG contribution moderate"
        else:
            interpretation = "KG contribution weak or sparse"
        out.append(
            {
                "query_group": group,
                "n_queries": query_count,
                "n_results": len(group_rows),
                "mean_kg_score": mean_kg,
                "top1_mean_kg_score": mean([float(row["kg_score"]) for row in top1]),
                "pct_results_with_kg_score": pct(sum(1 for row in group_rows if row["has_kg_score"]), len(group_rows)),
                "pct_results_with_direct_fact_evidence": direct_pct,
                "pct_results_with_relation_evidence": relation_pct,
                "pct_results_with_explanation_evidence": pct(sum(1 for row in group_rows if row["has_explanation_evidence"]), len(group_rows)),
                "interpretation": interpretation,
            }
        )
    return out


def evidence_type_counts(rows: list[dict[str, Any]]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for row in rows:
        text = str(row.get("explanation", ""))
        for evidence_type in EVIDENCE_TYPES:
            counts[evidence_type] += len(re.findall(re.escape(evidence_type), text, flags=re.IGNORECASE))
    return counts


def fmt(value: Any) -> str:
    try:
        return f"{float(value):.4f}"
    except Exception:
        return str(value)


def write_figure(component_summary: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    OUTPUT_FIG.parent.mkdir(parents=True, exist_ok=True)
    labels = [
        "Direct fact\n evidence",
        "Relation/context\n evidence",
        "Explanation\n evidence",
        "Penalty/\nguardrail",
        "Unclassified",
    ]
    values = [
        component_summary["pct_results_with_direct_fact_evidence"],
        component_summary["pct_results_with_relation_evidence"],
        component_summary["pct_results_with_explanation_evidence"],
        pct(sum(1 for row in rows if float(row["kg_penalty_diagnostic"]) > 0), len(rows)),
        pct(sum(1 for row in rows if float(row["kg_unclassified_score_diagnostic"]) > 0), len(rows)),
    ]
    colors = ["#2563eb", "#16a34a", "#7c3aed", "#dc2626", "#6b7280"]

    fig, ax = plt.subplots(figsize=(9.5, 5.6), facecolor="white")
    bars = ax.bar(labels, values, color=colors, edgecolor="white", linewidth=0.8)
    ax.set_title("KG score component diagnostic evidence")
    ax.set_ylabel("Share of hybrid result rows")
    ax.set_ylim(0, 1.05)
    ax.grid(axis="y", color="#e5e7eb", linewidth=0.9)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, height + 0.02, f"{height:.1%}", ha="center", va="bottom", fontsize=10)
    fig.text(
        0.5,
        0.01,
        "Hình 4.x. Phân rã diagnostic các nhóm evidence đóng góp vào KG score trong hybrid search",
        ha="center",
        va="bottom",
        fontsize=9.5,
        color="#374151",
    )
    fig.tight_layout(rect=(0.02, 0.06, 0.98, 0.98))
    fig.savefig(OUTPUT_FIG, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def write_report(rows: list[dict[str, Any]]) -> None:
    overall = summarize_overall(rows)
    components = summarize_components(rows)
    group_rows = summarize_by_group(rows)
    evidence_counts = evidence_type_counts(rows)
    write_figure(components, rows)

    data_used = [
        HYBRID_RESULTS,
        QUERY_SET,
        JUDGMENTS,
        Path(METADATA_PATH),
        PROJECT_ROOT / "data" / "ontology" / "taxon_enriched_facts_v2.owl",
    ]
    optional_files = [RUNTIME_VERIFICATION, FACT_COVERAGE_JSON, QUERY_PROFILES_CSV]
    data_used.extend(path for path in optional_files if path.exists())

    lines = [
        "# KG Score Component Diagnostic Analysis",
        "",
        "## Purpose",
        "",
        "Mục tiêu là tách `kg_score` thành các nhóm diagnostic để làm rõ KG đóng góp qua direct document facts, relation/context evidence, explanation và penalty/guardrail. Đây là diagnostic decomposition, không thay đổi scoring final và không thay thế công thức `final_score = vector_score + metadata_delta + kg_score + intent_adjustment`.",
        "",
        "## Data used",
        "",
    ]
    display_paths = []
    for path in data_used:
        path = Path(path)
        try:
            display_paths.append(str(path.relative_to(PROJECT_ROOT)) if path.is_absolute() else str(path))
        except ValueError:
            display_paths.append(str(path))
    lines.extend([f"- `{path}`" for path in display_paths])
    lines.extend(
        [
            "",
            "## Method",
            "",
            "- `baseline_hybrid_core.csv` không lưu `kg_score`/KG explanation chi tiết, nên script tái tính KG cho từng cặp query-doc bằng `kg_runtime.score_doc_with_kg()` và mapping KG hiện có.",
            "- Direct fact evidence nhận diện `aboutDisease`, `aboutTaxon`, `aboutLocation`, `documentProductionMode`, `mentions`.",
            "- Relation/context evidence nhận diện `affectsTaxon`, `causedBy`, `isFoundIn`, `hasSymptom`, `recommendedPrevention`, `recommendedTreatment`, `pathogen`, `symptom`, `prevention`, `treatment`, `relation match`.",
            "- Explanation evidence là việc runtime trả về `kg_explanation`; score diagnostic visibility dùng `min(0.05, kg_score * 0.1)` khi `kg_score > 0`.",
            "- Penalty/guardrail gồm penalty trong `kg_penalty_breakdown` và `abs(intent_adjustment)` nếu intent adjustment âm.",
            "- `kg_unclassified_score_diagnostic` giữ phần dương của `kg_score` chưa được phân loại vào direct hoặc relation/context. Các component là approximation phục vụ phân tích, không phải điểm final.",
            "",
            "## Overall KG usage",
            "",
            "| metric | value |",
            "| --- | ---: |",
        ]
    )
    for key, value in overall.items():
        lines.append(f"| {key} | {fmt(value)} |")

    lines.extend(
        [
            "",
            "## Component distribution",
            "",
            "| component metric | value |",
            "| --- | ---: |",
        ]
    )
    for key, value in components.items():
        lines.append(f"| {key} | {fmt(value)} |")

    lines.extend(
        [
            "",
            "## By-query-group analysis",
            "",
            "| query_group | n_queries | n_results | mean_kg_score | top1_mean_kg_score | pct_kg_score | pct_direct_fact | pct_relation | pct_explanation | interpretation |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for row in group_rows:
        lines.append(
            f"| {row['query_group']} | {row['n_queries']} | {row['n_results']} | {fmt(row['mean_kg_score'])} | "
            f"{fmt(row['top1_mean_kg_score'])} | {fmt(row['pct_results_with_kg_score'])} | "
            f"{fmt(row['pct_results_with_direct_fact_evidence'])} | {fmt(row['pct_results_with_relation_evidence'])} | "
            f"{fmt(row['pct_results_with_explanation_evidence'])} | {row['interpretation']} |"
        )

    lines.extend(
        [
            "",
            "## Evidence type counts",
            "",
            "| evidence_type | count |",
            "| --- | ---: |",
        ]
    )
    for evidence_type in EVIDENCE_TYPES:
        lines.append(f"| {evidence_type} | {evidence_counts[evidence_type]} |")

    strongest_group = max(group_rows, key=lambda row: row["mean_kg_score"])
    weakest_group = min(group_rows, key=lambda row: row["mean_kg_score"])
    direct_pct = components["pct_results_with_direct_fact_evidence"]
    relation_pct = components["pct_results_with_relation_evidence"]
    dominant = "direct facts" if direct_pct >= relation_pct else "relation/context evidence"
    lines.extend(
        [
            "",
            "## Interpretation for report",
            "",
            f"KG không chỉ là một điểm tổng: trong diagnostic này, đóng góp chủ yếu nghiêng về `{dominant}`. Direct document facts như `aboutDisease`, `aboutTaxon`, `aboutLocation`, `documentProductionMode` cho biết tài liệu khớp trực tiếp với entity/query. Relation/context evidence như disease-taxon, disease-pathogen, taxon-location, prevention/treatment/symptom giúp bổ sung ngữ cảnh chuyên ngành khi tài liệu không chỉ khớp từ khóa bề mặt.",
            "",
            "Explanation evidence giúp làm rõ vì sao tài liệu được ưu tiên trong hybrid search. Tuy nhiên decomposition này là diagnostic, dựa trên explanation/runtime result được tái tính, không thay thế công thức scoring final.",
            "",
            f"Nhóm có KG contribution mạnh nhất theo mean `kg_score` là `{strongest_group['query_group']}`; nhóm yếu nhất là `{weakest_group['query_group']}`. Các chiều disease/location có thể còn yếu nếu evidence trong ontology ít hơn taxon/production mode hoặc nếu query không được entity linking rõ.",
            "",
            "## Limitations",
            "",
            "- `baseline_hybrid_core.csv` không lưu đầy đủ từng component gốc, nên script phải tái tính KG bằng runtime hiện có.",
            "- Component score là rule-based approximation và diagnostic visibility score, không phải điểm final.",
            "- Phân tích này không chứng minh mọi fact là đúng chuyên ngành.",
            "- Không thay đổi kết quả hybrid final.",
            "- Future work nên instrument runtime để log chính xác từng component score ngay lúc search.",
            "",
            "## Safety confirmation",
            "",
            "- Không sửa `hybrid_search.py`.",
            "- Không sửa `kg_runtime.py`.",
            "- Không sửa ontology.",
            "- Không sửa metadata.",
            "- Không sửa query set.",
            "- Không sửa relevance judgments.",
            "- Không sửa baseline outputs/metrics cũ.",
            "",
            "## Outputs",
            "",
            f"- `{OUTPUT_CSV.relative_to(PROJECT_ROOT)}`",
            f"- `{OUTPUT_MD.relative_to(PROJECT_ROOT)}`",
            f"- `{OUTPUT_FIG.relative_to(PROJECT_ROOT)}`",
        ]
    )
    OUTPUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    rows = build_analysis_rows()
    write_csv(OUTPUT_CSV, rows, CSV_FIELDS)
    write_report(rows)
    print(f"[OK] Wrote {OUTPUT_CSV.relative_to(PROJECT_ROOT)}")
    print(f"[OK] Wrote {OUTPUT_MD.relative_to(PROJECT_ROOT)}")
    print(f"[OK] Wrote {OUTPUT_FIG.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
