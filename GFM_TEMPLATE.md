# Markdown GFM — Full Feature Template

> Copy toan bo noi dung file nay sang mot note moi (Ctrl+N -> Ctrl+V)
> de kiem tra day du cup phap ma MarkNote ho tro (GFM + task list + footnote + syntax highlight).

---

## 1. Headings (tieu de)

# Heading 1

## Heading 2

### Heading 3

#### Heading 4

##### Heading 5

###### Heading 6

**Setext style** (gach chan bang ky tu `=` va `-`):

Heading Setext 1
================

Heading Setext 2
----------------

---

## 2. Emphasis (dinh dang chu inline)

- **Bold** dung `**chu bat dau va ket thuc**`
- *Italic* dung `*chu nap*`
- ***Bold + Italic*** dung `***ca ba dau***`
- ~~Strikethrough~~ dung `~~hai dau ngang~~`
- `inline code` dung backtick `` ` ``

Mot doan van binh thuong de kiem tra gio hang: Lorem ipsum dolor
sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut
labore et dolore magna aliqua. Doan nay dang duoc gio hang tu dong.

---

## 3. Links (lien ket)

- Inline link: [Markdown Guide](https://www.markdownguide.org)
- Co tieu de khi tro: [Markdown Guide](https://www.markdownguide.org "Lien ket co tieu de")
- Autolink (trong ngoac nhon): <mailto:user@example.com>
- URL tro truc tiep (linkify): https://www.markdownguide.org
- Reference-style:

  [Markdown Guide][mdg]

  [mdg]: https://www.markdownguide.org

---

## 4. Images (anh)

Anh tu file cuc bo trong cung thu muc (vi du `screen.png`):

![Anh vi du](/tmp/opencode/not_a_real_file.png)

Hoac link web:

![Placeholder](https://via.placeholder.com/150)

> Luu y: anh cung duoc hien thi trong preview va khi xuat HTML/PDF.

---

## 5. Blockquote (trich dan)

> Day la mot blockquote.
> nhieu dong van deu nam trong blockquote.

> Blockquote long nhau:
>
> > Level 2
> >
> > > Level 3

Blockquote chua danh sach:

> - muc thu nhat
> - muc thu hai
>
> 1. muc danh so mot
> 2. muc danh so hai

---

## 6. Lists (danh sach)

Khong thu tu (unordered):

- apple
- banana
- cherry

Co thu tu (ordered):

1. first
2. second
3. third

Long nhau (nested):

- cap 1
  - cap 2
    - cap 3 (square)
- tro ve cap 1

1. ngoai
   - con giua
     1. con trong
2. ngoai lan thu hai

---

## 7. Task List (danh sach cong viec GFM)

- [x] Da hoan thanh cong viec nay
- [ ] Dang cho xu ly
- [ ] Chua bat dau

---

## 8. Tables (bang GFM)

Sua hang dinh dang de can le:

| Mon an  | Gia     | Danh gia |
|---------|:-------:|---------:|
| Pho     | 50.000  |        5 |
| Bun cha | 40.000  |        4 |
| Banh mi | 20.000  |        5 |

Bang khong can le dac biet:

| th   | td   |
|------|------|
| a    | b    |

---

## 9. Code Blocks

Code Python (co to mau syntax):

```python
def fib(n: int) -> int:
    """Tra ve so Fibonacci thu n."""
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

print(fib(10))
```

Code Bash:

```bash
#!/usr/bin/env bash
# Dem so dong trong file
wc -l GFM_TEMPLATE.md
```

Code C:

```c
#include <stdio.h>

int main(void) {
    printf("Hello, MarkNote\n");
    return 0;
}
```

Code SQL (FTS5 duoc dung trong MarkNote):

```sql
-- Tim note chua tu "apache" va tag "linux"
SELECT title, snippet(notes_fts, 1, '<b>', '</b>', '...', 12)
FROM notes
JOIN notes_fts ON notes_fts.rowid = notes.id
WHERE notes_fts MATCH 'apache AND tag:linux';
```

Code khong khai bao ngon ngu (khong to mau):

```
plain text block
khong co syntax highlight
```

Inline code trong doan van: dung `self.notes.searchFTS(keyword, tag_name)` de tim.

---

## 10. Horizontal Rules (duong ke ngang)

Cach tao duong ke ngang bang dau `---`:

---

Hoac `***`:

***

Hoac `___`:

___

---

## 11. Footnotes (ghi chu chan)

Day la mot cau co ghi chu chan[^1] va mot cau nua[^note-ha-so].

[^1]: Dinh nghia ghi chu chan so mot.
[^note-ha-so]: Ghi chu chan co ten kieu "ha-so" (reference-style).

Phan dinh nghia ghi chu chan se duoc xep vao cuoi tai khung `.footnotes`.

---

## 12. Hard Line Breaks (xuong dong cuong buoc)

De xuong dong hien thi ngay, ket thuc dong truoc bang `\`:

dong thu nhat\
dong thu hai tren cung mot doan

Hoac ket bang **hai dau cach**:

dong thu ba\
dong thu bon

---

## 13. Escaping (thoat ky tu dac biet)

Mun hien thi nguyen ky tu Markdown thi them dau `\`:

\# khong phai heading, \* khong in dam\*, \` khong phai code\`, \[khong phai link\], ~khong phai strikethrough~.

---

## 14. Raw HTML (HTML thuan)

Gap rong vi gfm-like cho phep HTML:

- Phim tat: <kbd>Ctrl</kbd> + <kbd>F</kbd>
- Anh sang: <mark>highlight</mark> trong doan van
- Khoi <div style="background:#f6f8fa;padding:8px;border:1px solid #d8dee4;">HTML block thu cong</div>

---

## 15. Page Break (ngan trang khi in/PDF)

Chen dong HTML duoi day ngay truoc noi dung muon bat dau o trang moi (chi tac
dong khi xuat PDF hoac in; xuat ra 2 trang trong vi du duoi):

<div style="page-break-after: always;"></div>

Sau khuong can la phan nay nam o *trang moi* khi xuat PDF.

---

## 16. Table of Contents (muc luc tu dong)

Dat `[[TOC]]` o bat ky cho nao (thuong la dau file) de sinh muc luc tu cac
tieu de h1-h6, co the bo tieu de tuy y bang `[[TOC="...]]`:

[[TOC="Chi muc cua toi"]]

# Muc A

## Muc A.1

### Muc A.1.1

## Muc A.2

# Muc B

Muc luc o tren co link nhan: khi xuat PDF, click vao dong trong muc luc se
nhay toi dung muc do; cuoi moi dong co gach cham `......` va so trang cua
muc do (giong muc luc trong Word).

---

## 17. Combination (ket hop nhieu cup phap)

> **Ghi chu quan trong**: trong blockquote, duoc dung **bold**, `code` va table:

| Cot A  | Cot B  |
|--------|--------|
| 1      | 2      |

```text
--- ket hop duoc ----
```

- [x] Template da bao phu: heading, emphasis, link, image, blockquote, list, task, table, code, hr, footnote, line break, escape, raw HTML, page break, TOC.
- [ ] Ban da thu them cup phap khac?

---

*Note: PDF xuat ra co san so trang "X / Y" o goc duoi moi trang. Xoa cac doan ghi chu truoc khi dung that.*