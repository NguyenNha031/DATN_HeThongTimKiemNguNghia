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
|P@1|28|0.8214285714285714|0.75|0.07142857142857142|0.0|3|24|1|2.5|0.31731050786291415|False|hybrid>vector_metadata||
|MRR|28|0.8693877551020408|0.8217687074829932|0.047619047619047616|0.0|4|23|1|4.0|0.34302782731118187|False|hybrid>vector_metadata||
|nDCG@10|28|0.7222030264667223|0.6636095865403359|0.05859343992638646|0.0|9|13|6|30.0|0.08840247992639415|False|hybrid>vector_metadata||
|P@5|28|0.40714285714285714|0.39285714285714285|0.014285714285714287|0.0|4|21|3|9.0|0.3804551252503885|False|hybrid>vector_metadata||
|Recall@5|28|0.4980442176870748|0.4887755102040816|0.009268707482993192|0.0|4|21|3|13.0|0.8657723749926214|False|hybrid>vector_metadata||
|nDCG@5|28|0.669526385544799|0.6143017033355447|0.05522468220925431|0.0|9|14|5|27.0|0.10942115881922927|False|hybrid>vector_metadata||

**Interpretation (cautious):**
- P@1: hybrid better on 3 queries; vector_metadata better on 1 queries; p=0.31731050786291415
- MRR: hybrid better on 4 queries; vector_metadata better on 1 queries; p=0.34302782731118187
- nDCG@10: hybrid better on 9 queries; vector_metadata better on 6 queries; p=0.08840247992639415
- P@5: hybrid better on 4 queries; vector_metadata better on 3 queries; p=0.3804551252503885
- Recall@5: hybrid better on 4 queries; vector_metadata better on 3 queries; p=0.8657723749926214
- nDCG@5: hybrid better on 9 queries; vector_metadata better on 5 queries; p=0.10942115881922927

**Limitations:** 28 core queries; results only apply to this set; statistical test requires paired per-query scores; absence of scipy prevents running Wilcoxon.
