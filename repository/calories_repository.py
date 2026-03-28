import sqlite3
from pathlib import Path
from dotenv import load_dotenv

from database_utils.calories_database_utils import (
    CALORIES_DB_PATH,
    ensure_calories_database,
    initialize_calories_database,
)

from datetime import datetime

load_dotenv()

DB_PATH = CALORIES_DB_PATH

def init_db(db_path: Path = DB_PATH) -> None:
    ensure_calories_database(db_path)
    initialize_calories_database(db_path)

def add_entry(food_name: str, calories: float, day: int = None, month: int = None, year: int = None, hour: int = None, minute: int = None) -> int:
    now = datetime.now()
    day = day if day is not None else now.day
    month = month if month is not None else now.month
    year = year if year is not None else now.year
    hour = hour if hour is not None else now.hour
    minute = minute if minute is not None else now.minute

    init_db()
    connection = sqlite3.connect(DB_PATH)

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO daily_calories (day, month, year, hour, minute, food_name, calories)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (day, month, year, hour, minute, food_name, calories)
        )
        connection.commit()
        return cursor.lastrowid
    finally:
        connection.close()

def get_entries_by_date(day: int, month: int, year: int) -> list[dict]:
    init_db()
    connection = sqlite3.connect(DB_PATH)

    try:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT id, day, month, year, hour, minute, food_name, calories FROM daily_calories WHERE day = ? AND month = ? AND year = ? ORDER BY hour, minute",
            (day, month, year)
        )
        rows = cursor.fetchall()

        return [
            {"id": row[0], "day": row[1], "month": row[2], "year": row[3], "hour": row[4], "minute": row[5], "food_name": row[6], "calories": row[7]}
            for row in rows
        ]
    finally:
        connection.close()

def get_all_entries() -> list[dict]:
    init_db()
    connection = sqlite3.connect(DB_PATH)

    try:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT id, day, month, year, hour, minute, food_name, calories FROM daily_calories ORDER BY year, month, day, hour, minute"
        )
        rows = cursor.fetchall()

        return [
            {"id": row[0], "day": row[1], "month": row[2], "year": row[3], "hour": row[4], "minute": row[5], "food_name": row[6], "calories": row[7]}
            for row in rows
        ]
    finally:
        connection.close()

def delete_entry(entry_id: int) -> None:
    init_db()
    connection = sqlite3.connect(DB_PATH)

    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM daily_calories WHERE id = ?", (entry_id,))
        connection.commit()
    finally:
        connection.close()


def update_entry(
    entry_id: int,
    food_name: str,
    calories: float,
    day: int,
    month: int,
    year: int,
    hour: int,
    minute: int,
) -> None:
    init_db()
    connection = sqlite3.connect(DB_PATH)

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            UPDATE daily_calories
            SET day = ?, month = ?, year = ?, hour = ?, minute = ?, food_name = ?, calories = ?
            WHERE id = ?
            """,
            (day, month, year, hour, minute, food_name, calories, entry_id)
        )
        connection.commit()
    finally:
        connection.close()
