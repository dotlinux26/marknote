# Hướng dẫn cú pháp Markdown trong MarkNote

> Bảng tra đầy đủ cú pháp mà MarkNote render được.
> Bộ xử lý: markdown-it-py theo chuẩn **GFM** (GitHub Flavored Markdown)
> mở rộng thêm task list, footnote, link tự động và một số cú pháp riêng của MarkNote.

## 1. Tiêu đề (heading)

```markdown
# H1
## H2
### H3
#### H4
##### H5
###### H6
```

Kiểu gạch chân (setext):

```markdown
H1 lớn
======

H2 phụ
------
```

Mỗi heading được gán **id ổn định** (tự bỏ dấu, gạch nối, vd `## Danh sách` →
`danh-sach`), dùng làm đích nhảy cho mục lục và link nội bộ.

## 2. Nhấn mạnh chữ

| Cú pháp | Kết quả |
|---------|---------|
| `**đậm**` | **đậm** |
| `*nghiêng*` | *nghiêng* |
| `***đậm nghiêng***` | ***đậm nghiêng*** |
| `~~gạch ngang~~` | ~~gạch ngang~~ |
| `` `code` `` | `code` |

## 3. Link

```markdown
[Văn bản](https://example.com)                              ← link thường
[Văn bản](https://example.com "Chú thích")                  ← có tooltip
<https://example.com>                                       ← autolink
https://example.com                                         ← link tự động (linkify)
[Tham chiếu][id]
[id]: https://example.com                                   ← reference-style
[Trở về mục tiêu đề](#danh-sach)                           ← link nội bộ trong note
```

## 4. Ảnh

```markdown
![Mô tả](duong-dan-toi-file.png)
![Ảnh web](https://example.com/hinh.png)
```

Ảnh hiển thị trong preview và giữ nguyên khi xuất HTML/PDF.

## 5. Trích dẫn (blockquote)

```markdown
> Cấp 1
> nối tiếp dòng
>> Cấp 2
```

Blockquote có thể chứa danh sách, đoạn văn, bảng.

## 6. Danh sách

```markdown
- không thứ tự
  - lồng cấp 2
    - lồng cấp 3

1. có thứ tự
2. mục hai
   1. mục con
```

## 7. Task list (danh sách công việc)

```markdown
- [ ] chưa làm
- [x] đã làm xong
```

## 8. Bảng (GFM)

```markdown
| Cột trái | Cột giữa | Cột phải |
|:---------|:--------:|---------:|
| trái     | giữa     | phải     |
```

## 9. Code block

```markdown
```python
def f():
    return 42
```

```
Khối không khai báo ngôn ngữ
```
```

Cú pháp được **tô màu** bằng Pygments. Hỗ trợ nhiều ngôn ngữ, ví dụ:
`python`, `bash`, `c`, `json`, `sql`, `text`, … Nếu ngôn ngữ không nhận ra thì
render như code thường. Khối code được hiện hơn lên tên ngôn ngữ ở góc trên
bên trái.

Code nội dòng: `` chạy `searchFTS()` để tra cứu ``

## 10. Đường kẻ ngang

```markdown
---
***
___
```

## 11. Footnote (ghi chú cuối trang)

```markdown
Một ghi chú[^1] và một ghi chú khác[^note2].

[^1]: Nội dung ghi chú thứ nhất.
[^note2]: Ghi chú có thể đặt tên.
```

Phần định nghĩa tự dồn về cuối trong khối `.footnotes`, kèm nút back‑ref
quay lại chỗ chú thích.

## 12. Xuống dòng cưỡng bức

```markdown
Dòng 1\(xuống dòng)
Dòng 2  (hai khoảng trắng cuối dòng)
```

## 13. Thoát ký tự đặc biệt

Thêm dấu `\` trước ký tự muốn hiện nguyên văn:
`\#`, `\*`, <code>\\`</code>, `\[`, `\~`.

## 14. HTML thô (raw HTML)

MarkNote cho phép chèn HTML trực tiếp vào Markdown (cấu hình GFM `html: true`):

```html
Phím <kbd>Ctrl</kbd>
Điểm nhấn <mark>vàng</mark>
<div style="background:#f6f8fa;padding:8px;">Khối tự do</div>
```

## 15. Mục lục tự động — `[[TOC]]`  (cú pháp riêng của MarkNote)

Đặt ngay chỗ muốn hiện mục lục (thường đầu file):

```markdown
[[TOC]]
```

- Sinh mục lục từ **tất cả heading h1–h6**, lồng theo cấp.
- Trong preview: bấm vào dòng mục lục cuộn tới đúng mục.
- Khi **xuất PDF**: mỗi dòng có **gạch chấm dẫn tới số trang thật** của mục
  (style giống mục lục Word), và vẫn bấm nhảy được. Số trang chỉ hiển thị khi
  in/xuất, không hiện trên màn hình.
- Nếu chưa có heading nào, dòng `[[TOC]]` được bỏ qua.

Đổi tiêu đề của khung mục lục:

```markdown
[[TOC="Mục lục"]]
```

## 16. Ngắt trang khi xuất PDF  (cú pháp riêng của MarkNote)

Chèn dòng HTML sau ngay trước nội dung muốn bắt đầu ở trang mới:

```html
<div style="page-break-after: always;"></div>
```

Chỉ tác động khi in/xuất PDF; trên màn hình hiến như một khối trống.
Khi xuất PDF, đoạn văn/code/bảng/blockquote tự tránh bị cắt đôi trang
(cấu hình `page-break-inside: avoid`), heading không bị đứng cuối trang.

## 17. Đánh số trang

Mỗi file PDF xuất ra có đánh số **"trang hiện tại / tổng số trang"**
ngay giữa mép dưới trang, áp dụng tự động, không cần khai báo.

## 18. Bảng tổng hợp nhanh

| Nhóm | Cú pháp | Đã hỗ trợ |
|------|---------|:---------:|
| Heading | `#`…`######`, setext, id ổn định | x |
| Nhấn mạnh | `**`, `*`, `***`, `~~`, `` ` `` | x |
| Link | thường, tooltip, autolink, linkify, reference, nội bộ `#id` | x |
| Ảnh | cục bộ và web | x |
| Blockquote | đơn, lồng, chứa nội dung | x |
| Danh sách | ul / ol / lồng nhau | x |
| Task list | `- [ ]` `- [x]` | x |
| Bảng | GFM + can lề | x |
| Code | fence nhiều ngôn ngữ, highlight, inline | x |
| HR | `---`, `***`, `___` | x |
| Footnote | `[^1]` + định nghĩa + back‑ref | x |
| Ngắt dòng | `\` hoặc 2 spaces | x |
| Escape | `\*` … | x |
| HTML thô | `<kbd>`, `<mark>`, `<div>`, ... | x |
| Footnote-end context | cuối file tự gom | x |
| `[[TOC]]` | sinh mục lục, đổi tiêu đề bằng `[[TOC="..."]]` | x |
| Page break | `<div style="page-break-after: always;">` | x |
| Footer số trang | PDF tự in "x / y" | x |