from __future__ import annotations

import csv
import argparse
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

from rdflib import Graph, Literal, RDF, OWL, URIRef
from rdflib.namespace import RDFS

# Reuse ontology index helpers from kg_runtime (incremental integration)
import kg_runtime


DEFAULT_METADATA_PATH = Path("data") / "metadata" / "document_metadata.xlsx"
DEFAULT_OWL_PATH = Path("data") / "ontology" / "taxon.owl"
DEFAULT_OUTPUT_OWL_PATH = Path("data") / "ontology" / "taxon_enriched.owl"
DEFAULT_REPORT_PATH = Path("data") / "ontology" / "mapping_report.csv"


MANUAL_ALIASES: dict[str, dict[str, list[str]]] = {
    "disease": {
        "AHPND": [
            "ahpnd",
            "acute hepatopancreatic necrosis disease",
            "benh hoai tu gan tuy cap",
            "bệnh hoại tử gan tụy cấp",
        ],
        "fish diseases": [
            "fish diseases",
            "benh thuong gap",
            "benh thuong gap tren ca",
            "benh ca",
            "benh ca thuong gap",
        ],
        "health management": [
            "health management",
            "quan ly suc khoe",
        ],
        "biosecurity": [
            "biosecurity",
            "an toan sinh hoc",
        ],
        "disease prevention": [
            "disease prevention",
            "phong benh",
        ],
    },
    "species": {
        "shrimp": [
            "shrimp",
            "tom",
            "tôm",
        ],
        "fish": [
            "fish",
            "ca bop",
            "cá bớp",
            "cá bop",
        ],
        "Penaeus monodon": [
            "penaeus monodon",
            "tom su",
            "tom sú",
            "black tiger shrimp",
        ],
        # Map to the ontology's existing prefLabel/alias ("Tôm thẻ chân trắng")
        # so that metadata value "Penaeus vannamei" can still be linked to KG.
        "tôm thẻ chân trắng": [
            "penaeus vannamei",
            "litopenaeus vannamei",
            "tom the chan trang",
            "tom thẻ chân trắng",
            "whiteleg shrimp",
            "white shrimp",
        ],
        "lobster": [
            "lobster",
            "lobsters",
            "tom hum",
            "tôm hùm",
        ],
    },
    "location": {
        "India": ["india", "an do", "ấn độ"],
        "Vietnam": ["vietnam", "viet nam", "việt nam"],
        "Khanh Hoa": ["khanh hoa", "khánh hòa"],
        "Latin America": ["latin america", "my la tinh"],
        "Caribbean": ["caribbean"],
        "Global": ["global", "toan cau", "toàn cầu"],
    },
    "mode": {
        # Ontology currently only contains "Aquaculture" as a ProductionMode.
        # Map hatchery/shrimp aquaculture variants to that existing node.
        "Aquaculture": [
            "shrimp aquaculture",
            "nuoi tom",
            "nuôi tôm",
            "hatchery",
            "hatchery aquaculture",
            "trai giong",
            "trại giống",
            "aquaculture",
            "nuoi trong thuy san",
            "nuôi trồng thủy sản",
        ],
    },
}


def _local_name(uri: Any) -> str:
    s = str(uri)
    if "#" in s:
        return s.rsplit("#", 1)[-1]
    if "/" in s:
        return s.rsplit("/", 1)[-1]
    return s


def _find_class_uri(graph: Graph, local_name: str) -> Any | None:
    for c in graph.subjects(RDF.type, OWL.Class):
        if _local_name(c) == local_name:
            return c
    return None


def _find_predicate_uri(graph: Graph, local_name: str) -> Any | None:
    # Scan only predicate URIs that appear in the graph.
    for p in set(graph.predicates()):
        if _local_name(p) == local_name:
            return p
    return None


def _split_multi_value(v: Any) -> list[str]:
    if v is None or (isinstance(v, float) and v != v):
        return []
    s = str(v).strip()
    if not s:
        return []
    # Metadata uses semicolon separators.
    parts = [x.strip() for x in s.split(";")]
    return [p for p in parts if p]


def _canonicalize_term(entity_type: str, term_norm: str) -> str:
    # Keep consistent with kg_runtime matching behavior (normalize first).
    if entity_type == "species":
        if term_norm in {"lobsters"}:
            return "lobster"
        if term_norm in {
            "penaeus vannamei",
            "litopenaeus vannamei",
            "whiteleg shrimp",
            "white shrimp",
        }:
            return "Penaeus vannamei"
        if term_norm in {"penaeus monodon", "black tiger shrimp"}:
            return "Penaeus monodon"
        if term_norm in {"tom su", "tom sú"}:
            return "Penaeus monodon"
        if term_norm in {"tom", "tôm"}:
            return "shrimp"
    if entity_type == "location":
        if term_norm in {"khanh hoa"}:
            return "Khanh Hoa"
        if term_norm in {"vietnam"}:
            return "Vietnam"
        if term_norm in {"india"}:
            return "India"
        if term_norm in {"global"}:
            return "Global"
    return term_norm


def _build_manual_fallback_map(entity_type: str) -> dict[str, str]:
    """
    alias_norm -> canonical_term (normalized).
    """
    out: dict[str, str] = {}
    for canonical, aliases in MANUAL_ALIASES.get(entity_type, {}).items():
        out[kg_runtime.normalize_kg_text(canonical)] = kg_runtime.normalize_kg_text(canonical)
        for a in aliases:
            out[kg_runtime.normalize_kg_text(a)] = kg_runtime.normalize_kg_text(canonical)
    return out


@dataclass(frozen=True)
class MappingResult:
    mapped_uris: list[str]
    status: str
    reason: str


def _map_value_to_uris(
    term: str,
    entity_type: str,
    kg_index: dict[str, Any],
    manual_alias_map: dict[str, str],
) -> MappingResult:
    """
    Ontology-first mapping:
    - exact normalized alias match in kg_index
    - fallback to whitespace-insensitive match
    - manual fallback canonicalization (then re-try exact match)
    """
    term_norm = kg_runtime.normalize_kg_text(term)
    if not term_norm:
        return MappingResult([], "empty", "empty term")

    label_to_entities = kg_index.get("label_to_entities") or {}

    def candidates_for_alias(alias_norm: str) -> list[str]:
        ents = label_to_entities.get(alias_norm) or []
        return [e["uri"] for e in ents if e.get("entity_type") == entity_type]

    # 1) exact
    uris = candidates_for_alias(term_norm)
    if uris:
        return MappingResult(uris, "mapped", "ontology exact alias match")

    # 2) whitespace-insensitive
    term_comp = term_norm.replace(" ", "")
    alias_matches = []
    for alias_norm in label_to_entities.keys():
        if alias_norm.replace(" ", "") == term_comp:
            alias_matches.append(alias_norm)
    for alias_norm in alias_matches:
        uris = candidates_for_alias(alias_norm)
        if uris:
            return MappingResult(uris, "mapped", "ontology whitespace-insensitive match")

    # 3) manual fallback
    canonical_norm = manual_alias_map.get(term_norm)
    if canonical_norm:
        uris = candidates_for_alias(canonical_norm)
        if uris:
            return MappingResult(uris, "mapped_manual", "manual fallback mapped to ontology alias")

    return MappingResult([], "unmapped", "no ontology match (and manual fallback failed)")


def sync_metadata_to_owl(
    metadata_path: Path = DEFAULT_METADATA_PATH,
    owl_path: Path = DEFAULT_OWL_PATH,
    output_owl_path: Path = DEFAULT_OUTPUT_OWL_PATH,
    report_path: Path = DEFAULT_REPORT_PATH,
) -> None:
    graph = kg_runtime.load_kg(owl_path)
    kg_index = kg_runtime.build_kg_index(graph)

    doc_class_uri = _find_class_uri(graph, "Document")
    if not doc_class_uri:
        raise RuntimeError("Ontology missing owl:Class Document (cannot create/update individuals).")
    doc_ns_prefix = str(doc_class_uri).rsplit("#", 1)[0] + "#"

    # Predicates (best-effort; if not exist, we will skip and report)
    p_doc_id = _find_predicate_uri(graph, "docId") or _find_predicate_uri(graph, "docID")
    p_title = _find_predicate_uri(graph, "title")
    p_file_path = _find_predicate_uri(graph, "filePath")
    p_language = _find_predicate_uri(graph, "language")
    p_keywords = _find_predicate_uri(graph, "keywords")

    p_about_taxon = _find_predicate_uri(graph, "aboutTaxon")
    p_about_disease = _find_predicate_uri(graph, "aboutDisease")
    p_about_location = _find_predicate_uri(graph, "aboutLocation")
    p_doc_prod_mode = _find_predicate_uri(graph, "documentProductionMode")

    # Pre-build manual fallback maps for required entity types
    manual_maps = {
        et: _build_manual_fallback_map(et)
        for et in ["disease", "species", "location", "mode"]
    }

    df = pd.read_excel(metadata_path)
    required_columns = ["doc_id", "title", "file_path", "related_taxon", "related_disease", "related_location", "production_mode"]
    missing = [c for c in required_columns if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required metadata columns: {missing}")
    report_rows: list[dict[str, Any]] = []
    created_count = 0
    updated_count = 0
    skipped_count = 0
    unmapped_counts = {"disease": 0, "species": 0, "location": 0, "mode": 0}
    def _walk_superclasses(g: Graph, class_uri: URIRef, max_depth: int = 12) -> set[URIRef]:
        out: set[URIRef] = set()
        frontier: list[URIRef] = [class_uri]
        depth = 0
        while frontier and depth < max_depth:
            nxt: list[URIRef] = []
            for c in frontier:
                if c in out:
                    continue
                out.add(c)
                for sup in g.objects(c, RDFS.subClassOf):
                    if isinstance(sup, URIRef) and sup not in out:
                        nxt.append(sup)
            frontier = nxt
            depth += 1
        return out
    doc_related_classes: set[URIRef] = set()
    try:
        for cls in graph.subjects(RDF.type, OWL.Class):
            if not isinstance(cls, URIRef):
                continue
            ancestors = _walk_superclasses(graph, cls, max_depth=12)
            if doc_class_uri in ancestors or cls == doc_class_uri:
                doc_related_classes.add(cls)
    except Exception:
        doc_related_classes = {doc_class_uri}

    def doc_uri_for_doc_id(doc_id: str) -> URIRef:
        # Reuse existing node if it is typed as Document (or a bounded subclass).
        doc_id_str = str(doc_id).strip()
        if not doc_id_str:
            return URIRef("")
        for typed_cls in doc_related_classes:
            for s in graph.subjects(RDF.type, typed_cls):
                if _local_name(s) == doc_id_str:
                    return s
        return URIRef(doc_ns_prefix + doc_id_str)

    # Iterate rows and update/create Document individuals
    for row_index, row in df.iterrows():
        doc_id = str(row.get("doc_id", "")).strip()
        if not doc_id:
            skipped_count += 1
            report_rows.append(
                {
                    "row_index": row_index,
                    "doc_id": "",
                    "field_name": "doc_id",
                    "raw_value": "",
                    "status": "skipped",
                    "mapped_uri_or_reason": "empty doc_id",
                }
            )
            continue

        doc_uri = doc_uri_for_doc_id(doc_id)
        existed = bool(list(graph.objects(doc_uri, RDF.type)))
        if existed:
            updated_count += 1
        else:
            created_count += 1

        # Ensure rdf:type Document
        graph.add((doc_uri, RDF.type, doc_class_uri))

        # Datatype fields (only set if predicate exists)
        def set_datatype_if_possible(field_name: str, predicate: Any | None, raw_value: Any) -> None:
            if predicate is None:
                if raw_value is not None and str(raw_value).strip():
                    report_rows.append(
                        {
                            "row_index": row_index,
                            "doc_id": doc_id,
                            "field_name": field_name,
                            "raw_value": raw_value,
                            "status": "skipped_no_predicate",
                            "mapped_uri_or_reason": "predicate missing in ontology",
                        }
                    )
                return

            if raw_value is None or (isinstance(raw_value, float) and raw_value != raw_value):
                return
            raw_value_str = str(raw_value).strip()
            if not raw_value_str:
                return

            # Update: remove previous values for clean overwrite
            graph.remove((doc_uri, predicate, None))
            graph.add((doc_uri, predicate, Literal(raw_value_str)))
            report_rows.append(
                {
                    "row_index": row_index,
                    "doc_id": doc_id,
                    "field_name": field_name,
                    "raw_value": raw_value_str,
                    "status": "set",
                    "mapped_uri_or_reason": str(doc_uri),
                }
            )

        # docId is used as node identifier; store as datatype only if predicate exists.
        set_datatype_if_possible("docId", p_doc_id, doc_id)
        set_datatype_if_possible("title", p_title, row.get("title"))
        set_datatype_if_possible("filePath", p_file_path, row.get("file_path"))
        set_datatype_if_possible("language", p_language, row.get("language"))
        set_datatype_if_possible("keywords", p_keywords, row.get("keywords"))

        # Object properties: map terms to ontology URIs
        def set_object_terms_if_possible(
            field_name: str,
            predicate: Any | None,
            raw_cell: Any,
            entity_type: str,
            manual_map: dict[str, str],
        ) -> None:
            terms = _split_multi_value(raw_cell)
            if not terms:
                return

            if predicate is None:
                for t in terms:
                    report_rows.append(
                        {
                            "row_index": row_index,
                            "doc_id": doc_id,
                            "field_name": field_name,
                            "raw_value": t,
                            "status": "skipped_no_predicate",
                            "mapped_uri_or_reason": "predicate missing in ontology",
                        }
                    )
                return

            mapped_uris: list[str] = []
            for t in terms:
                m = _map_value_to_uris(
                    term=t,
                    entity_type=entity_type,
                    kg_index=kg_index,
                    manual_alias_map=manual_map,
                )
                if m.mapped_uris:
                    mapped_uris.extend(m.mapped_uris)
                    report_rows.append(
                        {
                            "row_index": row_index,
                            "doc_id": doc_id,
                            "field_name": field_name,
                            "raw_value": t,
                            "status": m.status,
                            "mapped_uri_or_reason": ";".join(m.mapped_uris),
                        }
                    )
                else:
                    unmapped_counts[entity_type] += 1
                    report_rows.append(
                        {
                            "row_index": row_index,
                            "doc_id": doc_id,
                            "field_name": field_name,
                            "raw_value": t,
                            "status": m.status,
                            "mapped_uri_or_reason": m.reason,
                        }
                    )

            # Update: remove previous object assertions, then set mapped ones
            if mapped_uris:
                mapped_uris_uniq = []
                seen = set()
                for u in mapped_uris:
                    if u not in seen:
                        seen.add(u)
                        mapped_uris_uniq.append(u)
                graph.remove((doc_uri, predicate, None))
                for u in mapped_uris_uniq:
                    graph.add((doc_uri, predicate, URIRef(u)))

            else:
                # If no mapped URIs, don't overwrite existing triples.
                pass

        # NOTE: We do not crash on mapping issues; we only report.
        set_object_terms_if_possible(
            "aboutTaxon",
            p_about_taxon,
            row.get("related_taxon"),
            entity_type="species",
            manual_map=manual_maps["species"],
        )
        set_object_terms_if_possible(
            "aboutDisease",
            p_about_disease,
            row.get("related_disease"),
            entity_type="disease",
            manual_map=manual_maps["disease"],
        )
        set_object_terms_if_possible(
            "aboutLocation",
            p_about_location,
            row.get("related_location"),
            entity_type="location",
            manual_map=manual_maps["location"],
        )
        set_object_terms_if_possible(
            "documentProductionMode",
            p_doc_prod_mode,
            row.get("production_mode"),
            entity_type="mode",
            manual_map=manual_maps["mode"],
        )

    # Output ontology with backup if output exists
    output_owl_path.parent.mkdir(parents=True, exist_ok=True)
    if output_owl_path.exists():
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = output_owl_path.with_suffix(output_owl_path.suffix + f".bak_{ts}")
        shutil.copy2(str(output_owl_path), str(backup_path))
        print(f"[INFO] Backup created: {backup_path}")

    graph.serialize(destination=str(output_owl_path), format="xml")

    # Write report CSV
    report_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(report_rows).to_csv(report_path, index=False, encoding="utf-8-sig")

    # Summary
    print("[DONE] sync_metadata_to_owl")
    print(f"created_count: {created_count}")
    print(f"updated_count: {updated_count}")
    print(f"skipped_count: {skipped_count}")
    print("unmapped_counts_by_type:")
    for k, v in unmapped_counts.items():
        print(f"  - {k}: {v}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sync document metadata into OWL ontology.")
    parser.add_argument("--metadata_path", type=str, default=str(DEFAULT_METADATA_PATH))
    parser.add_argument("--owl_path", type=str, default=str(DEFAULT_OWL_PATH))
    parser.add_argument("--output_owl_path", type=str, default=str(DEFAULT_OUTPUT_OWL_PATH))
    parser.add_argument("--report_path", type=str, default=str(DEFAULT_REPORT_PATH))
    args = parser.parse_args()

    sync_metadata_to_owl(
        metadata_path=Path(args.metadata_path),
        owl_path=Path(args.owl_path),
        output_owl_path=Path(args.output_owl_path),
        report_path=Path(args.report_path),
    )

