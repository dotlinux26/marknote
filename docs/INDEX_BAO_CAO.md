# Chỉ mục tài liệu MarkNote (dành cho nhóm báo cáo)

> Bản đồ tài liệu: file nào trả lời câu hỏi nào. Tất cả đều trong thư mục `docs/`
> (cộng thêm `KEHOACH_MarkNote.md` ở root), đã render sẵn ảnh trong `docs/diagrams/`.

## 1. Hỏi nhanh — đọc cái gì

| Bạn cần | Đọc |
|---------|-----|
| Cách cài, chạy, phím tắt, dùng từng chức năng | `HUONG_DAN_SU_DUNG.md` |
| Cú pháp Markdown nào hoạt động (kèm ví dụ) | `HUONG_DAN_CU_PHAP_MARKDOWN.md` |
| Đã làm được những tính năng nào (đối chiếu kế hoạch) | `DANH_SACH_TINH_NANG.md` |
| Vì sao chọn thư viện, kiến trúc, vấn đề kỹ thuật, cách xử lý | `VAN_DE_KY_THUAT.md` |
| Schema CSDL, bảng, trigger, câu SQL mẫu | `SCHEMA_CSDL.md` |
| Mô tả chi tiết 13 use case | `MO_TA_USE_CASE.md` |
| Sơ đồ use case / tuần tự / lớp / ER | `SODO_USE_CASE.md`, `SODO_TUAN_TU.md`, `SODO_LOP.md`, `docs/diagrams/schema_er.*` |
| Cách tự vẽ lại sơ đồ | `CACH_VE_SO_DO.md` |
| Bảng cú pháp GFM gọn | `TONG_HOP_GFM.md` |
| Bản demo cú pháp bấm chạy thử | `GFM_TEMPLATE.md` (root repo) |

## 2. Bộ tài liệu mở rộng (EXTEND)

Mới bổ sung 4 file phục vụ báo cáo và hướng dẫn bạn khác:

1. `HUONG_DAN_SU_DUNG.md` — quy trình sử dụng ứng dụng.
2. `HUONG_DAN_CU_PHAP_MARKDOWN.md` — toàn bộ cú pháp + cú pháp riêng của MarkNote.
3. `DANH_SACH_TINH_NANG.md` — kiểm kê tính năng đối chiếu kế hoạch.
4. `VAN_DE_KY_THUAT.md` — quyết định thiết kế, thư viện, các khó khăn đã xử lý.

## 3. Phân vai gợi ý cho nhóm báo cáo

| Thành viên phụ trách | Nội dung dựa trên |
|---------------------|-------------------|
| Tổng quan + giao diện | HUONG_DAN_SU_DUNG, ảnh chụp màn hình |
| Phần Analysis (yêu cầu) | KEHOACH_MarkNote (mục 1–6), MO_TA_USE_CASE, SODO_USE_CASE |
| Phần Design (thiết kế) | SCHEMA_CSDL, SODO_LOP, SODO_TUAN_TU, CACH_VE_SO_DO |
| Phần Implementation (thư viện, thuật toán) | VAN_DE_KY_THUAT, DANH_SACH_TINH_NANG |
| Phần Test/Demo | GFM_TEMPLATE, HUONG_DAN_CU_PHAP_MARKDOWN, kết quả smoke test |

## 4. Nhận xét dữ liệu / cảnh báo khi viết báo cáo

- Mọi tính năng tuyên bố trong `DANH_SACH_TINH_NANG.md` đều đang chạy trong
  mã nguồn `src/`.
- Số trang PDF, số trang trong mục lục là **tự động tính lúc render**, không
  hardcode — nên trích dẫn là "tính động theo nội dung".
- Ứng dụng hoạt động **hoàn toàn offline** (kể cả export); không có mạng.
- Các hình trong `docs/diagrams/` có nguồn vẽ lại được (PlantUML / Graphviz).