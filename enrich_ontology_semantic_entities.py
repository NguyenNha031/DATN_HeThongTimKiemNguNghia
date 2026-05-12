from __future__ import annotations

import json
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from rdflib import Literal, URIRef
from rdflib.namespace import RDF, OWL, RDFS, SKOS

import kg_runtime
import semantic_normalization as sn


INPUT_OWL_PATH = Path("data") / "ontology" / "taxon_enriched_aliases.owl"
_DEFAULT_METADATA_XLSX_PATH = Path("data") / "metadata" / "document_metadata.xlsx"
_CLEAN_METADATA_XLSX_PATH = Path("data") / "metadata" / "document_metadata_cleaned.xlsx"
METADATA_XLSX_PATH = _CLEAN_METADATA_XLSX_PATH if _CLEAN_METADATA_XLSX_PATH.exists() else _DEFAULT_METADATA_XLSX_PATH

OUTPUT_OWL_PATH = Path("data") / "ontology" / "taxon_enriched_semantic.owl"

OUTPUT_REPORT_JSON = Path("outputs") / "metadata_normalization_report.json"
OUTPUT_REPORT_CSV = Path("outputs") / "metadata_normalization_report.csv"


CORE_FIELDS = [
    ("related_taxon", "aboutTaxon", "species"),
    ("related_disease", "aboutDisease", "disease"),
    ("related_location", "aboutLocation", "location"),
    ("production_mode", "documentProductionMode", "mode"),
]


def _reconfigure_stdout_utf8() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stdin.reconfigure(encoding="utf-8")
    except Exception:
        pass


def _split_multi_value(v: Any) -> list[str]:
    if v is None:
        return []
    try:
        if isinstance(v, float) and v != v:
            return []
    except Exception:
        pass
    s = str(v).strip()
    if not s:
        return []
    return [x.strip() for x in s.split(";") if x.strip()]


def _find_class_uri_by_localname(graph, local_name: str) -> URIRef | None:
    for c in graph.subjects(RDF.type, OWL.Class):
        if str(c).endswith("#" + local_name) or str(c).endswith("/" + local_name):
            return c  # type: ignore[return-value]
    return None


def enrich_semantic_entities(
    input_owl_path: Path = INPUT_OWL_PATH,
    metadata_xlsx_path: Path = METADATA_XLSX_PATH,
    output_owl_path: Path = OUTPUT_OWL_PATH,
) -> None:
    _reconfigure_stdout_utf8()

    graph = kg_runtime.load_kg(input_owl_path)
    kg_index = kg_runtime.build_kg_index(graph)

    # Class URIs we may need for ADD_NEW_ENTITY decisions.
    class_cache: dict[str, URIRef] = {}
    for cls_name in ["Taxon", "Fish", "Shrimp", "Crustacean", "ProductionMode"]:
        cu = _find_class_uri_by_localname(graph, cls_name)
        if cu is not None:
            class_cache[cls_name] = cu

    df = __import__("pandas").read_excel(metadata_xlsx_path)

    decisions: list[dict[str, Any]] = []
    to_create: dict[str, sn.NormalizationDecision] = {}

    for _, row in df.iterrows():
        doc_id = str(row.get("doc_id", "")).strip()
        for col, prop, expected_type in CORE_FIELDS:
            for tok in _split_multi_value(row.get(col, "")):
                d = sn.decide_token_action(
                    token=tok,
                    source_field=col,
                    candidate_property=prop,
                    kg_index=kg_index,
                    expected_entity_type=expected_type,
                )
                decisions.append(
                    {
                        "doc_id": doc_id,
                        "token": d.token,
                        "source_field": d.source_field,
                        "candidate_property": d.candidate_property,
                        "normalized_label": d.normalized_label,
                        "candidate_class": d.candidate_class,
                        "candidate_property_suggested": d.candidate_property_suggested,
                        "target_uri": d.target_uri,
                        "decision": d.decision,
                        "reason": d.reason,
                        "confidence": d.confidence,
                    }
                )
                if d.decision == "ADD_NEW_ENTITY" and d.confidence == "high" and d.target_uri:
                    to_create[d.target_uri] = d

    created = []
    for uri_str, d in sorted(to_create.items(), key=lambda x: x[0]):
        cls_name = d.candidate_class
        if not cls_name:
            continue
        if cls_name not in class_cache:
            # If class doesn't exist, do not create entity.
            continue
        u = URIRef(uri_str)
        if any(True for _ in graph.triples((u, None, None))):
            continue

        graph.add((u, RDF.type, OWL.NamedIndividual))
        graph.add((u, RDF.type, class_cache[cls_name]))

        # Add a conservative label set: prefLabel = titlecased, altLabel = raw token.
        # We do NOT overwrite existing labels.
        label = d.normalized_label.replace("_", " ")
        graph.add((u, SKOS.prefLabel, Literal(label)))
        graph.add((u, SKOS.altLabel, Literal(d.token)))
        created.append({"uri": uri_str, "class": cls_name, "labels": [label, d.token], "reason": d.reason})

    # Backup if output exists
    if output_owl_path.exists():
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = output_owl_path.with_suffix(output_owl_path.suffix + f".bak_{ts}")
        shutil.copy2(str(output_owl_path), str(backup))
        print(f"[SEMANTIC-ENRICH] Backup created: {backup}")

    graph.serialize(destination=str(output_owl_path), format="xml")

    OUTPUT_REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_JSON.write_text(
        json.dumps(
            {
                "input_owl": str(INPUT_OWL_PATH),
                "output_owl": str(output_owl_path),
                "created_entity_count": len(created),
                "created_entities": created,
                "decision_rows": len(decisions),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    # CSV decisions (flat, for filtering)
    import pandas as pd

    pd.DataFrame(decisions).to_csv(OUTPUT_REPORT_CSV, index=False, encoding="utf-8-sig")

    print("[SEMANTIC-ENRICH] Done.")
    print(f"  - created_entity_count: {len(created)}")
    print(f"  - output_owl: {output_owl_path}")
    print(f"  - report_json: {OUTPUT_REPORT_JSON}")
    print(f"  - report_csv: {OUTPUT_REPORT_CSV}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Enrich ontology with safe generic semantic entities.")
    parser.add_argument("--input_owl_path", type=str, default=str(INPUT_OWL_PATH))
    parser.add_argument("--metadata_xlsx_path", type=str, default=str(METADATA_XLSX_PATH))
    parser.add_argument("--output_owl_path", type=str, default=str(OUTPUT_OWL_PATH))
    args = parser.parse_args()

    enrich_semantic_entities(
        input_owl_path=Path(args.input_owl_path),
        metadata_xlsx_path=Path(args.metadata_xlsx_path),
        output_owl_path=Path(args.output_owl_path),
    )

