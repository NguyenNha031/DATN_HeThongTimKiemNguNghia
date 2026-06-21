# Semantic Rules and English-first Label Strategy

## 1. Purpose

This document summarizes the semantic-rule strategy for the current ontology/KG retrieval snapshot. It has three purposes:

- Document the rule-like evidence already used at runtime by KG scoring, metadata reranking, and intent guardrails.
- Define an English-first label strategy suitable for an English-dominant aquaculture corpus while preserving Vietnamese, scientific, abbreviated, and common variant labels.
- Propose safe future semantic rule groups that can improve the ontology without automatically asserting weak or ambiguous facts.

This is a strategy and documentation artifact only. It does not modify the ontology, metadata, baselines, metrics, query set, relevance judgments, URI scheme, class names, property names, or individuals.

## 2. Current runtime rule-like evidence

The current system does not run a full OWL/SWRL reasoner during retrieval. Instead, it uses structured KG facts and conservative rule-like scoring in `kg_runtime.py`, metadata matching in `hybrid_search.py`, and narrow intent guardrails in the final reranking stage.

| Rule/evidence group | Runtime relation/function | Current role | Used in |
| ------------------- | ------------------------- | ------------ | ------- |
| Document-Disease evidence | `aboutDisease`; `kg_runtime.score_doc_with_kg()` | Direct disease match adds KG evidence. Current weight: `+0.25` for exact query disease against document disease fact. | `kg_score` |
| Document-Taxon evidence | `aboutTaxon`; `kg_runtime.score_doc_with_kg()` | Direct taxon match adds KG evidence. Specific taxon receives stronger evidence than generic taxon. Current weights: `+0.20`, generic `+0.06`. | `kg_score` |
| Document-Location evidence | `aboutLocation`; `kg_runtime.score_doc_with_kg()` | Direct location match adds structured local evidence. Current weight: `+0.10`. | `kg_score` |
| Document-ProductionMode evidence | `documentProductionMode`; `kg_runtime.score_doc_with_kg()` | Direct production-mode match supports hatchery/aquaculture/capture context. Current weights: `+0.10`, generic `+0.04`. | `kg_score` |
| Disease-Taxon relation evidence | `affectsTaxon`; `kg_runtime.score_doc_with_kg()` | If query disease affects a taxon and the document is about that taxon, the document receives relation evidence. Current weight: `+0.10`. | `kg_score` |
| Disease-Pathogen relation evidence | `causedBy`; `kg_runtime.get_document_facts()` and `score_doc_with_kg()` | Disease facts enrich document facts with pathogen context. A query pathogen matching document pathogen context receives evidence. Current direct relation path weight: `+0.08`; pathogen context weight: `+0.06`. | `kg_score` |
| Disease context evidence | `hasSymptom`, `recommendedPrevention`, `recommendedTreatment`; `get_document_facts()` | Disease nodes provide 1-hop context for symptoms, prevention, and treatment. Current weights: symptom `+0.04`, prevention `+0.05`, treatment `+0.05`. | `kg_score` |
| Taxon-Location relation evidence | `isFoundIn`; `score_doc_with_kg()` | If query taxon and query location match a known taxon range and the document is about the taxon, a soft relation bonus is applied. Current weight: `+0.12`. | `kg_score` |
| Disease guard / missing disease penalty | `score_doc_with_kg()` | If query contains a specific disease but document lacks disease direct/relation evidence, non-disease KG evidence is downweighted and a penalty is applied. Current penalty: `-0.18`; non-disease evidence multiplier: `0.25`. | `kg_score` |
| Generic taxon/mode handling | `score_doc_with_kg()` checks `Generic_` URI fragments | Generic entities are allowed but receive smaller weights to avoid over-ranking broad aquaculture/shrimp facts. | `kg_score` |
| Metadata disease/species/location/mode matching | `hybrid_search.compute_match_features()` and `compute_hybrid_delta()` | Matches query entities against normalized metadata fields. Disease-priority, species-priority, and generic profiles control metadata boosts and penalties. | `metadata_delta` |
| Disease-species synergy | `compute_hybrid_delta()` | Disease-priority query receives extra evidence when both disease and species match metadata. Current weight: `+0.08`. | `metadata_delta` |
| Species-location synergy | `compute_hybrid_delta()` | Species-priority query receives extra evidence when both species and location match metadata. Current weight: `+0.05`. | `metadata_delta` |
| Location parent handling | `compute_match_features()` with `LOCATION_PARENT_MAP` | A narrow location can match a parent location when direct metadata match is absent. This is a soft metadata matching rule, not an ontology assertion. | `metadata_delta` |
| Local aquaculture vs capture guard | `kg_runtime.score_doc_with_kg()` and `hybrid_search.hybrid_search()` | Narrow local aquaculture/lobster intent penalizes capture or market fisheries documents when aquaculture candidates exist. Current KG-side penalty observed: `-0.09`; late intent penalty: `-0.12`. | `kg_score` and `intent_adjustment` |
| Narrow final intent guardrails | `hybrid_search._intent_narrow_final_adjustment()` | Query/title patterns adjust a few specific cases such as Vietnam brackish disease manual, biosecurity+hatchery+vannamei, Thailand low-water-exchange, and hatchery vannamei production. | `intent_adjustment` |
| Ontology/SPARQL baseline evidence | `run_core_baselines.py` ontology baseline | SPARQL counts matches over `aboutDisease`, `aboutTaxon`, `aboutLocation`, and `documentProductionMode`, then combines this tie-break signal with KG scoring. | `ontology_sparql` baseline |

Current runtime scoring is therefore best described as knowledge-enhanced retrieval with structured KG evidence and rule-based reranking. It should not be described as full automatic logical reasoning.

## 3. Proposed semantic rule groups for future work

Future semantic rules should be implemented conservatively. A recommended approach is to use controlled Python rules or SPARQL `CONSTRUCT` queries to generate candidate facts, then validate those candidates before adding them to the ontology. SWRL can be considered later, but only with explicit validation and regression testing.

| Proposed rule group | Example rule | Safe use | Risk if over-asserted |
| ------------------- | ------------ | -------- | --------------------- |
| Disease-pathogen context | If a document is `aboutDisease AHPND`, then `Vibrio parahaemolyticus` can be used as contextual evidence for ranking. | Use as soft scoring or explanation evidence unless the source explicitly states pathogen evidence. | Incorrectly treating every AHPND document as directly about the pathogen can inflate pathogen-specific retrieval. |
| Disease-symptom context | If disease has `hasSymptom` and a document is about that disease, symptoms can support query-document explanation. | Use as weak context evidence; require explicit source evidence before asserting document-level symptom facts. | Symptom terms can be generic and may create false positives. |
| Disease-prevention/treatment context | If disease has `recommendedPrevention` or `recommendedTreatment`, disease documents can inherit weak prevention/treatment context for ranking. | Use as contextual KG evidence with low weights. | Can make treatment/prevention queries retrieve general disease documents too aggressively. |
| Taxon-location hierarchy | If `Khanh Hoa partOf Vietnam`, a query for Vietnam can softly match Khanh Hoa documents and vice versa with controlled direction. | Use parent/child location matching for soft scoring and explanation. | Country-level matches can dominate local-specific queries if weights are too high. |
| Production-mode hierarchy | If hatchery is a production context under aquaculture, hatchery documents can support aquaculture queries. | Use hierarchy-aware soft scoring; keep hatchery-specific queries stricter. | Broad aquaculture documents may outrank hatchery-specific documents. |
| Shrimp hatchery relation | Shrimp hatchery is related to shrimp aquaculture and shrimp life stages such as broodstock, larvae, and post-larvae. | Add controlled concepts for life stage and hatchery context after metadata/source validation. | Over-general life-stage rules can merge distinct biological and production contexts. |
| Document-level disease assertion | Add `Document aboutDisease X` only when metadata, title, keywords, or source text strongly support it. | Require explicit evidence from curated metadata or source document. | Weak disease mentions can become hard KG facts and distort disease-specific retrieval. |
| Document-level location assertion | Add `Document aboutLocation X` only when location evidence is explicit in metadata/title/source. | Prefer exact named locations; add parent locations only through validated hierarchy rules. | Inferring locations from institution/source alone can introduce incorrect locality. |
| Document-level production-mode assertion | Add `documentProductionMode` when production context is explicit. | Use controlled vocabulary and avoid guessing from broad title words. | Ambiguous mode labels can trigger wrong aquaculture/capture guardrails. |
| Candidate fact rejection | Reject candidate facts below confidence threshold or with conflicting evidence. | Keep candidate-fact audit files before ontology update. | Auto-asserting all candidates makes the KG less reliable and harder to debug. |

### 3.1 Disease-pathogen-symptom-prevention-treatment rules

Recommended future rules:

- If a disease node has `causedBy`, `hasSymptom`, `recommendedPrevention`, or `recommendedTreatment`, use those connected entities as contextual evidence for ranking and explanation.
- If a document is `aboutDisease AHPND`, pathogen/symptom/prevention/treatment facts should not automatically become hard document facts unless the document title, metadata, keywords, or source text explicitly supports them.
- For pathogen-centered queries such as `Vibrio parahaemolyticus`, bridge pathogen evidence to AHPND/vibriosis carefully and keep the weight lower than explicit `aboutDisease` or explicit pathogen evidence.

### 3.2 Taxon-location-production mode rules

Recommended future rules:

- Model location hierarchy explicitly, for example `Khanh Hoa partOf Vietnam`, then use it for soft scoring rather than unconditional hard expansion.
- Model production-mode hierarchy, for example hatchery as a production context under aquaculture.
- Model shrimp hatchery and life-stage terms such as broodstock, larvae, and post-larvae as controlled concepts after checking corpus evidence.
- Keep local queries strict enough that a broad country match does not outrank a specific province/district match.

### 3.3 Document-level safe rules

Recommended future rules:

- Assert `aboutDisease`, `aboutTaxon`, `aboutLocation`, and `documentProductionMode` only when evidence is explicit.
- Prefer metadata and source title/keywords for high-confidence document facts.
- Store generated candidate facts separately, review them, then assert only validated facts.
- Re-run runtime verification, competency questions, retrieval metrics, and error analysis after any ontology update.

## 4. English-first label strategy

Because the source corpus is primarily English, future ontology versions should use English as the canonical modeling language. Vietnamese terms, scientific names, abbreviations, and common variants should be retained as labels and aliases rather than replacing canonical English labels.

| Entity aspect | Recommended canonical form | Alternative labels |
| ------------- | -------------------------- | ------------------ |
| Class names | English class names, for example `Disease`, `Taxon`, `Location`, `ProductionMode`, `Document` | Vietnamese class labels may be stored as `rdfs:label` or `skos:altLabel` if needed |
| Object properties | English camelCase, for example `aboutDisease`, `aboutTaxon`, `affectsTaxon`, `causedBy`, `hasSymptom` | Vietnamese descriptions can be documentation labels, not property local names |
| Individual URI/local name | Prefer English or stable technical identifiers in future versions | Keep old URI stable unless a migration plan exists |
| `skos:prefLabel` | English canonical human-readable label | One preferred English label per language/context |
| `skos:altLabel` | Synonyms and aliases | Vietnamese names, scientific names, abbreviations, spelling variants, corpus-specific variants |
| `rdfs:label` | Human-readable fallback | Can mirror English canonical label for simple display |

Recommended examples for future normalized labels:

| Entity | Recommended labels |
| ------ | ------------------ |
| AHPND | `skos:prefLabel "acute hepatopancreatic necrosis disease"@en`; `skos:altLabel "AHPND"@en`; `skos:altLabel "acute hepatopancreatic necrosis syndrome"@en`; `skos:altLabel "benh hoai tu gan tuy cap"@vi`; `skos:altLabel "bệnh hoại tử gan tụy cấp"@vi` |
| Penaeus monodon | `skos:prefLabel "black tiger shrimp"@en`; `skos:altLabel "Penaeus monodon"@la`; `skos:altLabel "tom su"@vi`; `skos:altLabel "tôm sú"@vi` |
| Penaeus vannamei | `skos:prefLabel "whiteleg shrimp"@en`; `skos:altLabel "Penaeus vannamei"@la`; `skos:altLabel "tom the chan trang"@vi`; `skos:altLabel "tôm thẻ chân trắng"@vi` |
| Khanh Hoa | `skos:prefLabel "Khanh Hoa"@en`; `skos:altLabel "Khánh Hòa"@vi`; future relation: `partOf Vietnam` if a location hierarchy is introduced |

The current runtime already uses labels and aliases from `rdfs:label`, `skos:prefLabel`, `skos:altLabel`, `scientificName`, `diseaseCode`, and document `title` when building the KG index. However, the ontology quality check shows that only part of indexed entities have explicit `rdfs` or `skos` labels. Therefore, English-first label normalization should be treated as recommended next step, not as a completed property of the current snapshot.

## 5. Recommended safe workflow

1. Keep URI identifiers stable for the current snapshot.
2. Add or normalize labels before adding new facts.
3. Validate alias and entity linking using representative English, Vietnamese, scientific, and abbreviated query forms.
4. Generate candidate facts with controlled Python rules or SPARQL `CONSTRUCT`.
5. Review candidate facts manually or accept only high-confidence rules with clear evidence.
6. Assert validated facts into the ontology only after review.
7. Re-run runtime verification, competency questions, error analysis, and retrieval metrics.
8. Document every new rule and its expected effect on retrieval.

## 6. Thesis-ready content for later use

Snapshot hiện tại của hệ thống sử dụng ontology/KG như một tầng tri thức có cấu trúc để tăng cường truy hồi. Trong runtime, các quan hệ như `aboutDisease`, `aboutTaxon`, `aboutLocation`, `documentProductionMode`, `affectsTaxon`, `causedBy`, `hasSymptom`, `recommendedPrevention` và `recommendedTreatment` được dùng như evidence có trọng số trong quá trình reranking. Ngoài ra, hệ thống còn có một số guardrail hẹp theo intent, ví dụ xử lý truy vấn nuôi trồng địa phương hoặc truy vấn hatchery cụ thể, nhằm giảm trường hợp tài liệu rộng hoặc sai ngữ cảnh vượt lên đầu.

Tuy nhiên, snapshot này không nên được mô tả là một hệ suy luận tự động đầy đủ. Hệ thống chưa chạy SWRL/reasoner để tự động assert hàng loạt triple mới vào ontology. Phần đóng góp hiện tại phù hợp hơn với cách mô tả "knowledge-enhanced retrieval": vector search tạo candidate, metadata và KG facts cung cấp evidence có thể giải thích, sau đó các heuristic/guardrail miền hẹp được dùng để điều chỉnh thứ hạng.

Hướng phát triển hợp lý là chuẩn hóa ontology theo chiến lược English-first do corpus chủ yếu là tiếng Anh. Class, property, URI hoặc canonical label nên ưu tiên tiếng Anh hoặc định danh kỹ thuật ổn định; tiếng Việt, tên khoa học, viết tắt và biến thể phổ biến nên được lưu trong `skos:altLabel`, `skos:prefLabel` hoặc `rdfs:label`. Các semantic rules mới nên được triển khai thận trọng bằng controlled Python rules hoặc SPARQL `CONSTRUCT` có kiểm chứng, tạo candidate facts trước, review bằng evidence, rồi mới assert vào ontology.

## 7. Limitations

- This is a strategy document, not a new metric result.
- It does not prove that all proposed semantic rules are implemented.
- It does not replace ontology quality checking, competency-question evaluation, or retrieval evaluation.
- It does not run SWRL, OWL reasoning, HermiT, Pellet, or any other reasoner.
- English-first label normalization is recommended for future ontology versions; it is not claimed to be fully completed in the current snapshot.
- If future rules are implemented, retrieval metrics, competency questions, ontology quality checks, and error analysis should be re-run before reporting new conclusions.
