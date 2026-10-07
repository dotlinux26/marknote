# MarkNote

Ứng dụng ghi chú **Markdown offline** cho Linux (và cả Windows/macOS),
viết bằng **Python + PySide6 (Qt 6)**: soạn thảo bên trái, xem trước kết quả
bên phải song song, chọn theme CSS, tìm kiếm toàn kho (FTS5) và xuất ra
HTML / PDF / Markdown — tất cả **không cần kết nối mạng**.

## Tính năng chính

- **Soạn thảo Markdown (GFM)**: heading, bảng, task list, footnote, code
  block tô màu (Pygments), table, raw HTML…
- **Xem trước song song**: gõ bên trái, render bên phải sau 0,3 giây; đồng bộ
  cuộn editor với preview (`Ctrl+Shift+S`).
- **Quản lý note**: tạo / lưu / xóa, **đổi tên inline** ngay trên thanh tiêu đề
  (nút bút ✎ hoặc phím `F2`).
- **Tag**: gán/gỡ tag, tạo tag mới, lọc danh sách theo tag.
- **Tìm kiếm toàn kho (SQLite FTS5)**: nhanh, hỗ trợ nhiều từ khóa và
  `tag:linux`, hiển thị snippet có tô màu từ khóa.
- **Tìm / thay thế** trong note (`Ctrl+F`, `Ctrl+H`).
- **Theme CSS**: `default`, `github`, `dark` – đổi theme không cần khởi động lại.
- **Xuất bản** cùng một theme:
  - Xuất **HTML** (một file tự chứa, dùng được offline).
  - Xuất **PDF** (A4): mục lục tự động `[[TOC]]` kiểu Word có **số trang thật**,
    link nhảy, số trang "x / y" ở chân trang, ngắt trang, chống cắt trang.
  - Xuất **Markdown** (`.md`).
- Giao diện tiếng Anh, palette sáng ổn định (chống xung đột theme tối của HĐH).

## Yêu cầu hệ thống

| Hệ điều hành | Hỗ trợ | Ghi chú |
|--------------|:------:|---------|
| Linux (x86_64) | ✅ | bản chính, cần Python 3.10+ và thư viện pango cho chức năng PDF |
| Windows (x86_64) | ✅ | cài như mã nguồn; chức năng PDF cần thêm Pango (xem hướng dẫn) |
| macOS | 🟡 | code nền tảng nên chạy được, chưa phát hành chính thức |

- Python **3.10 trở lên**.
- `pip` + `venv` (hoặc công cụ đóng gói như trong `docs/HUONG_DAN_CAI_DAT.md`).
- **pango ≥ 1.44** (để xuất PDF bằng WeasyPrint): luôn có sẵn trên hầu hết
  máy Linux desktop; máy tối giản cài thêm vài gói (xem bảng bên dưới).

## Cài đặt nhanh (Linux)

Cách đơn giản nhất là chạy trong venv:

```bash
python3 -m venv .venv --system-site-packages
source .venv/bin/activate
pip install -r requirements.txt
```

Còn thiếu thư viện pango cho xuất PDF? Cài theo distro:

| Distro | Lệnh |
|--------|------|
| Ubuntu/Debian | `sudo apt install libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz-subset0` |
| Fedora/RHEL | `sudo dnf install pango` |
| Arch/Manjaro | `sudo pacman -S pango` |
| Alpine | `sudo apk add so:libpango-1.0.so.0 so:libgobject-2.0.so.0` |

Cài vào hệ thống (tạo lệnh `marknote`):

```bash
sudo make install
```

## Chạy ứng dụng

```bash
make run
```

hoặc:

```bash
source .venv/bin/activate
python src/main.py
```

> **Cài đặt chi tiết từng bước cho Linux, Windows, macOS và cách đóng gói**
> (AppImage, file chạy trên Windows) xem tại
> **[`docs/HUONG_DAN_CAI_DAT.md`](docs/HUONG_DAN_CAI_DAT.md)**.

## Cách dùng nhanh

| Phím | Chức năng |
|------|-----------|
| `Ctrl+N` | Tạo note mới |
| `Ctrl+S` | Lưu note |
| `F2` | Đổi tên note (Enter để lưu, Esc để hủy) |
| `Ctrl+D` | Xóa note |
| `Ctrl+F` | Tìm trong note |
| `Ctrl+H` | Tìm và thay thế |
| `Ctrl+Shift+S` | Đồng bộ cuộn on/off |
| `Ctrl+Q` | Thoát |

- Mục lục tự động: viết `[[TOC]]` (hoặc `[[TOC="Mục lục của tôi"]]`) vào
  đầu note.
- Ngắt trang khi xuất PDF:
  `<div style="page-break-after: always;"></div>`.
- Dữ liệu người dùng nằm tại `~/.marknote/` (`notes.db` + thư mục `themes`).

## Cấu trúc dự án

```
marknote/
  Makefile  LICENSE  README.md  CHANGELOG  requirements.txt
  GFM_TEMPLATE.md        bản demo đầy đủ cú pháp để thử nhanh
  src/main.py            cửa sổ chính, điều phối mọi tính năng
  src/db.py              SQLite + FTS5 (NoteDAO, TagDAO, SettingsDAO)
  src/editor.py          ô soạn thảo + bảng điều hướng + tìm/thay thế
  src/preview.py         renderer Markdown, pane WebEngine, cú pháp [[TOC]]
  src/exporter.py        xuất HTML/PDF (đánh số trang, mục lục kiểu Word)
  src/theme.py           quản lý file CSS theme
  src/settings.py        hằng số, đường dẫn, hộp thoại Appearance
  assets/themes/         default.css, github.css, dark.css
  docs/                  tài liệu chi tiết, sơ đồ, báo cáo
  dist/                  sản phẩm đóng gói (AppImage, bản Windows) – tạo ra khi build
```

## Đóng gói & phân phối

- **Linux đa distro**: build **AppImage** bằng PyInstaller (x86_64) — một file
  chạy được trên Ubuntu/Debian/Fedora/Arch/Manjaro… Xem hướng dẫn trong
  `docs/HUONG_DAN_CAI_DAT.md`.
- **Windows**: build trên máy Windows bằng `build_windows.ps1` (PyInstaller)
  hoặc chạy trực tiếp từ mã nguồn bằng venv. **Không** cross-compile Linux→
  Windows được.
- **macOS**: dựng bằng PyInstaller trên máy macOS nếu cần.

## Sao lưu dữ liệu

Toàn bộ dữ liệu nằm trong một thư mục `~/.marknote`:

```bash
cp -r ~/.marknote ~/backup-marknote        # sao lưu
sqlite3 ~/.marknote/notes.db ".tables"     # xem trực tiếp bằng sqlite3
```

Xóa toàn bộ dữ liệu người dùng:

```bash
rm -rf ~/.marknote
```

## Tài liệu chi tiết

- `docs/INDEX_BAO_CAO.md` — chỉ mục toàn bộ tài liệu, gợi ý phân vai báo cáo.
- `docs/HUONG_DAN_CAI_DAT.md` — **cài đặt chi tiết** mọi HĐH + đóng gói.
- `docs/HUONG_DAN_SU_DUNG.md` — hướng dẫn sử dụng từng tính năng.
- `docs/HUONG_DAN_CU_PHAP_MARKDOWN.md` — bảng tra cú pháp + cú pháp riêng.
- `docs/DANH_SACH_TINH_NANG.md` — kiểm kê tính năng đối chiếu 13 UC.
- `docs/VAN_DE_KY_THUAT.md` — kiến trúc, lựa chọn thư viện, vấn đề kỹ thuật.
- Các tài liệu `SCHEMA_CSDL`, `MO_TA_USE_CASE`, `SODO_*`, `TONG_HOP_GFM`.

## Giấy phép

Xem file `LICENSE` (MIT).