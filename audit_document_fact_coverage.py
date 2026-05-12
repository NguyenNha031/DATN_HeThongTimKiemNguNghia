from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

import kg_runtime


DEFAULT_ONTOLOGY_PATH = Path("data") / "ontology" / "taxon_enriched_aliases.owl"
_DEFAULT_METADATA_XLSX_PATH = Path("data") / "metadata" / "document_metadata.xlsx"
_CLEAN_METADATA_XLSX_PATH = Path("data") / "metadata" / "document_metadata_cleaned.xlsx"
DEFAULT_METADATA_XLSX_PATH = _CLEAN_METADATA_XLSX_PATH if _CLEAN_METADATA_XLSX_PATH.exists() else _DEFAULT_METADATA_XLSX_PATH
DEFAULT_VERIFICATION_JSON_PATH = Path("outputs") / "kg_runtime_verification.json"

OUTPUT_AUDIT_JSON_PATH = Path("outputs") / "document_fact_coverage_audit.json"
OUTPUT_AUDIT_CSV_PATH = Path("outputs") / "document_fact_coverage_audit.csv"


CORE_FACT_TYPES = {
    "aboutTaxon": {
        "predicate_local_name": "aboutTaxon",
        "metadata_column": "related_taxon",
    },
    "aboutDisease": {
        "predicate_local_name": "aboutDisease",
        "metadata_column": "related_disease",
    },
    "aboutLocation": {
        "predicate_local_name": "aboutLocation",
        "metadata_column": "related_location",
    },
    "documentProductionMode": {
        "predicate_local_name": "documentProductionMode",
        "metadata_column": "production_mode",
    },
}


def _reconfigure_stdout_utf8() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stdin.reconfigure(encoding="utf-8")
    except Exception:
        pass


def _local_name(uri: Any) -> str:
    s = str(uri)
    if "#" in s:
        return s.rsplit("#", 1)[-1]
    if "/" in s:
        return s.rsplit("/", 1)[-1]
    return s


def _split_multi_value(v: Any) -> list[str]:
    if v is None:
        return []
    if isinstance(v, float) and v != v:  # NaN
        return []
    s = str(v).strip()
    if not s:
        return []
    return [x.strip() for x in s.split(";") if x.strip()]


def _walk_superclasses(g: "kg_runtime.Graph", class_uri: Any, max_depth: int = 12) -> set[Any]:
    # Local helper to avoid relying on internal kg_runtime functions.
    out: set[Any] = set()
    frontier: list[Any] = [class_uri]
    depth = 0
    while frontier and depth < max_depth:
        nxt: list[Any] = []
        for c in frontier:
            if c in out:
                continue
            out.add(c)
            for sup in g.objects(c, kg_runtime.RDFS.subClassOf):  # type: ignore[attr-defined]
                if sup not in out:
                    nxt.append(sup)
        frontier = nxt
        depth += 1
    return out


def _infer_doc_related_classes(graph: Any, doc_class_uri: Any) -> set[Any]:
    # Document individuals often use subclasses (e.g. TechnicalReport).
    related: set[Any] = {doc_class_uri}
    try:
        # Identify all OWL classes that are bounded subclasses of Document.
        for cls in graph.subjects(kg_runtime.RDF.type, kg_runtime.OWL.Class):  # type: ignore[attr-defined]
            if _local_name(cls) == "Document":
                related.add(cls)
                continue
            try:
                ancestors = _walk_superclasses(graph, cls, max_depth=12)
                if doc_class_uri in ancestors:
                    related.add(cls)
            except Exception:
                continue
    except Exception:
        pass
    return related


def _find_class_uri_by_localname(graph: Any, local_name: str) -> Any | None:
    try:
        for c in graph.subjects(kg_runtime.RDF.type, kg_runtime.OWL.Class):  # type: ignore[attr-defined]
            if _local_name(c) == local_name:
                return c
    except Exception:
        pass
    return None


def _find_predicate_uris_by_localnames(graph: Any, local_names: Iterable[str]) -> dict[str, Any]:
    wanted = set(local_names)
    out: dict[str, Any] = {}
    for p in set(graph.predicates()):
        if _local_name(p) in wanted:
            out[_local_name(p)] = p
    return out


def analyze_fact_coverage(
    ontology_path: Path = DEFAULT_ONTOLOGY_PATH,
    metadata_xlsx_path: Path = DEFAULT_METADATA_XLSX_PATH,
    verification_json_path: Path = DEFAULT_VERIFICATION_JSON_PATH,
    output_json_path: Path = OUTPUT_AUDIT_JSON_PATH,
    output_csv_path: Path = OUTPUT_AUDIT_CSV_PATH,
) -> None:
    _reconfigure_stdout_utf8()

    graph = kg_runtime.load_kg(ontology_path)
    kg_index = kg_runtime.build_kg_index(graph)

    doc_class_uri = _find_class_uri_by_localname(graph, "Document")
    if not doc_class_uri:
        raise RuntimeError("Ontology missing Document class (owl:Class) - cannot audit.")

    doc_related_classes = _infer_doc_related_classes(graph, doc_class_uri)

    # Collect all Document nodes (union typed by document-related classes).
    doc_uris: set[Any] = set()
    for cls in doc_related_classes:
        try:
            for s in graph.subjects(kg_runtime.RDF.type, cls):  # type: ignore[attr-defined]
                doc_uris.add(s)
        except Exception:
            continue

    predicate_uris = _find_predicate_uris_by_localnames(
        graph, [v["predicate_local_name"] for v in CORE_FACT_TYPES.values()]
    )

    # Metadata lookup
    df_meta = pd.read_excel(metadata_xlsx_path)
    if "doc_id" not in df_meta.columns:
        raise ValueError("Missing metadata column: doc_id")

    metadata_lookup = {str(r["doc_id"]).strip(): r.to_dict() for _, r in df_meta.iterrows()}

    p_title = None
    for p in set(graph.predicates()):
        if _local_name(p) == "title":
            p_title = p
            break

    # Verification top-k docs (for top missing facts)
    verification_obj: dict[str, Any] = {}
    if verification_json_path.exists():
        try:
            verification_obj = json.loads(verification_json_path.read_text(encoding="utf-8"))
        except Exception:
            verification_obj = {}

    top_priority_docs: set[str] = set()
    for qd in verification_obj.get("per_query_verification_details") or []:
        for item in (qd.get("top5_results") or []):
            uri = item.get("doc_uri_in_kg")
            if uri:
                top_priority_docs.add(str(uri))

    missing_fact_counter: Counter[str] = Counter()
    missing_fact_by_doc: dict[str, list[str]] = {}

    # Precompute label_to_entities for mapping confidence.
    label_to_entities = kg_index.get("label_to_entities") or {}

    # Audit per document
    audit_rows: list[dict[str, Any]] = []

    fact_type_pred_map = {}
    for ft, info in CORE_FACT_TYPES.items():
        pred_local = info["predicate_local_name"]
        if pred_local in predicate_uris:
            fact_type_pred_map[ft] = predicate_uris[pred_local]

    total_docs = len(doc_uris)

    docs_with_any_fact = 0
    docs_with_all_core_facts = 0
    docs_with_zero_core_facts = 0

    per_fact_type_doc_presence = defaultdict(int)

    # Index metadata presence quickly
    def metadata_has_column(row: dict, col: str) -> bool:
        if not row:
            return False
        v = row.get(col)
        return bool(v is not None and not (isinstance(v, float) and v != v) and str(v).strip())

    # Confidence mapping: exact normalized alias match only.
    def map_tokens_exact(tokens: list[str], entity_type_key: str) -> tuple[list[str], bool, bool]:
        mapped = []
        any_unmapped = False
        any_mapped = False
        for t in tokens:
            t_norm = kg_runtime.normalize_kg_text(t)
            if not t_norm:
                continue
            ents = label_to_entities.get(t_norm) or []
            ents = [e for e in ents if (e.get("entity_type") or "") == entity_type_key]
            if ents:
                any_mapped = True
                mapped.extend([e["uri"] for e in ents if e.get("uri")])
            else:
                any_unmapped = True
        return mapped, any_mapped, (not any_unmapped)

    entity_type_map = {
        "aboutTaxon": "species",
        "aboutDisease": "disease",
        "aboutLocation": "location",
        "documentProductionMode": "mode",
    }

    # Iterate stable order by string form but keep URIRef nodes for rdflib graph queries.
    doc_uris_sorted = sorted(list(doc_uris), key=lambda x: str(x))
    for doc_uri in doc_uris_sorted:
        doc_id = _local_name(doc_uri)
        row_meta = metadata_lookup.get(str(doc_id), {})
        metadata_row_found = bool(row_meta)

        fact_counts: dict[str, int] = {}
        fact_present: dict[str, bool] = {}

        total_structured = 0
        for ft, pred_node in fact_type_pred_map.items():
            try:
                c = len(list(graph.objects(doc_uri, pred_node)))
            except Exception:
                c = 0
            fact_counts[ft] = c
            fact_present[ft] = c > 0
            if c > 0:
                total_structured += 1
                per_fact_type_doc_presence[ft] += 1

        any_core_fact = total_structured > 0
        all_core = all(fact_present.get(ft, False) for ft in CORE_FACT_TYPES.keys())
        zero_core = not any_core_fact

        if any_core_fact:
            docs_with_any_fact += 1
        if all_core:
            docs_with_all_core_facts += 1
        if zero_core:
            docs_with_zero_core_facts += 1

        title_val = ""
        if p_title is not None:
            try:
                for t in graph.objects(doc_uri, p_title):
                    title_val = str(t).strip()
                    break
            except Exception:
                title_val = ""

        # metadata present flags/counts
        metadata_present_flags = {}
        metadata_value_tokens = {}
        for ft, info in CORE_FACT_TYPES.items():
            col = info["metadata_column"]
            v = row_meta.get(col, "")
            tokens = _split_multi_value(v)
            metadata_present_flags[ft] = bool(tokens)
            metadata_value_tokens[ft] = tokens

        missing_fact_types: list[str] = []
        for ft in CORE_FACT_TYPES.keys():
            if fact_counts.get(ft, 0) == 0 and metadata_present_flags.get(ft, False):
                missing_fact_types.append(ft)

        confidence_to_backfill = "low"
        if metadata_row_found and missing_fact_types:
            # For each missing fact type: exact alias mapping confidence.
            per_ft_conf = {}
            for ft in missing_fact_types:
                tokens = metadata_value_tokens.get(ft) or []
                _, any_mapped, all_mapped_exact = map_tokens_exact(tokens, entity_type_map[ft])
                if all_mapped_exact and any_mapped:
                    per_ft_conf[ft] = "high"
                elif any_mapped:
                    per_ft_conf[ft] = "medium"
                else:
                    per_ft_conf[ft] = "low"

            # overall
            if all(v == "high" for v in per_ft_conf.values()):
                confidence_to_backfill = "high"
            elif any(v in ("high", "medium") for v in per_ft_conf.values()):
                confidence_to_backfill = "medium"
            else:
                confidence_to_backfill = "low"

        if str(doc_uri) in top_priority_docs:
            missing_fact_by_doc[str(doc_uri)] = missing_fact_types
            for ft in missing_fact_types:
                missing_fact_counter[ft] += 1

        audit_rows.append(
            {
                "doc_uri": doc_uri,
                "doc_id": doc_id,
                "title": title_val,
                "metadata_row_found": metadata_row_found,
                "aboutTaxon_count": fact_counts.get("aboutTaxon", 0),
                "has_aboutTaxon": fact_present.get("aboutTaxon", False),
                "aboutDisease_count": fact_counts.get("aboutDisease", 0),
                "has_aboutDisease": fact_present.get("aboutDisease", False),
                "aboutLocation_count": fact_counts.get("aboutLocation", 0),
                "has_aboutLocation": fact_present.get("aboutLocation", False),
                "documentProductionMode_count": fact_counts.get("documentProductionMode", 0),
                "has_documentProductionMode": fact_present.get("documentProductionMode", False),
                "total_structured_fact_count": total_structured,
                "metadata_aboutTaxon_present": metadata_present_flags.get("aboutTaxon", False),
                "metadata_aboutDisease_present": metadata_present_flags.get("aboutDisease", False),
                "metadata_aboutLocation_present": metadata_present_flags.get("aboutLocation", False),
                "metadata_documentProductionMode_present": metadata_present_flags.get("documentProductionMode", False),
                "missing_fact_types": ";".join(missing_fact_types),
                "confidence_to_backfill": confidence_to_backfill,
            }
        )

    # Aggregate summary
    fact_coverage_ratio = {}
    for ft in CORE_FACT_TYPES.keys():
        fact_coverage_ratio[ft] = float(per_fact_type_doc_presence.get(ft, 0)) / float(total_docs) if total_docs else 0.0

    missing_fact_types_top = [
        {"fact_type": k, "count": v} for k, v in missing_fact_counter.most_common(20)
    ]

    audit_obj = {
        "ontology_path_analyzed": str(ontology_path),
        "total_documents": total_docs,
        "docs_with_at_least_1_core_structured_fact": docs_with_any_fact,
        "docs_with_all_4_core_fact_types": docs_with_all_core_facts,
        "docs_with_zero_core_facts": docs_with_zero_core_facts,
        "coverage_ratio_by_fact_type": fact_coverage_ratio,
        "top_priority_missing_fact_types_from_verification": missing_fact_types_top,
        "missing_fact_by_doc_uri_for_priority_docs": missing_fact_by_doc,
    }

    output_json_path.parent.mkdir(parents=True, exist_ok=True)
    output_json_path.write_text(
        json.dumps({"aggregate": audit_obj, "documents": audit_rows}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    output_csv_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(audit_rows).to_csv(output_csv_path, index=False, encoding="utf-8-sig")

    print("[AUDIT] Done.")
    print(f"[AUDIT] JSON: {output_json_path}")
    print(f"[AUDIT] CSV: {output_csv_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Audit OWL Document fact coverage.")
    parser.add_argument("--ontology_path", type=str, default=str(DEFAULT_ONTOLOGY_PATH))
    parser.add_argument("--metadata_xlsx_path", type=str, default=str(DEFAULT_METADATA_XLSX_PATH))
    parser.add_argument("--verification_json_path", type=str, default=str(DEFAULT_VERIFICATION_JSON_PATH))
    parser.add_argument("--output_json_path", type=str, default=str(OUTPUT_AUDIT_JSON_PATH))
    parser.add_argument("--output_csv_path", type=str, default=str(OUTPUT_AUDIT_CSV_PATH))
    args = parser.parse_args()

    analyze_fact_coverage(
        ontology_path=Path(args.ontology_path),
        metadata_xlsx_path=Path(args.metadata_xlsx_path),
        verification_json_path=Path(args.verification_json_path),
        output_json_path=Path(args.output_json_path),
        output_csv_path=Path(args.output_csv_path),
    )

