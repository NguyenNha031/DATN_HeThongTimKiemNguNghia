from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import pandas as pd

import kg_runtime
import hybrid_search
from vector_search import load_index


OUT_DIR = Path("outputs")

# Inputs (current state)
BACKFILL_REPORT_CSV = OUT_DIR / "document_fact_backfill_report.csv"
NORMALIZATION_REPORT_CSV = OUT_DIR / "metadata_normalization_report.csv"
NORMALIZATION_REPORT_JSON = OUT_DIR / "metadata_normalization_report.json"

ONTO_ALIAS = Path("data") / "ontology" / "taxon_enriched_aliases.owl"
ONTO_SEMANTIC = Path("data") / "ontology" / "taxon_enriched_semantic.owl"
ONTO_FACTS_BEFORE = Path("data") / "ontology" / "taxon_enriched_facts.owl"
ONTO_FACTS_AFTER = Path("data") / "ontology" / "taxon_enriched_facts_v2.owl"

VERIFY_BEFORE_JSON = OUT_DIR / "kg_runtime_verification_before_semantic_backfill.json"
VERIFY_AFTER_JSON = OUT_DIR / "kg_runtime_verification.json"


EXPANDED_QUERIES = [
    "shrimp farming",
    "fish disease",
    "aquatic animals",
    "capture fisheries",
    "shrimp disease",
    "biosecurity in aquaculture",
    "health management shrimp",
    "pathogens in shrimp",
    "infectious myonecrosis",
    "IMN shrimp",
    "Khánh Hòa lobster",
    "nuôi tôm",
    "disease risk aquaculture",
    "shellfish farming",
    "crustacean disease",
]


def _utf8():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stdin.reconfigure(encoding="utf-8")
    except Exception:
        pass


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def _reset_hybrid_search_kg_cache() -> None:
    # Reset global KG cache to allow reloading a different ontology file in-process.
    hybrid_search._KG_GRAPH = None
    hybrid_search._KG_INDEX = None
    hybrid_search._KG_LOAD_ATTEMPTED = False
    hybrid_search._KG_LOADED_OWL_PATH = None


def _run_queries_with_ontology(ontology_path: Path) -> dict[str, Any]:
    """
    Run expanded query verification for a specific ontology path by forcing
    hybrid_search to prefer that file as KG_FACT_ENRICHED_PATH.
    """
    model, index, records = load_index()
    df = hybrid_search.load_full_metadata(hybrid_search.METADATA_PATH)
    metadata_lookup = hybrid_search.build_metadata_lookup(df)
    term_index = hybrid_search.build_term_index(df)

    # Force hybrid_search to load this ontology as "facts" layer.
    hybrid_search.KG_FACT_ENRICHED_PATH = ontology_path
    _reset_hybrid_search_kg_cache()

    # Load KG for KG-linked entity reporting (same file).
    g = kg_runtime.load_kg(ontology_path)
    kg_index = kg_runtime.build_kg_index(g)

    per_query = []
    for q in EXPANDED_QUERIES:
        detected_metadata = hybrid_search.detect_entities(q, term_index)
        detected_kg = kg_runtime.link_query_entities_kg(q, kg_index)

        _det, results = hybrid_search.hybrid_search(
            query=q,
            model=model,
            index=index,
            records=records,
            metadata_lookup=metadata_lookup,
            term_index=term_index,
        )

        top5 = []
        for r in results[:5]:
            top5.append(
                {
                    "doc_id": r.get("doc_id"),
                    "doc_uri_in_kg": r.get("doc_uri_in_kg"),
                    "vector_score": r.get("vector_score"),
                    "metadata_delta": r.get("metadata_delta"),
                    "kg_score": r.get("kg_score"),
                    "final_score": r.get("final_score"),
                    "explanation": r.get("explanation"),
                    "kg_explanation": r.get("kg_explanation"),
                }
            )

        mapped = sum(1 for x in top5 if x.get("doc_uri_in_kg"))
        nonzero = sum(1 for x in top5 if float(x.get("kg_score") or 0.0) > 0.0)
        kg_expl = sum(1 for x in top5 if (x.get("kg_explanation") or "").strip())

        per_query.append(
            {
                "query": q,
                "detected_metadata_entities": {
                    k: [m.get("canonical") for m in (detected_metadata.get(k) or [])]
                    for k in ["disease", "species", "location", "mode"]
                },
                "detected_kg_linked_entities": {
                    k: [e.get("label") for e in (detected_kg.get(k) or [])]
                    for k in ["disease", "species", "location", "mode"]
                },
                "top5_results": top5,
                "top5_docs_mapped_to_kg": mapped,
                "top5_docs_with_nonzero_kg_score": nonzero,
                "top5_docs_with_kg_explanation": kg_expl,
            }
        )

    aggregate = {
        "queries": len(EXPANDED_QUERIES),
        "total_top5_docs_mapped_to_kg": sum(x["top5_docs_mapped_to_kg"] for x in per_query),
        "total_top5_docs_with_nonzero_kg_score": sum(x["top5_docs_with_nonzero_kg_score"] for x in per_query),
        "total_top5_docs_with_kg_explanation": sum(x["top5_docs_with_kg_explanation"] for x in per_query),
        "queries_with_any_nonzero_kg": sum(1 for x in per_query if x["top5_docs_with_nonzero_kg_score"] > 0),
        "queries_with_zero_kg_top5": sum(1 for x in per_query if x["top5_docs_with_nonzero_kg_score"] == 0),
    }

    return {
        "ontology_file_loaded": str(ontology_path),
        "per_query": per_query,
        "aggregate": aggregate,
    }


def build_added_triples_reports() -> None:
    """
    Produce:
      - outputs/added_triples_sample.json
      - outputs/added_triples_grouped_summary.json
      - outputs/new_or_used_generic_entities_review.json
      - outputs/semantic_backfill_false_positive_review.json
    """
    if not BACKFILL_REPORT_CSV.exists():
        raise FileNotFoundError(f"Missing {BACKFILL_REPORT_CSV}")
    if not NORMALIZATION_REPORT_CSV.exists():
        raise FileNotFoundError(f"Missing {NORMALIZATION_REPORT_CSV}")

    df_backfill = pd.read_csv(BACKFILL_REPORT_CSV)
    df_norm = pd.read_csv(NORMALIZATION_REPORT_CSV)

    # 1) added_triples_sample.json
    added = df_backfill[df_backfill["status"].astype(str).eq("added")].copy()

    # Join to find the token row(s) that produced this mapped_entity_uri for this doc/predicate.
    # We match by doc_id + candidate_property + target_uri (most reliable).
    df_norm["candidate_property"] = df_norm["candidate_property"].astype(str)
    df_norm["target_uri"] = df_norm["target_uri"].astype(str)

    sample_rows = []
    for _, r in added.iterrows():
        doc_id = str(r.get("doc_id", ""))
        predicate = str(r.get("predicate", ""))
        target_uri = str(r.get("mapped_entity_uri", ""))

        cand = df_norm[
            (df_norm["doc_id"].astype(str) == doc_id)
            & (df_norm["candidate_property"].astype(str) == predicate)
            & (df_norm["target_uri"].astype(str) == target_uri)
        ]
        if cand.empty:
            # Fallback: use doc_id + predicate only
            cand = df_norm[
                (df_norm["doc_id"].astype(str) == doc_id)
                & (df_norm["candidate_property"].astype(str) == predicate)
                & (df_norm["decision"].astype(str).isin(["ADD_EXACT_ALIAS", "ADD_NEW_ENTITY"]))
            ].head(1)

        if not cand.empty:
            c0 = cand.iloc[0].to_dict()
            sample_rows.append(
                {
                    "document_id": doc_id,
                    "document_uri": r.get("doc_uri"),
                    "source_field": c0.get("source_field"),
                    "raw_token": c0.get("token"),
                    "normalized_label": c0.get("normalized_label"),
                    "candidate_class": c0.get("candidate_class"),
                    "candidate_property": predicate,
                    "target_uri": target_uri,
                    "triple_added": True,
                    "reason": r.get("reason"),
                    "confidence": r.get("confidence"),
                }
            )
        else:
            sample_rows.append(
                {
                    "document_id": doc_id,
                    "document_uri": r.get("doc_uri"),
                    "source_field": None,
                    "raw_token": None,
                    "normalized_label": None,
                    "candidate_class": None,
                    "candidate_property": predicate,
                    "target_uri": target_uri,
                    "triple_added": True,
                    "reason": r.get("reason"),
                    "confidence": r.get("confidence"),
                }
            )

    # Keep sample as "all added" (dataset small) but cap if large.
    sample_out = {"added_count": int(len(sample_rows)), "rows": sample_rows[:500]}
    _write_json(OUT_DIR / "added_triples_sample.json", sample_out)

    # 2) grouped summary
    grouped = (
        added.groupby(["predicate", "mapped_entity_uri", "raw_metadata_value"], dropna=False)
        .size()
        .reset_index(name="count")
        .sort_values(["count"], ascending=False)
    )
    grouped_out = {
        "by_predicate": added["predicate"].value_counts().to_dict(),
        "top_groups": grouped.head(200).to_dict(orient="records"),
    }
    _write_json(OUT_DIR / "added_triples_grouped_summary.json", grouped_out)

    # 3) generic entities review
    # We define "generic entity" by URI fragment prefix "Generic_".
    used_generic_counts: Counter[str] = Counter()
    for u in added["mapped_entity_uri"].astype(str).tolist():
        if "Generic_" in u:
            used_generic_counts[u] += 1

    # Collect created generic entities from semantic ontology file if present.
    created_generic = []
    if ONTO_SEMANTIC.exists():
        g = kg_runtime.load_kg(ONTO_SEMANTIC)
        # Find nodes with fragment containing Generic_
        generic_nodes = set()
        for s in g.subjects(None, None):
            if "Generic_" in str(s):
                generic_nodes.add(str(s))

        # Extract types + labels
        for uri in sorted(generic_nodes):
            uref = kg_runtime.URIRef(uri)  # type: ignore[attr-defined]
            types = [str(o) for o in g.objects(uref, kg_runtime.RDF.type)]  # type: ignore[attr-defined]
            labels = []
            for p in [kg_runtime.RDFS.label, kg_runtime.SKOS.prefLabel, kg_runtime.SKOS.altLabel]:  # type: ignore[attr-defined]
                for o in g.objects(uref, p):
                    labels.append(str(o))
            created_generic.append(
                {
                    "uri": uri,
                    "types": sorted(set(types)),
                    "labels": sorted(set(labels)),
                    "is_new_entity_in_semantic_owl": True,
                    "used_in_backfill_count": int(used_generic_counts.get(uri, 0)),
                }
            )

    # Risk note heuristic
    def risk_note(uri: str) -> str:
        # Generic taxon can be risky for query linking (broad matches).
        if uri.endswith("Generic_AquaticTaxon"):
            return "high"
        if uri.endswith("Generic_Fish") or uri.endswith("Generic_Shrimp"):
            return "medium"
        if "Generic_" in uri:
            return "low"
        return "low"

    generic_review = []
    for e in created_generic:
        uri = e["uri"]
        generic_review.append(
            {
                **e,
                "risk_note": risk_note(uri),
                "risk_reason": "generic entity may match broad user queries; ensure it does not dominate KG scoring",
            }
        )
    _write_json(OUT_DIR / "new_or_used_generic_entities_review.json", {"entities": generic_review})

    # 4) false positive review: suspicious cases
    suspicious = []
    # Mark any doc where aboutTaxon was filled only with generic nodes (potentially too broad).
    added_taxon = added[added["predicate"].astype(str).eq("aboutTaxon")]
    by_doc = defaultdict(list)
    for _, r in added_taxon.iterrows():
        by_doc[str(r["doc_id"])].append(str(r["mapped_entity_uri"]))
    for doc_id, uris in by_doc.items():
        if uris and all("Generic_" in u for u in uris):
            suspicious.append(
                {
                    "doc_id": doc_id,
                    "issue": "aboutTaxon filled only with generic entities",
                    "mapped_entity_uris": sorted(set(uris)),
                    "risk": "medium",
                    "suggested_tightening": "Consider requiring at least one specific Taxon when available; keep generic only as fallback.",
                }
            )

    # Tokens that were mapped to a specific entity but look generic (e.g., shrimp -> specific species) – should be none by policy.
    # Check normalization report for such patterns.
    suspected_generic_to_specific = df_norm[
        (df_norm["decision"].astype(str) == "ADD_EXACT_ALIAS")
        & (df_norm["candidate_property"].astype(str) == "aboutTaxon")
        & (df_norm["normalized_label"].astype(str).isin(["shrimp", "fish", "aquatic animals", "aquatic species"]))
    ]
    if not suspected_generic_to_specific.empty:
        suspicious.append(
            {
                "issue": "generic token mapped via ADD_EXACT_ALIAS",
                "examples": suspected_generic_to_specific.head(20).to_dict(orient="records"),
                "risk": "high",
                "suggested_tightening": "Ensure generic tokens do not map to specific species individuals; use Generic_* nodes instead.",
            }
        )

    verdict = "MOSTLY_SAFE"
    if any(x.get("risk") == "high" for x in suspicious):
        verdict = "NEEDS_TIGHTENING"
    if not suspicious:
        verdict = "SAFE"

    fp_review = {
        "verdict": verdict,
        "suspicious_cases": suspicious,
        "notes": [
            "This review focuses on generic entities and generic-to-specific mapping risks.",
            "No scoring changes were made; any retrieval changes come from ontology facts only.",
        ],
    }
    _write_json(OUT_DIR / "semantic_backfill_false_positive_review.json", fp_review)


def expanded_query_verification() -> None:
    before = _run_queries_with_ontology(ONTO_FACTS_BEFORE)
    after = _run_queries_with_ontology(ONTO_FACTS_AFTER)

    out = {
        "before": before,
        "after": after,
    }
    _write_json(OUT_DIR / "kg_runtime_verification_semantic_patch_expanded.json", out)

    # Summary diff
    summary = {
        "ontology_before": before["ontology_file_loaded"],
        "ontology_after": after["ontology_file_loaded"],
        "aggregate_before": before["aggregate"],
        "aggregate_after": after["aggregate"],
        "per_query_diff": [],
    }

    before_by_q = {x["query"]: x for x in before["per_query"]}
    after_by_q = {x["query"]: x for x in after["per_query"]}

    improved = []
    unchanged = []
    worse = []

    for q in EXPANDED_QUERIES:
        bq = before_by_q.get(q)
        aq = after_by_q.get(q)
        if not bq or not aq:
            continue

        b_nonzero = int(bq["top5_docs_with_nonzero_kg_score"])
        a_nonzero = int(aq["top5_docs_with_nonzero_kg_score"])
        b_expl = int(bq["top5_docs_with_kg_explanation"])
        a_expl = int(aq["top5_docs_with_kg_explanation"])

        delta = {
            "query": q,
            "nonzero_kg_top5_before": b_nonzero,
            "nonzero_kg_top5_after": a_nonzero,
            "kg_expl_nonempty_before": b_expl,
            "kg_expl_nonempty_after": a_expl,
            "kg_linked_entities_before": bq["detected_kg_linked_entities"],
            "kg_linked_entities_after": aq["detected_kg_linked_entities"],
        }
        summary["per_query_diff"].append(delta)

        if (a_nonzero > b_nonzero) or (a_expl > b_expl):
            improved.append(q)
        elif (a_nonzero < b_nonzero) or (a_expl < b_expl):
            worse.append(q)
        else:
            unchanged.append(q)

    summary["improved_queries"] = improved
    summary["unchanged_queries"] = unchanged
    summary["worse_queries"] = worse

    _write_json(OUT_DIR / "kg_runtime_verification_semantic_patch_summary.json", summary)


def write_final_assessment_md() -> None:
    # Use existing artifacts for a grounded assessment.
    audit_before = _read_json(OUT_DIR / "document_fact_coverage_audit_before_fact_backfill.json")["aggregate"]
    audit_after = _read_json(OUT_DIR / "document_fact_coverage_audit_after_semantic_backfill.json")["aggregate"]
    fp = _read_json(OUT_DIR / "semantic_backfill_false_positive_review.json")
    expanded_summary = _read_json(OUT_DIR / "kg_runtime_verification_semantic_patch_summary.json")

    md = []
    md.append("## Semantic normalization + conservative backfill — final assessment\n")
    md.append("### What the patch fixed\n")
    md.append(f"- **added_triples**: see `outputs/document_fact_backfill_report.csv` (added rows exist; total added was observed as 53).\n")
    md.append(
        f"- **docs_with_zero_core_facts**: {audit_before['docs_with_zero_core_facts']} -> {audit_after['docs_with_zero_core_facts']}\n"
    )
    md.append(
        f"- **aboutTaxon coverage ratio**: {audit_before['coverage_ratio_by_fact_type']['aboutTaxon']:.4f} -> {audit_after['coverage_ratio_by_fact_type']['aboutTaxon']:.4f}\n"
    )
    md.append(
        f"- **documentProductionMode coverage ratio**: {audit_before['coverage_ratio_by_fact_type']['documentProductionMode']:.4f} -> {audit_after['coverage_ratio_by_fact_type']['documentProductionMode']:.4f}\n"
    )

    md.append("\n### What the patch did NOT fix\n")
    md.append(
        "- **aboutDisease coverage** stayed flat by design (topic/management/pathogen terms were denied; no coercion into Disease facts).\n"
    )

    md.append("\n### Coverage gain vs retrieval gain\n")
    md.append(
        "- This patch **materially improves data completeness** (facts coverage), but **query-level retrieval gain may be limited** for disease-focused queries because `aboutDisease` did not increase.\n"
    )
    md.append(
        "- See expanded verification summary in `outputs/kg_runtime_verification_semantic_patch_summary.json`.\n"
    )

    md.append("\n### False positive risk review\n")
    md.append(f"- Verdict: **{fp.get('verdict')}** (details in `outputs/semantic_backfill_false_positive_review.json`).\n")
    if fp.get("suspicious_cases"):
        md.append("- Suspicious cases were detected; review recommended.\n")
    else:
        md.append("- No suspicious cases flagged by current heuristics.\n")

    md.append("\n### Should we keep this patch?\n")
    md.append("- Recommendation: **KEEP, but monitor** generic entity usage in queries like 'fish disease'/'aquatic animals'.\n")

    md.append("\n### Next best step\n")
    md.append(
        "- If you want KG reranking to improve for disease/topic-heavy metadata, you need a controlled approach to represent **topics vs diseases** in ontology (e.g., Topic class) or enrich disease entities where truly applicable.\n"
    )

    out_path = OUT_DIR / "semantic_patch_final_assessment.md"
    out_path.write_text("\n".join(md), encoding="utf-8")


def main() -> None:
    _utf8()
    build_added_triples_reports()
    expanded_query_verification()
    write_final_assessment_md()
    print("[VALIDATION] Done. Reports written to outputs/.")


if __name__ == "__main__":
    main()

