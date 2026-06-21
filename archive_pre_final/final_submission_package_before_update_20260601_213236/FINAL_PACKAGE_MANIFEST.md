# Final Submission Package Manifest

Generated at: `2026-05-27T22:33:28`
Final package directory: `final_submission_package/`

## 1. Summary

- Source files copied: **230**
- Total package files including manifests: **232**
- Total package size including manifests: **479.11 MB**
- Missing required files: **1**
- Copy conflicts: **0**
- Skipped optional/blocked entries: **5**
- This package is a clean final submission copy for instructor review.
- No source files were deleted, moved, renamed, edited, or regenerated.
- No experiment was rerun.

## 2. Safety Confirmations

- `archive_pre_final/` copied: **False**
- Cache/bytecode entries found in package: **0**
- `vector_store_backup_round*` directories copied: **False**
- `outputs/archive/`, `data/metadata/archive/`, and `data/ontology/archive/` were not included by the explicit copy list.

## 3. Missing Files

| group | source_path | status | reason |
|---|---|---|---|
| metrics | data/eval/metrics/baseline_metrics_by_query.csv | missing | Source path does not exist. |

## 4. Skipped Files/Groups

| group | source_path | status | reason |
|---|---|---|---|
| root/config | requirements.txt | skipped_optional_missing | Source path does not exist. |
| root/config | README.txt | skipped_optional_missing | Source path does not exist. |
| root/config | environment.yml | skipped_optional_missing | Source path does not exist. |
| root/config | pyproject.toml | skipped_optional_missing | Source path does not exist. |
| root/config | setup.py | skipped_optional_missing | Source path does not exist. |

## 5. Copy Conflicts

No copy conflicts.

## 6. Copied Files By Group

### root/runtime

| source_path | dest_path | size_bytes |
|---|---|---|
| app_streamlit.py | app_streamlit.py | 23890 |
| hybrid_search.py | hybrid_search.py | 62348 |
| kg_runtime.py | kg_runtime.py | 33931 |
| vector_search.py | vector_search.py | 8624 |
| run_core_baselines.py | run_core_baselines.py | 26269 |
| measure_core_baseline_latency.py | measure_core_baseline_latency.py | 9022 |
| run_wilcoxon_significance_test.py | run_wilcoxon_significance_test.py | 14551 |
| evaluate_competency_questions.py | evaluate_competency_questions.py | 10792 |
| verify_ontology_quality.py | verify_ontology_quality.py | 15245 |
| verify_ontology_reasoner_consistency.py | verify_ontology_reasoner_consistency.py | 18133 |
| generate_error_analysis_core.py | generate_error_analysis_core.py | 10660 |
| generate_evaluation_layers_summary.py | generate_evaluation_layers_summary.py | 19879 |
| analyze_query_understanding_profiles.py | analyze_query_understanding_profiles.py | 20895 |

### root/config

| source_path | dest_path | size_bytes |
|---|---|---|
| README.md | README.md | 1781 |

### Streamlit demo

| source_path | dest_path | size_bytes |
|---|---|---|
| .streamlit/config.toml | .streamlit/config.toml | 155 |

### ontology

| source_path | dest_path | size_bytes |
|---|---|---|
| data/ontology/taxon_enriched_facts_v2.owl | data/ontology/taxon_enriched_facts_v2.owl | 185160 |
| data/ontology/taxon_enriched_facts.owl | data/ontology/taxon_enriched_facts.owl | 142693 |
| data/ontology/taxon_enriched_aliases.owl | data/ontology/taxon_enriched_aliases.owl | 142280 |
| data/ontology/taxon_enriched.owl | data/ontology/taxon_enriched.owl | 141708 |
| data/ontology/taxon.owl | data/ontology/taxon.owl | 155078 |
| data/ontology/mapping_report.csv | data/ontology/mapping_report.csv | 135182 |

### metadata

| source_path | dest_path | size_bytes |
|---|---|---|
| data/metadata/document_metadata_cleaned.xlsx | data/metadata/document_metadata_cleaned.xlsx | 41497 |
| data/metadata/document_metadata.xlsx | data/metadata/document_metadata.xlsx | 21611 |

### raw_docs

| source_path | dest_path | size_bytes |
|---|---|---|
| data/raw_docs/BIOLOGY_001_biology13100758.pdf | data/raw_docs/BIOLOGY_001_biology13100758.pdf | 3656901 |
| data/raw_docs/FAO_001_cb2119en.pdf | data/raw_docs/FAO_001_cb2119en.pdf | 2837382 |
| data/raw_docs/FAO_002_a1152e.pdf | data/raw_docs/FAO_002_a1152e.pdf | 3581648 |
| data/raw_docs/FAO_003_ca2976en.pdf | data/raw_docs/FAO_003_ca2976en.pdf | 6691426 |
| data/raw_docs/FAO_004_cc6858en.pdf | data/raw_docs/FAO_004_cc6858en.pdf | 34677269 |
| data/raw_docs/FAO_005_y5040e.pdf | data/raw_docs/FAO_005_y5040e.pdf | 392844 |
| data/raw_docs/FAO_006_bt131e.pdf | data/raw_docs/FAO_006_bt131e.pdf | 2438802 |
| data/raw_docs/FAO_007_cd8164en.pdf | data/raw_docs/FAO_007_cd8164en.pdf | 1235572 |
| data/raw_docs/FAO_008_cb8926en.pdf | data/raw_docs/FAO_008_cb8926en.pdf | 3368163 |
| data/raw_docs/FAO_009_y1679e.pdf | data/raw_docs/FAO_009_y1679e.pdf | 3475127 |
| data/raw_docs/FAO_010_ca6052en.pdf | data/raw_docs/FAO_010_ca6052en.pdf | 2857806 |
| data/raw_docs/FAO_011_ad824e.pdf | data/raw_docs/FAO_011_ad824e.pdf | 238076 |
| data/raw_docs/FAO_012_ad505e.pdf | data/raw_docs/FAO_012_ad505e.pdf | 672185 |
| data/raw_docs/FAO_013_y5325e.pdf | data/raw_docs/FAO_013_y5325e.pdf | 538879 |
| data/raw_docs/FAO_014_cd8658en.pdf | data/raw_docs/FAO_014_cd8658en.pdf | 409149 |
| data/raw_docs/FAO_015_t0411e.pdf | data/raw_docs/FAO_015_t0411e.pdf | 534703 |
| data/raw_docs/FAO_016_cd7559en.pdf | data/raw_docs/FAO_016_cd7559en.pdf | 2637352 |
| data/raw_docs/FAO_017_ca7588en.pdf | data/raw_docs/FAO_017_ca7588en.pdf | 34994958 |
| data/raw_docs/FAO_018_t1623e.pdf | data/raw_docs/FAO_018_t1623e.pdf | 870732 |
| data/raw_docs/FAO_019_i0490e.pdf | data/raw_docs/FAO_019_i0490e.pdf | 4521107 |
| data/raw_docs/FAO_020_i2571e.pdf | data/raw_docs/FAO_020_i2571e.pdf | 4048265 |
| data/raw_docs/FAO_021_cd8667en.pdf | data/raw_docs/FAO_021_cd8667en.pdf | 1976309 |
| data/raw_docs/FAO_022_i1750e.pdf | data/raw_docs/FAO_022_i1750e.pdf | 1804971 |
| data/raw_docs/FAO_023_i0970e.pdf | data/raw_docs/FAO_023_i0970e.pdf | 7120652 |
| data/raw_docs/FAO_024_u3100e.pdf | data/raw_docs/FAO_024_u3100e.pdf | 335212 |
| data/raw_docs/FAO_025_a0366e.pdf | data/raw_docs/FAO_025_a0366e.pdf | 1078825 |
| data/raw_docs/FAO_026_br813e.pdf | data/raw_docs/FAO_026_br813e.pdf | 366409 |
| data/raw_docs/FAO_027_cd6476en.pdf | data/raw_docs/FAO_027_cd6476en.pdf | 1950755 |
| data/raw_docs/FAO_028_i3569e.pdf | data/raw_docs/FAO_028_i3569e.pdf | 2583818 |
| data/raw_docs/FAO_029_i9705en.pdf | data/raw_docs/FAO_029_i9705en.pdf | 16659485 |
| data/raw_docs/FAO_031_cd8563en.pdf | data/raw_docs/FAO_031_cd8563en.pdf | 9202961 |
| data/raw_docs/FAO_032_cd8633en.pdf | data/raw_docs/FAO_032_cd8633en.pdf | 430307 |
| data/raw_docs/FAO_033_cc6625en.pdf | data/raw_docs/FAO_033_cc6625en.pdf | 5923373 |
| data/raw_docs/FAO_034_ca2705en.pdf | data/raw_docs/FAO_034_ca2705en.pdf | 555647 |
| data/raw_docs/FAO_035_w3594e.pdf | data/raw_docs/FAO_035_w3594e.pdf | 526773 |
| data/raw_docs/FAO_036_i1137e.pdf | data/raw_docs/FAO_036_i1137e.pdf | 1713567 |
| data/raw_docs/FAO_037_na265en.pdf | data/raw_docs/FAO_037_na265en.pdf | 683985 |
| data/raw_docs/FAO_038_ca6702en.pdf | data/raw_docs/FAO_038_ca6702en.pdf | 861870 |
| data/raw_docs/FAO_039_ad893e.pdf | data/raw_docs/FAO_039_ad893e.pdf | 633135 |
| data/raw_docs/FAO_040_i8064en.pdf | data/raw_docs/FAO_040_i8064en.pdf | 3778749 |
| data/raw_docs/FAO_041_cd3785en.pdf | data/raw_docs/FAO_041_cd3785en.pdf | 2206169 |
| data/raw_docs/FAO_042_biosecurity_philippines.pdf | data/raw_docs/FAO_042_biosecurity_philippines.pdf | 4655063 |
| data/raw_docs/FAO_042_i3720e.pdf | data/raw_docs/FAO_042_i3720e.pdf | 8839521 |
| data/raw_docs/FAO_043_boosting_biosecurity_peru.pdf | data/raw_docs/FAO_043_boosting_biosecurity_peru.pdf | 614195 |
| data/raw_docs/FAO_044_i2734e03i.pdf | data/raw_docs/FAO_044_i2734e03i.pdf | 4882582 |
| data/raw_docs/FAO_045_ca6163en.pdf | data/raw_docs/FAO_045_ca6163en.pdf | 520499 |
| data/raw_docs/IJMS_001_ijms26178478.pdf | data/raw_docs/IJMS_001_ijms26178478.pdf | 4165432 |
| data/raw_docs/NACA_001_1737869839.pdf | data/raw_docs/NACA_001_1737869839.pdf | 56312263 |
| data/raw_docs/NACA_002_1749824700.pdf | data/raw_docs/NACA_002_1749824700.pdf | 1162852 |
| data/raw_docs/NACA_003_1494554353.pdf | data/raw_docs/NACA_003_1494554353.pdf | 2425728 |
| data/raw_docs/PLOS_001_pone.0091930.pdf | data/raw_docs/PLOS_001_pone.0091930.pdf | 1783090 |
| data/raw_docs/PMC_001_PMC10820212.pdf | data/raw_docs/PMC_001_PMC10820212.pdf | 825771 |
| data/raw_docs/PMC_002_PMC6963587.pdf | data/raw_docs/PMC_002_PMC6963587.pdf | 198189 |
| data/raw_docs/PMC_003_PMC11657822.pdf | data/raw_docs/PMC_003_PMC11657822.pdf | 3666087 |
| data/raw_docs/PMC_004_PMC12128546.pdf | data/raw_docs/PMC_004_PMC12128546.pdf | 3692281 |
| data/raw_docs/PMC_005_PMC12552485.pdf | data/raw_docs/PMC_005_PMC12552485.pdf | 2695289 |
| data/raw_docs/PMC_006_PMC8042889.pdf | data/raw_docs/PMC_006_PMC8042889.pdf | 2332238 |
| data/raw_docs/PMC_007_PMC8067269.pdf | data/raw_docs/PMC_007_PMC8067269.pdf | 2962901 |
| data/raw_docs/PMC_008_PMC11611405.pdf | data/raw_docs/PMC_008_PMC11611405.pdf | 3250959 |
| data/raw_docs/PMC_009_PMC12030750.pdf | data/raw_docs/PMC_009_PMC12030750.pdf | 2350238 |
| data/raw_docs/PMC_010_PMC7409025.pdf | data/raw_docs/PMC_010_PMC7409025.pdf | 1592624 |
| data/raw_docs/PMC_011_PMC5742833.pdf | data/raw_docs/PMC_011_PMC5742833.pdf | 4873671 |
| data/raw_docs/PMC_012_PMC7223513.pdf | data/raw_docs/PMC_012_PMC7223513.pdf | 518367 |
| data/raw_docs/PMC_013_PMC12825151.pdf | data/raw_docs/PMC_013_PMC12825151.pdf | 1384168 |
| data/raw_docs/PMC_014_PMC9531857.pdf | data/raw_docs/PMC_014_PMC9531857.pdf | 1479014 |
| data/raw_docs/PMC_015_PMC12006376.pdf | data/raw_docs/PMC_015_PMC12006376.pdf | 2713899 |
| data/raw_docs/PMC_016_PMC4815145.pdf | data/raw_docs/PMC_016_PMC4815145.pdf | 1733261 |
| data/raw_docs/PMC_017_PMC11223889.pdf | data/raw_docs/PMC_017_PMC11223889.pdf | 4207087 |
| data/raw_docs/PMC_018_PMC12008197.pdf | data/raw_docs/PMC_018_PMC12008197.pdf | 3776158 |
| data/raw_docs/PMC_019_PMC6797625.pdf | data/raw_docs/PMC_019_PMC6797625.pdf | 1688443 |
| data/raw_docs/PMC_020_PMC10701378.pdf | data/raw_docs/PMC_020_PMC10701378.pdf | 5632033 |
| data/raw_docs/PMC_021_PMC9427843.pdf | data/raw_docs/PMC_021_PMC9427843.pdf | 7470050 |
| data/raw_docs/PMC_022_PMC11081493.pdf | data/raw_docs/PMC_022_PMC11081493.pdf | 2595651 |
| data/raw_docs/PMC_023_PMC10229113.pdf | data/raw_docs/PMC_023_PMC10229113.pdf | 1442350 |
| data/raw_docs/PMC_024_PMC9139878.pdf | data/raw_docs/PMC_024_PMC9139878.pdf | 1883191 |
| data/raw_docs/PMC_025_PMC4510448.pdf | data/raw_docs/PMC_025_PMC4510448.pdf | 227195 |
| data/raw_docs/PMC_026_PMC11205452.pdf | data/raw_docs/PMC_026_PMC11205452.pdf | 3812393 |
| data/raw_docs/PMC_027_PMC12745081.pdf | data/raw_docs/PMC_027_PMC12745081.pdf | 1780141 |
| data/raw_docs/PMC_028_PMC5603525.pdf | data/raw_docs/PMC_028_PMC5603525.pdf | 4179909 |
| data/raw_docs/PMC_029_PMC6955853.pdf | data/raw_docs/PMC_029_PMC6955853.pdf | 17528305 |
| data/raw_docs/PMC_030_PMC10476614.pdf | data/raw_docs/PMC_030_PMC10476614.pdf | 2727978 |
| data/raw_docs/PMC_031_PMC91383.pdf | data/raw_docs/PMC_031_PMC91383.pdf | 129405 |
| data/raw_docs/PMC_032_PMC12435696.pdf | data/raw_docs/PMC_032_PMC12435696.pdf | 2374633 |
| data/raw_docs/PMC_033_PMC8339124.pdf | data/raw_docs/PMC_033_PMC8339124.pdf | 3148392 |
| data/raw_docs/PMC_034_PMC10141217.pdf | data/raw_docs/PMC_034_PMC10141217.pdf | 22251326 |
| data/raw_docs/PMC_035_PMC11861540.pdf | data/raw_docs/PMC_035_PMC11861540.pdf | 12708855 |
| data/raw_docs/PMC_036_PMC9125206.pdf | data/raw_docs/PMC_036_PMC9125206.pdf | 5285910 |
| data/raw_docs/RIA3_001_quy_hoach_nuoi_tom_hum_2030.pdf | data/raw_docs/RIA3_001_quy_hoach_nuoi_tom_hum_2030.pdf | 2533358 |
| data/raw_docs/RIA3_002_TBKQ_QTDX_PhuYen_KhanhHoa_17112023.pdf | data/raw_docs/RIA3_002_TBKQ_QTDX_PhuYen_KhanhHoa_17112023.pdf | 1670425 |
| data/raw_docs/RIA3_003_TBKQ_QTMT_DOT14_T6_2025.pdf | data/raw_docs/RIA3_003_TBKQ_QTMT_DOT14_T6_2025.pdf | 1843283 |
| data/raw_docs/SEAFDEC_001_DharAK2021.pdf | data/raw_docs/SEAFDEC_001_DharAK2021.pdf | 1734398 |
| data/raw_docs/SEAFDEC_002_Wong2016.pdf | data/raw_docs/SEAFDEC_002_Wong2016.pdf | 230067 |
| data/raw_docs/SEAFDEC_003_Yuasa2016.pdf | data/raw_docs/SEAFDEC_003_Yuasa2016.pdf | 252706 |
| data/raw_docs/SEAFDEC_004_sp15-3.pdf | data/raw_docs/SEAFDEC_004_sp15-3.pdf | 449077 |
| data/raw_docs/SEAFDEC_005_WahSLP2016.pdf | data/raw_docs/SEAFDEC_005_WahSLP2016.pdf | 235457 |
| data/raw_docs/SEAFDEC_006_Apostol2016.pdf | data/raw_docs/SEAFDEC_006_Apostol2016.pdf | 435532 |
| data/raw_docs/SEAFDEC_007_Penir2019.pdf | data/raw_docs/SEAFDEC_007_Penir2019.pdf | 113485 |
| data/raw_docs/SEAFDEC_008_Putth2016.pdf | data/raw_docs/SEAFDEC_008_Putth2016.pdf | 584977 |
| data/raw_docs/SEAFDEC_009_Hastuti2016.pdf | data/raw_docs/SEAFDEC_009_Hastuti2016.pdf | 264524 |
| data/raw_docs/SEAFDEC_010_Hirono2016.pdf | data/raw_docs/SEAFDEC_010_Hirono2016.pdf | 401561 |
| data/raw_docs/SEAFDEC_011_Kua2016.pdf | data/raw_docs/SEAFDEC_011_Kua2016.pdf | 335696 |
| data/raw_docs/TB_001_NyanTawCRSDCaMau.pdf | data/raw_docs/TB_001_NyanTawCRSDCaMau.pdf | 8173752 |
| data/raw_docs/TB_002_cong_nghe_gen_va_chon_giong_tom_khang_benh.pdf | data/raw_docs/TB_002_cong_nghe_gen_va_chon_giong_tom_khang_benh.pdf | 311117 |
| data/raw_docs/TB_003_co_che_co_ban_cua_nhiem_don_le_va_dong_nhiem_DIV1_va_WSSV_o_tom_the_chan_trang.pdf | data/raw_docs/TB_003_co_che_co_ban_cua_nhiem_don_le_va_dong_nhiem_DIV1_va_WSSV_o_tom_the_chan_trang.pdf | 431191 |
| data/raw_docs/TB_004_hoai_tu_co_o_tom_the_chan_trang.pdf | data/raw_docs/TB_004_hoai_tu_co_o_tom_the_chan_trang.pdf | 227871 |
| data/raw_docs/TB_005_su_hien_dien_cua_benh_dom_trang_va_EHP_va_AHPND_tai_DBSCL_2022_2024.pdf | data/raw_docs/TB_005_su_hien_dien_cua_benh_dom_trang_va_EHP_va_AHPND_tai_DBSCL_2022_2024.pdf | 233937 |
| data/raw_docs/TB_006_hoai_tu_co_IMNV_tren_tom_va_chien_luoc_kiem_soat.pdf | data/raw_docs/TB_006_hoai_tu_co_IMNV_tren_tom_va_chien_luoc_kiem_soat.pdf | 969292 |
| data/raw_docs/TB_007_benh_dom_trang_o_tom_nuoi_va_cong_nghe_nuoi_tom_nham_phong_benh_dom_trang.pdf | data/raw_docs/TB_007_benh_dom_trang_o_tom_nuoi_va_cong_nghe_nuoi_tom_nham_phong_benh_dom_trang.pdf | 6218939 |
| data/raw_docs/TCKHTS_001.pdf | data/raw_docs/TCKHTS_001.pdf | 910982 |
| data/raw_docs/TCTS_001_024286.pdf | data/raw_docs/TCTS_001_024286.pdf | 710724 |

### vector_store

| source_path | dest_path | size_bytes |
|---|---|---|
| vector_store/chunks.index | vector_store/chunks.index | 39252525 |
| vector_store/chunks_meta.pkl | vector_store/chunks_meta.pkl | 22144185 |
| vector_store/config.pkl | vector_store/config.pkl | 90 |

### eval data

| source_path | dest_path | size_bytes |
|---|---|---|
| data/eval/final_query_set_core.csv | data/eval/final_query_set_core.csv | 8582 |
| data/eval/relevance_judgments_core.csv | data/eval/relevance_judgments_core.csv | 67133 |
| data/eval/competency_questions_core.csv | data/eval/competency_questions_core.csv | 2215 |
| data/eval/final_query_set_extended.csv | data/eval/final_query_set_extended.csv | 39613 |
| data/eval/relevance_judgments_extended.csv | data/eval/relevance_judgments_extended.csv | 1250368 |
| data/eval/final_query_set.csv | data/eval/final_query_set.csv | 16088 |

### results

| source_path | dest_path | size_bytes |
|---|---|---|
| data/eval/results/baseline_lexical_core.csv | data/eval/results/baseline_lexical_core.csv | 103963 |
| data/eval/results/baseline_vector_core.csv | data/eval/results/baseline_vector_core.csv | 113075 |
| data/eval/results/baseline_vector_metadata_core.csv | data/eval/results/baseline_vector_metadata_core.csv | 115214 |
| data/eval/results/baseline_ontology_sparql_core.csv | data/eval/results/baseline_ontology_sparql_core.csv | 105698 |
| data/eval/results/baseline_hybrid_core.csv | data/eval/results/baseline_hybrid_core.csv | 102387 |
| data/eval/results/baseline_vector_metadata_kg_no_intent_core.csv | data/eval/results/baseline_vector_metadata_kg_no_intent_core.csv | 135000 |
| data/eval/results/baseline_hybrid_candidate_fusion_core.csv | data/eval/results/baseline_hybrid_candidate_fusion_core.csv | 259666 |
| data/eval/results/kg_ablation_results_core.csv | data/eval/results/kg_ablation_results_core.csv | 569320 |
| data/eval/results/baseline_lexical_extended.csv | data/eval/results/baseline_lexical_extended.csv | 351784 |
| data/eval/results/baseline_vector_extended.csv | data/eval/results/baseline_vector_extended.csv | 385730 |
| data/eval/results/baseline_vector_metadata_extended.csv | data/eval/results/baseline_vector_metadata_extended.csv | 389358 |
| data/eval/results/baseline_ontology_sparql_extended.csv | data/eval/results/baseline_ontology_sparql_extended.csv | 359839 |
| data/eval/results/baseline_hybrid_extended.csv | data/eval/results/baseline_hybrid_extended.csv | 344465 |
| data/eval/results/baseline_hybrid_candidate_fusion_extended.csv | data/eval/results/baseline_hybrid_candidate_fusion_extended.csv | 894380 |

### metrics

| source_path | dest_path | size_bytes |
|---|---|---|
| data/eval/metrics/baseline_metrics_summary.csv | data/eval/metrics/baseline_metrics_summary.csv | 1267 |
| data/eval/metrics/baseline_metrics_per_query.csv | data/eval/metrics/baseline_metrics_per_query.csv | 31548 |
| data/eval/metrics/baseline_metrics_by_group.csv | data/eval/metrics/baseline_metrics_by_group.csv | 2744 |
| data/eval/metrics/baseline_latency_summary.csv | data/eval/metrics/baseline_latency_summary.csv | 2575 |
| data/eval/metrics/baseline_metrics_summary_plus.csv | data/eval/metrics/baseline_metrics_summary_plus.csv | 1217 |
| data/eval/metrics/baseline_metrics_by_query_plus.csv | data/eval/metrics/baseline_metrics_by_query_plus.csv | 31956 |
| data/eval/metrics/baseline_metrics_by_group_plus.csv | data/eval/metrics/baseline_metrics_by_group_plus.csv | 5336 |
| data/eval/metrics/hybrid_candidate_fusion_metrics_summary.csv | data/eval/metrics/hybrid_candidate_fusion_metrics_summary.csv | 650 |
| data/eval/metrics/hybrid_candidate_fusion_metrics_by_query.csv | data/eval/metrics/hybrid_candidate_fusion_metrics_by_query.csv | 16639 |
| data/eval/metrics/hybrid_candidate_fusion_metrics_by_group.csv | data/eval/metrics/hybrid_candidate_fusion_metrics_by_group.csv | 2841 |
| data/eval/metrics/baseline_metrics_summary_extended.csv | data/eval/metrics/baseline_metrics_summary_extended.csv | 1189 |
| data/eval/metrics/baseline_metrics_by_query_extended.csv | data/eval/metrics/baseline_metrics_by_query_extended.csv | 114008 |
| data/eval/metrics/baseline_metrics_by_group_extended.csv | data/eval/metrics/baseline_metrics_by_group_extended.csv | 6128 |
| data/eval/metrics/kg_ablation_metrics_summary.csv | data/eval/metrics/kg_ablation_metrics_summary.csv | 999 |
| data/eval/metrics/kg_ablation_metrics_by_query.csv | data/eval/metrics/kg_ablation_metrics_by_query.csv | 27789 |
| data/eval/metrics/kg_ablation_metrics_by_group.csv | data/eval/metrics/kg_ablation_metrics_by_group.csv | 4836 |
| data/eval/metrics/compute_core_metrics.py | data/eval/metrics/compute_core_metrics.py | 14098 |

### experiments

| source_path | dest_path | size_bytes |
|---|---|---|
| experiments/run_hybrid_candidate_fusion.py | experiments/run_hybrid_candidate_fusion.py | 27908 |
| experiments/run_extended_evaluation.py | experiments/run_extended_evaluation.py | 81344 |
| experiments/compute_baseline_metrics_plus.py | experiments/compute_baseline_metrics_plus.py | 12110 |
| experiments/analyze_kg_score_components.py | experiments/analyze_kg_score_components.py | 25036 |
| experiments/run_kg_ablation.py | experiments/run_kg_ablation.py | 23839 |
| experiments/generate_query_expansion_examples.py | experiments/generate_query_expansion_examples.py | 39638 |

### outputs reports

| source_path | dest_path | size_bytes |
|---|---|---|
| outputs/hybrid_candidate_fusion_analysis.md | outputs/hybrid_candidate_fusion_analysis.md | 4255 |
| outputs/extended_query_evaluation_report.md | outputs/extended_query_evaluation_report.md | 5464 |
| outputs/extended_query_judgment_audit.md | outputs/extended_query_judgment_audit.md | 1392 |
| outputs/baseline_metrics_plus_report.md | outputs/baseline_metrics_plus_report.md | 1875 |
| outputs/kg_score_component_analysis.md | outputs/kg_score_component_analysis.md | 6222 |
| outputs/kg_ablation_analysis.md | outputs/kg_ablation_analysis.md | 4818 |
| outputs/query_expansion_design.md | outputs/query_expansion_design.md | 7330 |
| outputs/query_expansion_examples.csv | outputs/query_expansion_examples.csv | 61704 |
| outputs/kg_score_component_analysis.csv | outputs/kg_score_component_analysis.csv | 212887 |
| outputs/query_understanding_profiles.csv | outputs/query_understanding_profiles.csv | 14799 |
| outputs/query_understanding_profiles.json | outputs/query_understanding_profiles.json | 41738 |
| outputs/query_understanding_profiles.md | outputs/query_understanding_profiles.md | 9673 |
| outputs/hybrid_vs_vector_metadata_by_group.csv | outputs/hybrid_vs_vector_metadata_by_group.csv | 1059 |
| outputs/hybrid_vs_vector_metadata_by_group.md | outputs/hybrid_vs_vector_metadata_by_group.md | 1725 |
| outputs/wilcoxon_hybrid_vs_vector_metadata.csv | outputs/wilcoxon_hybrid_vs_vector_metadata.csv | 1146 |
| outputs/wilcoxon_hybrid_vs_vector_metadata.json | outputs/wilcoxon_hybrid_vs_vector_metadata.json | 3481 |
| outputs/wilcoxon_hybrid_vs_vector_metadata.md | outputs/wilcoxon_hybrid_vs_vector_metadata.md | 2285 |
| outputs/ontology_quality_check.json | outputs/ontology_quality_check.json | 3759 |
| outputs/ontology_quality_check.md | outputs/ontology_quality_check.md | 2652 |
| outputs/ontology_reasoner_consistency_check.json | outputs/ontology_reasoner_consistency_check.json | 6204 |
| outputs/ontology_reasoner_consistency_check.md | outputs/ontology_reasoner_consistency_check.md | 2807 |
| outputs/competency_questions_results.csv | outputs/competency_questions_results.csv | 22520 |
| outputs/competency_questions_summary.json | outputs/competency_questions_summary.json | 1285 |
| outputs/error_analysis_core.csv | outputs/error_analysis_core.csv | 8987 |
| outputs/error_analysis_summary.json | outputs/error_analysis_summary.json | 619 |
| outputs/evaluation_layers_summary.json | outputs/evaluation_layers_summary.json | 28227 |
| outputs/evaluation_layers_summary.md | outputs/evaluation_layers_summary.md | 8041 |
| outputs/final_score_formula_and_runtime_flow.md | outputs/final_score_formula_and_runtime_flow.md | 4268 |
| outputs/streamlit_demo_notes.md | outputs/streamlit_demo_notes.md | 1419 |
| outputs/kg_runtime_verification.json | outputs/kg_runtime_verification.json | 23455 |
| outputs/document_fact_coverage_audit.json | outputs/document_fact_coverage_audit.json | 101245 |
| outputs/final_submission_file_checklist.md | outputs/final_submission_file_checklist.md | 8973 |
| outputs/project_file_cleanup_audit.md | outputs/project_file_cleanup_audit.md | 106307 |
| outputs/project_file_archive_move_plan.md | outputs/project_file_archive_move_plan.md | 79405 |
| outputs/project_file_archive_execution_report.md | outputs/project_file_archive_execution_report.md | 37664 |
| outputs/final_package_post_archive_check.md | outputs/final_package_post_archive_check.md | 33533 |
| outputs/protected_modified_files_review.md | outputs/protected_modified_files_review.md | 3805 |

### figures

| source_path | dest_path | size_bytes |
|---|---|---|
| outputs/figures/fig_baseline_key_metrics.png | outputs/figures/fig_baseline_key_metrics.png | 190013 |
| outputs/figures/fig_quality_latency_tradeoff.png | outputs/figures/fig_quality_latency_tradeoff.png | 149441 |
| outputs/figures/fig_hybrid_vs_vector_metadata_by_group.png | outputs/figures/fig_hybrid_vs_vector_metadata_by_group.png | 165347 |
| outputs/figures/fig_ablation_key_metrics.png | outputs/figures/fig_ablation_key_metrics.png | 216020 |
| outputs/figures/fig_kg_runtime_contribution_summary.png | outputs/figures/fig_kg_runtime_contribution_summary.png | 245471 |
| outputs/figures/fig_kg_ablation_summary.png | outputs/figures/fig_kg_ablation_summary.png | 175540 |
| outputs/figures/fig_candidate_fusion_summary.png | outputs/figures/fig_candidate_fusion_summary.png | 159510 |
| outputs/figures/fig_extended_evaluation_summary.png | outputs/figures/fig_extended_evaluation_summary.png | 183330 |
| outputs/figures/fig_baseline_key_metrics.pdf | outputs/figures/fig_baseline_key_metrics.pdf | 24211 |
| outputs/figures/fig_quality_latency_tradeoff.pdf | outputs/figures/fig_quality_latency_tradeoff.pdf | 24883 |
| outputs/figures/fig_hybrid_vs_vector_metadata_by_group.pdf | outputs/figures/fig_hybrid_vs_vector_metadata_by_group.pdf | 25209 |
| outputs/figures/fig_ablation_key_metrics.pdf | outputs/figures/fig_ablation_key_metrics.pdf | 25629 |
| outputs/figures/fig_query_expansion_examples.png | outputs/figures/fig_query_expansion_examples.png | 190973 |
| outputs/figures/fig_kg_score_components.png | outputs/figures/fig_kg_score_components.png | 136658 |

## 7. Post-Copy Check

| path | exists_in_package |
|---|---|
| app_streamlit.py | True |
| .streamlit/config.toml | True |
| hybrid_search.py | True |
| kg_runtime.py | True |
| vector_search.py | True |
| data/ontology/taxon_enriched_facts_v2.owl | True |
| data/metadata/document_metadata_cleaned.xlsx | True |
| data/eval/final_query_set_core.csv | True |
| data/eval/relevance_judgments_core.csv | True |
| data/eval/metrics/baseline_metrics_summary.csv | True |
| data/eval/results/baseline_hybrid_core.csv | True |
| vector_store/chunks.index | True |
| outputs/figures/fig_baseline_key_metrics.png | True |
| outputs/figures/fig_extended_evaluation_summary.png | True |

## 8. Notes

- Raw documents were copied to preserve demo/source tracing capability.
- The final package intentionally excludes archived/deprecated outputs and vector store backups.
- Audit/check reports were included to document cleanup and post-archive verification.
- `data/eval/metrics/baseline_metrics_by_query.csv` was requested but not found; `baseline_metrics_per_query.csv` was copied because it exists and is used in the current project.
