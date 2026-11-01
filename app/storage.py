"""SQLite data storage: every run is logged (inputs, outputs, status, warnings)."""
import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone

from . import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    source TEXT NOT NULL,
    brief TEXT NOT NULL,
    provider TEXT,
    status TEXT NOT NULL,
    attempts INTEGER DEFAULT 0,
    deck_title TEXT,
    n_slides INTEGER,
    deck_json TEXT,
    pptx_path TEXT,
    warnings TEXT,
    error TEXT
);
"""


@contextmanager
def _conn(path=None):
    con = sqlite3.connect(path or config.DB_PATH)
    con.row_factory = sqlite3.Row
    try:
        con.executescript(SCHEMA)
        yield con
        con.commit()
    finally:
        con.close()


def save_run(*, source, brief, provider, status, attempts=0, deck=None, pptx_path=None,
             warnings=None, error=None, db_path=None) -> int:
    with _conn(db_path) as con:
        cur = con.execute(
            "INSERT INTO runs (created_at, source, brief, provider, status, attempts, deck_title,"
            " n_slides, deck_json, pptx_path, warnings, error) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                datetime.now(timezone.utc).isoformat(timespec="seconds"),
                source, brief, provider, status, attempts,
                deck.deck_title if deck else None,
                len(deck.slides) if deck else None,
                deck.model_dump_json() if deck else None,
                str(pptx_path) if pptx_path else None,
                json.dumps(warnings or []),
                error,
            ),
        )
        return cur.lastrowid


def list_runs(limit=50, db_path=None):
    with _conn(db_path) as con:
        return [dict(r) for r in con.execute("SELECT * FROM runs ORDER BY id DESC LIMIT ?", (limit,))]


def stats(db_path=None):
    with _conn(db_path) as con:
        rows = con.execute("SELECT status, COUNT(*) c FROM runs GROUP BY status").fetchall()
        return {r["status"]: r["c"] for r in rows}
