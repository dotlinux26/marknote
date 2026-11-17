# CẨM NANG HƯỚNG DẪN CÚ PHÁP MARKNOTE (v1.2.5)

Tài liệu hướng dẫn chi tiết toàn bộ các cú pháp Markdown nâng cao, bảng biểu, sơ đồ, biểu đồ donut, mục lục và các widget chuyên dụng được tối ưu hóa cho hiển thị trực quan (Preview) và xuất bản PDF chất lượng cao trong **MarkNote**.

---

## 1. Mục Lục Thông Minh (Smart TOC)

MarkNote trang bị bộ tạo mục lục động với khả năng nhận diện đa cấp bậc, tự động tạo liên kết anchor và hỗ trợ in ấn chuyên nghiệp.

### Cú pháp
```markdown
[[TOC]]
```

### Các tùy chọn nâng cao
Bạn có thể kết hợp đổi tên tiêu đề, căn lề và loại bỏ dấu chấm bullet:
```markdown
[[TOC="MỤC LỤC BÁO CÁO" center no-bullet]]
```

| Tham số | Ý nghĩa | Ví dụ |
|:---|:---|:---|
| `"Tên tùy chỉnh"` | Đặt lại tiêu đề mục lục | `[[TOC="NỘI DUNG CHÍNH"]]` |
| `center` | Căn giữa tiêu đề mục lục | `[[TOC center]]` |
| `right` | Căn phải tiêu đề mục lục | `[[TOC right]]` |
| `left` | Căn trái tiêu đề (mặc định) | `[[TOC left]]` |
| `no-bullet` | Ẩn dấu chấm bullet (`•`), thụt lề sạch sẽ | `[[TOC no-bullet]]` |

### Quy tắc hoạt động thông minh của MarkNote
1. **Chỉ quét các mục bên dưới `[[TOC]]`:** Các tiêu đề xuất hiện trước `[[TOC]]` (như tiêu đề bìa, thông tin tác giả, metadata) sẽ **không** bị đưa vào mục lục.
2. **Nhận diện cả Markdown `#` lẫn thẻ HTML `<h1>` - `<h6>`:** Dù bạn viết `# Heading` hay `<h2>Tiêu đề</h2>` trong HTML, mục lục đều tự động nhận diện và gán liên kết.
3. **Phân cấp phông chữ chuyên nghiệp:**
   - **Cấp 1 (Mục chính to nhất):** In đậm, chữ thẳng (`font-weight: 700`).
   - **Cấp 2 (Mục con cấp 2, ví dụ 1.2):** Đậm nghiêng (`font-weight: 600; font-style: italic`).
   - **Cấp 3 (Mục con cấp 3, ví dụ 1.1.2):** Nghiêng bình thường (`font-weight: 400; font-style: italic`).
   - **Cấp 4+ (Mục con sâu hơn):** Chữ thường, thẳng.
4. **Xuất PDF:** Khi in ra PDF, mục lục tự động sinh đường chấm dẫn (`leader dots`) kèm số trang chính xác bên phải.

---

## 2. Biểu Đồ Tròn Donut Chart (Donut Vector Widget)

MarkNote hỗ trợ cú pháp vẽ biểu đồ donut vector SVG cực kỳ ngắn gọn, tự động căn giữa toàn trang, không nền viền và tính toán tỷ lệ chính xác.

### Cú pháp khối mã (Khuyên dùng)
````markdown
```donut
5 Issues
Critical: 0
High: 1
Medium: 2
Low: 2
```
````

Hoặc viết ngắn gọn không cần ghi tổng (hệ thống tự động cộng dồn):
````markdown
```donut
Critical: 0
High: 1
Medium: 2
Low: 2
```
````

Hoặc đổi tên nhãn ở tâm:
````markdown
```donut
title: Findings
Critical: 2
High: 3
Medium: 1
Low: 4
```
````

### Cú pháp 1 dòng (Directive)
```markdown
[[donut 5 Issues | Critical: 0 | High: 1 | Medium: 2 | Low: 2]]
```
hoặc:
```markdown
[[donut crit=0 high=1 med=2 low=2]]
```

### Đặc tính:
- Vòng tròn donut hiển thị to rõ (~110px), số lượng tâm to đậm nổi bật.
- Căn giữa toàn trang, viền trong suốt (`border: none; background: transparent`).
- Khi xuất PDF bằng WeasyPrint, biểu đồ là vector SVG 100% sắc nét, không bị răng cưa hay mất màu.

---

## 3. Bảng Dữ Liệu Tự Động Co Giãn & Ngắt Dòng (GFM Tables)

Bảng biểu trong MarkNote được cấu hình CSS tự động thích ứng với trang giấy in:

```markdown
| Mã Module | Tên Tuyến API | Số Thao Tác | Trạng Thái | Ghi Chú Đánh Giá |
|:---|:---|:---:|:---:|:---|
| `MOD-01` | `auth` | 6 | **Directly Tested** | Đã kiểm thử trực tiếp 100% các endpoint xác thực. |
| `MOD-02` | `listings` | 45 | **Deep Tested** | Module rủi ro cao: kiểm thử IDOR, Mass Assignment và Input Validation. |
```

- **Căn lề cột:**
  - `:---` Căn trái
  - `:---:` Căn giữa
  - `---:` Căn phải
- **Tính năng tự động của MarkNote:**
  - **Tự động Fit chiều rộng 100% trang:** Bảng luôn trải đều không bị lệch.
  - **Tự động bẻ dòng (Word Wrap):** Văn bản dài hoặc đường dẫn dài sẽ tự động xuống dòng, không bao giờ bị cắt cụt hay tràn ra ngoài mép giấy.
  - **Lặp lại tiêu đề khi sang trang in:** Khi bảng dài nhiều trang, dòng tiêu đề (`thead`) sẽ tự động lặp lại ở đầu trang tiếp theo.

---

## 4. Danh Sách Công Việc (Tasklist / Checklist)

Hỗ trợ cả cú pháp Markdown chuẩn và dấu ngoặc vuông viết tắt:

```markdown
- [x] Thu thập và rà soát danh sách endpoint OpenAPI
- [x] Cấu hình tài khoản kiểm thử cho Tenant A và Tenant B
- [ ] Thực hiện tấn công thử nghiệm leo quyền IDOR
- [ ] Báo cáo kết quả và xác minh vá lỗi (Retest)
```

MarkNote tự động chuyển đổi thành checkbox vector SVG đồng bộ, đẹp mắt và căn thẳng hàng hoàn hảo.

---

## 5. Sơ Đồ Quy Trình & Cây Kiến Trúc (Flow & Tree Blocks)

Để vẽ các giai đoạn quy trình hoặc cấu trúc phân cấp, sử dụng khối mã `text` với ký tự Unicode box-drawing:

````markdown
```text
[Giai đoạn 1: Lập kế hoạch & Khóa phạm vi]
 └── Khớp nối OpenAPI 333 endpoints ──> Thiết lập tài khoản Tenant A & B

[Giai đoạn 2: Khảo sát & Dò quét bề mặt]
 └── Quét tự động DAST ──> Liệt kê bảng danh mục tham số endpoint

[Giai đoạn 3: Tấn công khai thác chuyên sâu]
 └── Ma trận phân quyền đa khách thuê ──> Kiểm thử leo quyền dọc & ngang

[Giai đoạn 4: Xác minh, Báo cáo & Retest]
 └── Phân tích bán kính ảnh hưởng ──> Báo cáo và kiểm tra lại bản vá
```
````

Trình in của MarkNote đã được ép cấu hình chống tràn lề, tự động ngắt dòng nếu dòng vẽ quá dài.

---

## 6. Huy Hiệu Mức Độ Nghiêm Trọng (Severity Badges)

Sử dụng trực tiếp trong văn bản hoặc bên trong bảng dữ liệu:

```html
<span class="sev-badge sev-crit">CRITICAL</span>
<span class="sev-badge sev-high">HIGH</span>
<span class="sev-badge sev-med">MEDIUM</span>
<span class="sev-badge sev-low">LOW</span>
<span class="sev-badge sev-pass">100% PASS</span>
```

---

## 7. Khung Ghi Chú & Cảnh Báo (Callout Boxes)

Dùng để nhấn mạnh thông tin quan trọng hoặc cảnh báo bảo mật:

```html
<div class="callout callout-info">
  <b>Thông tin:</b> Quá trình kiểm thử được thực hiện trong môi trường Staging cách ly hoàn toàn.
</div>

<div class="callout callout-warning">
  <b>Cảnh báo:</b> API thiếu cơ chế kiểm soát tần suất truy vấn (Rate Limiting).
</div>

<div class="callout callout-danger">
  <b>Nguy hiểm:</b> Lỗ hổng cho phép người dùng Tenant A xem dữ liệu của Tenant B.
</div>

<div class="callout callout-success">
  <b>Đạt chuẩn:</b> Tất cả các phát hiện đã được khắc phục hoàn toàn trong lần tái kiểm tra.
</div>
```

---

## 8. Ngắt Trang Chủ Động Khi Xuất PDF (Page Break)

Khi muốn một đề mục lớn hoặc phụ lục luôn bắt đầu ở trang mới trong PDF:

```html
<div class="page-break"></div>
```

---

## 9. Định Dạng Văn Bản & Khối Mã (Code Highlighting)

MarkNote tích hợp công cụ tô màu mã nguồn Pygments với hơn 100+ ngôn ngữ:

````markdown
```python
def verify_token(token: str) -> bool:
    # Xác thực chữ ký số
    return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
```
````

---

## 10. Phím Tắt & Tiện Ích Trong MarkNote

| Phím tắt | Chức năng |
|:---|:---|
| `Ctrl + N` | Tạo ghi chú mới |
| `Ctrl + O` | Mở tệp Markdown |
| `Ctrl + S` | Lưu tệp hiện tại |
| `Ctrl + E` | Xuất file HTML độc lập |
| `Ctrl + P` | Xuất tài liệu ra PDF chuẩn in ấn A4 |
| `Ctrl + F` | Tìm kiếm văn bản trong tài liệu |
| `Ctrl + H` | Tìm kiếm và thay thế văn bản |
| `F11` | Bật / tắt chế độ toàn màn hình |
| `Sync Scroll` | Tự động đồng bộ vị trí cuộn giữa cửa sổ soạn thảo và cửa sổ xem trước |
| `Line Numbers` | Đánh số dòng chuẩn code editor ở lề trái |
