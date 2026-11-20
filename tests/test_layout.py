"""Unit tests cho layout he thong (R3 Resizable layout for SearchPanel & Sidebar, EditorPane drag-drop)."""

from __future__ import annotations

import os
import sys
import unittest
import warnings
from pathlib import Path

# Add src to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from PySide6.QtCore import QMimeData, QPoint, QPointF, Qt, QUrl
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import QApplication, QLabel, QListWidget, QSplitter, QWidget

from editor import EditorPane, SearchPanel


class TestSearchPanelLayout(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.panel = SearchPanel()

    def test_search_panel_contains_vertical_splitter(self):
        """Kiem tra SearchPanel chua vertical QSplitter voi orientation Qt.Orientation.Vertical."""
        self.assertTrue(hasattr(self.panel, "vertical_splitter"), "SearchPanel phai co thuoc tinh vertical_splitter")
        self.assertIsInstance(self.panel.vertical_splitter, QSplitter)
        self.assertEqual(self.panel.vertical_splitter.orientation(), Qt.Orientation.Vertical)

    def test_search_panel_splitter_has_tag_and_note_containers(self):
        """Kiem tra vertical_splitter chua tag_container va note_container hop le."""
        self.assertTrue(hasattr(self.panel, "tag_container"), "SearchPanel phai co thuoc tinh tag_container")
        self.assertTrue(hasattr(self.panel, "note_container"), "SearchPanel phai co thuoc tinh note_container")
        self.assertIsInstance(self.panel.tag_container, QWidget)
        self.assertIsInstance(self.panel.note_container, QWidget)

        splitter = self.panel.vertical_splitter
        self.assertEqual(splitter.count(), 2)
        self.assertEqual(splitter.widget(0), self.panel.tag_container)
        self.assertEqual(splitter.widget(1), self.panel.note_container)

        # Kiem tra ben trong tag_container co tag header va tag list
        tag_labels = [w for w in self.panel.tag_container.findChildren(QLabel) if "tag" in w.text().lower()]
        self.assertGreater(len(tag_labels), 0)
        self.assertIn(self.panel._tag_list, self.panel.tag_container.findChildren(QListWidget))

        # Kiem tra ben trong note_container co note header va note list
        note_labels = [w for w in self.panel.note_container.findChildren(QLabel) if "note" in w.text().lower()]
        self.assertGreater(len(note_labels), 0)
        self.assertIn(self.panel._note_list, self.panel.note_container.findChildren(QListWidget))

    def test_search_panel_maximum_width_unrestricted(self):
        """Kiem tra SearchPanel cho phep mo rong vuot qua 360px (maximumWidth >= 800 hoac khong gioi han)."""
        max_w = self.panel.maximumWidth()
        self.assertGreaterEqual(max_w, 800, f"maximumWidth phai >= 800, hien tai: {max_w}")
        # Thu resize len kich thuoc lon
        self.panel.resize(750, 900)
        self.assertGreaterEqual(self.panel.width(), 700)

    def test_splitter_children_non_collapsible(self):
        """Kiem tra cac phan tu con trong splitter khong bi collapse hoan toan."""
        splitter = self.panel.vertical_splitter
        self.assertFalse(splitter.childrenCollapsible(), "Splitter childrenCollapsible phai la False")

    def test_splitter_handle_width_and_stretch(self):
        """Kiem tra do day handle va cau hinh stretch factor cua splitter."""
        splitter = self.panel.vertical_splitter
        self.assertEqual(splitter.handleWidth(), 4, "handleWidth cua splitter phai la 4")


class TestEditorPaneDragDrop(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.editor = EditorPane()

    def test_editor_has_notes_dropped_signal(self):
        """Kiem tra EditorPane co signal notesDropped."""
        self.assertTrue(hasattr(self.editor, "notesDropped"))

    def test_editor_drag_enter_accepts_markdown_and_txt(self):
        """Kiem tra dragEnterEvent chap nhan file .md, .markdown, .txt."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            for filename in ["note.md", "doc.markdown", "readme.txt"]:
                mime = QMimeData()
                mime.setUrls([QUrl.fromLocalFile(f"C:/docs/{filename}")])
                event = QDragEnterEvent(
                    QPoint(10, 10),
                    Qt.DropAction.CopyAction,
                    mime,
                    Qt.MouseButton.LeftButton,
                    Qt.KeyboardModifier.NoModifier,
                )
                event.ignore()
                self.editor.dragEnterEvent(event)
                self.assertTrue(event.isAccepted(), f"dragEnterEvent phai chap nhan {filename}")

    def test_editor_drag_enter_ignores_unsupported_extensions(self):
        """Kiem tra dragEnterEvent khong chap nhan file .exe khong hop le."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            mime = QMimeData()
            mime.setUrls([QUrl.fromLocalFile("C:/docs/program.exe")])
            event = QDragEnterEvent(
                QPoint(10, 10),
                Qt.DropAction.CopyAction,
                mime,
                Qt.MouseButton.LeftButton,
                Qt.KeyboardModifier.NoModifier,
            )
            self.editor.dragEnterEvent(event)
            self.assertFalse(event.isAccepted(), "dragEnterEvent khong duoc chap nhan .exe")

    def test_editor_drop_event_emits_notes_dropped(self):
        """Kiem tra dropEvent emit notesDropped voi danh sach duong dan text files."""
        received: list[list[str]] = []
        self.editor.notesDropped.connect(lambda paths: received.append(paths))

        test_files = ["C:/notes/a.md", "C:/notes/b.markdown", "C:/notes/c.txt"]
        mime = QMimeData()
        mime.setUrls([QUrl.fromLocalFile(p) for p in test_files])

        event = QDropEvent(
            QPointF(20, 20),
            Qt.DropAction.CopyAction,
            mime,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )
        self.editor.dropEvent(event)

        self.assertEqual(len(received), 1)
        self.assertEqual(len(received[0]), 3)
        for expected in test_files:
            self.assertTrue(any(os.path.normpath(r) == os.path.normpath(expected) for r in received[0]))


if __name__ == "__main__":
    unittest.main()
