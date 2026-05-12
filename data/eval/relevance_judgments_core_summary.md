# Tóm tắt relevance judgments — CORE

| Hạng mục | Giá trị |
|----------|---------|
| File | `data/eval/relevance_judgments_core.csv` |
| Số query có judgment | 28 / 28 |
| Tổng dòng (cặp query–doc) | 181 |
| very_relevant (2) | 58 |
| partially_relevant (1) | 63 |
| not_relevant (0) | 60 |
| Số doc xét / query (min–max–avg) | 5 – 8 – ~6.46 |

**Vòng siết (bước 2):** Mỗi query core có **ít nhất 5** judgments; query khó / dễ nhầm được nâng lên **6–8** judgments khi corpus cho phép. Bổ sung hard negative và near-miss (đặc biệt local, hatchery đa quốc gia, biosecurity vs PMP, lobster vs capture, AHPND/WSSV/pathogen). Một số lý do đã củng cố bằng `hybrid_comparison.csv` / `kg_runtime_verification.json` trong `judgment_reason` hoặc `judged_using_fields`.

Mỗi query giữ tổ hợp positive / partial / not_relevant phù hợp đánh giá top‑k; tránh chỉ toàn nhãn 2.

**Lưu ý:** Judgments chủ yếu metadata + tiêu đề/keyword + bằng chứng hybrid/KG đã ghi; chưa đối chiếu full‑text từng chunk PDF. **Chưa** chạy baseline, **chưa** tính metric (bước 3).
