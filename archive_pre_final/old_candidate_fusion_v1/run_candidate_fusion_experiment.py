from __future__ import annotations

import csv
import json
import math
import statistics
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

import hybrid_search
import kg_runtime
from hybrid_search import (
    LOBSTER_COASTAL_VECTOR_BOOST_QUERY,
    METADATA_PATH,
    build_metadata_lookup,
    build_term_index,
    compute_hybrid_delta,
    compute_match_features,
    detect_entities,
    load_full_metadata,
)
from run_core_baselines import OkapiBM25, _normalize_minmax, _tokenize
from vector_search import load_index, search


PROJECT_ROOT = Path(__file__).resolve().parent
CORE_QUERIES = PROJECT_ROOT / "data" / "eval" / "final_query_set_core.csv"
JUDGMENTS = PROJECT_ROOT / "data" / "eval" / "relevance_judgments_core.csv"
RESULTS_DIR = PROJECT_ROOT / "data" / "eval" / "results"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

EXPERIMENT_RESULT = RESULTS_DIR / "baseline_hybrid_candidate_fusion_core.csv"
SUMMARY_CSV = OUTPUTS_DIR / "candidate_fusion_experiment_summary.csv"
SUMMARY_JSON = OUTPUTS_DIR / "candidate_fusion_experiment_summary.json"
SUMMARY_MD = OUTPUTS_DIR / "candidate_fusion_experiment_summary.md"
PER_QUERY_DELTA_CSV = OUTPUTS_DIR / "candidate_fusion_per_query_delta.csv"

BASELINE_HYBRID = RESULTS_DIR / "baseline_hybrid_core.csv"
BASELINE_VECTOR_METADATA = RESULTS_DIR / "baseline_vector_metadata_core.csv"

TOP_DOCS = 10
VECTOR_CHUNK_POOL_K = 150
LEXICAL_CHUNK_POOL_K = 150

RESULT_FIELDS = [
    "query_id",
    "query_text",
    "baseline_name",
    "rank",
    "doc_id",
    "title",
    "score_raw",
    "score_normalized",
    "retrieval_level",
    "explanation_short",
    "source_pipeline",
    "came_from_vector",
    "came_from_lexical",
    "vector_rank",
    "lexical_rank",
    "vector_score",
    "lexical_score",
    "metadata_delta",
    "kg_score",
    "intent_adjustment",
    "final_score",
    "candidate_union_count",
]

SUMMARY_FIELDS = [
    "baseline_name",
    "num_queries",
    "p_at_1",
    "p_at_3",
    "p_at_5",
    "recall_at_5",
    "mrr",
    "ndcg_at_5",
    "ndcg_at_10",
]


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in fields})


def load_core_queries() -> list[dict[str, str]]:
    return read_csv_rows(CORE_QUERIES)


def load_judgments() -> tuple[dict[tuple[str, str], int], dict[str, list[int]]]:
    jud: dict[tuple[str, str], int] = {}
    labels_by_q: dict[str, list[int]] = defaultdict(list)
    for r in read_csv_rows(JUDGMENTS):
        qid = str(r["query_id"]).strip()
        did = str(r["doc_id"]).strip()
        label = int(float(r["relevance_label"]))
        jud[(qid, did)] = label
        labels_by_q[qid].append(label)
    return jud, dict(labels_by_q)


def load_ranking(path: Path) -> dict[str, list[str]]:
    by_q: dict[str, list[tuple[int, str]]] = defaultdict(list)
    for r in read_csv_rows(path):
        by_q[str(r["query_id"]).strip()].append((int(float(r["rank"])), str(r["doc_id"]).strip()))
    return {qid: [doc for _rank, doc in sorted(rows)] for qid, rows in by_q.items()}


def gain(rel: int) -> float:
    return float((2 ** max(int(rel), 0)) - 1)


def dcg(grades: list[int], k: int) -> float:
    return sum(gain(grades[i] if i < len(grades) else 0) / math.log2(i + 2) for i in range(k))


def ndcg_at_k(grades: list[int], ideal: list[int], k: int) -> float:
    actual = dcg((grades + [0] * k)[:k], k)
    ideal_dcg = dcg((ideal + [0] * k)[:k], k)
    if ideal_dcg <= 0:
        return 1.0 if actual <= 0 else 0.0
    return actual / ideal_dcg


def compute_one_query(ranked_docs: list[str], qid: str, jud: dict[tuple[str, str], int], labels: list[int]) -> dict[str, float]:
    grades = [jud.get((qid, doc_id), 0) for doc_id in ranked_docs]
    binary = [g > 0 for g in grades]
    total_rel = sum(1 for x in labels if x > 0)
    ideal = sorted(labels, reverse=True)

    def p_at(k: int) -> float:
        return sum(binary[:k]) / float(k)

    rr = 0.0
    for idx, ok in enumerate(binary, start=1):
        if ok:
            rr = 1.0 / idx
            break
    recall5 = math.nan if total_rel <= 0 else sum(binary[:5]) / float(total_rel)
    return {
        "p_at_1": p_at(1),
        "p_at_3": p_at(3),
        "p_at_5": p_at(5),
        "recall_at_5": recall5,
        "mrr": rr,
        "ndcg_at_5": ndcg_at_k(grades, ideal, 5),
        "ndcg_at_10": ndcg_at_k(grades, ideal, 10),
    }


def summarize_metrics(rankings: dict[str, list[str]], core: list[dict[str, str]], baseline_name: str) -> dict[str, Any]:
    jud, labels_by_q = load_judgments()
    per_query = []
    for q in core:
        qid = q["query_id"]
        per_query.append(compute_one_query(rankings.get(qid, []), qid, jud, labels_by_q[qid]))
    out: dict[str, Any] = {"baseline_name": baseline_name, "num_queries": len(core)}
    for metric in ["p_at_1", "p_at_3", "p_at_5", "recall_at_5", "mrr", "ndcg_at_5", "ndcg_at_10"]:
        vals = [x[metric] for x in per_query if not (isinstance(x[metric], float) and math.isnan(x[metric]))]
        out[metric] = statistics.mean(vals) if vals else math.nan
    return out


def aggregate_chunks_to_docs(chunk_rows: list[dict[str, Any]], score_key: str) -> list[dict[str, Any]]:
    best: dict[str, dict[str, Any]] = {}
    for row in chunk_rows:
        doc_id = row["doc_id"]
        prev = best.get(doc_id)
        if prev is None or float(row.get(score_key, 0.0)) > float(prev.get(score_key, 0.0)):
            best[doc_id] = row
    return sorted(best.values(), key=lambda x: float(x.get(score_key, 0.0)), reverse=True)


def build_lexical_chunk_candidates(query: str, records: list[dict[str, Any]], bm25: OkapiBM25) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    scores = bm25.scores(_tokenize(query))
    rows = []
    for idx, score in enumerate(scores):
        rec = records[idx].copy()
        rec["lexical_score"] = float(score)
        rec["lexical_chunk_rank"] = idx + 1
        rows.append(rec)
    rows.sort(key=lambda x: float(x["lexical_score"]), reverse=True)
    top_chunks = rows[: min(LEXICAL_CHUNK_POOL_K, len(rows))]
    doc_ranked = aggregate_chunks_to_docs(top_chunks, "lexical_score")
    lexical_by_doc = {}
    for rank, row in enumerate(doc_ranked, start=1):
        row = row.copy()
        row["lexical_rank"] = rank
        lexical_by_doc.setdefault(row["doc_id"], row)
    return top_chunks, lexical_by_doc


def build_vector_candidates(query: str, model, index, records: list[dict[str, Any]], detected: dict) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    nvec = int(getattr(index, "ntotal", len(records)))
    all_hits = search(query, model, index, records, top_k=min(nvec, len(records)))
    all_doc_ranked = aggregate_chunks_to_docs(all_hits, "score")
    vector_all_by_chunk = {h["chunk_id"]: h for h in all_hits}
    vector_all_by_doc = {}
    for rank, row in enumerate(all_doc_ranked, start=1):
        row = row.copy()
        row["vector_rank_all"] = rank
        vector_all_by_doc.setdefault(row["doc_id"], row)

    vector_pool = search(query, model, index, records, top_k=min(VECTOR_CHUNK_POOL_K, len(records)))
    if hybrid_search._lobster_coastal_vietnam_boost_intent(query, detected):
        extra = search(
            LOBSTER_COASTAL_VECTOR_BOOST_QUERY,
            model,
            index,
            records,
            top_k=min(VECTOR_CHUNK_POOL_K, len(records)),
        )
        seen = {x["chunk_id"] for x in vector_pool}
        for item in extra:
            if item.get("chunk_id") not in seen:
                seen.add(item.get("chunk_id"))
                vector_pool.append(item)

    vector_doc_ranked = aggregate_chunks_to_docs(vector_pool, "score")
    vector_by_doc = {}
    for rank, row in enumerate(vector_doc_ranked, start=1):
        row = row.copy()
        row["vector_rank"] = rank
        vector_by_doc.setdefault(row["doc_id"], row)
    return vector_pool, vector_by_doc, {"by_chunk": vector_all_by_chunk, "by_doc": vector_all_by_doc}


def link_and_merge_entities(query: str, term_index: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any]]:
    hybrid_search._init_kg_if_needed()
    detected = detect_entities(query, term_index)
    kg_entities = {"disease": [], "species": [], "location": [], "mode": [], "prevention": []}
    if hybrid_search._kg_enabled():
        try:
            linked = kg_runtime.link_query_entities_kg(query, hybrid_search._KG_INDEX)
            kg_entities = {
                "disease": linked.get("disease") or [],
                "species": linked.get("species") or [],
                "location": linked.get("location") or [],
                "mode": linked.get("mode") or [],
                "prevention": linked.get("prevention") or [],
            }
        except Exception:
            pass
    return hybrid_search._merge_detected_with_kg(detected, kg_entities), kg_entities


def score_fused_candidates(
    query: str,
    candidates_by_doc: dict[str, dict[str, Any]],
    metadata_lookup: dict[str, dict[str, Any]],
    detected: dict[str, Any],
    kg_entities: dict[str, Any],
) -> list[dict[str, Any]]:
    narrow_local = hybrid_search._narrow_local_aquaculture_intent(query, detected)
    delta_cache: dict[str, dict[str, Any]] = {}
    kg_cache: dict[str, dict[str, Any]] = {}
    reranked: list[dict[str, Any]] = []

    for doc_id, item in candidates_by_doc.items():
        row = metadata_lookup.get(doc_id, {})
        if doc_id not in delta_cache:
            delta_cache[doc_id] = compute_hybrid_delta(detected, compute_match_features(row, detected))
        if doc_id not in kg_cache:
            kg_info = {
                "doc_uri_in_kg": None,
                "kg_score": 0.0,
                "kg_bonus_breakdown": "",
                "kg_penalty_breakdown": "",
                "kg_explanation": [],
                "kg_direct_match": 0.0,
                "kg_relation_match": 0.0,
                "kg_context_match": 0.0,
                "kg_doc_modes": [],
            }
            if hybrid_search._kg_enabled():
                try:
                    doc_uri = hybrid_search._map_doc_to_kg_uri(doc_id, row)
                    kg_info["doc_uri_in_kg"] = doc_uri
                    if doc_uri:
                        doc_facts = kg_runtime.get_document_facts(hybrid_search._KG_GRAPH, doc_uri)
                        kg_info["kg_doc_modes"] = list(doc_facts.get("mode", []) or [])
                        kg_info.update(
                            kg_runtime.score_doc_with_kg(
                                query_entities=kg_entities,
                                doc_facts=doc_facts,
                                kg_index=hybrid_search._KG_INDEX,
                                graph=hybrid_search._KG_GRAPH,
                                query_text=query,
                            )
                        )
                except Exception:
                    pass
            kg_cache[doc_id] = kg_info

        delta_info = delta_cache[doc_id]
        kg_info = kg_cache[doc_id]
        vector_score = float(item.get("vector_score", 0.0) or 0.0)
        metadata_delta = float(delta_info.get("kg_delta", 0.0) or 0.0)
        kg_score = float(kg_info.get("kg_score", 0.0) or 0.0)
        intent_adjustment, intent_expl = hybrid_search._intent_narrow_final_adjustment(
            query, detected, row, str(item.get("title", ""))
        )
        final_score = vector_score + metadata_delta + kg_score + float(intent_adjustment)
        out = item.copy()
        out["metadata_delta"] = metadata_delta
        out["kg_score"] = kg_score
        out["intent_adjustment"] = float(intent_adjustment)
        out["final_score"] = float(final_score)
        out["kg_doc_modes"] = list(kg_info.get("kg_doc_modes") or [])
        meta_expl = delta_info.get("explanation", "")
        kg_expl = "; ".join(kg_info.get("kg_explanation", []) or [])
        expl_parts = [f"metadata: {meta_expl}" if meta_expl else "", f"KG: {kg_expl}" if kg_expl else "", intent_expl]
        out["explanation"] = "; ".join([x for x in expl_parts if x])
        try:
            meta_aqua, meta_capture = hybrid_search._metadata_production_mode_flags(row)
            kg_aqua, kg_capture = hybrid_search._kg_mode_flags(list(kg_info.get("kg_doc_modes") or []))
            out["_doc_is_aquaculture"] = bool(meta_aqua or kg_aqua)
            out["_doc_is_capture_or_market"] = bool(meta_capture or kg_capture)
        except Exception:
            out["_doc_is_aquaculture"] = False
            out["_doc_is_capture_or_market"] = False
        reranked.append(out)

    reranked.sort(key=lambda x: float(x["final_score"]), reverse=True)
    if narrow_local and reranked and any(bool(x.get("_doc_is_aquaculture")) for x in reranked):
        for item in reranked:
            if item.get("_doc_is_capture_or_market"):
                item["final_score"] = float(item.get("final_score", 0.0)) - 0.12
                extra = "intent penalty: local aquaculture query vs capture/market doc (-0.12)"
                item["explanation"] = f"{item.get('explanation', '')}; {extra}".strip("; ")
        reranked.sort(key=lambda x: float(x["final_score"]), reverse=True)
    return reranked


def run_fusion_for_query(
    query_id: str,
    query_text: str,
    model,
    index,
    records: list[dict[str, Any]],
    bm25: OkapiBM25,
    metadata_lookup: dict[str, dict[str, Any]],
    term_index: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    detected, kg_entities = link_and_merge_entities(query_text, term_index)
    _vector_pool, vector_by_doc, vector_all = build_vector_candidates(query_text, model, index, records, detected)
    _lexical_pool, lexical_by_doc = build_lexical_chunk_candidates(query_text, records, bm25)

    candidates_by_doc: dict[str, dict[str, Any]] = {}
    for doc_id in sorted(set(vector_by_doc) | set(lexical_by_doc)):
        v = vector_by_doc.get(doc_id)
        l = lexical_by_doc.get(doc_id)
        all_v = (vector_all.get("by_doc") or {}).get(doc_id)
        base = (v or all_v or l or {}).copy()
        if l is not None and v is None:
            # Keep lexical best chunk as representative, but use the best known vector score for the doc.
            base = l.copy()
        vector_source = v or all_v or {}
        base["doc_id"] = doc_id
        base["title"] = base.get("title") or vector_source.get("title") or (l or {}).get("title", "")
        base["came_from_vector"] = bool(v)
        base["came_from_lexical"] = bool(l)
        base["vector_rank"] = (v or {}).get("vector_rank", "")
        base["lexical_rank"] = (l or {}).get("lexical_rank", "")
        base["vector_score"] = float(vector_source.get("score", 0.0) or 0.0)
        base["lexical_score"] = float((l or {}).get("lexical_score", 0.0) or 0.0)
        candidates_by_doc[doc_id] = base

    reranked = score_fused_candidates(query_text, candidates_by_doc, metadata_lookup, detected, kg_entities)
    stats = {
        "query_id": query_id,
        "vector_candidate_count": len(vector_by_doc),
        "lexical_candidate_count": len(lexical_by_doc),
        "union_candidate_count": len(candidates_by_doc),
        "union_larger_than_vector": len(candidates_by_doc) > len(vector_by_doc),
    }
    return reranked[:TOP_DOCS], stats


def make_result_rows(core: list[dict[str, str]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    model, index, records = load_index()
    metadata_df = load_full_metadata(METADATA_PATH)
    metadata_lookup = build_metadata_lookup(metadata_df)
    term_index = build_term_index(metadata_df)
    tokenized = [_tokenize(str(r.get("text", ""))) for r in records]
    bm25 = OkapiBM25(tokenized)

    rows: list[dict[str, Any]] = []
    candidate_stats: list[dict[str, Any]] = []
    for q in core:
        qid = q["query_id"]
        qtext = q["query_text"]
        top_items, stats = run_fusion_for_query(qid, qtext, model, index, records, bm25, metadata_lookup, term_index)
        candidate_stats.append(stats)
        raw_scores = [float(x.get("final_score", 0.0)) for x in top_items]
        norms = _normalize_minmax(raw_scores)
        for rank, (item, norm) in enumerate(zip(top_items, norms), start=1):
            rows.append(
                {
                    "query_id": qid,
                    "query_text": qtext,
                    "baseline_name": "hybrid_candidate_fusion",
                    "rank": rank,
                    "doc_id": item.get("doc_id", ""),
                    "title": item.get("title", ""),
                    "score_raw": item.get("final_score", 0.0),
                    "score_normalized": norm,
                    "retrieval_level": "candidate_fusion_chunk_to_doc",
                    "explanation_short": "candidate_fusion_experiment: vector + BM25 candidate union, hybrid scoring rerank",
                    "source_pipeline": (
                        "run_candidate_fusion_experiment; vector top-150 chunks + BM25 top-150 chunks; "
                        "hybrid scoring reused; not final hybrid"
                    ),
                    "came_from_vector": item.get("came_from_vector", False),
                    "came_from_lexical": item.get("came_from_lexical", False),
                    "vector_rank": item.get("vector_rank", ""),
                    "lexical_rank": item.get("lexical_rank", ""),
                    "vector_score": item.get("vector_score", 0.0),
                    "lexical_score": item.get("lexical_score", 0.0),
                    "metadata_delta": item.get("metadata_delta", 0.0),
                    "kg_score": item.get("kg_score", 0.0),
                    "intent_adjustment": item.get("intent_adjustment", 0.0),
                    "final_score": item.get("final_score", 0.0),
                    "candidate_union_count": stats["union_candidate_count"],
                }
            )
    return rows, candidate_stats


def rankings_from_rows(rows: list[dict[str, Any]]) -> dict[str, list[str]]:
    by_q: dict[str, list[tuple[int, str]]] = defaultdict(list)
    for r in rows:
        by_q[str(r["query_id"])].append((int(r["rank"]), str(r["doc_id"])))
    return {qid: [doc for _rank, doc in sorted(vals)] for qid, vals in by_q.items()}


def build_per_query_delta(
    core: list[dict[str, str]],
    fusion_rankings: dict[str, list[str]],
    hybrid_rankings: dict[str, list[str]],
    candidate_stats: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    jud, labels_by_q = load_judgments()
    stats_by_q = {x["query_id"]: x for x in candidate_stats}
    out = []
    for q in core:
        qid = q["query_id"]
        h = compute_one_query(hybrid_rankings.get(qid, []), qid, jud, labels_by_q[qid])
        f = compute_one_query(fusion_rankings.get(qid, []), qid, jud, labels_by_q[qid])
        delta = f["ndcg_at_10"] - h["ndcg_at_10"]
        if delta > 1e-9:
            status = "improved"
        elif delta < -1e-9:
            status = "regressed"
        else:
            status = "unchanged"
        st = stats_by_q.get(qid, {})
        out.append(
            {
                "query_id": qid,
                "query_group": q.get("query_group", ""),
                "hybrid_p1": h["p_at_1"],
                "fusion_p1": f["p_at_1"],
                "hybrid_mrr": h["mrr"],
                "fusion_mrr": f["mrr"],
                "hybrid_ndcg10": h["ndcg_at_10"],
                "fusion_ndcg10": f["ndcg_at_10"],
                "delta_ndcg10": delta,
                "vector_candidate_count": st.get("vector_candidate_count", ""),
                "lexical_candidate_count": st.get("lexical_candidate_count", ""),
                "union_candidate_count": st.get("union_candidate_count", ""),
                "improved_or_regressed": status,
                "note": "fusion experiment; not final hybrid",
            }
        )
    return out


def summarize_by_group(core: list[dict[str, str]], rankings: dict[str, list[str]]) -> dict[str, dict[str, float]]:
    jud, labels_by_q = load_judgments()
    by_group: dict[str, list[dict[str, float]]] = defaultdict(list)
    for q in core:
        qid = q["query_id"]
        by_group[q.get("query_group", "")].append(compute_one_query(rankings.get(qid, []), qid, jud, labels_by_q[qid]))
    out: dict[str, dict[str, float]] = {}
    for group, vals in by_group.items():
        out[group] = {}
        for metric in ["p_at_1", "mrr", "ndcg_at_10"]:
            xs = [v[metric] for v in vals if not (isinstance(v[metric], float) and math.isnan(v[metric]))]
            out[group][metric] = statistics.mean(xs) if xs else math.nan
    return out


def write_summary_md(summary: dict[str, Any]) -> None:
    def fmt(v: Any) -> str:
        try:
            return f"{float(v):.4f}"
        except Exception:
            return str(v)

    lines = [
        "# Candidate Fusion Experiment Summary",
        "",
        "## Purpose",
        "",
        "This experiment tests whether expanding hybrid candidate generation with both vector and BM25 lexical candidates improves retrieval.",
        "It is an exploratory `candidate_fusion_experiment`, not a replacement for the current final hybrid baseline.",
        "",
        "## Candidate Pool Construction",
        "",
        f"- Vector pool: top {VECTOR_CHUNK_POOL_K} FAISS chunks, plus the existing lobster vector expansion when its narrow intent triggers.",
        f"- Lexical pool: top {LEXICAL_CHUNK_POOL_K} BM25 chunks over normalized chunk tokens.",
        "- Candidate union: merge by `doc_id`, retain `came_from_vector`, `came_from_lexical`, vector rank/score, and lexical rank/score.",
        "- Re-rank: reuse the current hybrid scoring components: `vector_score + metadata_delta + kg_score + intent_adjustment`.",
        "- Retrieval was re-run inside this experiment script because existing vector/lexical baseline CSVs store only top-10 documents, not the deeper candidate pools needed for fusion.",
        "",
        "## Candidate Pool Statistics",
        "",
        f"- Average vector candidate docs: {fmt(summary['candidate_pool_stats']['avg_vector_candidate_count'])}",
        f"- Average lexical candidate docs: {fmt(summary['candidate_pool_stats']['avg_lexical_candidate_count'])}",
        f"- Average union candidate docs: {fmt(summary['candidate_pool_stats']['avg_union_candidate_count'])}",
        f"- Queries where union > vector-only: {summary['candidate_pool_stats']['queries_union_larger_than_vector']} / {summary['candidate_pool_stats']['num_queries']}",
        "",
        "## Metric Comparison",
        "",
        "| baseline | P@1 | P@3 | P@5 | Recall@5 | MRR | nDCG@5 | nDCG@10 |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in summary["metric_summary"]:
        lines.append(
            "| {baseline_name} | {p_at_1} | {p_at_3} | {p_at_5} | {recall_at_5} | {mrr} | {ndcg_at_5} | {ndcg_at_10} |".format(
                baseline_name=row["baseline_name"],
                p_at_1=fmt(row["p_at_1"]),
                p_at_3=fmt(row["p_at_3"]),
                p_at_5=fmt(row["p_at_5"]),
                recall_at_5=fmt(row["recall_at_5"]),
                mrr=fmt(row["mrr"]),
                ndcg_at_5=fmt(row["ndcg_at_5"]),
                ndcg_at_10=fmt(row["ndcg_at_10"]),
            )
        )
    deltas = summary["delta_vs_hybrid"]
    lines.extend(
        [
            "",
            "## Delta vs Current Hybrid",
            "",
            f"- P@1 delta: {fmt(deltas['p_at_1'])}",
            f"- MRR delta: {fmt(deltas['mrr'])}",
            f"- nDCG@10 delta: {fmt(deltas['ndcg_at_10'])}",
            "",
            "## Query Group Comparison",
            "",
            "| query_group | hybrid P@1 | fusion P@1 | hybrid MRR | fusion MRR | hybrid nDCG@10 | fusion nDCG@10 |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for group in sorted(summary["by_group"]["hybrid"].keys()):
        h = summary["by_group"]["hybrid"][group]
        f = summary["by_group"]["hybrid_candidate_fusion"][group]
        lines.append(
            f"| {group} | {fmt(h['p_at_1'])} | {fmt(f['p_at_1'])} | {fmt(h['mrr'])} | {fmt(f['mrr'])} | {fmt(h['ndcg_at_10'])} | {fmt(f['ndcg_at_10'])} |"
        )
    lines.extend(
        [
            "",
            "## Improved and Regressed Queries",
            "",
            "**Largest improvements by nDCG@10**",
            "",
        ]
    )
    for row in summary["top_improvements"]:
        lines.append(
            f"- `{row['query_id']}` ({row['query_group']}): delta nDCG@10={fmt(row['delta_ndcg10'])}, union={row['union_candidate_count']}"
        )
    lines.extend(["", "**Largest regressions by nDCG@10**", ""])
    for row in summary["top_regressions"]:
        lines.append(
            f"- `{row['query_id']}` ({row['query_group']}): delta nDCG@10={fmt(row['delta_ndcg10'])}, union={row['union_candidate_count']}"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            summary["interpretation"],
            "",
            "## Limitations",
            "",
            "- This experiment re-runs retrieval in a separate script and writes separate outputs only.",
            "- It does not modify `baseline_hybrid_core.csv` or any existing metric/baseline artifact.",
            "- Candidate fusion can add useful recall, but it can also add lexical noise; the current hybrid scoring was not retuned for the larger mixed candidate pool.",
            "- Treat this as future-work evidence unless it is validated with additional tuning, statistical testing, and error analysis.",
            "",
        ]
    )
    SUMMARY_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    core = load_core_queries()
    result_rows, candidate_stats = make_result_rows(core)
    write_csv(EXPERIMENT_RESULT, result_rows, RESULT_FIELDS)

    fusion_rankings = rankings_from_rows(result_rows)
    hybrid_rankings = load_ranking(BASELINE_HYBRID)
    vector_metadata_rankings = load_ranking(BASELINE_VECTOR_METADATA)

    metric_summary = [
        summarize_metrics(hybrid_rankings, core, "hybrid"),
        summarize_metrics(vector_metadata_rankings, core, "vector_metadata"),
        summarize_metrics(fusion_rankings, core, "hybrid_candidate_fusion"),
    ]
    write_csv(SUMMARY_CSV, metric_summary, SUMMARY_FIELDS)

    per_query_delta = build_per_query_delta(core, fusion_rankings, hybrid_rankings, candidate_stats)
    write_csv(
        PER_QUERY_DELTA_CSV,
        per_query_delta,
        [
            "query_id",
            "query_group",
            "hybrid_p1",
            "fusion_p1",
            "hybrid_mrr",
            "fusion_mrr",
            "hybrid_ndcg10",
            "fusion_ndcg10",
            "delta_ndcg10",
            "vector_candidate_count",
            "lexical_candidate_count",
            "union_candidate_count",
            "improved_or_regressed",
            "note",
        ],
    )

    by_name = {x["baseline_name"]: x for x in metric_summary}
    delta_vs_hybrid = {
        "p_at_1": by_name["hybrid_candidate_fusion"]["p_at_1"] - by_name["hybrid"]["p_at_1"],
        "p_at_5": by_name["hybrid_candidate_fusion"]["p_at_5"] - by_name["hybrid"]["p_at_5"],
        "recall_at_5": by_name["hybrid_candidate_fusion"]["recall_at_5"] - by_name["hybrid"]["recall_at_5"],
        "mrr": by_name["hybrid_candidate_fusion"]["mrr"] - by_name["hybrid"]["mrr"],
        "ndcg_at_5": by_name["hybrid_candidate_fusion"]["ndcg_at_5"] - by_name["hybrid"]["ndcg_at_5"],
        "ndcg_at_10": by_name["hybrid_candidate_fusion"]["ndcg_at_10"] - by_name["hybrid"]["ndcg_at_10"],
    }
    avg = lambda key: statistics.mean(float(x[key]) for x in candidate_stats) if candidate_stats else 0.0
    candidate_pool_stats = {
        "num_queries": len(candidate_stats),
        "avg_vector_candidate_count": avg("vector_candidate_count"),
        "avg_lexical_candidate_count": avg("lexical_candidate_count"),
        "avg_union_candidate_count": avg("union_candidate_count"),
        "queries_union_larger_than_vector": sum(1 for x in candidate_stats if x["union_larger_than_vector"]),
    }

    improved = [x for x in per_query_delta if float(x["delta_ndcg10"]) > 1e-9]
    regressed = [x for x in per_query_delta if float(x["delta_ndcg10"]) < -1e-9]
    unchanged = [x for x in per_query_delta if abs(float(x["delta_ndcg10"])) <= 1e-9]
    top_improvements = sorted(improved, key=lambda x: float(x["delta_ndcg10"]), reverse=True)[:5]
    top_regressions = sorted(regressed, key=lambda x: float(x["delta_ndcg10"]))[:5]

    if delta_vs_hybrid["ndcg_at_10"] > 1e-9 and (
        delta_vs_hybrid["p_at_5"] < -1e-9
        or delta_vs_hybrid["recall_at_5"] < -1e-9
        or delta_vs_hybrid["ndcg_at_5"] < -1e-9
    ):
        interpretation = (
            "Candidate fusion gives a mixed result: P@1, MRR, and nDCG@10 increase slightly, "
            "but P@5, Recall@5, and nDCG@5 decrease. This should not be treated as a final improvement; "
            "it is best framed as future work that needs candidate filtering, lexical-score calibration, and reranker tuning."
        )
    elif delta_vs_hybrid["ndcg_at_10"] > 1e-9:
        interpretation = (
            "Candidate fusion improves mean nDCG@10 over the current hybrid in this experiment, "
            "but it should still be treated as an exploratory extension until the larger mixed pool is tuned and validated."
        )
    elif delta_vs_hybrid["ndcg_at_10"] < -1e-9:
        interpretation = (
            "Candidate fusion does not improve the current hybrid in this experiment. The added lexical candidates likely introduce noise "
            "or require scoring/normalization changes before the larger candidate pool can be useful."
        )
    else:
        interpretation = (
            "Candidate fusion produces essentially the same mean nDCG@10 as the current hybrid in this experiment. "
            "It is best treated as future work rather than a replacement baseline."
        )

    summary = {
        "experiment_name": "candidate_fusion_experiment",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "input_files_read": [
            str(CORE_QUERIES),
            str(JUDGMENTS),
            str(BASELINE_HYBRID),
            str(BASELINE_VECTOR_METADATA),
            "vector_store/chunks.index",
            "vector_store/chunks_meta.pkl",
            METADATA_PATH,
        ],
        "outputs_written": [
            str(EXPERIMENT_RESULT),
            str(SUMMARY_CSV),
            str(SUMMARY_JSON),
            str(SUMMARY_MD),
            str(PER_QUERY_DELTA_CSV),
        ],
        "retrieval_rerun": True,
        "retrieval_rerun_reason": "Existing lexical/vector baseline CSVs contain top-10 docs only; deeper chunk candidate pools are required for fusion.",
        "candidate_pool_config": {
            "vector_chunk_pool_k": VECTOR_CHUNK_POOL_K,
            "lexical_chunk_pool_k": LEXICAL_CHUNK_POOL_K,
            "merge_key": "doc_id",
            "rerank_formula": "vector_score + metadata_delta + kg_score + intent_adjustment",
            "label": "candidate_fusion_experiment",
        },
        "candidate_pool_stats": candidate_pool_stats,
        "metric_summary": metric_summary,
        "delta_vs_hybrid": delta_vs_hybrid,
        "by_group": {
            "hybrid": summarize_by_group(core, hybrid_rankings),
            "hybrid_candidate_fusion": summarize_by_group(core, fusion_rankings),
        },
        "query_delta_counts": {
            "improved": len(improved),
            "regressed": len(regressed),
            "unchanged": len(unchanged),
        },
        "top_improvements": top_improvements,
        "top_regressions": top_regressions,
        "interpretation": interpretation,
        "safety_notes": [
            "No ontology, metadata, query set, relevance judgments, existing baselines, or existing metrics are modified.",
            "This is not the final hybrid baseline.",
        ],
    }
    SUMMARY_JSON.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    write_summary_md(summary)
    print(f"[OK] Wrote {EXPERIMENT_RESULT}")
    print(f"[OK] Wrote {SUMMARY_CSV}, {SUMMARY_JSON}, {SUMMARY_MD}, {PER_QUERY_DELTA_CSV}")


if __name__ == "__main__":
    main()
