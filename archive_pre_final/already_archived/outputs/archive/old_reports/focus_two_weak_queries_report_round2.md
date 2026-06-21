# Báo cáo vòng 2: 2 truy vấn yếu (IMN + nuôi tôm hùm Khánh Hòa)

## 1) Phạm vi vòng 2 (đúng yêu cầu)

- **Chỉ xử lý**: (1) `infectious myonecrosis` (IMN) và (2) `nuôi tôm hùm ở Khánh Hòa`.
- **Không làm**: thêm dataset mới, refactor lớn, đổi kiến trúc pipeline, thêm thuật toán mới.
- **Mục tiêu chính**: heuristic có kiểm soát cho intent hẹp kiểu **“nuôi + địa phương cụ thể”** để tài liệu **capture/market** không vượt lên nếu có tài liệu **aquaculture/farming/local** trong candidate pool.

Artifacts vòng 2:
- `outputs/focus_two_queries_round2_before.json`
- `outputs/focus_two_queries_round2_after.json`

## 2) Infectious myonecrosis — before/after (round2)

Nguồn số liệu: `outputs/focus_two_queries_round2_before.json` vs `outputs/focus_two_queries_round2_after.json`.

| Chỉ số | Trước | Sau |
|---|---:|---:|
| **top1 vector** | `FAO_010` (0.6177) | `FAO_010` (0.6177) |
| **top1 hybrid** | `FAO_010` | `FAO_010` |
| **metadata_delta** | 0.35 | 0.35 |
| **kg_score** | 0.43 | 0.43 |
| **final_score** | 1.3977 | 1.3977 |

- **Kết luận**: **Giữ nguyên ranking (chưa cần/không nên can thiệp)**. Baseline đã đúng intent (FAO IMN manual đứng top1); thay đổi thêm vào ranking lúc này dễ tạo false positive hơn là gain.
- **Làm rõ/củng cố**: alias/canonical disease đã **ổn định** về bucket `IMN` (tính nhất quán khi giải thích/CSV/export).

## 3) Nuôi tôm hùm ở Khánh Hòa — before/after (round2)

Nguồn số liệu: `outputs/focus_two_queries_round2_before.json` vs `outputs/focus_two_queries_round2_after.json`.

| Chỉ số | Trước | Sau |
|---|---:|---:|
| **top1 vector** | `SEAFDEC_008` (0.6984) | `SEAFDEC_008` (0.6984) |
| **top1 hybrid** | `FAO_015` | `FAO_015` |
| **metadata_delta** | 0.22 | 0.22 |
| **kg_score** | 0.23 | 0.23 |
| **final_score** | 1.2318 | 1.1118 |

- **Kết luận**: **Cải thiện một phần (intent hẹp được “siết” tốt hơn), nhưng top1 chưa thể thành tài liệu nuôi tại Khánh Hòa**.
- **Cụ thể đã cải thiện gì**:
  - Query “nuôi + Khánh Hòa” được kích hoạt **intent gate** (conservative) và áp **late penalty** cho tài liệu mang ngữ cảnh **capture/market** *chỉ khi* trong candidate pool có ít nhất 1 tài liệu có dấu hiệu **aquaculture**.
  - Vì `FAO_015` là tài liệu catalogue/capture, `final_score` giảm (mục tiêu: tránh capture/market vượt aquaculture nếu aquaculture có mặt trong pool).
- **Vì sao chưa thể kéo đúng intent “nuôi tại Khánh Hòa”** (nguyên nhân có căn cứ):
  - **Metadata** hiện chỉ có **2 tài liệu liên quan lobster** và đều là **capture fisheries / Global** (không có doc “aquaculture tại Khánh Hòa” trong metadata):
    - `FAO_014`: `related_taxon=lobster`, `production_mode=capture fisheries`
    - `FAO_015`: `related_taxon=lobsters; Decapoda`, `production_mode=capture fisheries`
  - **KG facts** cũng không có document nào đồng thời `aboutTaxon=Tom_hum_bong` và `aboutLocation=Ven_bien_Khanh_Hoa` (đã kiểm tra bằng truy vấn KG runtime).
  - Do đó, hệ thống không có “đúng tài liệu nuôi địa phương” để đẩy lên top1; việc ép ranking mạnh hơn sẽ khiến top1 chuyển sang tài liệu **không liên quan taxon/location** (rủi ro regression cao hơn).

## 4) Regression check (6 query bắt buộc)

Đối chiếu round2 before/after cho các query kiểm tra:
- **bệnh AHPND trên tôm**: giữ ổn (top1 vector/hybrid và các score không đổi).
- **bệnh đốm trắng ở tôm thẻ chân trắng**: giữ ổn.
- **biosecurity trong hatchery tôm thẻ chân trắng**: giữ ổn.
- **tài liệu về trại giống tôm sú ở Ấn Độ**: giữ ổn.
- **infectious myonecrosis**: giữ ổn (ranking).
- **nuôi tôm hùm ở Khánh Hòa**: top1 hybrid giữ `FAO_015`; `final_score` giảm do intent penalty (không làm trồi tài liệu market/capture lên cao hơn).

## 5) Đánh giá “cải thiện / chưa cải thiện” (theo yêu cầu GVHD)

- **infectious myonecrosis**: **chưa cải thiện ranking** (có chủ đích) — vì baseline đã đúng; cải thiện chủ yếu ở **canonical consistency** (giảm sai lệch giải thích/bucket).
- **nuôi tôm hùm ở Khánh Hòa**: **cải thiện một phần** — intent hẹp được “khóa” tốt hơn để chống capture/market vượt aquaculture *khi aquaculture có trong pool*; nhưng **chưa thể đạt** top1 “nuôi tại Khánh Hòa” do **thiếu tài liệu đúng ngữ cảnh** trong corpus/metadata/KG facts hiện tại.

