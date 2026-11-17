"""Khung xem truoc song song, bo render Markdown va SyncScroll."""

from __future__ import annotations

import re
import unicodedata
from html import escape, unescape
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QColor
from PySide6.QtWebEngineCore import QWebEngineSettings
from PySide6.QtWebEngineWidgets import QWebEngineView

from exporter import (
    build_document,
    enhance_html_components,
    replace_checkboxes_with_svg,
    render_donut_widget,
    DONUT_DIRECTIVE_RE,
)
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

        orig_fence = self.md.renderer.rules.get("fence")

        def _render_fence(tokens, idx, options, env):
            tok = tokens[idx]
            info = tok.info.strip() if tok.info else ""
            lang = info.split()[0].lower() if info else ""
            if lang == "donut":
                return render_donut_widget(tok.content) + "\n"
            if orig_fence:
                return orig_fence(tokens, idx, options, env)
            return self.md.renderer.renderToken(tokens, idx, options)

        self.md.renderer.rules["fence"] = _render_fence

    def render(self, md: str) -> str:
        clean_md = normalize_tasklists(md or "")
        if "[[donut" in clean_md.lower():
            clean_md = DONUT_DIRECTIVE_RE.sub(lambda m: render_donut_widget(m.group("body")), clean_md)
        html = self.md.render(clean_md)
        return enhance_html_components(html)

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


class TocConfig:
    """Cau hinh tuy bien Table of Contents (TOC)."""

    def __init__(
        self,
        is_toc: bool = False,
        label: str = "Table of Contents",
        align: str = "left",
        no_bullet: bool = False,
        title_color: str = "#0969da",
        item_color: str = "",
        depth_colors: dict[int, str] | None = None,
        max_depth: int = 6,
    ):
        self.is_toc = is_toc
        self.label = label
        self.align = align
        self.no_bullet = no_bullet
        self.title_color = title_color
        self.item_color = item_color
        self.depth_colors = depth_colors or {}
        self.max_depth = max_depth

    def __iter__(self):
        return iter((self.is_toc, self.label, self.align, self.no_bullet))

    def __getitem__(self, idx):
        return (self.is_toc, self.label, self.align, self.no_bullet)[idx]

    def __repr__(self):
        return (
            f"TocConfig(is_toc={self.is_toc}, label={self.label!r}, align={self.align!r}, "
            f"no_bullet={self.no_bullet}, title_color={self.title_color!r}, "
            f"depth_colors={self.depth_colors!r}, max_depth={self.max_depth})"
        )


def _build_toc(
    items,
    label: str | TocConfig = "Table of Contents",
    align: str = "left",
    no_bullet: bool = False,
    title_color: str = "#0969da",
    item_color: str = "",
    depth_colors: dict[int, str] | None = None,
    max_depth: int = 6,
) -> str:
    if isinstance(label, TocConfig):
        cfg = label
        label = cfg.label
        align = cfg.align
        no_bullet = cfg.no_bullet
        title_color = cfg.title_color
        item_color = cfg.item_color
        depth_colors = cfg.depth_colors
        max_depth = cfg.max_depth

    depth_colors = depth_colors or {}
    filtered_items = [it for it in items if it[0] <= max_depth] if max_depth < 6 else items
    if not filtered_items:
        return ""

    toc_class = "toc no-bullet" if no_bullet else "toc"
    out = ['<div class="%s">' % toc_class]
    if label:
        align_class = "toc-title toc-align-%s" % (align or "left")
        title_style = (
            f' style="color: {escape(title_color)} !important; font-weight: 800 !important;"'
            if title_color
            else ' style="font-weight: 800 !important;"'
        )
        out.append('<div class="%s"%s><strong>%s</strong></div>' % (align_class, title_style, escape(label)))
    out.append("<ul>")
    stack = [filtered_items[0][0]]
    has_open_li = False
    for level, anchor, text in filtered_items:
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
        depth = len(stack)
        link_color = depth_colors.get(depth) or item_color
        style_attr = f' style="color: {escape(link_color)} !important;"' if link_color else ""
        out.append('<li class="toc-item toc-depth-%d"><a href="#%s"%s>%s</a>' % (depth, anchor, style_attr, text))
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
TOC_KV_RE = re.compile(
    r"""(?P<key>[\w-]+)\s*[=:]\s*(?:\"(?P<val1>[^\"]*)\"|'(?P<val2>[^']*)'|(?P<val3>[^\s\),]+))"""
)


def _parse_toc_directive(raw: str) -> TocConfig:
    """Phan tich cu phap [[TOC ...]] linh hoat:
    - Custom tieu de: [[TOC="Muc luc"]], [[TOC='Tieu de']], [[TOC title="Table of Contents"]]
    - Can le: center / align=center / right / left
    - No-bullet: no-bullet / nobullet
    - Mau tieu de: title-color="#0969da" / title_color="blue" (mac dinh xanh dam)
    - Mau tung cap: c1="#000" c2="#333" c3="navy"
    - Mau chung cho cac item: color="black" / item-color="#1f2328"
    - Do sau toi da: depth=3 / max-depth=3
    - Ket hop: [[TOC="Danh muc" center no-bullet title-color="#0284c7" c2="blue"]]
    """
    m = TOC_DIRECTIVE_RE.match(raw.strip())
    if not m:
        return TocConfig(False, "Table of Contents", "left", False)

    body = m.group("body") or ""
    tail = m.group("tail") or ""
    combined = f"{body} {tail}"

    # 1. Trich xuat tieu de neu co dau nhay truc tiep sau TOC
    label = "Table of Contents"
    tm = TOC_TITLE_QUOTE_RE.match(body.strip())
    if tm:
        label = tm.group(1) if tm.group(1) is not None else tm.group(2)
        body_rest = body.strip()[tm.end():]
        search_str = f"{body_rest} {tail}"
    else:
        # Tim kiem tieu de trong body
        tm_search = TOC_TITLE_QUOTE_RE.search(body)
        if tm_search and not any(k in body[:tm_search.start()].lower() for k in ("color", "align", "depth", "title")):
            label = tm_search.group(1) if tm_search.group(1) is not None else tm_search.group(2)
            span = tm_search.span()
            search_str = f"{body[:span[0]]} {body[span[1]:]} {tail}"
        else:
            search_str = combined

    # 2. Trich xuat cac cap thuoc tinh key-value
    depth_colors: dict[int, str] = {}
    title_color = "#0969da"  # Mac dinh tieu de in dam mau xanh chuan
    item_color = ""
    max_depth = 6

    for km in TOC_KV_RE.finditer(search_str):
        k = km.group("key").lower()
        v = (
            km.group("val1")
            if km.group("val1") is not None
            else (km.group("val2") if km.group("val2") is not None else km.group("val3"))
        )
        if not v:
            continue
        v = v.strip()

        if k in ("title", "label") and label == "Table of Contents":
            label = v
        elif k in ("title-color", "title_color", "titlecolor"):
            title_color = v
        elif k in ("color", "item-color", "item_color"):
            item_color = v
        elif k in ("max-depth", "maxdepth", "depth"):
            try:
                max_depth = int(v)
            except ValueError:
                pass
        elif k in ("c1", "color1", "level1-color", "level1_color"):
            depth_colors[1] = v
        elif k in ("c2", "color2", "level2-color", "level2_color"):
            depth_colors[2] = v
        elif k in ("c3", "color3", "level3-color", "level3_color"):
            depth_colors[3] = v
        elif k in ("c4", "color4", "level4-color", "level4_color"):
            depth_colors[4] = v
        elif k in ("c5", "color5", "level5-color", "level5_color"):
            depth_colors[5] = v
        elif k in ("c6", "color6", "level6-color", "level6_color"):
            depth_colors[6] = v

    # 3. Can le trai / giua / phai
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

    # 4. No-bullet
    no_bullet = bool(TOC_NO_BULLET_RE.search(search_str))

    return TocConfig(
        is_toc=True,
        label=label.strip(),
        align=align,
        no_bullet=no_bullet,
        title_color=title_color,
        item_color=item_color,
        depth_colors=depth_colors,
        max_depth=max_depth,
    )


TOC_RE = TOC_DIRECTIVE_RE
HTML_HEADING_RE = re.compile(
    r"<h([1-6])\b([^>]*)>(.*?)</h\1>",
    re.IGNORECASE | re.DOTALL,
)
ID_ATTR_RE = re.compile(r"""\bid\s*=\s*(?:\"([^\"]*)\"|'([^']*)')""", re.IGNORECASE)
TOC_DIRECTIVE_SEARCH_RE = re.compile(
    r"\[\[TOC(?P<body>.*?)\]\](?:\((?P<tail>.*?)\))?",
    re.IGNORECASE,
)


def _anchors_toc(state):
    """Gan id cho heading (Markdown # va HTML <h1-6>) va thay [[TOC ...]] bang muc luc co link nhan.
    CHI liet ke cac muc o duoi vi tri cua [[TOC ...]] trong tai lieu."""
    taken = set()
    headings = []
    toc_index = None
    toc_cfg: TocConfig | None = None
    toc_in_html = False
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
            if toc_index is not None:
                headings.append((level, anchor, escape(text)))
        elif tok.type in ("html_block", "html_inline"):
            toc_pos_in_tok = -1
            if toc_index is None and ("[[toc" in tok.content.lower()):
                dm = TOC_DIRECTIVE_SEARCH_RE.search(tok.content)
                if dm:
                    cfg = _parse_toc_directive(dm.group(0))
                    if cfg.is_toc:
                        toc_index = i
                        toc_cfg = cfg
                        toc_in_html = True
                        toc_pos_in_tok = dm.start()

            if "<h" in tok.content.lower():
                def _repl_h(m: re.Match) -> str:
                    lvl = int(m.group(1))
                    attrs = m.group(2)
                    inner = m.group(3)
                    pure_text = unescape(re.sub(r"<[^>]+>", "", inner).strip())
                    if not pure_text:
                        return m.group(0)
                    id_m = ID_ATTR_RE.search(attrs)
                    if id_m:
                        anc = id_m.group(1) or id_m.group(2)
                        taken.add(anc)
                        new_tag = f"<h{lvl}{attrs}>{inner}</h{lvl}>"
                    else:
                        anc = _slugify(pure_text, taken)
                        new_tag = f'<h{lvl} id="{anc}"{attrs}>{inner}</h{lvl}>'

                    is_after_toc = False
                    if toc_pos_in_tok >= 0:
                        is_after_toc = (m.start() > toc_pos_in_tok)
                    elif toc_index is not None:
                        is_after_toc = True

                    if is_after_toc:
                        headings.append((lvl, anc, escape(pure_text)))
                    return new_tag

                tok.content = HTML_HEADING_RE.sub(_repl_h, tok.content)

        elif toc_index is None and tok.type == "inline":
            cfg = _parse_toc_directive(tok.content)
            if cfg.is_toc:
                toc_index = i
                toc_cfg = cfg
                toc_in_html = False
        i += 1

    if toc_index is None or toc_cfg is None:
        return

    toc_html = _build_toc(headings, toc_cfg) if headings else ""

    if toc_in_html:
        tokens[toc_index].content = TOC_DIRECTIVE_SEARCH_RE.sub(lambda _: toc_html, tokens[toc_index].content, count=1)
    else:
        start = toc_index - 1
        if start >= 0 and tokens[start].type == "paragraph_open":
            if headings:
                token = tokens[start]
                token.type = "html_block"
                token.tag = ""
                token.content = toc_html
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