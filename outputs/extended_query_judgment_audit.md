# Extended Query Judgment Audit

- Generated at: 2026-05-31T09:01:55.488095+00:00
- Number of extended queries: 96
- Number of judgments: 2730
- Queries without relevant docs: 0

## Label distribution

| label | count |
| ---: | ---: |
| 0 | 1114 |
| 1 | 880 |
| 2 | 736 |

## Query group distribution

| query_group | n_queries | n_judgments | n_label_2 | n_label_1 | n_label_0 |
| --- | ---: | ---: | ---: | ---: | ---: |
| biosecurity-management | 16 | 452 | 83 | 129 | 240 |
| disease-specific | 16 | 435 | 161 | 113 | 161 |
| generic-mixed | 16 | 439 | 223 | 192 | 24 |
| hatchery-production-mode | 16 | 499 | 147 | 176 | 176 |
| local | 16 | 433 | 67 | 137 | 229 |
| species-location | 16 | 472 | 55 | 133 | 284 |

## Manual review warnings

- No query is missing relevant documents in the generated judgment file.

## Method note

Judgments were generated from a pooled set of lexical, vector, vector_metadata, ontology_sparql, hybrid, hybrid_candidate_fusion results plus metadata-matched candidate documents. Core query labels were copied from the core judgment file; extra unjudged core candidates were treated as non-relevant. New query labels use metadata evidence from title, related disease, related taxon, related location, production mode and keywords. Manual review is still recommended before using this as the sole official evaluation set.
