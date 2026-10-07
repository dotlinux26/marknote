"""Khung xem truoc song song, bo render Markdown va SyncScroll."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QColor
from PySide6.QtWebEngineWidgets import QWebEngineView

from exporter import build_document
from settings import (
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

    def render(self, md: str) -> str:
        return self.md.render(md or "")

    @staticmethod
    def _highlight(code: str, lang: str | None, attrs: str) -> str:
        name = lang.split()[0] if lang else None
        return _pygments_html(code, name)


class PreviewPane(QWebEngineView):
    """Khung xem truoc: render GFM moi lan co thay doi, dung theme."""

    def __init__(self, renderer, theme_manager, parent=None):
        super().__init__(parent)
        self._renderer = renderer
        self._theme = theme_manager
        self._last_md = ""
        self.setMinimumWidth(360)
        self.page().setBackgroundColor(QColor("#ffffff"))

    def render(self, md: str):
        """Render lai bang noi dung markdown hien tai (UC06)."""
        self._last_md = md or ""
        css = self._theme.getCss(self._theme.current())
        doc = build_document(self._renderer.render(self._last_md), css or "")
        self.setHtml(doc, QUrl.fromLocalFile(str(Path.home())))

    def reloadCss(self, css: str | None = None):
        """UC12: doi theme thi render lai voi CSS moi, khong can restart."""
        if not self._last_md:
            return
        if css is None:
            css = self._theme.getCss(self._theme.current()) or ""
        doc = build_document(self._renderer.render(self._last_md), css)
        self.setHtml(doc, QUrl.fromLocalFile(str(Path.home())))

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