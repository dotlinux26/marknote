"""Comprehensive verification test suite.

Covers:
1. Print directives and per-page styling (R1).
2. Native file import and duplicate auto-naming (R2).
3. SearchPanel resizable vertical splitter and drag-drop (R3).
4. Font Awesome SVG icon loading and crispness (R4).
5. SQLite storage optimization, pragmas, and routine maintenance (R5).
"""

from __future__ import annotations

import base64
import io
import os
import sys
import tempfile
import unittest
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from PIL import Image
from PySide6.QtCore import QMimeData, QSize, Qt, QUrl
from PySide6.QtGui import QColor, QIcon, QPixmap
from PySide6.QtWidgets import QApplication, QSplitter

_app = QApplication.instance() or QApplication([])

from db import DbManager, NoteDAO
from editor import SearchPanel
from exporter import (
    Exporter,
    PrintDirectiveConfig,
    adjust_image_alpha,
    build_document,
    build_pdf_page_rule,
    generate_page_css,
    parse_page_targets,
    parse_print_directive,
    parse_print_directives,
)
from icons import ALIASES, ICONS_SVG, export_app_icon_png, get_icon, get_pixmap
from main import MainWindow
from preview import MarkdownRenderer


class TestPrintDirectivesComprehensive(unittest.TestCase):
    """Verify R1 print directives, Pillow alpha scaling, CSS rules, and preview stripping."""

    def test_parse_complex_print_directive(self):
        text = (
            '[[print image="assets/paper.png" fit=stretch alpha="40%" '
            'position="top center" bg-color="#ffffff" gradient="linear-gradient(45deg, #eee, #fff)" '
            'text-color="#111111" pages="1-3,5" style="border: 1px solid black; padding: 10mm;"]]'
        )
        cfg = parse_print_directive(text)
        self.assertEqual(cfg.bg, "assets/paper.png")
        self.assertEqual(cfg.mode, "stretch")
        self.assertAlmostEqual(cfg.opacity, 0.4)
        self.assertEqual(cfg.position, "top center")
        self.assertEqual(cfg.bg_color, "#ffffff")
        self.assertEqual(cfg.gradient, "linear-gradient(45deg, #eee, #fff)")
        self.assertEqual(cfg.text_color, "#111111")
        self.assertEqual(cfg.pages, "1-3,5")
        self.assertIn("border: 1px solid black;", cfg.style)

    def test_parse_page_targets_extended(self):
        self.assertEqual(parse_page_targets("1-4"), [1, 2, 3, 4])
        self.assertEqual(parse_page_targets("4-2"), [2, 3, 4])
        self.assertEqual(parse_page_targets("1, 2, 5, 8"), [1, 2, 5, 8])
        self.assertEqual(parse_page_targets("odd"), ["odd"])
        self.assertEqual(parse_page_targets("even"), ["even"])
        self.assertEqual(parse_page_targets("all"), ["all"])

    def test_pillow_alpha_scaling_extreme_values(self):
        # 100% alpha (1.0)
        im = Image.new("RGBA", (10, 10), (100, 150, 200, 255))
        buf = io.BytesIO()
        im.save(buf, format="PNG")
        uri_100 = adjust_image_alpha(buf.getvalue(), alpha=1.0)
        self.assertTrue(uri_100.startswith("data:image/png;base64,"))

        # 0% alpha (0.0) -> fully transparent
        uri_0 = adjust_image_alpha(buf.getvalue(), alpha=0.0)
        decoded = base64.b64decode(uri_0.split(",", 1)[1])
        out_im = Image.open(io.BytesIO(decoded))
        self.assertEqual(out_im.getpixel((5, 5))[3], 0)

    def test_generate_page_css_odd_even(self):
        cfg_odd = PrintDirectiveConfig(bg_color="#fafafa", pages="odd")
        css_odd = generate_page_css(cfg_odd)
        self.assertIn("@page :right", css_odd)
        self.assertIn("background-color: #fafafa;", css_odd)

        cfg_even = PrintDirectiveConfig(bg_color="#f0f0f0", pages="even")
        css_even = generate_page_css(cfg_even)
        self.assertIn("@page :left", css_even)
        self.assertIn("background-color: #f0f0f0;", css_even)

    def test_markdown_renderer_hides_multiple_tokens(self):
        renderer = MarkdownRenderer()
        md = (
            "# Heading 1\n\n"
            '[[print bg="paper.png" mode=cover]]\n\n'
            "Some intermediate text.\n\n"
            '[[page-bg page=2 bg-color="#fff" text-color="#000"]]\n\n'
            "Final conclusion."
        )
        html = renderer.render(md)
        self.assertNotIn("[[print", html)
        self.assertNotIn("[[page-bg", html)
        self.assertIn("Heading 1", html)
        self.assertIn("Some intermediate text.", html)
        self.assertIn("Final conclusion.", html)


class TestFileImportComprehensive(unittest.TestCase):
    """Verify R2 native file import, auto-naming with stem and duplicate suffixes."""

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmp_dir.name) / "test_import.db"
        self.db = DbManager(self.db_path)
        self.dao = NoteDAO(self.db)

    def tearDown(self):
        self.db.close()
        self.tmp_dir.cleanup()

    def test_import_vietnamese_unicode_content(self):
        file_path = Path(self.tmp_dir.name) / "Báo cáo môn học.md"
        content = "# Báo cáo\nĐây là nội dung tiếng Việt có dấu: ắ, ằ, ố, ể, đ."
        file_path.write_text(content, encoding="utf-8")

        note_id = self.dao.importFile(file_path)
        self.assertGreater(note_id, 0)

        note = self.dao.getById(note_id)
        self.assertEqual(note["title"], "Báo cáo môn học")
        self.assertEqual(note["content_md"], content)

    def test_duplicate_naming_progression_up_to_5(self):
        file_path = Path(self.tmp_dir.name) / "Task.txt"
        file_path.write_text("Task item", encoding="utf-8")

        id0 = self.dao.importFile(file_path)
        self.assertEqual(self.dao.getById(id0)["title"], "Task")

        for i in range(1, 6):
            idn = self.dao.importFile(file_path)
            self.assertEqual(self.dao.getById(idn)["title"], f"Task ({i})")

    def test_main_window_import_filters_invalid_extensions(self):
        win = MainWindow(db=self.db)
        try:
            # Create a non-text/markdown file
            png_file = Path(self.tmp_dir.name) / "image.png"
            png_file.write_bytes(b"\x89PNG\r\n\x1a\n")

            # Create valid text file
            txt_file = Path(self.tmp_dir.name) / "NoteDoc.txt"
            txt_file.write_text("Hello text note", encoding="utf-8")

            imported_ids = win.importFiles([png_file, txt_file])
            self.assertEqual(len(imported_ids), 1)
            self.assertEqual(win.title_label.title(), "NoteDoc")
        finally:
            win.close()


class TestSearchPanelSplitterComprehensive(unittest.TestCase):
    """Verify R3 resizable SearchPanel, QSplitter(Qt.Orientation.Vertical) and drag-drop."""

    def test_search_panel_splitter_configuration(self):
        panel = SearchPanel()
        self.assertIsNotNone(panel.splitter)
        self.assertIsInstance(panel.splitter, QSplitter)
        self.assertEqual(panel.splitter.orientation(), Qt.Orientation.Vertical)
        self.assertEqual(panel.splitter.count(), 2)

        # Confirm maximum width restriction is absent
        self.assertEqual(panel.maximumWidth(), 16777215)  # QWIDGETSIZE_MAX default

    def test_extract_dropped_files_from_urls(self):
        panel = SearchPanel()
        mime = QMimeData()
        urls = [
            QUrl.fromLocalFile(r"C:\docs\note1.md"),
            QUrl.fromLocalFile(r"C:\docs\note2.txt"),
        ]
        mime.setUrls(urls)

        extracted = panel._extract_dropped_files(mime)
        self.assertEqual(len(extracted), 2)
        self.assertTrue(extracted[0].endswith("note1.md"))
        self.assertTrue(extracted[1].endswith("note2.txt"))


class TestSqliteStoragePragmasComprehensive(unittest.TestCase):
    """Verify R5 SQLite pragmas, optimization, and routine maintenance."""

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmp_dir.name) / "test_pragma.db"
        self.db = DbManager(self.db_path)

    def tearDown(self):
        self.db.close()
        self.tmp_dir.cleanup()

    def test_all_optimization_pragmas(self):
        conn = self.db.connect()
        pragmas = {
            "journal_mode": conn.execute("PRAGMA journal_mode").fetchone()[0].lower(),
            "synchronous": conn.execute("PRAGMA synchronous").fetchone()[0],
            "temp_store": conn.execute("PRAGMA temp_store").fetchone()[0],
            "cache_size": conn.execute("PRAGMA cache_size").fetchone()[0],
            "page_size": conn.execute("PRAGMA page_size").fetchone()[0],
        }
        self.assertEqual(pragmas["journal_mode"], "wal")
        self.assertEqual(pragmas["synchronous"], 1)  # NORMAL
        self.assertEqual(pragmas["temp_store"], 2)   # MEMORY
        self.assertIn(pragmas["cache_size"], (-16000, -64000))
        self.assertEqual(pragmas["page_size"], 4096)

    def test_routine_maintenance_execution(self):
        dao = NoteDAO(self.db)
        dao.insert("Maintenance Test", "Content testing routine optimization and vacuum")
        # Should execute without errors
        self.db.routine_optimize()

        # Verify database is operational after routine optimization
        results = dao.searchFTS("routine")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Maintenance Test")


class TestFontAwesomeIconsComprehensive(unittest.TestCase):
    """Verify R4 Font Awesome SVG icons, aliases, get_pixmap, and export."""

    def test_all_svg_icons_valid_and_non_empty(self):
        for name in ICONS_SVG:
            icon = get_icon(name)
            self.assertIsInstance(icon, QIcon)
            self.assertFalse(icon.isNull(), f"Icon '{name}' should not be null")

    def test_all_defined_aliases(self):
        for alias, target in ALIASES.items():
            icon = get_icon(alias)
            self.assertFalse(icon.isNull(), f"Alias '{alias}' -> '{target}' should return valid icon")

    def test_invalid_icon_name_returns_null_icon_safely(self):
        icon = get_icon("non_existent_icon_name_xyz")
        self.assertTrue(icon.isNull())

    def test_get_pixmap_custom_sizes_and_colors(self):
        for size in [16, 24, 32, 64]:
            pix = get_pixmap("file_save", size=size, color=QColor("#0969da"))
            self.assertIsInstance(pix, QPixmap)
            self.assertEqual(pix.width(), size)
            self.assertEqual(pix.height(), size)
            self.assertFalse(pix.isNull())

    def test_export_app_icon_png(self):
        tmp_png = Path(tempfile.gettempdir()) / "test_marknote_icon.png"
        try:
            export_app_icon_png(tmp_png, size=128)
            self.assertTrue(tmp_png.exists())
            self.assertGreater(tmp_png.stat().st_size, 500)
            with Image.open(tmp_png) as img:
                self.assertEqual(img.size, (128, 128))
        finally:
            if tmp_png.exists():
                try:
                    tmp_png.unlink()
                except Exception:
                    pass


if __name__ == "__main__":
    unittest.main()
