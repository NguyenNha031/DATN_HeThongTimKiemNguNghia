# KG sync and verification report for 138-doc corpus

## Executive summary

| metric | value |
| --- | --- |
| status | PASS |
| metadata docs | 138 |
| KG document nodes | 138 |
| mapped docs | 138 |
| unmapped docs | 0 |
| stale KG docs | 0 |
| triple count before/after | 1324 -> 1528 |
| KNQG_002 present/facts | True / taxon=1, disease=1, location=2, mode=1 |
| RIA3_002/RIA3_003 absent | True / True |
| reasoner status | completed; consistent=True; unsat=0 |
| competency questions | 10/10 correct; partial=0; incorrect=0 |
| can proceed to core baselines? | YES |

Không chạy baseline, metrics hoặc latency trong bước này.

## Backup summary

| file | size_bytes | triples | sha256 |
| --- | ---: | ---: | --- |
| `data/ontology/archive/taxon_enriched_facts_v2_before_138docs_sync_20260531_131532.owl` | 185160 | 1324 | `966cc034e8c9a8420a5288f046705df1385758343aaaf25064ac9ed3c0764079` |
| `data/ontology/taxon_enriched_facts_v2.owl.bak_20260531_131548` | 185160 | 1324 | `966cc034e8c9a8420a5288f046705df1385758343aaaf25064ac9ed3c0764079` |
| `data/ontology/archive/taxon_enriched_facts_v2_before_138docs_mode_patch_20260531_132312.owl` | 214394 | 1514 | `19d7035916b08994fc9959cbf176a4fea61af3628a6098a86b2dba582801af7a` |
| `data/ontology/taxon_enriched_facts_v2.owl` | 216645 | 1528 | `d4b71fa9cddf131bdcc2b0a0eed04d84cb688f4a6f86ac30dee3f03826ce2c5d` |

## Sync details

| item | value |
| --- | --- |
| script/function used | `sync_metadata_to_owl.py` + stale document cleanup + production mode coverage patch |
| ontology input/output | `data/ontology/taxon_enriched_facts_v2.owl` |
| document nodes created by sync | 30 |
| document nodes updated by sync | 108 |
| stale document nodes removed | 2 (`RIA3_002`, `RIA3_003`) |
| production mode patch | 11 docs, 14 triples |
| runtime source after sync | facts_v2 / `data\ontology\taxon_enriched_facts_v2.owl` |
| final triple count | 1528 |

## Mapping audit

| metric | value |
| --- | --- |
| metadata_docs | 138 |
| kg_docs | 138 |
| mapped_docs | 138 |
| unmapped_docs | 0 |
| stale_kg_docs | 0 |
| metadata_missing_in_kg | 0 |
| runtime_doc_id_mappings | 138 |

## Fact coverage

| fact type | docs | ratio |
| --- | ---: | ---: |
| aboutTaxon | 130 | 0.942 |
| aboutDisease | 78 | 0.565 |
| aboutLocation | 78 | 0.565 |
| documentProductionMode | 138 | 1.000 |
| at least 1 core fact | 138 | 1.000 |
| all 4 core fact types | 29 | 0.210 |
| zero core facts | 0 | 0.000 |

### New docs fact coverage

| metric | value |
| --- | ---: |
| new docs checked | 30 |
| aboutTaxon docs | 24 |
| aboutDisease docs | 10 |
| aboutLocation docs | 30 |
| documentProductionMode docs | 30 |
| all 4 core fact types | 10 |
| zero core facts | 0 |

## KNQG_002 check

| fact | value |
| --- | --- |
| KG node exists | True |
| aboutTaxon | Tom_hum_bong |
| aboutDisease | MilkyDisease |
| aboutLocation | Ven_bien_Khanh_Hoa; Vietnam |
| documentProductionMode | Generic_CoastalAquaculture |
| mentions |  |

## Removed docs check

| doc_id | in metadata | in KG active docs |
| --- | --- | --- |
| RIA3_002 | False | False |
| RIA3_003 | False | False |

## Runtime verification

| metric | value |
| --- | --- |
| ontology_file_loaded | `data\ontology\taxon_enriched_facts_v2.owl` |
| total_metadata_docs | 138 |
| total_document_nodes_in_kg | 138 |
| mapped_doc_count | 138 |
| unmapped_doc_count | 0 |
| global_top5_docs_mapped_to_kg | 20 |
| global_top5_docs_with_nonzero_kg_score | 13 |
| global_top5_docs_with_kg_explanation | 13 |
| any_query_all_zero_kg | False |

## Reasoner consistency

| metric | value |
| --- | --- |
| status | completed |
| reasoner | owlready2_hermit |
| consistent | True |
| unsatisfiable_classes | 0 |
| elapsed_seconds | 3.1454 |

## Competency questions

| metric | value |
| --- | ---: |
| total | 10 |
| correct | 10 |
| partial | 0 |
| incorrect | 0 |
| accuracy_like_ratio | 1.0 |

## Problems / warnings

| severity | scope | item | issue | suggestion |
| --- | --- | --- | --- | --- |
| INFO | fact coverage | all docs | Không có document nào thiếu toàn bộ core KG facts |  |
| WARNING | fact coverage | 109 docs | Không phải mọi tài liệu đều có đủ cả 4 fact type; nhiều tài liệu không disease/location-specific | Xem kg_sync_138docs_fact_coverage.csv |
| INFO | mapping raw terms | 339 | Một số raw terms trong metadata không map trực tiếp; coverage cấp document đã đủ tối thiểu và priority runtime không thiếu fact | Xem kg_sync_138docs_mapping_report_raw.csv |
| INFO | reasoner fallback | owlready2_pellet | Pellet attempt lỗi Java class version nhưng owlready2_hermit hoàn tất và consistent=True | Không blocker |

## Next step recommendation

Có thể chuyển sang bước rerun core baselines/hybrid search/metrics/latency cho corpus 138 tài liệu. Trước khi chạy, nên backup `outputs/`, `data/eval/metrics/`, `data/eval/results/` và snapshot report hiện tại.

## Output files

- `outputs/kg_sync_138docs_report.md`
- `outputs/kg_sync_138docs_summary.csv`
- `outputs/kg_sync_138docs_mapping_audit.csv`
- `outputs/kg_sync_138docs_mapping_report_raw.csv`
- `outputs/kg_sync_138docs_fact_coverage.csv`
- `outputs/kg_sync_138docs_fact_coverage.json`
- `outputs/kg_sync_138docs_production_mode_patch.csv`
- `outputs/kg_runtime_verification_138docs.json`
- `outputs/kg_runtime_verification_138docs.md`
- `outputs/ontology_reasoner_consistency_138docs.json`
- `outputs/ontology_reasoner_consistency_138docs.md`
- `outputs/competency_questions_138docs_results.csv`
- `outputs/competency_questions_138docs_summary.json`
