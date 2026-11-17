<div class="report-cover" style="text-align: center; padding: 40px 20px 20px;">
  <p style="font-size: 1.1rem; font-weight: 700; margin-bottom: 4px; text-transform: uppercase; letter-spacing: 0.05em;">BỘ CÔNG THƯƠNG</p>
  <p style="font-size: 1.25rem; font-weight: 800; margin-top: 0; margin-bottom: 4px; text-transform: uppercase;">TRƯỜNG ĐẠI HỌC CÔNG NGHIỆP HÀ NỘI</p>
  <p style="font-size: 1.15rem; font-weight: 700; margin-top: 0; text-transform: uppercase; color: #1e3a8a;">TRƯỜNG CÔNG NGHỆ THÔNG TIN VÀ TRUYỀN THÔNG</p>
  
  <div style="width: 140px; height: 3px; background: #1e3a8a; margin: 25px auto 40px;"></div>

  <p style="font-size: 1.2rem; font-weight: 700; text-transform: uppercase; color: #475569; margin-bottom: 10px;">BÁO CÁO HỌC PHẦN</p>
  <h1 style="font-size: 2.1rem; font-weight: 900; color: #0f172a; text-transform: uppercase; margin: 10px 0 25px; line-height: 1.3;">
    PHẦN MỀM MÃ NGUỒN MỞ
  </h1>

  <div style="border: 2px solid #cbd5e1; border-radius: 8px; padding: 20px; margin: 30px auto; max-width: 720px; background: #f8fafc;">
    <p style="font-size: 1.05rem; font-weight: 600; color: #475569; margin: 0 0 6px;">ĐỀ TÀI NGHIÊN CỨU VÀ PHÁT TRIỂN:</p>
    <p style="font-size: 1.45rem; font-weight: 800; color: #1e40af; margin: 0; text-transform: uppercase;">
      PHÁT TRIỂN ỨNG DỤNG SOẠN THẢO VÀ QUẢN LÝ GHI CHÚ CÁ NHÂN MÃ NGUỒN MỞ MARKNOTE
    </p>
  </div>

  <div style="margin-top: 50px; text-align: left; display: inline-block; min-width: 480px; font-size: 1.02rem; line-height: 1.8;">
    <table style="width: 100%; border: none; background: transparent;">
      <tr style="border: none;"><td style="width: 45%; font-weight: 700; border: none; padding: 4px 0;">Giảng viên hướng dẫn:</td><td style="border: none; padding: 4px 0;">ThS. Vũ Thị Dương</td></tr>
      <tr style="border: none;"><td style="font-weight: 700; border: none; padding: 4px 0;">Nhóm thực hiện:</td><td style="border: none; padding: 4px 0;">Nhóm 09</td></tr>
      <tr style="border: none;"><td style="font-weight: 700; border: none; padding: 4px 0; vertical-align: top;">Sinh viên thực hiện:</td><td style="border: none; padding: 4px 0;">
        1. <b>Nguyễn Đức Cảnh</b> - MSSV: 2024601793<br>
        2. <b>Ngô Đức Anh</b> - MSSV: 2023602011<br>
        3. <b>Nguyễn Quang Khải</b> - MSSV: 2024604327<br>
        4. <b>Nguyễn Công Tiến</b> - MSSV: 2024605077
      </td></tr>
      <tr style="border: none;"><td style="font-weight: 700; border: none; padding: 4px 0;">Lớp học phần:</td><td style="border: none; padding: 4px 0;">20241IT6030001 (Khóa 19)</td></tr>
    </table>
  </div>

  <div style="margin-top: 60px; font-size: 1rem; font-weight: 600; color: #64748b;">
    Hà Nội – Năm 2026
  </div>
</div>

<div class="page-break"></div>

## BẢNG DANH MỤC TỪ VIẾT TẮT

| Ký hiệu viết tắt | Thuật ngữ đầy đủ tiếng Anh | Giải nghĩa tiếng Việt |
|:---|:---|:---|
| **PMNM / OSS** | Open Source Software | Phần mềm mã nguồn mở |
| **OSI** | Open Source Initiative | Tổ chức Sáng kiến Mã nguồn mở |
| **FSF** | Free Software Foundation | Quỹ Phần mềm Tự do |
| **GFM** | GitHub Flavored Markdown | Quy chuẩn định dạng Markdown mở rộng của GitHub |
| **CSDL / DB** | Database / Relational Database | Cơ sở dữ liệu quan hệ |
| **FTS5** | Full-Text Search 5 | Mô-đun tìm kiếm toàn văn bản trong SQLite |
| **GUI** | Graphical User Interface | Giao diện đồ họa người dùng |
| **IDE** | Integrated Development Environment | Môi trường phát triển tích hợp |
| **TOC** | Table of Contents | Bảng mục lục tự động |
| **SVG** | Scalable Vector Graphics | Định dạng đồ họa vector hai chiều |
| **CI/CD** | Continuous Integration / Continuous Deployment | Tích hợp liên tục và Triển khai liên tục |
| **API** | Application Programming Interface | Giao diện lập trình ứng dụng |
| **MVC** | Model - View - Controller | Mô hình kiến trúc phần mềm 3 tầng |

---

[[TOC="MỤC LỤC BÁO CÁO" center no-bullet]]

<div class="page-break"></div>

# Phần 1: MỞ ĐẦU

### 1. Tóm lược ý tưởng và lý do nghiên cứu đề tài
Trong kỷ nguyên số và phát triển phần mềm hiện đại, việc ghi chép kỹ thuật, quản lý tri thức cá nhân (Personal Knowledge Management - PKM) và soạn thảo tài liệu khoa học đóng vai trò then chốt đối với kỹ sư CNTT và sinh viên. Tuy nhiên, các giải pháp phổ biến hiện nay (như Notion, Obsidian, Evernote, Google Docs) đều tồn tại những nhược điểm lớn:
- **Nguy cơ quyền riêng tư và thất thoát dữ liệu:** Phần lớn đòi hỏi kết nối máy chủ đám mây, dữ liệu người dùng bị lưu trữ tập trung và tiềm ẩn nguy cơ bị khai thác thông tin.
- **Phụ thuộc kết nối mạng:** Hoạt động kém hiệu quả hoặc mất tính năng khi làm việc tại môi trường cô lập mạng (offline/air-gapped labs).
- **Khả năng xuất bản hạn chế:** Khó kết xuất tài liệu in ấn PDF chuẩn A4 có mục lục động đánh đúng số trang thực tế và bảng biểu tự co giãn.

Xuất phát từ các yêu cầu thực tiễn đó, nhóm sinh viên lựa chọn đề tài **"Phát triển ứng dụng soạn thảo và quản lý ghi chú cá nhân mã nguồn mở MarkNote"** nhằm tạo ra một giải pháp desktop mã nguồn mở hoàn chỉnh, hoạt động ngoại tuyến 100%, độc lập nền tảng và hỗ trợ xuất bản tài liệu kỹ thuật đạt chuẩn mực công nghiệp.

### 2. Xác định nội dung học tập và kiến thức, kỹ năng nền tảng
Để thực hiện đề tài, nhóm vận dụng các kiến thức cốt lõi đã tích lũy trong chương trình đào tạo:
- Kỹ thuật lập trình ngôn ngữ **Python** và lập trình hướng đối tượng (OOP).
- Phân tích và thiết kế hệ thống thông tin theo chuẩn UML (Use Case, Class, Sequence Diagram).
- Quản trị và truy vấn cơ sở dữ liệu quan hệ với **SQLite**.

### 3. Kiến thức then chốt lĩnh hội từ học phần Phần mềm mã nguồn mở
Quá trình nghiên cứu đề tài giúp người học làm chủ các chuẩn mực then chốt của học phần:
- **Phương pháp thẩm định và lựa chọn PMNM (Bài 5):** Nắm vững quy trình 4 bước thẩm định công nghệ và đánh giá định lượng dự án theo thang điểm Points of FAIL (PoF).
- **Phân loại phần mềm nguồn mở (Bài 7 & Bài 8):** Định vị phần mềm thuộc nhóm Ứng dụng Desktop chạy trên Linux, khai thác CSDL nhúng SQLite FTS5 và công cụ biên soạn tài liệu học tập ngoại tuyến.
- **Khía cạnh pháp lý & Giấy phép (Licensing):** Thực hành cấp phép bản quyền phần mềm theo giấy phép chuẩn OSI (**MIT License**) và kiểm kê nghĩa vụ pháp lý các thư viện phụ thuộc bên thứ ba (**THIRD_PARTY_NOTICES**).
- **Quy trình phát triển cộng đồng (Bài 9):** Làm chủ quy trình quản lý phiên bản với Git, quản lý luồng đóng góp (Issues, Pull Requests, Code Review) và tự động hóa CI/CD qua GitHub Actions.

<div class="page-break"></div>

# Phần 2: KẾT QUẢ NGHIÊN CỨU

## 2.1. Cộng đồng phát triển PMNM và hệ sinh thái công cụ
Dự án MarkNote được phát triển dựa trên việc tích hợp các thư viện nguồn mở chất lượng cao trong hệ sinh thái Python và Qt:
1. **PySide6 (Qt for Python):** Bộ công cụ phát triển giao diện người dùng đồ họa chuẩn công nghiệp do Qt Company và cộng đồng The Qt Project phát triển, tuân thủ giấy phép nguồn mở LGPLv3.
2. **markdown-it-py & mdit-py-plugins:** Bộ phân tích cú pháp Markdown chuẩn CommonMark/GFM nhanh và khả năng mở rộng plugin cao.
3. **Pygments:** Thư viện tô màu mã nguồn phổ biến hàng đầu trong hệ sinh thái Python (BSD License).
4. **WeasyPrint & Pango:** Động cơ kết xuất tài liệu HTML/CSS sang PDF in ấn A4 tại chỗ chất lượng cao, độc lập với trình duyệt.
5. **SQLite FTS5:** Động cơ cơ sở dữ liệu quan hệ nhúng hỗ trợ bộ chỉ mục toàn văn bản (Full-Text Search).

## 2.2. Giấy phép phát hành và các điều khoản pháp lý
MarkNote được phát hành chính thức theo giấy phép **MIT License** — một trong những giấy phép nguồn mở thông dụng và tự do nhất được tổ chức OSI công nhận.
- **Quyền hạn cấp cho người dùng:** Tự do sử dụng cho mục đích cá nhân lẫn thương mại, sao chép, chỉnh sửa, hợp nhất, xuất bản, phân phối và cấp phép lại mã nguồn.
- **Nghĩa vụ pháp lý:** Người sử dụng và phân phối lại chỉ cần giữ nguyên thông báo bản quyền gốc (Copyright Notice) và điều khoản miễn trừ trách nhiệm pháp lý của tác giả.
- **So sánh với các giấy phép khác:** So với GNU GPL (buộc dẫn xuất mã nguồn copyleft), giấy phép MIT mang tính chất tương thích cao (permissive), cho phép dễ dàng tích hợp vào nhiều môi trường triển khai khác nhau mà không tạo ra rào cản pháp lý.

## 2.3. Tính phổ biến của công cụ
- **Hỗ trợ đa nền tảng:** Ứng dụng được thiết kế ưu tiên hệ điều hành nguồn mở **Linux** (hỗ trợ mọi bản phân phối Ubuntu, Debian, Fedora, Arch Linux thông qua định dạng AppImage), đồng thời vận hành mượt mà trên **Windows 10/11** và **macOS**.
- **Đối tượng sử dụng phù hợp:** Kỹ sư phần mềm, chuyên gia an toàn thông tin (lập báo cáo pentest/audit), giảng viên, nhà nghiên cứu khoa học và sinh viên kỹ thuật có nhu cầu ghi chép ngoại tuyến và xuất bản tài liệu chuẩn A4.
- **Đánh giá từ cộng đồng:** Ứng dụng nhận được sự quan tâm nhờ khả năng chạy hoàn toàn offline không cần cấu hình mạng, bộ cài đặt gọn nhẹ và tốc độ tìm kiếm văn bản tức thời.

## 2.4. Tính mở của công cụ

### 2.4.1. Vị trí lưu trữ mã nguồn tập trung
Toàn bộ mã nguồn, tài liệu thiết kế và các bản phát hành được lưu trữ công khai, minh bạch tại kho lưu trữ GitHub chính thức:
- **Địa chỉ kho lưu trữ:** `https://github.com/dotlinux26/marknote`
- **Quản lý người tham gia:** Dự án áp dụng quy chuẩn quản lý qua GitHub Issues (báo cáo lỗi, đề xuất tính năng) và GitHub Discussions (trao đổi kỹ thuật cộng đồng).

### 2.4.2. Tham gia cộng đồng và quy trình đóng góp mã nguồn
Quy trình đóng góp tính năng mới tuân thủ nghiêm ngặt tài liệu hướng dẫn `CONTRIBUTING.md`:
1. **Fork & Branch:** Người đóng góp tiến hành tạo bản sao (fork) kho lưu trữ và tạo nhánh tính năng mới (`feature/ten-tinh-nang`).
2. **Quy chuẩn mã nguồn (Coding Standard):** Tuân thủ quy chuẩn PEP 8 của Python, ghi chú hàm tường minh và cập nhật bộ kiểm thử đơn vị (`tests/`).
3. **Pull Request & CI Automation:** Gửi Pull Request vào nhánh `main`. Hệ thống GitHub Actions tự động kích hoạt pipeline kiểm tra cú pháp, thực thi Unit Tests và kiểm tra đóng gói trên cả Linux và Windows.
4. **Code Review:** Trưởng dự án kiểm duyệt và phản hồi trong vòng 48 giờ trước khi hợp nhất.

> 📸 **[VỊ TRÍ CHÈN ẢNH - HÌNH 2.1: Giao diện kho lưu trữ GitHub dự án MarkNote]**
> - **Mục đích minh họa:** Chứng minh tính mở, minh bạch của dự án và hệ thống quản lý mã nguồn trực tuyến.
> - **Thao tác lấy ảnh:** Truy cập trình duyệt web vào địa chỉ `https://github.com/dotlinux26/marknote`, chụp toàn màn hình trang chủ kho lưu trữ (thể hiện rõ danh sách tệp, các tag phiên bản v1.2.5 và badge trạng thái CI/CD).

<div class="page-break"></div>

## 2.5. Giới thiệu bài toán: Ứng dụng ghi chú cá nhân MarkNote
- **Nguồn gốc bài toán:** Bắt nguồn từ nhu cầu tự chủ công cụ ghi chép khi làm việc trong các môi trường phòng thí nghiệm mạng nội bộ cách ly (Air-gapped Lab), nơi các ứng dụng đám mây không thể hoạt động.
- **Mục tiêu sản phẩm:** Xây dựng một trình biên soạn ghi chú cá nhân kết hợp xuất bản báo cáo kỹ thuật offline hoàn chỉnh với 5 trụ cột:
  1. *Soạn thảo song song:* Hiển thị trực quan hai khung hình chia đôi với độ trễ phản hồi cực thấp.
  2. *Cuộn đồng bộ (Sync Scroll):* Khắc phục triệt để hiện tượng lệch dòng khi tài liệu có nhiều ảnh hoặc bảng dài.
  3. *Tìm kiếm toàn văn FTS5:* Truy xuất thông tin tức thời theo từ khóa và bộ lọc nhãn `tag:`.
  4. *Mục lục thông minh (Smart TOC):* Tự động sinh mục lục phân cấp font chữ rõ ràng, tính đúng số trang in thực tế.
  5. *Đồ họa trực quan:* Tích hợp biểu đồ tròn Donut vector SVG và bảng biểu tự động wrap dòng chống tràn lề trang giấy.

## 2.6. Giấy phép phát hành phần mềm và kiểm kê bản quyền bên thứ ba
MarkNote tuân thủ nghiêm ngặt nguyên tắc cấp phép nguồn mở của OSI và FSF. Toàn bộ các gói thư viện phụ thuộc được kiểm kê và phân loại rõ ràng trong tệp `THIRD_PARTY_NOTICES.md`:

| Tên thư viện | Phiên bản | Giấy phép | Vai trò trong hệ thống | Trách nhiệm tuân thủ pháp lý |
|:---|:---:|:---:|:---|:---|
| **MarkNote** (Gốc) | 1.2.5 | **MIT** | Ứng dụng soạn thảo ghi chú | Công khai thông báo bản quyền Copyright 2026. |
| **PySide6 / Qt 6** | ≥ 6.5.0 | **LGPLv3** | Bộ thư viện giao diện đồ họa GUI | Sử dụng liên kết động (dynamic linking), cho phép người dùng thay thế thư viện Qt. |
| **markdown-it-py** | ≥ 3.0.0 | **MIT** | Bộ phân tích cú pháp GFM Markdown | Giữ nguyên thông báo bản quyền trong mã phân phối. |
| **Pygments** | ≥ 2.15.0 | **BSD-2-Clause** | Tô màu cú pháp mã nguồn | Đính kèm giấy phép BSD trong bản phân phối. |
| **WeasyPrint** | ≥ 60.0 | **BSD-3-Clause** | Động cơ xuất tài liệu PDF in ấn A4 | Bảo lưu điều khoản miễn trừ trách nhiệm pháp lý. |
| **SQLite3** | Nhúng | **Public Domain** | Cơ sở dữ liệu và chỉ mục FTS5 | Tự do sử dụng hoàn toàn không điều kiện. |

## 2.7. Thực hiện bài toán

### 2.7.1. Phân tích yêu cầu hệ thống

#### A. Yêu cầu chức năng (13 Use Cases cốt lõi)
Hệ thống được thiết kế phục vụ một tác nhân chính (**User** - Người dùng cá nhân) với toàn quyền quản trị cục bộ:

```text
               ┌─────────────────────────────────────────────────────────┐
               │                  HỆ THỐNG MARKNOTE                      │
               │                                                         │
               │   [UC01: Tạo ghi chú]        [UC07: Bật/Tắt Sync Scroll]│
               │   [UC02: Mở/Xem ghi chú]     [UC08: Tìm trong ghi chú]  │
    ┌──────┐   │   [UC03: Chỉnh sửa ghi chú]  [UC09: Thay thế văn bản]   │
    │ User │───┼──>[UC04: Xóa ghi chú]        [UC10: Tìm kiếm FTS5]      │
    └──────┘   │   [UC05: Gắn/Gỡ nhãn Tag]    [UC11: Xem danh sách theme]│
               │   [UC06: Live Preview song song] [UC12: Chuyển theme]   │
               │   [UC13: Xuất tài liệu PDF/HTML chuẩn in ấn]            │
               └─────────────────────────────────────────────────────────┘
```

> 📸 **[VỊ TRÍ CHÈN ẢNH - HÌNH 2.2: Sơ đồ Use Case tổng quát hệ thống MarkNote]**
> - **Mục đích minh họa:** Thể hiện trực quan 13 trường hợp sử dụng (Use Cases) của hệ thống.
> - **Nguồn lấy ảnh:** Tệp vector có sẵn tại `docs/diagrams/usecase.svg` trong thư mục dự án.

#### B. Yêu cầu phi chức năng
- **Tốc độ phản hồi:** Thời gian trễ render Live Preview được tối ưu hóa ở mức 300ms (debounce timer), đảm bảo không gây giật lag khi gõ văn bản nhanh.
- **Tiêu thụ tài nguyên:** Dung lượng chiếm dụng RAM khi hoạt động dưới 150MB, thời gian khởi động ứng dụng lạnh dưới 1.2 giây trên Linux.
- **Tính khả chuyển (Portability):** Khởi chạy độc lập không cần cài đặt môi trường Python máy khách thông qua bản đóng gói AppImage hoặc Portable Zip.

<div class="page-break"></div>

#### C. Thiết kế Cơ sở dữ liệu SQLite & Chỉ mục FTS5
Cơ sở dữ liệu được thiết kế tối giản, lưu trữ tập trung trong tệp duy nhất `~/.marknote/notes.db`:
- **Bảng `notes`:** Lưu trữ thông tin ghi chú (`id`, `title`, `content_md`, `created_at`, `updated_at`, `pinned`, `archived`).
- **Bảng `tags`:** Quản lý nhãn phân loại (`id`, `name UNIQUE`, `color`).
- **Bảng `note_tag`:** Bảng kết hợp thiết lập quan hệ nhiều - nhiều giữa ghi chú và nhãn (`note_id`, `tag_id`, khóa chính kép, cơ chế `ON DELETE CASCADE`).
- **Bảng ảo `notes_fts`:** Bảng ảo sử dụng mô-đun **FTS5** đánh chỉ mục toàn văn trên cột `title` và `content_md`. Ba Trigger cơ sở dữ liệu (`after insert`, `after update`, `after delete`) đảm bảo chỉ mục luôn được đồng bộ tự động trong thời gian thực.

> 📸 **[VỊ TRÍ CHÈN ẢNH - HÌNH 2.3: Sơ đồ thực thể liên kết ERD của cơ sở dữ liệu MarkNote]**
> - **Mục đích minh họa:** Kiến trúc dữ liệu và quan hệ giữa các bảng cơ sở dữ liệu và bảng ảo FTS5.
> - **Nguồn lấy ảnh:** Tệp sơ đồ chuẩn có sẵn tại `docs/diagrams/schema_er.png` (hoặc `schema_er.svg`).

---

### 2.7.2. Phân công và Hiện thực hóa hệ thống

#### A. Kiến trúc phân lớp phần mềm (MVC / DAO Pattern)
Hệ thống được tổ chức theo mô hình kiến trúc 3 tầng phân tách trách nhiệm rõ ràng:
1. **Tầng Giao diện (Presentation / View):**
   - `editor.py`: Vùng soạn thảo văn bản kế thừa từ `QPlainTextEdit`, tích hợp thước đếm số dòng (`LineNumberArea`), thanh tìm kiếm/thay thế và nút thao tác nhanh.
   - `preview.py`: Khung xem trước kết quả sử dụng `QWebEngineView` (nhân Chromium nhúng), hiển thị trực tiếp HTML/CSS.
   - `theme.py`: Trình nạp và chuyển đổi nóng CSS theme (`default.css`, `dark.css`, `github.css`).
2. **Tầng Xử lý Nghiệp vụ & Kết xuất (Controller / Logic):**
   - `main.py`: Cửa sổ điều phối trung tâm, xử lý các sự kiện người dùng và điều phối dữ liệu giữa editor và preview.
   - `exporter.py`: Engine xuất bản tài liệu độc lập; chuyển đổi Markdown thành file HTML tự chứa (nhúng Base64) và gọi WeasyPrint để kết xuất PDF A4 chuẩn in ấn.
3. **Tầng Truy cập Dữ liệu (Data Access Object - DAO):**
   - `db.py`: Đóng gói toàn bộ thao tác truy vấn SQLite thông qua các lớp chuyên trách `NoteDAO`, `TagDAO`, `SettingsDAO`.

> 📸 **[VỊ TRÍ CHÈN ẢNH - HÌNH 2.4: Sơ đồ lớp (Class Diagram) hệ thống MarkNote]**
> - **Mục đích minh họa:** Cấu trúc hướng đối tượng và quan hệ tương tác giữa các lớp chính trong mã nguồn `src/`.
> - **Nguồn lấy ảnh:** Tệp sơ đồ có sẵn tại `docs/diagrams/lop.svg`.

#### B. Hiện thực hóa các chức năng cốt lõi và hướng dẫn minh chứng

##### 1. Chức năng Soạn thảo song song & Cuộn đồng bộ (Sync Scroll)
Khi người dùng gõ văn bản ở khung soạn thảo bên trái, sự kiện `textChanged` kích hoạt bộ đếm thời gian debounce 300ms. Dữ liệu được đưa qua `MarkdownRenderer` kết xuất thành HTML và nạp vào `QWebEngineView`. Khi bật Sync Scroll, vị trí thanh cuộn editor được tính toán theo tỷ lệ phần trăm và chuyển đổi vị trí trang web tương ứng qua lệnh JavaScript.

> 📸 **[VỊ TRÍ CHÈN ẢNH - HÌNH 2.5: Giao diện soạn thảo song song với Live Preview và đánh số dòng Editor]**
> - **Mục đích minh họa:** Trực quan hóa tính năng soạn thảo GFM bên trái, xem trước kết quả bên phải, cột số dòng code (Line Numbers) và nút kích hoạt Sync Scroll.
> - **Thao tác lấy ảnh:** Khởi chạy MarkNote, mở một ghi chú kỹ thuật có bảng biểu và code block, bật tính năng `Sync Scroll`, chụp toàn màn hình ứng dụng.

##### 2. Chức năng Tìm kiếm toàn văn FTS5 và Lọc theo Tag
Người dùng nhập từ khóa tìm kiếm vào ô tra cứu trên thanh công cụ. Hệ thống tự động phân tách chuỗi: nếu phát hiện tiền tố `tag:tên_tag`, hệ thống thực hiện phép `JOIN` qua bảng `note_tag` kết hợp với toán tử `MATCH` của FTS5. Kết quả trả về danh sách ghi chú phù hợp kèm trích đoạn ngữ cảnh (`snippet`) tô màu vàng từ khóa tìm thấy.

> 📸 **[VỊ TRÍ CHÈN ẢNH - HÌNH 2.6: Tìm kiếm toàn văn bản siêu tốc bằng SQLite FTS5 kết hợp lọc Tag]**
> - **Mục đích minh họa:** Khả năng tìm kiếm nhanh theo cú pháp kết hợp (ví dụ: `apache tag:linux`) và hiển thị đoạn trích dẫn bôi vàng từ khóa.
> - **Thao tác lấy ảnh:** Nhập vào ô tìm kiếm từ khóa `tag:linux` hoặc một từ khóa có trong nội dung ghi chú, chụp danh sách kết quả hiển thị bên panel trái.

##### 3. Chức năng Mục lục thông minh (Smart TOC) và Biểu đồ Donut SVG
- **Smart TOC:** Cú pháp `[[TOC="MỤC LỤC BÁO CÁO" center no-bullet]]` chỉ quét các đề mục xuất hiện **bên dưới** vị trí TOC, tự động phân cấp font chữ (Cấp 1 in đậm chữ thẳng, Cấp 2 đậm nghiêng, Cấp 3 nghiêng bình thường).
- **Donut Chart:** Cú pháp khối ```` ```donut ```` tự động vẽ vòng tròn vector SVG sắc nét, tự động tính tổng số lượng và căn giữa trang, không viền hộp xám.

> 📸 **[VỊ TRÍ CHÈN ẢNH - HÌNH 2.7: Minh chứng Mục lục Smart TOC và Biểu đồ Donut Chart hiển thị trên Preview]**
> - **Mục đích minh họa:** Khả năng kết xuất trực quan mục lục phân cấp chuẩn mực và biểu đồ donut tròn trịa ngay trong cửa sổ ứng dụng.
> - **Thao tác lấy ảnh:** Soạn thảo một ghi chú chứa khối `[[TOC center no-bullet]]` và khối ```` ```donut ````, chụp khung Preview bên phải.

##### 4. Chức năng Kết xuất PDF in ấn chuẩn A4
Người dùng nhấn `Ctrl+P` hoặc chọn menu Export PDF. Ứng dụng tích hợp động cơ WeasyPrint để kết xuất:
- Tự động đánh số trang chân trang dạng `"Trang x / y"`.
- Bảng mục lục tự động sinh đường chấm dẫn (`leader dots`) kèm số trang in chính xác.
- Bảng dữ liệu tự động wrap dòng chữ dài và tự động lặp lại dòng tiêu đề (`thead`) khi bảng kéo dài qua nhiều trang.

> 📸 **[VỊ TRÍ CHÈN ẢNH - HÌNH 2.8: Tệp tài liệu PDF được xuất ra mở trên trình đọc PDF]**
> - **Mục đích minh họa:** Chứng minh chất lượng in ấn A4 sắc nét, mục lục có số trang thật và ngắt trang hoàn hảo.
> - **Thao tác lấy ảnh:** Mở tệp PDF đã xuất (ví dụ `mới.pdf` hoặc tệp báo cáo vừa xuất) bằng trình duyệt hoặc Adobe Acrobat/Evince, chụp trang mục lục và trang chứa bảng biểu.

<div class="page-break"></div>

#### C. Đóng gói đa nền tảng và Tự động hóa CI/CD
1. **Đóng gói Linux AppImage:** Sử dụng kịch bản `packaging/build_appimage_docker.sh` đóng gói toàn bộ thư viện Python, Qt và nhị phân WeasyPrint vào một tệp duy nhất `.AppImage`. Người dùng chỉ cần tải về, cấp quyền thực thi và chạy trên bất kỳ bản phân phối Linux nào (Ubuntu, Debian, Fedora, Arch, Alpine).
2. **Đóng gói Windows Portable:** Kịch bản `packaging/build_windows.ps1` đóng gói mã nguồn và nhúng sẵn `weasyprint.exe` kèm đầy đủ thư viện Pango/GLib DLLs vào thư mục chạy độc lập, nén thành tệp zip phân phối.
3. **Pipeline Tự động hóa CI/CD (GitHub Actions):** Thiết lập tệp quy trình `.github/workflows/build-and-release.yml`. Mỗi khi lập trình viên đẩy tag phiên bản mới (ví dụ `v1.2.5`), hệ thống GitHub Actions tự động khởi chạy môi trường Ubuntu và Windows trên đám mây để kiểm thử đơn vị, biên dịch và tự động đính kèm các gói cài đặt vào trang GitHub Releases.

> 📸 **[VỊ TRÍ CHÈN ẢNH - HÌNH 2.9: Pipeline tự động hóa CI/CD trên GitHub Actions và Trang phát hành Releases]**
> - **Mục đích minh họa:** Minh chứng quy trình kiểm thử và phát hành tự động của dự án nguồn mở.
> - **Thao tác lấy ảnh:** Truy cập mục Actions và Releases trên GitHub repo `dotlinux26/marknote`, chụp quy trình build thành công và danh sách các tệp tải về (`.AppImage`, `.deb`, `.zip`).

---

# Phần 3: KIẾN THỨC LĨNH HỘI VÀ BÀI HỌC KINH NGHIỆM

## 3.1. Nội dung đã thực hiện và Chuẩn đầu ra học phần đạt được
Thông qua quá trình nghiên cứu và phát triển sản phẩm MarkNote, nhóm sinh viên đã đạt được toàn diện các chuẩn đầu ra cốt lõi của học phần Phần mềm mã nguồn mở:
1. **Làm chủ quy trình phát triển PMNM:** Nắm vững từ khâu khảo sát bài toán, thẩm định và chọn lựa thư viện theo tiêu chuẩn khoa học (Bài 5), thiết kế hệ thống theo chuẩn công nghiệp (Bài 7, 8, 9) đến quản lý mã nguồn trên GitHub.
2. **Nâng cao năng lực kỹ thuật và giải quyết vấn đề:** Làm chủ việc xây dựng ứng dụng máy tính đa nền tảng với PySide6/Qt 6, khai thác tính năng tìm kiếm văn bản tốc độ cao SQLite FTS5 và xử lý bài toán xuất bản tài liệu PDF in ấn A4.
3. **Ý thức pháp lý và bản quyền:** Hiểu rõ bản chất các loại giấy phép nguồn mở (Permissive như MIT/BSD so với Copyleft như GPL/LGPL), thực hành nghiêm túc việc công bố bản quyền và kê khai thư viện bên thứ ba.
4. **Kỹ năng làm việc nhóm kỹ thuật:** Rèn luyện kỹ năng phân chia mô-đun, quản lý tiến độ, tích hợp mã nguồn thông qua Pull Requests và tự động hóa quy trình kiểm thử CI/CD.

## 3.2. Hướng phát triển và Đề xuất
- **Đánh giá tính khả thi và vừa sức:** Đề tài có tính ứng dụng thực tiễn cao, khối lượng công việc phù hợp với năng lực của nhóm sinh viên CNTT, sản phẩm đã hoàn thiện và chạy thực tế ổn định.
- **Những khó khăn đã vượt qua:** Xử lý sự tương thích của động cơ in WeasyPrint trên môi trường Windows (thiếu DLLs hệ thống) đã được giải quyết triệt để thông qua cơ chế đóng gói nhị phân độc lập.
- **Hướng phát triển trong tương lai:**
  - Bổ sung cơ chế mã hóa dữ liệu đầu cuối (End-to-End Encryption) cho các ghi chú nhạy cảm bằng thuật toán AES-256.
  - Xây dựng hệ thống Plugin kiến trúc mở, cho phép cộng đồng tự phát triển thêm các bộ render sơ đồ (Mermaid.js, PlantUML) và widget mở rộng.
  - Phát triển ứng dụng di động đọc ghi chú đồng bộ cục bộ thông qua giao thức ngang hàng (P2P / Syncthing).

<div class="page-break"></div>

# TÀI LIỆU THAM KHẢO

1. **Bộ Giáo dục và Đào tạo / Trường Đại học Công nghiệp Hà Nội**, *Đề cương bài giảng học phần Phần mềm mã nguồn mở* (Bài 5: Lựa chọn và đánh giá PMNM; Bài 7: Tổng quan các hệ thống PMNM; Bài 8: Cơ sở dữ liệu mã nguồn mở; Bài 9: Kiến trúc và phát triển PMNM), Hà Nội, 2024–2026.
2. **TS. Hà Quốc Trung**, *Giáo trình Phần mềm mã nguồn mở và Hệ điều hành Linux*, Nhà xuất bản Bách Khoa Hà Nội, 2018.
3. **Open Source Initiative (OSI)**, *The Open Source Definition (Annotated)*, [Online]. Available: `https://opensource.org/osd`.
4. **Free Software Foundation (FSF)**, *What is Free Software? The Four Essential Freedoms*, [Online]. Available: `https://www.gnu.org/philosophy/free-sw.html`.
5. **The Qt Company**, *Qt for Python (PySide6) Documentation & Architecture Guides*, [Online]. Available: `https://doc.qt.io/qtforpython-6/`.
6. **SQLite Development Team**, *SQLite FTS5 Extension (Full-Text Search Engine Version 5)*, [Online]. Available: `https://www.sqlite.org/fts5.html`.
7. **CourtBouillon**, *WeasyPrint Document Engine & CSS Paged Media Module Level 3*, [Online]. Available: `https://doc.courtbouillon.org/weasyprint/`.
8. **Tom Callaway**, *Points of FAIL (PoF) - Evaluating Open Source Project Maturity*, FOSS Community Guidelines, 2011.
