"""Lop du lieu SQLite: DbManager, NoteDAO, TagDAO, SettingsDAO."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from settings import APP_DIR, DB_PATH, DEFAULT_SETTINGS

SCHEMA = """
CREATE TABLE IF NOT EXISTS notes(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  content_md TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  pinned INT DEFAULT 0,
  archived INT DEFAULT 0
);

CREATE TABLE IF NOT EXISTS tags(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT UNIQUE NOT NULL,
  color TEXT
);

CREATE TABLE IF NOT EXISTS note_tag(
  note_id INT,
  tag_id INT,
  PRIMARY KEY(note_id, tag_id),
  FOREIGN KEY(note_id) REFERENCES notes(id) ON DELETE CASCADE,
  FOREIGN KEY(tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS settings(
  key TEXT PRIMARY KEY,
  value TEXT
);

CREATE VIRTUAL TABLE IF NOT EXISTS notes_fts USING fts5(
  title, content_md, content='notes', content_rowid='id'
);

CREATE TRIGGER IF NOT EXISTS notes_ai AFTER INSERT ON notes BEGIN
  INSERT INTO notes_fts(rowid, title, content_md)
  VALUES (new.id, new.title, new.content_md);
END;

CREATE TRIGGER IF NOT EXISTS notes_ad AFTER DELETE ON notes BEGIN
  INSERT INTO notes_fts(notes_fts, rowid, title, content_md)
  VALUES ('delete', old.id, old.title, old.content_md);
END;

CREATE TRIGGER IF NOT EXISTS notes_au AFTER UPDATE ON notes BEGIN
  INSERT INTO notes_fts(notes_fts, rowid, title, content_md)
  VALUES ('delete', old.id, old.title, old.content_md);
  INSERT INTO notes_fts(rowid, title, content_md)
  VALUES (new.id, new.title, new.content_md);
END;

CREATE INDEX IF NOT EXISTS idx_notes_pinned_updated ON notes(pinned, updated_at DESC, id DESC);
CREATE INDEX IF NOT EXISTS idx_note_tag_tag_id ON note_tag(tag_id);
"""


class DbManager:
    """Quan ly mot ket noi SQLite duy nhat: ~/.marknote/notes.db."""

    def __init__(self, path: Path | str = DB_PATH):
        self.path = Path(path) if str(path) != ":memory:" else ":memory:"
        self._conn = None

    def connect(self) -> sqlite3.Connection:
        if self._conn is not None:
            return self._conn
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.path), timeout=5.0)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA page_size = 4096")
        self._conn.execute("PRAGMA auto_vacuum = INCREMENTAL")
        self._conn.execute("PRAGMA journal_mode = WAL")
        self._conn.execute("PRAGMA synchronous = NORMAL")
        self._conn.execute("PRAGMA temp_store = MEMORY")
        self._conn.execute("PRAGMA cache_size = -16000")
        self._conn.execute("PRAGMA mmap_size = 268435456")
        self._conn.execute("PRAGMA foreign_keys = ON")
        self._conn.executescript(SCHEMA)
        self._seed_settings()
        return self._conn

    def _seed_settings(self):
        for key, value in DEFAULT_SETTINGS.items():
            self._conn.execute(
                "INSERT OR IGNORE INTO settings(key, value) VALUES(?, ?)",
                (key, value),
            )
        self._conn.commit()

    def execute(self, sql: str, params=()) -> sqlite3.Cursor:
        conn = self.connect()
        with conn:
            return conn.execute(sql, params)

    def query(self, sql: str, params=()) -> list:
        conn = self.connect()
        cursor = conn.execute(sql, params)
        return cursor.fetchall()

    def query_one(self, sql: str, params=()):
        rows = self.query(sql, params)
        return rows[0] if rows else None

    def optimize(self):
        """Routine maintenance: compact FTS5 index and run PRAGMA optimize."""
        conn = self.connect()
        try:
            with conn:
                conn.execute("INSERT INTO notes_fts(notes_fts) VALUES('optimize')")
        except sqlite3.OperationalError:
            pass
        try:
            with conn:
                conn.execute("PRAGMA optimize")
        except sqlite3.OperationalError:
            pass

    def vacuum(self):
        """Routine VACUUM to reclaim free space, incremental vacuum and truncate WAL."""
        conn = self.connect()
        old_iso = conn.isolation_level
        try:
            conn.commit()
            conn.isolation_level = None
            conn.execute("VACUUM")
            conn.execute("PRAGMA incremental_vacuum")
            conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        finally:
            conn.isolation_level = old_iso

    def routine_optimize(self):
        """Combined routine maintenance: optimize and vacuum."""
        self.optimize()
        self.vacuum()

    def close(self):
        if self._conn is not None:
            try:
                self.optimize()
            except Exception:
                try:
                    self._conn.execute("PRAGMA optimize")
                except Exception:
                    pass
            self._conn.close()
            self._conn = None


class NoteDAO:
    """Cac thao tac voi bang notes va chi muc FTS5."""

    def __init__(self, db: DbManager):
        self.db = db

    def insert(self, title: str, md: str) -> int:
        cursor = self.db.execute(
            "INSERT INTO notes(title, content_md, updated_at) "
            "VALUES(?, ?, CURRENT_TIMESTAMP)",
            (title, md),
        )
        return cursor.lastrowid

    def update(self, note_id: int, md: str):
        self.db.execute(
            "UPDATE notes SET content_md=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
            (md, note_id),
        )

    def rename(self, note_id: int, title: str):
        self.db.execute(
            "UPDATE notes SET title=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
            (title, note_id),
        )

    def delete(self, note_id: int):
        self.db.execute("DELETE FROM notes WHERE id=?", (note_id,))

    def getById(self, note_id: int):
        return self.db.query_one(
            "SELECT id, title, content_md, created_at, updated_at "
            "FROM notes WHERE id=?",
            (note_id,),
        )

    def getByTitle(self, title: str):
        return self.db.query_one(
            "SELECT id, title, content_md, created_at, updated_at "
            "FROM notes WHERE title=?",
            (title,),
        )

    def title_exists(self, title: str) -> bool:
        """Kiem tra xem tieu de da ton tai trong bang notes hay chua."""
        row = self.db.query_one("SELECT 1 FROM notes WHERE title=?", (title,))
        return row is not None

    def get_unique_title(self, base_title: str) -> str:
        """Sinh tieu de duy nhat: giu nguyen stem neu chua ton tai, them (1), (2)... neu trung."""
        stem = (base_title or "").strip() or "Untitled"
        if not self.title_exists(stem):
            return stem
        counter = 1
        while True:
            candidate = f"{stem} ({counter})"
            if not self.title_exists(candidate):
                return candidate
            counter += 1

    def import_file(self, path: Path | str) -> int:
        """Doc file .txt hoac .md, tu dong dat ten theo stem kem hau to (1) neu trung."""
        file_path = Path(path)
        content = file_path.read_text(encoding="utf-8", errors="replace")
        title = self.get_unique_title(file_path.stem)
        return self.insert(title, content)

    # Aliases
    get_by_id = getById
    get_by_title = getByTitle
    titleExists = title_exists
    getUniqueTitle = get_unique_title
    importFile = import_file

    def list(self, tagName: str | None = None) -> list:
        """Danh sach note, sap xep: pinned DESC, updated_at DESC."""
        if tagName:
            return self.db.query(
                "SELECT n.id, n.title, n.updated_at FROM notes n "
                "JOIN note_tag nt ON nt.note_id = n.id "
                "JOIN tags t ON t.id = nt.tag_id "
                "WHERE t.name=? "
                "ORDER BY n.pinned DESC, n.updated_at DESC, n.id DESC",
                (tagName,),
            )
        return self.db.query(
            "SELECT id, title, updated_at FROM notes "
            "ORDER BY pinned DESC, updated_at DESC, id DESC"
        )

    def searchFTS(self, query: str, tagName: str | None = None) -> list:
        """Tim toan kho qua FTS5, co snippet danh dau tu khoa."""
        match = self._to_match(query)
        if not match:
            return self.list(tagName)
        sql = (
            "SELECT n.id, n.title, n.updated_at, "
            "snippet(notes_fts, 1, char(1), char(2), ' ... ', 14) AS snip "
            "FROM notes_fts f JOIN notes n ON n.id = f.rowid "
        )
        params = [match]
        if tagName:
            sql += (
                "JOIN note_tag nt ON nt.note_id = n.id "
                "JOIN tags t ON t.id = nt.tag_id "
                "WHERE notes_fts MATCH ? AND t.name=?"
            )
            params.append(tagName)
        else:
            sql += "WHERE notes_fts MATCH ?"
        sql += " ORDER BY n.pinned DESC, n.updated_at DESC, n.id DESC"
        return self.db.query(sql, params)

    @staticmethod
    def _to_match(query: str) -> str:
        """Bo dau ky tu dac biet cua FTS5, moi tu tim tien to."""
        terms = []
        for word in query.split():
            clean = word.replace('"', " ").strip()
            if clean:
                terms.append('"%s"*' % clean)
        return " ".join(terms)


class TagDAO:
    """Cac thao tac voi bang tags va bang quan he note_tag."""

    def __init__(self, db: DbManager):
        self.db = db

    def create(self, name: str) -> int:
        self.db.execute("INSERT OR IGNORE INTO tags(name) VALUES(?)", (name,))
        row = self.db.query_one("SELECT id FROM tags WHERE name=?", (name,))
        return row["id"]

    def listAll(self) -> list:
        return self.db.query("SELECT id, name FROM tags ORDER BY name")

    def getByNote(self, note_id: int) -> list:
        return self.db.query(
            "SELECT t.id, t.name FROM tags t "
            "JOIN note_tag nt ON nt.tag_id = t.id "
            "WHERE nt.note_id=? ORDER BY t.name",
            (note_id,),
        )

    def assign(self, note_id: int, tag_id: int):
        self.db.execute(
            "INSERT OR IGNORE INTO note_tag(note_id, tag_id) VALUES(?, ?)",
            (note_id, tag_id),
        )

    def unassign(self, note_id: int, tag_id: int):
        self.db.execute(
            "DELETE FROM note_tag WHERE note_id=? AND tag_id=?",
            (note_id, tag_id),
        )


class SettingsDAO:
    """Bang settings key - value: theme, sync_scroll, last_opened_id."""

    def __init__(self, db: DbManager):
        self.db = db

    def get(self, key: str, default: str = "") -> str:
        row = self.db.query_one("SELECT value FROM settings WHERE key=?", (key,))
        return row["value"] if row is not None else default

    def set(self, key: str, value: str):
        self.db.execute(
            "INSERT INTO settings(key, value) VALUES(?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, value),
        )
