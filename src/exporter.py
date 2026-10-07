"""Xuat HTML va PDF voi CSS cua theme da chon, nhung inline."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

PDF_PAGE_RULE = (
    "\n"
    "@page {\n"
    "  size: A4;\n"
    "  margin: 18mm 16mm 22mm 16mm;\n"
    "  @bottom-center {\n"
    "    content: counter(page) \" / \" counter(pages);\n"
    "    font-size: 9pt;\n"
    "    color: #59636e;\n"
    "  }\n"
    "}\n"
)

TOC_PRINT_RULE = (
    "\n"
    "@media print {\n"
    "  .markdown-body .toc a {\n"
    "    color: var(--fg-default, #1f2328);\n"
    "    text-decoration: none;\n"
    "  }\n"
    "  .markdown-body .toc a::after {\n"
    "    content: leader('. ') target-counter(attr(href), page);\n"
    "    color: var(--fg-muted, #59636e);\n"
    "    padding-left: 6px;\n"
    "  }\n"
    "}\n"
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


def find_windows_weasyprint() -> Path | None:
    """Tim ban weasyprint.exe da dong goi san (kem Pango) tren Windows.

    Chay direct bang ban pre-built cua chinh noi WeasyPrint
    (release weasyprint-windows.zip) => KHONG can cai Pango qua pacman/MSYS2.
    """
    if sys.platform != "win32":
        return None
    candidates: list[Path] = []
    env_exe = os.environ.get("WEASYPRINT_EXE")
    if env_exe:
        candidates.append(Path(env_exe))
    root = Path(sys.executable).resolve().parent
    candidates.extend(
        [
            root / "bin" / "weasyprint" / "weasyprint.exe",
            root / "weasyprint" / "weasyprint.exe",
            root / "_internal" / "bin" / "weasyprint" / "weasyprint.exe",
            root / "_internal" / "weasyprint" / "weasyprint.exe",
        ]
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def render_pdf_via_cli(document: str, path: str) -> None:
    """Xuat PDF bang weasyprint.exe (gom san Pango) qua command line."""
    exe = find_windows_weasyprint()
    if exe is None:
        raise RuntimeError("weasyprint-libs")
    with tempfile.TemporaryDirectory() as tmp:
        html_file = Path(tmp) / "marknote-export.html"
        html_file.write_text(document, encoding="utf-8")
        result = subprocess.run(
            [str(exe), str(html_file), str(path)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError("weasyprint-failed")


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
        document = build_document(
            html_body, css + PDF_PAGE_RULE + TOC_PRINT_RULE
        )
        try:
            HTML(string=document).write_pdf(str(path))
        except OSError as exc:
            msg = str(exc).lower()
            if "cannot load library" in msg and any(
                lib in msg for lib in ("libgobject", "libpango", "gobject", "pango")
            ):
                # Windows: Python weasyprint khong tim thay Pango ->
                # doi sang ban weasyprint.exe dong goi san (kem Pango).
                if sys.platform == "win32" and find_windows_weasyprint():
                    render_pdf_via_cli(document, path)
                else:
                    raise RuntimeError("weasyprint-libs") from exc
            else:
                raise