"""O soan thao Markdown, hop thoai tim/thay the va bang dieu huong."""

from __future__ import annotations

import re
from pathlib import Path

from PySide6.QtCore import QMimeData, QPoint, QRect, QSize, Qt, Signal
from PySide6.QtGui import (
    QColor,
    QFontDatabase,
    QImage,
    QPainter,
    QTextCharFormat,
    QTextCursor,
)
from PySide6.QtWidgets import (
    QApplication,
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

from media import (
    copy_file_to_media,
    is_image_url,
    make_markdown_image_tag,
    save_qimage_to_media,
)

COLOR_MATCH = "#fff8c5"
COLOR_CURRENT = "#f8b886"


class LineNumberArea(QWidget):
    """Cot so dong danh cho EditorPane theo tieu chuan Qt Code Editor."""

    def __init__(self, editor: EditorPane):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self) -> QSize:
        return QSize(self.editor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self.editor.lineNumberAreaPaintEvent(event)

    def mousePressEvent(self, event):
        pos = event.position().toPoint()
        block = self.editor.firstVisibleBlock()
        top = int(self.editor.blockBoundingGeometry(block).translated(self.editor.contentOffset()).top())
        bottom = top + int(self.editor.blockBoundingRect(block).height())
        while block.isValid():
            if top <= pos.y() <= bottom:
                cursor = self.editor.textCursor()
                cursor.setPosition(block.position())
                self.editor.setTextCursor(cursor)
                self.editor.setFocus()
                break
            block = block.next()
            top = bottom
            bottom = top + int(self.editor.blockBoundingRect(block).height())


class EditorPane(QPlainTextEdit):
    """O soan thao ben trai, ho tro tim highlight, chen anh, keo tha va paste anh."""

    imageInserted = Signal(str)
    insertImageRequested = Signal()
    openMediaRequested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        font.setPointSize(12)
        self.setFont(font)
        self.setPlaceholderText("No note opened. Press New to create one.")
        self.setTabStopDistance(4 * self.fontMetrics().horizontalAdvance(" "))
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        self._find_dialog = None
        self._matches = []
        self._index = -1
        self._case_sensitive = False

        self.lineNumberArea = LineNumberArea(self)
        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.lineNumberArea.update)
        self.updateLineNumberAreaWidth(0)

    def lineNumberAreaWidth(self) -> int:
        digits = 1
        m = max(1, self.blockCount())
        while m >= 10:
            m //= 10
            digits += 1
        space = 14 + self.fontMetrics().horizontalAdvance("9") * digits + 8
        return space

    def updateLineNumberAreaWidth(self, _=0):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def updateLineNumberArea(self, rect: QRect, dy: int):
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(
            cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()
        )

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.lineNumberArea)
        is_dark = self.palette().base().color().lightness() < 128
        if is_dark:
            bg_color = QColor("#1e1e1e")
            border_color = QColor("#30363d")
            text_color = QColor("#6e7681")
            current_text_color = QColor("#e6edf3")
        else:
            bg_color = QColor("#f6f8fa")
            border_color = QColor("#d8dee4")
            text_color = QColor("#8c959f")
            current_text_color = QColor("#1f2328")

        painter.fillRect(event.rect(), bg_color)
        painter.setPen(border_color)
        painter.drawLine(
            event.rect().width() - 1,
            event.rect().top(),
            event.rect().width() - 1,
            event.rect().bottom(),
        )

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())

        current_line = self.textCursor().blockNumber()
        painter.setFont(self.font())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                if block_number == current_line:
                    painter.setPen(current_text_color)
                    font = painter.font()
                    font.setBold(True)
                    painter.setFont(font)
                    painter.drawText(
                        0,
                        top,
                        self.lineNumberArea.width() - 8,
                        self.fontMetrics().height(),
                        Qt.AlignmentFlag.AlignRight,
                        number,
                    )
                    font.setBold(False)
                    painter.setFont(font)
                else:
                    painter.setPen(text_color)
                    painter.drawText(
                        0,
                        top,
                        self.lineNumberArea.width() - 8,
                        self.fontMetrics().height(),
                        Qt.AlignmentFlag.AlignRight,
                        number,
                    )

            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1

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

    # ----------------------------------------------------------- media / anh
    def insertImageFromFile(self, file_path: Path | str) -> str:
        """Sao chep file vao thu muc media chung va chen ma Markdown tai vi tri con tro."""
        saved_name = copy_file_to_media(file_path)
        tag = make_markdown_image_tag(saved_name)
        cursor = self.textCursor()
        cursor.insertText(tag)
        self.setTextCursor(cursor)
        self.ensureCursorVisible()
        self.imageInserted.emit(saved_name)
        return saved_name

    def insertImageFromQImage(self, qimage: QImage) -> str:
        """Luu QImage thanh PNG trong thu muc media va chen ma Markdown tai vi tri con tro."""
        saved_name = save_qimage_to_media(qimage)
        tag = make_markdown_image_tag(saved_name)
        cursor = self.textCursor()
        cursor.insertText(tag)
        self.setTextCursor(cursor)
        self.ensureCursorVisible()
        self.imageInserted.emit(saved_name)
        return saved_name

    def insertFromMimeData(self, source: QMimeData):
        """Xu ly paste (Ctrl+V): ho tro paste anh tu clipboard hoac paste file anh da copy."""
        if self.isReadOnly():
            return

        # 1. Du lieu anh truc tiep trong clipboard (chup man hinh, copy image)
        if source.hasImage():
            img = source.imageData()
            if isinstance(img, QImage) and not img.isNull():
                self.insertImageFromQImage(img)
                return
            clip = QApplication.clipboard()
            if clip:
                clip_img = clip.image()
                if not clip_img.isNull():
                    self.insertImageFromQImage(clip_img)
                    return

        # 2. File anh duoc copy tu Explorer / trinh quan ly file
        if source.hasUrls():
            image_urls = [u for u in source.urls() if is_image_url(u)]
            if image_urls:
                for u in image_urls:
                    self.insertImageFromFile(u.toLocalFile())
                return

        super().insertFromMimeData(source)

    def _has_acceptable_media(self, mime: QMimeData) -> bool:
        if mime.hasImage():
            return True
        if mime.hasUrls():
            return any(is_image_url(u) for u in mime.urls())
        return False

    def dragEnterEvent(self, event):
        if self._has_acceptable_media(event.mimeData()):
            event.acceptProposedAction()
            return
        super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if self._has_acceptable_media(event.mimeData()):
            event.acceptProposedAction()
            return
        super().dragMoveEvent(event)

    def dropEvent(self, event):
        mime = event.mimeData()
        if self._has_acceptable_media(mime):
            pos = event.position().toPoint() if hasattr(event, "position") else event.pos()
            cursor = self.cursorForPosition(pos)
            self.setTextCursor(cursor)

            if mime.hasUrls():
                image_urls = [u for u in mime.urls() if is_image_url(u)]
                if image_urls:
                    event.acceptProposedAction()
                    for u in image_urls:
                        self.insertImageFromFile(u.toLocalFile())
                    return

            if mime.hasImage():
                img = mime.imageData()
                if isinstance(img, QImage) and not img.isNull():
                    event.acceptProposedAction()
                    self.insertImageFromQImage(img)
                    return
                clip = QApplication.clipboard()
                if clip and not clip.image().isNull():
                    event.acceptProposedAction()
                    self.insertImageFromQImage(clip.image())
                    return

        super().dropEvent(event)

    def contextMenuEvent(self, event):
        menu = self.createStandardContextMenu()
        menu.addSeparator()
        act_insert = menu.addAction("Insert Image...")
        act_insert.triggered.connect(self.insertImageRequested.emit)
        act_media = menu.addAction("Open Media Folder")
        act_media.triggered.connect(self.openMediaRequested.emit)
        menu.exec(event.globalPos())


class FindReplaceDialog(QDialog):
    """Tim trong note hien tai (UC08) va thay the (UC09)."""

    contentReplaced = Signal()

    def __init__(self, editor: EditorPane, replace_mode: bool = False, parent=None):
        super().__init__(parent)
        self._editor = editor
        editor._find_dialog = self
        self._last_keyword = None
        self._last_case = None

        self.setWindowTitle("Find and Replace")
        self.setMinimumWidth(430)

        find_label = QLabel("Find:")
        self._find_edit = QLineEdit()
        self._find_edit.setPlaceholderText("Enter text to search")
        self._case_box = QCheckBox("Match case")
        self._status = QLabel("0/0")
        self._status.setObjectName("mutedLabel")

        replace_label = QLabel("Replace with:")
        self._replace_edit = QLineEdit()
        self._replace_edit.setPlaceholderText("Replacement text")
        self._replace_row = QWidget()
        replace_row = QHBoxLayout(self._replace_row)
        replace_row.setContentsMargins(0, 0, 0, 0)
        replace_row.addWidget(replace_label)
        replace_row.addWidget(self._replace_edit)
        self._replace_row.setVisible(replace_mode)

        btn_next = QPushButton("Find Next")
        btn_prev = QPushButton("Find Previous")
        btn_prev.setToolTip("Shift + Enter")
        btn_replace = QPushButton("Replace")
        btn_replace_all = QPushButton("Replace All")
        btn_close = QPushButton("Close")
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
            self._status.setText("Enter text to search")
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

            QMessageBox.information(self, "Replace", "Replaced %d occurrence(s)." % count)


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
        self._search_edit.setPlaceholderText("Search all notes, e.g.: apache tag:linux")
        self._search_edit.textChanged.connect(lambda _text: self.filtersChanged.emit())

        tag_header = QLabel("Filter by tag")
        tag_header.setObjectName("sidebarHeader")
        self._tag_list = QListWidget()
        self._tag_list.itemClicked.connect(self._on_tag_clicked)

        note_header = QLabel("Notes")
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
        all_item = QListWidgetItem("All")
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
        self._tag_name = None if text == "All" else text
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
            title = row["title"] or "Untitled"
            snippet = ""
            if searched and "snip" in row.keys():
                snippet = _snippet_html(row["snip"]) if row["snip"] else ""
            if snippet:
                subtitle = snippet
            else:
                updated = (row["updated_at"] or "")[:16]
                subtitle = "Modified: " + updated if updated else "Created"
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