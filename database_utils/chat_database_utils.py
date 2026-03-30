import os
import sqlite3
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

DB_DIR = Path(os.getenv("DB_PATH", "databases"))
if not DB_DIR.is_absolute():
    DB_DIR = Path(__file__).resolve().parent.parent / DB_DIR

DB_DIR.mkdir(parents=True, exist_ok=True)

CHAT_DB_PATH = DB_DIR / "chat.db"


def ensure_chat_database(db_path: Path = CHAT_DB_PATH) -> None:
    connection = sqlite3.connect(db_path)
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS chat (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.commit()
    finally:
        connection.close()


def save_chat_message(user: str, message: str, db_path: Path = CHAT_DB_PATH) -> None:
    ensure_chat_database(db_path)
    connection = sqlite3.connect(db_path)
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO chat (user, message) VALUES (?, ?)
            """,
            (user, message)
        )
        connection.commit()
    finally:
        connection.close()


def get_last_messages(limit: int = 10, db_path: Path = CHAT_DB_PATH):
    ensure_chat_database(db_path)
    connection = sqlite3.connect(db_path)
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT user, message, created_at FROM chat ORDER BY created_at DESC LIMIT ?
            """,
            (limit,)
        )
        return cursor.fetchall()
    finally:
        connection.close()
