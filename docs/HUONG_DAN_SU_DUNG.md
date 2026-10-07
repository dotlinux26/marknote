# Hướng dẫn sử dụng MarkNote

> Tài liệu này mô tả cách dùng từng tính năng của MarkNote.
> Phù hợp cho người mới và cho nhóm làm báo cáo trích dẫn quy trình sử dụng.

## 1. Cài đặt và chạy

Yêu cầu: Python 3.11+ (đã thử nghiệm trên Python 3.13).

```bash
# Tạo môi trường ảo riêng (khuyên dùng)
python3 -m venv .venv --system-site-packages
source .venv/bin/activate
pip install -r requirements.txt

# Chạy ứng dụng
make run
```

Hoặc cài vào hệ thống:

```bash
sudo make install
marknote
```

Cấu trúc thư mục dữ liệu:

| Đường dẫn | Nội dung |
|-----------|----------|
| `~/.marknote/notes.db` | Cơ sở dữ liệu SQLite (notes, tags, settings, FTS5) |
| `~/.marknote/themes/` | Các file theme CSS dùng cho preview và xuất bản |

## 2. Màn hình chính

Gồm 3 vùng, chia bằng thanh kéo:

1. **Bên trái — Bảng điều hướng**: ô tìm kiếm toàn kho, danh sách tag để lọc, danh sách note.
2. **Giữa — Soạn thảo**: ô nhập Markdown (xuất hiện placeholder khi chưa mở note).
3. **Phải — Preview**: kết quả render trực tiếp theo theme CSS đang chọn, tự cập nhật khi gõ (debounce 0,3 giây).

Thanh trên gồm menu File / Edit / View / Settings / Help và toolbar các nút
New, Save, Delete, Find, Replace, Sync Scroll, Settings.

## 3. Danh sách phím tắt

| Phím | Chức năng |
|------|-----------|
| `Ctrl+N` | Tạo note mới |
| `Ctrl+S` | Lưu note hiện tại |
| `F2` | Đổi tên note (inline ngay trên thanh tên) |
| `Ctrl+D` | Xóa note (có xác nhận) |
| `Ctrl+F` | Tìm trong note hiện tại |
| `Ctrl+H` | Tìm và thay thế |
| `Ctrl+Shift+S` | Bật/tắt đồng bộ cuộn editor với preview |
| `Ctrl+Q` | Thoát |

Lưu ý: trong hộp thoại Tìm, `Enter` xuống kết quả tiếp, `Shift+Enter`
quay lại kết quả trước, `Esc` đóng hộp thoại.

## 4. Quản lý note

### 4.1. Tạo note
`Ctrl+N` → nhập tiêu đề → Enter. Note mới được ghi vào database và mở ra.

### 4.2. Lưu note
`Ctrl+S`. Hệ thống báo "Note saved". Nếu có thay đổi chưa lưu mà bạn mở note
khác / thoát chương trình, hộp thoại sẽ hỏi **Save / Discard / Cancel**.

### 4.3. Đổi tên note
Bấm nút bút **✎** ngay cạnh tên note (hoặc `F2`):

- Ô tên hiện tại tự chỉnh sửa được (inline edit), toàn bộ chữ được chọn sẵn.
- Nhấn **Enter** hoặc **bấm chuột ra ngoài** → lưu tên mới và cập nhật
  danh sách bên trái.
- Nhấn **Esc** → hủy, giữ tên cũ.

### 4.4. Xóa note
`Ctrl+D` (hoặc File > Delete) → xác nhận Yes/No. Không thể hoàn tác.

## 5. Tag

- Nút **Tags** cạnh tên note hiển thị các tag của note đang mở
  (mỗi tag nối bằng dấu phẩy; không có tag thì hiện chữ "Tags").
- Bấm nút Tags → bảng chọn: tick/bỏ tick để gán hoặc bỏ tag; mục
  **New tag...** tạo tag mới.
- Bên trái, mục **Filter by tag** lọc danh sách note theo tag.

## 6. Tìm kiếm

### 6.1. Tìm trong note hiện tại
`Ctrl+F` → gõ từ khóa → highlight mọi chỗ trùng, kèm ô "Match case".
`Ctrl+H` mở thêm phần Replace / Replace All.

### 6.2. Tìm toàn kho (FTS5)
Gõ vào ô tìm phía trên bảng điều hướng:

| Cú pháp | Kết quả |
|---------|---------|
| `apache` | Note chứa từ "apache" |
| `apache tag:linux` | Note chứa "apache" và thuộc tag "linux" |
| `linux curl` | Note chứa cả hai từ |

Kết quả hiện câu trích (snippet), từ khóa được **tô màu vàng** `#fff8c5`.

Cú pháp đầy đủ Điểm theo SQLite FTS5 (AND, OR, NOT, `*`, `"cụm từ"`, …).

## 7. Giao diện và theme

- **Settings > Appearance** mở hộp thoại chọn theme CSS (Preview theme).
  Các theme mặc định: `default`, `github`, `dark`.
- Chọn theme mới → preview và bản xuất HTML/PDF vẽ lại ngay bằng CSS đó,
  không cần khởi động lại.
- Theme là file CSS thật trong `~/.marknote/themes/`; bạn có thể bỏ thêm
  file `.css` của riêng mình vào đó.
- Giao diện chương trình (khung cửa sổ) luôn dùng tông màu sáng nhẹ, bo góc
  2px, nút phẳng không nền, không bị lệ thuộc theme tối của hệ điều hành.

## 8. Xuất bản

### 8.1. Export HTML
File > Export HTML → chọn vị trí lưu. File HTML **tự chứa** toàn bộ CSS
theme nên mở ở đâu cũng đẹp như nhau (dùng được offline).

### 8.2. Export PDF
File > Export PDF → chọn vị trí lưu. Khổ **A4**, lề 18/16/22mm:

- Mỗi trang in số trang dạng **"1 / 5"** ở góc dưới giữa.
- Mục lục tự động (xem mục "Markdown — cú pháp" dưới đây) khi xuất PDF có
  **gạch chấm dẫn tới số trang thật** của từng mục, giống mục lục trong Word.
  Bấm vào một dòng trong mục lục sẽ **nhảy tới đúng mục**.
- Cần thư viện `weasyprint`. Nếu thiếu, chương trình báo hướng dẫn cài.

### 8.3. Export Markdown
File > Export Markdown → chọn vị trí lưu → ghi đúng nội dung Markdown
đang soạn (kể cả đoạn chưa lưu) ra file `.md`.

## 9. Đồng bộ cuộn (Sync Scroll)

Bật theo mặc định: kéo cuộn bên soạn thảo thì preview cuộn theo tương ứng.
Tắt/bật bằng `Ctrl+Shift+S`; trạng thái được ghi nhớ qua mỗi lần mở chương trình.

## 10. Thử nhanh đầy đủ cú pháp

Trong repo có file **`GFM_TEMPLATE.md`** — bản demo đầy đủ mọi cú pháp
(heading, emphasis, link, image, blockquote, list, task, table, code,
footnote, hard-break, escape, raw HTML, page break, TOC). Mở file và copy
nội dung vào một note mới để xem từng loại render ra sao.

## 11. Vị trí dữ liệu và sao lưu

Toàn bộ dữ liệu nằm trong `~/.marknote/`:

```bash
# Sao lưu
cp -r ~/.marknote ~/backup-marknote

# Xem trực tiếp dữ liệu bằng sqlite3
sqlite3 ~/.marknote/notes.db ".tables"
sqlite3 ~/.marknote/notes.db "SELECT id, title FROM notes;"
```