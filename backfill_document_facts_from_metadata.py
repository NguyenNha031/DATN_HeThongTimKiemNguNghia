from __future__ import annotations

import csv
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

import kg_runtime
import semantic_normalization as sn
from rdflib import RDF, URIRef
from rdflib.namespace import SKOS


DEFAULT_INPUT_ONTOLOGY_PATH = Path("data") / "ontology" / "taxon_enriched_semantic.owl"
_DEFAULT_METADATA_XLSX_PATH = Path("data") / "metadata" / "document_metadata.xlsx"
_CLEAN_METADATA_XLSX_PATH = Path("data") / "metadata" / "document_metadata_cleaned.xlsx"
DEFAULT_METADATA_XLSX_PATH = _CLEAN_METADATA_XLSX_PATH if _CLEAN_METADATA_XLSX_PATH.exists() else _DEFAULT_METADATA_XLSX_PATH
DEFAULT_AUDIT_JSON_PATH = Path("outputs") / "document_fact_coverage_audit.json"

DEFAULT_OUTPUT_ONTOLOGY_PATH = Path("data") / "ontology" / "taxon_enriched_facts_v2.owl"
DEFAULT_REPORT_JSON_PATH = Path("outputs") / "document_fact_backfill_report.json"
DEFAULT_REPORT_CSV_PATH = Path("outputs") / "document_fact_backfill_report.csv"


CORE_FACT_TYPES = {
    "aboutTaxon": {
        "predicate_local_name": "aboutTaxon",
        "metadata_column": "related_taxon",
        "expected_entity_type": "species",
    },
    "aboutDisease": {
        "predicate_local_name": "aboutDisease",
        "metadata_column": "related_disease",
        "expected_entity_type": "disease",
    },
    "aboutLocation": {
        "predicate_local_name": "aboutLocation",
        "metadata_column": "related_location",
        "expected_entity_type": "location",
    },
    "documentProductionMode": {
        "predicate_local_name": "documentProductionMode",
        "metadata_column": "production_mode",
        "expected_entity_type": "mode",
    },
}


def _reconfigure_stdout_utf8() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stdin.reconfigure(encoding="utf-8")
    except Exception:
        pass


def _split_multi_value(v: Any) -> list[str]:
    if v is None:
        return []
    if isinstance(v, float) and v != v:
        return []
    s = str(v).strip()
    if not s:
        return []
    return [x.strip() for x in s.split(";") if x.strip()]


def _local_name(uri: Any) -> str:
    s = str(uri)
    if "#" in s:
        return s.rsplit("#", 1)[-1]
    if "/" in s:
        return s.rsplit("/", 1)[-1]
    return s


def _find_predicate_uri_by_localname(graph, local_name: str):
    for p in set(graph.predicates()):
        if _local_name(p) == local_name:
            return p
    return None


def _load_audit(audit_json_path: Path) -> dict[str, Any]:
    obj = json.loads(audit_json_path.read_text(encoding="utf-8"))
    # Script writes: {"aggregate": ..., "documents": [...]}
    docs = obj.get("documents") or []
    aggregate = obj.get("aggregate") or {}
    return {"aggregate": aggregate, "documents": docs}


def backfill_document_facts_from_metadata(
    input_ontology_path: Path = DEFAULT_INPUT_ONTOLOGY_PATH,
    metadata_xlsx_path: Path = DEFAULT_METADATA_XLSX_PATH,
    audit_json_path: Path = DEFAULT_AUDIT_JSON_PATH,
    output_ontology_path: Path = DEFAULT_OUTPUT_ONTOLOGY_PATH,
    report_json_path: Path = DEFAULT_REPORT_JSON_PATH,
    report_csv_path: Path = DEFAULT_REPORT_CSV_PATH,
) -> None:
    _reconfigure_stdout_utf8()

    graph = kg_runtime.load_kg(input_ontology_path)
    kg_index = kg_runtime.build_kg_index(graph)
    label_to_entities = kg_index.get("label_to_entities") or {}

    # Predicates needed
    predicates = {}
    for ft, info in CORE_FACT_TYPES.items():
        p = _find_predicate_uri_by_localname(graph, info["predicate_local_name"])
        if p is not None:
            predicates[ft] = p

    # Metadata
    df_meta = pd.read_excel(metadata_xlsx_path)
    if "doc_id" not in df_meta.columns:
        raise ValueError("metadata.xlsx missing doc_id")
    metadata_lookup = {}
    for _, row in df_meta.iterrows():
        doc_id = str(row["doc_id"]).strip()
        metadata_lookup[doc_id] = row.to_dict()

    audit_obj = _load_audit(audit_json_path)
    audit_docs = audit_obj.get("documents") or []

    # Backup output if exists
    output_ontology_path.parent.mkdir(parents=True, exist_ok=True)
    if output_ontology_path.exists():
        backup_path = output_ontology_path.with_suffix(output_ontology_path.suffix + ".bak")
        # Add timestamp-like uniqueness via file size not stable; just append count by loop.
        suffix_i = 1
        while backup_path.exists():
            backup_path = output_ontology_path.with_suffix(output_ontology_path.suffix + f".bak_{suffix_i}")
            suffix_i += 1
        # shutil is heavier to import, but acceptable
        import shutil

        shutil.copy2(str(output_ontology_path), str(backup_path))
        print(f"[BACKFILL] Backup created: {backup_path}")

    added_triples = 0
    skipped_docs = 0
    report_rows: list[dict[str, Any]] = []
    normalization_rows: list[dict[str, Any]] = []

    def map_tokens_exact(tokens: list[str], expected_entity_type: str) -> tuple[list[str], list[str]]:
        mapped_uris: list[str] = []
        unmapped: list[str] = []
        for t in tokens:
            t_norm = kg_runtime.normalize_kg_text(t)
            if not t_norm:
                continue
            ents = label_to_entities.get(t_norm) or []
            ents = [e for e in ents if (e.get("entity_type") or "") == expected_entity_type]
            if ents:
                mapped_uris.extend([e["uri"] for e in ents if e.get("uri")])
            else:
                unmapped.append(t)
        # de-dupe while preserving order
        seen = set()
        uniq = []
        for u in mapped_uris:
            if u not in seen:
                seen.add(u)
                uniq.append(u)
        return uniq, unmapped

    for doc in audit_docs:
        doc_uri = doc.get("doc_uri")
        doc_id = str(doc.get("doc_id", "") or "").strip()
        metadata_row_found = bool(doc.get("metadata_row_found", False))
        missing_fact_types_str = str(doc.get("missing_fact_types", "") or "")
        missing_fact_types = [x for x in missing_fact_types_str.split(";") if x]

        if not doc_uri or not doc_id:
            continue
        if not metadata_row_found:
            skipped_docs += 1
            continue
        if not missing_fact_types:
            continue
        if doc_id not in metadata_lookup:
            skipped_docs += 1
            continue

        md_row = metadata_lookup[doc_id]
        doc_uri_node = URIRef(doc_uri)

        # Backfill per fact type: add triples only when *all* tokens map exactly
        # to existing ontology entities (high confidence for that triple).
        for ft in missing_fact_types:
            if ft not in CORE_FACT_TYPES:
                continue
            if ft not in predicates:
                # Predicate missing -> cannot backfill.
                report_rows.append(
                    {
                        "doc_id": doc_id,
                        "doc_uri": doc_uri,
                        "predicate": CORE_FACT_TYPES[ft]["predicate_local_name"],
                        "raw_metadata_value": md_row.get(CORE_FACT_TYPES[ft]["metadata_column"], ""),
                        "mapped_entity_uri": "",
                        "confidence": "low",
                        "status": "skipped_no_predicate",
                        "reason": "predicate missing in ontology",
                    }
                )
                continue

            md_col = CORE_FACT_TYPES[ft]["metadata_column"]
            raw_value = md_row.get(md_col, "")
            tokens = _split_multi_value(raw_value)
            if not tokens:
                continue

            expected_type = CORE_FACT_TYPES[ft]["expected_entity_type"]

            mapped_uris: list[str] = []
            unmapped_tokens: list[str] = []
            denied_tokens: list[str] = []

            for tok in tokens:
                dec = sn.decide_token_action(
                    token=tok,
                    source_field=md_col,
                    candidate_property=CORE_FACT_TYPES[ft]["predicate_local_name"],
                    kg_index=kg_index,
                    expected_entity_type=expected_type,
                )
                normalization_rows.append(
                    {
                        "doc_id": doc_id,
                        "doc_uri": doc_uri,
                        "token": dec.token,
                        "source_field": dec.source_field,
                        "candidate_property": dec.candidate_property,
                        "normalized_label": dec.normalized_label,
                        "candidate_class": dec.candidate_class,
                        "candidate_property_suggested": dec.candidate_property_suggested,
                        "target_uri": dec.target_uri,
                        "decision": dec.decision,
                        "reason": dec.reason,
                        "confidence": dec.confidence,
                    }
                )

                if dec.decision == "ADD_EXACT_ALIAS" and dec.target_uri:
                    mapped_uris.append(dec.target_uri)
                elif dec.decision == "ADD_NEW_ENTITY" and dec.target_uri:
                    # This run does not create entities; it requires prior semantic enrichment step.
                    # Treat as unmapped for backfill and let report explain.
                    unmapped_tokens.append(tok)
                elif dec.decision == "RECLASSIFY_PROPERTY":
                    denied_tokens.append(tok)
                else:
                    unmapped_tokens.append(tok)

            # Report unmapped tokens only (do not block mapped triples).
            for um in unmapped_tokens:
                    report_rows.append(
                        {
                            "doc_id": doc_id,
                            "doc_uri": doc_uri,
                            "predicate": CORE_FACT_TYPES[ft]["predicate_local_name"],
                            "raw_metadata_value": raw_value,
                            "mapped_entity_uri": "",
                            "confidence": "low",
                            "status": "skipped_unmapped_token",
                        "reason": f"unmapped_or_denied token: {um}",
                        }
                    )

            for dt in denied_tokens:
                report_rows.append(
                    {
                        "doc_id": doc_id,
                        "doc_uri": doc_uri,
                        "predicate": CORE_FACT_TYPES[ft]["predicate_local_name"],
                        "raw_metadata_value": raw_value,
                        "mapped_entity_uri": "",
                        "confidence": "high",
                        "status": "denied_auto_backfill",
                        "reason": f"denied/reclassify: {dt}",
                    }
                )

            # Add triples only for mapped URIs with exact alias match (high confidence per triple).
            if not mapped_uris:
                continue

            # Add triples (avoid duplicates)
            for ent_uri in mapped_uris:
                p_uri = predicates[ft]
                if (doc_uri_node, p_uri, URIRef(ent_uri)) in graph:
                    continue
                graph.add((doc_uri_node, p_uri, URIRef(ent_uri)))
                added_triples += 1
                report_rows.append(
                    {
                        "doc_id": doc_id,
                        "doc_uri": doc_uri,
                        "predicate": CORE_FACT_TYPES[ft]["predicate_local_name"],
                        "raw_metadata_value": raw_value,
                        "mapped_entity_uri": ent_uri,
                        "confidence": "high",
                        "status": "added",
                        "reason": "exact ontology alias match",
                    }
                )

    # Save output ontology
    import shutil

    output_ontology_path.parent.mkdir(parents=True, exist_ok=True)
    graph.serialize(destination=str(output_ontology_path), format="xml")

    # Write report
    outputs = {
        "added_triples": added_triples,
        "skipped_docs": skipped_docs,
        "input_ontology": str(input_ontology_path),
        "output_ontology": str(output_ontology_path),
        "audit_json": str(audit_json_path),
    }
    Path(report_json_path).parent.mkdir(parents=True, exist_ok=True)
    report_json_path.write_text(json.dumps({**outputs, "rows": report_rows}, ensure_ascii=False, indent=2), encoding="utf-8")

    # CSV
    Path(report_csv_path).parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(report_rows).to_csv(report_csv_path, index=False, encoding="utf-8-sig")

    # Normalization report (machine-readable)
    norm_json = Path("outputs") / "metadata_normalization_report.json"
    norm_csv = Path("outputs") / "metadata_normalization_report.csv"
    norm_json.write_text(
        json.dumps(
            {
                "input_ontology": str(input_ontology_path),
                "decision_rows": len(normalization_rows),
                "rows": normalization_rows,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    pd.DataFrame(normalization_rows).to_csv(norm_csv, index=False, encoding="utf-8-sig")

    print("[BACKFILL] Done.")
    print(f"  - added_triples: {added_triples}")
    print(f"  - skipped_docs: {skipped_docs}")
    print(f"  - report_json: {report_json_path}")
    print(f"  - report_csv: {report_csv_path}")
    print(f"  - normalization_json: {norm_json}")
    print(f"  - normalization_csv: {norm_csv}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Backfill document facts from metadata (conservative).")
    parser.add_argument("--input_ontology_path", type=str, default=str(DEFAULT_INPUT_ONTOLOGY_PATH))
    parser.add_argument("--metadata_xlsx_path", type=str, default=str(DEFAULT_METADATA_XLSX_PATH))
    parser.add_argument("--audit_json_path", type=str, default=str(DEFAULT_AUDIT_JSON_PATH))
    parser.add_argument("--output_ontology_path", type=str, default=str(DEFAULT_OUTPUT_ONTOLOGY_PATH))
    parser.add_argument("--report_json_path", type=str, default=str(DEFAULT_REPORT_JSON_PATH))
    parser.add_argument("--report_csv_path", type=str, default=str(DEFAULT_REPORT_CSV_PATH))
    args = parser.parse_args()

    backfill_document_facts_from_metadata(
        input_ontology_path=Path(args.input_ontology_path),
        metadata_xlsx_path=Path(args.metadata_xlsx_path),
        audit_json_path=Path(args.audit_json_path),
        output_ontology_path=Path(args.output_ontology_path),
        report_json_path=Path(args.report_json_path),
        report_csv_path=Path(args.report_csv_path),
    )

