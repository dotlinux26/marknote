# Hướng dẫn cài đặt chi tiết MarkNote (Linux / Windows / macOS)

> Mục tiêu: cài được MarkNote trên **mọi bản phân phối Linux**, trên
> **Windows**, và hiểu rõ cách **đóng gói tĩnh** (AppImage / file .exe) —
> kể cả những giới hạn cần biết.

## 0. Tóm tắt ngắn

| Hệ điều hành | Cách chạy nhanh nhất | Ghi chú PDF | Đóng gói tĩnh |
|--------------|----------------------|-------------|---------------|
| Linux | venv (`make run`) | cần gói `pango` của distro | **AppImage** (1 file) |
| Windows | venv (PowerShell) | cần Pango qua **MSYS2** | `dist\marknote\marknote.exe` |
| macOS | venv (Homebrew) | `brew install weasyprint` | PyInstaller dựng trên máy macOS |

Mọi cách cài đều chạy **cùng một mã nguồn**, không có bản "khác" cho từng OS.

---

## 1. Cài đặt trên Linux

### 1.1. Chạy bằng môi trường ảo (khuyên dùng, không cần quyền root)

Yêu cầu: Python **3.10+** và `pip`/`venv` (các distro đều có).

```bash
cd marknote
python3 -m venv .venv --system-site-packages
.venv/bin/pip install -r requirements.txt
make run
```

- Cờ `--system-site-packages` giúp venv dùng sẵn các thư viện hệ thống
  (markdown-it-py, Pygments, WeasyPrint…) nên nhẹ hơn.
- PySide6 (giá trị ~250 MB) cần cài vào venv vì không phải lúc nào hệ thống
  cũng có sẵn.

### 1.2. Cài pango để xuất PDF

WeasyPrint chuyển HTML ra PDF nhờ thư viện **Pango** (đọc văn bản, tạo glyph,
ngắt dòng). Trên máy Linux desktop thường đã có sẵn. Nếu thiếu, PDF export sẽ
báo "Missing Pango libraries". Cài theo distro:

| Distro | Lệnh cài |
|--------|----------|
| Ubuntu / Debian | `sudo apt install libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz-subset0` |
| Fedora / RHEL / Rocky | `sudo dnf install pango` |
| openSUSE | `sudo zypper install pango` |
| Arch / Manjaro | `sudo pacman -S pango` |
| Alpine | `sudo apk add so:libpango-1.0.so.0 so:libgobject-2.0.so.0` |
| Gentoo | `sudo emerge -av pango` |

Kiểm tra đã có chưa:

```bash
pango-view --version
```

### 1.3. Cài vào hệ thống (tạo lệnh `marknote`)

```bash
sudo make install
marknote
```

Cách gỡ:

```bash
sudo make uninstall
```

### 1.4. Chạy bằng AppImage (một file cho mọi distro)

Nguyên tắc: `make appimage` (hoặc script Docker) đóng gói sẵn **Python +
PySide6 + QtWebEngine + Pygments + WeasyPrint** vào **một file** `MarkNote-1.1-x86_64.AppImage`.
Không cần cài Python, không cần distro cụ thể.

```bash
chmod +x MarkNote-1.1-x86_64.AppImage
./MarkNote-1.1-x86_64.AppImage
```

Nếu máy chưa có FUSE (cảnh báo khi chạy):

```bash
APPIMAGE_EXTRACT_AND_RUN=1 ./MarkNote-1.1-x86_64.AppImage
```

Ghi vào menu ứng dụng: với GNOME/KDE, di chuyển `.AppImage` vào
`~/.Applications` hoặc nháy đúp trong trình quản lý file.

**Giới hạn glibc cần biết** (quan trọng): AppImage "kế thừa" glibc của máy
build. Bản build trên máy hiện tại (glibc 2.42) chạy tốt trên các distro hiện
đại (Ubuntu 23.04+, Debian 12+, Fedora 39+…). Muốn AppImage chạy được cả các
bản cũ hơn (Ubuntu 20.04, Debian 11) thì phải build **trong container Ubuntu
20.04** — làm sẵn:

```bash
bash packaging/build_appimage_docker.sh
```

*(yêu cầu Docker; kết quả vẫn là một file `.AppImage`.)*

---

## 2. Cài đặt trên Windows

MarkNote là ứng dụng Python/Qt nên **chạy được nguyên xác trên Windows**. Có
hai cách: chạy từ mã nguồn, hoặc build ra file `.exe` đóng gói.

### 2.1. Cài Python

- Tải Python 3.10+ tại https://www.python.org/downloads/windows/
- Khi cài, **tích chọn "Add Python to PATH"**.

### 2.2. Chạy từ mã nguồn (nhanh, không cần compile)

Mở PowerShell trong thư mục `marknote`:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe src\main.py
```

Dữ liệu người dùng nằm tại `%USERPROFILE%\.marknote\` (tương đương
`~/.marknote` trên Linux).

### 2.3. Chức năng xuất PDF trên Windows — đọc kỹ

WeasyPrint trên Windows cần Pango. Thuận tiện nhất là cài qua **MSYS2**:

```powershell
# 1) Cài MSYS2 từ https://www.msys2.org (mặc định)
# 2) Mở "MSYS2 UCRT64" shell, chạy:
pacman -S mingw-w64-ucrt-x86_64-pango
```

Sau đó cho MarkNote biết chỗ tìm các thư viện Pango:

```powershell
set WEASYPRINT_DLL_DIRECTORIES=C:\msys64\ucrt64\bin
```

Nếu **không** cần xuất PDF thì bỏ qua hẳn bước này; mọi tính năng khác vẫn
chạy đầy đủ.

> Cách khác: xuất PDF bằng **WSL** (cài Ubuntu trong WSL rồi dùng MarkNote
> trên Linux) hoặc đổi thành **Export HTML** rồi in ra PDF từ trình duyệt.

### 2.4. Build file chạy trực tiếp trên Windows (PyInstaller)

```powershell
powershell -ExecutionPolicy Bypass -File packaging\build_windows.ps1
```

Kết quả:

- `dist\marknote\marknote.exe` — chạy luôn, còn kèm thư mục `_internal`.
- `dist\MarkNote-1.1-windows-x64.zip` — nén sẵn để chuyển cho máy khác.

Lưu ý build trên Windows phải thực hiện **trên máy Windows**: PyInstaller
không cross-compile được (không thể build ra `.exe` ngay trên Linux).

---

## 3. macOS (thông tin tham khảo)

```bash
brew install python3 weasyprint
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
make run
```

Dựng app `.app` đóng gói có thể dùng PyInstaller trên chính máy macOS.

---

## 4. Build từ mã nguồn / đóng gói tĩnh

### 4.1. AppImage (Linux, 1 file tự chứa)

```bash
make appimage          # chạy PyInstaller + đóng gói AppImage
```

Hoặc muốn tương thích distro cũ: `bash packaging/build_appimage_docker.sh`.

Thành phần được đóng gói tự động: PySide6 (Qt Core/Gui/Widgets/WebEngine),
Python 3, Pygments (mọi ngôn ngữ/highlight), mdit-py-plugins, WeasyPrint kèm
đủ những thư viện đi kèm, các file CSS theme trong `assets/`.

Khi đóng gói, PyInstaller **loại trừ** PyQt5/PyQt6/PySide2 hoặc tkinter để
tránh đụng nhiều bộ binding Qt trong một app.

### 4.2. Windows: xem mục 2.4.

### 4.3. Goi nguồn (source tarball) cho việc cài từ mã nguồn

```bash
make dist              # ra marknote-1.1.tar.gz
```

---

## 5. Kiểm tra cài đặt thành công

```bash
# Linux/macOS
make run                       # cửa sổ MarkNote mở ra
python3 -c "import PySide6, weasyprint, markdown_it; print('sẵn sàng')"
```

```powershell
# Windows
.\.venv\Scripts\python.exe -c "import PySide6, weasyprint, markdown_it; print('sẵn sàng')"
```

Nếu chỉ thiếu `weasyprint` thì bật lệnh `pip install weasyprint` (và cài pango
như mục 1.2/2.3) — hoặc bỏ qua nếu không dùng Export PDF.

---

## 6. Xử lý sự cố nhanh

| Hiện tượng | Nguyên nhân / cách xử lý |
|------------|--------------------------|
| `ModuleNotFoundError: PySide6` | PySide6 chưa cài: `pip install -r requirements.txt` |
| App không mở, console báo font/EGL | Chạy với `QTWEBENGINE_CHROMIUM_FLAGS="--no-sandbox --disable-gpu"` (thường do GPU/máy ảo) |
| Export PDF báo "Missing Pango libraries" | Cài pango theo distro (mục 1.2) hoặc MSYS2 (mục 2.3) |
| AppImage không mở (cần FUSE) | `APPIMAGE_EXTRACT_AND_RUN=1 ./MarkNote-*.AppImage` |
| AppImage "GLIBC_2.xx not found" | AppImage build trên máy quá mới; dùng `build_appimage_docker.sh` để build lại trong distro cũ |
| Trên Windows PDF không nhận chữ | Thiếu font hệ thống hoặc `WEASYPRINT_DLL_DIRECTORIES` chưa trỏ đúng `ucrt64\bin` |
| Menu/app chữ trắng nền trắng | Palette sáng ép cứng đã xử lý hộ; nếu vẫn gặp, gỡ theme tối của HĐH khi dùng |

---

## 7. Các tập tin liên quan đến cài đặt/đóng gói

| Tập tin | Mục đích |
|---------|----------|
| `requirements.txt` | Danh sách thư viện chính thức |
| `Makefile` | `run`, `install`, `uninstall`, `dist`, `appimage` |
| `packaging/build_windows.ps1` | Build file chạy trực tiếp trên Windows |
| `packaging/build_appimage_docker.sh` | Build AppImage trong container cũ (rộng tương thích) |
| `packaging/make_icon.py` | Sinh icon PNG cho AppImage/desktop |
| `docs/VAN_DE_KY_THUAT.md` | Vì sao dùng venv, PySide6, WeasyPrint… |