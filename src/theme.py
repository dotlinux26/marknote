"""Quan ly theme CSS: quet thu muc, doc noi dung va ap dung."""

from __future__ import annotations

import sys
from pathlib import Path

from settings import DEFAULT_THEME, THEME_DIR, THEME_SUFFIX, KEY_THEME

def _resolve_assets_theme_dir() -> Path:
    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            cand = Path(meipass) / "assets" / "themes"
            if cand.is_dir():
                return cand
        cand = Path(sys.executable).resolve().parent / "assets" / "themes"
        if cand.is_dir():
            return cand
    return Path(__file__).resolve().parent.parent / "assets" / "themes"

ASSETS_THEME_DIR = _resolve_assets_theme_dir()


class ThemeManager:
    """Doc danh sach file .css va noi dung cua chung."""

    def __init__(self, settings_dao):
        self._settings = settings_dao
        self.directory = THEME_DIR
        self.last_error: str | None = None

    def ensureDefaults(self):
        """Copy theme mac dinh tu assets sang thu muc nguoi dung neu can."""
        self.directory.mkdir(parents=True, exist_ok=True)
        if not list(self.directory.glob("*" + THEME_SUFFIX)):
            for css in sorted(ASSETS_THEME_DIR.glob("*" + THEME_SUFFIX)):
                target = self.directory / css.name
                if not target.exists():
                    target.write_text(css.read_text(encoding="utf-8"), encoding="utf-8")

    def listThemes(self) -> list:
        """UC11: quet thu muc, loc .css, tra ten khong kem phan mo rong."""
        if not self.directory.exists():
            return []
        return sorted(
            path.stem
            for path in self.directory.iterdir()
            if path.is_file() and path.suffix == THEME_SUFFIX
        )

    def getCss(self, name: str) -> str | None:
        """Doc noi dung file theme. Tra None neu file khong ton tai."""
        path = self.directory / (name + THEME_SUFFIX)
        if not path.exists():
            return None
        return path.read_text(encoding="utf-8")

    def current(self) -> str:
        return self._settings.get(KEY_THEME, DEFAULT_THEME)

    @staticmethod
    def validate(css: str) -> bool:
        """Kiem tra so bo: khac rong, can bang dau ngoac nhon."""
        if not css or "{" not in css:
            return False
        return css.count("{") == css.count("}")

    def applyTheme(self, name: str) -> bool:
        """UC12: luu ten theme vao settings quan he database."""
        self.last_error = None
        css = self.getCss(name)
        if css is None:
            self.last_error = "missing"
            return False
        if not self.validate(css):
            self.last_error = "invalid"
            return False
        self._settings.set(KEY_THEME, name)
        return True

    def resetToDefault(self) -> bool:
        return self.applyTheme(DEFAULT_THEME)
