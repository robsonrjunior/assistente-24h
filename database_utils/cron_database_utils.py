import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

DB_DIR = Path(os.getenv("DB_PATH", "databases"))
if not DB_DIR.is_absolute():
	DB_DIR = Path(__file__).resolve().parent.parent / DB_DIR

DB_DIR.mkdir(parents=True, exist_ok=True)

CRON_DB_PATH = DB_DIR / "cron.db"


def ensure_cron_database(db_path: Path = CRON_DB_PATH) -> None:
	connection = sqlite3.connect(db_path)

	try:
		cursor = connection.cursor()
		cursor.execute(
			"""
			CREATE TABLE IF NOT EXISTS cron (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				name TEXT NOT NULL,
				description TEXT,
				cron_expression TEXT NOT NULL,
				is_active INTEGER NOT NULL DEFAULT 1,
				max_runs INTEGER,
				run_count INTEGER NOT NULL DEFAULT 0,
				created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
				updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
				last_run_at TEXT
			)
			"""
		)
		cursor.execute(
			"""
			CREATE TRIGGER IF NOT EXISTS set_cron_updated_at
			AFTER UPDATE ON cron
			FOR EACH ROW
			BEGIN
				UPDATE cron
				SET updated_at = CURRENT_TIMESTAMP
				WHERE id = NEW.id;
			END;
			"""
		)
		connection.commit()
	finally:
		connection.close()


def initialize_cron_database(db_path: Path = CRON_DB_PATH) -> None:
	ensure_cron_database(db_path)
