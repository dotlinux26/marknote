"""Xuat HTML va PDF voi CSS cua theme da chon, nhung inline."""

from __future__ import annotations

from pathlib import Path

PDF_PAGE_RULE = (
    "\n@page { size: A4; margin: 18mm 16mm; }\n"
)

HTML_HEADER = (
    "<!DOCTYPE html>\n"
    '<html lang="vi">\n'
    "<head>\n"
    '<meta charset="utf-8">\n'
    '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    "<title>%s</title>\n"
    "<style>\n"
)
HTML_FOOTER = (
    "\n</style>\n"
    "</head>\n"
    "<body>\n"
    '<main class="markdown-body">\n'
    "\n</main>\n"
    "</body>\n"
    "</html>\n"
)


def build_document(html_body: str, css: str, title: str = "MarkNote") -> str:
    """Ghep HTML da render voi CSS inline thanh mot trang doc lap."""
    return (
        HTML_HEADER % title
        + css
        + HTML_FOOTER.replace("\n</main>\n", "\n" + html_body + "\n</main>\n")
    )


class Exporter:
    """Ghi ra file HTML hoac PDF dung chung mot theme (UC13)."""

    def toHtml(self, html_body: str, css: str, path) -> None:
        Path(path).write_text(
            build_document(html_body, css), encoding="utf-8"
        )

    def toPdf(self, html_body: str, css: str, path) -> None:
        try:
            from weasyprint import HTML
        except ImportError as exc:
            raise RuntimeError("weasyprint-missing") from exc
        document = build_document(html_body, css + PDF_PAGE_RULE)
        HTML(string=document).write_pdf(str(path))