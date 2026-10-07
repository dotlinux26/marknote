# Các vấn đề kỹ thuật và quyết định thiết kế

> Tài liệu dành cho nhóm báo cáo: giải thích "tại sao làm như vậy", các thư
> viện dùng, các khó khăn gặp phải và cách xử lý.

## 1. Tổng quan kiến trúc

Ứng dụng desktop viết bằng **Python** + **PySide6 (Qt 6)**:

```
┌────────────────────────────────────────────┐
│  UI: main.py - editor.py - preview.py     │
│      - settings.py (Qt Widgets, Fusion)   │
├────────────────────────────────────────────┤
│  Logic: theme.py - exporter.py            │
│  Render: preview.py (markdown-it-py +     │
│          Pygments + QWebEngineView)        │
├────────────────────────────────────────────┤
│  Dữ liệu: db.py -> SQLite (notes.db)      │
│           FTS5 + trigger + 3 bảng chính    │
└────────────────────────────────────────────┘
```

Tách thành 8 module trong `src/` để mỗi lớp có một trách nhiệm, dễ kiểm thử
và dễ đối chiếu với use case trong kế hoạch.

## 2. Lựa chọn thư viện

| Thành phần | Thư viện | Lý do chọn |
|-----------|----------|-----------|
| GUI | PySide6 (Qt6) | Qt là bộ toolkit bản xứ mạnh; giấy phép LGPL; có sẵn WebEngine để hiển thị HTML/CSS |
| Render Markdown | markdown-it-py (preset `gfm-like`, `linkify`) | Theo chuẩn CommonMark + GFM; nhanh, plugin mở rộng, cộng đồng lớn |
| Plugin | mdit-py-plugins (tasklists, footnote) | Bổ sung đúng 2 tính năng GFM còn thiếu |
| Tô màu code | Pygments | Hỗ trợ hàng trăm ngôn ngữ, xuất ra HTML với style **inline** (tự chứa, dùng offline) |
| Xem trước | QWebEngineView (Chromium) | Cùng một engine với trình duyệt nên HTML/CSS hiển thị chính xác |
| Xuất PDF | WeasyPrint | Nguyên render HTML→PDF tại chỗ 100% offline; hỗ trợ `@page`, `target-counter`, `leader()`, `counter(pages)` |

Lưu ý: PySide6 gồm gói `PySide6-Essentials` + `PySide6-Addons`
(`PySide6-QtWebEngine` nằm trong Addons → phải cài cả hai).

## 3. Dữ liệu và tìm kiếm FTS5

- SQLite 1 file tại `~/.marknote/notes.db`, không cần máy chủ.
- Bảng `notes` (title, content_md, created_at, updated_at, pinned, archived)
  + bảng `tags` + bảng quan hệ `note_tag`.
- Bảng ảo `notes_fts` dùng **FTS5**; 3 trigger `after insert/update/delete`
  giữ cho chỉ mục luôn khớp dữ liệu (kể cả khi đổi tên note).
- FTS5 `MATCH` hỗ trợ `tag:` đi cùng qua JOIN note_tag; kết quả dùng
  `snippet()` để trích đoạn và đánh dấu từ khóa bằng ký tự điều khiển
  `char(1)`/`char(2)`.

## 4. Render và export dùng chung một "nguồn"

Cùng một chuỗi HTML sinh bởi `MarkdownRenderer` được tái sử dụng:
preview (setHtml), Export HTML, Export PDF (WeasyPrint). CSS theme nội tuyến
vào HTML nên file xuất ra là một file tự chứa.

Mở rộng quan trọng: **core rule `anchors_toc`** trong markdown-it:
- Gắn `id` cho mọi heading (slug bỏ dấu nhờ `unicodedata`, duy nhất bằng bộ
  đếm) → đích nhảy cho link nội bộ.
- Thay cú pháp `[[TOC]]` / `[[TOC="Tiêu đề"]]` bằng khối `<div class="toc">`
  sinh từ danh sách heading đã thu thập.

## 5. Mục lục kiểu Word trong PDF

PDF không "biết" số trang trước, nên ta không thể chèn số trang tĩnh. Giải
pháp: thêm CSS print-only vào đường xuất PDF:

```css
@media print {
  .toc a::after {
    content: leader('. ') target-counter(attr(href), page);
  }
}
```

- `target-counter(attr(href), page)` hỏi WeasyPrint: "trang chứa phần tử
  trỏ đến trong href là trang mấy" → tính chính xác tại thời điểm dàn trang.
- `leader('. ')` vẽ chuỗi chấm choán khoảng trống tới số trang.
- Chỉ khai báo trong `@media print` và chỉ nối thêm khi export PDF, nên
  preview trên màn hình của mục lục không bị lệch/thiếu số trang.

Dùng màu từ biến CSS `--fg-*` nên tự thích nghi theo các theme (dark…).

## 6. Môi trường chạy và venv

Trên máy phát triển, gói PySide6 cài bằng `pip system` bị thiếu (import
`PySide6.QtCore` lỗi), cùng chuẩn giữ nguyên môi trường hệ thống. Giải pháp:
`python3 -m venv --system-site-packages .venv`:
- `.venv` chứa PySide6-Essentials 6.9.2 + PySide6-Addons 6.9.2 + mdit-py-plugins;
- các thư viện thuần Python ổn định (markdown-it-py, Pygments, WeasyPrint)
  dùng từ hệ thống qua `--system-site-packages`.
- Lệnh chạy: `make run` (tự nhận `.venv` nếu có), an toàn hơn `python3 src/main.py`.

Mạng cài gói chậm → dùng repo local / mirror nội bộ cho các wheel lớn (PySide6).

## 7. Vấn đề hiển thị Qt trên OS tối

Khi hệ điều hành dùng theme tối, widget không được QSS bao phủ (ví dụ danh
sách thả xuống của QComboBox, list item) có thể hiển thị **chữ đen nền đen**
hoặc **chữ trắng nền trắng**. Xử lý để tương phản ổn định:

1. **Ép một palette sáng đầy đủ** qua `QPalette` khi khởi tạo
   (Window/Text/Highlight/Disabled…).
2. Phủ QSS rõ ràng cho `QComboBox QAbstractItemView`,
   `QListWidget::item:selected`, `QMenu::item`, `QToolButton`…

Kết quả: giao diện luôn sáng nhẹ, đọc rõ, không phụ thuộc theme của môi trường.

## 8. WebEngine và canvas

- Phải gọi `QApplication.setAttribute(AA_ShareOpenGLContexts)` **trước** khi
  tạo QApplication, nếu không QWebEngineView lỗi khi khởi tạo.
- Trong môi trường headless/thử nghiệm dùng:
  `QT_QPA_PLATFORM=offscreen QTWEBENGINE_CHROMIUM_FLAGS="--no-sandbox --disable-gpu"`.
- Nội dung render kiểm chứng bằng cách đọc lại JS trong page
  (`runJavaScript`) và chụp vùng màn hình thật.

## 9. Các mốc cài đặt và lỗi làm móng

- `QLineEdit::returnPressed` + `editingFinished` gây commit kép → cờ
  `_editing` chặn.
- QMessageBox modal trong test tự động → test phải patch để không treo.
- `find()`/thay thế: xử lý nhạy cảm hoa/thường bằng `re.IGNORECASE`,
  Replace All đi từ cuối lên đầu để không lệch vị trí.
- Dấu câu tiếng Việt trong slug: dùng `unicodedata NFKD` bỏ dấu trước khi
  tạo id, đảm bảo link nội bộ dùng utf-8 ổn định.

## 10. Hạn chế đã biết và hướng mở rộng

- **Chưa** đóng gói thành binary tĩnh 1 file (ngoài phạm vi kế hoạch).
- `[[TOC]]` khi xuất HTML chỉ là mục lục nhảy bằng id, không có số trang
  (ác thực tính `target-counter` là riêng PDF).
- Dữ liệu nằm ở `~/.marknote` — nếu cần danh mục + cấu hình thêm, người dùng
  có thể mở `settings.py` (APP_DIR/DB_PATH…).
- Hướng mở: chủ đề dark cho toàn cửa sổ (không chỉ preview), trình in thử
  trước PDF, gói PyInstaller nếu từng cần phân phối.