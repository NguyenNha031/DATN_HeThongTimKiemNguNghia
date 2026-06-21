"""
Bước 7 — đo latency truy vấn cho 5 baseline trên core query set.

Chạy từ project root:
  python measure_core_baseline_latency.py

Không ghi đè baseline_*_core.csv; chỉ cập nhật data/eval/metrics/baseline_latency_summary.csv
và (tùy chọn) baseline_latency_per_query.csv.
"""
from __future__ import annotations

import io
import statistics
import sys
import time
from contextlib import redirect_stdout
from pathlib import Path

import pandas as pd

import hybrid_search
import run_core_baselines as rcb
from run_core_baselines import (
    CORE_QUERIES,
    HYBRID_CANDIDATE_CHUNKS,
    OkapiBM25,
    TOP_DOCS,
    hybrid_rows,
    lexical_bm25_rows,
    ontology_sparql_rows,
    vector_metadata_kg_no_intent_rows,
    vector_metadata_rows,
    vector_rows,
)
from hybrid_search import (
    METADATA_PATH,
    build_metadata_lookup,
    build_term_index,
    load_full_metadata,
)
from vector_search import load_index

PROJECT_ROOT = Path(__file__).resolve().parent
METRICS_DIR = PROJECT_ROOT / "data" / "eval" / "metrics"

RUNS_PER_QUERY = 5
LATENCY_SCOPE = (
    "Wall-clock per query: full baseline row builder in run_core_baselines "
    "(BM25 all-chunks+pool / FAISS search+pool / KG score+SPARQL+hybrid_search as applicable), "
    "including building top-10 row dicts; excludes model/index/KG load and pandas read of query CSV."
)


def _load_queries() -> list[tuple[str, str]]:
    df_q = pd.read_csv(CORE_QUERIES, encoding="utf-8-sig")
    return [(str(r["query_id"]), str(r["query_text"])) for _, r in df_q.iterrows()]


def _time_ms(fn) -> float:
    t0 = time.perf_counter()
    fn()
    return (time.perf_counter() - t0) * 1000.0


def _run_silent(fn) -> None:
    buf = io.StringIO()
    with redirect_stdout(buf):
        fn()


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    queries = _load_queries()
    nq = len(queries)
    if nq == 0:
        raise SystemExit("No queries in core set")

    # --- Load resources (NOT included in per-query latency) ---
    print("[STEP] Loading corpus + BM25...")
    records = rcb._load_chunk_records()
    tok_corpus = [rcb._tokenize(r["text"]) for r in records]
    bm25 = OkapiBM25(tok_corpus)

    print("[STEP] Loading metadata + term index...")
    df_meta = load_full_metadata(str(METADATA_PATH))
    metadata_lookup = build_metadata_lookup(df_meta)
    term_index = build_term_index(df_meta)
    title_by_doc = {str(r["doc_id"]): str(r.get("title", "")) for _, r in df_meta.iterrows()}

    print("[STEP] Loading embedding model + FAISS index...")
    model, index, vec_records = load_index()

    print("[STEP] Initializing KG (same as run_core_baselines)...")
    hybrid_search._init_kg_if_needed()
    graph = hybrid_search._KG_GRAPH
    kg_index = hybrid_search._KG_INDEX
    map_fn = hybrid_search._map_doc_to_kg_uri
    kg_ok = graph is not None and kg_index is not None
    if not kg_ok:
        print("[WARN] KG unavailable; ontology_sparql timing uses placeholder path from run_core_baselines.")

    _orig_final = hybrid_search.FINAL_K
    _orig_cand = hybrid_search.CANDIDATE_K
    hybrid_search.FINAL_K = TOP_DOCS
    hybrid_search.CANDIDATE_K = HYBRID_CANDIDATE_CHUNKS

    per_query_rows: list[dict] = []
    summary_rows: list[dict] = []

    try:
        baselines: list[tuple[str, callable]] = [
            (
                "lexical",
                lambda qid, qt: lexical_bm25_rows(qid, qt, records, bm25, title_by_doc),
            ),
            (
                "vector",
                lambda qid, qt: vector_rows(qid, qt, model, index, vec_records, title_by_doc),
            ),
            (
                "vector_metadata",
                lambda qid, qt: vector_metadata_rows(
                    qid, qt, model, index, vec_records, metadata_lookup, term_index, title_by_doc
                ),
            ),
            (
                "vector_metadata_kg_no_intent",
                lambda qid, qt: vector_metadata_kg_no_intent_rows(
                    qid, qt, model, index, vec_records, metadata_lookup, term_index, title_by_doc
                ),
            ),
        ]

        if kg_ok:
            baselines.append(
                (
                    "ontology_sparql",
                    lambda qid, qt: ontology_sparql_rows(
                        qid, qt, graph, kg_index, metadata_lookup, title_by_doc, map_fn
                    ),
                )
            )
        else:
            summary_rows.append(
                {
                    "baseline_name": "ontology_sparql",
                    "num_queries": str(nq),
                    "runs_per_query": "0",
                    "warmup_done": "skipped",
                    "latency_scope": LATENCY_SCOPE,
                    "mean_query_latency_ms": "",
                    "median_query_latency_ms": "",
                    "min_query_latency_ms": "",
                    "max_query_latency_ms": "",
                    "notes": "KG not loaded; same placeholder ranking as run_core_baselines without graph — latency not measured",
                }
            )

        baselines.append(
            (
                "hybrid",
                lambda qid, qt: hybrid_rows(
                    qid, qt, model, index, vec_records, metadata_lookup, term_index, title_by_doc
                ),
            )
        )

        for baseline_name, builder in baselines:
            qid0, qt0 = queries[0]
            print(f"[WARMUP] {baseline_name}...")
            _run_silent(lambda: builder(qid0, qt0))

            means_per_q: list[float] = []
            for qid, qtext in queries:
                run_times: list[float] = []
                for _ in range(RUNS_PER_QUERY):
                    ms = _time_ms(lambda: _run_silent(lambda: builder(qid, qtext)))
                    run_times.append(ms)
                mq = statistics.mean(run_times)
                means_per_q.append(mq)
                per_query_rows.append(
                    {
                        "baseline_name": baseline_name,
                        "query_id": qid,
                        "runs_per_query": RUNS_PER_QUERY,
                        "mean_latency_ms": round(mq, 3),
                        "stdev_latency_ms": round(statistics.stdev(run_times), 3) if len(run_times) > 1 else 0.0,
                    }
                )

            summary_rows.append(
                {
                    "baseline_name": baseline_name,
                    "num_queries": str(nq),
                    "runs_per_query": str(RUNS_PER_QUERY),
                    "warmup_done": "yes (1 call first query)",
                    "latency_scope": LATENCY_SCOPE,
                    "mean_query_latency_ms": round(statistics.mean(means_per_q), 3),
                    "median_query_latency_ms": round(statistics.median(means_per_q), 3),
                    "min_query_latency_ms": round(min(means_per_q), 3),
                    "max_query_latency_ms": round(max(means_per_q), 3),
                    "notes": (
                        "Windows; CPU; single process. Stdout suppressed during timed calls. "
                        "Hybrid/vector_metadata use FINAL_K=10 CANDIDATE_K=150 as in run_core_baselines.main."
                    ),
                }
            )
            print(
                f"[OK] {baseline_name}: mean over queries={summary_rows[-1]['mean_query_latency_ms']} ms "
                f"(median of per-query means={summary_rows[-1]['median_query_latency_ms']} ms)"
            )

    finally:
        hybrid_search.FINAL_K = _orig_final
        hybrid_search.CANDIDATE_K = _orig_cand

    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    summary_path = METRICS_DIR / "baseline_latency_summary.csv"
    import csv

    fields = [
        "baseline_name",
        "num_queries",
        "runs_per_query",
        "warmup_done",
        "latency_scope",
        "mean_query_latency_ms",
        "median_query_latency_ms",
        "min_query_latency_ms",
        "max_query_latency_ms",
        "notes",
    ]
    with open(summary_path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(summary_rows)

    per_path = METRICS_DIR / "baseline_latency_per_query.csv"
    pq_fields = [
        "baseline_name",
        "query_id",
        "runs_per_query",
        "mean_latency_ms",
        "stdev_latency_ms",
    ]
    with open(per_path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=pq_fields)
        w.writeheader()
        w.writerows(per_query_rows)

    print(f"[DONE] Wrote {summary_path.name} + {per_path.name}")


if __name__ == "__main__":
    main()
