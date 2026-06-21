# Final Score Formula and Runtime Flow

## Purpose

This note documents the runtime scoring formula implemented in `hybrid_search.py` and the KG evidence flow implemented in `kg_runtime.py`. It is a code-based explanation only: no baseline was rerun and no metric, ontology, metadata, query set, or judgment file was modified.

## Final Score Formula

```text
final_score = vector_score + metadata_delta + kg_score + intent_adjustment
```

In `hybrid_search.py`, each vector candidate is reranked after metadata and KG evidence are computed for its document. The code reads the original vector score, computes the metadata-based delta, obtains the KG score if the document can be mapped into the KG, applies a narrow intent adjustment, and then sorts candidates by `final_score`.

## Score Components

- `vector_score`: the original similarity score returned by vector retrieval for a chunk candidate.
- `metadata_delta`: the heuristic metadata reranking delta computed from matches between detected query entities and document metadata fields such as disease, taxon/species, location, and production mode. The delta can add bonuses for matches and apply penalties for important missing evidence, depending on the query profile.
- `kg_score`: the additional KG-based score returned by `kg_runtime.score_doc_with_kg()`. It is based on direct document facts, 1-hop KG relation evidence, and contextual evidence such as pathogen, symptom, prevention, or treatment links. It may also include KG penalties when expected disease or intent evidence is missing.
- `intent_adjustment`: a final heuristic adjustment for narrow intent cases, for example when a local aquaculture query should prefer aquaculture documents over capture/market-oriented documents.

## Hybrid Search Runtime Pseudo-code

```text
normalize query
-> detect entities from local term/metadata aliases
-> initialize KG if available
-> link KG entities from ontology aliases if available
-> merge KG-linked entities into detected entities
-> retrieve vector candidates
-> optionally add extra vector candidates for narrow lobster/coastal intent
-> map each chunk candidate to its document id
-> map document id/title/file path to KG document URI if possible
-> compute metadata_delta from metadata match features
-> get KG document facts
-> compute kg_score and KG explanation from fact/relation/context evidence
-> apply intent_adjustment
-> compute final_score
-> keep the best scoring chunk per document
-> sort by final_score
-> return Top-k
```

## Runtime Principles

- The reranking logic is heuristic; it is not an automatically learned model.
- Relevance judgments are not manually adjusted by the runtime.
- The query set, metadata, ontology, judgments, baseline outputs, and metric files are not edited to make metrics look better.
- KG runtime uses fact and relation evidence to rerank and explain results.
- Runtime retrieval does not run a full OWL/SWRL reasoner.
- Reasoner consistency checking is a separate evaluation step, not part of online retrieval/reranking.

## Report-ready Paragraph

Trong pipeline hybrid search, điểm xếp hạng cuối cùng được tính theo công thức `final_score = vector_score + metadata_delta + kg_score + intent_adjustment`. `vector_score` là điểm tương đồng ban đầu từ truy hồi vector, trong khi `metadata_delta` là phần điều chỉnh heuristic dựa trên mức khớp giữa thực thể trong truy vấn và metadata tài liệu. Thành phần `kg_score` được tính ở runtime từ bằng chứng trong Knowledge Graph, bao gồm fact trực tiếp của tài liệu, quan hệ 1-hop giữa các thực thể, và một số bằng chứng ngữ cảnh như tác nhân gây bệnh, triệu chứng, phòng trị hoặc production mode. Cuối cùng, `intent_adjustment` xử lý các ý định hẹp để tránh ưu tiên sai loại tài liệu. Cơ chế này không phải mô hình học tự động và không chỉnh sửa relevance judgments, query set, metadata hay ontology để tối ưu metric; KG được dùng để rerank và giải thích dựa trên bằng chứng đã có, còn kiểm tra nhất quán bằng reasoner là một bước đánh giá riêng, không chạy trong runtime retrieval.
