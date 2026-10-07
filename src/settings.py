"""Duong dan, hang so va hop thoai cai dat cua MarkNote."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QVBoxLayout,
)

APP_NAME = "MarkNote"
APP_DIR = Path.home() / ".marknote"
DB_PATH = APP_DIR / "notes.db"
THEME_DIR = APP_DIR / "themes"
THEME_SUFFIX = ".css"

DEFAULT_THEME = "default"
SYNC_SCROLL_ON = "ON"
SYNC_SCROLL_OFF = "OFF"
KEY_THEME = "theme"
KEY_SYNC_SCROLL = "sync_scroll"
KEY_LAST_OPENED = "last_opened_id"

DEFAULT_SETTINGS = {
    KEY_THEME: DEFAULT_THEME,
    KEY_SYNC_SCROLL: SYNC_SCROLL_ON,
    KEY_LAST_OPENED: "0",
}


class SettingsDialog(QDialog):
    """Hop thoai Cai dat > Appearance: xem va chon theme CSS."""

    themeSelected = Signal(str)

    def __init__(self, theme_manager, settings_dao, parent=None):
        super().__init__(parent)
        self._theme_manager = theme_manager
        self._settings = settings_dao
        self._loading = True

        self.setWindowTitle("Cai dat - Giao dien")
        self.setMinimumWidth(440)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)

        title = QLabel("Giao dien xem truoc")
        title.setObjectName("dialogTitle")

        self._combo = QComboBox()
        self._combo.currentIndexChanged.connect(self._on_theme_chosen)

        self._path_label = QLabel()
        self._path_label.setWordWrap(True)
        self._path_label.setObjectName("mutedLabel")

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        form.setSpacing(10)
        form.addRow("Theme CSS:", self._combo)
        form.addRow("Thu muc theme:", self._path_label)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        buttons.accepted.connect(self.accept)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 16)
        layout.setSpacing(14)
        layout.addWidget(title)
        layout.addLayout(form)
        layout.addWidget(buttons)

        self._reload()

    def _reload(self):
        """Quet thu muc theme va do danh sach vao dropdown (UC11)."""
        self._loading = True
        self._combo.clear()
        current = self._settings.get(KEY_THEME, DEFAULT_THEME)
        for name in self._theme_manager.listThemes():
            self._combo.addItem(name, name)
        index = self._combo.findData(current)
        if index < 0 and self._combo.count() > 0:
            index = 0
        if index >= 0:
            self._combo.setCurrentIndex(index)
        self._path_label.setText(str(self._theme_manager.directory))
        self._loading = False

    def _on_theme_chosen(self, index):
        """Chon theme moi trong dropdown (UC12)."""
        if self._loading or index < 0:
            return
        name = self._combo.itemData(index)
        if not name:
            return
        if self._theme_manager.applyTheme(name):
            self.themeSelected.emit(name)
            return
        error = self._theme_manager.last_error
        if error == "missing":
            self._recover_missing(name)
        else:
            self._reject_invalid(name)

    def _recover_missing(self, name):
        from PySide6.QtWidgets import QMessageBox

        answer = QMessageBox.question(
            self,
            "Theme file missing",
            f"Khong tim thay file {name}.css trong {self._theme_manager.directory}.\n"
            "Ve lai theme default.css?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if answer == QMessageBox.StandardButton.Yes:
            self._theme_manager.applyTheme(DEFAULT_THEME)
            self.themeSelected.emit(DEFAULT_THEME)
        self._restore_combo_selection()

    def _reject_invalid(self, name):
        from PySide6.QtWidgets import QMessageBox

        QMessageBox.warning(
            self,
            "CSS sai cu phap",
            f"File {name}.css khong hop le. Giu theme truoc do.",
        )
        self._restore_combo_selection()

    def _restore_combo_selection(self):
        self._loading = True
        index = self._combo.findData(self._settings.get(KEY_THEME, DEFAULT_THEME))
        if index >= 0:
            self._combo.setCurrentIndex(index)
        self._loading = False
