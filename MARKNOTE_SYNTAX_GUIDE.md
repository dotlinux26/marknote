# CẨM NANG HƯỚNG DẪN CÚ PHÁP & TÍNH NĂNG MARKNOTE (v1.3.0)

Tài liệu chuẩn hóa toàn bộ cú pháp Markdown nâng cao, chỉ thị in ấn (`[[print ...]]`), tạo trang bìa Full-Bleed tràn viền 100%, bảng biểu, biểu đồ Donut SVG, mục lục động và các widget chuyên dụng phục vụ soạn thảo và xuất bản PDF/HTML chuyên nghiệp trong **MarkNote**.

---

## 1. Hướng Dẫn Tạo Trang Bìa Tràn Viền 100% (Full-Bleed Cover Page)

Khi xuất tài liệu sang PDF, trang bìa mặc định có thể bị co cụm và dính viền trắng của lề giấy in A4 (`margin: 18mm`). Để tạo một trang bìa to rộng **tràn viền 100% (Full A4 210mm × 297mm)**, không viền trắng và không dính số trang ở chân bìa, hãy áp dụng mẫu chuẩn sau:

### Cú pháp mẫu chuẩn (Copy & Paste dùng ngay)

```html
<style>
/* 1. Xóa lề và ẩn số trang cho riêng Trang 1 */
@page :first {
  margin: 0;
  @bottom-center { content: none; }
  @top-center { content: none; }
}

/* 2. Khung bìa phủ trọn vẹn 100% khổ giấy A4 */
.cover-page {
  width: 210mm;
  height: 297mm;
  box-sizing: border-box;
  padding: 35mm 25mm 25mm 25mm; /* Đệm nội dung bên trong lùi vào hợp lý */
  background: linear-gradient(145deg, #0f172a 0%, #1e3a8a 55%, #0284c7 100%);
  color: #ffffff;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

/* 3. Nhãn phân loại & Tiêu đề */
.cover-tag {
  font-size: 10pt;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: #38bdf8;
  font-weight: 700;
  margin-bottom: 10mm;
}

.cover-title {
  font-size: 30pt;
  font-weight: 800;
  line-height: 1.25;
  color: #ffffff;
  margin-bottom: 8mm;
}

.cover-subtitle {
  font-size: 13pt;
  line-height: 1.5;
  color: #cbd5e1;
  max-width: 160mm;
}

/* 4. Khung Metadata phía dưới */
.cover-meta {
  background: rgba(15, 23, 42, 0.65);
  border: 1px solid rgba(56, 189, 248, 0.35);
  border-radius: 8px;
  padding: 6mm 8mm;
  display: flex;
  justify-content: space-between;
}

.meta-col {
  flex: 1;
}

.meta-label {
  font-size: 8.5pt;
  text-transform: uppercase;
  color: #94a3b8;
  letter-spacing: 0.05em;
  margin-bottom: 2mm;
}

.meta-val {
  font-size: 10.5pt;
  font-weight: 700;
  color: #f8fafc;
}
</style>

<!-- KHỐI BÌA TRANG 1 -->
<div class="cover-page">
  <div>
    <div class="cover-tag">CONFIDENTIAL · INDEPENDENT SECURITY ASSESSMENT</div>
    <div class="cover-title">BÁO CÁO ĐÁNH GIÁ AN TOÀN THÔNG TIN & RETEST</div>
    <div class="cover-subtitle">Kiểm thử xâm nhập chuyên sâu kiến trúc đa khách thuê, hệ thống API và hạ tầng điện toán đám mây.</div>
  </div>

  <div class="cover-meta">
    <div class="meta-col">
      <div class="meta-label">Đơn vị thụ hưởng</div>
      <div class="meta-val">Tập đoàn / Doanh nghiệp ABC</div>
      <br>
      <div class="meta-label">Thời gian đánh giá</div>
      <div class="meta-val">Tháng 11, 2026</div>
    </div>
    <div class="meta-col">
      <div class="meta-label">Chuyên gia thực hiện</div>
      <div class="meta-val">Nguyễn Đức Cảnh (canhnguyen26)</div>
      <br>
      <div class="meta-label">Trạng thái phát hành</div>
      <div class="meta-val">Bản chính thức (Final Approved)</div>
    </div>
  </div>
</div>

<!-- LỆNH NGẮT TRANG BẮT BUỘC SAU BÌA -->
<div class="page-break"></div>
```

> **Nguyên tắc kỹ thuật:**
> - `@page :first { margin: 0; }` loại bỏ toàn bộ khoảng cách thừa để màu nền trải rộng 100% ra mép trang.
> - `@bottom-center { content: none; }` tự động ẩn số trang `1 / N` trên bìa.
> - Bắt buộc thêm `<div class="page-break"></div>` ở cuối khối bìa để các trang sau tiếp tục với lề tiêu chuẩn và số trang đánh từ trang 2.

---

## 2. Chỉ Thị Hình Nền & In Ấn (`[[print ...]]` / `[[page-bg ...]]`)

MarkNote cho phép tùy biến nền tài liệu in PDF bằng chỉ thị directive 1 dòng cực kỳ linh hoạt (tự động ẩn khỏi màn hình Preview):

### Các cú pháp thường dùng:

1. **Hình nền Watermark / Giấy in cho toàn bộ tài liệu:**
   ```markdown
   [[print bg="media/watermark.png" mode="contain" opacity="0.15" position="center" pages="all"]]
   ```

2. **Hình nền dạng hoa văn lặp lại (Pattern / Giấy kẻ caro):**
   ```markdown
   [[print bg="media/grid-pattern.png" mode="repeat" opacity="0.2" pages="all"]]
   ```

3. **Chỉ đặt nền cho riêng Trang bìa (Trang 1):**
   ```markdown
   [[print bg="media/cover-art.jpg" mode="cover" pages="1"]]
   ```

4. **Nền dải màu Gradient theo trang lẻ hoặc chẵn:**
   ```markdown
   [[page-bg gradient="linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)" pages="even"]]
   ```

### Bảng tham số chi tiết:

| Thuộc tính | Tùy chọn giá trị | Ý nghĩa |
|:---|:---|:---|
| `bg` / `image` | `"path/to/img.png"` hoặc URL | Đường dẫn ảnh nền (tự động nhúng Base64) |
| `mode` / `fit` | `cover`, `contain`, `repeat`, `stretch` | Cách hiển thị ảnh (`stretch` = kéo giãn 100% 100%) |
| `opacity` / `alpha` | `0.1` đến `1.0` hoặc `15%`, `30%` | Điều chỉnh độ trong suốt tự động qua Pillow |
| `position` | `center`, `top left`, `top right`, ... | Vị trí đặt ảnh |
| `gradient` | `linear-gradient(...)`, `radial-gradient(...)` | Nền chuyển sắc CSS |
| `bg-color` | `#ffffff`, `rgba(...)` | Màu nền đơn sắc |
| `pages` / `page` | `all`, `1`, `1-3`, `odd`, `even` | Các trang in được áp dụng |
| `style` | `"margin: 0;"`, `"border: none;"` | CSS tùy biến bổ sung cho trang in |

---

## 3. Mục Lục Thông Minh (Smart TOC)

Tự động quét và hiển thị các đề mục, tự sinh đường chấm dẫn (`leader dots`) và số trang thực tế khi in PDF:

```markdown
[[TOC]]
```

### Các tùy chọn nâng cao:
```markdown
[[TOC="MỤC LỤC BÁO CÁO" center no-bullet]]
```

| Tham số | Ý nghĩa | Ví dụ |
|:---|:---|:---|
| `"Tên tùy chỉnh"` | Đổi tên tiêu đề mục lục | `[[TOC="NỘI DUNG CHÍNH"]]` |
| `center` / `left` / `right` | Căn chỉnh tiêu đề | `[[TOC center]]` |
| `no-bullet` | Ẩn dấu chấm đầu dòng, thụt lề chuẩn | `[[TOC no-bullet]]` |
| `max-depth=N` | Giới hạn cấp đề mục quét (1 - 6) | `[[TOC max-depth=3]]` |
| `title-color="màu"` | Màu tiêu đề bảng | `[[TOC title-color="#0284c7"]]` |

> **Lưu ý:** Mục lục chỉ quét các tiêu đề nằm **phía dưới** vị trí đặt `[[TOC]]`, giúp tự động loại bỏ tiêu đề trang bìa và metadata đầu file.

---

## 4. Biểu Đồ Tròn Donut Chart Vector SVG

Biểu đồ vector sắc nét 100%, căn giữa tự động và tính tỷ lệ chính xác:

````markdown
```donut
5 Issues
Critical: 0
High: 1
Medium: 2
Low: 2
```
````

Hoặc viết dạng rút gọn:
````markdown
```donut
title: Findings
Critical: 2
High: 3
Medium: 1
Low: 4
```
````

Hoặc cú pháp 1 dòng:
```markdown
[[donut 5 Issues | Critical: 0 | High: 1 | Medium: 2 | Low: 2]]
```

---

## 5. Bảng Dữ Liệu Tự Động Co Giãn & Ngắt Dòng (GFM Tables)

```markdown
| Mã Lỗi | Tên Chức Năng | Mức Độ | Trạng Thái | Mô Tả & Khuyến Nghị |
|:---|:---|:---:|:---:|:---|
| `SEC-01` | Quản trị API | CRITICAL | **Fixed** | Lỗ hổng IDOR đã được kiểm tra vá triệt để. |
| `SEC-02` | Xác thực JWT | HIGH | **Verified** | Đã bổ sung cơ chế xác minh khóa bí mật HS256. |
```

- **Tự động Fit 100% trang:** Bảng luôn trải đều không bị lệch lề.
- **Tự động bẻ dòng (Word Wrap):** Văn bản và đường dẫn dài tự động xuống hàng, không bao giờ bị cắt cụt.
- **Tự động lặp lại tiêu đề:** Tiêu đề cột (`thead`) tự động xuất hiện ở đầu trang sau khi bảng dài nhiều trang.

---

## 6. Danh Sách Công Việc (Tasklist / Checklist)

```markdown
- [x] Rà soát danh sách endpoint API
- [x] Thiết lập môi trường Staging
- [ ] Kiểm thử leo quyền dọc & ngang
- [ ] Xuất báo cáo nghiệm thu
```
Tự động chuyển đổi thành hộp checkbox vector SVG sắc nét, căn lề chuẩn mực.

---

## 7. Huy Hiệu Mức Độ (Severity Badges) & Hộp Cảnh Báo (Callouts)

### Huy hiệu:
```html
<span class="sev-badge sev-crit">CRITICAL</span>
<span class="sev-badge sev-high">HIGH</span>
<span class="sev-badge sev-med">MEDIUM</span>
<span class="sev-badge sev-low">LOW</span>
<span class="sev-badge sev-pass">100% PASS</span>
```

### Khung thông báo:
```html
<div class="callout callout-info">
  <b>Thông tin:</b> Quá trình đánh giá được thực hiện độc lập và khách quan.
</div>

<div class="callout callout-warning">
  <b>Cảnh báo:</b> Cần cấu hình giới hạn tần suất truy vấn (Rate Limiting).
</div>

<div class="callout callout-danger">
  <b>Lỗ hổng nghiêm trọng:</b> Truy cập trái phép dữ liệu nhạy cảm.
</div>
```

---

## 8. Lệnh Ngắt Trang & Phím Tắt Tiện Dụng

### Ngắt trang chủ động:
```html
<div class="page-break"></div>
```

### Bảng phím tắt ứng dụng:
| Phím tắt | Thao tác |
|:---|:---|
| `Ctrl + N` | Tạo ghi chú mới |
| `Ctrl + O` | Nhập tệp ngoài (Import `.md`, `.markdown`, `.txt`) |
| `Ctrl + S` | Lưu ghi chú hiện tại |
| `F2` | Đổi tên ghi chú nhanh |
| `Ctrl + P` | Xuất tài liệu ra PDF chuẩn in ấn A4 |
| `Ctrl + E` | Xuất tài liệu ra file HTML độc lập |
| `Ctrl + Shift + I` | Chèn hình ảnh tại vị trí con trỏ |
| `Ctrl + Shift + M` | Mở thư mục Media dùng chung |
| `Ctrl + Shift + S` | Bật / tắt cuộn đồng bộ (Sync Scroll) |
| `Ctrl + F` / `Ctrl + H` | Tìm kiếm / Thay thế văn bản |
