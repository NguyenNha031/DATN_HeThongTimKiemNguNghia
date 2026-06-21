#!/usr/bin/env python3
"""Run Wilcoxon signed-rank tests comparing `hybrid` vs `vector_metadata` per-query.

Creates outputs:
 - outputs/wilcoxon_hybrid_vs_vector_metadata.csv
 - outputs/wilcoxon_hybrid_vs_vector_metadata.json
 - outputs/wilcoxon_hybrid_vs_vector_metadata.md

The script prefers per-query metric files in `data/eval/metrics/` but will
recompute per-query metrics from relevance judgments and results if necessary.
It does not modify any input files.
"""
import csv
import json
import math
import os
import sys
from collections import defaultdict

try:
    import statistics
except Exception:
    statistics = None

try:
    import scipy.stats as ss
    SCIPY_AVAILABLE = True
except Exception:
    ss = None
    SCIPY_AVAILABLE = False

import argparse
import itertools


def safe_median(xs):
    if not xs:
        return None
    try:
        return statistics.median(xs)
    except Exception:
        xs_sorted = sorted(xs)
        n = len(xs_sorted)
        mid = n // 2
        if n % 2:
            return xs_sorted[mid]
        return (xs_sorted[mid - 1] + xs_sorted[mid]) / 2.0


def _norm(name):
    if name is None:
        return ''
    # strip BOM, whitespace, lowercase
    return name.lstrip('\ufeff').strip().lower().replace(' ', '_').replace('-', '_')


def pick_col(names, candidates):
    # names: iterable of original header names
    norm_map = { _norm(n): n for n in names }
    for c in candidates:
        nc = _norm(c)
        if nc in norm_map:
            return norm_map[nc]
    # try partial substring match
    for c in candidates:
        nc = _norm(c)
        for k, orig in norm_map.items():
            if nc in k or k in nc:
                return orig
    return None


def read_csv_rows(path):
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)


def load_results(path):
    rows = read_csv_rows(path)
    if not rows:
        return {}
    names = rows[0].keys()
    qcol = pick_col(names, ["query_id", "qid", "query", "q"])
    dcol = pick_col(names, ["doc_id", "docno", "id", "document_id", "docid"])
    rcol = pick_col(names, ["rank", "position", "pos"])
    sco = pick_col(names, ["score"])
    if qcol is None or dcol is None:
        raise ValueError(f"Cannot detect query/doc columns in {path}; headers: {names}")
    perq = defaultdict(list)
    for r in rows:
        q = r[qcol]
        doc = r[dcol]
        rank = int(r[rcol]) if rcol and r[rcol] not in (None, "") else None
        score = float(r[sco]) if sco and r[sco] not in (None, "") else None
        perq[q].append({"doc": doc, "rank": rank, "score": score})
    # if rank missing, sort by score if available
    for q, docs in perq.items():
        if any(d["rank"] is None for d in docs):
            docs.sort(key=lambda x: (-(x["score"] if x["score"] is not None else 0)))
            for i, d in enumerate(docs, start=1):
                d["rank"] = i
    return perq


def load_qrels(path):
    rows = read_csv_rows(path)
    if not rows:
        return {}
    names = rows[0].keys()
    qcol = pick_col(names, ["query_id", "qid", "query", "q"])
    dcol = pick_col(names, ["doc_id", "docno", "id", "document_id", "docid"])
    relcol = pick_col(names, ["relevance", "rel", "label", "grade"])
    if qcol is None or dcol is None or relcol is None:
        raise ValueError(f"Cannot detect qrels columns in {path}; headers: {names}")
    qrels = defaultdict(dict)
    for r in rows:
        q = r[qcol]
        d = r[dcol]
        try:
            rel = float(r[relcol])
        except Exception:
            rel = 1.0 if r[relcol] not in (None, "", "0") else 0.0
        qrels[q][d] = rel
    return qrels


def precision_at_k(retrieved_docs, qrels_for_q, k):
    if k <= 0:
        return 0.0
    topk = [d["doc"] for d in sorted(retrieved_docs, key=lambda x: x["rank"])][:k]
    if not topk:
        return 0.0
    rels = [1 if qrels_for_q.get(d, 0) > 0 else 0 for d in topk]
    return sum(rels) / float(k)


def recall_at_k(retrieved_docs, qrels_for_q, k):
    relevant = [d for d, r in qrels_for_q.items() if r > 0]
    if not relevant:
        return 0.0
    topk = [d["doc"] for d in sorted(retrieved_docs, key=lambda x: x["rank"])][:k]
    rels = [1 for d in topk if qrels_for_q.get(d, 0) > 0]
    return sum(rels) / float(len(relevant))


def reciprocal_rank(retrieved_docs, qrels_for_q):
    for d in sorted(retrieved_docs, key=lambda x: x["rank"]):
        if qrels_for_q.get(d["doc"], 0) > 0:
            return 1.0 / float(d["rank"]) if d["rank"] and d["rank"] > 0 else 0.0
    return 0.0


def ndcg_at_k(retrieved_docs, qrels_for_q, k):
    def dcg(rels):
        s = 0.0
        for i, r in enumerate(rels, start=1):
            s += (2 ** r - 1) / math.log2(i + 1)
        return s

    topk = [d["doc"] for d in sorted(retrieved_docs, key=lambda x: x["rank"])][:k]
    rels = [qrels_for_q.get(d, 0.0) for d in topk]
    idcg_rels = sorted([v for v in qrels_for_q.values() if v is not None], reverse=True)[:k]
    if not idcg_rels:
        return 0.0
    return dcg(rels) / dcg(idcg_rels)


def compute_metrics_for_run(perq_results, qrels, query_list):
    metrics = {}
    for q in query_list:
        res = perq_results.get(q, [])
        qrel = qrels.get(q, {})
        metrics[q] = {
            "P@1": precision_at_k(res, qrel, 1),
            "P@5": precision_at_k(res, qrel, 5),
            "Recall@5": recall_at_k(res, qrel, 5),
            "MRR": reciprocal_rank(res, qrel),
            "nDCG@5": ndcg_at_k(res, qrel, 5),
            "nDCG@10": ndcg_at_k(res, qrel, 10),
        }
    return metrics


def load_or_compute_per_query_metrics(metrics_dir, qrels_path, results_paths, query_list):
    # prefer metrics_dir if it contains per-query metric CSVs
    if metrics_dir and os.path.isdir(metrics_dir):
        # look for files named with baseline keys
        files = os.listdir(metrics_dir)
        mapping = {}
        for f in files:
            lf = f.lower()
            if "vector" in lf and f.endswith('.csv'):
                mapping['vector_metadata'] = os.path.join(metrics_dir, f)
            if "hybrid" in lf and f.endswith('.csv'):
                mapping['hybrid'] = os.path.join(metrics_dir, f)
        if 'vector_metadata' in mapping and 'hybrid' in mapping:
            # read per-query metrics from csvs into dicts
            per = {}
            for key, path in mapping.items():
                rows = read_csv_rows(path)
                per[key] = {r[next(iter(r.keys()))]: {k: float(v) if v != '' else 0.0 for k, v in r.items() if k != next(iter(r.keys()))} for r in rows}
            return per

    # else compute from results and qrels
    qrels = load_qrels(qrels_path)
    perq_vector = load_results(results_paths['vector_metadata'])
    perq_hybrid = load_results(results_paths['hybrid'])
    metrics_vector = compute_metrics_for_run(perq_vector, qrels, query_list)
    metrics_hybrid = compute_metrics_for_run(perq_hybrid, qrels, query_list)
    return {'vector_metadata': metrics_vector, 'hybrid': metrics_hybrid}


def run_tests(metrics_per_query, query_list, output_prefix):
    metrics_to_check = ["P@1", "MRR", "nDCG@10"]
    extra_metrics = ["P@5", "Recall@5", "nDCG@5"]
    # include extra metrics only if present
    for m in extra_metrics:
        # check first query availability
        if all(m in metrics_per_query['hybrid'].get(q, {}) for q in query_list):
            metrics_to_check.append(m)

    rows = []
    summary = {}
    for metric in metrics_to_check:
        hybrid_scores = [metrics_per_query['hybrid'].get(q, {}).get(metric, 0.0) for q in query_list]
        vector_scores = [metrics_per_query['vector_metadata'].get(q, {}).get(metric, 0.0) for q in query_list]
        diffs = [h - v for h, v in zip(hybrid_scores, vector_scores)]
        n_queries = len(query_list)
        mean_h = float(sum(hybrid_scores) / n_queries) if n_queries else 0.0
        mean_v = float(sum(vector_scores) / n_queries) if n_queries else 0.0
        mean_diff = float(sum(diffs) / n_queries) if n_queries else 0.0
        median_diff = safe_median(diffs)
        num_h_better = sum(1 for d in diffs if d > 0)
        num_eq = sum(1 for d in diffs if abs(d) < 1e-12)
        num_v_better = sum(1 for d in diffs if d < 0)

        wil_stat = None
        p_value = None
        significant = False
        effect = None
        note = ""
        if all(abs(d) < 1e-12 for d in diffs):
            note = "All per-query differences are zero; Wilcoxon not applicable."
        else:
            if SCIPY_AVAILABLE and ss is not None:
                try:
                    stat, p = ss.wilcoxon(hybrid_scores, vector_scores)
                    wil_stat = float(stat)
                    p_value = float(p)
                    significant = p_value < 0.05
                    if mean_diff > 0:
                        effect = 'hybrid>vector_metadata'
                    elif mean_diff < 0:
                        effect = 'hybrid<vector_metadata'
                    else:
                        effect = 'no_mean_diff'
                except Exception as e:
                    note = f"Scipy wilcoxon failed: {e}"
            else:
                note = "scipy not available; cannot run Wilcoxon test."

        row = {
            "metric": metric,
            "baseline_a": "vector_metadata",
            "baseline_b": "hybrid",
            "n_queries": n_queries,
            "mean_hybrid": mean_h,
            "mean_vector_metadata": mean_v,
            "mean_diff": mean_diff,
            "median_diff": median_diff,
            "num_hybrid_better": num_h_better,
            "num_equal": num_eq,
            "num_vector_metadata_better": num_v_better,
            "wilcoxon_statistic": wil_stat,
            "p_value": p_value,
            "significant_at_0_05": significant,
            "effect_direction": effect,
            "note": note,
        }
        rows.append(row)
        summary[metric] = row

    # write outputs
    os.makedirs(os.path.dirname(output_prefix), exist_ok=True)
    csv_path = output_prefix + '.csv'
    json_path = output_prefix + '.json'
    md_path = output_prefix + '.md'

    # CSV
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        fieldnames = list(rows[0].keys()) if rows else []
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow({k: ('' if v is None else v) for k, v in r.items()})

    # JSON
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({'results': rows, 'scipy_available': SCIPY_AVAILABLE}, f, indent=2)

    # MD
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write('# Wilcoxon signed-rank test: hybrid vs vector_metadata\n\n')
        f.write('**Objective:** Compare per-query stability improvements of `hybrid` vs `vector_metadata` on core queries.\\n\n')
        f.write('**Inputs used:**\n')
        f.write('- data/eval/final_query_set_core.csv\n')
        f.write('- data/eval/relevance_judgments_core.csv\n')
        f.write('- data/eval/results/baseline_vector_metadata_core.csv\n')
        f.write('- data/eval/results/baseline_hybrid_core.csv\n\n')
        f.write('**Metrics tested:** ' + ', '.join([r['metric'] for r in rows]) + '\n\n')
        f.write('**Results:**\n\n')
        # simple markdown table
        hdrs = ['metric','n_queries','mean_hybrid','mean_vector_metadata','mean_diff','median_diff','num_hybrid_better','num_equal','num_vector_metadata_better','wilcoxon_statistic','p_value','significant_at_0_05','effect_direction','note']
        f.write('|' + '|'.join(hdrs) + '|\n')
        f.write('|' + '|'.join(['---']*len(hdrs)) + '|\n')
        for r in rows:
            f.write('|' + '|'.join(str(r.get(h, '')) for h in hdrs) + '|\n')
        f.write('\n')
        f.write('**Interpretation (cautious):**\n')
        for r in rows:
            line = f"- {r['metric']}: hybrid better on {r['num_hybrid_better']} queries; vector_metadata better on {r['num_vector_metadata_better']} queries; p={r['p_value']}"
            if r['note']:
                line += f"; note: {r['note']}"
            f.write(line + '\n')
        f.write('\n')
        f.write('**Limitations:** 28 core queries; results only apply to this set; statistical test requires paired per-query scores; absence of scipy prevents running Wilcoxon.\n')

    return {'csv': csv_path, 'json': json_path, 'md': md_path}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--queries', default='data/eval/final_query_set_core.csv')
    parser.add_argument('--qrels', default='data/eval/relevance_judgments_core.csv')
    parser.add_argument('--results_vector', default='data/eval/results/baseline_vector_metadata_core.csv')
    parser.add_argument('--results_hybrid', default='data/eval/results/baseline_hybrid_core.csv')
    parser.add_argument('--metrics_dir', default='data/eval/metrics')
    parser.add_argument('--output_prefix', default='outputs/wilcoxon_hybrid_vs_vector_metadata')
    args = parser.parse_args()

    # read query list; assume first column contains query id per row
    if not os.path.exists(args.queries):
        print('Query list not found:', args.queries, file=sys.stderr)
        sys.exit(2)
    qrows = read_csv_rows(args.queries)
    if not qrows:
        print('No queries found in', args.queries, file=sys.stderr)
        sys.exit(2)
    qid_col = next(iter(qrows[0].keys()))
    query_list = [r[qid_col] for r in qrows]

    results_paths = {'vector_metadata': args.results_vector, 'hybrid': args.results_hybrid}
    for p in results_paths.values():
        if not os.path.exists(p):
            print('Result file not found:', p, file=sys.stderr)
            sys.exit(2)
    if not os.path.exists(args.qrels):
        print('Qrels file not found:', args.qrels, file=sys.stderr)
        sys.exit(2)

    metrics_per_query = load_or_compute_per_query_metrics(args.metrics_dir, args.qrels, results_paths, query_list)

    out = run_tests(metrics_per_query, query_list, args.output_prefix)
    print('Wrote outputs:', out)


if __name__ == '__main__':
    main()
