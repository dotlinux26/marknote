"""Cua so chinh cua MarkNote - ghi chu Markdown offline."""

from __future__ import annotations

import sqlite3
import sys

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QInputDialog,
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QSplitter,
    QToolBar,
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
QMenu { background: #ffffff; border: 1px solid #d1d9e0; border-radius: 2px; padding: 4px; }
QMenu::item { padding: 6px 20px; border-radius: 2px; }
QMenu::item:selected { color: #1f2328; background: #eef1f4; }
QMenu::separator { height: 1px; background: #d8dee4; margin: 4px 8px; }
QToolBar { background: #f6f8fa; border: none; border-bottom: 1px solid #d8dee4; spacing: 4px; padding: 4px 6px; }
QToolButton { padding: 5px 10px; border: 1px solid #d1d9e0; border-radius: 2px; background: transparent; }
QToolButton:hover { background: #eef1f4; }
QToolButton:pressed { background: #d8dee4; }
QToolButton:checked { background: #ddf4ff; border-color: #54aeff; color: #0969da; }
QLineEdit { padding: 6px 8px; border: 1px solid #d1d9e0; border-radius: 2px; background: #ffffff; }
QLineEdit:focus { border-color: #0969da; }
QPlainTextEdit { background: #ffffff; border: 1px solid #d8dee4; border-radius: 2px; padding: 6px; selection-background-color: #add6ff; }
QListWidget { background: #ffffff; border: 1px solid #d8dee4; border-radius: 2px; outline: 0; }
QListWidget::item { border-radius: 2px; }
QListWidget::item:selected { background: #ddf4ff; }
QListWidget::item:hover { background: #f6f8fa; }
QPushButton { padding: 5px 10px; border: 1px solid #d1d9e0; border-radius: 2px; background: transparent; }
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
QLabel#sidebarHeader { font-weight: 600; color: #59636e; padding-top: 6px; }
QLabel#noteTitle { font-weight: 600; color: #1f2328; }
QLabel#noteSubtitle { color: #59636e; font-size: 12px; }
QLabel#dialogTitle { font-size: 16px; font-weight: 600; color: #1f2328; }
QLabel#mutedLabel { color: #59636e; }
"""

DEBOUNCE_MS = 300


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

        self.setWindowTitle(APP_NAME + " - Ghi chu Markdown offline")
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
        self.act_new = act("Moi", self)
        self.act_new.setShortcut(QKeySequence.StandardKey.New)
        self.act_save = act("Luu", self)
        self.act_save.setShortcut(QKeySequence.StandardKey.Save)
        self.act_delete = act("Xoa", self)
        self.act_delete.setShortcut(QKeySequence("Ctrl+D"))
        self.act_export_html = act("Xuat HTML", self)
        self.act_export_pdf = act("Xuat PDF", self)
        self.act_quit = act("Thoat", self)
        self.act_quit.setShortcut(QKeySequence("Ctrl+Q"))
        self.act_find = act("Tim kiem", self)
        self.act_find.setShortcut(QKeySequence.StandardKey.Find)
        self.act_replace = act("Thay the", self)
        self.act_replace.setShortcut(QKeySequence("Ctrl+H"))
        self.act_sync = act("Dong bo cuon", self)
        self.act_sync.setShortcut(QKeySequence("Ctrl+Shift+S"))
        self.act_sync.setCheckable(True)
        self.act_sync.setChecked(self.sync_controller.isEnabled())
        self.act_settings = act("Giao dien...", self)
        self.act_about = act("Gioi thieu", self)

    def _build_ui(self):
        menubar = self.menuBar()

        menu_file = menubar.addMenu("&File")
        menu_file.addAction(self.act_new)
        menu_file.addAction(self.act_save)
        menu_file.addAction(self.act_delete)
        menu_file.addSeparator()
        menu_file.addAction(self.act_export_html)
        menu_file.addAction(self.act_export_pdf)
        menu_file.addSeparator()
        menu_file.addAction(self.act_quit)

        menu_edit = menubar.addMenu("&Sua")
        menu_edit.addAction(self.act_find)
        menu_edit.addAction(self.act_replace)

        menu_view = menubar.addMenu("&Xem")
        menu_view.addAction(self.act_sync)

        menu_settings = menubar.addMenu("&Cai dat")
        menu_settings.addAction(self.act_settings)

        menu_help = menubar.addMenu("&Tro giup")
        menu_help.addAction(self.act_about)

        toolbar = QToolBar("Thanh cong cu", self)
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
        self.title_label = QLabel("Chua mo note nao", self)
        self.title_label.setObjectName("noteTitleBar")
        self.title_label.setMinimumWidth(200)
        self.tag_button = QPushButton("The", self)
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

        self.statusBar().showMessage("San sang")

    def _connect_signals(self):
        self.act_new.triggered.connect(self.onNewNote)
        self.act_save.triggered.connect(self.save)
        self.act_delete.triggered.connect(self.onDelete)
        self.act_export_html.triggered.connect(self.onExportHtml)
        self.act_export_pdf.triggered.connect(self.onExportPdf)
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

    def _apply_theme_check(self):
        """Kiem tra theme o dau: file mat thi thong bao va reset ve default."""
        if self.theme_manager.current() not in self.theme_manager.listThemes():
            QMessageBox.warning(
                self,
                "Theme file missing",
                "File theme dang chon khong con ton tai.\n"
                "Ung dung se ve lai theme default.",
            )
            self.theme_manager.resetToDefault()
            self.settings.set(KEY_THEME, DEFAULT_THEME)

    # ---------------------------------------------------------------- UC
    def _confirm_proceed(self) -> bool:
        """Hoi luu khi note dang co thay doi chua luu."""
        if not self._dirty or self._current_id is None:
            return True
        answer = QMessageBox.question(
            self,
            "Chua luu",
            "Note hien tai co thay doi chua duoc luu.",
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
        title, ok = QInputDialog.getText(self, "Tao note moi", "Tieu de:")
        if not ok:
            return
        title = title.strip() or "Chua co tieu de"
        note_id = self.notes.insert(title, "")
        self.settings.set(KEY_LAST_OPENED, str(note_id))
        self.openNote(note_id)
        self.statusBar().showMessage("Da tao note moi")
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
        self.title_label.setText(note["title"])
        self.preview.render(self._loaded_text)
        self.panel.setActiveNote(note_id)
        self._refresh_note_tags()
        self.settings.set(KEY_LAST_OPENED, str(note_id))
        self.statusBar().showMessage("Da mo: %s" % note["title"])

    def save(self):
        """UC03 - Luu noi dung note hien tai vao database."""
        if self._current_id is None:
            self.statusBar().showMessage("Chua mo note nao")
            return
        text = self.editor.getText()
        if text == self._loaded_text:
            self.statusBar().showMessage("Khong co thay doi")
            return
        try:
            self.notes.update(self._current_id, text)
        except sqlite3.OperationalError:
            self._dirty = True
            self.statusBar().showMessage("Database is locked, thu lai")
            return
        self._loaded_text = text
        self._dirty = False
        self.preview.render(text)
        self._refresh_sidebar()
        self.statusBar().showMessage("Da luu note")

    def onDelete(self):
        """UC04 - Xoa note hien tai sau khi xac nhan."""
        if self._current_id is None:
            self.statusBar().showMessage("Chua mo note nao")
            return
        title = self.title_label.text()
        answer = QMessageBox.question(
            self,
            "Xac nhan xoa",
            "Xoa note \"%s\"?\nThao tac nay khong the hoan tac." % title,
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
        self.title_label.setText("Chua mo note nao")
        self.settings.set(KEY_LAST_OPENED, "0")
        self._refresh_sidebar()
        self.statusBar().showMessage("Da xoa note")

    def _refresh_note_tags(self):
        self._note_tags = self.tags.getByNote(self._current_id or 0)
        self._populate_tag_menu()

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
        new_action = self.tag_menu.addAction("The moi...")
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
        name, ok = QInputDialog.getText(self, "The moi", "Ten the:")
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
            self.statusBar().showMessage("Chua co note. Nhan Moi de tao note moi.")

    def onOpenSettings(self):
        """UC11/UC12 - Mo cai dat giao dien, chon theme CSS."""
        dialog = SettingsDialog(self.theme_manager, self.settings, parent=self)
        dialog.themeSelected.connect(self._on_theme_changed)
        dialog.exec()

    def _on_theme_changed(self, name: str):
        """UC12 - Sua theme: render lai preview bang CSS moi, khong restart."""
        self.preview.reloadCss()
        self.statusBar().showMessage("Da doi theme sang %s" % name)

    def _on_sync_toggled(self, checked: bool):
        """UC07 - Bat/tat dong bo cuon va luu vao settings."""
        self.sync_controller.setEnabled(checked)
        msg = "Da bat" if checked else "Da tat"
        self.statusBar().showMessage("%s dong bo cuon editor va preview" % msg)

    def onExportHtml(self):
        """UC13 - Xuat HTML voi CSS theme dang chon, dung mot file."""
        if self._current_id is None:
            self.statusBar().showMessage("Chua mo note nao")
            return
        default_name = self.title_label.text() + ".html"
        path, _ = QFileDialog.getSaveFileName(
            self, "Xuat HTML", default_name, "HTML (*.html)"
        )
        if not path:
            return
        html_body = self.renderer.render(self.editor.getText())
        css = self.theme_manager.getCss(self.theme_manager.current()) or ""
        self.exporter.toHtml(html_body, css, path)
        self.statusBar().showMessage("Da xuat HTML: %s" % path)

    def onExportPdf(self):
        """UC13 - Xuat PDF kho A4, dung chung theme voi xuat HTML."""
        if self._current_id is None:
            self.statusBar().showMessage("Chua mo note nao")
            return
        default_name = self.title_label.text() + ".pdf"
        path, _ = QFileDialog.getSaveFileName(
            self, "Xuat PDF", default_name, "PDF (*.pdf)"
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
                    "Thieu thu vien",
                    "Can cai WeasyPrint de xuat PDF.\n"
                    "pip install weasyprint",
                )
            else:
                QMessageBox.warning(self, "Loi xuat PDF", "Loi khi tao file PDF.")
            return
        self.statusBar().showMessage("Da xuat PDF: %s" % path)

    def onAbout(self):
        QMessageBox.about(
            self,
            "Gioi thieu",
            APP_NAME + "\n"
            "Phan mem ghi chu Markdown offline cho Linux.\n"
            "Chon theme CSS, xem truoc song song, tim kiem FTS5,\n"
            "xuat HTML va PDF. Chay offline 100%.",
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
    app.setStyleSheet(APP_STYLE)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())