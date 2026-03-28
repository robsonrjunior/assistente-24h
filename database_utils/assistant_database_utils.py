import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

DB_DIR = Path(os.getenv("DB_PATH", "databases"))
if not DB_DIR.is_absolute():
	DB_DIR = Path(__file__).resolve().parent.parent / DB_DIR

DB_DIR.mkdir(parents=True, exist_ok=True)

ASSISTANT_DB_PATH = DB_DIR / "assistant.db"

DEFAULT_ASSISTANT_CONFIGURATION = {
	"name": "Assistente 24h",
	"personality": "Calmo, prestativo e eficiente",
	"user_name": "Usuário",
	"user_preferred_name": "Usuário",
	"language": "Portuguese (Brazil)",
	"time_zone": "UTC -3",
	"current_mood": "Neutral",
}


def ensure_assistant_database(db_path: Path = ASSISTANT_DB_PATH) -> None:
	connection = sqlite3.connect(db_path)

	try:
		cursor = connection.cursor()
		cursor.execute(
			"""
			CREATE TABLE IF NOT EXISTS assistant (
				name TEXT NOT NULL,
				personality TEXT,
				user_name TEXT,
				user_preferred_name TEXT,
				language TEXT,
				time_zone TEXT,
				created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
				updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
				last_interaction_at TEXT,
				current_mood TEXT,
				first_interaction_at TEXT
			)
			"""
		)
		cursor.execute(
			"""
			CREATE TRIGGER IF NOT EXISTS set_assistant_updated_at
			AFTER UPDATE ON assistant
			FOR EACH ROW
			BEGIN
				UPDATE assistant
				SET updated_at = CURRENT_TIMESTAMP
				WHERE rowid = NEW.rowid;
			END;
			"""
		)
		connection.commit()
	finally:
		connection.close()


def initialize_assistant_database(db_path: Path = ASSISTANT_DB_PATH) -> None:
	ensure_assistant_database(db_path)
	connection = sqlite3.connect(db_path)

	try:
		cursor = connection.cursor()
		cursor.execute("SELECT COUNT(*) FROM assistant")
		count = cursor.fetchone()[0]

		if count == 0:
			cursor.execute(
				"""
				INSERT INTO assistant (name, personality, user_name, user_preferred_name, language, time_zone, current_mood)
				VALUES (?, ?, ?, ?, ?, ?, ?)
				""",
				(
					DEFAULT_ASSISTANT_CONFIGURATION["name"],
					DEFAULT_ASSISTANT_CONFIGURATION["personality"],
					DEFAULT_ASSISTANT_CONFIGURATION["user_name"],
					DEFAULT_ASSISTANT_CONFIGURATION["user_preferred_name"],
					DEFAULT_ASSISTANT_CONFIGURATION["language"],
					DEFAULT_ASSISTANT_CONFIGURATION["time_zone"],
					DEFAULT_ASSISTANT_CONFIGURATION["current_mood"],
				),
			)
			connection.commit()
	finally:
		connection.close()
