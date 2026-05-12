from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pandas as pd
from rdflib import RDF, OWL

import kg_runtime
import hybrid_search
from vector_search import load_index


OUTPUT_JSON_PATH = Path("outputs") / "kg_runtime_verification.json"


def _local_name(uri: Any) -> str:
    s = str(uri)
    if "#" in s:
        return s.rsplit("#", 1)[-1]
    if "/" in s:
        return s.rsplit("/", 1)[-1]
    return s


def _find_document_class_uri(graph) -> Any | None:
    for c in graph.subjects(RDF.type, OWL.Class):
        if _local_name(c) == "Document":
            return c
    return None


def _summarize_mapping_report(mapping_report_path: Path) -> dict[str, int]:
    # Cột mapping_report.csv:
    # row_index,doc_id,field_name,raw_value,status,mapped_uri_or_reason
    if not mapping_report_path.exists():
        return {
            "disease_unmapped": 0,
            "species_unmapped": 0,
            "location_unmapped": 0,
            "mode_unmapped": 0,
        }

    df = pd.read_csv(mapping_report_path)
    unmapped = df[df["status"].astype(str).str.contains("unmapped", na=False)]
    # Giá trị field_name trong sync_metadata_to_owl.py:
    # aboutDisease, aboutTaxon, aboutLocation, documentProductionMode
    return {
        "disease_unmapped": int((unmapped["field_name"] == "aboutDisease").sum()),
        "species_unmapped": int((unmapped["field_name"] == "aboutTaxon").sum()),
        "location_unmapped": int((unmapped["field_name"] == "aboutLocation").sum()),
        "mode_unmapped": int((unmapped["field_name"] == "documentProductionMode").sum()),
    }


def verify_runtime() -> None:
    # Tránh in tiếng Việt làm lỗi mã hóa mặc định trên Windows.
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stdin.reconfigure(encoding="utf-8")
    except Exception:
        pass

    # 1) Nạp chỉ mục vector
    print("[VERIFY] Loading vector index...")
    model, index, records = load_index()

    # 2) Nạp metadata
    print("[VERIFY] Loading metadata...")
    df = hybrid_search.load_full_metadata(hybrid_search.METADATA_PATH)
    metadata_lookup = hybrid_search.build_metadata_lookup(df)
    term_index = hybrid_search.build_term_index(df)

    # 3) Nạp ontology KG (cùng thứ tự ưu tiên như lúc chạy)
    print("[VERIFY] Loading ontology with KG priority selection...")
    graph, loaded_owl_path, used_source = kg_runtime.load_kg_prefer_facts_then_alias_enriched(
        hybrid_search.KG_FACT_ENRICHED_PATH,
        hybrid_search.KG_ALIAS_ENRICHED_PATH,
        hybrid_search.KG_ENRICHED_PATH,
        hybrid_search.KG_FALLBACK_PATH,
    )
    kg_index = kg_runtime.build_kg_index(graph)

    total_metadata_docs = len(df)

    # Tổng nút tài liệu trong ontology: đếm entity_type == document.
    total_document_nodes_in_kg = sum(
        1 for _, info in (kg_index.get("uri_to_info") or {}).items() if info.get("entity_type") == "document"
    )

    # Ánh xạ doc_id metadata -> URI tài liệu KG (dockey_to_uri, tốt nhất có thể)
    dockey_to_uri = kg_index.get("dockey_to_uri") or {}
    mapped_doc_count = 0
    unmapped_doc_count = 0
    for doc_id in df["doc_id"].tolist():
        k = kg_runtime.normalize_kg_text(doc_id)
        if k and k in dockey_to_uri:
            mapped_doc_count += 1
        else:
            unmapped_doc_count += 1

    print("[VERIFY] Ontology loaded summary:")
    print(f"  - ontology file loaded: {loaded_owl_path} (used_source={used_source})")
    print(f"  - total document nodes in ontology (entity_type=document): {total_document_nodes_in_kg}")
    print(f"  - total metadata rows: {total_metadata_docs}")
    print(f"  - mapped metadata docs to KG document URIs: {mapped_doc_count}")
    print(f"  - unmapped metadata docs: {unmapped_doc_count}")

    mapping_report_path = Path("data") / "ontology" / "mapping_report.csv"
    mapping_report_summary = _summarize_mapping_report(mapping_report_path)
    print("[VERIFY] mapping_report summary (unmapped counts):")
    print(f"  - disease: {mapping_report_summary['disease_unmapped']}")
    print(f"  - species: {mapping_report_summary['species_unmapped']}")
    print(f"  - location: {mapping_report_summary['location_unmapped']}")
    print(f"  - mode: {mapping_report_summary['mode_unmapped']}")

    test_queries = [
        "bệnh AHPND trên tôm",
        "nuôi tôm hùm ở Khánh Hòa",
        "tài liệu về trại giống tôm sú ở Ấn Độ",
        "biosecurity trong hatchery tôm thẻ chân trắng",
    ]

    per_query_details: list[dict[str, Any]] = []
    global_top5_docs_mapped_to_kg = 0
    global_top5_docs_with_nonzero_kg_score = 0
    global_top5_docs_with_kg_explanation = 0

    any_query_all_zero_kg = False

    for q in test_queries:
        print("\n" + "=" * 100)
        print(f"[VERIFY] Query: {q}")

        detected = hybrid_search.detect_entities(q, term_index)
        kg_entities = kg_runtime.link_query_entities_kg(q, kg_index)

        # Khối xác minh hiển thị cho người đọc.
        print("  - detected metadata entities:")
        print(f"    * disease: {[m.get('canonical') for m in detected.get('disease', [])]}")
        print(f"    * prevention: {[m.get('canonical') for m in detected.get('prevention', [])]}")
        print(f"    * management: {[m.get('canonical') for m in detected.get('management', [])]}")
        print(f"    * topic: {[m.get('canonical') for m in detected.get('topic', [])]}")
        print(f"    * species: {[m.get('canonical') for m in detected.get('species', [])]}")
        print(f"    * location: {[m.get('canonical') for m in detected.get('location', [])]}")
        print(f"    * mode: {[m.get('canonical') for m in detected.get('mode', [])]}")
        print("  - detected KG-linked entities (ontology aliases):")
        print(
            f"    * disease: {[e.get('label') for e in (kg_entities.get('disease') or [])]}"
        )
        print(
            f"    * prevention: {[e.get('label') for e in (kg_entities.get('prevention') or [])]}"
        )
        print(
            f"    * species: {[e.get('label') for e in (kg_entities.get('species') or [])]}"
        )
        print(
            f"    * location: {[e.get('label') for e in (kg_entities.get('location') or [])]}"
        )
        print(
            f"    * mode: {[e.get('label') for e in (kg_entities.get('mode') or [])]}"
        )

        # Chạy hybrid đầy đủ để lấy top ứng viên và chi tiết chấm điểm.
        _, top_results = hybrid_search.hybrid_search(
            query=q,
            model=model,
            index=index,
            records=records,
            metadata_lookup=metadata_lookup,
            term_index=term_index,
        )

        # In top 5 ứng viên.
        rows = []
        nonzero_kg_docs = 0
        mapped_docs = 0
        docs_with_kg_expl = 0

        for i, r in enumerate(top_results[:5], start=1):
            doc_uri_in_kg = r.get("doc_uri_in_kg", None)
            kg_score = float(r.get("kg_score", 0.0) or 0.0)
            kg_expl = r.get("kg_explanation", "") or ""
            if doc_uri_in_kg:
                mapped_docs += 1
            if kg_score > 0:
                nonzero_kg_docs += 1
            if kg_expl.strip():
                docs_with_kg_expl += 1

            if kg_score > 0 and kg_expl.strip():
                kg_expl_for_print = kg_expl
            else:
                kg_expl_for_print = kg_expl if kg_expl else ""

            print(f"  - Top{i} doc_id={r.get('doc_id')} doc_uri_in_kg={doc_uri_in_kg} "
                  f"vector_score={r.get('vector_score')} metadata_delta={r.get('metadata_delta')} "
                  f"kg_score={kg_score} final_score={r.get('final_score')}")
            print(f"    explanation: {r.get('explanation','')}")
            if kg_expl_for_print:
                print(f"    kg_explanation: {kg_expl_for_print}")

            rows.append(
                {
                    "rank": i,
                    "doc_id": r.get("doc_id"),
                    "doc_uri_in_kg": doc_uri_in_kg,
                    "vector_score": r.get("vector_score"),
                    "metadata_delta": r.get("metadata_delta"),
                    "kg_score": kg_score,
                    "final_score": r.get("final_score"),
                    "explanation": r.get("explanation", ""),
                    "kg_explanation": kg_expl_for_print,
                }
            )

        global_top5_docs_mapped_to_kg += mapped_docs
        global_top5_docs_with_nonzero_kg_score += nonzero_kg_docs
        global_top5_docs_with_kg_explanation += docs_with_kg_expl

        if nonzero_kg_docs == 0:
            any_query_all_zero_kg = True
            print(f"  [VERIFY] KG contribution is ZERO for all top 5 results for this query.")

        per_query_details.append(
            {
                "query": q,
                "detected_metadata_entities": detected,
                "detected_kg_linked_entities": kg_entities,
                "top5_results": rows,
                "top5_docs_mapped_to_kg": mapped_docs,
                "top5_docs_with_nonzero_kg_score": nonzero_kg_docs,
                "top5_docs_with_kg_explanation": docs_with_kg_expl,
            }
        )

    # Tổng hợp kiểm tra
    print("\n" + "=" * 100)
    print("[VERIFY] Acceptance checklist outputs:")
    print(f"  - ontology file loaded: {loaded_owl_path}")
    print(f"  - total metadata docs: {total_metadata_docs}")
    print(f"  - mapped metadata docs to KG: {mapped_doc_count}")

    # Điều kiện: mapped_doc_count khác 0
    print(f"  - mapped_doc_count_nonzero={mapped_doc_count > 0}")

    any_successful = any(
        (
            d.get("top5_docs_mapped_to_kg", 0) > 0
            and d.get("top5_docs_with_nonzero_kg_score", 0) > 0
            and d.get("top5_docs_with_kg_explanation", 0) > 0
        )
        for d in per_query_details
    )
    print(f"  - at least one query has mapped docs AND kg_score>0 AND kg_explanation!=empty: {any_successful}")
    print(f"  - any query has zero kg contribution for all top-5: {any_query_all_zero_kg}")

    # Báo cáo dạng máy đọc được
    OUTPUT_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "ontology_file_loaded": loaded_owl_path,
        "total_document_nodes_in_kg": total_document_nodes_in_kg,
        "total_metadata_docs": total_metadata_docs,
        "mapped_doc_count": mapped_doc_count,
        "unmapped_doc_count": unmapped_doc_count,
        "mapping_report_summary": mapping_report_summary,
        "aggregate": {
            "global_top5_docs_mapped_to_kg": global_top5_docs_mapped_to_kg,
            "global_top5_docs_with_nonzero_kg_score": global_top5_docs_with_nonzero_kg_score,
            "global_top5_docs_with_kg_explanation": global_top5_docs_with_kg_explanation,
            "any_query_all_zero_kg": any_query_all_zero_kg,
        },
        "per_query_verification_details": per_query_details,
    }
    OUTPUT_JSON_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[VERIFY] JSON report saved: {OUTPUT_JSON_PATH}")


if __name__ == "__main__":
    verify_runtime()

