from __future__ import annotations

import csv
import json
import math
import re
import statistics
import sys
import unicodedata
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import hybrid_search
import run_core_baselines as core_baselines
from experiments import run_hybrid_candidate_fusion as fusion
from hybrid_search import METADATA_PATH, build_metadata_lookup, build_term_index, load_full_metadata
from run_core_baselines import OkapiBM25, _normalize_minmax, _tokenize
from vector_search import load_index


CORE_QUERY_SET = PROJECT_ROOT / "data" / "eval" / "final_query_set_core.csv"
CORE_JUDGMENTS = PROJECT_ROOT / "data" / "eval" / "relevance_judgments_core.csv"
EXT_QUERY_SET = PROJECT_ROOT / "data" / "eval" / "final_query_set_extended.csv"
EXT_JUDGMENTS = PROJECT_ROOT / "data" / "eval" / "relevance_judgments_extended.csv"
RESULTS_DIR = PROJECT_ROOT / "data" / "eval" / "results"
METRICS_DIR = PROJECT_ROOT / "data" / "eval" / "metrics"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

RESULT_FILES = {
    "lexical": RESULTS_DIR / "baseline_lexical_extended.csv",
    "vector": RESULTS_DIR / "baseline_vector_extended.csv",
    "vector_metadata": RESULTS_DIR / "baseline_vector_metadata_extended.csv",
    "ontology_sparql": RESULTS_DIR / "baseline_ontology_sparql_extended.csv",
    "hybrid": RESULTS_DIR / "baseline_hybrid_extended.csv",
    "hybrid_candidate_fusion": RESULTS_DIR / "baseline_hybrid_candidate_fusion_extended.csv",
}
SUMMARY_METRICS = METRICS_DIR / "baseline_metrics_summary_extended.csv"
BY_QUERY_METRICS = METRICS_DIR / "baseline_metrics_by_query_extended.csv"
BY_GROUP_METRICS = METRICS_DIR / "baseline_metrics_by_group_extended.csv"
JUDGMENT_AUDIT = OUTPUTS_DIR / "extended_query_judgment_audit.md"
EVAL_REPORT = OUTPUTS_DIR / "extended_query_evaluation_report.md"

TOP_DOCS = 10
TARGET_GROUP_COUNTS = {
    "disease-specific": 16,
    "species-location": 16,
    "local": 16,
    "hatchery-production-mode": 16,
    "biosecurity-management": 16,
    "generic-mixed": 16,
}

QUERY_COLUMNS = [
    "query_id",
    "query",
    "query_text",
    "query_group",
    "query_family",
    "primary_intent",
    "expected_entities_disease",
    "expected_entities_species",
    "expected_entities_location",
    "expected_entities_mode",
    "expected_entities_prevention",
    "expected_entities_management",
    "expected_entities_topic",
    "language",
    "difficulty_level",
    "reason_for_inclusion",
]

JUDGMENT_COLUMNS = [
    "query_id",
    "query_text",
    "query_group",
    "query_family",
    "doc_id",
    "title",
    "relevance_label",
    "relevance_label_text",
    "judgment_reason",
    "judged_using_fields",
]

METRIC_COLUMNS = [
    "baseline_name",
    "num_queries",
    "p_at_1",
    "p_at_3",
    "p_at_5",
    "recall_at_5",
    "recall_at_10",
    "mrr",
    "ndcg_at_5",
    "ndcg_at_10",
    "map",
]

BY_QUERY_COLUMNS = [
    "baseline_name",
    "query_id",
    "query_text",
    "query_group",
    "p_at_1",
    "p_at_3",
    "p_at_5",
    "recall_at_5",
    "recall_at_10",
    "mrr",
    "ndcg_at_5",
    "ndcg_at_10",
    "map",
]

BY_GROUP_COLUMNS = [
    "baseline_name",
    "query_group",
    "num_queries",
    "p_at_1",
    "p_at_3",
    "p_at_5",
    "recall_at_5",
    "recall_at_10",
    "mrr",
    "ndcg_at_5",
    "ndcg_at_10",
    "map",
]


NEW_QUERY_SPECS: list[dict[str, str]] = [
    {
        "query_id": "DS_EXT_001",
        "query_text": "white spot syndrome virus WSSV in shrimp",
        "query_group": "disease-specific",
        "query_family": "wssv_shrimp",
        "primary_intent": "disease_entity",
        "expected_entities_disease": "WSSV; white spot syndrome virus; WSD",
        "expected_entities_species": "shrimp; Penaeus vannamei; Penaeus monodon",
        "expected_entities_topic": "shrimp disease; viral disease",
        "language": "English",
    },
    {
        "query_id": "DS_EXT_002",
        "query_text": "AHPND EMS Vibrio parahaemolyticus whiteleg shrimp",
        "query_group": "disease-specific",
        "query_family": "ahpnd_ems_vibrio",
        "primary_intent": "disease_pathogen",
        "expected_entities_disease": "AHPND; EMS; Vibrio parahaemolyticus",
        "expected_entities_species": "Penaeus vannamei; whiteleg shrimp; shrimp",
        "expected_entities_topic": "acute hepatopancreatic necrosis disease",
        "language": "English",
    },
    {
        "query_id": "DS_EXT_003",
        "query_text": "EHP Enterocytozoon hepatopenaei trên tôm thẻ chân trắng",
        "query_group": "disease-specific",
        "query_family": "ehp_whiteleg",
        "primary_intent": "disease_entity",
        "expected_entities_disease": "EHP; Enterocytozoon hepatopenaei; HPM",
        "expected_entities_species": "tôm thẻ chân trắng; Penaeus vannamei; Litopenaeus vannamei",
        "expected_entities_topic": "shrimp disease",
        "language": "Vietnamese",
    },
    {
        "query_id": "DS_EXT_004",
        "query_text": "infectious myonecrosis virus IMNV Penaeus vannamei",
        "query_group": "disease-specific",
        "query_family": "imnv_vannamei",
        "primary_intent": "disease_entity",
        "expected_entities_disease": "IMNV; infectious myonecrosis; hoại tử cơ truyền nhiễm",
        "expected_entities_species": "Penaeus vannamei; Litopenaeus vannamei; shrimp",
        "expected_entities_topic": "viral disease",
        "language": "English",
    },
    {
        "query_id": "DS_EXT_005",
        "query_text": "DIV1 and WSSV co-infection in Litopenaeus vannamei",
        "query_group": "disease-specific",
        "query_family": "div1_wssv_coinfection",
        "primary_intent": "disease_coinfection",
        "expected_entities_disease": "DIV1; WSSV; co-infection",
        "expected_entities_species": "Litopenaeus vannamei; tôm thẻ chân trắng",
        "expected_entities_topic": "shrimp disease; viral disease",
        "language": "English",
    },
    {
        "query_id": "DS_EXT_006",
        "query_text": "vibriosis Vibrio campbellii shrimp hatchery larvae India",
        "query_group": "disease-specific",
        "query_family": "vibriosis_hatchery_india",
        "primary_intent": "disease_location",
        "expected_entities_disease": "vibriosis; Vibrio campbellii; luminescent bacteria",
        "expected_entities_species": "shrimp; Penaeus vannamei; larvae",
        "expected_entities_location": "India",
        "expected_entities_mode": "hatchery aquaculture",
        "language": "English",
    },
    {
        "query_id": "DS_EXT_007",
        "query_text": "translucent post-larvae disease TPD Penaeus vannamei",
        "query_group": "disease-specific",
        "query_family": "tpd_post_larvae",
        "primary_intent": "disease_life_stage",
        "expected_entities_disease": "TPD; translucent post-larvae disease; Vibrio parahaemolyticus",
        "expected_entities_species": "Penaeus vannamei; post-larvae; shrimp",
        "expected_entities_mode": "hatchery aquaculture",
        "language": "English",
    },
    {
        "query_id": "DS_EXT_008",
        "query_text": "Las bolitas syndrome Penaeus vannamei hatchery Latin America",
        "query_group": "disease-specific",
        "query_family": "las_bolitas",
        "primary_intent": "disease_location",
        "expected_entities_disease": "Las bolitas syndrome; AHPND",
        "expected_entities_species": "Penaeus vannamei; shrimp",
        "expected_entities_location": "Latin America",
        "expected_entities_mode": "hatchery aquaculture",
        "language": "English",
    },
    {
        "query_id": "DS_EXT_009",
        "query_text": "yellow head virus YHV shrimp disease",
        "query_group": "disease-specific",
        "query_family": "yhv_shrimp",
        "primary_intent": "disease_entity",
        "expected_entities_disease": "YHV; yellow head virus",
        "expected_entities_species": "shrimp; Penaeus vannamei; Penaeus monodon",
        "expected_entities_topic": "viral disease",
        "language": "English",
    },
    {
        "query_id": "DS_EXT_010",
        "query_text": "IHHNV pathogen monitoring in Penaeus vannamei",
        "query_group": "disease-specific",
        "query_family": "ihhnv_monitoring",
        "primary_intent": "disease_surveillance",
        "expected_entities_disease": "IHHNV; infectious hypodermal and hematopoietic necrosis virus",
        "expected_entities_species": "Penaeus vannamei; shrimp",
        "expected_entities_management": "pathogen monitoring; surveillance",
        "language": "English",
    },
    {
        "query_id": "SL_EXT_001",
        "query_text": "Penaeus monodon hatchery practices India",
        "query_group": "species-location",
        "query_family": "monodon_india_hatchery",
        "primary_intent": "species_location_mode",
        "expected_entities_species": "Penaeus monodon; tiger shrimp; shrimp",
        "expected_entities_location": "India",
        "expected_entities_mode": "hatchery aquaculture",
        "language": "English",
    },
    {
        "query_id": "SL_EXT_002",
        "query_text": "brackishwater shrimp culture Bangladesh Khulna Satkhira",
        "query_group": "species-location",
        "query_family": "bangladesh_brackish_shrimp",
        "primary_intent": "species_location",
        "expected_entities_species": "shrimp; brackishwater species",
        "expected_entities_location": "Bangladesh; Khulna; Satkhira",
        "expected_entities_mode": "aquaculture",
        "language": "English",
    },
    {
        "query_id": "SL_EXT_003",
        "query_text": "low water exchange shrimp farming Thailand",
        "query_group": "species-location",
        "query_family": "thailand_low_water_exchange",
        "primary_intent": "species_location_practice",
        "expected_entities_species": "shrimp; crustaceans",
        "expected_entities_location": "Thailand; Bangkok",
        "expected_entities_mode": "shrimp aquaculture",
        "expected_entities_topic": "low water exchange; pond culture",
        "language": "English",
    },
    {
        "query_id": "SL_EXT_004",
        "query_text": "Penaeus vannamei pathogen monitoring Latin America",
        "query_group": "species-location",
        "query_family": "vannamei_latin_america_monitoring",
        "primary_intent": "species_location_surveillance",
        "expected_entities_species": "Penaeus vannamei; shrimp",
        "expected_entities_location": "Latin America",
        "expected_entities_management": "pathogen monitoring; passive surveillance",
        "language": "English",
    },
    {
        "query_id": "SL_EXT_005",
        "query_text": "Litopenaeus vannamei broodstock larvae postlarvae Ecuador Mexico",
        "query_group": "species-location",
        "query_family": "vannamei_ecuador_mexico",
        "primary_intent": "species_location_life_stage",
        "expected_entities_species": "Litopenaeus vannamei; Penaeus vannamei; larvae; postlarvae; broodstock",
        "expected_entities_location": "Ecuador; Mexico",
        "expected_entities_mode": "hatchery aquaculture",
        "language": "English",
    },
    {
        "query_id": "SL_EXT_006",
        "query_text": "tôm hùm Khánh Hòa Vịnh Cam Ranh Vạn Ninh",
        "query_group": "species-location",
        "query_family": "lobster_khanh_hoa",
        "primary_intent": "species_location",
        "expected_entities_species": "tôm hùm; lobster",
        "expected_entities_location": "Khánh Hòa; Vịnh Cam Ranh; Vạn Ninh; Vịnh Văn Phong",
        "expected_entities_mode": "marine aquaculture",
        "language": "Vietnamese",
    },
    {
        "query_id": "SL_EXT_007",
        "query_text": "quan trắc môi trường tôm hùm Phú Yên Khánh Hòa",
        "query_group": "species-location",
        "query_family": "lobster_monitoring_central_vietnam",
        "primary_intent": "species_location_monitoring",
        "expected_entities_species": "tôm hùm; lobster",
        "expected_entities_location": "Phú Yên; Khánh Hòa",
        "expected_entities_management": "quan trắc môi trường; cảnh báo môi trường",
        "expected_entities_mode": "marine aquaculture",
        "language": "Vietnamese",
    },
    {
        "query_id": "SL_EXT_008",
        "query_text": "Nam Trung Bộ tôm thẻ chân trắng tôm sú quan trắc Vibrio",
        "query_group": "species-location",
        "query_family": "south_central_shrimp_monitoring",
        "primary_intent": "species_location_monitoring",
        "expected_entities_disease": "Vibrio spp.; Rickettsia-like bacteria",
        "expected_entities_species": "tôm thẻ chân trắng; tôm sú",
        "expected_entities_location": "Nam Trung Bộ; Phú Yên; Khánh Hòa; Bình Định; Ninh Thuận; Bình Thuận",
        "expected_entities_mode": "shrimp aquaculture; marine aquaculture",
        "language": "Vietnamese",
    },
    {
        "query_id": "SL_EXT_009",
        "query_text": "Penaeus vannamei introduction Asia Pacific disease risk",
        "query_group": "species-location",
        "query_family": "vannamei_asia_pacific_intro",
        "primary_intent": "species_location_risk",
        "expected_entities_species": "Penaeus vannamei; Penaeus stylirostris",
        "expected_entities_location": "Asia; Pacific",
        "expected_entities_topic": "animal introduction; disease risk; pathogen introduction",
        "language": "English",
    },
    {
        "query_id": "SL_EXT_010",
        "query_text": "lobster market trends Canada China global trade",
        "query_group": "species-location",
        "query_family": "lobster_market_canada_china",
        "primary_intent": "species_location_market",
        "expected_entities_species": "lobster",
        "expected_entities_location": "Canada; China; Global",
        "expected_entities_topic": "trade analysis; market trends",
        "expected_entities_mode": "capture fisheries",
        "language": "English",
    },
    {
        "query_id": "SL_EXT_011",
        "query_text": "fish farms water quality inland waters Hungary",
        "query_group": "species-location",
        "query_family": "fish_farms_hungary_water",
        "primary_intent": "species_location_environment",
        "expected_entities_species": "fish; aquatic animals",
        "expected_entities_location": "Hungary; inland waters",
        "expected_entities_topic": "water quality; fish farms",
        "expected_entities_mode": "inland fisheries; aquaculture",
        "language": "English",
    },
    {
        "query_id": "LO_EXT_001",
        "query_text": "ĐBSCL WSSV AHPND EHP trên tôm giống và tôm thương phẩm",
        "query_group": "local",
        "query_family": "mekong_delta_shrimp_disease",
        "primary_intent": "local_disease_surveillance",
        "expected_entities_disease": "WSSV; AHPND; EHP",
        "expected_entities_species": "tôm giống; tôm thương phẩm; tôm sú; tôm thẻ chân trắng",
        "expected_entities_location": "ĐBSCL; Đồng bằng sông Cửu Long",
        "expected_entities_mode": "shrimp aquaculture",
        "language": "Vietnamese",
    },
    {
        "query_id": "LO_EXT_002",
        "query_text": "quy hoạch nuôi tôm hùm Khánh Hòa đến 2030",
        "query_group": "local",
        "query_family": "khanh_hoa_lobster_planning",
        "primary_intent": "local_planning",
        "expected_entities_species": "tôm hùm; lobster",
        "expected_entities_location": "Khánh Hòa; Vạn Ninh; Cam Ranh; Vịnh Văn Phong",
        "expected_entities_topic": "quy hoạch; định hướng 2030; nuôi biển",
        "expected_entities_mode": "marine aquaculture",
        "language": "Vietnamese",
    },
    {
        "query_id": "LO_EXT_003",
        "query_text": "mưa lũ Phú Yên Khánh Hòa cảnh báo môi trường vùng nuôi tôm hùm",
        "query_group": "local",
        "query_family": "storm_lobster_monitoring",
        "primary_intent": "local_environment_warning",
        "expected_entities_disease": "Vibrio spp.; Rickettsia-like bacteria",
        "expected_entities_species": "tôm hùm; lobster",
        "expected_entities_location": "Phú Yên; Khánh Hòa",
        "expected_entities_management": "quan trắc môi trường; cảnh báo môi trường; mưa lũ",
        "expected_entities_mode": "marine aquaculture",
        "language": "Vietnamese",
    },
    {
        "query_id": "LO_EXT_004",
        "query_text": "nuôi tôm trên cát Thạch Hà Cẩm Xuyên Nghi Xuân Hà Tĩnh",
        "query_group": "local",
        "query_family": "ha_tinh_sand_shrimp",
        "primary_intent": "local_environment_disease",
        "expected_entities_species": "tôm; shrimp",
        "expected_entities_location": "Thạch Hà; Cẩm Xuyên; Nghi Xuân; Hà Tĩnh",
        "expected_entities_topic": "môi trường; dịch bệnh; nuôi tôm trên cát",
        "expected_entities_mode": "shrimp aquaculture",
        "language": "Vietnamese",
    },
    {
        "query_id": "LO_EXT_005",
        "query_text": "an toàn sinh học nuôi tôm Việt Nam WSSV EMS IMNV",
        "query_group": "local",
        "query_family": "vietnam_shrimp_biosecurity",
        "primary_intent": "local_biosecurity_disease",
        "expected_entities_disease": "WSSV; EMS; AHPNS; IMNV",
        "expected_entities_species": "tôm; Litopenaeus vannamei; tôm sú",
        "expected_entities_location": "Việt Nam",
        "expected_entities_prevention": "an toàn sinh học; biosecurity",
        "expected_entities_mode": "shrimp aquaculture",
        "language": "Vietnamese",
    },
    {
        "query_id": "LO_EXT_006",
        "query_text": "Cà Mau small-scale shrimp farmers risk management",
        "query_group": "local",
        "query_family": "camau_small_scale_shrimp",
        "primary_intent": "local_farmer_risk",
        "expected_entities_species": "shrimp; tôm",
        "expected_entities_location": "Cà Mau; Mekong Delta; Đồng bằng sông Cửu Long",
        "expected_entities_management": "risk management; small-scale farmers",
        "expected_entities_mode": "shrimp aquaculture",
        "language": "English",
    },
    {
        "query_id": "LO_EXT_007",
        "query_text": "Khánh Hòa Bình Định Ninh Thuận Bình Thuận quan trắc tôm",
        "query_group": "local",
        "query_family": "south_central_monitoring",
        "primary_intent": "local_monitoring",
        "expected_entities_species": "tôm hùm; tôm thẻ chân trắng; tôm sú",
        "expected_entities_location": "Khánh Hòa; Bình Định; Ninh Thuận; Bình Thuận; Nam Trung Bộ",
        "expected_entities_management": "quan trắc môi trường",
        "expected_entities_mode": "marine aquaculture; shrimp aquaculture",
        "language": "Vietnamese",
    },
    {
        "query_id": "LO_EXT_008",
        "query_text": "biosecurity Peru shrimp farming sustainable livelihoods",
        "query_group": "local",
        "query_family": "peru_shrimp_biosecurity",
        "primary_intent": "local_biosecurity",
        "expected_entities_species": "shrimp",
        "expected_entities_location": "Peru",
        "expected_entities_prevention": "biosecurity",
        "expected_entities_topic": "sustainable livelihoods; shrimp farming",
        "expected_entities_mode": "shrimp aquaculture",
        "language": "English",
    },
    {
        "query_id": "LO_EXT_009",
        "query_text": "Philippines AHPND shrimp aquaculture surveillance",
        "query_group": "local",
        "query_family": "philippines_ahpnd_surveillance",
        "primary_intent": "local_disease_surveillance",
        "expected_entities_disease": "AHPND",
        "expected_entities_species": "shrimp; Penaeus vannamei",
        "expected_entities_location": "Philippines",
        "expected_entities_management": "surveillance; disease monitoring",
        "expected_entities_mode": "shrimp aquaculture",
        "language": "English",
    },
    {
        "query_id": "HM_EXT_001",
        "query_text": "Penaeus monodon shrimp hatchery productivity health management",
        "query_group": "hatchery-production-mode",
        "query_family": "monodon_hatchery_health",
        "primary_intent": "hatchery_species_management",
        "expected_entities_species": "Penaeus monodon; shrimp",
        "expected_entities_mode": "hatchery aquaculture",
        "expected_entities_management": "health management; hatchery productivity",
        "language": "English",
    },
    {
        "query_id": "HM_EXT_002",
        "query_text": "white shrimp Penaeus vannamei hatchery biosecurity Latin America",
        "query_group": "hatchery-production-mode",
        "query_family": "vannamei_hatchery_biosecurity",
        "primary_intent": "hatchery_species_biosecurity",
        "expected_entities_species": "Penaeus vannamei; white shrimp",
        "expected_entities_location": "Latin America; Caribbean",
        "expected_entities_mode": "hatchery aquaculture",
        "expected_entities_prevention": "biosecurity; health management",
        "language": "English",
    },
    {
        "query_id": "HM_EXT_003",
        "query_text": "Penaeus monodon post-larvae hatchery WSSV HPV MBV IHHNV India",
        "query_group": "hatchery-production-mode",
        "query_family": "monodon_postlarvae_pathogens",
        "primary_intent": "hatchery_disease_life_stage",
        "expected_entities_disease": "WSSV; HPV; MBV; IHHNV",
        "expected_entities_species": "Penaeus monodon; post-larvae; shrimp",
        "expected_entities_location": "India; Kerala",
        "expected_entities_mode": "hatchery aquaculture",
        "language": "English",
    },
    {
        "query_id": "HM_EXT_004",
        "query_text": "Penaeus vannamei larvae low survival hatchery vibriosis",
        "query_group": "hatchery-production-mode",
        "query_family": "vannamei_larvae_low_survival",
        "primary_intent": "hatchery_disease_microbiome",
        "expected_entities_disease": "vibriosis; AHPND; zoea 2 syndrome",
        "expected_entities_species": "Penaeus vannamei; larvae; shrimp",
        "expected_entities_mode": "hatchery aquaculture",
        "expected_entities_topic": "microbiome; low survival",
        "language": "English",
    },
    {
        "query_id": "HM_EXT_005",
        "query_text": "Litopenaeus vannamei larvae postlarvae broodstock hatchery probiotics",
        "query_group": "hatchery-production-mode",
        "query_family": "vannamei_broodstock_probiotics",
        "primary_intent": "hatchery_life_stage",
        "expected_entities_disease": "vibriosis",
        "expected_entities_species": "Litopenaeus vannamei; larvae; postlarvae; broodstock",
        "expected_entities_location": "Ecuador; Mexico",
        "expected_entities_mode": "hatchery aquaculture",
        "expected_entities_topic": "probiotics; Vibrio",
        "language": "English",
    },
    {
        "query_id": "HM_EXT_006",
        "query_text": "luminescent Vibrios phage therapy hatchery post-larvae Penaeus vannamei",
        "query_group": "hatchery-production-mode",
        "query_family": "phage_luminous_vibrio",
        "primary_intent": "hatchery_disease_control",
        "expected_entities_disease": "vibriosis; luminous vibriosis; Vibrio harveyi",
        "expected_entities_species": "Penaeus vannamei; post-larvae; shrimp",
        "expected_entities_location": "India",
        "expected_entities_mode": "hatchery aquaculture",
        "expected_entities_prevention": "bacteriophage; phage therapy",
        "language": "English",
    },
    {
        "query_id": "HM_EXT_007",
        "query_text": "AHPND biomarkers microbiome shrimp hatchery larvae survival",
        "query_group": "hatchery-production-mode",
        "query_family": "ahpnd_hatchery_biomarkers",
        "primary_intent": "hatchery_disease_biomarker",
        "expected_entities_disease": "AHPND; vibriosis",
        "expected_entities_species": "Penaeus vannamei; larvae; shrimp",
        "expected_entities_mode": "hatchery aquaculture",
        "expected_entities_topic": "microbiome; biomarkers; survival",
        "language": "English",
    },
    {
        "query_id": "HM_EXT_008",
        "query_text": "trại giống tôm biofloc SPF an toàn sinh học",
        "query_group": "hatchery-production-mode",
        "query_family": "vietnam_hatchery_spf_biosecurity",
        "primary_intent": "hatchery_biosecurity",
        "expected_entities_species": "tôm; Litopenaeus vannamei; tôm sú",
        "expected_entities_mode": "hatchery aquaculture; shrimp aquaculture",
        "expected_entities_prevention": "an toàn sinh học; biosecurity; SPF; biofloc",
        "language": "Vietnamese",
    },
    {
        "query_id": "HM_EXT_009",
        "query_text": "zoea stage AHPND Vibrio alginolyticus hatchery Penaeus vannamei",
        "query_group": "hatchery-production-mode",
        "query_family": "zoea_ahpnd_hatchery",
        "primary_intent": "hatchery_larvae_disease",
        "expected_entities_disease": "AHPND; Las bolitas syndrome; Vibrio alginolyticus",
        "expected_entities_species": "Penaeus vannamei; zoea; post-larvae",
        "expected_entities_location": "Latin America",
        "expected_entities_mode": "hatchery aquaculture",
        "language": "English",
    },
    {
        "query_id": "HM_EXT_010",
        "query_text": "Indian shrimp hatcheries Vibrio campbellii larvae virulence",
        "query_group": "hatchery-production-mode",
        "query_family": "indian_hatchery_vibrio",
        "primary_intent": "hatchery_pathogen",
        "expected_entities_disease": "vibriosis; Vibrio campbellii",
        "expected_entities_species": "shrimp; Penaeus vannamei; larvae",
        "expected_entities_location": "India",
        "expected_entities_mode": "hatchery aquaculture",
        "language": "English",
    },
    {
        "query_id": "HM_EXT_011",
        "query_text": "post-larvae disease biosecurity in Penaeus vannamei hatchery",
        "query_group": "hatchery-production-mode",
        "query_family": "postlarvae_biosecurity",
        "primary_intent": "hatchery_prevention",
        "expected_entities_disease": "TPD; vibriosis; AHPND",
        "expected_entities_species": "Penaeus vannamei; post-larvae",
        "expected_entities_mode": "hatchery aquaculture",
        "expected_entities_prevention": "biosecurity",
        "language": "English",
    },
    {
        "query_id": "HM_EXT_012",
        "query_text": "shrimp hatchery health management India Latin America",
        "query_group": "hatchery-production-mode",
        "query_family": "hatchery_health_multiregion",
        "primary_intent": "hatchery_management",
        "expected_entities_species": "shrimp; Penaeus monodon; Penaeus vannamei",
        "expected_entities_location": "India; Latin America",
        "expected_entities_mode": "hatchery aquaculture",
        "expected_entities_management": "health management; biosecurity",
        "language": "English",
    },
    {
        "query_id": "BI_EXT_001",
        "query_text": "Progressive Management Pathway aquaculture biosecurity guidelines",
        "query_group": "biosecurity-management",
        "query_family": "pmp_biosecurity",
        "primary_intent": "biosecurity_framework",
        "expected_entities_prevention": "biosecurity; disease prevention; risk management",
        "expected_entities_management": "Progressive Management Pathway; guidelines",
        "expected_entities_topic": "aquatic animal diseases; disease outbreaks",
        "language": "English",
    },
    {
        "query_id": "BI_EXT_002",
        "query_text": "emergency preparedness aquatic animal disease national system",
        "query_group": "biosecurity-management",
        "query_family": "emergency_preparedness",
        "primary_intent": "emergency_response",
        "expected_entities_management": "emergency response; national system; aquatic animal health",
        "expected_entities_topic": "disease outbreak; contingency planning",
        "language": "English",
    },
    {
        "query_id": "BI_EXT_003",
        "query_text": "surveillance zoning aquatic animal diseases risk assessment",
        "query_group": "biosecurity-management",
        "query_family": "surveillance_zoning_extended",
        "primary_intent": "surveillance_zoning",
        "expected_entities_management": "surveillance; zoning; risk assessment",
        "expected_entities_topic": "aquatic animal diseases; animal health",
        "language": "English",
    },
    {
        "query_id": "BI_EXT_004",
        "query_text": "risk analysis movements of live aquatic animals pathogen spread",
        "query_group": "biosecurity-management",
        "query_family": "live_animal_movement_risk",
        "primary_intent": "risk_analysis_biosecurity",
        "expected_entities_management": "risk analysis; risk assessment; risk management; risk communication",
        "expected_entities_topic": "live aquatic animals; pathogen spread; disease transmission",
        "language": "English",
    },
    {
        "query_id": "BI_EXT_005",
        "query_text": "Penaeus vannamei introduction disease risk Asia Pacific",
        "query_group": "biosecurity-management",
        "query_family": "movement_disease_risk",
        "primary_intent": "biosecurity_movement",
        "expected_entities_species": "Penaeus vannamei; Penaeus stylirostris",
        "expected_entities_location": "Asia; Pacific",
        "expected_entities_management": "disease risk; pathogen introduction",
        "language": "English",
    },
    {
        "query_id": "BI_EXT_006",
        "query_text": "AHPND strategy manual disease prevention eradication policy",
        "query_group": "biosecurity-management",
        "query_family": "ahpnd_prevention_policy",
        "primary_intent": "disease_prevention_policy",
        "expected_entities_disease": "AHPND",
        "expected_entities_prevention": "disease prevention; disease control; disease eradication",
        "expected_entities_management": "policy; strategy manual",
        "language": "English",
    },
    {
        "query_id": "BI_EXT_007",
        "query_text": "health management biosecurity maintenance white shrimp hatcheries",
        "query_group": "biosecurity-management",
        "query_family": "hatchery_biosecurity_management",
        "primary_intent": "biosecurity_hatchery",
        "expected_entities_species": "Penaeus vannamei; white shrimp",
        "expected_entities_mode": "hatchery aquaculture",
        "expected_entities_prevention": "biosecurity; health management",
        "language": "English",
    },
    {
        "query_id": "BI_EXT_008",
        "query_text": "biosecurity disease surveillance shrimp AHPND Thailand Bangkok",
        "query_group": "biosecurity-management",
        "query_family": "ahpnd_surveillance_thailand",
        "primary_intent": "biosecurity_surveillance",
        "expected_entities_disease": "AHPND; EMS; Vibrio",
        "expected_entities_species": "shrimp; Penaeus vannamei; Penaeus monodon",
        "expected_entities_location": "Thailand; Bangkok",
        "expected_entities_prevention": "biosecurity; disease prevention",
        "expected_entities_management": "disease surveillance",
        "language": "English",
    },
    {
        "query_id": "BI_EXT_009",
        "query_text": "an toàn sinh học phòng bệnh đốm trắng tôm nuôi",
        "query_group": "biosecurity-management",
        "query_family": "wssv_biosecurity_vietnamese",
        "primary_intent": "biosecurity_disease_prevention",
        "expected_entities_disease": "WSSV; bệnh đốm trắng",
        "expected_entities_species": "tôm; tôm thẻ chân trắng; tôm sú",
        "expected_entities_prevention": "an toàn sinh học; biosecurity; biofloc",
        "expected_entities_mode": "shrimp aquaculture",
        "language": "Vietnamese",
    },
    {
        "query_id": "BI_EXT_010",
        "query_text": "risk analysis training aquaculture disease hazards food safety",
        "query_group": "biosecurity-management",
        "query_family": "risk_analysis_training",
        "primary_intent": "risk_analysis_training",
        "expected_entities_management": "risk analysis; risk factors; decision making",
        "expected_entities_topic": "pathogens; food safety; environmental hazards",
        "expected_entities_mode": "aquaculture",
        "language": "English",
    },
    {
        "query_id": "GE_EXT_001",
        "query_text": "sustainable aquaculture guidelines communication toolkit",
        "query_group": "generic-mixed",
        "query_family": "sustainable_aquaculture_communication",
        "primary_intent": "generic_guidelines",
        "expected_entities_topic": "sustainable aquaculture; guidelines; communication; stakeholders",
        "expected_entities_mode": "aquaculture",
        "language": "English",
    },
    {
        "query_id": "GE_EXT_002",
        "query_text": "ecosystem approach to aquaculture environmental management",
        "query_group": "generic-mixed",
        "query_family": "ecosystem_approach",
        "primary_intent": "generic_environment",
        "expected_entities_topic": "ecosystem approach; environmental management; environmental impact",
        "expected_entities_mode": "aquaculture",
        "language": "English",
    },
    {
        "query_id": "GE_EXT_003",
        "query_text": "aquaculture climate change adaptation fisheries resilience",
        "query_group": "generic-mixed",
        "query_family": "climate_adaptation",
        "primary_intent": "generic_climate",
        "expected_entities_topic": "climate change adaptation; resilience; sustainable development",
        "expected_entities_mode": "aquaculture; fisheries",
        "language": "English",
    },
    {
        "query_id": "GE_EXT_004",
        "query_text": "water quality and fish health environmental stress",
        "query_group": "generic-mixed",
        "query_family": "water_quality_fish_health",
        "primary_intent": "generic_fish_health",
        "expected_entities_species": "fish; aquatic animals",
        "expected_entities_topic": "water quality; fish health; environmental stress; toxicology",
        "expected_entities_mode": "inland fisheries; aquaculture",
        "language": "English",
    },
    {
        "query_id": "GE_EXT_005",
        "query_text": "gene banking aquatic genetic resources cryopreservation protocols",
        "query_group": "generic-mixed",
        "query_family": "gene_banking",
        "primary_intent": "generic_genetic_resources",
        "expected_entities_species": "aquatic species; fish; shellfish",
        "expected_entities_topic": "aquatic genetic resources; gene banks; cryopreservation; protocols",
        "expected_entities_mode": "aquaculture",
        "language": "English",
    },
    {
        "query_id": "GE_EXT_006",
        "query_text": "marine lobsters taxonomy habitats geographical distribution",
        "query_group": "generic-mixed",
        "query_family": "lobster_taxonomy",
        "primary_intent": "generic_species_catalogue",
        "expected_entities_species": "lobster; lobsters; Decapoda",
        "expected_entities_topic": "taxonomy; habitats; geographical distribution; identification",
        "expected_entities_mode": "capture fisheries",
        "language": "English",
    },
    {
        "query_id": "GE_EXT_007",
        "query_text": "aquaculture environmental impact assessment coastal areas",
        "query_group": "generic-mixed",
        "query_family": "environmental_impact_coastal",
        "primary_intent": "generic_environmental_assessment",
        "expected_entities_location": "coastal areas; marine environment",
        "expected_entities_topic": "environmental impact assessment; environmental protection",
        "expected_entities_mode": "aquaculture",
        "language": "English",
    },
    {
        "query_id": "GE_EXT_008",
        "query_text": "inland fisheries fish farms water quality survey managers",
        "query_group": "generic-mixed",
        "query_family": "fish_farm_water_survey",
        "primary_intent": "generic_water_quality",
        "expected_entities_species": "fish; aquatic animals",
        "expected_entities_location": "inland waters; Hungary; Global",
        "expected_entities_topic": "water quality; surveys; fish farms",
        "expected_entities_mode": "inland fisheries; aquaculture",
        "language": "English",
    },
    {
        "query_id": "GE_EXT_009",
        "query_text": "aquatic animal diseases diagnostic guide Asia",
        "query_group": "generic-mixed",
        "query_family": "diagnostic_guide_asia",
        "primary_intent": "generic_diagnostic",
        "expected_entities_species": "aquatic animals; fish; crustaceans",
        "expected_entities_location": "Asia",
        "expected_entities_topic": "diagnosis; animal diseases; fish diseases",
        "expected_entities_mode": "inland fisheries; aquaculture",
        "language": "English",
    },
    {
        "query_id": "GE_EXT_010",
        "query_text": "aquaculture production sustainable development food security",
        "query_group": "generic-mixed",
        "query_family": "production_sustainability",
        "primary_intent": "generic_sustainability",
        "expected_entities_topic": "aquaculture production; sustainable development; food security",
        "expected_entities_mode": "aquaculture",
        "language": "English",
    },
    {
        "query_id": "GE_EXT_011",
        "query_text": "risk factors invasive species genetic impacts aquaculture",
        "query_group": "generic-mixed",
        "query_family": "risk_factors_invasive_genetic",
        "primary_intent": "generic_risk",
        "expected_entities_management": "risk analysis; risk factors",
        "expected_entities_topic": "invasive species; genetic impacts; environmental hazards",
        "expected_entities_mode": "aquaculture",
        "language": "English",
    },
    {
        "query_id": "GE_EXT_012",
        "query_text": "fisheries aquaculture data collection regional planning",
        "query_group": "generic-mixed",
        "query_family": "regional_planning_data",
        "primary_intent": "generic_governance",
        "expected_entities_location": "Central Asia; Caucasus; Kazakhstan",
        "expected_entities_topic": "fishery data; data collection; regional planning",
        "expected_entities_mode": "inland fisheries; aquaculture",
        "language": "English",
    },
    {
        "query_id": "GE_EXT_013",
        "query_text": "nuôi biển tôm hùm lồng bè phát triển ngành",
        "query_group": "generic-mixed",
        "query_family": "marine_aquaculture_lobster",
        "primary_intent": "generic_marine_aquaculture",
        "expected_entities_species": "tôm hùm; lobster",
        "expected_entities_location": "Khánh Hòa; Việt Nam",
        "expected_entities_topic": "nuôi biển; phát triển ngành; nuôi lồng bè",
        "expected_entities_mode": "marine aquaculture",
        "language": "Vietnamese",
    },
    {
        "query_id": "GE_EXT_014",
        "query_text": "công nghệ gen chọn giống tôm kháng bệnh CRISPR",
        "query_group": "generic-mixed",
        "query_family": "shrimp_genetics_resistance",
        "primary_intent": "generic_genetics_disease_resistance",
        "expected_entities_disease": "WSSV; YHV",
        "expected_entities_species": "tôm; shrimp",
        "expected_entities_topic": "công nghệ gen; chọn giống; kháng bệnh; CRISPR; genomics",
        "expected_entities_mode": "shrimp aquaculture",
        "language": "Vietnamese",
    },
    {
        "query_id": "GE_EXT_015",
        "query_text": "probiotic LAB antagonizing Vibrio parahaemolyticus whiteleg shrimp",
        "query_group": "generic-mixed",
        "query_family": "probiotic_vibrio_control",
        "primary_intent": "generic_prevention_research",
        "expected_entities_disease": "AHPND; vibriosis; Vibrio parahaemolyticus",
        "expected_entities_species": "Penaeus vannamei; whiteleg shrimp",
        "expected_entities_prevention": "probiotic; lactic acid bacteria; LAB",
        "expected_entities_mode": "shrimp aquaculture",
        "language": "English",
    },
    {
        "query_id": "GE_EXT_016",
        "query_text": "microbiome Pacific whiteleg shrimp AHPND EMS outbreak",
        "query_group": "generic-mixed",
        "query_family": "microbiome_ahpnd_outbreak",
        "primary_intent": "generic_research_microbiome",
        "expected_entities_disease": "AHPND; EMS",
        "expected_entities_species": "Pacific whiteleg shrimp; Litopenaeus vannamei",
        "expected_entities_topic": "microbiome; outbreak; bacterial community",
        "expected_entities_mode": "shrimp aquaculture",
        "language": "English",
    },
]


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def normalize(value: Any) -> str:
    text = "" if value is None or (isinstance(value, float) and math.isnan(value)) else str(value)
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def split_terms(value: Any) -> list[str]:
    text = "" if value is None or (isinstance(value, float) and math.isnan(value)) else str(value)
    raw_terms = re.split(r"[;,/|]", text)
    terms = []
    for term in raw_terms:
        cleaned = term.strip()
        if cleaned and cleaned.lower() not in {"nan", "none"}:
            terms.append(cleaned)
    return terms


def term_matches(term: str, text_norm: str) -> bool:
    term_norm = normalize(term)
    if not term_norm:
        return False
    if term_norm in text_norm:
        return True
    tokens = [tok for tok in term_norm.split() if len(tok) >= 3]
    if len(tokens) >= 2:
        return all(tok in text_norm for tok in tokens)
    return False


def field_matches(terms: list[str], *texts: Any) -> list[str]:
    text_norm = normalize(" ".join("" if x is None else str(x) for x in texts))
    return [term for term in terms if term_matches(term, text_norm)]


def make_extended_query_set() -> list[dict[str, Any]]:
    core = pd.read_csv(CORE_QUERY_SET, encoding="utf-8-sig")
    rows: list[dict[str, Any]] = []
    for _, row in core.iterrows():
        item = {col: row.get(col, "") for col in core.columns}
        item["query"] = item.get("query_text", "")
        item["language"] = "Vietnamese" if normalize(item.get("query_text", "")).split()[:1] else ""
        rows.append(item)

    for spec in NEW_QUERY_SPECS:
        item = {
            "query_id": spec["query_id"],
            "query": spec["query_text"],
            "query_text": spec["query_text"],
            "query_group": spec["query_group"],
            "query_family": spec.get("query_family", ""),
            "primary_intent": spec.get("primary_intent", ""),
            "expected_entities_disease": spec.get("expected_entities_disease", ""),
            "expected_entities_species": spec.get("expected_entities_species", ""),
            "expected_entities_location": spec.get("expected_entities_location", ""),
            "expected_entities_mode": spec.get("expected_entities_mode", ""),
            "expected_entities_prevention": spec.get("expected_entities_prevention", ""),
            "expected_entities_management": spec.get("expected_entities_management", ""),
            "expected_entities_topic": spec.get("expected_entities_topic", ""),
            "language": spec.get("language", ""),
            "difficulty_level": spec.get("difficulty_level", "medium"),
            "reason_for_inclusion": "Extended evaluation query generated from metadata-backed disease/species/location/mode/topic coverage.",
        }
        rows.append(item)

    ids = [str(row["query_id"]) for row in rows]
    duplicates = sorted({qid for qid in ids if ids.count(qid) > 1})
    if duplicates:
        raise ValueError(f"Duplicate extended query IDs: {duplicates}")

    counts = defaultdict(int)
    for row in rows:
        counts[str(row["query_group"])] += 1
    for group, expected in TARGET_GROUP_COUNTS.items():
        if counts[group] != expected:
            raise ValueError(f"Expected {expected} queries for {group}, got {counts[group]}")
    return rows


def get_query_text(row: dict[str, Any]) -> str:
    return str(row.get("query_text") or row.get("query") or "")


def run_baselines(query_rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    df_meta = load_full_metadata(str(METADATA_PATH))
    metadata_lookup = build_metadata_lookup(df_meta)
    term_index = build_term_index(df_meta)
    title_by_doc = {str(row["doc_id"]): str(row.get("title", "")) for _, row in df_meta.iterrows()}

    records = core_baselines._load_chunk_records()
    bm25 = OkapiBM25([_tokenize(str(row.get("text", ""))) for row in records])

    print("[STEP] Loading vector model + FAISS for extended baselines...")
    model, index, vec_records = load_index()
    if len(vec_records) != len(records):
        print("[WARN] BM25 chunk records and vector records have different lengths.")

    hybrid_search._init_kg_if_needed()
    graph = hybrid_search._KG_GRAPH
    kg_index = hybrid_search._KG_INDEX
    map_fn = hybrid_search._map_doc_to_kg_uri

    orig_final = hybrid_search.FINAL_K
    orig_candidate = hybrid_search.CANDIDATE_K
    hybrid_search.FINAL_K = TOP_DOCS
    hybrid_search.CANDIDATE_K = core_baselines.HYBRID_CANDIDATE_CHUNKS
    result_rows: dict[str, list[dict[str, Any]]] = {
        "lexical": [],
        "vector": [],
        "vector_metadata": [],
        "ontology_sparql": [],
        "hybrid": [],
        "hybrid_candidate_fusion": [],
    }
    try:
        for query in query_rows:
            qid = str(query["query_id"])
            qtext = get_query_text(query)
            print(f"[RUN] {qid}: {qtext[:80]}...")
            result_rows["lexical"].extend(core_baselines.lexical_bm25_rows(qid, qtext, records, bm25, title_by_doc))
            result_rows["vector"].extend(core_baselines.vector_rows(qid, qtext, model, index, vec_records, title_by_doc))
            result_rows["vector_metadata"].extend(
                core_baselines.vector_metadata_rows(qid, qtext, model, index, vec_records, metadata_lookup, term_index, title_by_doc)
            )
            if graph is not None and kg_index is not None:
                result_rows["ontology_sparql"].extend(
                    core_baselines.ontology_sparql_rows(
                        qid, qtext, graph, kg_index, metadata_lookup, title_by_doc, map_fn
                    )
                )
            else:
                result_rows["ontology_sparql"].extend(
                    fallback_ontology_rows(qid, qtext, metadata_lookup, title_by_doc)
                )
            result_rows["hybrid"].extend(
                core_baselines.hybrid_rows(qid, qtext, model, index, vec_records, metadata_lookup, term_index, title_by_doc)
            )

        kg_seed_by_query = rows_to_seed_lookup(result_rows["ontology_sparql"])
        result_rows["hybrid_candidate_fusion"] = run_candidate_fusion_rows(
            query_rows, model, index, vec_records, bm25, metadata_lookup, term_index, kg_seed_by_query
        )
    finally:
        hybrid_search.FINAL_K = orig_final
        hybrid_search.CANDIDATE_K = orig_candidate

    for name in ["lexical", "vector", "vector_metadata", "ontology_sparql", "hybrid"]:
        core_baselines.write_csv(RESULT_FILES[name], result_rows[name])
    write_csv(RESULT_FILES["hybrid_candidate_fusion"], result_rows["hybrid_candidate_fusion"], fusion.RESULT_FIELDS)
    return result_rows


def fallback_ontology_rows(
    query_id: str,
    query_text: str,
    metadata_lookup: dict[str, dict[str, Any]],
    title_by_doc: dict[str, str],
) -> list[dict[str, Any]]:
    rows = []
    for rank, doc_id in enumerate(list(metadata_lookup.keys())[:TOP_DOCS], start=1):
        rows.append(
            {
                "query_id": query_id,
                "query_text": query_text,
                "baseline_name": "ontology_sparql",
                "rank": rank,
                "doc_id": doc_id,
                "title": title_by_doc.get(doc_id, ""),
                "score_raw": 0.0,
                "score_normalized": 1.0 if rank == 1 else 0.0,
                "retrieval_level": "kg_structured",
                "explanation_short": "KG disabled; sparse placeholder ranking",
                "source_pipeline": "experiments/run_extended_evaluation.py fallback",
            }
        )
    return rows


def rows_to_seed_lookup(rows: list[dict[str, Any]]) -> dict[str, dict[str, dict[str, Any]]]:
    by_query: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in rows:
        try:
            rank = int(float(row.get("rank", 0)))
        except Exception:
            continue
        if rank > fusion.KG_SEED_TOP_K:
            continue
        qid = str(row.get("query_id", ""))
        doc_id = str(row.get("doc_id", ""))
        if qid and doc_id:
            by_query[qid][doc_id] = row | {"rank_int": rank}
    return dict(by_query)


def run_candidate_fusion_rows(
    query_rows: list[dict[str, Any]],
    model: Any,
    index: Any,
    records: list[dict[str, Any]],
    bm25: OkapiBM25,
    metadata_lookup: dict[str, dict[str, Any]],
    term_index: list[dict[str, Any]],
    kg_seed_by_query: dict[str, dict[str, dict[str, Any]]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for query in query_rows:
        qid = str(query["query_id"])
        qtext = get_query_text(query)
        top_items, stats = fusion.build_fused_candidates_for_query(
            qid, qtext, model, index, records, bm25, metadata_lookup, term_index, kg_seed_by_query
        )
        raw_scores = [float(item.get("final_score", 0.0)) for item in top_items]
        normalized = _normalize_minmax(raw_scores)
        for rank, (item, norm_score) in enumerate(zip(top_items, normalized), start=1):
            rows.append(
                {
                    "query_id": qid,
                    "query": qtext,
                    "query_text": qtext,
                    "query_group": query.get("query_group", ""),
                    "baseline_name": "hybrid_candidate_fusion",
                    "rank": rank,
                    "doc_id": item.get("doc_id", ""),
                    "title": item.get("title", ""),
                    "score_raw": item.get("final_score", 0.0),
                    "score_normalized": norm_score,
                    "final_score": item.get("final_score", 0.0),
                    "vector_score": item.get("vector_score", 0.0),
                    "metadata_delta": item.get("metadata_delta", 0.0),
                    "kg_score": item.get("kg_score", 0.0),
                    "intent_adjustment": item.get("intent_adjustment", 0.0),
                    "lexical_rank": item.get("lexical_rank", ""),
                    "lexical_score": item.get("lexical_score", 0.0),
                    "kg_seed_rank": item.get("kg_seed_rank", ""),
                    "kg_seed_score": item.get("kg_seed_score", 0.0),
                    "vector_rank": item.get("vector_rank", ""),
                    "candidate_sources": item.get("candidate_sources", ""),
                    "candidate_union_count": stats["union_candidate_count"],
                    "retrieval_level": "hybrid_candidate_fusion_doc_pool",
                    "explanation": item.get("explanation", ""),
                    "explanation_short": "BM25 + vector + KG/SPARQL seed candidate union, hybrid scoring rerank",
                    "source_pipeline": (
                        "experiments/run_extended_evaluation.py; "
                        f"lexical_top_k={fusion.LEXICAL_TOP_K}; vector_top_k={fusion.VECTOR_TOP_K}; "
                        f"kg_seed_top_k={fusion.KG_SEED_TOP_K}; scoring=vector_score+metadata_delta+kg_score+intent_adjustment; "
                        "not final hybrid"
                    ),
                }
            )
    return rows


def metadata_text(row: dict[str, Any]) -> str:
    fields = [
        "title",
        "related_disease",
        "related_taxon",
        "related_location",
        "production_mode",
        "keywords",
        "note",
    ]
    return " ".join(str(row.get(field, "")) for field in fields)


def metadata_match_score(query: dict[str, Any], meta_row: dict[str, Any]) -> tuple[float, dict[str, list[str]]]:
    disease = split_terms(query.get("expected_entities_disease", ""))
    species = split_terms(query.get("expected_entities_species", ""))
    locations = split_terms(query.get("expected_entities_location", ""))
    modes = split_terms(query.get("expected_entities_mode", ""))
    prevention = split_terms(query.get("expected_entities_prevention", ""))
    management = split_terms(query.get("expected_entities_management", ""))
    topics = split_terms(query.get("expected_entities_topic", ""))

    matches = {
        "disease": field_matches(disease, meta_row.get("related_disease", ""), meta_row.get("keywords", ""), meta_row.get("title", "")),
        "species": field_matches(species, meta_row.get("related_taxon", ""), meta_row.get("keywords", ""), meta_row.get("title", "")),
        "location": field_matches(locations, meta_row.get("related_location", ""), meta_row.get("keywords", ""), meta_row.get("title", "")),
        "mode": field_matches(modes, meta_row.get("production_mode", ""), meta_row.get("keywords", ""), meta_row.get("title", "")),
        "prevention": field_matches(prevention, meta_row.get("keywords", ""), meta_row.get("title", ""), meta_row.get("note", "")),
        "management": field_matches(management, meta_row.get("keywords", ""), meta_row.get("title", ""), meta_row.get("note", "")),
        "topic": field_matches(topics, meta_row.get("keywords", ""), meta_row.get("title", ""), meta_row.get("note", "")),
    }
    score = (
        3.0 * bool(matches["disease"])
        + 2.5 * bool(matches["species"])
        + 2.5 * bool(matches["location"])
        + 2.0 * bool(matches["mode"])
        + 1.8 * bool(matches["prevention"])
        + 1.6 * bool(matches["management"])
        + 1.4 * bool(matches["topic"])
    )
    query_tokens = [tok for tok in normalize(get_query_text(query)).split() if len(tok) >= 4]
    meta_norm = normalize(metadata_text(meta_row))
    overlap = sum(1 for tok in set(query_tokens) if tok in meta_norm)
    score += min(overlap, 6) * 0.25
    return score, matches


def label_from_matches(query: dict[str, Any], score: float, matches: dict[str, list[str]]) -> int:
    group = str(query.get("query_group", ""))
    has = {key: bool(value) for key, value in matches.items()}
    if group == "disease-specific":
        if has["disease"] and (has["species"] or has["location"] or has["mode"] or score >= 4.0):
            return 2
        if has["disease"] or score >= 3.0:
            return 1
    elif group == "species-location":
        if has["species"] and has["location"]:
            return 2
        if (has["species"] and (has["mode"] or has["topic"] or score >= 3.5)) or has["location"]:
            return 1
    elif group == "local":
        if has["location"] and (has["species"] or has["disease"] or has["mode"] or has["management"] or has["topic"]):
            return 2
        if has["location"] or score >= 3.0:
            return 1
    elif group == "hatchery-production-mode":
        if has["mode"] and (has["species"] or has["disease"] or has["prevention"] or has["management"]):
            return 2
        if has["mode"] or (has["species"] and score >= 3.0):
            return 1
    elif group == "biosecurity-management":
        if (has["prevention"] or has["management"]) and (has["disease"] or has["species"] or has["mode"] or has["topic"] or score >= 3.0):
            return 2
        if has["prevention"] or has["management"] or has["topic"] or score >= 3.0:
            return 1
    else:
        if (has["topic"] or has["mode"]) and (has["species"] or has["location"] or has["disease"] or score >= 4.0):
            return 2
        if has["topic"] or has["mode"] or has["species"] or has["disease"] or score >= 3.0:
            return 1
    return 0


def label_text(label: int) -> str:
    if label == 2:
        return "very_relevant"
    if label == 1:
        return "partially_relevant"
    return "not_relevant"


def matches_to_reason(score: float, matches: dict[str, list[str]], source: str) -> str:
    parts = []
    for key, values in matches.items():
        if values:
            parts.append(f"{key}={'; '.join(values[:4])}")
    if not parts:
        parts.append("no strong metadata entity match")
    return f"{source}; metadata_score={score:.2f}; " + " | ".join(parts)


def generate_judgments(
    query_rows: list[dict[str, Any]],
    result_rows: dict[str, list[dict[str, Any]]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    metadata_df = load_full_metadata(str(METADATA_PATH)).fillna("")
    meta_by_doc = {str(row["doc_id"]): row.to_dict() for _, row in metadata_df.iterrows()}
    title_by_doc = {doc_id: str(row.get("title", "")) for doc_id, row in meta_by_doc.items()}
    core_judgments = {(row["query_id"], row["doc_id"]): row for row in read_csv_rows(CORE_JUDGMENTS)}
    core_query_ids = {str(row["query_id"]) for row in read_csv_rows(CORE_QUERY_SET)}

    result_pool: dict[str, set[str]] = defaultdict(set)
    for rows in result_rows.values():
        for row in rows:
            result_pool[str(row["query_id"])].add(str(row["doc_id"]))

    judgment_rows: list[dict[str, Any]] = []
    weak_queries: list[str] = []
    query_map = {str(row["query_id"]): row for row in query_rows}

    for query in query_rows:
        qid = str(query["query_id"])
        scored_metadata: list[tuple[str, float, dict[str, list[str]]]] = []
        for doc_id, meta_row in meta_by_doc.items():
            score, matches = metadata_match_score(query, meta_row)
            if score > 0:
                scored_metadata.append((doc_id, score, matches))
        scored_metadata.sort(key=lambda item: item[1], reverse=True)

        pool = set(result_pool.get(qid, set()))
        pool.update(doc_id for doc_id, score, _ in scored_metadata[:12] if score >= 2.0)

        query_positive_count = 0
        existing_positive_count = 0
        for doc_id in sorted(pool):
            core_key = (qid, doc_id)
            if core_key in core_judgments:
                source = core_judgments[core_key]
                label = int(float(source["relevance_label"]))
                query_positive_count += int(label > 0)
                judgment_rows.append(
                    {
                        "query_id": qid,
                        "query_text": get_query_text(query),
                        "query_group": query.get("query_group", ""),
                        "query_family": query.get("query_family", ""),
                        "doc_id": doc_id,
                        "title": title_by_doc.get(doc_id, source.get("title", "")),
                        "relevance_label": label,
                        "relevance_label_text": source.get("relevance_label_text", label_text(label)),
                        "judgment_reason": "Copied from core relevance judgments.",
                        "judged_using_fields": source.get("judged_using_fields", "core_judgment"),
                    }
                )
                continue

            if qid in core_query_ids:
                label = 0
                score = 0.0
                matches = {key: [] for key in ["disease", "species", "location", "mode", "prevention", "management", "topic"]}
                source_text = "Core query extra candidate treated as non-relevant unless judged in core"
            else:
                meta_row = meta_by_doc.get(doc_id, {})
                score, matches = metadata_match_score(query, meta_row)
                label = label_from_matches(query, score, matches)
                source_text = "Generated from multi-source candidate pool and metadata fields"
                query_positive_count += int(label > 0)
                existing_positive_count += int(label > 0)

            judgment_rows.append(
                {
                    "query_id": qid,
                    "query_text": get_query_text(query),
                    "query_group": query.get("query_group", ""),
                    "query_family": query.get("query_family", ""),
                    "doc_id": doc_id,
                    "title": title_by_doc.get(doc_id, ""),
                    "relevance_label": label,
                    "relevance_label_text": label_text(label),
                    "judgment_reason": matches_to_reason(score, matches, source_text),
                    "judged_using_fields": "title;related_disease;related_taxon;related_location;production_mode;keywords;retrieval_pool",
                }
            )

        if query_positive_count == 0:
            for doc_id, score, matches in scored_metadata[:5]:
                if doc_id in pool:
                    continue
                label = 1 if existing_positive_count == 0 else 0
                if label > 0:
                    query_positive_count += 1
                judgment_rows.append(
                    {
                        "query_id": qid,
                        "query_text": get_query_text(query),
                        "query_group": query.get("query_group", ""),
                        "query_family": query.get("query_family", ""),
                        "doc_id": doc_id,
                        "title": title_by_doc.get(doc_id, ""),
                        "relevance_label": label,
                        "relevance_label_text": label_text(label),
                        "judgment_reason": matches_to_reason(score, matches, "Metadata fallback candidate; manual review recommended"),
                        "judged_using_fields": "title;related_disease;related_taxon;related_location;production_mode;keywords",
                    }
                )
                if query_positive_count > 0:
                    break
        if query_positive_count == 0:
            weak_queries.append(qid)

    # Deduplicate while preserving the highest label if the same query-doc is reached twice.
    dedup: dict[tuple[str, str], dict[str, Any]] = {}
    for row in judgment_rows:
        key = (str(row["query_id"]), str(row["doc_id"]))
        prev = dedup.get(key)
        if prev is None or int(row["relevance_label"]) > int(prev["relevance_label"]):
            dedup[key] = row
    out = sorted(dedup.values(), key=lambda row: (str(row["query_id"]), -int(row["relevance_label"]), str(row["doc_id"])))

    labels = defaultdict(int)
    by_group = defaultdict(lambda: {"n_queries": 0, "n_judgments": 0, "n_label_2": 0, "n_label_1": 0, "n_label_0": 0})
    for row in out:
        labels[int(row["relevance_label"])] += 1
        group = str(query_map[str(row["query_id"])]["query_group"])
        by_group[group]["n_judgments"] += 1
        by_group[group][f"n_label_{int(row['relevance_label'])}"] += 1
    for query in query_rows:
        by_group[str(query["query_group"])]["n_queries"] += 1

    audit = {
        "total_queries": len(query_rows),
        "total_judgments": len(out),
        "label_distribution": dict(sorted(labels.items())),
        "by_group": dict(sorted(by_group.items())),
        "queries_without_relevant_docs": weak_queries,
    }
    return out, audit


def rankings_from_rows(rows: list[dict[str, Any]]) -> dict[str, list[str]]:
    by_query: dict[str, list[tuple[int, str]]] = defaultdict(list)
    for row in rows:
        by_query[str(row["query_id"])].append((int(float(row["rank"])), str(row["doc_id"])))
    return {qid: [doc_id for _rank, doc_id in sorted(items)] for qid, items in by_query.items()}


def load_judgment_labels() -> tuple[dict[tuple[str, str], int], dict[str, list[int]]]:
    judgments: dict[tuple[str, str], int] = {}
    labels_by_query: dict[str, list[int]] = defaultdict(list)
    for row in read_csv_rows(EXT_JUDGMENTS):
        qid = str(row["query_id"])
        doc_id = str(row["doc_id"])
        label = int(float(row["relevance_label"]))
        judgments[(qid, doc_id)] = label
        labels_by_query[qid].append(label)
    return judgments, dict(labels_by_query)


def gain(label: int) -> float:
    return float((2 ** max(int(label), 0)) - 1)


def dcg(labels: list[int], k: int) -> float:
    padded = labels + [0] * max(0, k - len(labels))
    return sum(gain(padded[i]) / math.log2(i + 2) for i in range(k))


def ndcg_at(labels: list[int], ideal: list[int], k: int) -> float:
    ideal_dcg = dcg(ideal, k)
    actual = dcg(labels, k)
    if ideal_dcg <= 0:
        return 1.0 if actual <= 0 else 0.0
    return actual / ideal_dcg


def average_precision(binary: list[bool], total_relevant: int) -> float:
    if total_relevant <= 0:
        return math.nan
    hits = 0
    precision_sum = 0.0
    for index, is_relevant in enumerate(binary, start=1):
        if is_relevant:
            hits += 1
            precision_sum += hits / float(index)
    return precision_sum / float(total_relevant)


def compute_query_metrics(
    ranked_docs: list[str],
    qid: str,
    judgments: dict[tuple[str, str], int],
    labels: list[int],
) -> dict[str, float]:
    grades = [judgments.get((qid, doc_id), 0) for doc_id in ranked_docs]
    binary = [grade > 0 for grade in grades]
    total_relevant = sum(1 for label in labels if label > 0)
    ideal = sorted(labels, reverse=True)

    def p_at(k: int) -> float:
        return sum(binary[:k]) / float(k)

    def recall_at(k: int) -> float:
        return math.nan if total_relevant <= 0 else sum(binary[:k]) / float(total_relevant)

    rr = 0.0
    for index, ok in enumerate(binary, start=1):
        if ok:
            rr = 1.0 / float(index)
            break
    return {
        "p_at_1": p_at(1),
        "p_at_3": p_at(3),
        "p_at_5": p_at(5),
        "recall_at_5": recall_at(5),
        "recall_at_10": recall_at(10),
        "mrr": rr,
        "ndcg_at_5": ndcg_at(grades, ideal, 5),
        "ndcg_at_10": ndcg_at(grades, ideal, 10),
        "map": average_precision(binary, total_relevant),
    }


def mean_metric(rows: list[dict[str, Any]], metric: str) -> float:
    values = []
    for row in rows:
        value = row.get(metric)
        if isinstance(value, float) and math.isnan(value):
            continue
        values.append(float(value))
    return statistics.mean(values) if values else math.nan


def compute_metrics(
    query_rows: list[dict[str, Any]],
    result_rows: dict[str, list[dict[str, Any]]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    judgments, labels_by_query = load_judgment_labels()
    by_query_rows: list[dict[str, Any]] = []
    for method, rows in result_rows.items():
        rankings = rankings_from_rows(rows)
        for query in query_rows:
            qid = str(query["query_id"])
            metrics = compute_query_metrics(rankings.get(qid, []), qid, judgments, labels_by_query.get(qid, []))
            by_query_rows.append(
                {
                    "baseline_name": method,
                    "query_id": qid,
                    "query_text": get_query_text(query),
                    "query_group": query.get("query_group", ""),
                    **metrics,
                }
            )

    summary_rows = []
    for method in result_rows:
        rows = [row for row in by_query_rows if row["baseline_name"] == method]
        summary = {"baseline_name": method, "num_queries": len(rows)}
        for metric in METRIC_COLUMNS[2:]:
            summary[metric] = mean_metric(rows, metric)
        summary_rows.append(summary)

    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in by_query_rows:
        grouped[(str(row["baseline_name"]), str(row["query_group"]))].append(row)
    group_rows = []
    for (method, group), rows in sorted(grouped.items()):
        item = {"baseline_name": method, "query_group": group, "num_queries": len(rows)}
        for metric in BY_GROUP_COLUMNS[3:]:
            item[metric] = mean_metric(rows, metric)
        group_rows.append(item)
    return summary_rows, by_query_rows, group_rows


def fmt(value: Any) -> str:
    try:
        if isinstance(value, float) and math.isnan(value):
            return ""
        return f"{float(value):.4f}"
    except Exception:
        return str(value)


def write_judgment_audit(query_rows: list[dict[str, Any]], audit: dict[str, Any]) -> None:
    lines = [
        "# Extended Query Judgment Audit",
        "",
        f"- Generated at: {datetime.now(timezone.utc).isoformat()}",
        f"- Number of extended queries: {audit['total_queries']}",
        f"- Number of judgments: {audit['total_judgments']}",
        f"- Queries without relevant docs: {len(audit['queries_without_relevant_docs'])}",
        "",
        "## Label distribution",
        "",
        "| label | count |",
        "| ---: | ---: |",
    ]
    for label, count in sorted(audit["label_distribution"].items()):
        lines.append(f"| {label} | {count} |")
    lines.extend(["", "## Query group distribution", "", "| query_group | n_queries | n_judgments | n_label_2 | n_label_1 | n_label_0 |", "| --- | ---: | ---: | ---: | ---: | ---: |"])
    for group, row in audit["by_group"].items():
        lines.append(
            f"| {group} | {row['n_queries']} | {row['n_judgments']} | {row['n_label_2']} | {row['n_label_1']} | {row['n_label_0']} |"
        )
    lines.extend(["", "## Manual review warnings", ""])
    if audit["queries_without_relevant_docs"]:
        for qid in audit["queries_without_relevant_docs"]:
            lines.append(f"- `{qid}` has no relevant document after automatic judging and should be reviewed.")
    else:
        lines.append("- No query is missing relevant documents in the generated judgment file.")
    lines.extend(
        [
            "",
            "## Method note",
            "",
            "Judgments were generated from a pooled set of lexical, vector, vector_metadata, ontology_sparql, hybrid, hybrid_candidate_fusion results plus metadata-matched candidate documents. Core query labels were copied from the core judgment file; extra unjudged core candidates were treated as non-relevant. New query labels use metadata evidence from title, related disease, related taxon, related location, production mode and keywords. Manual review is still recommended before using this as the sole official evaluation set.",
            "",
        ]
    )
    JUDGMENT_AUDIT.write_text("\n".join(lines), encoding="utf-8")


def wilcoxon_report(by_query_rows: list[dict[str, Any]]) -> tuple[str, dict[str, Any]]:
    try:
        from scipy.stats import wilcoxon
    except Exception as exc:
        return f"Wilcoxon was not run because scipy is unavailable: {exc}", {}

    rows_by = {(row["baseline_name"], row["query_id"]): row for row in by_query_rows}
    qids = sorted({row["query_id"] for row in by_query_rows})
    out: dict[str, Any] = {}
    lines = ["| metric | statistic | p_value |", "| --- | ---: | ---: |"]
    for metric in ["p_at_1", "mrr", "ndcg_at_10"]:
        hybrid_values = [float(rows_by[("hybrid", qid)][metric]) for qid in qids]
        vm_values = [float(rows_by[("vector_metadata", qid)][metric]) for qid in qids]
        diffs = [h - v for h, v in zip(hybrid_values, vm_values)]
        if all(abs(diff) <= 1e-12 for diff in diffs):
            stat = 0.0
            p_value = 1.0
        else:
            res = wilcoxon(hybrid_values, vm_values, zero_method="wilcox", alternative="two-sided")
            stat = float(res.statistic)
            p_value = float(res.pvalue)
        out[metric] = {"statistic": stat, "p_value": p_value}
        lines.append(f"| {metric} | {fmt(stat)} | {fmt(p_value)} |")
    return "\n".join(lines), out


def write_eval_report(
    query_rows: list[dict[str, Any]],
    audit: dict[str, Any],
    summary_rows: list[dict[str, Any]],
    by_query_rows: list[dict[str, Any]],
    group_rows: list[dict[str, Any]],
) -> None:
    summary_by_method = {row["baseline_name"]: row for row in summary_rows}
    group_lookup: dict[tuple[str, str], dict[str, Any]] = {
        (row["baseline_name"], row["query_group"]): row for row in group_rows
    }
    group_counts = pd.DataFrame(query_rows)["query_group"].value_counts().sort_index().to_dict()
    methods = ["lexical", "vector", "vector_metadata", "ontology_sparql", "hybrid", "hybrid_candidate_fusion"]
    wilcoxon_md, wilcoxon_data = wilcoxon_report(by_query_rows)

    best_method = max(methods, key=lambda method: float(summary_by_method[method]["ndcg_at_10"]))
    candidate_delta = (
        float(summary_by_method["hybrid_candidate_fusion"]["ndcg_at_10"])
        - float(summary_by_method["hybrid"]["ndcg_at_10"])
    )
    recommendation = (
        "A. Có thể đưa vào Chương 4 như `Đánh giá mở rộng trên query set extended`, nhưng vẫn nên ghi chú judgments cần manual review."
        if len(audit["queries_without_relevant_docs"]) == 0 and best_method in {"hybrid", "hybrid_candidate_fusion"}
        else "B. Nên đưa vào phụ lục hoặc mục thảo luận như stress-test mở rộng cho đến khi judgments được review thủ công."
    )

    lines = [
        "# Extended Query Evaluation Report",
        "",
        "## Purpose",
        "",
        "Mục tiêu là mở rộng query set từ 28 core queries lên khoảng 90-100 queries để kiểm tra độ ổn định của các baseline trên tập truy vấn lớn hơn.",
        "",
        "## Scope and caution",
        "",
        "- Đây là evaluation extension, không thay thế core evaluation final ngay.",
        "- Core evaluation 28 queries vẫn là snapshot chính nếu báo cáo chưa thay hoàn toàn.",
        "- Extended judgments được tạo theo quy trình có kiểm soát dựa trên metadata và candidate pooling, nhưng vẫn cần manual review nếu dùng làm kết luận chính thức.",
        "",
        "## Extended query set",
        "",
        "| query_group | n_queries |",
        "| --- | ---: |",
    ]
    for group, count in group_counts.items():
        lines.append(f"| {group} | {count} |")

    lines.extend(["", "## Judgment statistics", "", "| label | count |", "| ---: | ---: |"])
    for label, count in sorted(audit["label_distribution"].items()):
        lines.append(f"| {label} | {count} |")
    lines.extend(["", "| query_group | n_queries | n_judgments | n_label_2 | n_label_1 |", "| --- | ---: | ---: | ---: | ---: |"])
    for group, row in audit["by_group"].items():
        lines.append(f"| {group} | {row['n_queries']} | {row['n_judgments']} | {row['n_label_2']} | {row['n_label_1']} |")

    lines.extend(
        [
            "",
            "## Metrics summary",
            "",
            "| method | P@1 | P@5 | Recall@5 | Recall@10 | MRR | nDCG@5 | nDCG@10 | MAP |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for method in methods:
        row = summary_by_method[method]
        lines.append(
            f"| {method} | {fmt(row['p_at_1'])} | {fmt(row['p_at_5'])} | {fmt(row['recall_at_5'])} | "
            f"{fmt(row['recall_at_10'])} | {fmt(row['mrr'])} | {fmt(row['ndcg_at_5'])} | "
            f"{fmt(row['ndcg_at_10'])} | {fmt(row['map'])} |"
        )

    lines.extend(
        [
            "",
            "## Comparison with core evaluation",
            "",
            f"- Best overall method on extended nDCG@10: `{best_method}`.",
            "- Hybrid remains a strong baseline, but the ranking should be interpreted cautiously because the extended judgments are generated automatically from metadata/candidate pools.",
            "- Vector_metadata remains close to hybrid on several precision metrics but loses KG/intent evidence used by hybrid.",
            "- Ontology_sparql is useful when entities are explicit, but can be weaker for broad/generic information needs.",
            f"- Candidate fusion nDCG@10 delta vs hybrid: {fmt(candidate_delta)}.",
            "",
            "## Group-level analysis",
            "",
            "| query_group | best_method | best_nDCG@10 | hybrid_nDCG@10 | vector_metadata_nDCG@10 | candidate_fusion_nDCG@10 | interpretation |",
            "| --- | --- | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for group in sorted(group_counts):
        best = max(methods, key=lambda method: float(group_lookup[(method, group)]["ndcg_at_10"]))
        best_ndcg = float(group_lookup[(best, group)]["ndcg_at_10"])
        hybrid_ndcg = float(group_lookup[("hybrid", group)]["ndcg_at_10"])
        vm_ndcg = float(group_lookup[("vector_metadata", group)]["ndcg_at_10"])
        cf_ndcg = float(group_lookup[("hybrid_candidate_fusion", group)]["ndcg_at_10"])
        if best == "hybrid_candidate_fusion":
            interp = "candidate fusion benefits this group by expanding candidate coverage"
        elif best == "hybrid":
            interp = "hybrid scoring remains strongest"
        elif best == "ontology_sparql":
            interp = "explicit KG/entity matching is useful"
        else:
            interp = f"{best} is strongest; inspect candidate noise and metadata coverage"
        lines.append(f"| {group} | {best} | {fmt(best_ndcg)} | {fmt(hybrid_ndcg)} | {fmt(vm_ndcg)} | {fmt(cf_ndcg)} | {interp} |")

    lines.extend(
        [
            "",
            "## Statistical check",
            "",
            "Wilcoxon signed-rank test for hybrid vs vector_metadata on per-query metrics:",
            "",
            wilcoxon_md,
            "",
            "## Limitations",
            "",
            "- Extended relevance judgments cần manual review thêm.",
            "- Một số query có thể còn judgment pool chưa đầy đủ dù đã dùng nhiều nguồn candidate.",
            "- Extended set giúp tăng độ phủ đánh giá nhưng chưa thay thế hoàn toàn đánh giá core nếu chưa được giảng viên hoặc đánh giá viên kiểm chứng.",
            "",
            "## Recommendation for report",
            "",
            recommendation,
            "",
            "## Outputs",
            "",
            f"- `{EXT_QUERY_SET.relative_to(PROJECT_ROOT)}`",
            f"- `{EXT_JUDGMENTS.relative_to(PROJECT_ROOT)}`",
            *[f"- `{path.relative_to(PROJECT_ROOT)}`" for path in RESULT_FILES.values()],
            f"- `{SUMMARY_METRICS.relative_to(PROJECT_ROOT)}`",
            f"- `{BY_QUERY_METRICS.relative_to(PROJECT_ROOT)}`",
            f"- `{BY_GROUP_METRICS.relative_to(PROJECT_ROOT)}`",
            f"- `{JUDGMENT_AUDIT.relative_to(PROJECT_ROOT)}`",
            f"- `{EVAL_REPORT.relative_to(PROJECT_ROOT)}`",
            "",
            "<!-- wilcoxon_json: " + json.dumps(wilcoxon_data, ensure_ascii=False) + " -->",
        ]
    )
    EVAL_REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    query_rows = make_extended_query_set()
    write_csv(EXT_QUERY_SET, query_rows, QUERY_COLUMNS)
    print(f"[OK] Wrote {EXT_QUERY_SET.relative_to(PROJECT_ROOT)} ({len(query_rows)} queries)")

    result_rows = run_baselines(query_rows)
    print("[OK] Wrote extended baseline result CSVs")

    judgment_rows, audit = generate_judgments(query_rows, result_rows)
    write_csv(EXT_JUDGMENTS, judgment_rows, JUDGMENT_COLUMNS)
    write_judgment_audit(query_rows, audit)
    print(f"[OK] Wrote {EXT_JUDGMENTS.relative_to(PROJECT_ROOT)} ({len(judgment_rows)} judgments)")

    summary_rows, by_query_rows, group_rows = compute_metrics(query_rows, result_rows)
    write_csv(SUMMARY_METRICS, summary_rows, METRIC_COLUMNS)
    write_csv(BY_QUERY_METRICS, by_query_rows, BY_QUERY_COLUMNS)
    write_csv(BY_GROUP_METRICS, group_rows, BY_GROUP_COLUMNS)
    write_eval_report(query_rows, audit, summary_rows, by_query_rows, group_rows)
    print("[OK] Wrote extended metrics and reports")


if __name__ == "__main__":
    main()
