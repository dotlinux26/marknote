# MarkNote - Phần Mềm Nguồn Mở Soạn Thảo Ghi Chú Cá Nhân

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Release: v1.2.5](https://img.shields.io/badge/Release-v1.2.5-brightgreen.svg)](https://github.com/dotlinux26/marknote/releases)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![GUI: PySide6](https://img.shields.io/badge/GUI-PySide6%20%2F%20Qt%206-green.svg)](https://wiki.qt.io/Qt_for_Python)
[![Open Source: OSI Compliant](https://img.shields.io/badge/Open%20Source-OSI%20Compliant-brightgreen.svg)](docs/LICENSE_COMPLIANCE.md)
[![CI/CD: GitHub Actions](https://img.shields.io/badge/CI%2FCD-Passing-success.svg)](https://github.com/dotlinux26/marknote/actions)

**MarkNote** là một dự án **phát triển phần mềm nguồn mở soạn thảo và quản lý ghi chú cá nhân** chất lượng cao, hoạt động hoàn toàn offline, đa nền tảng (Linux, Windows, macOS). Ứng dụng được xây dựng trên nền tảng **Python + PySide6 (Qt 6)** kết hợp engine kết xuất tài liệu hiện đại, mang đến trải nghiệm viết ghi chú, soạn thảo báo cáo kỹ thuật và xuất bản ấn phẩm PDF/HTML chuẩn mực công nghiệp.

---

## 🌟 Mục Tiêu & Triết Lý Phát Triển

1. **Phần Mềm Nguồn Mở Tự Do (Open Source & Free):**
   - Phát hành theo giấy phép **MIT License**, đảm bảo 10 tiêu chí của Open Source Initiative (OSI) và 4 quyền tự do cốt lõi của Free Software Foundation (FSF).
   - Mã nguồn minh bạch, sạch sẽ, khuyến khích cộng đồng cùng học tập, sử dụng và đóng góp phát triển.
2. **Ưu Tiên Quyền Riêng Tư (Privacy-First & 100% Offline):**
   - Toàn bộ ghi chú, cấu hình và tệp đa phương tiện được lưu trữ cục bộ trên máy tính của bạn (cơ sở dữ liệu SQLite cục bộ).
   - Không telemetry, không thu thập dữ liệu, không bắt buộc tạo tài khoản và không phụ thuộc bất kỳ máy chủ đám mây nào.
3. **Soạn Thảo Trực Quan & Xuất Bản Chuyên Nghiệp:**
   - Hỗ trợ đầy đủ cú pháp GitHub Flavored Markdown (GFM), Toán học KaTeX, Khối mã nguồn Pygments, Bảng dữ liệu tự động xuống dòng và Biểu đồ vector SVG.
   - Khả năng xuất bản **PDF A4 chuẩn in ấn** với số trang thực, mục lục động tự động sinh số trang (leader dots), ngắt trang thông minh và chống tràn lề.

---

## 🚀 Các Tính Năng Nổi Bật

### 1. Soạn Thảo & Xem Trước Trực Quan
- **Cửa sổ song song (Split Pane):** Soạn thảo bên trái, xem trước kết quả bên phải theo thời gian thực (độ trễ 0.3s mượt mà).
- **Đánh số dòng code (Line Numbers):** Cột đếm số dòng văn bản chuẩn IDE chuyên nghiệp ở mép trái editor.
- **Cuộn đồng bộ thông minh (Sync Scroll):** Cuộn editor thì preview tự động cuộn theo tương ứng và ngược lại (bật/tắt bằng phím `Ctrl+Shift+S`).
- **Tô màu mã nguồn (Syntax Highlighting):** Tích hợp bộ thư viện Pygments nhận diện hơn 100+ ngôn ngữ lập trình (Python, Bash, C/C++, Rust, Go, JavaScript, v.v.).

### 2. Quản Trị Ghi Chú & Tìm Kiếm Toàn Kho
- **Quản lý ghi chú cá nhân:** Tạo mới, lưu, xóa, gắn nhãn (Tag), đổi tên ghi chú trực tiếp inline (`F2` hoặc nút ✎).
- **Tìm kiếm toàn văn siêu tốc (SQLite FTS5):** Tìm kiếm tức thì trong toàn bộ kho ghi chú theo từ khóa, hỗ trợ lọc nâng cao theo nhãn (ví dụ `tag:linux`, `tag:security`).
- **Tìm & Thay thế nội bộ:** Phím tắt tìm kiếm (`Ctrl+F`) và thay thế hàng loạt (`Ctrl+H`) ngay trong tệp đang mở.

### 3. Thư Viện Ảnh & Tệp Đa Phương Tiện
- **Chèn ảnh linh hoạt:** Kéo thả ảnh trực tiếp vào editor, dán ảnh chụp màn hình nhanh (`Ctrl+V`) từ clipboard hoặc bấm nút `+ Image` (`Ctrl+Shift+I`).
- **Thư mục Media dùng chung:** Truy cập nhanh kho tài nguyên media cá nhân bằng phím `Ctrl+Shift+M`.
- **Tự động nhúng Base64:** Khi xuất file HTML hoặc PDF, hình ảnh được tự động mã hóa Base64 thành một tệp duy nhất, dễ dàng chia sẻ mà không lo đứt liên kết ảnh.

### 4. Hệ Thống Xuất Bản Đỉnh Cao (PDF / HTML / Markdown)
- **Mục lục thông minh (Smart TOC):**
  - Cú pháp linh hoạt: `[[TOC]]`, `[[TOC="MỤC LỤC BÁO CÁO" center no-bullet]]`.
  - **Thuật toán lọc chuẩn xác:** Chỉ quét và liệt kê các mục nằm **bên dưới** vị trí TOC (loại trừ tiêu đề bìa và metadata ở đầu file).
  - Nhận diện cả Markdown (`#`) lẫn HTML raw (`<h1>` - `<h6>`).
  - Phân cấp kiểu chữ chuẩn: Cấp 1 in đậm chữ thẳng, Cấp 2 đậm nghiêng, Cấp 3 nghiêng bình thường.
  - Khi in PDF: Tự động tính toán số trang thực tế và vẽ đường chấm dẫn (`leader dots`).
- **Biểu đồ tròn Donut Chart (Vector SVG Widget):**
  - Cú pháp Markdown siêu gọn:
    ````markdown
    ```donut
    5 Issues
    Critical: 0
    High: 1
    Medium: 2
    Low: 2
    ```
    ````
  - Tự động cộng dồn tổng số, tự động căn giữa toàn trang, không viền hộp xám, nét vẽ SVG sắc nét 100%.
- **Bảng dữ liệu GFM tự động Fit & Wrap:**
  - Tự động căng đều 100% chiều rộng trang.
  - Tự động ngắt chữ xuống dòng khi nội dung dài, không bao giờ bị cắt cụt chữ.
  - Tự động lặp lại tiêu đề (`thead`) ở đầu trang in tiếp theo khi bảng dài nhiều trang.
- **Tasklist / Checklist:** Tự động chuẩn hóa `[ ]`, `[x]`, `- [ ]` thành checkbox vector SVG sắc nét, không bị lệch lề.
- **Ngắt trang chủ động:** Dễ dàng ngắt trang in PDF bằng thẻ `<div class="page-break"></div>`.

> 📖 **Xem hướng dẫn cú pháp chi tiết tại:** [**`MARKNOTE_SYNTAX_GUIDE.md`**](MARKNOTE_SYNTAX_GUIDE.md)

---

## 💻 Yêu Cầu Hệ Thống & Cài Đặt

| Hệ điều hành | Hỗ trợ | Phương thức phân phối |
|:---|:---:|:---|
| **Linux (Mọi distro)** | ✅ | AppImage (x86_64), gói .deb, .rpm, tarball |
| **Windows (10/11 x64)**| ✅ | Bản Portable độc lập đóng gói sẵn (`marknote.exe`) |
| **macOS** | 🟡 | Chạy qua Python hoặc đóng gói PyInstaller macOS |

### 1. Tải bản dựng sẵn (Khuyên dùng)
Bạn có thể tải các bản phát hành mới nhất từ trang [**Releases**](https://github.com/dotlinux26/marknote/releases):
- **Linux:** Tải file `MarkNote-x.x.x-x86_64.AppImage`, cấp quyền thực thi (`chmod +x`) và chạy ngay.
- **Windows:** Tải file `MarkNote-x.x.x-windows-x64.zip`, giải nén và mở `marknote.exe`.

### 2. Chạy từ mã nguồn (Dành cho nhà phát triển)
Yêu cầu: **Python 3.10 trở lên**.

```bash
# 1. Clone repository
git clone https://github.com/dotlinux26/marknote.git
cd marknote

# 2. Khởi tạo môi trường ảo
python -m venv .venv

# Kích hoạt trên Linux/macOS:
source .venv/bin/activate
# Kích hoạt trên Windows (PowerShell):
# .\.venv\Scripts\Activate.ps1

# 3. Cài đặt các gói phụ thuộc
pip install -r requirements.txt

# 4. Chạy ứng dụng
python src/main.py
```

*Lưu ý cho Linux tối giản:* Để sử dụng tính năng xuất PDF qua WeasyPrint, hãy cài thêm thư viện pango:
```bash
# Ubuntu / Debian:
sudo apt install libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz-subset0
# Fedora / RHEL:
sudo dnf install pango
# Arch Linux:
sudo pacman -S pango
```

---

## ⌨️ Bảng Phím Tắt Tiện Dụng

| Phím tắt | Chức năng |
|:---|:---|
| `Ctrl + N` | Tạo ghi chú mới |
| `Ctrl + S` | Lưu ghi chú hiện tại |
| `F2` | Đổi tên tiêu đề ghi chú nhanh |
| `Ctrl + D` | Xóa ghi chú |
| `Ctrl + F` | Tìm kiếm văn bản trong ghi chú |
| `Ctrl + H` | Tìm kiếm và thay thế văn bản |
| `Ctrl + Shift + I` | Chèn tệp hình ảnh tại vị trí con trỏ |
| `Ctrl + Shift + M` | Mở thư mục thư viện đa phương tiện (Media Folder) |
| `Ctrl + Shift + S` | Bật / tắt chế độ cuộn đồng bộ (Sync Scroll) |
| `Ctrl + E` | Xuất ghi chú ra tệp HTML độc lập |
| `Ctrl + P` | Xuất ghi chú ra tài liệu PDF chuẩn in ấn A4 |
| `F11` | Bật / tắt chế độ toàn màn hình |
| `Ctrl + Q` | Thoát ứng dụng |

---

## 📁 Cấu Trúc Mã Nguồn

```text
marknote/
├── assets/
│   ├── icons/                 # Bộ biểu tượng ứng dụng và vector SVG
│   └── themes/                # Theme giao diện CSS (default, dark, github)
├── docs/                      # Tài liệu kỹ thuật, báo cáo phân tích và sơ đồ kiến trúc
├── packaging/                 # Kịch bản đóng gói tự động (AppImage, Docker, Windows)
├── src/
│   ├── main.py                # Điểm khởi chạy chính & điều phối cửa sổ ứng dụng
│   ├── editor.py              # Khung soạn thảo, đánh số dòng và thanh công cụ
│   ├── preview.py             # Bộ render GFM Markdown, WebEngine và xử lý TOC
│   ├── exporter.py            # Engine xuất HTML và PDF (WeasyPrint, Donut Widget)
│   ├── db.py                  # Cơ sở dữ liệu SQLite FTS5 (Notes, Tags, Settings)
│   ├── media.py               # Quản lý hình ảnh và nhúng Base64
│   ├── theme.py               # Quản lý và nạp động CSS themes
│   └── settings.py            # Cấu hình hệ thống và phím tắt
├── tests/                     # Bộ kiểm thử đơn vị tự động (Unit Tests)
├── Makefile                   # Kịch bản tự động hóa xây dựng và kiểm thử
├── MARKNOTE_SYNTAX_GUIDE.md   # Cẩm nang tra cứu cú pháp Markdown và Widget
├── CONTRIBUTING.md            # Hướng dẫn quy trình đóng góp mã nguồn mở
├── THIRD_PARTY_NOTICES.md     # Kê khai bản quyền và giấy phép bên thứ ba
├── LICENSE                    # Giấy phép nguồn mở MIT License
└── README.md                  # Giới thiệu tổng quan dự án
```

---

## 🤝 Đóng Góp Phát Triển (Contributing)

Dự án phát triển phần mềm nguồn mở MarkNote luôn chào đón mọi sự đóng góp từ cộng đồng lập trình viên, từ việc báo lỗi (Issue), đề xuất ý tưởng cải tiến cho đến các đóng góp mã nguồn (Pull Request).

Vui lòng tham khảo tệp [**`CONTRIBUTING.md`**](CONTRIBUTING.md) để nắm rõ quy chuẩn mã nguồn, quy trình kiểm thử và cách thức gửi PR.

---

## 📜 Giấy Phép & Bản Quyền (License)

- Dự án MarkNote được phát hành theo giấy phép nguồn mở **[MIT License](LICENSE)**.
- Bản quyền thuộc về © 2026 **Nguyen Duc Canh**.
- Thông tin tuân thủ giấy phép nguồn mở và kê khai các thành phần bên thứ ba (PySide6, WeasyPrint, Pygments, markdown-it-py) được ghi nhận đầy đủ tại [**`THIRD_PARTY_NOTICES.md`**](THIRD_PARTY_NOTICES.md) và [**`docs/LICENSE_COMPLIANCE.md`**](docs/LICENSE_COMPLIANCE.md).
