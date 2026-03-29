import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

DB_DIR = Path(os.getenv("DB_PATH", "databases"))
if not DB_DIR.is_absolute():
    DB_DIR = Path(__file__).resolve().parent.parent / DB_DIR

DB_DIR.mkdir(parents=True, exist_ok=True)

EVOLUTION_DB_PATH = DB_DIR / "evolution.db"


def ensure_evolution_database(db_path: Path = EVOLUTION_DB_PATH) -> None:
    connection = sqlite3.connect(db_path)

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS processed_messages (
                message_key TEXT PRIMARY KEY,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.commit()
    finally:
        connection.close()


def register_processed_message(message_key: str, db_path: Path = EVOLUTION_DB_PATH) -> bool:
    """Returns True when message was newly registered, False when it already exists."""
    ensure_evolution_database(db_path)
    connection = sqlite3.connect(db_path)

    try:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO processed_messages (message_key) VALUES (?)",
            (message_key,),
        )
        connection.commit()
        return cursor.rowcount == 1
    finally:
        connection.close()


def cleanup_processed_messages(max_age_days: int = 30, db_path: Path = EVOLUTION_DB_PATH) -> None:
    ensure_evolution_database(db_path)
    connection = sqlite3.connect(db_path)

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            DELETE FROM processed_messages
            WHERE created_at < datetime('now', ?)
            """,
            (f"-{max_age_days} days",),
        )
        connection.commit()
    finally:
        connection.close()
