import os
import re
import pickle
from pathlib import Path

import faiss
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

# LIBRARY FOR FILE READING
# Install required libraries: pymupdf, python-docx, openpyxl, sentence-transformers, faiss-cpu, pandas
# Example: pip install pymupdf python-docx openpyxl sentence-transformers faiss-cpu pandas

# Configuration
# Default metadata path
_DEFAULT_METADATA_PATH = Path("data") / "metadata" / "document_metadata.xlsx"
_CLEAN_METADATA_PATH = Path("data") / "metadata" / "document_metadata_cleaned.xlsx"
# Use cleaned metadata if available, otherwise fallback to default
METADATA_PATH = str(_CLEAN_METADATA_PATH) if _CLEAN_METADATA_PATH.exists() else str(_DEFAULT_METADATA_PATH)
DOC_BASE_DIR = Path(".")
INDEX_DIR = Path("vector_store")
INDEX_DIR.mkdir(parents=True, exist_ok=True)

# Embedding model configuration
EMBED_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
CHUNK_SIZE = 800  # Number of characters per chunk
CHUNK_OVERLAP = 150  # Overlap between chunks
TOP_K = 5


# 2. ĐỌC FILE
def read_pdf(path: str) -> str:
    text_parts = []
    with fitz.open(path) as doc:
        for page in doc:
            text_parts.append(page.get_text("text"))
    return "\n".join(text_parts)


def read_docx(path: str) -> str:
    doc = DocxDocument(path)
    return "\n".join(p.text for p in doc.paragraphs)


def read_txt(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def read_document(path: str) -> str:
    ext = Path(path).suffix.lower()
    if ext == ".pdf":
        return read_pdf(path)
    if ext == ".docx":
        return read_docx(path)
    if ext == ".txt":
        return read_txt(path)
    raise ValueError(f"Unsupported file type: {ext}")


# 3. LÀM SẠCH VĂN BẢN + CHIA CHUNK
def clean_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\n+", "\n", text)
    return text.strip()


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 150) -> list[str]:
    text = clean_text(text)
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += max(1, chunk_size - overlap)
    return chunks


# 4. NẠP METADATA
def load_metadata(metadata_path: str) -> pd.DataFrame:
    path = Path(metadata_path)
    if not path.exists():
        raise FileNotFoundError(f"Metadata file not found: {metadata_path}")

    if path.suffix.lower() == ".xlsx":
        df = pd.read_excel(path)
    elif path.suffix.lower() == ".csv":
        df = pd.read_csv(path)
    else:
        raise ValueError("Metadata must be .xlsx or .csv")

    required_cols = ["doc_id", "title", "file_path"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required metadata columns: {missing}")

    return df


# 5. DỰNG BỘ DỮ LIỆU CHUNK
def build_chunks_from_metadata(df: pd.DataFrame) -> list[dict]:
    records = []

    for _, row in df.iterrows():
        doc_id = str(row.get("doc_id", "")).strip()
        title = str(row.get("title", "")).strip()
        file_path = str(row.get("file_path", "")).strip()

        if not file_path:
            print(f"[WARN] Missing file_path for doc_id={doc_id}")
            continue

        abs_path = DOC_BASE_DIR / file_path
        if not abs_path.exists():
            print(f"[WARN] File not found for doc_id={doc_id}: {abs_path}")
            continue

        try:
            raw_text = read_document(str(abs_path))
            raw_text = clean_text(raw_text)
            if not raw_text:
                print(f"[WARN] Empty text for doc_id={doc_id}")
                continue

            chunks = chunk_text(raw_text, CHUNK_SIZE, CHUNK_OVERLAP)

            for idx, chunk in enumerate(chunks):
                records.append({
                    "doc_id": doc_id,
                    "title": title,
                    "file_path": file_path,
                    "chunk_id": f"{doc_id}_chunk_{idx}",
                    "chunk_index": idx,
                    "text": chunk
                })

            print(f"[INFO] Document {doc_id}: {len(chunks)} chunks processed.")

        except Exception as e:
            print(f"[ERROR] Failed reading {doc_id}: {e}")

    return records


# 6. VECTOR HÓA (EMBEDDING) + FAISS
def build_faiss_index(records: list[dict], model_name: str):
    if not records:
        raise ValueError("No chunk records available to index.")
    model = SentenceTransformer(model_name)
    texts = [r["text"] for r in records]
    embeddings = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True
    )
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)  
    index.add(embeddings.astype("float32"))
    return model, index, embeddings


# 7. LƯU / NẠP CHỈ MỤC
def save_index(index, records, model_name):
    faiss.write_index(index, str(INDEX_DIR / "chunks.index"))
    with open(INDEX_DIR / "chunks_meta.pkl", "wb") as f:
        pickle.dump(records, f)
    with open(INDEX_DIR / "config.pkl", "wb") as f:
        pickle.dump({"model_name": model_name}, f)
    print("[INFO] Vector index saved successfully.")


def load_index():
    index_path = INDEX_DIR / "chunks.index"
    meta_path = INDEX_DIR / "chunks_meta.pkl"
    cfg_path = INDEX_DIR / "config.pkl"
    if not index_path.exists() or not meta_path.exists() or not cfg_path.exists():
        raise FileNotFoundError("Index files not found. Run build step first.")
    index = faiss.read_index(str(index_path))
    with open(meta_path, "rb") as f:
        records = pickle.load(f)
    with open(cfg_path, "rb") as f:
        cfg = pickle.load(f)
    model = SentenceTransformer(cfg["model_name"])
    return model, index, records


# 8. TÌM KIẾM
def search(query: str, model, index, records, top_k: int = 5):
    query_vec = model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True
    ).astype("float32")

    scores, indices = index.search(query_vec, top_k)

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx == -1:
            continue
        rec = records[idx].copy()
        rec["score"] = float(score)
        results.append(rec)

    return results


# 9. HIỂN THỊ KẾT QUẢ
def print_results(results: list[dict]):
    if not results:
        print("Không có kết quả.")
        return

    for rank, r in enumerate(results, start=1):
        print("=" * 100)
        print(f"Top {rank}")
        print(f"Score    : {r['score']:.4f}")
        print(f"Doc ID   : {r['doc_id']}")
        print(f"Title    : {r['title']}")
        print(f"Chunk ID : {r['chunk_id']}")
        print(f"File     : {r['file_path']}")
        print("Text:")
        print(r["text"][:1000])
        print()


# 10. HÀM MAIN / PIPELINE
def build_pipeline():
    print("[STEP] Loading metadata...")
    df = load_metadata(METADATA_PATH)

    print("[STEP] Reading documents and chunking...")
    records = build_chunks_from_metadata(df)

    print("[STEP] Building embeddings + FAISS index...")
    model, index, _ = build_faiss_index(records, EMBED_MODEL_NAME)

    print("[STEP] Saving index...")
    save_index(index, records, EMBED_MODEL_NAME)

    print("[DONE] Vector store built successfully.")


def interactive_search():
    print("[STEP] Loading vector index...")
    model, index, records = load_index()

    print("[READY] Nhập câu hỏi để tìm kiếm. Gõ 'exit' để thoát.")
    while True:
        query = input("\nCâu hỏi: ").strip()
        if query.lower() in {"exit", "quit"}:
            break

        results = search(query, model, index, records, top_k=TOP_K)
        print_results(results)


if __name__ == "__main__":
    import sys

    mode = (sys.argv[1].strip().lower() if len(sys.argv) > 1 else "search")

    if mode in {"build", "index"}:
        build_pipeline()
    elif mode in {"search", "interactive"}:
        interactive_search()
    else:
        raise ValueError("Usage: python vector_search.py [build|search]")
