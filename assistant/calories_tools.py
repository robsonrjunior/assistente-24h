import sqlite3
from datetime import datetime

from database_utils.calories_database_utils import CALORIES_DB_PATH, ensure_calories_database, initialize_calories_database

def _validate_date(day: int, month: int, year: int) -> None:
    datetime(year=year, month=month, day=day)


def _validate_time(hour: int, minute: int) -> None:
    if not 0 <= hour <= 23:
        raise ValueError("hour deve estar entre 0 e 23")
    if not 0 <= minute <= 59:
        raise ValueError("minute deve estar entre 0 e 59")


def _connect() -> sqlite3.Connection:
    ensure_calories_database(CALORIES_DB_PATH)
    initialize_calories_database(CALORIES_DB_PATH)
    return sqlite3.connect(CALORIES_DB_PATH)


def _get_all_entries() -> list[dict]:
    connection = _connect()

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


def _get_entries_by_date(day: int, month: int, year: int) -> list[dict]:
    connection = _connect()

    try:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT id, day, month, year, hour, minute, food_name, calories FROM daily_calories WHERE day = ? AND month = ? AND year = ? ORDER BY hour, minute",
            (day, month, year),
        )
        rows = cursor.fetchall()
        return [
            {"id": row[0], "day": row[1], "month": row[2], "year": row[3], "hour": row[4], "minute": row[5], "food_name": row[6], "calories": row[7]}
            for row in rows
        ]
    finally:
        connection.close()


def _insert_entry(food_name: str, calories: float, day: int, month: int, year: int, hour: int, minute: int) -> int:
    connection = _connect()

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO daily_calories (day, month, year, hour, minute, food_name, calories)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (day, month, year, hour, minute, food_name, calories),
        )
        connection.commit()
        return cursor.lastrowid
    finally:
        connection.close()


def _update_entry(entry_id: int, food_name: str, calories: float, day: int, month: int, year: int, hour: int, minute: int) -> None:
    connection = _connect()

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            UPDATE daily_calories
            SET day = ?, month = ?, year = ?, hour = ?, minute = ?, food_name = ?, calories = ?
            WHERE id = ?
            """,
            (day, month, year, hour, minute, food_name, calories, entry_id),
        )
        connection.commit()
    finally:
        connection.close()


def _get_calorie_entry(entry_id: int) -> dict | None:
    for entry in _get_all_entries():
        if entry["id"] == entry_id:
            return entry
    return None


def add_calories(
    food_name: str,
    calories: float,
    day: int | None = None,
    month: int | None = None,
    year: int | None = None,
    hour: int | None = None,
    minute: int | None = None,
) -> dict:
    """Adds a calorie entry for a food item."""
    if not food_name or not food_name.strip():
        raise ValueError("food_name não pode estar vazio")
    if calories < 0:
        raise ValueError("calories não pode ser negativo")

    now = datetime.now()
    day = day if day is not None else now.day
    month = month if month is not None else now.month
    year = year if year is not None else now.year
    hour = hour if hour is not None else now.hour
    minute = minute if minute is not None else now.minute

    _validate_date(day=day, month=month, year=year)
    _validate_time(hour=hour, minute=minute)

    entry_id = _insert_entry(food_name=food_name.strip(), calories=calories, day=day, month=month, year=year, hour=hour, minute=minute)

    return {
        "message": "Caloria adicionada com sucesso",
        "id": entry_id,
        "food_name": food_name.strip(),
        "calories": calories,
        "date": f"{year:04d}-{month:02d}-{day:02d}",
        "time": f"{hour:02d}:{minute:02d}",
    }


def get_calories() -> dict:
    """Returns all calorie entries and the accumulated total."""
    entries = _get_all_entries()
    total = sum(entry["calories"] for entry in entries)

    return {
        "count": len(entries),
        "total_calories": total,
        "entries": entries,
    }


def get_calories_by_date(day: int, month: int, year: int) -> dict:
    """Returns calories for a specific date."""
    _validate_date(day=day, month=month, year=year)

    entries = _get_entries_by_date(day=day, month=month, year=year)
    total = sum(entry["calories"] for entry in entries)

    return {
        "date": f"{year:04d}-{month:02d}-{day:02d}",
        "count": len(entries),
        "total_calories": total,
        "entries": entries,
    }


def update_calories(
    entry_id: int,
    food_name: str | None = None,
    calories: float | None = None,
    day: int | None = None,
    month: int | None = None,
    year: int | None = None,
    hour: int | None = None,
    minute: int | None = None,
) -> dict:
    """Updates an existing calorie entry while preserving its identifier."""
    existing = _get_calorie_entry(entry_id)
    if not existing:
        raise ValueError(f"Registro de calorias {entry_id} não encontrado")

    updated_food_name = existing["food_name"] if food_name is None else food_name.strip()
    updated_calories = existing["calories"] if calories is None else calories
    updated_day = existing["day"] if day is None else day
    updated_month = existing["month"] if month is None else month
    updated_year = existing["year"] if year is None else year
    updated_hour = existing["hour"] if hour is None else hour
    updated_minute = existing["minute"] if minute is None else minute

    if not updated_food_name:
        raise ValueError("food_name não pode estar vazio")
    if updated_calories < 0:
        raise ValueError("calories não pode ser negativo")

    _validate_date(day=updated_day, month=updated_month, year=updated_year)
    _validate_time(hour=updated_hour, minute=updated_minute)

    _update_entry(entry_id=entry_id, food_name=updated_food_name, calories=updated_calories, day=updated_day, month=updated_month, year=updated_year, hour=updated_hour, minute=updated_minute)

    return {
        "message": "Registro de calorias atualizado com sucesso",
        "id": entry_id,
        "food_name": updated_food_name,
        "calories": updated_calories,
        "date": f"{updated_year:04d}-{updated_month:02d}-{updated_day:02d}",
        "time": f"{updated_hour:02d}:{updated_minute:02d}",
    }

tools = [
    add_calories,
    get_calories,
    get_calories_by_date,
    update_calories,
]