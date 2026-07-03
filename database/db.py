"""
Challenge Arena - Database Setup
SQLite database initialization and connection management.
"""

import sqlite3
import os
from pathlib import Path

DB_DIR = Path(__file__).parent.parent / "data"
DB_PATH = DB_DIR / "challenge_arena.db"


def get_db_path():
    """Get the database file path."""
    return str(DB_PATH)


def get_connection():
    """Get a new database connection."""
    os.makedirs(str(DB_DIR), exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Initialize the database schema."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            role TEXT NOT NULL DEFAULT 'student' CHECK(role IN ('admin', 'student')),
            cohort TEXT DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS challenges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description_md TEXT DEFAULT '',
            type TEXT NOT NULL CHECK(type IN ('classification', 'regression', 'rag', 'llm', 'code_challenge')),
            primary_metric TEXT NOT NULL DEFAULT 'accuracy',
            is_open INTEGER DEFAULT 0,
            deadline TIMESTAMP DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS challenge_resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            challenge_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            storage_path TEXT NOT NULL,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (challenge_id) REFERENCES challenges(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS ground_truths (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            challenge_id INTEGER NOT NULL UNIQUE,
            storage_path TEXT NOT NULL,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (challenge_id) REFERENCES challenges(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            challenge_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            storage_path TEXT NOT NULL,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active_for_ranking INTEGER DEFAULT 1,
            metrics_json TEXT DEFAULT NULL,
            primary_score REAL DEFAULT NULL,
            status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'scored', 'error')),
            error_message TEXT DEFAULT NULL,
            manual_score REAL DEFAULT NULL,
            manual_feedback TEXT DEFAULT NULL,
            FOREIGN KEY (challenge_id) REFERENCES challenges(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS submission_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            submission_id INTEGER NOT NULL,
            challenge_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            storage_path TEXT NOT NULL,
            uploaded_at TIMESTAMP NOT NULL,
            metrics_json TEXT DEFAULT NULL,
            primary_score REAL DEFAULT NULL,
            status TEXT DEFAULT 'pending',
            FOREIGN KEY (challenge_id) REFERENCES challenges(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_submissions_active ON submissions(challenge_id, user_id, is_active_for_ranking);
        CREATE INDEX IF NOT EXISTS idx_submissions_challenge ON submissions(challenge_id);
        CREATE INDEX IF NOT EXISTS idx_submissions_user ON submissions(user_id);
        CREATE INDEX IF NOT EXISTS idx_challenges_open ON challenges(is_open);
    """)

    conn.commit()
    conn.close()
    print(f"Database initialized at: {DB_PATH}")