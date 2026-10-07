# MarkNote

Phan mem ghi chu Markdown offline cho Linux, co xem truoc song song,
chon theme CSS, tim kiem va xuat HTML/PDF.

## Tinh nang

- Tao, mo, sua, xoa note Markdown, luu trong `~/.marknote/notes.db`.
- Doi ten note ngay tran thanh tieu de (nut but, F2).
- Gan/go tag cho note; nut Tags hien ten tag cua note dang mo.
- Xem truoc song song: go ben trai, render ben phai, debounce 300ms.
- Dong bo cuon editor va preview.
- Tim trong note (Ctrl+F), thay the (Ctrl+H).
- Tim toan kho ket hop loc tag, vi du `apache tag:linux`, snippet to mau.
- Chon theme CSS (default, github, dark), doi theme khong can restart.
- Xuat HTML, PDF va Markdown dung chung mot theme dang chon.
- PDF A4: so trang "x / y", mục luc tu dong `[[TOC]]` kieu Word co so trang va
  link nhan; ngat trang bang HTML; chong cat tranh trang.
- Giao dien tieng Anh, palette sang ep cung chong xung dot theme toi OS.
- Chay offline 100%, khong sync cloud.

## Yeu cau he thong

- Python 3.10 tro len.
- Cac thu vien trong `requirements.txt`.
- Linux (Ubuntu/Fedora).

## Cai dat

Tao moi truong ao va cai thu vien:

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Hoac cai vao he thong:

```
sudo make install
```

Sau do mo ung dung bang lenh `marknote`.

## Chay truc tiep tu ma nguon

```
make run
```

Hoac:

```
source .venv/bin/activate
python src/main.py
```

## Cach dung

| Phim | Chuc nang |
|---|---|
| Ctrl+N | Tao note moi |
| Ctrl+S | Luu note |
| F2 | Doi ten note (nut but ✎) |
| Ctrl+D | Xoa note |
| Ctrl+F | Tim trong note |
| Ctrl+H | Thay the trong note |
| Ctrl+Shift+S | Dong bo cuon ON/OFF |
| Ctrl+Q | Thoat |

- Menu File > Export HTML / Export PDF / Export Markdown de xuat file.
- Menu Settings > Appearance de chon theme CSS.
- Mục luc tu dong: chua `[[TOC]]` hoac `[[TOC="Mục luc"]]` trong note.
- Ngat trang khi in: chua `<div style="page-break-after: always;"></div>`.
- Du lieu nguoi dung nam o `~/.marknote/` (notes.db + themes).

## Cau truc du an

```
marknote/
  Makefile  LICENSE  README.md  CHANGELOG  requirements.txt
  src/main.py  src/db.py  src/editor.py  src/preview.py
  src/exporter.py  src/theme.py  src/settings.py
  assets/themes/default.css  github.css  dark.css
  docs/        tai lieu bao cao, so do va cu phap GFM
  TAILIEUTHAMKHAO/  bai giang tham khao mon MNM
```
marknote/
  Makefile  LICENSE  README.md  CHANGELOG  requirements.txt
  GFM_TEMPLATE.md     ban demo day du cu phap Markdown de thu
  src/main.py  src/db.py  src/editor.py  src/preview.py
  src/exporter.py  src/theme.py  src/settings.py
  assets/themes/default.css  github.css  dark.css
  docs/        tai lieu bao cao, so do va cu phap GFM
  TAILIEUTHAMKHAO/  bai giang tham khao mon MNM
```

## Tai lieu bao cao

- `docs/INDEX_BAO_CAO.md` - chi muc toan bo tai lieu, goi y phan vai bao cao.
- `docs/HUONG_DAN_SU_DUNG.md` - huong dan su dung tung tinh nang.
- `docs/HUONG_DAN_CU_PHAP_MARKDOWN.md` - toan bo cu phap + cu phap rieng.
- `docs/DANH_SACH_TINH_NANG.md` - kiem ke tinh nang, doi chieu 13 UC.
- `docs/VAN_DE_KY_THUAT.md` - kien truc, lua chon thu vien, van de ky thuat.
- `docs/SCHEMA_CSDL.md` - co so du lieu va so do ER.
- `docs/MO_TA_USE_CASE.md` - mo ta 13 Use-Case va Actor.
- `docs/SODO_USE_CASE.md` - so do Use-Case.
- `docs/SODO_TUAN_TU.md` - cac so do tuan tu.
- `docs/SODO_LOP.md` - so do lop.
- `docs/CACH_VE_SO_DO.md` - cach ve lai cac so do.
- `docs/TONG_HOP_GFM.md` - tong hop cu phap GFM.

## Giay phep

Xem file `LICENSE` (MIT).