# To hop cu phap GitHub Flavored Markdown (GFM)

Tai lieu nay tong hop day du cu phap Markdown ma MarkNote ho tro,
dua tren phan mem `markdown-it-py` chay che do `gfm-like` va plugin
`tasklists`, `footnote`. Duoc danh dau "Khong lam" la ngoai pham vi cua
ke hoach, ghi rõ de tranh nham lan khi thao luan bai bao cao.

## 1. Cu phap co ban

| Nhom | Cu phap | Vi du |
|---|---|---|
| Heading | `#` den `######`, setext (`===`, `---`) | `## Muc 2` |
| Dinh dang | `**bold**`, `*italic*`, `~~gach~~`, `__bold__`, `_italic_` | `**chu dam**` |
| Code inline | `` `code` `` | `` `sudo apt install` `` |
| Code block | `` ```python ``, `` ```bash ``, `` ```sql `` | xem muc 3 |
| Link | `[text](url)`, `[text](url "tieu de")`, autolink `<http://...>` | `[GitHub](https://github.com)` |
| Anh | `![alt](duong-dan)`, ho tro anh local va base64 | `![icon](anh.png)` |
| Trich dan | `> doan vao` , nhieu tang `>>` | `> Luu y quan trong` |
| Danh sach | `-`, `*`, `+`, `1.`, long nhau 2-3 cap | `- muc 1` va thut vao `  - muc 1.1` |
| Checklist | `- [ ]` chua lam, `- [x]` da lam | `- [x] hoan thanh` |
| Duong ke | `---`, `***`, `___` | `---` |
| Bang | `\| a \| b \|` va dong can le | xem muc 4 |
| HTML inline | `<b>`, `<img>`, `<div>`, `<details>` | `<details>...` |
| Escaping | `\*` hien ky tu dac biet | `\*khong in dam\*` |
| Footnote | `[^1]` va dinh nghia `[^1]: ...` | xem muc 5 |

## 2. Dac trung rieng cua GitHub

| Tinh nang | Vi du |
|---|---|
| Autolink | `github.com` tu dong thanh lien ket |
| Task list | `- [x] da xong` |
| Strikethrough | `~~da xong~~` |
| Bang can le | `\|:---\|` trai, `\|:---:\|` giua, `\|---:\|` phai |
| URL tu dong ngat dong | Link dai tu dong wrap |
| Highlight code | ` ```diff `, ` ```python `, ` ```js `, ` ```bash `, ` ```sql ` |

## 3. Code block va to mau Pygments

```python
import os
for thu_muc in os.listdir("."):
    print(thu_muc)
```

```bash
sudo apt install python3-pyside6
```

Cac block code duoc to mau bang Pygments, CSS o dang inline nen file
HTML xuat ra doc lap, khong can file CSS di kem.

## 4. Bang voi can le

| O trai | O giua | O phai |
|:---|:---:|---:|
| chu trai | chu giua | chu phai |
| a | b | c |

## 5. Footnote

Day la chu thich[^1].

[^1]: Noi dung chu thich duoc dinh nghia cuoi bai.

## 6. Khong lam (ngoai pham vi)

| Tinh nang | Ghi chu |
|---|---|
| Math LaTeX | Khong ho tro cong thuc toan |
| Mermaid / diagram | Khong ho tro so do trong note |
| Plugin tuy chinh | Khong nap plugin ngoai le |
| Embed video | Khong nhanh nhu cau |
| Xuat gop nhieu note | Chi xuat 1 note mot lan |