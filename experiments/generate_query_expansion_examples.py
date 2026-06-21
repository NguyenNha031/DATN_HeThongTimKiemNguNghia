from __future__ import annotations

import csv
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import hybrid_search
import kg_runtime


CORE_QUERIES = PROJECT_ROOT / "data" / "eval" / "final_query_set_core.csv"
EXT_QUERIES = PROJECT_ROOT / "data" / "eval" / "final_query_set_extended.csv"
METADATA = PROJECT_ROOT / "data" / "metadata" / "document_metadata_cleaned.xlsx"
ONTOLOGY = PROJECT_ROOT / "data" / "ontology" / "taxon_enriched_facts_v2.owl"
QUERY_PROFILES = PROJECT_ROOT / "outputs" / "query_understanding_profiles.csv"
KG_VERIFICATION = PROJECT_ROOT / "outputs" / "kg_runtime_verification.json"
FACT_COVERAGE = PROJECT_ROOT / "outputs" / "document_fact_coverage_audit.json"

EXAMPLES_OUT = PROJECT_ROOT / "outputs" / "query_expansion_examples.csv"
DESIGN_OUT = PROJECT_ROOT / "outputs" / "query_expansion_design.md"
FIGURE_OUT = PROJECT_ROOT / "outputs" / "figures" / "fig_query_expansion_examples.png"

FIELDS = [
    "query_id",
    "original_query",
    "query_group",
    "detected_entity",
    "entity_type",
    "expansion_type",
    "expansion_terms",
    "expansion_source",
    "expanded_query_example",
    "expected_effect",
    "risk_or_caution",
    "should_use_in_final",
    "notes",
]


SAFE_MANUAL_EXAMPLES: list[dict[str, str]] = [
    {
        "query_id": "QE_DISEASE_AHPND_ALIAS",
        "original_query": "AHPND shrimp disease",
        "query_group": "disease-specific",
        "detected_entity": "AHPND",
        "entity_type": "disease",
        "expansion_type": "disease_alias",
        "expansion_terms": "acute hepatopancreatic necrosis disease; EMS; AHPNS",
        "expansion_source": "metadata related_disease; skos:altLabel; fallback_metadata_alias",
        "expected_effect": "Improve matching when documents use full disease name or EMS/AHPNS wording instead of AHPND.",
        "risk_or_caution": "EMS/AHPNS can be broader than AHPND in some sources; keep disease intent anchored.",
        "should_use_in_final": "false",
    },
    {
        "query_id": "QE_DISEASE_AHPND_PATHOGEN",
        "original_query": "AHPND shrimp disease",
        "query_group": "disease-specific",
        "detected_entity": "AHPND",
        "entity_type": "disease",
        "expansion_type": "disease_to_pathogen",
        "expansion_terms": "Vibrio parahaemolyticus; Vibrio; bacterial pathogen",
        "expansion_source": "ontology relation causedBy; metadata keywords",
        "expected_effect": "Bridge disease queries to pathogen-focused documents.",
        "risk_or_caution": "Vibrio is broad; use with lower weight or only as candidate expansion.",
        "should_use_in_final": "false",
    },
    {
        "query_id": "QE_DISEASE_AHPND_PREVENTION",
        "original_query": "AHPND shrimp disease prevention",
        "query_group": "biosecurity-management",
        "detected_entity": "AHPND",
        "entity_type": "disease",
        "expansion_type": "disease_to_prevention",
        "expansion_terms": "biosecurity; disease prevention; disease control; surveillance",
        "expansion_source": "ontology relation recommendedPrevention; metadata keywords",
        "expected_effect": "Retrieve management/prevention manuals for AHPND-oriented queries.",
        "risk_or_caution": "Can drift toward generic biosecurity; retain AHPND term in rewritten query.",
        "should_use_in_final": "false",
    },
    {
        "query_id": "QE_DISEASE_WSSV_ALIAS",
        "original_query": "WSSV shrimp",
        "query_group": "disease-specific",
        "detected_entity": "WSSV",
        "entity_type": "disease",
        "expansion_type": "disease_alias",
        "expansion_terms": "white spot syndrome virus; white spot disease; bệnh đốm trắng",
        "expansion_source": "metadata related_disease; fallback_metadata_alias",
        "expected_effect": "Improve recall for Vietnamese and English WSSV variants.",
        "risk_or_caution": "White spot disease can appear as disease or virus wording; use as synonym only.",
        "should_use_in_final": "false",
    },
    {
        "query_id": "QE_DISEASE_WSSV_PREVENTION",
        "original_query": "bệnh đốm trắng ở tôm nuôi",
        "query_group": "local",
        "detected_entity": "WSSV",
        "entity_type": "disease",
        "expansion_type": "disease_to_prevention",
        "expansion_terms": "PCR; LAMP-PCR; biofloc; chế phẩm sinh học; biosecurity",
        "expansion_source": "metadata keywords; manual_safe_rule_from_existing_facts",
        "expected_effect": "Connect WSSV query to prevention/diagnostic documents.",
        "risk_or_caution": "Diagnostic and prevention terms should not dominate disease intent.",
        "should_use_in_final": "false",
    },
    {
        "query_id": "QE_DISEASE_IMNV_ALIAS",
        "original_query": "infectious myonecrosis",
        "query_group": "disease-specific",
        "detected_entity": "IMNV",
        "entity_type": "disease",
        "expansion_type": "disease_alias",
        "expansion_terms": "infectious myonecrosis virus; IMN; hoại tử cơ truyền nhiễm",
        "expansion_source": "metadata related_disease; fallback_metadata_alias",
        "expected_effect": "Improve cross-language matching for IMNV/IMN queries.",
        "risk_or_caution": "IMN can refer to disease while IMNV is virus; keep both but low-risk alias.",
        "should_use_in_final": "false",
    },
    {
        "query_id": "QE_DISEASE_EHP_ALIAS",
        "original_query": "EHP trên tôm",
        "query_group": "disease-specific",
        "detected_entity": "EHP",
        "entity_type": "disease",
        "expansion_type": "disease_alias",
        "expansion_terms": "Enterocytozoon hepatopenaei; hepatopancreatic microsporidiosis; HPM; vi bào tử trùng gan tụy",
        "expansion_source": "metadata related_disease; fallback_metadata_alias",
        "expected_effect": "Recover EHP documents using scientific pathogen/disease names.",
        "risk_or_caution": "Long scientific aliases may add lexical noise; use as candidate expansion.",
        "should_use_in_final": "false",
    },
    {
        "query_id": "QE_DISEASE_VIBRIOSIS_PATHOGEN",
        "original_query": "vibriosis shrimp hatchery",
        "query_group": "hatchery-production-mode",
        "detected_entity": "vibriosis",
        "entity_type": "disease",
        "expansion_type": "disease_to_pathogen",
        "expansion_terms": "Vibrio parahaemolyticus; Vibrio harveyi; Vibrio campbellii; Vibrio alginolyticus",
        "expansion_source": "metadata related_disease; metadata keywords; ontology relation causedBy",
        "expected_effect": "Bridge disease query to pathogen-specific hatchery studies.",
        "risk_or_caution": "Vibrio species are broad; should be weighted by hatchery/disease context.",
        "should_use_in_final": "false",
    },
    {
        "query_id": "QE_TAXON_VANNAMEI_ALIAS",
        "original_query": "whiteleg shrimp hatchery",
        "query_group": "hatchery-production-mode",
        "detected_entity": "whiteleg shrimp",
        "entity_type": "taxon",
        "expansion_type": "taxon_scientific_name",
        "expansion_terms": "Penaeus vannamei; Litopenaeus vannamei; tôm thẻ chân trắng; Pacific whiteleg shrimp",
        "expansion_source": "skos:altLabel; metadata related_taxon; fallback_metadata_alias",
        "expected_effect": "Improve matching between common names and scientific/Vietnamese names.",
        "risk_or_caution": "Penaeus/Litopenaeus naming variants should be treated as aliases, not separate species.",
        "should_use_in_final": "false",
    },
    {
        "query_id": "QE_TAXON_MONODON_ALIAS",
        "original_query": "black tiger shrimp hatchery India",
        "query_group": "species-location",
        "detected_entity": "black tiger shrimp",
        "entity_type": "taxon",
        "expansion_type": "taxon_scientific_name",
        "expansion_terms": "Penaeus monodon; tôm sú; tiger shrimp",
        "expansion_source": "metadata related_taxon; fallback_metadata_alias",
        "expected_effect": "Connect black tiger shrimp wording with Penaeus monodon hatchery manuals.",
        "risk_or_caution": "Generic shrimp docs may be over-retrieved; keep India/hatchery constraints.",
        "should_use_in_final": "false",
    },
    {
        "query_id": "QE_TAXON_LOBSTER_ALIAS",
        "original_query": "lobster Khanh Hoa",
        "query_group": "local",
        "detected_entity": "lobster",
        "entity_type": "taxon",
        "expansion_type": "taxon_alias",
        "expansion_terms": "tôm hùm; spiny lobster; Panulirus ornatus; tôm hùm xanh",
        "expansion_source": "metadata related_taxon; skos:altLabel; fallback_metadata_alias",
        "expected_effect": "Improve matching for Vietnamese local lobster planning/monitoring documents.",
        "risk_or_caution": "Lobster market/capture documents may enter; preserve local aquaculture intent.",
        "should_use_in_final": "false",
    },
    {
        "query_id": "QE_TAXON_SHRIMP_COMMON",
        "original_query": "shrimp disease prevention",
        "query_group": "biosecurity-management",
        "detected_entity": "shrimp",
        "entity_type": "taxon",
        "expansion_type": "taxon_common_name",
        "expansion_terms": "tôm; prawns and shrimps; crustaceans; Penaeus",
        "expansion_source": "metadata related_taxon; metadata keywords",
        "expected_effect": "Recover documents using broad crustacean/shrimp terminology.",
        "risk_or_caution": "Broad taxon expansion can reduce precision; use only for candidate generation.",
        "should_use_in_final": "false",
    },
    {
        "query_id": "QE_LOCATION_KHANHHOA_ALIAS",
        "original_query": "nuôi tôm hùm Khánh Hòa",
        "query_group": "local",
        "detected_entity": "Khánh Hòa",
        "entity_type": "location",
        "expansion_type": "location_alias",
        "expansion_terms": "Khanh Hoa; Vịnh Cam Ranh; Cam Ranh; Vạn Ninh; Vịnh Văn Phong",
        "expansion_source": "metadata related_location; fallback_metadata_alias",
        "expected_effect": "Retrieve documents naming bays/districts rather than only province name.",
        "risk_or_caution": "Do not over-expand to all Vietnam if query is local and narrow.",
        "should_use_in_final": "false",
    },
    {
        "query_id": "QE_LOCATION_KHANHHOA_PARENT",
        "original_query": "lobster Khanh Hoa",
        "query_group": "local",
        "detected_entity": "Khánh Hòa",
        "entity_type": "location",
        "expansion_type": "location_parent",
        "expansion_terms": "Việt Nam; Nam Trung Bộ; coastal Vietnam",
        "expansion_source": "metadata related_location; manual_safe_rule_from_existing_facts",
        "expected_effect": "Allow broader coastal Vietnam documents to seed candidates when local docs are sparse.",
        "risk_or_caution": "Parent location is broad; should be lower weight than exact location.",
        "should_use_in_final": "false",
    },
    {
        "query_id": "QE_LOCATION_MEKONG_ALIAS",
        "original_query": "Mekong Delta shrimp farming",
        "query_group": "local",
        "detected_entity": "Mekong Delta",
        "entity_type": "location",
        "expansion_type": "location_alias",
        "expansion_terms": "ĐBSCL; Đồng bằng sông Cửu Long; Vietnamese Mekong Delta",
        "expansion_source": "metadata related_location; fallback_metadata_alias",
        "expected_effect": "Improve matching for Vietnamese reports using ĐBSCL abbreviation.",
        "risk_or_caution": "Avoid expanding to all Vietnam unless candidate recall is too low.",
        "should_use_in_final": "false",
    },
    {
        "query_id": "QE_LOCATION_THAILAND_ALIAS",
        "original_query": "shrimp farming Thailand",
        "query_group": "species-location",
        "detected_entity": "Thailand",
        "entity_type": "location",
        "expansion_type": "location_alias",
        "expansion_terms": "Bangkok; Thailand; Thai shrimp farming",
        "expansion_source": "metadata related_location",
        "expected_effect": "Recover FAO/technical seminar documents using Bangkok/Thailand context.",
        "risk_or_caution": "Bangkok may indicate seminar location rather than production location.",
        "should_use_in_final": "false",
    },
    {
        "query_id": "QE_LOCATION_PHILIPPINES_ALIAS",
        "original_query": "AHPND Philippines shrimp",
        "query_group": "local",
        "detected_entity": "Philippines",
        "entity_type": "location",
        "expansion_type": "location_alias",
        "expansion_terms": "Philippines; Southeast Asia; shrimp aquaculture Philippines",
        "expansion_source": "metadata related_location; manual_safe_rule_from_existing_facts",
        "expected_effect": "Support local disease surveillance queries where country is central.",
        "risk_or_caution": "Southeast Asia is broad; use lower weight.",
        "should_use_in_final": "false",
    },
    {
        "query_id": "QE_LOCATION_VIETNAM_ALIAS",
        "original_query": "shrimp farming Vietnam",
        "query_group": "local",
        "detected_entity": "Vietnam",
        "entity_type": "location",
        "expansion_type": "location_alias",
        "expansion_terms": "Việt Nam; Vietnam; ĐBSCL; Khánh Hòa; Nam Trung Bộ",
        "expansion_source": "metadata related_location",
        "expected_effect": "Map English/Vietnamese location names for local aquaculture documents.",
        "risk_or_caution": "Province/region expansion should depend on query context.",
        "should_use_in_final": "false",
    },
    {
        "query_id": "QE_MODE_HATCHERY_ALIAS",
        "original_query": "biosecurity shrimp hatchery",
        "query_group": "biosecurity-management",
        "detected_entity": "hatchery",
        "entity_type": "production_mode",
        "expansion_type": "production_mode_alias",
        "expansion_terms": "trại giống; shrimp hatchery; hatchery aquaculture; larval rearing; post-larvae",
        "expansion_source": "metadata production_mode; metadata keywords; fallback_metadata_alias",
        "expected_effect": "Improve retrieval for hatchery-specific biosecurity/health management documents.",
        "risk_or_caution": "Larval/post-larvae terms may over-focus on life stage.",
        "should_use_in_final": "false",
    },
    {
        "query_id": "QE_MODE_AQUACULTURE_ALIAS",
        "original_query": "aquaculture biosecurity guidelines",
        "query_group": "biosecurity-management",
        "detected_entity": "aquaculture",
        "entity_type": "production_mode",
        "expansion_type": "production_mode_alias",
        "expansion_terms": "nuôi trồng thủy sản; aquaculture; shrimp aquaculture; marine aquaculture",
        "expansion_source": "metadata production_mode; skos:altLabel",
        "expected_effect": "Bridge English and Vietnamese aquaculture mode wording.",
        "risk_or_caution": "Generic aquaculture expansion is broad; preserve topic constraints.",
        "should_use_in_final": "false",
    },
    {
        "query_id": "QE_MODE_GROWOUT_ALIAS",
        "original_query": "shrimp grow-out disease prevention",
        "query_group": "biosecurity-management",
        "detected_entity": "grow-out",
        "entity_type": "production_mode",
        "expansion_type": "production_mode_alias",
        "expansion_terms": "growout; grow-out aquaculture; pond culture; shrimp farming",
        "expansion_source": "metadata keywords; manual_safe_rule_from_existing_facts",
        "expected_effect": "Recover pond/grow-out documents even if they do not use the exact query term.",
        "risk_or_caution": "May mix hatchery and grow-out if production mode is not guarded.",
        "should_use_in_final": "false",
    },
    {
        "query_id": "QE_MODE_BROODSTOCK_ALIAS",
        "original_query": "broodstock post-larvae shrimp hatchery",
        "query_group": "hatchery-production-mode",
        "detected_entity": "broodstock",
        "entity_type": "production_mode",
        "expansion_type": "production_mode_alias",
        "expansion_terms": "broodstock; larvae; postlarvae; post-larvae; probiotics; hatchery tanks",
        "expansion_source": "metadata keywords; metadata production_mode",
        "expected_effect": "Connect life-stage hatchery queries to relevant microbiome/probiotics studies.",
        "risk_or_caution": "Life-stage terms should not replace species/disease constraints.",
        "should_use_in_final": "false",
    },
    {
        "query_id": "QE_TOPIC_BIOSECURITY_ALIAS",
        "original_query": "biosecurity shrimp hatchery",
        "query_group": "biosecurity-management",
        "detected_entity": "biosecurity",
        "entity_type": "topic",
        "expansion_type": "topic_alias",
        "expansion_terms": "an toàn sinh học; disease prevention; health management; disease control",
        "expansion_source": "metadata keywords; skos:altLabel; query_understanding_profiles",
        "expected_effect": "Improve cross-language matching for biosecurity/health management topics.",
        "risk_or_caution": "Can drift to generic management if species/mode are dropped.",
        "should_use_in_final": "false",
    },
    {
        "query_id": "QE_TOPIC_SURVEILLANCE_ALIAS",
        "original_query": "surveillance zoning aquatic animal diseases",
        "query_group": "biosecurity-management",
        "detected_entity": "surveillance",
        "entity_type": "topic",
        "expansion_type": "topic_alias",
        "expansion_terms": "disease surveillance; zoning; risk assessment; animal health",
        "expansion_source": "metadata keywords; query_understanding_profiles",
        "expected_effect": "Strengthen matching to surveillance/zoning manuals.",
        "risk_or_caution": "Risk assessment is broader than surveillance; lower weight recommended.",
        "should_use_in_final": "false",
    },
    {
        "query_id": "QE_MIXED_AHPND_VANNAMEI",
        "original_query": "AHPND Penaeus vannamei hatchery",
        "query_group": "disease-specific",
        "detected_entity": "AHPND + Penaeus vannamei + hatchery",
        "entity_type": "disease",
        "expansion_type": "disease_to_pathogen",
        "expansion_terms": "acute hepatopancreatic necrosis disease; Vibrio parahaemolyticus; whiteleg shrimp; tôm thẻ chân trắng; hatchery aquaculture",
        "expansion_source": "ontology relation causedBy; metadata related_taxon; metadata production_mode",
        "expected_effect": "Expand disease, species and production mode together while keeping query intent specific.",
        "risk_or_caution": "Multi-axis expansion should be capped to avoid overlong vector query.",
        "should_use_in_final": "false",
    },
    {
        "query_id": "QE_MIXED_LOBSTER_KHANHHOA",
        "original_query": "lobster Khanh Hoa aquaculture",
        "query_group": "local",
        "detected_entity": "lobster + Khánh Hòa + aquaculture",
        "entity_type": "taxon",
        "expansion_type": "taxon_alias",
        "expansion_terms": "tôm hùm; spiny lobster; Panulirus ornatus; Vịnh Cam Ranh; Vạn Ninh; marine aquaculture",
        "expansion_source": "metadata related_taxon; metadata related_location; metadata production_mode",
        "expected_effect": "Improve local marine aquaculture candidate recall.",
        "risk_or_caution": "Must avoid capture-fisheries lobster market documents when query is aquaculture.",
        "should_use_in_final": "false",
    },
    {
        "query_id": "QE_MIXED_WSSV_MEKONG",
        "original_query": "WSSV Mekong Delta shrimp",
        "query_group": "local",
        "detected_entity": "WSSV + Mekong Delta + shrimp",
        "entity_type": "disease",
        "expansion_type": "disease_alias",
        "expansion_terms": "white spot syndrome virus; bệnh đốm trắng; ĐBSCL; Đồng bằng sông Cửu Long; tôm giống; tôm thương phẩm",
        "expansion_source": "metadata related_disease; metadata related_location; metadata related_taxon",
        "expected_effect": "Connect local Vietnamese surveillance reports with English disease abbreviations.",
        "risk_or_caution": "Local evidence should be ranked above generic WSSV manuals.",
        "should_use_in_final": "false",
    },
]


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in FIELDS})


def split_terms(value: Any) -> list[str]:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return []
    terms = []
    for term in str(value).replace("|", ";").split(";"):
        term = term.strip()
        if term and term.lower() not in {"nan", "none"}:
            terms.append(term)
    return terms


def load_kg_index() -> tuple[Any, dict[str, Any]]:
    hybrid_search._init_kg_if_needed()
    return hybrid_search._KG_GRAPH, hybrid_search._KG_INDEX or {}


def labels_for_uris(uris: list[str], kg_index: dict[str, Any]) -> list[str]:
    uri_to_info = kg_index.get("uri_to_info") or {}
    labels = []
    for uri in uris:
        info = uri_to_info.get(str(uri)) or {}
        label = info.get("label") or str(uri).rsplit("#", 1)[-1]
        aliases = info.get("aliases") or []
        for value in [label, *aliases[:4]]:
            if value and value not in labels:
                labels.append(str(value))
    return labels


def kg_rows_from_core_queries() -> list[dict[str, str]]:
    graph, kg_index = load_kg_index()
    if not graph or not kg_index:
        return []
    queries = pd.read_csv(CORE_QUERIES, encoding="utf-8-sig")
    rows = []
    for _, query in queries.iterrows():
        query_id = str(query["query_id"])
        query_text = str(query["query_text"])
        query_group = str(query["query_group"])
        linked = kg_runtime.link_query_entities_kg(query_text, kg_index)
        for bucket, entity_type in [
            ("disease", "disease"),
            ("species", "taxon"),
            ("location", "location"),
            ("mode", "production_mode"),
            ("prevention", "topic"),
        ]:
            for entity in linked.get(bucket) or []:
                uri = entity.get("uri")
                label = entity.get("label") or entity.get("matched_alias") or ""
                if not uri:
                    continue
                info = (kg_index.get("uri_to_info") or {}).get(str(uri), {})
                aliases = [x for x in info.get("aliases", []) if x and x != label]
                if aliases:
                    rows.append(
                        make_row(
                            query_id,
                            query_text,
                            query_group,
                            label,
                            entity_type,
                            f"{entity_type}_alias" if entity_type != "taxon" else "taxon_alias",
                            aliases[:6],
                            "skos:altLabel; skos:prefLabel",
                            "Alias expansion can improve entity linking and lexical/vector recall.",
                            "Alias-only expansion is low risk, but should still be capped.",
                        )
                    )
                neighbors = kg_runtime.get_entity_neighbors(graph, str(uri))
                relation_map = {
                    "causedBy": ("disease_to_pathogen", "pathogen", "ontology relation causedBy"),
                    "hasSymptom": ("disease_to_symptom", "symptom", "ontology relation hasSymptom"),
                    "recommendedPrevention": ("disease_to_prevention", "prevention", "ontology relation recommendedPrevention"),
                    "recommendedTreatment": ("disease_to_treatment", "treatment", "ontology relation recommendedTreatment"),
                    "isFoundIn": ("location_parent", "location", "ontology relation isFoundIn"),
                }
                for rel, (expansion_type, _target_type, source) in relation_map.items():
                    terms = labels_for_uris(neighbors.get(rel, [])[:8], kg_index)
                    if terms:
                        rows.append(
                            make_row(
                                query_id,
                                query_text,
                                query_group,
                                label,
                                entity_type,
                                expansion_type,
                                terms[:8],
                                source,
                                "Relation expansion can add KG-neighbor evidence to candidate generation.",
                                "Use lower weight than exact entity terms to avoid query drift.",
                            )
                        )
    return rows


def make_row(
    query_id: str,
    original_query: str,
    query_group: str,
    detected_entity: str,
    entity_type: str,
    expansion_type: str,
    terms: list[str] | str,
    source: str,
    expected_effect: str,
    risk: str,
    should_use: str = "false",
    notes: str = "Prototype/design example; not applied to final hybrid runtime.",
) -> dict[str, str]:
    if isinstance(terms, str):
        term_text = terms
    else:
        term_text = "; ".join(dict.fromkeys([str(term) for term in terms if str(term).strip()]))
    expanded = f"{original_query} {' '.join(term_text.split('; ')[:4])}".strip()
    return {
        "query_id": query_id,
        "original_query": original_query,
        "query_group": query_group,
        "detected_entity": detected_entity,
        "entity_type": entity_type,
        "expansion_type": expansion_type,
        "expansion_terms": term_text,
        "expansion_source": source,
        "expanded_query_example": expanded,
        "expected_effect": expected_effect,
        "risk_or_caution": risk,
        "should_use_in_final": should_use,
        "notes": notes,
    }


def metadata_examples() -> list[dict[str, str]]:
    metadata = pd.read_excel(METADATA).fillna("")
    rows = []
    disease_counts = Counter()
    taxon_counts = Counter()
    location_counts = Counter()
    mode_counts = Counter()
    for _, row in metadata.iterrows():
        disease_counts.update(split_terms(row.get("related_disease", "")))
        taxon_counts.update(split_terms(row.get("related_taxon", "")))
        location_counts.update(split_terms(row.get("related_location", "")))
        mode_counts.update(split_terms(row.get("production_mode", "")))

    for disease, _count in disease_counts.most_common(8):
        related_docs = metadata[metadata["related_disease"].astype(str).str.contains(disease, case=False, regex=False)]
        terms = []
        for value in related_docs["keywords"].head(4):
            terms.extend(split_terms(value)[:4])
        rows.append(
            make_row(
                f"QE_META_DISEASE_{len(rows)+1:03d}",
                f"{disease} shrimp disease",
                "disease-specific",
                disease,
                "disease",
                "disease_alias",
                [disease, *terms[:6]],
                "metadata related_disease; metadata keywords",
                "Metadata-driven disease aliases can fill gaps when ontology labels are sparse.",
                "Metadata terms may include broad keywords; manual review recommended.",
            )
        )

    for taxon, _count in taxon_counts.most_common(8):
        rows.append(
            make_row(
                f"QE_META_TAXON_{len(rows)+1:03d}",
                f"{taxon} aquaculture",
                "species-location",
                taxon,
                "taxon",
                "taxon_alias",
                [taxon],
                "metadata related_taxon",
                "Metadata taxon variants support common/scientific-name expansion.",
                "Single metadata term may be generic; combine with disease/location/mode constraints.",
            )
        )

    for location, _count in location_counts.most_common(6):
        rows.append(
            make_row(
                f"QE_META_LOCATION_{len(rows)+1:03d}",
                f"aquaculture {location}",
                "local",
                location,
                "location",
                "location_alias",
                [location],
                "metadata related_location",
                "Location expansion improves recall for local/regional documents.",
                "Parent/broader locations should use lower weight to avoid local query drift.",
            )
        )

    for mode, _count in mode_counts.most_common(6):
        rows.append(
            make_row(
                f"QE_META_MODE_{len(rows)+1:03d}",
                f"{mode} shrimp",
                "hatchery-production-mode",
                mode,
                "production_mode",
                "production_mode_alias",
                [mode],
                "metadata production_mode",
                "Production-mode expansion helps mode-sensitive retrieval.",
                "Do not mix hatchery/grow-out/capture modes without guardrails.",
            )
        )
    return rows


def deduplicate(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    seen = set()
    output = []
    for row in rows:
        key = (
            row["original_query"].lower(),
            row["detected_entity"].lower(),
            row["expansion_type"].lower(),
            row["expansion_terms"].lower(),
        )
        if key in seen or not row["expansion_terms"].strip():
            continue
        seen.add(key)
        output.append(row)
    return output


def generate_examples() -> list[dict[str, str]]:
    rows = []
    rows.extend(SAFE_MANUAL_EXAMPLES)
    rows.extend(kg_rows_from_core_queries())
    rows.extend(metadata_examples())
    return deduplicate(rows)


def write_figure(rows: list[dict[str, str]]) -> None:
    FIGURE_OUT.parent.mkdir(parents=True, exist_ok=True)
    showcase = [
        ("AHPND shrimp disease", "AHPND", "Vibrio parahaemolyticus, disease alias, prevention"),
        ("lobster Khanh Hoa", "lobster + Khánh Hòa", "tôm hùm, spiny lobster, Vịnh Cam Ranh"),
        ("biosecurity shrimp hatchery", "biosecurity + hatchery", "an toàn sinh học, hatchery aquaculture, disease prevention"),
    ]
    fig, ax = plt.subplots(figsize=(12, 4.8), facecolor="white")
    ax.axis("off")
    x_positions = [0.08, 0.43, 0.74]
    headers = ["Original query", "Detected entity", "Expansion terms"]
    for x, header in zip(x_positions, headers):
        ax.text(x, 0.92, header, ha="center", va="center", fontsize=12, fontweight="bold", color="#111827")
    for idx, (query, entity, terms) in enumerate(showcase):
        y = 0.72 - idx * 0.25
        for x, text, color in [
            (x_positions[0], query, "#eff6ff"),
            (x_positions[1], entity, "#ecfdf5"),
            (x_positions[2], terms, "#fff7ed"),
        ]:
            ax.text(
                x,
                y,
                text,
                ha="center",
                va="center",
                fontsize=10.5,
                color="#111827",
                bbox={"boxstyle": "round,pad=0.45", "facecolor": color, "edgecolor": "#d1d5db"},
            )
        ax.annotate("", xy=(0.34, y), xytext=(0.20, y), arrowprops={"arrowstyle": "->", "color": "#6b7280", "lw": 1.4})
        ax.annotate("", xy=(0.63, y), xytext=(0.50, y), arrowprops={"arrowstyle": "->", "color": "#6b7280", "lw": 1.4})
    fig.text(
        0.5,
        0.03,
        "Hình 4.x. Minh họa ontology-based query expansion từ thực thể truy vấn sang alias và quan hệ KG",
        ha="center",
        va="bottom",
        fontsize=10,
        color="#374151",
    )
    fig.tight_layout(rect=(0.02, 0.08, 0.98, 0.98))
    fig.savefig(FIGURE_OUT, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def markdown_table(rows: list[list[str]]) -> list[str]:
    output = []
    output.append("| " + " | ".join(rows[0]) + " |")
    output.append("| " + " | ".join(["---"] * len(rows[0])) + " |")
    for row in rows[1:]:
        output.append("| " + " | ".join(row) + " |")
    return output


def write_design_report(rows: list[dict[str, str]]) -> None:
    counts = Counter(row["expansion_type"] for row in rows)
    examples = rows[:12]
    expansion_rows = [
        ["Expansion type", "Source", "Example", "Expected benefit", "Risk"],
        ["disease alias", "SKOS/metadata", "WSSV -> white spot syndrome virus", "Cross-language/entity recall", "Alias ambiguity"],
        ["disease to pathogen", "causedBy", "AHPND -> Vibrio parahaemolyticus", "Bridge disease-pathogen documents", "Pathogen too broad"],
        ["disease to symptom", "hasSymptom", "disease -> clinical signs", "Recover symptom-focused docs", "Symptom not disease-specific"],
        ["disease to prevention/treatment", "recommendedPrevention/Treatment", "AHPND -> biosecurity", "Management document recall", "Query drift to generic management"],
        ["taxon alias/scientific name", "SKOS/metadata", "whiteleg shrimp -> Penaeus vannamei", "Common/scientific name bridge", "Generic shrimp over-expansion"],
        ["location alias/hierarchy", "metadata/KG", "Khánh Hòa -> Vạn Ninh/Cam Ranh", "Local document recall", "Parent location too broad"],
        ["production mode alias", "metadata/KG", "hatchery -> trại giống", "Mode-sensitive retrieval", "Mixing hatchery/grow-out/capture"],
    ]

    lines = [
        "# Ontology-based Query Expansion Design",
        "",
        "## Purpose",
        "",
        "Mục tiêu là sử dụng ontology/KG và metadata để mở rộng truy vấn bằng alias, quan hệ disease-pathogen/symptom/prevention/treatment, taxon names và location hierarchy nhằm cải thiện candidate recall. Đây là prototype/design, không thay thế hybrid final.",
        "",
        "## Motivation",
        "",
        "- Hybrid hiện tại vẫn phụ thuộc vào candidate pool ban đầu.",
        "- Disease/pathogen bridge còn có thể yếu nếu query dùng disease nhưng tài liệu nhấn mạnh pathogen.",
        "- Location hierarchy và alias địa phương như Khánh Hòa/Khanh Hoa/ĐBSCL ảnh hưởng entity linking.",
        "- Candidate fusion cho thấy mở rộng candidate pool có tiềm năng tăng Recall@10/MAP.",
        "- KG diagnostic cho thấy direct facts và relation evidence đã đóng góp vào reranking.",
        "",
        "## Expansion types",
        "",
        *markdown_table(expansion_rows),
        "",
        "## Examples",
        "",
        "| original_query | detected_entity | expansion_type | expansion_terms | expected_effect |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in examples:
        terms = row["expansion_terms"].replace("|", "/")
        if len(terms) > 90:
            terms = terms[:87] + "..."
        lines.append(
            f"| {row['original_query']} | {row['detected_entity']} | {row['expansion_type']} | {terms} | {row['expected_effect']} |"
        )
    lines.extend(
        [
            "",
            "## How it could be integrated",
            "",
            "1. Query rewriting before vector retrieval: tạo expanded query text nhưng giới hạn số term và trọng số.",
            "2. Candidate expansion only: dùng query expansion để tăng candidate pool, sau đó rerank bằng hybrid hiện có.",
            "3. KG seed generation: dùng entity và relation expansion như một nguồn seed tương tự `hybrid_candidate_fusion`.",
            "",
            "## Safety and guardrails",
            "",
            "- Chỉ dùng expansion có source rõ: SKOS/ontology relation/metadata field.",
            "- Không tự động assert fact mới vào ontology.",
            "- Không mở rộng quá rộng gây query drift.",
            "- Disease-specific query phải giữ disease intent chính.",
            "- Location query phải tránh parent location quá rộng nếu query yêu cầu địa phương hẹp.",
            "- Production mode phải tránh trộn hatchery/grow-out/capture nếu intent hẹp.",
            "- Cần đánh giá metric riêng trước khi đưa vào hybrid final.",
            "",
            "## Relation to current experiments",
            "",
            "- Candidate fusion cho thấy mở rộng candidate pool có thể tăng Recall@10/MAP.",
            "- KG diagnostic cho thấy direct facts và relation evidence đã có đóng góp.",
            "- Query expansion là hướng tiếp theo để tăng recall và entity coverage trước bước reranking.",
            "",
            "## Example coverage",
            "",
            "| expansion_type | n_examples |",
            "| --- | ---: |",
        ]
    )
    for key, value in sorted(counts.items()):
        lines.append(f"| {key} | {value} |")
    lines.extend(
        [
            "",
            "## Limitations",
            "",
            "- Mới là prototype/design, chưa thay thế hybrid final.",
            "- Cần manual review expansion rules.",
            "- Cần đánh giá riêng nếu dùng trong runtime.",
            "- Một số expansion từ metadata là alias/candidate hints, không phải ontology assertion.",
            "",
            "## Report-ready Vietnamese paragraph",
            "",
            "Trong tương lai, hệ thống có thể bổ sung ontology-based query expansion để tăng độ phủ candidate trước khi reranking. Cụ thể, truy vấn về bệnh có thể được mở rộng sang pathogen, triệu chứng, biện pháp phòng trị; truy vấn về loài có thể bổ sung tên khoa học, tên thường gọi và tên tiếng Việt; truy vấn địa phương có thể dùng alias hoặc vùng liên quan từ metadata/KG. Cơ chế này cần được kiểm soát bằng guardrail để tránh query drift, đặc biệt với truy vấn disease-specific hoặc local hẹp. Vì vậy, query expansion nên được xem là hướng mở rộng/future work hoặc thí nghiệm candidate generation, chưa phải thành phần final của hybrid search.",
            "",
            "## Outputs",
            "",
            f"- `{EXAMPLES_OUT.relative_to(PROJECT_ROOT)}`",
            f"- `{DESIGN_OUT.relative_to(PROJECT_ROOT)}`",
            f"- `{FIGURE_OUT.relative_to(PROJECT_ROOT)}`",
        ]
    )
    DESIGN_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    rows = generate_examples()
    write_csv(EXAMPLES_OUT, rows)
    write_design_report(rows)
    write_figure(rows)
    print(f"[OK] Wrote {EXAMPLES_OUT.relative_to(PROJECT_ROOT)} ({len(rows)} examples)")
    print(f"[OK] Wrote {DESIGN_OUT.relative_to(PROJECT_ROOT)}")
    print(f"[OK] Wrote {FIGURE_OUT.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
