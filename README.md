# MarkNote

Phan mem ghi chu Markdown offline cho Linux, co xem truoc song song,
chon theme CSS, tim kiem va xuat HTML/PDF.

## Tinh nang

- Tao, mo, sua, xoa note Markdown, luu trong `~/.marknote/notes.db`.
- Gan/go tag cho note.
- Xem truoc song song: go ben trai, render ben phai, debounce 300ms.
- Dong bo cuon editor va preview.
- Tim trong note (Ctrl+F), thay the (Ctrl+H).
- Tim toan kho ket hop loc tag, vi du `apache tag:linux`.
- Chon theme CSS (default, github, dark), doi theme khong can restart.
- Xuat HTML va PDF dung chung mot theme dang chon.
- Chay offline 100%, khong sync cloud.

## Yeu cau he thong

- Python 3.10 tro len.
- Cac thu vien trong `requirements.txt`.
- Linux (Ubuntu/Fedora).

## Cai dat

Cai thu vien bang pip:

```
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
python3 src/main.py
```

## Cach dung

| Phim | Chuc nang |
|---|---|
| Ctrl+N | Tao note moi |
| Ctrl+S | Luu note |
| Ctrl+D | Xoa note |
| Ctrl+F | Tim trong note |
| Ctrl+H | Thay the trong note |
| Ctrl+Shift+S | Dong bo cuon ON/OFF |

- Menu File > Xuat HTML / Xuat PDF de xuat file da luu.
- Menu Cai dat > Giao dien de chon theme CSS.
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

## Xoa du lieu nguoi dung

Xoa toan bo du lieu nguoi dung:

```
rm -rf ~/.marknote
```

## Tai lieu bao cao

- `docs/SCHEMA_CSDL.md` - co so du lieu va so do ER.
- `docs/MO_TA_USE_CASE.md` - mo ta 13 Use-Case va Actor.
- `docs/SODO_USE_CASE.md` - so do Use-Case.
- `docs/SODO_TUAN_TU.md` - cac so do tuan tu.
- `docs/SODO_LOP.md` - so do lop.
- `docs/CACH_VE_SO_DO.md` - cach ve lai cac so do.
- `docs/TONG_HOP_GFM.md` - tong hop cu phap GFM.

## Giay phep

Xem file `LICENSE` (MIT).