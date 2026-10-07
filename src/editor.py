"""O soan thao Markdown, hop thoai tim/thay the va bang dieu huong."""

from __future__ import annotations

import re

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFontDatabase, QTextCharFormat, QTextCursor
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPlainTextEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

COLOR_MATCH = "#fff8c5"
COLOR_CURRENT = "#f8b886"


class EditorPane(QPlainTextEdit):
    """O soan thao ben trai, ho tro tim highlight nhieu vi tri."""

    def __init__(self, parent=None):
        super().__init__(parent)
        font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        font.setPointSize(12)
        self.setFont(font)
        self.setPlaceholderText("Chua mo note nao. Nhan Moi de tao note moi.")
        self.setTabStopDistance(4 * self.fontMetrics().horizontalAdvance(" "))
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        self._find_dialog = None
        self._matches = []
        self._index = -1
        self._case_sensitive = False

    def setText(self, md: str):
        self.setPlainText(md or "")
        self.clearFind()

    def getText(self) -> str:
        return self.toPlainText()

    def clearFind(self):
        self._matches = []
        self._index = -1
        self.setExtraSelections([])

    def find(self, keyword: str, case_sensitive: bool = False) -> int:
        """Tim toan bo va highlight; tra ve so luong ket qua (UC08)."""
        text = self.toPlainText()
        self._case_sensitive = case_sensitive
        flags = 0 if case_sensitive else re.IGNORECASE
        self._matches = [
            (m.start(), m.end() - m.start())
            for m in re.finditer(re.escape(keyword), text, flags)
        ]
        self._index = -1
        self._paint_highlights()
        return len(self._matches)

    def findNext(self, backward: bool = False) -> tuple:
        """Chuyen den ket qua ke tiep/truoc, tra ve (index, tong)."""
        total = len(self._matches)
        if not total or not self._matches:
            return (-1, 0)
        self._index = (self._index - 1) % total if backward else (self._index + 1) % total
        start, length = self._matches[self._index]
        cursor = QTextCursor(self.document())
        cursor.setPosition(start)
        cursor.setPosition(start + length, QTextCursor.MoveMode.KeepAnchor)
        self.setTextCursor(cursor)
        self.ensureCursorVisible()
        self._paint_highlights()
        return (self._index, total)

    def replace(self, find_text: str, replace_text: str) -> bool:
        """Thay the ket qua dang chon (UC09). Tra False neu khong co ket qua."""
        if self._index < 0 or not self._matches:
            return False
        start, length = self._matches[self._index]
        cursor = QTextCursor(self.document())
        cursor.setPosition(start)
        cursor.setPosition(start + length, QTextCursor.MoveMode.KeepAnchor)
        cursor.beginEditBlock()
        cursor.insertText(replace_text)
        cursor.endEditBlock()
        self.find(find_text, self._case_sensitive)
        return True

    def replaceAll(self, find_text: str, replace_text: str, case_sensitive: bool) -> int:
        """Thay tat ca ket qua, them nguoc tu cuoi len dau. Tra ve so luong."""
        total = self.find(find_text, case_sensitive)
        if not total:
            return 0
        cursor = QTextCursor(self.document())
        cursor.beginEditBlock()
        for start, length in reversed(self._matches):
            c = QTextCursor(self.document())
            c.setPosition(start)
            c.setPosition(start + length, QTextCursor.MoveMode.KeepAnchor)
            c.insertText(replace_text)
        cursor.endEditBlock()
        self.find(find_text, case_sensitive)
        return total

    def findStatus(self) -> str:
        if self._index < 0 or not self._matches:
            return "0/0"
        return "%d/%d" % (self._index + 1, len(self._matches))

    def _paint_highlights(self):
        selections = []
        match_format = QTextCharFormat()
        match_format.setBackground(QColor(COLOR_MATCH))
        current_format = QTextCharFormat()
        current_format.setBackground(QColor(COLOR_CURRENT))
        for index, (start, length) in enumerate(self._matches):
            selection = QTextEdit.ExtraSelection()
            selection.format = current_format if index == self._index else match_format
            cursor = QTextCursor(self.document())
            cursor.setPosition(start)
            cursor.setPosition(start + length, QTextCursor.MoveMode.KeepAnchor)
            selection.cursor = cursor
            selections.append(selection)
        self.setExtraSelections(selections)

    def keyPressEvent(self, event):
        if self._find_dialog is not None and self._find_dialog.isVisible():
            if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                backward = bool(event.modifiers() & Qt.KeyboardModifier.ShiftModifier)
                self._find_dialog.findNext(backward=backward)
                return
            if event.key() == Qt.Key.Key_Escape:
                self._find_dialog.close()
                return
        super().keyPressEvent(event)


class FindReplaceDialog(QDialog):
    """Tim trong note hien tai (UC08) va thay the (UC09)."""

    contentReplaced = Signal()

    def __init__(self, editor: EditorPane, replace_mode: bool = False, parent=None):
        super().__init__(parent)
        self._editor = editor
        editor._find_dialog = self
        self._last_keyword = None
        self._last_case = None

        self.setWindowTitle("Tim kiem va thay the")
        self.setMinimumWidth(430)

        find_label = QLabel("Tim:")
        self._find_edit = QLineEdit()
        self._find_edit.setPlaceholderText("Nhap tu can tim")
        self._case_box = QCheckBox("Phan biet hoa thuong")
        self._status = QLabel("0/0")
        self._status.setObjectName("mutedLabel")

        replace_label = QLabel("Thay bang:")
        self._replace_edit = QLineEdit()
        self._replace_edit.setPlaceholderText("Nhap noi dung thay the")
        self._replace_row = QWidget()
        replace_row = QHBoxLayout(self._replace_row)
        replace_row.setContentsMargins(0, 0, 0, 0)
        replace_row.addWidget(replace_label)
        replace_row.addWidget(self._replace_edit)
        self._replace_row.setVisible(replace_mode)

        btn_next = QPushButton("Tim tiep")
        btn_prev = QPushButton("Tim truoc")
        btn_prev.setToolTip("Shift + Enter")
        btn_replace = QPushButton("Thay the")
        btn_replace_all = QPushButton("Thay tat ca")
        btn_close = QPushButton("Dong")
        btn_replace.setVisible(replace_mode)
        btn_replace_all.setVisible(replace_mode)

        row1 = QHBoxLayout()
        row1.addWidget(find_label)
        row1.addWidget(self._find_edit, 1)
        row1.addWidget(self._case_box)
        row1.addWidget(self._status)

        actions = QHBoxLayout()
        actions.addWidget(btn_next)
        actions.addWidget(btn_prev)
        actions.addStretch(1)
        actions.addWidget(btn_replace)
        actions.addWidget(btn_replace_all)
        actions.addWidget(btn_close)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)
        layout.addLayout(row1)
        layout.addWidget(self._replace_row)
        layout.addLayout(actions)

        self._find_edit.returnPressed.connect(lambda: self.findNext())
        btn_next.clicked.connect(lambda: self.findNext())
        btn_prev.clicked.connect(lambda: self.findNext(backward=True))
        btn_replace.clicked.connect(self.replaceOne)
        btn_replace_all.clicked.connect(self.replaceAll)
        btn_close.clicked.connect(self.closeEventProxy)
        self.finished.connect(self._on_closed)

    def closeEventProxy(self):
        self.close()

    def _on_closed(self, _result):
        self._editor.clearFind()
        if self._editor._find_dialog is self:
            self._editor._find_dialog = None

    def _keyword(self) -> str:
        return self._find_edit.text()

    def _prepare_find(self) -> bool:
        keyword = self._keyword()
        case = self._case_box.isChecked()
        if not keyword:
            self._status.setText("Nhap tu can tim")
            return False
        count = self._editor.find(keyword, case)
        self._status.setText("%d/%d" % (0 if not count else 1, count))
        self._last_keyword = keyword
        self._last_case = case
        return count > 0

    def findNext(self, backward: bool = False):
        keyword = self._keyword()
        case = self._case_box.isChecked()
        if keyword != self._last_keyword or case != self._last_case:
            if not self._prepare_find():
                return
        index, total = self._editor.findNext(backward=backward)
        if total:
            self._status.setText("%d/%d" % (index + 1, total))

    def replaceOne(self):
        keyword = self._keyword()
        replace_text = self._replace_edit.text()
        if not self._prepare_find():
            return
        self._editor.findNext(backward=False)
        if self._editor.replace(keyword, replace_text):
            self.contentReplaced.emit()
            self._status.setText(self._editor.findStatus())

    def replaceAll(self):
        keyword = self._keyword()
        replace_text = self._replace_edit.text()
        case = self._case_box.isChecked()
        count = self._editor.replaceAll(keyword, replace_text, case)
        self._status.setText("%d/0" % 0)
        if count:
            self.contentReplaced.emit()
            from PySide6.QtWidgets import QMessageBox

            QMessageBox.information(self, "Thay the", "Da thay %d vi tri." % count)


class NoteListItem(QWidget):
    """Mot dong trong danh sach note: tieu de + dong phu."""

    def __init__(self, title: str, subtitle_html: str, parent=None):
        super().__init__(parent)
        self.title = QLabel(title)
        self.title.setObjectName("noteTitle")
        self.subtitle = QLabel(subtitle_html)
        self.subtitle.setObjectName("noteSubtitle")
        self.subtitle.setTextFormat(Qt.TextFormat.RichText)
        self.subtitle.setWordWrap(True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(0)
        layout.addWidget(self.title)
        layout.addWidget(self.subtitle)
        self.setSizePolicy(
            self.sizePolicy().horizontalPolicy(), self.sizePolicy().verticalPolicy()
        )


class SearchPanel(QWidget):
    """Bang ben trai: tim toan kho, loc tag va danh sach note."""

    filtersChanged = Signal()
    noteSelected = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._root = None
        self.setMinimumWidth(230)
        self.setMaximumWidth(360)

        self._search_edit = QLineEdit()
        self._search_edit.setPlaceholderText("Tim toan kho, vi du: apache tag:linux")
        self._search_edit.textChanged.connect(lambda _text: self.filtersChanged.emit())

        tag_header = QLabel("Loc theo tag")
        tag_header.setObjectName("sidebarHeader")
        self._tag_list = QListWidget()
        self._tag_list.itemClicked.connect(self._on_tag_clicked)

        note_header = QLabel("Danh sach note")
        note_header.setObjectName("sidebarHeader")
        self._note_list = QListWidget()
        self._note_list.setSpacing(2)
        self._note_list.itemClicked.connect(self._on_note_clicked)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        layout.addWidget(self._search_edit)
        layout.addWidget(tag_header)
        layout.addWidget(self._tag_list, 0)
        layout.addWidget(note_header)
        layout.addWidget(self._note_list, 1)

        self._clear_filters()

    def _clear_filters(self):
        self._keyword = ""
        self._tag_name = None

    def keyword(self) -> str:
        return self._keyword

    def tagName(self):
        return self._tag_name

    def currentQuery(self) -> str:
        return self._search_edit.text()

    def setTags(self, names: list, current: str | None):
        self._tag_list.clear()
        all_item = QListWidgetItem("Tat ca")
        self._tag_list.addItem(all_item)
        if current is None:
            self._tag_list.setCurrentItem(all_item)
        for name in names:
            item = QListWidgetItem(name)
            if name == current:
                self._tag_list.setCurrentItem(item)
            self._tag_list.addItem(item)

    def _on_tag_clicked(self, item):
        text = item.text()
        self._tag_name = None if text == "Tat ca" else text
        self.filtersChanged.emit()

    def refresh_filters_from_query(self):
        """Tach tag:<ten> ra khoi chuoi tim kiem (UC10)."""
        text = self.currentQuery().strip()
        tag_token = None
        terms = []
        for token in text.split():
            if token.startswith("tag:"):
                tag_token = token[4:].strip()
            elif token:
                terms.append(token)
        self._keyword = " ".join(terms)
        if tag_token is not None:
            self._tag_name = tag_token or None
            self._select_tag(self._tag_name)

    def _select_tag(self, name):
        for index in range(self._tag_list.count()):
            item = self._tag_list.item(index)
            item_text = item.text()
            if item_text == name:
                self._tag_list.setCurrentItem(item)
                return

    def setNotes(self, rows, searched: bool):
        self._note_list.blockSignals(True)
        self._note_list.clear()
        for row in rows:
            title = row["title"] or "Khong co tieu de"
            snippet = ""
            if searched and "snip" in row.keys():
                snippet = _snippet_html(row["snip"]) if row["snip"] else ""
            if snippet:
                subtitle = snippet
            else:
                updated = (row["updated_at"] or "")[:16]
                subtitle = "Sua: " + updated if updated else "Vua tao"
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, row["id"])
            widget = NoteListItem(title, subtitle)
            item.setSizeHint(widget.sizeHint())
            self._note_list.addItem(item)
            self._note_list.setItemWidget(item, widget)
        self._note_list.blockSignals(False)

    def selectNoteById(self, note_id: int):
        for index in range(self._note_list.count()):
            item = self._note_list.item(index)
            if item.data(Qt.ItemDataRole.UserRole) == note_id:
                self._note_list.setCurrentItem(item)
                return

    def setActiveNote(self, note_id: int):
        self.selectNoteById(note_id)

    def _on_note_clicked(self, item):
        note_id = item.data(Qt.ItemDataRole.UserRole)
        if note_id:
            self.noteSelected.emit(note_id)


def _snippet_html(snippet: str) -> str:
    """Chuyen snippet tu FTS sang HTML nhan nen vang cho tu khoa."""
    safe = str(snippet).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    safe = safe.replace("\x01", '<span style="background-color:#fff8c5;">')
    safe = safe.replace("\x02", "</span>")
    return safe