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


def has_assistant_configuration(db_path: Path = ASSISTANT_DB_PATH) -> bool:
	ensure_assistant_database(db_path)
	connection = sqlite3.connect(db_path)

	try:
		cursor = connection.cursor()
		cursor.execute("SELECT 1 FROM assistant LIMIT 1")
		return cursor.fetchone() is not None
	finally:
		connection.close()


def save_initial_assistant_configuration(
	configuration: dict,
	db_path: Path = ASSISTANT_DB_PATH,
) -> None:
	ensure_assistant_database(db_path)
	connection = sqlite3.connect(db_path)

	try:
		cursor = connection.cursor()
		cursor.execute("SELECT rowid FROM assistant ORDER BY rowid ASC LIMIT 1")
		existing_row = cursor.fetchone()

		values = (
			configuration["name"],
			configuration["personality"],
			configuration["user_name"],
			configuration["user_preferred_name"],
			configuration["language"],
			configuration["time_zone"],
			configuration["current_mood"],
		)

		if existing_row:
			cursor.execute(
				"""
				UPDATE assistant
				SET name = ?, personality = ?, user_name = ?, user_preferred_name = ?, language = ?, time_zone = ?, current_mood = ?
				WHERE rowid = ?
				""",
				(*values, existing_row[0]),
			)
		else:
			cursor.execute(
				"""
				INSERT INTO assistant (name, personality, user_name, user_preferred_name, language, time_zone, current_mood)
				VALUES (?, ?, ?, ?, ?, ?, ?)
				""",
				values,
			)

		connection.commit()
	finally:
		connection.close()
