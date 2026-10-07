# Cach ve va tao ra cac so do trong bao cao

Tai lieu nay huong dan cach ve lai cac so do cua MarkNote bang
**PlantUML** (so do use-case, tuan tu, lop) va **Graphviz** (so do ER
co so du lieu). Tat ca so do deu co tep nguon trong `docs/diagrams/`.

## 1. Cong cu can cai

| Cong cu | Tao ra | Cach cai |
|---|---|---|
| Java (JRE) | Chay PlantUML | `sudo apt install default-jre` |
| PlantUML | Use-case, tuan tu, lop | Tai jar ve may, chay `java -jar plantuml.jar` |
| Graphviz | So do ER | `sudo apt install graphviz` |

Cai Python (can cho ung dung):

```
sudo apt install python3-pyside6 graphviz
pip install weasyprint markdown-it-py mdit-py-plugins Pygments
```

## 2. Ve so do use-case / tuan tu / lop bang PlantUML

Tep nguon la cac file `.puml`. Vi du so do use-case:

```
@startuml
left to right direction
actor "Nguoi dung" as U
rectangle MarkNote {
  (Tao note) as UC1
  ...
}
U --> UC1
@enduml
```

Tao file anh dinh dang SVG:

```
java -jar plantuml.jar -tsvg docs/diagrams/usecase.puml
```

Tao PNG:

```
java -jar plantuml.jar -tpng docs/diagrams/usecase.puml
```

Chay cho nhieu file cung luc:

```
java -jar plantuml.jar -tsvg docs/diagrams/*.puml
```

Anh se nam canh file nguon trong thu muc `docs/diagrams/`.

## 3. Ve so do ER bang Graphviz

Tep nguon la `docs/diagrams/schema_er.dot` (dinh dang DOT). Tao anh:

```
dot -Tpng docs/diagrams/schema_er.dot -o docs/diagrams/schema_er.png
dot -Tsvg docs/diagrams/schema_er.dot -o docs/diagrams/schema_er.svg
```

## 4. Cach tao so do truc tiep tren web (khong can cai)

PlantUML cung cap dich vu truc tuyen tai

```
https://www.plantuml.com/plantuml/uml
```

Mo tep `.puml` trong trinh soan thao, copy toan bo noi dung vao o
nhap tren trang do, nhan nut tao bieu do, hinh se duoc tao ngay.
Khong can cai phan mem gi.

## 5. Danh sach tep nguon co san

| File | Loai so do | Ket qua |
|---|---|---|
| `docs/diagrams/usecase.puml` | Use-case | `usecase.svg` |
| `docs/diagrams/seq_tao_note.puml` | Tuan tu | `seq_tao_note.svg` |
| `docs/diagrams/seq_sync_scroll.puml` | Tuan tu | `seq_sync_scroll.svg` |
| `docs/diagrams/seq_chon_theme.puml` | Tuan tu | `seq_chon_theme.svg` |
| `docs/diagrams/seq_xuat_pdf.puml` | Tuan tu | `seq_xuat_pdf.svg` |
| `docs/diagrams/lop.puml` | Lop | `lop.svg` |
| `docs/diagrams/schema_er.dot` | ER | `schema_er.png`, `schema_er.svg` |

Ghi chu: khi xuat file PDF de nap bao cao, nen xuat hinh SVG/PNG voi
nen trong suot de giao dien khong bi vien trang.

## 6. May chu va do an lam viec

- May chu dang chay he dieu hanh: Linux (Ubuntu/Fedora).
- Do an cong nghe: Python 3 + PySide6/Qt + SQLite3/FTS5 +
  markdown-it-py (GFM) + Pygments + WeasyPrint.
- Ung dung offline 100%, khong sync cloud, khong collab realtime.