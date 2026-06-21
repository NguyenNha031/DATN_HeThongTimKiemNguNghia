# Wilcoxon signed-rank test: hybrid vs vector_metadata

**Objective:** Compare per-query stability improvements of `hybrid` vs `vector_metadata` on core queries.\n
**Inputs used:**
- data/eval/final_query_set_core.csv
- data/eval/relevance_judgments_core.csv
- data/eval/results/baseline_vector_metadata_core.csv
- data/eval/results/baseline_hybrid_core.csv

**Metrics tested:** P@1, MRR, nDCG@10, P@5, Recall@5, nDCG@5

**Results:**

|metric|n_queries|mean_hybrid|mean_vector_metadata|mean_diff|median_diff|num_hybrid_better|num_equal|num_vector_metadata_better|wilcoxon_statistic|p_value|significant_at_0_05|effect_direction|note|
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|P@1|28|0.8214285714285714|0.6428571428571429|0.17857142857142858|0.0|5|23|0|0.0|0.025347318677468252|True|hybrid>vector_metadata||
|MRR|28|0.875|0.7452380952380953|0.12976190476190477|0.0|6|21|1|2.0|0.04215345023570544|True|hybrid>vector_metadata||
|nDCG@10|28|0.7109812351773269|0.6013594879961613|0.10962174718116557|0.0|11|13|4|13.0|0.007598223082063245|True|hybrid>vector_metadata||
|P@5|28|0.39285714285714285|0.37142857142857144|0.021428571428571432|0.0|5|20|3|9.0|0.1956677425436415|False|hybrid>vector_metadata||
|Recall@5|28|0.48613945578231293|0.4590136054421769|0.027125850340136048|0.0|5|20|3|10.0|0.2620327985527309|False|hybrid>vector_metadata||
|nDCG@5|28|0.6645143121603682|0.553576012771043|0.1109382993893252|0.0|9|15|4|13.0|0.02312980249735946|True|hybrid>vector_metadata||

**Interpretation (cautious):**
- P@1: hybrid better on 5 queries; vector_metadata better on 0 queries; p=0.025347318677468252
- MRR: hybrid better on 6 queries; vector_metadata better on 1 queries; p=0.04215345023570544
- nDCG@10: hybrid better on 11 queries; vector_metadata better on 4 queries; p=0.007598223082063245
- P@5: hybrid better on 5 queries; vector_metadata better on 3 queries; p=0.1956677425436415
- Recall@5: hybrid better on 5 queries; vector_metadata better on 3 queries; p=0.2620327985527309
- nDCG@5: hybrid better on 9 queries; vector_metadata better on 4 queries; p=0.02312980249735946

**Limitations:** 28 core queries; results only apply to this set; statistical test requires paired per-query scores; absence of scipy prevents running Wilcoxon.
