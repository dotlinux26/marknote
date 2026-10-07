"""Cua so chinh cua MarkNote - ghi chu Markdown offline."""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QSplitter,
    QToolBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from db import DbManager, NoteDAO, SettingsDAO, TagDAO
from editor import EditorPane, FindReplaceDialog, SearchPanel
from exporter import Exporter
from preview import MarkdownRenderer, PreviewPane, SyncScrollController
from settings import APP_NAME, DEFAULT_THEME, SettingsDialog, KEY_LAST_OPENED, KEY_THEME
from theme import ThemeManager

APP_STYLE = """
QMainWindow, QDialog, QMessageBox { background: #f6f8fa; }
QWidget { color: #1f2328; font-size: 14px; }
QMenuBar { background: #ffffff; border-bottom: 1px solid #d8dee4; }
QMenuBar::item { padding: 6px 10px; background: transparent; border-radius: 2px; }
QMenuBar::item:selected { background: #eef1f4; }
QMenu { background: #ffffff; border: 1px solid #d1d9e0; border-radius: 2px; padding: 4px; color: #1f2328; }
QMenu::item { padding: 6px 20px; border-radius: 2px; color: #1f2328; }
QMenu::item:selected { color: #1f2328; background: #eef1f4; }
QMenu::item:disabled { color: #8b949e; }
QMenu::separator { height: 1px; background: #d8dee4; margin: 4px 8px; }
QToolBar { background: #f6f8fa; border: none; border-bottom: 1px solid #d8dee4; spacing: 4px; padding: 4px 6px; }
QToolButton { padding: 5px 10px; border: 1px solid #d1d9e0; border-radius: 2px; background: transparent; color: #1f2328; }
QToolButton:hover { background: #eef1f4; }
QToolButton:pressed { background: #d8dee4; }
QToolButton:checked { background: #ddf4ff; border-color: #54aeff; color: #0969da; }
QLineEdit { padding: 6px 8px; border: 1px solid #d1d9e0; border-radius: 2px; background: #ffffff; color: #1f2328; }
QLineEdit:focus { border-color: #0969da; }
QPlainTextEdit { background: #ffffff; border: 1px solid #d8dee4; border-radius: 2px; padding: 6px; color: #1f2328; selection-background-color: #add6ff; }
QComboBox { padding: 5px 8px; border: 1px solid #d1d9e0; border-radius: 2px; background: #ffffff; color: #1f2328; }
QComboBox:hover { background: #f6f8fa; }
QComboBox::drop-down { border: none; width: 24px; }
QComboBox QAbstractItemView { background: #ffffff; color: #1f2328; border: 1px solid #d1d9e0; selection-background-color: #ddf4ff; selection-color: #1f2328; outline: 0; }
QListWidget { background: #ffffff; border: 1px solid #d8dee4; border-radius: 2px; outline: 0; color: #1f2328; }
QListWidget::item { border-radius: 2px; color: #1f2328; }
QListWidget::item:selected { background: #ddf4ff; color: #1f2328; }
QListWidget::item:hover { background: #f6f8fa; color: #1f2328; }
QListWidget::item:selected:hover { background: #ddf4ff; color: #1f2328; }
QPushButton { padding: 5px 10px; border: 1px solid #d1d9e0; border-radius: 2px; background: transparent; color: #1f2328; }
QPushButton:hover { background: #eef1f4; }
QPushButton:pressed { background: #d8dee4; }
QStatusBar { background: #ffffff; border-top: 1px solid #d8dee4; color: #59636e; }
QStatusBar::item { border: none; }
QSplitter::handle { background: #d8dee4; }
QCheckBox { spacing: 6px; }
QScrollBar:vertical { background: transparent; width: 10px; margin: 0; }
QScrollBar::handle:vertical { background: #d1d9e0; border-radius: 2px; min-height: 24px; }
QScrollBar::handle:vertical:hover { background: #8b949e; }
QScrollBar:horizontal { background: transparent; height: 10px; margin: 0; }
QScrollBar::handle:horizontal { background: #d1d9e0; border-radius: 2px; min-width: 24px; }
QScrollBar::add-line, QScrollBar::sub-line { width: 0; height: 0; }
QScrollBar::add-page, QScrollBar::sub-page { background: transparent; }
QLabel#noteTitleBar { font-size: 15px; font-weight: 600; padding: 2px 6px; }
QLineEdit#noteTitleEdit { font-size: 15px; font-weight: 600; padding: 2px 6px; border: 1px solid #0969da; border-radius: 2px; }
QToolButton#pencilButton { border: none; background: transparent; padding: 2px 6px; font-size: 16px; color: #59636e; }
QToolButton#pencilButton:hover { color: #0969da; background: #eef1f4; border-radius: 2px; }
QToolButton#pencilButton:disabled { color: #d1d9e0; }
QLabel#sidebarHeader { font-weight: 600; color: #59636e; padding-top: 6px; }
QLabel#noteTitle { font-weight: 600; color: #1f2328; }
QLabel#noteSubtitle { color: #59636e; font-size: 12px; }
QLabel#dialogTitle { font-size: 16px; font-weight: 600; color: #1f2328; }
QLabel#mutedLabel { color: #59636e; }
"""

DEBOUNCE_MS = 300


class _TitleEdit(QLineEdit):
    cancelled = Signal()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.cancelled.emit()
        else:
            super().keyPressEvent(event)


class NoteTitleBar(QWidget):
    """Tieu de note dang mo + nut but de doi ten truc tiep tren editor."""

    renamed = Signal(int, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._editing = False
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self.label = QLabel("No note open")
        self.label.setObjectName("noteTitleBar")
        self.label.setMinimumWidth(200)

        self.edit = _TitleEdit()
        self.edit.setObjectName("noteTitleEdit")
        self.edit.hide()

        self.pencil = QToolButton()
        self.pencil.setObjectName("pencilButton")
        self.pencil.setText("\u270e")
        self.pencil.setToolTip("Rename note (F2)")
        self.pencil.setCursor(Qt.CursorShape.PointingHandCursor)
        self.pencil.setEnabled(False)

        layout.addWidget(self.label)
        layout.addWidget(self.edit)
        layout.addWidget(self.pencil)

        self.pencil.clicked.connect(self.begin_edit)
        self.edit.returnPressed.connect(self._commit)
        self.edit.editingFinished.connect(self._commit)
        self.edit.cancelled.connect(self._cancel)

    @property
    def note_id(self):
        return self._note_id

    @note_id.setter
    def note_id(self, value):
        self._note_id = value
        self.pencil.setEnabled(value is not None)

    def title(self) -> str:
        return self.label.text()

    def setTitle(self, text: str):
        self.label.setText(text)

    def begin_edit(self):
        if self._note_id is None or self._editing:
            return
        self._editing = True
        self.label.hide()
        self.pencil.hide()
        self.edit.setText(self.label.text())
        self.edit.show()
        self.edit.setFocus(Qt.FocusReason.OtherFocusReason)
        self.edit.selectAll()

    def _commit(self):
        if not self._editing:
            return
        self._editing = False
        new = self.edit.text().strip()
        old = self.label.text()
        if new and new != old:
            self.renamed.emit(self._note_id, new)
            self.label.setText(new)
        self._end_edit()

    def _cancel(self):
        if not self._editing:
            return
        self._editing = False
        self._end_edit()

    def _end_edit(self):
        self.edit.hide()
        self.label.show()
        self.pencil.show()


class MainWindow(QMainWindow):
    """Cua so chinh, noi ket cac thanh phan va trien khai 13 UC."""

    def __init__(self):
        super().__init__()
        self.db = DbManager()
        self.db.connect()
        self.settings = SettingsDAO(self.db)
        self.notes = NoteDAO(self.db)
        self.tags = TagDAO(self.db)
        self.theme_manager = ThemeManager(self.settings)
        self.theme_manager.ensureDefaults()

        self.renderer = MarkdownRenderer()
        self.sync_controller = SyncScrollController(self.settings)
        self.exporter = Exporter()

        self._current_id = None
        self._loaded_text = ""
        self._dirty = False
        self._loading_note = False
        self._note_tags = []

        self.setWindowTitle(APP_NAME + " - Offline Markdown Notes")
        self.resize(1200, 780)

        self._render_timer = QTimer(self)
        self._render_timer.setSingleShot(True)
        self._render_timer.setInterval(DEBOUNCE_MS)
        self._render_timer.timeout.connect(self._on_render_timeout)

        self._build_actions()
        self._build_ui()
        self._connect_signals()
        self._apply_theme_check()

        self._refresh_sidebar()
        self._open_last_note()

    # ------------------------------------------------------------------ UI
    def _build_actions(self):
        act = QAction
        self.act_new = act("New", self)
        self.act_new.setShortcut(QKeySequence.StandardKey.New)
        self.act_save = act("Save", self)
        self.act_save.setShortcut(QKeySequence.StandardKey.Save)
        self.act_rename = act("Rename...", self)
        self.act_rename.setShortcut(QKeySequence("F2"))
        self.act_delete = act("Delete", self)
        self.act_delete.setShortcut(QKeySequence("Ctrl+D"))
        self.act_export_html = act("Export HTML", self)
        self.act_export_pdf = act("Export PDF", self)
        self.act_export_md = act("Export Markdown", self)
        self.act_quit = act("Quit", self)
        self.act_quit.setShortcut(QKeySequence("Ctrl+Q"))
        self.act_find = act("Find", self)
        self.act_find.setShortcut(QKeySequence.StandardKey.Find)
        self.act_replace = act("Replace", self)
        self.act_replace.setShortcut(QKeySequence("Ctrl+H"))
        self.act_sync = act("Sync Scroll", self)
        self.act_sync.setShortcut(QKeySequence("Ctrl+Shift+S"))
        self.act_sync.setCheckable(True)
        self.act_sync.setChecked(self.sync_controller.isEnabled())
        self.act_settings = act("Appearance...", self)
        self.act_about = act("About", self)

    def _build_ui(self):
        menubar = self.menuBar()

        menu_file = menubar.addMenu("&File")
        menu_file.addAction(self.act_new)
        menu_file.addAction(self.act_save)
        menu_file.addAction(self.act_rename)
        menu_file.addAction(self.act_delete)
        menu_file.addSeparator()
        menu_file.addAction(self.act_export_html)
        menu_file.addAction(self.act_export_pdf)
        menu_file.addAction(self.act_export_md)
        menu_file.addSeparator()
        menu_file.addAction(self.act_quit)

        menu_edit = menubar.addMenu("&Edit")
        menu_edit.addAction(self.act_find)
        menu_edit.addAction(self.act_replace)

        menu_view = menubar.addMenu("&View")
        menu_view.addAction(self.act_sync)

        menu_settings = menubar.addMenu("&Settings")
        menu_settings.addAction(self.act_settings)

        menu_help = menubar.addMenu("&Help")
        menu_help.addAction(self.act_about)

        toolbar = QToolBar("Toolbar", self)
        toolbar.setMovable(False)
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        toolbar.addAction(self.act_new)
        toolbar.addAction(self.act_save)
        toolbar.addAction(self.act_delete)
        toolbar.addSeparator()
        toolbar.addAction(self.act_find)
        toolbar.addAction(self.act_replace)
        toolbar.addSeparator()
        toolbar.addAction(self.act_sync)
        toolbar.addSeparator()
        toolbar.addAction(self.act_settings)
        self.addToolBar(toolbar)

        self.panel = SearchPanel(self)

        self.editor = EditorPane(self)
        self.title_label = NoteTitleBar(self)
        self.tag_button = QPushButton("Tags", self)
        self.tag_menu = QMenu(self)
        self.tag_button.setMenu(self.tag_menu)
        header = QWidget(self)
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 4)
        header_layout.setSpacing(4)
        header_row = QVBoxLayout()
        header_row.setContentsMargins(4, 4, 4, 0)
        header_row.addWidget(self.title_label)
        header_row.addWidget(self.tag_button, 0, Qt.AlignmentFlag.AlignLeft)
        header_layout.addLayout(header_row)
        header_layout.addWidget(self.editor)

        self.preview = PreviewPane(self.renderer, self.theme_manager, self)

        right_splitter = QSplitter(Qt.Orientation.Horizontal, self)
        right_splitter.addWidget(header)
        right_splitter.addWidget(self.preview)
        right_splitter.setStretchFactor(0, 1)
        right_splitter.setStretchFactor(1, 1)
        right_splitter.setSizes([520, 560])

        main_splitter = QSplitter(Qt.Orientation.Horizontal, self)
        main_splitter.addWidget(self.panel)
        main_splitter.addWidget(right_splitter)
        main_splitter.setStretchFactor(0, 0)
        main_splitter.setStretchFactor(1, 1)
        main_splitter.setSizes([280, 900])
        self.setCentralWidget(main_splitter)

        self.statusBar().showMessage("Ready")

    def _connect_signals(self):
        self.act_new.triggered.connect(self.onNewNote)
        self.act_save.triggered.connect(self.save)
        self.act_rename.triggered.connect(self.onRename)
        self.act_delete.triggered.connect(self.onDelete)
        self.act_export_html.triggered.connect(self.onExportHtml)
        self.act_export_pdf.triggered.connect(self.onExportPdf)
        self.act_export_md.triggered.connect(self.onExportMd)
        self.act_quit.triggered.connect(self.close)
        self.act_find.triggered.connect(self.onFind)
        self.act_replace.triggered.connect(self.onReplace)
        self.act_sync.toggled.connect(self._on_sync_toggled)
        self.act_settings.triggered.connect(self.onOpenSettings)
        self.act_about.triggered.connect(self.onAbout)

        self.panel.filtersChanged.connect(self._refresh_sidebar)
        self.panel.noteSelected.connect(self.openNote)
        self.editor.textChanged.connect(self._on_text_changed)
        self.editor.verticalScrollBar().valueChanged.connect(self._on_editor_scroll)
        self.title_label.renamed.connect(self._on_rename)

    def _apply_theme_check(self):
        """Check theme at startup: missing file shows a warning and resets to default."""
        if self.theme_manager.current() not in self.theme_manager.listThemes():
            QMessageBox.warning(
                self,
                "Theme file missing",
                "The selected theme file no longer exists.\n"
                "The application will switch back to the default theme.",
            )
            self.theme_manager.resetToDefault()
            self.settings.set(KEY_THEME, DEFAULT_THEME)

    # ---------------------------------------------------------------- UC
    def _confirm_proceed(self) -> bool:
        """Ask to save when the current note has unsaved changes."""
        if not self._dirty or self._current_id is None:
            return True
        answer = QMessageBox.question(
            self,
            "Unsaved changes",
            "The current note has unsaved changes.",
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Save,
        )
        if answer == QMessageBox.StandardButton.Cancel:
            return False
        if answer == QMessageBox.StandardButton.Save:
            self.save()
        return True

    def onNewNote(self):
        """UC01 - Tao note moi: nhap tieu de, ghi vao database."""
        if not self._confirm_proceed():
            return
        title, ok = QInputDialog.getText(self, "New note", "Title:")
        if not ok:
            return
        title = title.strip() or "Untitled"
        note_id = self.notes.insert(title, "")
        self.settings.set(KEY_LAST_OPENED, str(note_id))
        self.openNote(note_id)
        self.statusBar().showMessage("Note created")
        self.editor.setFocus()

    def openNote(self, note_id: int):
        """UC02 - Mo va xem note: do noi dung vao editor va preview."""
        if note_id == self._current_id:
            self.panel.setActiveNote(note_id)
            return
        if not self._confirm_proceed():
            return
        note = self.notes.getById(note_id)
        if note is None:
            return
        self._current_id = note_id
        self._loaded_text = note["content_md"] or ""
        self._dirty = False
        self._loading_note = True
        self.editor.setText(self._loaded_text)
        self._loading_note = False
        self.title_label.note_id = note_id
        self.title_label.setTitle(note["title"])
        self.preview.render(self._loaded_text)
        self.panel.setActiveNote(note_id)
        self._refresh_note_tags()
        self.settings.set(KEY_LAST_OPENED, str(note_id))
        self.statusBar().showMessage("Opened: %s" % note["title"])

    def save(self):
        """UC03 - Save the content of the current note into the database."""
        if self._current_id is None:
            self.statusBar().showMessage("No note open")
            return
        text = self.editor.getText()
        if text == self._loaded_text:
            self.statusBar().showMessage("No changes")
            return
        try:
            self.notes.update(self._current_id, text)
        except sqlite3.OperationalError:
            self._dirty = True
            self.statusBar().showMessage("Database is locked, try again")
            return
        self._loaded_text = text
        self._dirty = False
        self.preview.render(text)
        self._refresh_sidebar()
        self.statusBar().showMessage("Note saved")

    def onRename(self):
        """Rename the current note right in the title bar (F2 / pencil)."""
        self.title_label.begin_edit()

    def _on_rename(self, note_id: int, title: str):
        self.notes.rename(note_id, title)
        self._refresh_sidebar()
        self.statusBar().showMessage("Note renamed")

    def onDelete(self):
        """UC04 - Delete the current note after confirmation."""
        if self._current_id is None:
            self.statusBar().showMessage("No note open")
            return
        title = self.title_label.title()
        answer = QMessageBox.question(
            self,
            "Confirm delete",
            "Delete note \"%s\"?\nThis action cannot be undone." % title,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        self.notes.delete(self._current_id)
        self._current_id = None
        self._loaded_text = ""
        self._dirty = False
        self._loading_note = True
        self.editor.setText("")
        self._loading_note = False
        self.preview.render("")
        self.title_label.note_id = None
        self.title_label.setTitle("No note open")
        self.settings.set(KEY_LAST_OPENED, "0")
        self._refresh_sidebar()
        self.statusBar().showMessage("Note deleted")

    def _refresh_note_tags(self):
        self._note_tags = self.tags.getByNote(self._current_id or 0)
        self._populate_tag_menu()
        names = [row["name"] for row in self._note_tags]
        label = ", ".join(names)
        if len(label) > 42:
            label = label[:41] + "..."
        self.tag_button.setText(label or "Tags")
        self.tag_button.setToolTip(", ".join(names) or "Tags")

    def _populate_tag_menu(self):
        self.tag_menu.clear()
        if self._current_id is None:
            return
        all_tags = self.tags.listAll()
        assigned = {row["id"] for row in self._note_tags}
        for tag in all_tags:
            action = self.tag_menu.addAction(tag["name"])
            action.setCheckable(True)
            action.setChecked(tag["id"] in assigned)
            action.toggled.connect(
                lambda checked, tag_id=tag["id"]: self._on_tag_toggled(tag_id, checked)
            )
        self.tag_menu.addSeparator()
        new_action = self.tag_menu.addAction("New tag...")
        new_action.triggered.connect(self._on_new_tag)

    def _on_tag_toggled(self, tag_id: int, checked: bool):
        """UC05 - Gan hoac go tag cho note hien tai."""
        if self._current_id is None:
            return
        if checked:
            self.tags.assign(self._current_id, tag_id)
        else:
            self.tags.unassign(self._current_id, tag_id)
        self._refresh_note_tags()
        self._refresh_sidebar()
        if self._current_id is not None:
            self.panel.selectNoteById(self._current_id)

    def _on_new_tag(self):
        name, ok = QInputDialog.getText(self, "New tag", "Tag name:")
        if not ok or not name.strip():
            return
        tag_id = self.tags.create(name.strip())
        if self._current_id is not None:
            self.tags.assign(self._current_id, tag_id)
        self._refresh_note_tags()
        self._refresh_sidebar()

    def onFind(self):
        """UC08 - Mo hop thoai tim kiem trong note hien tai."""
        dialog = FindReplaceDialog(self.editor, replace_mode=False, parent=self)
        dialog.show()
        dialog.raise_()
        dialog.activateWindow()

    def onReplace(self):
        """UC09 - Mo hop thoai tim va thay the trong note hien tai."""
        dialog = FindReplaceDialog(self.editor, replace_mode=True, parent=self)
        dialog.contentReplaced.connect(self._on_replaced)
        dialog.show()
        dialog.raise_()
        dialog.activateWindow()

    def _on_replaced(self):
        """Sau khi thay the: cap nhat database va render lai preview."""
        self.save()
        self.preview.render(self.editor.getText())

    def _refresh_sidebar(self):
        self.panel.refresh_filters_from_query()
        keyword = self.panel.keyword()
        tag_name = self.panel.tagName()
        if keyword:
            rows = self.notes.searchFTS(keyword, tag_name)
        else:
            rows = self.notes.list(tag_name)
        self.panel.setTags([row["name"] for row in self.tags.listAll()], tag_name)
        self.panel.setNotes(rows, searched=bool(keyword))
        if self._current_id is not None:
            self.panel.selectNoteById(self._current_id)

    def _open_last_note(self):
        try:
            last_id = int(self.settings.get(KEY_LAST_OPENED, "0"))
        except ValueError:
            last_id = 0
        if last_id and self.notes.getById(last_id) is not None:
            self.openNote(last_id)
        else:
            self._populate_tag_menu()
            self.statusBar().showMessage("No notes yet. Press New to create one.")

    def onOpenSettings(self):
        """UC11/UC12 - Mo cai dat giao dien, chon theme CSS."""
        dialog = SettingsDialog(self.theme_manager, self.settings, parent=self)
        dialog.themeSelected.connect(self._on_theme_changed)
        dialog.exec()

    def _on_theme_changed(self, name: str):
        """UC12 - Apply theme: re-render the preview, no restart needed."""
        self.preview.reloadCss()
        self.statusBar().showMessage("Theme changed to %s" % name)

    def _on_sync_toggled(self, checked: bool):
        """UC07 - Toggle editor/preview scroll sync and store the setting."""
        self.sync_controller.setEnabled(checked)
        state = "Enabled" if checked else "Disabled"
        self.statusBar().showMessage("%s sync scroll between editor and preview" % state)

    def onExportMd(self):
        """Export the current note as a plain .md file."""
        if self._current_id is None:
            self.statusBar().showMessage("No note open")
            return
        default_name = self.title_label.title() + ".md"
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Markdown", default_name, "Markdown (*.md)"
        )
        if not path:
            return
        Path(path).write_text(self.editor.getText() or "", encoding="utf-8")
        self.statusBar().showMessage("Exported Markdown: %s" % path)

    def onExportHtml(self):
        """UC13 - Export HTML with the current theme CSS, single file."""
        if self._current_id is None:
            self.statusBar().showMessage("No note open")
            return
        default_name = self.title_label.title() + ".html"
        path, _ = QFileDialog.getSaveFileName(
            self, "Export HTML", default_name, "HTML (*.html)"
        )
        if not path:
            return
        html_body = self.renderer.render(self.editor.getText())
        css = self.theme_manager.getCss(self.theme_manager.current()) or ""
        self.exporter.toHtml(html_body, css, path)
        self.statusBar().showMessage("Exported HTML: %s" % path)

    def onExportPdf(self):
        """UC13 - Export PDF (A4), using the same theme as HTML export."""
        if self._current_id is None:
            self.statusBar().showMessage("No note open")
            return
        default_name = self.title_label.title() + ".pdf"
        path, _ = QFileDialog.getSaveFileName(
            self, "Export PDF", default_name, "PDF (*.pdf)"
        )
        if not path:
            return
        html_body = self.renderer.render(self.editor.getText())
        css = self.theme_manager.getCss(self.theme_manager.current()) or ""
        try:
            self.exporter.toPdf(html_body, css, path)
        except RuntimeError as exc:
            if str(exc) == "weasyprint-missing":
                QMessageBox.warning(
                    self,
                    "Missing library",
                    "WeasyPrint is required to export PDF.\n"
                    "pip install weasyprint",
                )
            elif str(exc) == "weasyprint-libs":
                QMessageBox.warning(
                    self,
                    "Missing Pango libraries",
                    "WeasyPrint could not load the Pango text-rendering "
                    "library.\n\n"
                    "Linux: install the pango library of your distro "
                    "(e.g. libpango-1.0-0 via apt, pango via dnf/pacman).\n\n"
                    "Windows: install Pango through MSYS2 "
                    "(pacman -S mingw-w64-ucrt-x86_64-pango) or use the "
                    "standalone WeasyPrint build.",
                )
            else:
                QMessageBox.warning(self, "PDF export error", "Error while creating the PDF file.")
            return
        self.statusBar().showMessage("Exported PDF: %s" % path)

    def onAbout(self):
        QMessageBox.about(
            self,
            "About",
            APP_NAME + "\n"
            "Offline Markdown note-taking for Linux.\n"
            "Select a CSS theme, live preview, FTS5 full-text search,\n"
            "HTML and PDF export. Runs 100% offline.",
        )

    # ---------------------------------------------------------- editor
    def _on_text_changed(self):
        if self._loading_note:
            return
        self._dirty = self.editor.getText() != self._loaded_text
        self._render_timer.start()

    def _on_render_timeout(self):
        if self._current_id is not None:
            self.preview.render(self.editor.getText())

    def _on_editor_scroll(self, value: int):
        if self._loading_note or self._current_id is None:
            return
        scrollbar = self.editor.verticalScrollBar()
        maximum = scrollbar.maximum()
        percent = value / maximum if maximum > 0 else 0.0
        percent = self.sync_controller.onScroll(percent)
        if percent is not None:
            self.preview.setScroll(percent)

    # ------------------------------------------------------------- quit
    def closeEvent(self, event):
        if not self._confirm_proceed():
            event.ignore()
            return
        self.db.close()
        event.accept()


def main() -> int:
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationName(APP_NAME)
    app.setPalette(_light_palette())
    app.setStyleSheet(APP_STYLE)
    window = MainWindow()
    window.show()
    return app.exec()


def _light_palette():
    from PySide6.QtGui import QColor, QPalette

    pal = QPalette()
    fg = QColor("#1f2328")
    bg = QColor("#f6f8fa")
    base = QColor("#ffffff")
    pal.setColor(QPalette.ColorRole.Window, bg)
    pal.setColor(QPalette.ColorRole.WindowText, fg)
    pal.setColor(QPalette.ColorRole.Base, base)
    pal.setColor(QPalette.ColorRole.AlternateBase, bg)
    pal.setColor(QPalette.ColorRole.Text, fg)
    pal.setColor(QPalette.ColorRole.Button, bg)
    pal.setColor(QPalette.ColorRole.ButtonText, fg)
    pal.setColor(QPalette.ColorRole.Highlight, QColor("#ddf4ff"))
    pal.setColor(QPalette.ColorRole.HighlightedText, fg)
    pal.setColor(QPalette.ColorRole.ToolTipBase, base)
    pal.setColor(QPalette.ColorRole.ToolTipText, fg)
    pal.setColor(QPalette.ColorRole.PlaceholderText, QColor("#59636e"))
    pal.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor("#8b949e"))
    pal.setColor(
        QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor("#8b949e")
    )
    pal.setColor(
        QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor("#8b949e")
    )
    return pal


if __name__ == "__main__":
    sys.exit(main())