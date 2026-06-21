# KNQG_002 text extraction after PDF update

- Th?i ?i?m report: 2026-05-31 13:06:54

## Summary

| metric | value |
| --- | --- |
| doc_id | KNQG_002 |
| file_path | data/raw_docs/KNQG_002_ky_thuat_nuoi_tom_hum_long_phong_tri_benh.pdf |
| size_bytes | 60773248 |
| pages | 63 |
| project_parser_chars | 69586 |
| pymupdf_chars | 69586 |
| selected_text_chars | 69586 |
| keyword_hit_count | 9 |
| keyword_checks | tôm hùm=True; nuôi lồng=True; phòng trị bệnh=True; bệnh sữa=False; đỏ thân=True; thức ăn=True; lồng nuôi=True; môi trường=True; Khánh Hòa=True; Nam Trung Bộ=True |
| head_1000 | BỘ THỦY SẢN <br>wy TRUNG TAM KHUYEN NGU QUOC GIA <br>NU0IT0MIHÙM LũŨNG <br>VÀ CAC BIEN PHAP PHONG TRI BENH <br>oo <br>x ~~ ¬%: <br>S. <br>: <br>Vem Lili 2 <br>là La XS <br>& <br>` s <br>a y3»; <br>... |
| tail_1000 | vùng phân bố tom him <br>20 <br>Chương 3. BIỆN PHÁP PHÒNG BỆNH TỔNG HỢP Ở <br>TÔM HÙM NUÔI LỒNG <br>24 <br>1. Quản lý môi trường nuôi <br>25 <br>2. Tăng cường sức đề kháng của tôm hùm <br>27 <br>3.... |
| extraction_status | PASS |

## Keyword checks

| keyword | found |
| --- | --- |
| tôm hùm | True |
| nuôi lồng | True |
| phòng trị bệnh | True |
| bệnh sữa | False |
| đỏ thân | True |
| thức ăn | True |
| lồng nuôi | True |
| môi trường | True |
| Khánh Hòa | True |
| Nam Trung Bộ | True |

## Text sample head

```text
BỘ THỦY SẢN 
wy TRUNG TAM KHUYEN NGU QUOC GIA 
NU0IT0MIHÙM LũŨNG 
VÀ CAC BIEN PHAP PHONG TRI BENH 
oo 
x ~~ ¬%: 
S. 
: 
Vem Lili 2 
là La XS 
& 
` s 
a y3»; 
<- bn sient 
n 
Co 
eG eae 
i 
`... 
—_ 
ie OS eo | 
i 
zeal 
Mes) = 
= lauli 
k 
Leer 
iO NHÀ XUẤT 
BANNONGNGHIER yàu-2#6<== ˆ. — 
:

BỘ THỦY SẢN 
TRUNG TÂM KHUYẾN NGƯ QUỐC GIA 
Biên soạn: ThS. VÕ VĂN NHA 
KỸ THUẬT NUÔI TÔM HÙM LỒNG 
VÀ CÁC BIỆN PHÁP PHÒNG TRỊ BỆNH 
NHÀ XUẤT BẢN NÔNG NGHIỆP 
HÀ NỘI - 2006

Chương 1: Giới thiệu chung. 
Chương 2: Vài nét về tình hình nuôi và một số yếu tố 
môi trường vàng phân bố tôm him. 
Chương 3: Biện pháp phòng bệnh tổng hợp ở tôm 
hùm nuôi lông. 
Chương 4: Một số bệnh thường gặp ở tôm him nuôi 
lông và biện pháp phòng trị. 
Trong quá trình biên soạn, mặc dù đã hết sức cố 
sáng song sẽ không tránh khỏi thiếu sót, rất mong nhận 
được ý kiến đóng góp, phê bình của bạn đọc để cuốn 
sách hoàn thiện hon trong những lần xuất bản sau. 
Tác giả 
4

Chương I 
GIỚI THIỆU CHUNG 
1. VỊ TRÍ PHÂN LOẠI TÔM HÙ
```

## Text sample tail

```text
vùng phân bố tom him 
20 
Chương 3. BIỆN PHÁP PHÒNG BỆNH TỔNG HỢP Ở 
TÔM HÙM NUÔI LỒNG 
24 
1. Quản lý môi trường nuôi 
25 
2. Tăng cường sức đề kháng của tôm hùm 
27 
3. Tiêu diệt và kìm hãm sự phát triển của tác nhân 
gây bệnh 
33 
Chương 4. MỘT SỐ BỆNH THƯỜNG GẶP Ở TÔM HÙM 
NUÔI LỒNG VÀ BIỆN PHÁP PHÒNG TRỊ 
37 
1. Một số bệnh thường gặp ở tôm hùm nuôi lông 
37 
2. Cách tính lượng thuốc dùng trong phòng, trị bệnh 
tôm hùm 
53 
Tai liệu tham khảo 
56 
50

Chịu trách nhiệm xuất bản 
NGUYÊN CAO DOANH 
Phụ trách bản thảo 
LẠI THỊ THANH TRÀ 
Trình bày bìa 
TOÀN LINH 
NHÀ XUẤT BẢN NÔNG NGHIỆP 
6/167 - Phương Mai - Đống Đa - Hà Nội 
DT: (04) 8524504 - 8521940 FAX: (04) 5760748 
E-mail: nxbnn@hn.vnn.vn 
CHI NHANH NXB NONG NGHIEP 
58 Nguyễn Binh Khiêm - Q.1 Tp. Hồ Chí Minh 
DT: (08) 8297157 - 8299521 
FAX: (08) 9101036 
In 516 bản khổ (15 x 21)cm tai Công ty Cổ phân in 15. Giấy chấp 
nhận DKDT số 850-2006/CXB/35-170/NN do Cục xuất bản cấp ngày 
14/11/2006. In xong và nộp lưu chiểu quý 1/2007.
```
