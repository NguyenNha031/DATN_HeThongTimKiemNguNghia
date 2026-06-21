# Extended Query Judgment Audit

- Generated at: 2026-05-27T03:15:54.316609+00:00
- Number of extended queries: 96
- Number of judgments: 2727
- Queries without relevant docs: 0

## Label distribution

| label | count |
| ---: | ---: |
| 0 | 1197 |
| 1 | 850 |
| 2 | 680 |

## Query group distribution

| query_group | n_queries | n_judgments | n_label_2 | n_label_1 | n_label_0 |
| --- | ---: | ---: | ---: | ---: | ---: |
| biosecurity-management | 16 | 439 | 85 | 119 | 235 |
| disease-specific | 16 | 431 | 155 | 119 | 157 |
| generic-mixed | 16 | 429 | 212 | 176 | 41 |
| hatchery-production-mode | 16 | 499 | 149 | 176 | 174 |
| local | 16 | 469 | 33 | 155 | 281 |
| species-location | 16 | 460 | 46 | 105 | 309 |

## Manual review warnings

- No query is missing relevant documents in the generated judgment file.

## Method note

Judgments were generated from a pooled set of lexical, vector, vector_metadata, ontology_sparql, hybrid, hybrid_candidate_fusion results plus metadata-matched candidate documents. Core query labels were copied from the core judgment file; extra unjudged core candidates were treated as non-relevant. New query labels use metadata evidence from title, related disease, related taxon, related location, production mode and keywords. Manual review is still recommended before using this as the sole official evaluation set.
