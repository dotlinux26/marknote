"""Xuat HTML va PDF voi CSS cua theme da chon, nhung inline."""

from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from media import embed_images_as_base64

CHECKBOX_TAG_RE = re.compile(
    r'<input\b[^>]*class=["\'][^"\']*task-list-item-checkbox[^"\']*["\'][^>]*>'
)

UNCHECKED_SVG = (
    '<svg class="task-svg task-unchecked" width="15" height="15" viewBox="0 0 16 16" fill="none" '
    'xmlns="http://www.w3.org/2000/svg">'
    '<rect x="1.5" y="1.5" width="13" height="13" rx="3" stroke="#8c959f" stroke-width="1.8" fill="#ffffff"/>'
    '</svg>'
)

CHECKED_SVG = (
    '<svg class="task-svg task-checked" width="15" height="15" viewBox="0 0 16 16" fill="none" '
    'xmlns="http://www.w3.org/2000/svg">'
    '<rect x="1" y="1" width="14" height="14" rx="3" fill="#0969da" stroke="#0969da" stroke-width="1"/>'
    '<path d="M4.5 8L7 10.5L11.5 5.5" stroke="#ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
    '</svg>'
)


def replace_checkboxes_with_svg(html: str) -> str:
    """Thay the checkbox mac dinh bang vector SVG sac net va can le chuan."""
    if not html or "task-list-item-checkbox" not in html:
        return html

    def _repl(m: re.Match) -> str:
        tag = m.group(0)
        return CHECKED_SVG if "checked" in tag else UNCHECKED_SVG

    return CHECKBOX_TAG_RE.sub(_repl, html)


DOCUMENT_BASE_CSS = (
    "\n/* MarkNote Base Document Styles: Tasklists, Tables, Code Blocks, and TOC */\n"
    ".markdown-body ul.contains-task-list,\n"
    ".markdown-body ol.contains-task-list {\n"
    "  list-style: none !important;\n"
    "  list-style-type: none !important;\n"
    "  padding-left: 0 !important;\n"
    "  margin-left: 0 !important;\n"
    "}\n"
    ".markdown-body li.task-list-item > ul.contains-task-list,\n"
    ".markdown-body li.task-list-item > ol.contains-task-list {\n"
    "  padding-left: 24px !important;\n"
    "  margin-left: 0 !important;\n"
    "}\n"
    ".markdown-body li.task-list-item {\n"
    "  list-style: none !important;\n"
    "  list-style-type: none !important;\n"
    "  padding-left: 24px !important;\n"
    "  text-indent: -24px !important;\n"
    "  margin-top: 5px;\n"
    "  margin-bottom: 5px;\n"
    "  line-height: 1.6;\n"
    "}\n"
    ".markdown-body li.task-list-item > input.task-list-item-checkbox {\n"
    "  margin: 0 6px 0 0;\n"
    "  vertical-align: middle;\n"
    "}\n"
    ".markdown-body .task-svg {\n"
    "  vertical-align: -2px;\n"
    "  margin-right: 6px;\n"
    "  display: inline-block;\n"
    "  flex-shrink: 0;\n"
    "}\n"
    "/* Ep bang luon fit 100% chieu rong va tu dong wrap noi dung */\n"
    ".markdown-body table {\n"
    "  display: table !important;\n"
    "  width: 100% !important;\n"
    "  max-width: 100% !important;\n"
    "  table-layout: auto !important;\n"
    "  border-collapse: collapse !important;\n"
    "  word-wrap: break-word !important;\n"
    "  overflow-wrap: break-word !important;\n"
    "  word-break: break-word !important;\n"
    "}\n"
    ".markdown-body table th,\n"
    ".markdown-body table td {\n"
    "  word-wrap: break-word !important;\n"
    "  overflow-wrap: break-word !important;\n"
    "  word-break: break-word !important;\n"
    "  white-space: normal !important;\n"
    "}\n"
    ".markdown-body table code {\n"
    "  word-break: break-all !important;\n"
    "  overflow-wrap: break-word !important;\n"
    "  white-space: normal !important;\n"
    "}\n"
    "/* Ep code block va inline code tu dong xuong dong */\n"
    ".markdown-body pre,\n"
    ".markdown-body pre code {\n"
    "  white-space: pre-wrap !important;\n"
    "  word-break: break-word !important;\n"
    "  overflow-wrap: break-word !important;\n"
    "}\n"
    "/* Bo goc va can le cho Table of Contents (TOC) */\n"
    ".markdown-body .toc {\n"
    "  box-decoration-break: clone !important;\n"
    "  -webkit-box-decoration-break: clone !important;\n"
    "}\n"
    ".markdown-body .toc > ul > li > a {\n"
    "  font-weight: 600 !important;\n"
    "}\n"
    ".markdown-body .toc ul ul li a {\n"
    "  font-style: italic !important;\n"
    "  font-weight: normal !important;\n"
    "}\n"
    ".markdown-body .toc a::after {\n"
    "  font-style: normal !important;\n"
    "  font-weight: normal !important;\n"
    "}\n"
)
TASKLIST_BASE_CSS = DOCUMENT_BASE_CSS

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
    "  .markdown-body .toc {\n"
    "    box-decoration-break: clone !important;\n"
    "    -webkit-box-decoration-break: clone !important;\n"
    "  }\n"
    "  .markdown-body .toc a {\n"
    "    color: var(--fg-default, #1f2328);\n"
    "    text-decoration: none;\n"
    "  }\n"
    "  .markdown-body .toc > ul > li > a {\n"
    "    font-weight: 600 !important;\n"
    "  }\n"
    "  .markdown-body .toc ul ul li a {\n"
    "    font-style: italic !important;\n"
    "    font-weight: normal !important;\n"
    "  }\n"
    "  .markdown-body .toc a::after {\n"
    "    content: leader('. ') target-counter(attr(href), page);\n"
    "    color: var(--fg-muted, #59636e);\n"
    "    padding-left: 6px;\n"
    "    font-style: normal !important;\n"
    "    font-weight: normal !important;\n"
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
    full_css = (css or "") + "\n" + TASKLIST_BASE_CSS
    return (
        HTML_HEADER % title
        + full_css
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
    # Project root khi chay source truc tiep
    project_root = Path(__file__).resolve().parent.parent
    candidates.extend(
        [
            project_root / "dist" / "marknote" / "bin" / "weasyprint" / "weasyprint.exe",
            project_root / "build" / "weasyprint-windows" / "weasyprint.exe",
            project_root / "build" / "weasyprint-test" / "weasyprint.exe",
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
        run_kwargs = {
            "capture_output": True,
            "text": True,
        }
        if sys.platform == "win32":
            run_kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
        result = subprocess.run(
            [str(exe), str(html_file), str(path)],
            **run_kwargs,
        )
        if result.returncode != 0:
            raise RuntimeError("weasyprint-failed")


class Exporter:
    """Ghi ra file HTML hoac PDF dung chung mot theme (UC13)."""

    def toHtml(self, html_body: str, css: str, path) -> None:
        html_body = replace_checkboxes_with_svg(html_body)
        html_body = embed_images_as_base64(html_body)
        Path(path).write_text(
            build_document(html_body, css), encoding="utf-8"
        )

    def toPdf(self, html_body: str, css: str, path) -> None:
        html_body = replace_checkboxes_with_svg(html_body)
        html_body = embed_images_as_base64(html_body)
        document = build_document(
            html_body, css + PDF_PAGE_RULE + TOC_PRINT_RULE
        )
        cli_exe = find_windows_weasyprint()

        try:
            from weasyprint import HTML
            HTML(string=document).write_pdf(str(path))
            return
        except (ImportError, OSError, Exception) as exc:
            # Neu co ban weasyprint.exe dong goi san (kem Pango) tren Windows, uu tien fallback ngay
            if sys.platform == "win32" and cli_exe:
                render_pdf_via_cli(document, path)
                return

            msg = str(exc).lower()
            if isinstance(exc, ImportError) and "weasyprint" in msg:
                raise RuntimeError("weasyprint-missing") from exc
            if "cannot load library" in msg and any(
                lib in msg for lib in ("libgobject", "libpango", "gobject", "pango")
            ):
                raise RuntimeError("weasyprint-libs") from exc
            raise
