# Candidate Fusion Experiment Summary

## Purpose

This experiment tests whether expanding hybrid candidate generation with both vector and BM25 lexical candidates improves retrieval.
It is an exploratory `candidate_fusion_experiment`, not a replacement for the current final hybrid baseline.

## Candidate Pool Construction

- Vector pool: top 150 FAISS chunks, plus the existing lobster vector expansion when its narrow intent triggers.
- Lexical pool: top 150 BM25 chunks over normalized chunk tokens.
- Candidate union: merge by `doc_id`, retain `came_from_vector`, `came_from_lexical`, vector rank/score, and lexical rank/score.
- Re-rank: reuse the current hybrid scoring components: `vector_score + metadata_delta + kg_score + intent_adjustment`.
- Retrieval was re-run inside this experiment script because existing vector/lexical baseline CSVs store only top-10 documents, not the deeper candidate pools needed for fusion.

## Candidate Pool Statistics

- Average vector candidate docs: 32.7857
- Average lexical candidate docs: 11.1071
- Average union candidate docs: 38.4643
- Queries where union > vector-only: 26 / 28

## Metric Comparison

| baseline | P@1 | P@3 | P@5 | Recall@5 | MRR | nDCG@5 | nDCG@10 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| hybrid | 0.8214 | 0.5357 | 0.4071 | 0.4980 | 0.8694 | 0.6695 | 0.7222 |
| vector_metadata | 0.7500 | 0.5238 | 0.3929 | 0.4888 | 0.8218 | 0.6143 | 0.6636 |
| hybrid_candidate_fusion | 0.8571 | 0.5476 | 0.3857 | 0.4713 | 0.9000 | 0.6534 | 0.7252 |

## Delta vs Current Hybrid

- P@1 delta: 0.0357
- MRR delta: 0.0306
- nDCG@10 delta: 0.0030

## Query Group Comparison

| query_group | hybrid P@1 | fusion P@1 | hybrid MRR | fusion MRR | hybrid nDCG@10 | fusion nDCG@10 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| biosecurity-management | 0.8333 | 0.8333 | 0.9167 | 0.9167 | 0.7794 | 0.7794 |
| disease-specific | 0.6667 | 0.6667 | 0.7278 | 0.7278 | 0.6450 | 0.6516 |
| hatchery-production-mode | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.6891 | 0.6607 |
| local | 0.8571 | 1.0000 | 0.8776 | 1.0000 | 0.7334 | 0.7661 |
| species-location | 0.8000 | 0.8000 | 0.8667 | 0.8667 | 0.7571 | 0.7431 |

## Improved and Regressed Queries

**Largest improvements by nDCG@10**

- `LO_005` (local): delta nDCG@10=0.2291, union=25
- `SL_007` (species-location): delta nDCG@10=0.0508, union=66
- `DS_010` (disease-specific): delta nDCG@10=0.0394, union=40

**Largest regressions by nDCG@10**

- `HM_002` (hatchery-production-mode): delta nDCG@10=-0.1135, union=31
- `SL_001` (species-location): delta nDCG@10=-0.0972, union=26
- `SL_006` (species-location): delta nDCG@10=-0.0236, union=38

## Interpretation

Candidate fusion gives a mixed result: P@1, MRR, and nDCG@10 increase slightly, but P@5, Recall@5, and nDCG@5 decrease. This should not be treated as a final improvement; it is best framed as future work that needs candidate filtering, lexical-score calibration, and reranker tuning.

## Limitations

- This experiment re-runs retrieval in a separate script and writes separate outputs only.
- It does not modify `baseline_hybrid_core.csv` or any existing metric/baseline artifact.
- Candidate fusion can add useful recall, but it can also add lexical noise; the current hybrid scoring was not retuned for the larger mixed candidate pool.
- Treat this as future-work evidence unless it is validated with additional tuning, statistical testing, and error analysis.
