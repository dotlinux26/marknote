# Hướng Dẫn Đóng Góp Cho Dự Án MarkNote (Contributing Guide)

Chào mừng bạn đến với dự án **MarkNote**! Chúng tôi trân trọng mọi hình thức đóng góp từ cộng đồng mã nguồn mở, bao gồm báo lỗi (bug report), đề xuất tính năng (feature request), hoàn thiện tài liệu, hoặc trực tiếp gửi mã nguồn (Pull Request).

---

## 1. Quy Tắc Ứng Xử (Code of Conduct)
Chúng tôi cam kết tạo ra một môi trường cởi mở, hòa đồng, tôn trọng và không phân biệt đối xử. Xin vui lòng giao tiếp một cách lịch sự, mang tính xây dựng khi trao đổi trên GitHub Issues hoặc Pull Requests.

---

## 2. Báo Lỗi & Đề Xuất Tính Năng
- Trước khi mở một Issue mới, hãy kiểm tra danh sách **Issues** hiện có để tránh trùng lặp.
- Khi báo lỗi, hãy cung cấp:
  1. Hệ điều hành và phiên bản (ví dụ: Windows 11 x64, Ubuntu 24.04).
  2. Phiên bản Python và PySide6 đang sử dụng.
  3. Các bước cụ thể để tái hiện lỗi (Steps to reproduce).
  4. Ảnh chụp màn hình hoặc log lỗi trong terminal (nếu có).

---

## 3. Quy Trình Gửi Mã Nguồn (Pull Request Workflow)

1. **Fork repository** về tài khoản GitHub của bạn.
2. **Clone repo đã fork về máy**:
   ```bash
   git clone https://github.com/<tai-khoan-cua-ban>/marknote.git
   cd marknote
   ```
3. **Tạo nhánh mới** cho tính năng hoặc bản sửa lỗi:
   ```bash
   git checkout -b feature/ten-tinh-nang
   # hoặc: git checkout -b fix/ten-loi
   ```
4. **Thiết lập môi trường phát triển**:
   ```bash
   python -m venv .venv
   # Windows:
   .\.venv\Scripts\Activate.ps1
   # Linux/macOS:
   source .venv/bin/activate

   pip install -r requirements.txt
   ```
5. **Chạy thử ứng dụng**:
   ```bash
   python src/main.py
   ```
6. **Commit thay đổi** tuân theo chuẩn Conventional Commits:
   ```bash
   git commit -m "feat: bổ sung phím tắt xuất file nhanh"
   # hoặc: git commit -m "fix: sửa lỗi mất focus khi đổi tên note"
   ```
7. **Đẩy lên nhánh fork của bạn**:
   ```bash
   git push origin feature/ten-tinh-nang
   ```
8. **Mở Pull Request (PR)** trên GitHub repository chính:
   - Mô tả rõ mục đích của PR và những thay đổi đã thực hiện.
   - Liên kết tới Issue liên quan (ví dụ: `Closes #12`).

---

## 4. Chuẩn Mực Viết Mã Nguồn (Coding Standards)
- Tuân thủ phong cách lập trình Python chuẩn **PEP 8**.
- Khuyến khích sử dụng **Type Hints** (`from __future__ import annotations`).
- Giữ các hàm và class có tính độc lập cao, tuân thủ nguyên tắc Single Responsibility.
- Đảm bảo mã nguồn chạy tốt trên cả **Linux** và **Windows**.

---

## 5. Bản Quyền & Giấy Phép Đóng Góp (Licensing Policy)
- Bằng việc gửi mã nguồn thông qua Pull Request, bạn đồng ý rằng toàn bộ đóng góp của bạn sẽ được phát hành theo **Giấy phép MIT** của dự án MarkNote.
- Bạn cam kết rằng mã nguồn đóng góp là do chính bạn tạo ra hoặc bạn có toàn quyền pháp lý để cấp phép theo điều khoản MIT.
- Không sao chép mã nguồn có bản quyền đóng hoặc có giấy phép không tương thích (như GPLv3 thuần túy) vào phần core của dự án mà không có sự đồng thuận từ ban quản trị.
