"""
Bước 3: chạy baseline retrieval trên core query set, xuất CSV chuẩn hóa.
Không tính metric; không sửa hybrid scoring / ontology.

Chạy từ thư mục project:
  python run_core_baselines.py
"""
from __future__ import annotations

import csv
import math
import pickle
from collections import defaultdict
from pathlib import Path

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
    normalize_text,
)
from hybrid_search import _lobster_coastal_vietnam_boost_intent as _lobster_boost
from hybrid_search import _metadata_production_mode_flags as _meta_pm_flags
from hybrid_search import _narrow_local_aquaculture_intent as _narrow_local
from vector_search import INDEX_DIR, load_index, search

PROJECT_ROOT = Path(__file__).resolve().parent
CORE_QUERIES = PROJECT_ROOT / "data" / "eval" / "final_query_set_core.csv"
RESULTS_DIR = PROJECT_ROOT / "data" / "eval" / "results"

# Top doc mỗi query (bước 4 dùng P@k)
TOP_DOCS = 10
# Số chunk vector pool trước khi gộp doc (vector / vector_metadata)
CHUNK_POOL_K = 120
# Pool cho hybrid / vector_metadata: chỉ tăng số chunk vào rerank, không đổi công thức điểm
HYBRID_CANDIDATE_CHUNKS = 150

BASELINE_FILES = {
    "lexical": RESULTS_DIR / "baseline_lexical_core.csv",
    "vector": RESULTS_DIR / "baseline_vector_core.csv",
    "vector_metadata": RESULTS_DIR / "baseline_vector_metadata_core.csv",
    "ontology_sparql": RESULTS_DIR / "baseline_ontology_sparql_core.csv",
    "hybrid": RESULTS_DIR / "baseline_hybrid_core.csv",
}

CSV_FIELDS = [
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
]


def _tokenize(s: str) -> list[str]:
    return [t for t in normalize_text(s).split() if t]


class OkapiBM25:
    """BM25Okapi trên token đã chuẩn hóa (không ontology / KG)."""

    def __init__(self, tokenized_corpus: list[list[str]], k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus = tokenized_corpus
        self.N = len(tokenized_corpus)
        if self.N == 0:
            self.avgdl = 0.0
            self.idf = {}
            return
        self.doc_len = [len(d) for d in tokenized_corpus]
        self.avgdl = sum(self.doc_len) / self.N
        df: dict[str, int] = defaultdict(int)
        for d in tokenized_corpus:
            for t in set(d):
                df[t] += 1
        self.idf = {}
        for t, n in df.items():
            # idf cho BM25+
            self.idf[t] = math.log(1 + (self.N - n + 0.5) / (n + 0.5))

    def scores(self, query_tokens: list[str]) -> list[float]:
        if self.N == 0:
            return []
        scores = [0.0] * self.N
        for i, doc in enumerate(self.corpus):
            dl = self.doc_len[i]
            s = 0.0
            freqs: dict[str, int] = defaultdict(int)
            for t in doc:
                freqs[t] += 1
            for q in query_tokens:
                if q not in freqs:
                    continue
                idf = self.idf.get(q, 0.0)
                f = freqs[q]
                denom = f + self.k1 * (1 - self.b + self.b * dl / self.avgdl) if self.avgdl > 0 else f + self.k1
                s += idf * (f * (self.k1 + 1)) / denom
            scores[i] = s
        return scores


def _load_chunk_records() -> list[dict]:
    meta_path = INDEX_DIR / "chunks_meta.pkl"
    if not meta_path.exists():
        raise FileNotFoundError(f"Missing {meta_path}; build vector index first.")
    with open(meta_path, "rb") as f:
        return pickle.load(f)


def _aggregate_chunks_to_docs(
    chunk_rows: list[tuple[dict, float]],
) -> list[tuple[str, float, dict]]:
    """Mỗi doc_id lấy chunk có điểm cao nhất (max-pooling)."""
    best: dict[str, tuple[float, dict]] = {}
    for rec, sc in chunk_rows:
        did = rec["doc_id"]
        prev = best.get(did)
        if prev is None or sc > prev[0]:
            best[did] = (sc, rec)
    out = [(did, sc, rec) for did, (sc, rec) in best.items()]
    out.sort(key=lambda x: x[1], reverse=True)
    return out


def _normalize_minmax(values: list[float]) -> list[float]:
    if not values:
        return []
    lo, hi = min(values), max(values)
    if hi <= lo:
        return [1.0] * len(values)
    return [(v - lo) / (hi - lo) for v in values]


def lexical_bm25_rows(
    query_id: str,
    query_text: str,
    records: list[dict],
    bm25: OkapiBM25,
    title_by_doc: dict[str, str],
) -> list[dict]:
    """
    BM25 trên mọi chunk (cùng công thức Okapi); max-pool theo doc trên **toàn corpus chunk**
    rồi lấy top TOP_DOCS doc — tránh lỗi chỉ xét prefix chunk khiến <10 doc khác biệt.
    """
    qtok = _tokenize(query_text)
    sc = bm25.scores(qtok)
    indexed = [(records[i], sc[i]) for i in range(len(records))]
    indexed.sort(key=lambda x: x[1], reverse=True)
    doc_ranked = _aggregate_chunks_to_docs(indexed)
    doc_ranked = doc_ranked[:TOP_DOCS]
    raws = [x[1] for x in doc_ranked]
    norms = _normalize_minmax(raws)
    rows = []
    for rank, ((doc_id, raw, _), norm) in enumerate(zip(doc_ranked, norms), start=1):
        rows.append(
            {
                "query_id": query_id,
                "query_text": query_text,
                "baseline_name": "lexical",
                "rank": rank,
                "doc_id": doc_id,
                "title": title_by_doc.get(doc_id, ""),
                "score_raw": raw,
                "score_normalized": norm,
                "retrieval_level": "chunk_to_doc",
                "explanation_short": "BM25 Okapi keyword overlap on normalized chunk tokens",
                "source_pipeline": "run_core_baselines.OkapiBM25 (all chunks scored) + max-pool per doc",
            }
        )
    return rows


def vector_rows(
    query_id: str,
    query_text: str,
    model,
    index,
    records: list[dict],
    title_by_doc: dict[str, str],
) -> list[dict]:
    """
    FAISS trả về đủ neighbor = số vector trong index (cùng similarity IP); max-pool theo doc
    trên toàn chunk rồi top TOP_DOCS — không cắt sớm ở top_k nhỏ.
    """
    nvec = int(getattr(index, "ntotal", len(records)))
    top_k = min(max(nvec, 1), len(records))
    hits = search(query_text, model, index, records, top_k=top_k)
    chunk_rows = [(h, float(h["score"])) for h in hits]
    doc_ranked = _aggregate_chunks_to_docs(chunk_rows)[:TOP_DOCS]
    raws = [x[1] for x in doc_ranked]
    norms = _normalize_minmax(raws)
    rows = []
    for rank, ((doc_id, raw, _), norm) in enumerate(zip(doc_ranked, norms), start=1):
        rows.append(
            {
                "query_id": query_id,
                "query_text": query_text,
                "baseline_name": "vector",
                "rank": rank,
                "doc_id": doc_id,
                "title": title_by_doc.get(doc_id, ""),
                "score_raw": raw,
                "score_normalized": norm,
                "retrieval_level": "chunk_to_doc",
                "explanation_short": "cosine embedding similarity (FAISS IP, normalized vectors)",
                "source_pipeline": "vector_search.search top_k=ntotal chunks (paraphrase-multilingual-MiniLM-L12-v2) + max-pool per doc",
            }
        )
    return rows


def vector_metadata_rows(
    query_id: str,
    query_text: str,
    model,
    index,
    records: list[dict],
    metadata_lookup: dict,
    term_index: list,
    title_by_doc: dict[str, str],
) -> list[dict]:
    """
    Vector + metadata_delta (hybrid_search.compute_hybrid_delta), không KG link, không kg_score.
    Entity: chỉ detect_entities(term_index) — không merge link_query_entities_kg.
    """
    detected = detect_entities(query_text, term_index)
    ck = hybrid_search.CANDIDATE_K
    candidates = search(query_text, model, index, records, top_k=ck)
    if _lobster_boost(query_text, detected):
        extra = search(
            LOBSTER_COASTAL_VECTOR_BOOST_QUERY, model, index, records, top_k=ck
        )
        seen = {c["chunk_id"] for c in candidates}
        for c in extra:
            cid = c.get("chunk_id")
            if cid and cid not in seen:
                seen.add(cid)
                candidates.append(c)

    best_by_doc: dict[str, dict] = {}
    delta_cache: dict[str, dict] = {}

    for item in candidates:
        doc_id = item["doc_id"]
        if doc_id not in delta_cache:
            row = metadata_lookup.get(doc_id, {})
            match_info = compute_match_features(row, detected)
            delta_cache[doc_id] = compute_hybrid_delta(detected, match_info)

        delta_info = delta_cache[doc_id]
        vector_score = float(item["score"])
        metadata_delta = float(delta_info["kg_delta"])
        final_score = vector_score + metadata_delta
        prev = best_by_doc.get(doc_id)
        if prev is not None and final_score <= float(prev["final_score"]):
            continue
        new_item = item.copy()
        new_item["vector_score"] = vector_score
        new_item["metadata_delta"] = metadata_delta
        new_item["final_score"] = final_score
        new_item["explanation"] = delta_info.get("explanation", "")
        row = metadata_lookup.get(doc_id, {})
        meta_aqua, meta_cap = _meta_pm_flags(row)
        new_item["_doc_is_aquaculture"] = bool(meta_aqua)
        new_item["_doc_is_capture_or_market"] = bool(meta_cap)
        best_by_doc[doc_id] = new_item

    reranked = sorted(best_by_doc.values(), key=lambda x: x["final_score"], reverse=True)

    narrow = _narrow_local(query_text, detected)
    if narrow and reranked:
        any_aqua = any(bool(x.get("_doc_is_aquaculture")) for x in reranked)
        if any_aqua:
            for x in reranked:
                if x.get("_doc_is_capture_or_market"):
                    pen = 0.12
                    x["final_score"] = float(x.get("final_score", 0.0)) - pen
                    expl = x.get("explanation", "") or ""
                    x["explanation"] = (
                        f"{expl}; intent penalty local aquaculture vs capture/market (-{pen:.2f})"
                        if expl
                        else f"intent penalty (-{pen:.2f})"
                    )
            reranked.sort(key=lambda x: x["final_score"], reverse=True)

    reranked = reranked[:TOP_DOCS]
    raws = [float(x["final_score"]) for x in reranked]
    norms = _normalize_minmax(raws)
    rows = []
    for rank, (item, norm) in enumerate(zip(reranked, norms), start=1):
        rows.append(
            {
                "query_id": query_id,
                "query_text": query_text,
                "baseline_name": "vector_metadata",
                "rank": rank,
                "doc_id": item["doc_id"],
                "title": title_by_doc.get(item["doc_id"], ""),
                "score_raw": float(item["final_score"]),
                "score_normalized": norm,
                "retrieval_level": "chunk_to_doc",
                "explanation_short": "embedding similarity + metadata_delta rerank (no KG link)",
                "source_pipeline": "run_core_baselines.vector_metadata_rows; hybrid_search.compute_hybrid_delta; detect_entities only",
            }
        )
    return rows


def ontology_sparql_rows(
    query_id: str,
    query_text: str,
    graph,
    kg_index: dict,
    metadata_lookup: dict,
    title_by_doc: dict[str, str],
    hybrid_map_fn,
) -> list[dict]:
    """
    SPARQL lọc doc có fact trùng entity URI; score_raw = kg_score (kg_runtime.score_doc_with_kg).
    """
    ns = kg_index["ns"]
    linked = kg_runtime.link_query_entities_kg(query_text, kg_index)
    target_uris: list[str] = []
    for bucket in ("disease", "species", "location", "mode", "pathogen", "prevention"):
        for e in linked.get(bucket) or []:
            u = e.get("uri")
            if u:
                target_uris.append(str(u))
    target_uris = list(dict.fromkeys(target_uris))

    sparql_hits: dict[str, int] = defaultdict(int)
    if target_uris and graph is not None:
        vals = " ".join(f"<{u}>" for u in target_uris)
        pred_list = ", ".join(
            [
                f"<{ns.aboutDisease}>",
                f"<{ns.aboutTaxon}>",
                f"<{ns.aboutLocation}>",
                f"<{ns.documentProductionMode}>",
            ]
        )
        q = f"""
        SELECT ?doc (COUNT(DISTINCT ?p) AS ?hc)
        WHERE {{
          VALUES ?t {{ {vals} }}
          ?doc ?p ?t .
          FILTER (?p IN ({pred_list}))
        }}
        GROUP BY ?doc
        """
        try:
            for row in graph.query(q):
                doc_uri = str(row[0])
                cnt = int(row[1]) if row[1] is not None else 0
                sparql_hits[doc_uri] = cnt
        except Exception:
            sparql_hits = defaultdict(int)

    scored: list[tuple[str, float, str]] = []
    for doc_id, row in metadata_lookup.items():
        uri = hybrid_map_fn(doc_id, row)
        if not uri:
            raw = 0.0
            expl = "no KG URI mapping for doc"
        else:
            facts = kg_runtime.get_document_facts(graph, uri)
            s = kg_runtime.score_doc_with_kg(
                query_entities=linked,
                doc_facts=facts,
                kg_index=kg_index,
                graph=graph,
                query_text=query_text,
            )
            raw = float(s.get("kg_score", 0.0) or 0.0)
            hc = sparql_hits.get(str(uri), 0)
            expl = f"SPARQL structured hits={hc}; kg_score; {s.get('kg_bonus_breakdown', '')[:120]}"
        # nhẹ nhàng ưu tiên doc có SPARQL hit khi kg_score tie
        boost = 0.001 * sparql_hits.get(str(uri or ""), 0)
        scored.append((doc_id, raw + boost, expl))

    scored.sort(key=lambda x: x[1], reverse=True)
    scored = scored[:TOP_DOCS]
    raws = [x[1] for x in scored]
    norms = _normalize_minmax(raws)
    rows = []
    for rank, ((doc_id, raw, expl), norm) in enumerate(zip(scored, norms), start=1):
        rows.append(
            {
                "query_id": query_id,
                "query_text": query_text,
                "baseline_name": "ontology_sparql",
                "rank": rank,
                "doc_id": doc_id,
                "title": title_by_doc.get(doc_id, ""),
                "score_raw": raw,
                "score_normalized": norm,
                "retrieval_level": "kg_structured",
                "explanation_short": "ontology / SPARQL entity match + kg_runtime.score_doc_with_kg",
                "source_pipeline": "run_core_baselines.ontology_sparql_rows; kg_runtime.link_query_entities_kg; rdflib SPARQL",
            }
        )
    return rows


def hybrid_rows(
    query_id: str,
    query_text: str,
    model,
    index,
    records: list[dict],
    metadata_lookup: dict,
    term_index: list,
    title_by_doc: dict[str, str],
) -> list[dict]:
    detected, results = hybrid_search.hybrid_search(
        query=query_text,
        model=model,
        index=index,
        records=records,
        metadata_lookup=metadata_lookup,
        term_index=term_index,
    )
    _ = detected
    raws = [float(r["final_score"]) for r in results]
    norms = _normalize_minmax(raws)
    rows = []
    for rank, (r, norm) in enumerate(zip(results, norms), start=1):
        rows.append(
            {
                "query_id": query_id,
                "query_text": query_text,
                "baseline_name": "hybrid",
                "rank": rank,
                "doc_id": r["doc_id"],
                "title": title_by_doc.get(r["doc_id"], ""),
                "score_raw": float(r["final_score"]),
                "score_normalized": norm,
                "retrieval_level": "chunk_to_doc",
                "explanation_short": "embedding + metadata_delta + KG rerank (pipeline hybrid_search.hybrid_search)",
                "source_pipeline": "hybrid_search.hybrid_search (unchanged)",
            }
        )
    return rows


def write_csv(path: Path, all_rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        w.writeheader()
        w.writerows(all_rows)


def refresh_lexical_vector_only() -> None:
    """Chỉ ghi lại lexical + vector CSV (siết top-10 doc/query); không đụng baseline khác."""
    import sys

    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    df_q = pd.read_csv(CORE_QUERIES, encoding="utf-8-sig")
    queries = [(str(r["query_id"]), str(r["query_text"])) for _, r in df_q.iterrows()]

    df_meta = load_full_metadata(str(METADATA_PATH))
    title_by_doc = {str(r["doc_id"]): str(r.get("title", "")) for _, r in df_meta.iterrows()}

    records = _load_chunk_records()
    tok_corpus = [_tokenize(r["text"]) for r in records]
    bm25 = OkapiBM25(tok_corpus)

    print("[STEP] Loading vector model + FAISS (lexical+vector refresh only)...")
    model, index, vec_records = load_index()

    lexical_all: list[dict] = []
    vector_all: list[dict] = []
    for qid, qtext in queries:
        print(f"[RUN] {qid}...")
        lexical_all.extend(lexical_bm25_rows(qid, qtext, records, bm25, title_by_doc))
        vector_all.extend(vector_rows(qid, qtext, model, index, vec_records, title_by_doc))

    write_csv(BASELINE_FILES["lexical"], lexical_all)
    write_csv(BASELINE_FILES["vector"], vector_all)
    print(f"[DONE] Wrote {BASELINE_FILES['lexical'].name} + {BASELINE_FILES['vector'].name}")


def main() -> None:
    import sys

    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    df_q = pd.read_csv(CORE_QUERIES, encoding="utf-8-sig")
    queries = [(str(r["query_id"]), str(r["query_text"])) for _, r in df_q.iterrows()]

    df_meta = load_full_metadata(str(METADATA_PATH))
    metadata_lookup = build_metadata_lookup(df_meta)
    term_index = build_term_index(df_meta)
    title_by_doc = {str(r["doc_id"]): str(r.get("title", "")) for _, r in df_meta.iterrows()}

    records = _load_chunk_records()
    tok_corpus = [_tokenize(r["text"]) for r in records]
    bm25 = OkapiBM25(tok_corpus)

    print("[STEP] Loading vector model + FAISS...")
    model, index, vec_records = load_index()
    if len(vec_records) != len(records):
        print("[WARN] chunks_meta.pkl length differs from loaded index; BM25 uses pkl, vector uses index.")

    hybrid_search._init_kg_if_needed()
    graph = hybrid_search._KG_GRAPH
    kg_index = hybrid_search._KG_INDEX
    map_fn = hybrid_search._map_doc_to_kg_uri

    # Cho hybrid / vector_metadata: pool chunk rộng hơn mặc định để gộp doc đủ TOP_DOCS (không đổi công thức điểm)
    _orig_final = hybrid_search.FINAL_K
    _orig_cand = hybrid_search.CANDIDATE_K
    hybrid_search.FINAL_K = TOP_DOCS
    hybrid_search.CANDIDATE_K = HYBRID_CANDIDATE_CHUNKS
    try:
        lexical_all: list[dict] = []
        vector_all: list[dict] = []
        vm_all: list[dict] = []
        onto_all: list[dict] = []
        hybrid_all: list[dict] = []

        for qid, qtext in queries:
            print(f"[RUN] {qid}: {qtext[:60]}...")
            lexical_all.extend(lexical_bm25_rows(qid, qtext, records, bm25, title_by_doc))
            vector_all.extend(vector_rows(qid, qtext, model, index, vec_records, title_by_doc))
            vm_all.extend(
                vector_metadata_rows(
                    qid, qtext, model, index, vec_records, metadata_lookup, term_index, title_by_doc
                )
            )
            if graph is not None and kg_index is not None:
                onto_all.extend(
                    ontology_sparql_rows(
                        qid,
                        qtext,
                        graph,
                        kg_index,
                        metadata_lookup,
                        title_by_doc,
                        map_fn,
                    )
                )
            else:
                # fallback: toàn doc score 0
                for rank, doc_id in enumerate(list(metadata_lookup.keys())[:TOP_DOCS], start=1):
                    onto_all.append(
                        {
                            "query_id": qid,
                            "query_text": qtext,
                            "baseline_name": "ontology_sparql",
                            "rank": rank,
                            "doc_id": doc_id,
                            "title": title_by_doc.get(doc_id, ""),
                            "score_raw": 0.0,
                            "score_normalized": 1.0 if rank == 1 else 0.0,
                            "retrieval_level": "kg_structured",
                            "explanation_short": "KG disabled; sparse placeholder ranking",
                            "source_pipeline": "run_core_baselines (KG unavailable)",
                        }
                    )
            hybrid_all.extend(
                hybrid_rows(qid, qtext, model, index, vec_records, metadata_lookup, term_index, title_by_doc)
            )

        write_csv(BASELINE_FILES["lexical"], lexical_all)
        write_csv(BASELINE_FILES["vector"], vector_all)
        write_csv(BASELINE_FILES["vector_metadata"], vm_all)
        write_csv(BASELINE_FILES["ontology_sparql"], onto_all)
        write_csv(BASELINE_FILES["hybrid"], hybrid_all)
    finally:
        hybrid_search.FINAL_K = _orig_final
        hybrid_search.CANDIDATE_K = _orig_cand

    _write_results_notes_template()


def _write_results_notes_template() -> None:
    """Ghi template notes (chạy full main). Có thể chỉnh tay phần Lexical/Vector sau khi --refresh-lexical-vector."""
    notes = RESULTS_DIR / "results_generation_notes.md"
    notes.write_text(
        """# Baseline results generation (bước 3)

## Đã chạy
- Script: `run_core_baselines.py` (project root).
- Query: `data/eval/final_query_set_core.csv` (28 query).
- Metadata titles: `data/metadata/document_metadata_cleaned.xlsx`.
- Vector index: `vector_store/chunks.index` + config; chunks list BM25: `vector_store/chunks_meta.pkl` (phải cùng corpus build).

## Lexical
- **BM25 Okapi** trên token sau `hybrid_search.normalize_text`, corpus = toàn bộ chunk text.
- Mỗi query: tính BM25 cho **mọi** chunk, rồi **max-pool** theo `doc_id` (điểm doc = max điểm chunk thuộc doc), sắp xếp doc theo điểm sau pool, lấy top 10. **Không** cắt trước ở top-N chunk (tránh dồn hết top chunk vào vài tài liệu dài).
- `retrieval_level`: `chunk_to_doc`.

## Vector
- `vector_search.search` — embedding `paraphrase-multilingual-MiniLM-L12-v2`, FAISS `IndexFlatIP`, vector L2-normalized.
- Mỗi query: `top_k = ntotal` (số vector trong index, thường bằng số chunk), cùng công thức similarity; sau đó max-pool theo doc như lexical, top 10.
- Không metadata, không KG.

## Vector + metadata
- Cùng pool ứng viên vector với hybrid ở mức **CANDIDATE_K** chunk + optional lobster English boost query (copy logic `hybrid_search`).
- Điểm = `vector_score + metadata_delta` với `compute_match_features` + `compute_hybrid_delta` từ `hybrid_search`.
- **Không** gọi `link_query_entities_kg` / **không** merge KG entities — chỉ `detect_entities(term_index)` (regex + từ điển metadata).
- Intent penalty nuôi địa phương: copy logic `_narrow_local_aquaculture_intent` + phạt capture/market khi có doc aquaculture trong pool.

## Ontology / SPARQL
- Nạp đồ thị như hybrid (`hybrid_search._init_kg_if_needed`).
- `kg_runtime.link_query_entities_kg` → tập URI; SPARQL `COUNT DISTINCT ?p` với `?doc ?p ?target` và `?p` ∈ {aboutDisease, aboutTaxon, aboutLocation, documentProductionMode}.
- `score_raw` = `kg_score` ( `score_doc_with_kg` ) + boost nhỏ 0.001 × (SPARQL hit count) để phá hòa; `retrieval_level`: `kg_structured`.
- Query không bắt được entity: vẫn xếp toàn corpus theo `kg_score` (thường thấp / âm).

## Hybrid
- `hybrid_search.hybrid_search`. Runtime tạm set `FINAL_K=10` và `CANDIDATE_K=150` (mặc định repo `FINAL_K=5`, `CANDIDATE_K=10`) để pool chunk đủ đa dạng doc khi xuất top-10; khôi phục sau chạy.
- `final_score = vector_score + metadata_delta + kg_score + intent_adjustment`; `intent_adjustment` là lớp guardrail cực hẹp (vòng kỹ thuật cuối), xem `hybrid_search._intent_narrow_final_adjustment`.

## score_normalized
- Trên tập **top doc đã xuất của từng query**, min–max trên `score_raw` → [0,1] (doc tốt nhất ~1). Nếu mọi điểm bằng nhau → toàn 1.

## Giới hạn
- Hybrid / vector_metadata xét doc trong pool tới **2×CANDIDATE_K** chunk (run này `CANDIDATE_K=150` tạm thời); vẫn có thể <10 doc nếu corpus/index ít chunk/doc đa dạng.
- Lexical / vector: đã dùng **toàn bộ chunk** cho điểm trước max-pool → mỗi query có đủ **10 doc** miễn là chỉ mục có ≥10 `doc_id` khác nhau (corpus hiện tại đạt).
- Ontology: query tự nhiên không khớp alias KG → SPARQL rỗng, xếp hạng chủ yếu từ `kg_score` / mapping URI.

## Metric
- **Chưa** tính P@k, Recall, MRR, nDCG (bước 4).
""",
        encoding="utf-8",
    )
    print("[DONE] Wrote CSV baselines + results_generation_notes.md")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--refresh-lexical-vector":
        refresh_lexical_vector_only()
    else:
        main()
