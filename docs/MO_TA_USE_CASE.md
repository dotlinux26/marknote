# Mo ta cac Use-Case cua MarkNote

## 1. Actor

| Ki hieu | Actor | Mo ta |
|---|---|---|
| U01 | Nguoi dung | Toan quyen tao, mo, sua, xoa, tag, tim kiem, thay the, chon theme, xuat HTML/PDF |

Ung dung offline mot nguoi dung nen chi can mot actor. Neu phan cong
can 2 actor, them **U02 - Khach xem (read-only)**: chi mo, tim, xuat,
khong sua/xoa.

## 2. Danh sach 13 Use-Case

| Ma | Ten UC | Mo ta ngan |
|---|---|---|
| UC01 | Tao note | Nhap tieu de va noi dung, luu vao database |
| UC02 | Mo/Xem note | Click note trong danh sach, do len editor va preview |
| UC03 | Sua note | Soan thao, Ctrl+S de cap nhat database |
| UC04 | Xoa note | Xoa sau khi xac nhan (CASCADE xoa tag gan) |
| UC05 | Gan/Go tag | Gan hoac go tag cho note, tao tag moi |
| UC06 | Preview song song | Render GFM lien tuc moi khi go, debounce 300ms |
| UC07 | Sync-scroll ON/OFF | Dong bo cuon editor va preview |
| UC08 | Tim trong note | Ctrl+F, highlight toan bo, Enter next/Shift+Enter prev |
| UC09 | Thay the trong note | Ctrl+H, thay 1 hoac thay tat ca |
| UC10 | Tim toan kho + loc tag | FTS5, vi du `apache tag:linux` |
| UC11 | Xem danh sach theme | Quet thu muc theme, do vao dropdown |
| UC12 | Chon theme | Doi CSS preview ngay, khong can restart |
| UC13 | Xuat HTML/PDF | Xuat file doc lap dung chung 1 theme |

## 3. Chi tiet tung UC

### UC01 - Tao note moi

- Pre: App dang mo
- Main:
  1. Bam New
  2. Nhap tieu de
  3. Soan noi dung `content_md`
  4. Bam Save
  5. `INSERT INTO notes(title, content_md, updated_at)`
- Post: Them 1 dong `notes`, note moi xuat hien trong danh sach

### UC02 - Mo/Xem note

- Main:
  1. Click note trong danh sach
  2. `SELECT title, content_md FROM notes WHERE id=?`
  3. Do `content_md` vao editor ben trai + render preview ben phai

### UC03 - Sua note

- Actor: Nguoi dung
- Pre: Dang mo note id=1, DB ket noi OK
- Post: `notes.content_md` va `updated_at` duoc cap nhat, preview hien
  thi noi dung moi
- Luong chinh:
  1. User go noi dung moi trong editor
  2. User nhan Ctrl+S
  3. He thong `UPDATE notes SET content_md=?, updated_at=CURRENT_TIMESTAMP WHERE id=1`
  4. He thong goi `PreviewPane.render(content_md)`
  5. Danh sach note cap nhat thoi gian sua
- Luong thay the: 3a. User khong doi gi -> bao "Khong co thay doi",
  bo qua update
- Ngoai le: 3b. DB locked -> bao "Database is locked, thu lai"

### UC04 - Xoa note

- Main:
  1. Bam Delete
  2. Hop thoai xac nhan
  3. `DELETE FROM notes WHERE id=?` (cascade xoa `note_tag`)

### UC05 - Gan/Go tag cho note

- Main gan: Mo note -> tick tag -> `INSERT OR IGNORE INTO note_tag`
- Main go: Bo tick tag -> `DELETE FROM note_tag WHERE note_id=? AND tag_id=?`
- Main tao tag moi: Nhap ten -> `INSERT INTO tags(name)` -> gan luon cho note

### UC06 - Xem Preview song song

- Main:
  1. Mo note
  2. Layout chia 2 panel bang QSplitter
  3. Editor trai hien `content_md`
  4. Preview phai parse qua `markdown-it-py` (GFM) + Pygments
  5. Nhung CSS theme -> hien thi HTML
- Moi lan go co debounce 300ms -> re-render

### UC07 - Bat/Tat Sync-scroll

- Main ON:
  1. Bam nut Sync
  2. `UPDATE settings value='ON' WHERE key='sync_scroll'`
  3. Khi cuon editor: `percent = scrollTop / maxScroll` -> set
     `scrollTop` tuong ung cho preview
- Main OFF: hai panel cuon doc lap

### UC08 - Tim trong note hien tai

- Main:
  1. Ctrl+F
  2. Nhap tu khoa
  3. Highlight vang moi vi tri trong editor
  4. Enter = next, Shift+Enter = prev, hien `3/12`

### UC09 - Thay the trong note

- Main:
  1. Ctrl+H
  2. Nhap find + replace
  3. Bam Replace / Replace All
  4. Bao "Da thay 12 vi tri"
  5. `UPDATE notes SET content_md`
  6. Preview re-render

### UC10 - Tim toan kho + loc tag

- Main:
  1. Nhap o Search `apache tag:linux`
  2. Query `notes_fts MATCH` + `JOIN note_tag`
  3. Tra list kem highlight tu khoa
  4. Click de mo note
- Main loc: Chon tag trong sidebar -> `SELECT ... WHERE tag.name=?` ->
  list thu hep
- Sort: `ORDER BY pinned DESC, updated_at DESC`

### UC11 - Xem danh sach theme

- Main:
  1. Mo Setting > Appearance
  2. `os.listdir('~/.marknote/themes')` loc `.css`
  3. Do vao QComboBox
  4. Chon san item theo `settings.theme`

### UC12 - Chon theme

- Actor: Nguoi dung
- Pre: Thu muc theme co it nhat `default.css`
- Post: `settings.theme` doi gia tri, preview render lai voi CSS moi
- Luong chinh:
  1. User mo Setting > Appearance
  2. He thong quet thu muc, do danh sach `.css` vao dropdown
  3. User click chon theme `dark`
  4. He thong doc noi dung `~/.marknote/themes/dark.css`
  5. `UPDATE settings SET value='dark' WHERE key='theme'`
  6. Preview nhung CSS moi va re-render
- Ngoai le:
  - File `.css` khong ton tai -> bao "Theme file missing", hoi reset ve default
  - CSS sai cu phap -> canh bao, render bang theme truoc do
  - Thu muc rong -> copy tu `assets/themes` roi quet lai

### UC13 - Xuat HTML / PDF

- Main HTML: Bam Export HTML -> chon path -> doc CSS theme -> ghep
  `html + css inline` -> ghi `.html`
- Main PDF: Bam Export PDF -> chon path -> lay HTML nhu tren ->
  `WeasyPrint(html).write_pdf(path)` kho A4
- Ca hai dung chung theme, khac nhau dung 1 buoc ky thuat

## 4. So do Use-Case

Xem file `SODO_USE_CASE.md` va hinh `diagrams/usecase.svg`.

## 5. Quan he include giua cac UC

```
UC6  <.. UC12 : <<include>>
UC6  <.. UC11 : <<include>>
UC11 <.. UC12 : <<include>>
UC13 <.. UC12 : <<include>>
UC13 <.. UC6  : <<include>>
UC10 <.. UC2  : <<include>>
```

Y nghia: muon Preview hay Xuat thi bat buoc phai co theme duoc chon
truoc; muon Tim toan kho thi phai cho note duoc Mo truoc.