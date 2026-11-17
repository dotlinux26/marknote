"""Khung xem truoc song song, bo render Markdown va SyncScroll."""

from __future__ import annotations

import re
import unicodedata
from html import escape
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QColor
from PySide6.QtWebEngineCore import QWebEngineSettings
from PySide6.QtWebEngineWidgets import QWebEngineView

from exporter import build_document, replace_checkboxes_with_svg
from settings import (
    APP_DIR,
    KEY_SYNC_SCROLL,
    SYNC_SCROLL_OFF,
    SYNC_SCROLL_ON,
)

try:
    from mdit_py_plugins.tasklists import tasklists_plugin
    from mdit_py_plugins.footnote import footnote_plugin

    _HAS_EXTRA_PLUGINS = True
except ImportError:
    _HAS_EXTRA_PLUGINS = False

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import TextLexer, get_lexer_by_name
from pygments.util import ClassNotFound


TASKLIST_RE = re.compile(
    r"^(?P<indent>[ \t]*)(?:[-*+]\s*)?\[(?P<mark>[ xX])\][ \t]*(?P<rest>.*)$"
)


def normalize_tasklists(md: str) -> str:
    """Chuan hoa cac dong danh sach cong viec ([ ], [x], -[ ], v.v.) thanh - [ ] chuan GFM,
    dong thoi bo qua cac block code ``` hoac ~~~."""
    if not md or "[" not in md:
        return md

    lines = md.splitlines(keepends=True)
    out: list[str] = []
    in_code_block = False
    fence_char = ""
    fence_len = 0

    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            char = stripped[0]
            count = len(stripped) - len(stripped.lstrip(char))
            if not in_code_block:
                in_code_block = True
                fence_char = char
                fence_len = count
                out.append(line)
                continue
            elif in_code_block and char == fence_char and count >= fence_len:
                in_code_block = False
                fence_char = ""
                fence_len = 0
                out.append(line)
                continue

        if in_code_block:
            out.append(line)
            continue

        m = TASKLIST_RE.match(line.rstrip("\r\n"))
        if m:
            indent = m.group("indent")
            mark = m.group("mark").lower()
            rest = m.group("rest")
            ending = "\r\n" if line.endswith("\r\n") else ("\n" if line.endswith("\n") else "")
            out.append(f"{indent}- [{mark}] {rest}{ending}")
        else:
            out.append(line)

    return "".join(out)


def _pygments_html(code: str, lang: str | None) -> str:
    """To mau code block bang Pygments, style inline cho file doc lap."""
    try:
        lexer = get_lexer_by_name(lang) if lang else TextLexer()
    except ClassNotFound:
        lexer = TextLexer()
    body = highlight(code, lexer, HtmlFormatter(nowrap=True, noclasses=True))
    clean_lang = (lang or "").replace('"', "")
    if clean_lang:
        return (
            '<pre data-lang="%s" class="highlight">'
            "<code>%s</code></pre>" % (clean_lang, body)
        )
    return '<pre class="highlight"><code>%s</code></pre>' % body


class MarkdownRenderer:
    """Chuyen Markdown theo chuan GFM sang HTML."""

    def __init__(self):
        from markdown_it import MarkdownIt

        self.md = MarkdownIt("gfm-like", {"linkify": True})
        self.md.options["highlight"] = self._highlight
        if _HAS_EXTRA_PLUGINS:
            self.md.use(tasklists_plugin)
            self.md.use(footnote_plugin)
        self.md.core.ruler.push("anchors_toc", _anchors_toc)

    def render(self, md: str) -> str:
        clean_md = normalize_tasklists(md or "")
        html = self.md.render(clean_md)
        return replace_checkboxes_with_svg(html)

    @staticmethod
    def _highlight(code: str, lang: str | None, attrs: str) -> str:
        name = lang.split()[0] if lang else None
        return _pygments_html(code, name)


def _slugify(text: str, taken: set) -> str:
    """Chuyen tieu de thanh id an toan (bo dau, giong GitHub)."""
    part = unicodedata.normalize("NFKD", text)
    part = "".join(ch for ch in part if not unicodedata.combining(ch))
    part = re.sub(r"[^\w\- ]+", "", part, flags=re.UNICODE).strip().lower()
    part = re.sub(r"[ _]+", "-", part) or "section"
    slug = part
    n = 2
    while slug in taken:
        slug = "%s-%d" % (part, n)
        n += 1
    taken.add(slug)
    return slug


def _inline_text(token) -> str:
    parts = []
    for child in token.children or ():
        if child.type in ("text", "code_inline", "image"):
            parts.append(child.content)
        elif child.type in ("softbreak", "hardbreak"):
            parts.append(" ")
    return "".join(parts).strip() or token.content.strip()


def _build_toc(items, label: str, align: str = "left", no_bullet: bool = False) -> str:
    toc_class = "toc no-bullet" if no_bullet else "toc"
    out = ['<div class="%s">' % toc_class]
    if label:
        align_class = "toc-title toc-align-%s" % (align or "left")
        out.append('<div class="%s"><strong>%s</strong></div>' % (align_class, escape(label)))
    out.append("<ul>")
    stack = [items[0][0]]
    has_open_li = False
    for level, anchor, text in items:
        while len(stack) > 1 and level < stack[-1]:
            if has_open_li:
                out.append("</li>")
                has_open_li = False
            out.append("</ul>")
            stack.pop()
        if level == stack[-1]:
            if has_open_li:
                out.append("</li>")
            has_open_li = False
        elif level > stack[-1]:
            out.append("<ul>")
            stack.append(level)
            has_open_li = False
        out.append('<li><a href="#%s">%s</a>' % (anchor, text))
        has_open_li = True
    if has_open_li:
        out.append("</li>")
    while stack:
        out.append("</ul>")
        stack.pop()
    out.append("</div>")
    return "".join(out)


TOC_DIRECTIVE_RE = re.compile(
    r"^\[\[TOC(?P<body>.*?)\]\](?:\((?P<tail>.*?)\))?$",
    re.IGNORECASE,
)
TOC_TITLE_QUOTE_RE = re.compile(r"""(?:=|\:)?\s*(?:\"([^\"]*)\"|'([^']*)')""")
TOC_ALIGN_RE = re.compile(r"\b(?:align\s*[=:]\s*)?(left|center|centre|right)\b", re.IGNORECASE)
TOC_NO_BULLET_RE = re.compile(r"\bno-?bullets?\b", re.IGNORECASE)


def _parse_toc_directive(raw: str) -> tuple[bool, str, str, bool]:
    """Phan tich cu phap [[TOC ...]] linh hoat:
    - Custom tieu de: [[TOC="Muc luc"]], [[TOC='Tieu de']]
    - Can le: center / align=center / right / left
    - No-bullet: no-bullet / nobullet
    - Ket hop: [[TOC="Danh muc" center no-bullet]] hoac [[TOC="Danh muc"]](center, no-bullet)
    """
    m = TOC_DIRECTIVE_RE.match(raw.strip())
    if not m:
        return (False, "Table of Contents", "left", False)

    body = m.group("body") or ""
    tail = m.group("tail") or ""
    combined = f"{body} {tail}"

    # 1. Trich xuat tieu de neu co dau nhay
    tm = TOC_TITLE_QUOTE_RE.search(body)
    if tm:
        label = tm.group(1) if tm.group(1) is not None else tm.group(2)
        span = tm.span()
        body_without_title = body[:span[0]] + body[span[1]:]
        search_str = f"{body_without_title} {tail}"
    else:
        label = "Table of Contents"
        search_str = combined

    # 2. Can le trai / giua / phai
    align = "left"
    am = TOC_ALIGN_RE.search(search_str)
    if am:
        val = am.group(1).lower()
        if val in ("center", "centre"):
            align = "center"
        elif val == "right":
            align = "right"
        elif val == "left":
            align = "left"

    # 3. No-bullet
    no_bullet = bool(TOC_NO_BULLET_RE.search(search_str))

    return (True, label.strip(), align, no_bullet)


TOC_RE = TOC_DIRECTIVE_RE


def _anchors_toc(state):
    """Gan id cho heading va thay [[TOC ...]] bang muc luc co link nhan."""
    taken = set()
    headings = []
    toc_index = None
    toc_label = "Table of Contents"
    toc_align = "left"
    toc_no_bullet = False
    tokens = state.tokens
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok.type == "heading_open":
            level = int(tok.tag.strip("h"))
            inline = tokens[i + 1] if i + 1 < len(tokens) else None
            text = _inline_text(inline) if inline is not None else ""
            anchor = _slugify(text, taken)
            tok.attrSet("id", anchor)
            headings.append((level, anchor, escape(text)))
        elif toc_index is None and tok.type == "inline":
            is_toc, label, align, no_bullet = _parse_toc_directive(tok.content)
            if is_toc:
                toc_index = i
                toc_label = label
                toc_align = align
                toc_no_bullet = no_bullet
        i += 1
    if toc_index is None:
        return
    start = toc_index - 1
    if start >= 0 and tokens[start].type == "paragraph_open":
        if headings:
            token = tokens[start]
            token.type = "html_block"
            token.tag = ""
            token.content = _build_toc(headings, toc_label, align=toc_align, no_bullet=toc_no_bullet)
            del tokens[start + 1 : start + 3]
        else:
            del tokens[start : start + 3]


class PreviewPane(QWebEngineView):
    """Khung xem truoc: render GFM moi lan co thay doi, dung theme."""

    def __init__(self, renderer, theme_manager, parent=None):
        super().__init__(parent)
        self._renderer = renderer
        self._theme = theme_manager
        self._last_md = ""
        self.setMinimumWidth(360)
        self.page().setBackgroundColor(QColor("#ffffff"))

        # Cho phep truy cap anh va file cuc bo tu thu muc media
        settings = self.settings()
        settings.setAttribute(
            QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True
        )
        settings.setAttribute(
            QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True
        )

    def _base_url(self) -> QUrl:
        return QUrl.fromLocalFile(str(APP_DIR.resolve()) + "/")

    def render(self, md: str):
        """Render lai bang noi dung markdown hien tai (UC06)."""
        self._last_md = md or ""
        css = self._theme.getCss(self._theme.current())
        doc = build_document(self._renderer.render(self._last_md), css or "")
        self.setHtml(doc, self._base_url())

    def reloadCss(self, css: str | None = None):
        """UC12: doi theme thi render lai voi CSS moi, khong can restart."""
        if not self._last_md:
            return
        if css is None:
            css = self._theme.getCss(self._theme.current()) or ""
        doc = build_document(self._renderer.render(self._last_md), css)
        self.setHtml(doc, self._base_url())

    def setScroll(self, percent: float):
        """UC07: cuon khung xem truoc theo phan tram tu thanh cuon editor."""
        if not self._last_md:
            return
        js = (
            "var d = document.documentElement;"
            "var max = d.scrollHeight - window.innerHeight;"
            "window.scrollTo(0, Math.round(%f * Math.max(0, max)));"
        ) % max(0.0, min(1.0, percent))
        self.page().runJavaScript(js)


class SyncScrollController:
    """Dieu khien dong bo cuon giua editor va preview (UC07)."""

    def __init__(self, settings_dao):
        self._settings = settings_dao
        self._enabled = (
            settings_dao.get(KEY_SYNC_SCROLL, SYNC_SCROLL_ON) == SYNC_SCROLL_ON
        )

    def setEnabled(self, enabled: bool):
        self._enabled = enabled
        self._settings.set(
            KEY_SYNC_SCROLL, SYNC_SCROLL_ON if enabled else SYNC_SCROLL_OFF
        )

    def isEnabled(self) -> bool:
        return self._enabled

    def onScroll(self, percent: float) -> float | None:
        """Tra ve phan tram muon cuon, hoac None neu sync dang tat."""
        if not self._enabled:
            return None
        return max(0.0, min(1.0, percent))