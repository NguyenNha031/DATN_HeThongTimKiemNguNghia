from __future__ import annotations

import json
from pathlib import Path
from typing import Any


OUT = Path("outputs") / "full_corpus_pipeline_summary.json"


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _mtime(path: Path) -> str | None:
    if not path.exists():
        return None
    return path.stat().st_mtime_ns.__str__()


def main() -> None:
    audit = _load_json(Path("outputs") / "full_corpus_metadata_audit.json")
    cleanup = _load_json(Path("outputs") / "full_corpus_metadata_cleanup_effect_summary.json")
    kg_verify = _load_json(Path("outputs") / "kg_runtime_verification.json")
    query_verify = _load_json(Path("outputs") / "full_corpus_query_verification.json")

    summary = {
        "metadata_path_expected": "data/metadata/document_metadata_cleaned.xlsx",
        "ontology_runtime_expected_preference": [
            "data/ontology/taxon_enriched_facts_v2.owl",
            "data/ontology/taxon_enriched_facts.owl",
            "data/ontology/taxon_enriched_aliases.owl",
            "data/ontology/taxon_enriched.owl",
            "data/ontology/taxon.owl",
        ],
        "audit": audit,
        "cleanup_effect": cleanup,
        "kg_runtime_verification": {
            "ontology_file_loaded": (kg_verify or {}).get("ontology_file_loaded"),
            "total_document_nodes_in_kg": (kg_verify or {}).get("total_document_nodes_in_kg"),
            "total_metadata_docs": (kg_verify or {}).get("total_metadata_docs"),
            "mapped_doc_count": (kg_verify or {}).get("mapped_doc_count"),
            "unmapped_doc_count": (kg_verify or {}).get("unmapped_doc_count"),
            "mapping_report_summary": (kg_verify or {}).get("mapping_report_summary"),
        }
        if kg_verify
        else None,
        "query_verification_file": str(Path("outputs") / "full_corpus_query_verification.json"),
        "file_timestamps": {
            "metadata_cleaned_xlsx": _mtime(Path("data") / "metadata" / "document_metadata_cleaned.xlsx"),
            "vector_chunks_index": _mtime(Path("vector_store") / "chunks.index"),
            "vector_chunks_meta": _mtime(Path("vector_store") / "chunks_meta.pkl"),
            "vector_config": _mtime(Path("vector_store") / "config.pkl"),
            "taxon_enriched_owl": _mtime(Path("data") / "ontology" / "taxon_enriched.owl"),
            "mapping_report_csv": _mtime(Path("data") / "ontology" / "mapping_report.csv"),
            "kg_runtime_verification_json": _mtime(Path("outputs") / "kg_runtime_verification.json"),
            "hybrid_comparison_csv": _mtime(Path("hybrid_comparison.csv")),
            "hybrid_results_txt": _mtime(Path("hybrid_results.txt")),
        },
        "notes": [
            "Vector index rebuild is required whenever new PDFs are added; this run rebuilt vector_store using cleaned metadata.",
            "KG runtime mapping coverage depends on Document nodes present in the currently loaded ontology file (often taxon_enriched_facts_v2.owl).",
            "Unmapped counts in mapping_report reflect metadata-to-ontology entity mapping gaps (alias/coverage), not vector indexing.",
        ],
        "query_verification_overview": {
            "metadata_path_used": (query_verify or {}).get("metadata_path_used"),
            "ontology_loaded": (query_verify or {}).get("ontology_loaded"),
            "query_count": len((query_verify or {}).get("queries") or []),
        }
        if query_verify
        else None,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[SUMMARY] Saved: {OUT}")


if __name__ == "__main__":
    main()

