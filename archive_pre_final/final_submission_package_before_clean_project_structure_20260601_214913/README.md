# Aquaculture Semantic Search - Final Submission Package

Đây là gói nộp cuối cho đề tài Aquaculture Semantic Search, được đóng gói theo snapshot final 138 tài liệu.

## Snapshot final

- Corpus: 138 documents
- Vector chunks: 28,542 chunks, 138/138 docs
- KG docs: 138/138 mapped
- Ontology runtime: `taxon_enriched_facts_v2.owl`
- Core queries: 28
- Extended queries: 96 supplementary

## Cấu trúc package

- `report/`: bản báo cáo Word/PDF nếu tìm thấy trong project root.
- `source_code/`: source code chính và các script đánh giá final/supplementary.
- `data_metadata/`: metadata, audit và phân bố topic; raw PDFs không được đóng gói trong package nhẹ.
- `ontology/`: ontology/KG runtime final và các report kiểm tra 138 docs.
- `vector_store_info/`: report vector store final; có kèm `vector_store/` nếu cần chạy demo trực tiếp.
- `evaluation/`: kết quả baseline, metric, ablation, supplementary evaluation, query set và relevance judgments.
- `figures/`: bộ hình Chương 4 final có hậu tố `*_138docs`.
- `streamlit_demo/`: app demo và các report kiểm tra/fix giao diện.
- `outputs_reports/`: ghi chú về cách phân loại các report đầu ra.

## Metric chính

Hybrid core đạt: P@1=0.8214, P@5=0.3929, Recall@10=0.6246, MRR=0.8750, nDCG@10=0.7110, MAP=0.4566.

Kiểm định Wilcoxon hybrid vs vector_metadata cho thấy khác biệt có ý nghĩa ở P@1, MRR, nDCG@5 và nDCG@10; không có ý nghĩa thống kê ở P@5 và Recall@5.

## Lưu ý diễn giải

- Candidate fusion là supplementary/extension, không thay thế Hybrid final.
- Extended evaluation là supporting evidence, không thay thế core 28 queries.
- Query expansion chưa rerun theo snapshot 138 docs, chỉ được xem là future work, không dùng như kết quả final.
- Raw PDFs are not included in this lightweight submission package due to size; metadata and paths are included.

## Chạy demo

Nếu môi trường đã cài đủ dependencies và có vector store đi kèm, chạy:

```bash
streamlit run app_streamlit.py
```

Trong package này, file demo nằm ở `streamlit_demo/app_streamlit.py`. Khi chạy từ project gốc, dùng `app_streamlit.py` ở root project.
