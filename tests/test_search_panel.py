"""Unit tests cho R3 (SearchPanel resizable layout & drag-drop signals) va R4 (Font Awesome icons)."""

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path

# Add src to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from PySide6.QtCore import QMimeData, QPointF, Qt, QUrl
from PySide6.QtGui import QDropEvent, QIcon, QPixmap
from PySide6.QtWidgets import QApplication, QLabel, QListWidget, QSplitter

from editor import SearchPanel
from icons import ICONS_SVG, export_app_icon_png, get_icon, get_pixmap


class TestSearchPanelLayoutAndSignals(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.panel = SearchPanel()

    def test_search_panel_resizable_no_max_width(self):
        """Kiem tra SearchPanel khong con bi gioi han maximumWidth(360)."""
        self.assertEqual(self.panel.minimumWidth(), 230)
        self.assertGreater(self.panel.maximumWidth(), 360)
        # Co the set kich thuoc rong tuy y (resizable)
        self.panel.resize(600, 800)
        self.assertEqual(self.panel.width(), 600)

    def test_search_panel_vertical_splitter(self):
        """Kiem tra QSplitter(Qt.Orientation.Vertical) giua Filter by tag va Notes."""
        splitter = self.panel.findChild(QSplitter)
        self.assertIsNotNone(splitter, "SearchPanel phai chua mot QSplitter")
        self.assertEqual(splitter.orientation(), Qt.Orientation.Vertical)
        self.assertEqual(splitter.count(), 2)

        # Widget 0: Filter by tag
        w0 = splitter.widget(0)
        self.assertIsNotNone(w0)
        tag_headers = [lbl for lbl in w0.findChildren(QLabel) if "tag" in lbl.text().lower()]
        self.assertTrue(len(tag_headers) > 0, "Widget tren phai chua tieu de Filter by tag")
        self.assertIsNotNone(w0.findChild(QListWidget), "Widget tren phai chua tag list")

        # Widget 1: Notes
        w1 = splitter.widget(1)
        self.assertIsNotNone(w1)
        note_headers = [lbl for lbl in w1.findChildren(QLabel) if "note" in lbl.text().lower()]
        self.assertTrue(len(note_headers) > 0, "Widget duoi phai chua tieu de Notes")
        self.assertIsNotNone(w1.findChild(QListWidget), "Widget duoi phai chua notes list")

    def test_drag_drop_signals_emitted_on_drop(self):
        """Kiem tra tin hieu filesDropped va fileDropped khi keo tha file vao SearchPanel."""
        self.assertTrue(self.panel.acceptDrops())

        received_batch: list[list[str]] = []
        received_single: list[str] = []

        self.panel.filesDropped.connect(lambda files: received_batch.append(files))
        self.panel.fileDropped.connect(lambda f: received_single.append(f))

        test_path = str(Path(__file__).resolve().parent.parent / "README.md")
        mime = QMimeData()
        mime.setUrls([QUrl.fromLocalFile(test_path)])

        event = QDropEvent(
            QPointF(50, 50),
            Qt.DropAction.CopyAction,
            mime,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )
        self.panel.dropEvent(event)

        self.assertEqual(len(received_batch), 1)
        self.assertTrue(
            any(os.path.normpath(f) == os.path.normpath(test_path) for f in received_batch[0])
        )
        self.assertEqual(len(received_single), 1)
        self.assertEqual(os.path.normpath(received_single[0]), os.path.normpath(test_path))


class TestFontAwesomeIcons(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        cls.app = QApplication.instance() or QApplication([])

    def test_icons_svg_and_get_icon(self):
        """Kiem tra tat ca icon SVG trong ICONS_SVG deu tra ve QIcon hop le."""
        for name in ICONS_SVG:
            icon = get_icon(name)
            self.assertIsInstance(icon, QIcon)
            self.assertFalse(icon.isNull(), f"Icon '{name}' khong duoc null")

    def test_icon_aliases(self):
        """Kiem tra cac bi danh icon thong dung."""
        for alias in ["new", "import", "save", "rename", "delete", "sync", "tags", "marknote"]:
            icon = get_icon(alias)
            self.assertFalse(icon.isNull(), f"Alias '{alias}' phai tra ve icon hop le")

    def test_get_pixmap(self):
        """Kiem tra ham get_pixmap tra ve QPixmap sac net."""
        pix = get_pixmap("tag", size=32)
        self.assertIsInstance(pix, QPixmap)
        self.assertEqual(pix.width(), 32)
        self.assertEqual(pix.height(), 32)
        self.assertFalse(pix.isNull())

    def test_export_app_icon_png(self):
        """Kiem tra xuat logo app ra file PNG."""
        assets_dir = Path(__file__).resolve().parent.parent / "assets"
        png_path = assets_dir / "marknote.png"
        export_app_icon_png(png_path, size=256)
        self.assertTrue(png_path.exists())
        self.assertGreater(png_path.stat().st_size, 1000)


if __name__ == "__main__":
    unittest.main()
