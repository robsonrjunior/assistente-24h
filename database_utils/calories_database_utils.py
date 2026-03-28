import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

DB_DIR = Path(os.getenv("DB_PATH", "databases"))
if not DB_DIR.is_absolute():
	DB_DIR = Path(__file__).resolve().parent.parent / DB_DIR

DB_DIR.mkdir(parents=True, exist_ok=True)

CALORIES_DB_PATH = DB_DIR / "calories.db"


def ensure_calories_database(db_path: Path = CALORIES_DB_PATH) -> None:
	connection = sqlite3.connect(db_path)

	try:
		cursor = connection.cursor()
		cursor.execute(
			"""
			CREATE TABLE IF NOT EXISTS daily_calories (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				day INTEGER NOT NULL,
				month INTEGER NOT NULL,
				year INTEGER NOT NULL,
				hour INTEGER NOT NULL,
				minute INTEGER NOT NULL,
				food_name TEXT NOT NULL,
				calories REAL NOT NULL
			)
			"""
		)
		connection.commit()
	finally:
		connection.close()


def initialize_calories_database(db_path: Path = CALORIES_DB_PATH) -> None:
	ensure_calories_database(db_path)
