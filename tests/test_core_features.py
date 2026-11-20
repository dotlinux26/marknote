"""Unit tests cho R2 (File Import & duplicate naming), R5 (SQLite pragmas & optimization), va Font Awesome Icons."""

import sys
import tempfile
import unittest
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QToolBar

_app = QApplication.instance() or QApplication([])

from db import DbManager, NoteDAO
from icons import get_icon
from main import MainWindow


class TestSqliteStorageOptimization(unittest.TestCase):
    """Kiem tra R5: SQLite storage optimization pragmas, routine VACUUM va optimize."""

    def setUp(self):
        self.tmp_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.db_path = Path(self.tmp_file.name)
        self.tmp_file.close()
        self.db = DbManager(self.db_path)

    def tearDown(self):
        self.db.close()
        if self.db_path.exists():
            try:
                self.db_path.unlink()
            except Exception:
                pass

    def test_pragmas(self):
        conn = self.db.connect()
        journal_mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
        synchronous = conn.execute("PRAGMA synchronous").fetchone()[0]
        temp_store = conn.execute("PRAGMA temp_store").fetchone()[0]
        cache_size = conn.execute("PRAGMA cache_size").fetchone()[0]
        page_size = conn.execute("PRAGMA page_size").fetchone()[0]

        self.assertEqual(journal_mode.lower(), "wal")
        self.assertEqual(synchronous, 1)  # 1 == NORMAL
        self.assertEqual(temp_store, 2)   # 2 == MEMORY
        self.assertIn(cache_size, (-16000, -64000))
        self.assertEqual(page_size, 4096)

    def test_vacuum_and_optimize(self):
        conn = self.db.connect()
        dao = NoteDAO(self.db)
        note_id = dao.insert("Sample Note", "# Content for testing search")
        self.assertGreater(note_id, 0)

        # FTS5 optimize and SQLite pragma optimize
        self.db.optimize()

        # Database VACUUM
        self.db.vacuum()

        # Routine combined maintenance
        self.db.routine_optimize()

        # Query after maintenance
        results = dao.searchFTS("testing")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Sample Note")


class TestFileImportAndAutoNaming(unittest.TestCase):
    """Kiem tra R2: Native file import, auto-naming with stem va (1), (2) duplicate suffix."""

    def setUp(self):
        self.tmp_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.db_path = Path(self.tmp_file.name)
        self.tmp_file.close()
        self.db = DbManager(self.db_path)
        self.dao = NoteDAO(self.db)
        self.tmp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.db.close()
        self.tmp_dir.cleanup()
        if self.db_path.exists():
            try:
                self.db_path.unlink()
            except Exception:
                pass

    def test_import_file_stem_naming(self):
        file_path = Path(self.tmp_dir.name) / "My Project Notes.md"
        file_path.write_text("# Project Heading\nSome notes", encoding="utf-8")

        note_id = self.dao.importFile(file_path)
        self.assertGreater(note_id, 0)

        note = self.dao.getById(note_id)
        self.assertEqual(note["title"], "My Project Notes")
        self.assertEqual(note["content_md"], "# Project Heading\nSome notes")

    def test_duplicate_naming_suffix(self):
        file_path = Path(self.tmp_dir.name) / "Daily Log.txt"
        file_path.write_text("Entry 1", encoding="utf-8")

        id1 = self.dao.importFile(file_path)
        note1 = self.dao.getById(id1)
        self.assertEqual(note1["title"], "Daily Log")

        # First duplicate -> should have " (1)"
        id2 = self.dao.importFile(file_path)
        note2 = self.dao.getById(id2)
        self.assertEqual(note2["title"], "Daily Log (1)")

        # Second duplicate -> should have " (2)"
        id3 = self.dao.importFile(file_path)
        note3 = self.dao.getById(id3)
        self.assertEqual(note3["title"], "Daily Log (2)")

        # Third duplicate -> should have " (3)"
        id4 = self.dao.importFile(file_path)
        note4 = self.dao.getById(id4)
        self.assertEqual(note4["title"], "Daily Log (3)")


class TestFontAwesomeIconsAndMainWindow(unittest.TestCase):
    """Kiem tra Font Awesome SVG icons trong Toolbar, Menubar, Window Icon, va Buttons."""

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmp_dir.name) / "test_gui.db"
        from db import DbManager
        self.win = MainWindow(db=DbManager(self.db_path))

    def tearDown(self):
        self.win.close()
        self.tmp_dir.cleanup()

    def test_toolbar_style_and_icons(self):
        toolbars = [w for w in self.win.children() if isinstance(w, QToolBar)]
        self.assertGreaterEqual(len(toolbars), 1)
        toolbar = toolbars[0]
        self.assertEqual(toolbar.toolButtonStyle(), Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

    def test_actions_have_crisp_icons(self):
        actions = [
            self.win.act_new,
            self.win.act_import,
            self.win.act_save,
            self.win.act_rename,
            self.win.act_delete,
            self.win.act_export_html,
            self.win.act_export_pdf,
            self.win.act_export_md,
            self.win.act_quit,
            self.win.act_find,
            self.win.act_replace,
            self.win.act_insert_image,
            self.win.act_open_media,
            self.win.act_sync,
            self.win.act_settings,
            self.win.act_about,
        ]
        for act in actions:
            self.assertFalse(act.icon().isNull(), f"Action '{act.text()}' must have a valid icon")

    def test_window_icon_is_set(self):
        self.assertFalse(self.win.windowIcon().isNull())

    def test_buttons_have_icons(self):
        self.assertFalse(self.win.tag_button.icon().isNull())
        self.assertFalse(self.win.btn_insert_image.icon().isNull())
        self.assertFalse(self.win.btn_open_media.icon().isNull())
        self.assertFalse(self.win.title_label.pencil.icon().isNull())

    def test_main_window_import_files(self):
        doc = Path(self.tmp_dir.name) / "QuickStart.md"
        doc.write_text("# Quick Start Guide\nWelcome to MarkNote", encoding="utf-8")

        imported_ids = self.win.importFiles([doc])
        self.assertEqual(len(imported_ids), 1)
        self.assertEqual(self.win.title_label.title(), "QuickStart")
        self.assertEqual(self.win.editor.getText(), "# Quick Start Guide\nWelcome to MarkNote")

        # Duplicate import
        imported_ids2 = self.win.importFiles([doc])
        self.assertEqual(len(imported_ids2), 1)
        self.assertEqual(self.win.title_label.title(), "QuickStart (1)")


if __name__ == "__main__":
    unittest.main()
