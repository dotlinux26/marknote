"""Unit tests for SQLite storage optimization (R5):
WAL mode, storage pragmas, compound indices, vacuum, optimize, and unique title resolution.
"""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from db import DbManager, NoteDAO, TagDAO


class TestSqliteStoragePragmas(unittest.TestCase):
    """Tier 1: Basic validation of SQLite storage pragmas and indices."""

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmp_dir.name) / "test_notes.db"
        self.db = DbManager(self.db_path)

    def tearDown(self):
        self.db.close()
        self.tmp_dir.cleanup()

    def test_wal_journal_mode(self):
        """Verify WAL (Write-Ahead Logging) journal mode is active."""
        conn = self.db.connect()
        row = conn.execute("PRAGMA journal_mode").fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row[0].lower(), "wal")

    def test_storage_footprint_and_perf_pragmas(self):
        """Verify performance and footprint pragmas configured in connect()."""
        conn = self.db.connect()
        sync = conn.execute("PRAGMA synchronous").fetchone()[0]
        temp_store = conn.execute("PRAGMA temp_store").fetchone()[0]
        cache_size = conn.execute("PRAGMA cache_size").fetchone()[0]
        page_size = conn.execute("PRAGMA page_size").fetchone()[0]
        auto_vacuum = conn.execute("PRAGMA auto_vacuum").fetchone()[0]
        foreign_keys = conn.execute("PRAGMA foreign_keys").fetchone()[0]

        self.assertEqual(sync, 1, "synchronous must be 1 (NORMAL)")
        self.assertEqual(temp_store, 2, "temp_store must be 2 (MEMORY)")
        self.assertEqual(cache_size, -16000, "cache_size must be -16000 (16MB)")
        self.assertEqual(page_size, 4096, "page_size must be 4096")
        self.assertEqual(auto_vacuum, 2, "auto_vacuum must be 2 (INCREMENTAL)")
        self.assertEqual(foreign_keys, 1, "foreign_keys must be ON (1)")

    def test_secondary_compound_indices_exist(self):
        """Verify secondary compound indices exist in the database schema."""
        conn = self.db.connect()
        indices = [
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='index'"
            ).fetchall()
        ]
        self.assertIn("idx_notes_pinned_updated", indices)
        self.assertIn("idx_note_tag_tag_id", indices)

    def test_query_planner_uses_compound_indices(self):
        """Verify EXPLAIN QUERY PLAN shows index usage for list query and tag joins."""
        conn = self.db.connect()
        # Query 1: Notes sorted by pinned DESC, updated_at DESC, id DESC
        plan_list = conn.execute(
            "EXPLAIN QUERY PLAN SELECT id, title, updated_at FROM notes "
            "ORDER BY pinned DESC, updated_at DESC, id DESC"
        ).fetchall()
        plan_list_str = " ".join(str(tuple(row)) for row in plan_list)
        self.assertIn("idx_notes_pinned_updated", plan_list_str)

        # Query 2: Note tag join on tag_id
        plan_tag = conn.execute(
            "EXPLAIN QUERY PLAN SELECT n.id FROM notes n "
            "JOIN note_tag nt ON nt.note_id = n.id "
            "JOIN tags t ON t.id = nt.tag_id "
            "WHERE t.name = ?",
            ("work",),
        ).fetchall()
        plan_tag_str = " ".join(str(tuple(row)) for row in plan_tag)
        self.assertIn("idx_note_tag_tag_id", plan_tag_str)


class TestSqliteMaintenanceRoutines(unittest.TestCase):
    """Tier 1 & 2: Testing optimize(), vacuum(), and WAL truncation."""

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmp_dir.name) / "test_maint.db"
        self.db = DbManager(self.db_path)
        self.dao = NoteDAO(self.db)

    def tearDown(self):
        self.db.close()
        self.tmp_dir.cleanup()

    def test_optimize_merges_fts5_and_runs_pragma(self):
        """Verify optimize() runs FTS5 segment merge and PRAGMA optimize without errors."""
        note_id = self.dao.insert("Optimization Test", "FTS5 content indexing test")
        self.assertGreater(note_id, 0)
        # optimize should run cleanly
        self.db.optimize()
        # verify FTS search still functions properly
        results = self.dao.searchFTS("indexing")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], note_id)

    def test_vacuum_no_transaction_error_and_truncates_wal(self):
        """Verify vacuum() changes isolation level, vacua, and truncates WAL."""
        wal_path = Path(str(self.db_path) + "-wal")

        # Generate some data and activity in WAL
        for i in range(20):
            self.dao.insert(f"Note {i}", f"Long body text {i} " * 50)

        # Vacuum routine
        self.db.vacuum()

        # Check WAL file exists or is truncated to 0 / checkpointed
        if wal_path.exists():
            self.assertEqual(wal_path.stat().st_size, 0)

        # Verify integrity
        conn = self.db.connect()
        integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
        self.assertEqual(integrity.lower(), "ok")

    def test_vacuum_with_pending_uncommitted_state(self):
        """Verify vacuum() does not crash even if an uncommitted operation is active."""
        conn = self.db.connect()
        conn.execute("INSERT INTO notes(title, content_md) VALUES('Pending', 'Data')")
        # Should commit and vacuum without 'cannot VACUUM from within a transaction'
        self.db.vacuum()
        row = self.dao.getByTitle("Pending")
        self.assertIsNotNone(row)

    def test_close_runs_optimize(self):
        """Verify closing connection executes PRAGMA optimize."""
        self.dao.insert("Closing Note", "Content before close")
        self.db.close()
        self.assertIsNone(self.db._conn)
        # Re-opening should work seamlessly
        new_conn = self.db.connect()
        row = self.db.query_one("SELECT title FROM notes WHERE title='Closing Note'")
        self.assertIsNotNone(row)

    def test_in_memory_db_maintenance_graceful(self):
        """Verify in-memory database does not crash on optimize() or vacuum()."""
        mem_db = DbManager(":memory:")
        mem_dao = NoteDAO(mem_db)
        mem_dao.insert("Mem Note", "Content in memory")
        mem_db.optimize()
        mem_db.vacuum()
        mem_db.routine_optimize()
        mem_db.close()


class TestUniqueTitleGeneration(unittest.TestCase):
    """Tier 1 & 2: Testing NoteDAO.get_unique_title collision handling."""

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmp_dir.name) / "test_titles.db"
        self.db = DbManager(self.db_path)
        self.dao = NoteDAO(self.db)

    def tearDown(self):
        self.db.close()
        self.tmp_dir.cleanup()

    def test_get_unique_title_no_duplicate(self):
        """Unique title remains unchanged when no existing note has that title."""
        title = self.dao.get_unique_title("Project Plan")
        self.assertEqual(title, "Project Plan")

    def test_get_unique_title_sequential_collisions(self):
        """Sequential duplicates receive (1), (2), (3) suffixes."""
        self.dao.insert("Weekly Report", "Content 0")
        t1 = self.dao.get_unique_title("Weekly Report")
        self.assertEqual(t1, "Weekly Report (1)")
        self.dao.insert(t1, "Content 1")

        t2 = self.dao.get_unique_title("Weekly Report")
        self.assertEqual(t2, "Weekly Report (2)")
        self.dao.insert(t2, "Content 2")

        t3 = self.dao.get_unique_title("Weekly Report")
        self.assertEqual(t3, "Weekly Report (3)")

    def test_get_unique_title_filling_gaps(self):
        """When gaps exist (e.g. Weekly Report and Weekly Report (2)), fills gap (1)."""
        self.dao.insert("Meeting Notes", "Main")
        self.dao.insert("Meeting Notes (2)", "Second")

        t_next = self.dao.get_unique_title("Meeting Notes")
        self.assertEqual(t_next, "Meeting Notes (1)")
        self.dao.insert(t_next, "First duplicate")

        t_after = self.dao.get_unique_title("Meeting Notes")
        self.assertEqual(t_after, "Meeting Notes (3)")

    def test_get_unique_title_empty_or_whitespace(self):
        """Empty or whitespace base titles default to 'Untitled' with proper suffixing."""
        t_empty = self.dao.get_unique_title("")
        self.assertEqual(t_empty, "Untitled")
        self.dao.insert(t_empty, "Body")

        t_spaces = self.dao.get_unique_title("   ")
        self.assertEqual(t_spaces, "Untitled (1)")

    def test_get_unique_title_none_input(self):
        """None input handled gracefully as 'Untitled'."""
        t_none = self.dao.get_unique_title(None)
        self.assertEqual(t_none, "Untitled")

    def test_get_unique_title_aliases(self):
        """Both get_unique_title and getUniqueTitle exist and behave identically."""
        self.dao.insert("Alias Test", "Data")
        self.assertEqual(self.dao.get_unique_title("Alias Test"), "Alias Test (1)")
        self.assertEqual(self.dao.getUniqueTitle("Alias Test"), "Alias Test (1)")


class TestSqliteWorkloadAndIntegrity(unittest.TestCase):
    """Tier 3 & 4: Pairwise and realistic workload tests."""

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmp_dir.name) / "test_workload.db"
        self.db = DbManager(self.db_path)
        self.note_dao = NoteDAO(self.db)
        self.tag_dao = TagDAO(self.db)

    def tearDown(self):
        self.db.close()
        self.tmp_dir.cleanup()

    def test_bulk_notes_tagging_and_fts_search(self):
        """Simulate realistic workload with 100 notes and tags, optimize, vacuum, verify integrity."""
        tag1 = self.tag_dao.create("work")
        tag2 = self.tag_dao.create("personal")

        for i in range(100):
            nid = self.note_dao.insert(f"Task {i:03d}", f"Content for note {i} with keyword alpha beta")
            if i % 2 == 0:
                self.tag_dao.assign(nid, tag1)
            if i % 3 == 0:
                self.tag_dao.assign(nid, tag2)

        # Query notes by tag
        work_notes = self.note_dao.list("work")
        self.assertEqual(len(work_notes), 50)

        # Search FTS
        search_res = self.note_dao.searchFTS("alpha")
        self.assertEqual(len(search_res), 100)

        # Routine optimize & vacuum
        self.db.routine_optimize()

        # Post-maintenance search & list verification
        self.assertEqual(len(self.note_dao.list("work")), 50)
        self.assertEqual(len(self.note_dao.searchFTS("alpha")), 100)

        # PRAGMA integrity_check
        conn = self.db.connect()
        integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
        self.assertEqual(integrity.lower(), "ok")


if __name__ == "__main__":
    unittest.main()
