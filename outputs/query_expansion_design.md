# Ontology-based Query Expansion Design

## Purpose

Mục tiêu là sử dụng ontology/KG và metadata để mở rộng truy vấn bằng alias, quan hệ disease-pathogen/symptom/prevention/treatment, taxon names và location hierarchy nhằm cải thiện candidate recall. Đây là prototype/design, không thay thế hybrid final.

## Motivation

- Hybrid hiện tại vẫn phụ thuộc vào candidate pool ban đầu.
- Disease/pathogen bridge còn có thể yếu nếu query dùng disease nhưng tài liệu nhấn mạnh pathogen.
- Location hierarchy và alias địa phương như Khánh Hòa/Khanh Hoa/ĐBSCL ảnh hưởng entity linking.
- Candidate fusion cho thấy mở rộng candidate pool có tiềm năng tăng Recall@10/MAP.
- KG diagnostic cho thấy direct facts và relation evidence đã đóng góp vào reranking.

## Expansion types

| Expansion type | Source | Example | Expected benefit | Risk |
| --- | --- | --- | --- | --- |
| disease alias | SKOS/metadata | WSSV -> white spot syndrome virus | Cross-language/entity recall | Alias ambiguity |
| disease to pathogen | causedBy | AHPND -> Vibrio parahaemolyticus | Bridge disease-pathogen documents | Pathogen too broad |
| disease to symptom | hasSymptom | disease -> clinical signs | Recover symptom-focused docs | Symptom not disease-specific |
| disease to prevention/treatment | recommendedPrevention/Treatment | AHPND -> biosecurity | Management document recall | Query drift to generic management |
| taxon alias/scientific name | SKOS/metadata | whiteleg shrimp -> Penaeus vannamei | Common/scientific name bridge | Generic shrimp over-expansion |
| location alias/hierarchy | metadata/KG | Khánh Hòa -> Vạn Ninh/Cam Ranh | Local document recall | Parent location too broad |
| production mode alias | metadata/KG | hatchery -> trại giống | Mode-sensitive retrieval | Mixing hatchery/grow-out/capture |

## Examples

| original_query | detected_entity | expansion_type | expansion_terms | expected_effect |
| --- | --- | --- | --- | --- |
| AHPND shrimp disease | AHPND | disease_alias | acute hepatopancreatic necrosis disease; EMS; AHPNS | Improve matching when documents use full disease name or EMS/AHPNS wording instead of AHPND. |
| AHPND shrimp disease | AHPND | disease_to_pathogen | Vibrio parahaemolyticus; Vibrio; bacterial pathogen | Bridge disease queries to pathogen-focused documents. |
| AHPND shrimp disease prevention | AHPND | disease_to_prevention | biosecurity; disease prevention; disease control; surveillance | Retrieve management/prevention manuals for AHPND-oriented queries. |
| WSSV shrimp | WSSV | disease_alias | white spot syndrome virus; white spot disease; bệnh đốm trắng | Improve recall for Vietnamese and English WSSV variants. |
| bệnh đốm trắng ở tôm nuôi | WSSV | disease_to_prevention | PCR; LAMP-PCR; biofloc; chế phẩm sinh học; biosecurity | Connect WSSV query to prevention/diagnostic documents. |
| infectious myonecrosis | IMNV | disease_alias | infectious myonecrosis virus; IMN; hoại tử cơ truyền nhiễm | Improve cross-language matching for IMNV/IMN queries. |
| EHP trên tôm | EHP | disease_alias | Enterocytozoon hepatopenaei; hepatopancreatic microsporidiosis; HPM; vi bào tử trùng ga... | Recover EHP documents using scientific pathogen/disease names. |
| vibriosis shrimp hatchery | vibriosis | disease_to_pathogen | Vibrio parahaemolyticus; Vibrio harveyi; Vibrio campbellii; Vibrio alginolyticus | Bridge disease query to pathogen-specific hatchery studies. |
| whiteleg shrimp hatchery | whiteleg shrimp | taxon_scientific_name | Penaeus vannamei; Litopenaeus vannamei; tôm thẻ chân trắng; Pacific whiteleg shrimp | Improve matching between common names and scientific/Vietnamese names. |
| black tiger shrimp hatchery India | black tiger shrimp | taxon_scientific_name | Penaeus monodon; tôm sú; tiger shrimp | Connect black tiger shrimp wording with Penaeus monodon hatchery manuals. |
| lobster Khanh Hoa | lobster | taxon_alias | tôm hùm; spiny lobster; Panulirus ornatus; tôm hùm xanh | Improve matching for Vietnamese local lobster planning/monitoring documents. |
| shrimp disease prevention | shrimp | taxon_common_name | tôm; prawns and shrimps; crustaceans; Penaeus | Recover documents using broad crustacean/shrimp terminology. |

## How it could be integrated

1. Query rewriting before vector retrieval: tạo expanded query text nhưng giới hạn số term và trọng số.
2. Candidate expansion only: dùng query expansion để tăng candidate pool, sau đó rerank bằng hybrid hiện có.
3. KG seed generation: dùng entity và relation expansion như một nguồn seed tương tự `hybrid_candidate_fusion`.

## Safety and guardrails

- Chỉ dùng expansion có source rõ: SKOS/ontology relation/metadata field.
- Không tự động assert fact mới vào ontology.
- Không mở rộng quá rộng gây query drift.
- Disease-specific query phải giữ disease intent chính.
- Location query phải tránh parent location quá rộng nếu query yêu cầu địa phương hẹp.
- Production mode phải tránh trộn hatchery/grow-out/capture nếu intent hẹp.
- Cần đánh giá metric riêng trước khi đưa vào hybrid final.

## Relation to current experiments

- Candidate fusion cho thấy mở rộng candidate pool có thể tăng Recall@10/MAP.
- KG diagnostic cho thấy direct facts và relation evidence đã có đóng góp.
- Query expansion là hướng tiếp theo để tăng recall và entity coverage trước bước reranking.

## Example coverage

| expansion_type | n_examples |
| --- | ---: |
| disease_alias | 22 |
| disease_to_pathogen | 10 |
| disease_to_prevention | 11 |
| disease_to_symptom | 7 |
| disease_to_treatment | 6 |
| location_alias | 20 |
| location_parent | 13 |
| production_mode_alias | 12 |
| taxon_alias | 20 |
| taxon_common_name | 1 |
| taxon_scientific_name | 2 |
| topic_alias | 4 |

## Limitations

- Mới là prototype/design, chưa thay thế hybrid final.
- Cần manual review expansion rules.
- Cần đánh giá riêng nếu dùng trong runtime.
- Một số expansion từ metadata là alias/candidate hints, không phải ontology assertion.

## Report-ready Vietnamese paragraph

Trong tương lai, hệ thống có thể bổ sung ontology-based query expansion để tăng độ phủ candidate trước khi reranking. Cụ thể, truy vấn về bệnh có thể được mở rộng sang pathogen, triệu chứng, biện pháp phòng trị; truy vấn về loài có thể bổ sung tên khoa học, tên thường gọi và tên tiếng Việt; truy vấn địa phương có thể dùng alias hoặc vùng liên quan từ metadata/KG. Cơ chế này cần được kiểm soát bằng guardrail để tránh query drift, đặc biệt với truy vấn disease-specific hoặc local hẹp. Vì vậy, query expansion nên được xem là hướng mở rộng/future work hoặc thí nghiệm candidate generation, chưa phải thành phần final của hybrid search.

## Outputs

- `outputs\query_expansion_examples.csv`
- `outputs\query_expansion_design.md`
- `outputs\figures\fig_query_expansion_examples.png`