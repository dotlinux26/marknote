# Danh sách tính năng MarkNote đã triển khai

> Tài liệu tổng hợp đối chiếu với **kế hoạch 13 use case** (KEHOACH_MarkNote.md)
> cộng thêm các tính năng mở rộng được bổ sung theo quá trình phát triển.
> Dùng cho nhóm báo cáo kiểm kê "đã làm được gì".

## A. Đối chiếu 13 use case trong kế hoạch

| UC | Tên | Triển khai | Ghi chú |
|----|-----|:----------:|---------|
| UC01 | Tạo note mới | x | `Ctrl+N`, nhập tiêu đề |
| UC02 | Mở và xem note | x | click dòng trong danh sách |
| UC03 | Lưu note | x | `Ctrl+S`, cảnh báo khi chưa lưu |
| UC04 | Xóa note | x | `Ctrl+D`, hộp thoại xác nhận |
| UC05 | Gán/giữa tag | x | nút Tags / New tag |
| UC06 | Xem preview song song | x | render sau 0,3s khi gõ |
| UC07 | Đồng bộ cuộn | x | `Ctrl+Shift+S`, nhớ cài đặt |
| UC08 | Tìm trong note | x | `Ctrl+F`, highlight mọi kết quả |
| UC09 | Tìm và thay thế | x | `Ctrl+H`, Replace/Replace All |
| UC10 | Tìm toàn kho FTS5 | x | `apache tag:linux`, snippet tô màu |
| UC11 | Xem danh sách theme | x | Settings > Appearance |
| UC12 | Chọn/đổi theme | x | áp tức thì, không cần restart |
| UC13 | Xuất HTML/PDF | x | HTML 1 file; PDF A4 + số trang |

## B. Tính năng mở rộng (ngoài 13 UC)

| Tính năng | Mô tả |
|-----------|-------|
| Đổi tên note inline | Nút bút **✎** (hoặc `F2`) cạnh tên note; Enter/click ra ngoài lưu, Esc hủy |
| Export Markdown | File > Export Markdown: lưu nội dung đang soạn ra file `.md` |
| Mục lục tự động `[[TOC]]` | Sinh mục lục từ heading h1–h6; đổi tiêu đề bằng `[[TOC="Mục lục"]]` |
| TOC kiểu Word khi in PDF | Gạch chấm `.....` + số trang thật tính tự động (`target-counter` + `leader`) |
| Link nhảy trong PDF | Bấm dòng mục lục (hoặc bất kỳ link nội bộ `#id`) nhảy tới đúng mục |
| Ngắt trang khi xuất | HTML `<div style="page-break-after: always;"></div>` |
| Số trang PDF | "trang / tổng số trang" ở chân mỗi trang |
| Chống cắt trang | code/bảng/blockquote không bị đứt giữa trang; heading không đứng cuối trang |
| Giao diện sáng ép cứng | Palette sáng cố định chống xung đột với theme tối của hệ điều hành |
| Bo góc 2px, nút phẳng | Tinh chỉnh giao diện theo yêu cầu |
| Hiển thị tag của note | Nút Tags hiện tên tag của note đang mở |
| Đánh dấu snippet tìm kiếm | Từ khóa FTS5 được tô nền vàng trong danh sách kết quả |

## C. Các thành phần kiến trúc

| Mô-đun | Vai trò |
|--------|---------|
| `src/main.py` | Cửa sổ chính, dàn ý màn hình, điều phối 13 UC + mở rộng, tạo thanh tiêu đề có rename inline |
| `src/editor.py` | Ô soạn thảo, tìm/thay thế (UC08–09), bảng điều hướng bên trái (UC10–11) |
| `src/preview.py` | Renderer GFM (markdown-it-py + plugin tasklist/footnote + Pygments), pane WebEngine, sync scroll, cú pháp `[[TOC]]` |
| `src/db.py` | DbManager, NoteDAO/TagDAO/SettingsDAO, schema SQLite + FTS5 + trigger |
| `src/theme.py` | Quản lý các file CSS theme trong `~/.marknote/themes/` |
| `src/settings.py` | Hằng số, đường dẫn, hộp thoại Appearance (UC11–12) |
| `src/exporter.py` | Xuất HTML/PDF; `@page` A4, số trang, TOC kiểu Word (UC13) |

## D. Hướng dẫn minh chứng trong báo cáo

- File **`GFM_TEMPLATE.md`** (root repo): chạy `make run`, `Ctrl+N`, dán nội
  dung file → chụp preview từng phần.
- Sơ đồ: `docs/diagrams/` gồm use case, tuần tự, lớp, ER đã render SVG/PNG.
- Thao tác PDF: File > Export PDF → mô tả số trang và bảng mục lục có số trang.
- Cơ sở dữ liệu: `docs/SCHEMA_CSDL.md`.

## E. Phạm vi cố ý không làm

- Không đồng bộ lên mây, không tài khoản — **100% offline**.
- Không icon/emoji đồ họa (chỉ dùng ký tự văn bản như ✎), tối giản giao diện.
- Không đóng gói biên dịch tĩnh một-bin (ngoài phạm vi kế hoạch; môi trường
  chạy dùng `venv`).
- Không chế độ dark tự động theo giờ (kế hoạch nêu rõ không thực hiện).