# Project Overview

This project focuses on ontology enrichment, metadata normalization, and hybrid search for domain-specific queries. The system integrates vector search, hybrid retrieval, and knowledge graph (KG) runtime verification.

## Project Structure

- **data/**: Contains evaluation datasets, metadata, and ontology files.
- **outputs/**: Stores generated reports and verification results.
- **vector_store/**: Contains FAISS vector indices.
- **scripts**: Python scripts for various tasks such as vector search, hybrid search, and KG runtime verification.

## Requirements

- Python 3.8+
- Required libraries: `pandas`, `numpy`, `sentence-transformers`, `faiss-cpu`, `rdflib`
- Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```

## How to Run

### 1. Build Vector Store

Run the following command to build the FAISS vector store:

```bash
python vector_search.py
```

### 2. Run Hybrid Search

Execute hybrid search with:

```bash
python hybrid_search.py
```

### 3. Verify KG Runtime

Verify the knowledge graph runtime:

```bash
python verify_kg_runtime.py
```

### 4. Run Baseline Retrieval

Run baseline retrieval on the core query set:

```bash
python run_core_baselines.py
```

### 5. Compute Metrics

Compute metrics for the core query set:

```bash
python data/eval/metrics/compute_core_metrics.py
```

## Outputs

- **Vector Store**: Stored in `vector_store/`
- **Reports**: Generated in `outputs/`
- **Metrics**: Saved in `data/eval/metrics/`

## Notes

- Ensure all paths are relative to the project directory.
- Do not include sensitive information (e.g., API keys) in the final submission.

---

For further details, refer to the individual script comments.
