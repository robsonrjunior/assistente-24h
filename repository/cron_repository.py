import sqlite3
from pathlib import Path
from database_utils.cron_database_utils import CRON_DB_PATH, ensure_cron_database, initialize_cron_database


DB_PATH = CRON_DB_PATH

def init_db(db_path: Path = DB_PATH) -> None:
    ensure_cron_database(db_path)
    initialize_cron_database(db_path)

def add_cron(name: str, cron_expression: str, description: str = "", is_active: bool = True, max_runs: int = None, run_count: int = 0) -> int:
    """
    Adds a new cron job to the 'cron' table.
    Returns:
        int: The id of the newly inserted row.
    """
    init_db()
    connection = sqlite3.connect(DB_PATH)

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO cron (name, description, cron_expression, is_active, max_runs, run_count)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (name, description, cron_expression, int(is_active), max_runs, run_count)
        )
        connection.commit()
        return cursor.lastrowid
    finally:
        connection.close()

def update_cron(id: int, name: str, cron_expression: str, description: str = "", is_active: bool = True, max_runs: int = None, run_count: int = 0) -> None:
    """
    Updates an existing cron job in the 'cron' table.
    """
    init_db()
    connection = sqlite3.connect(DB_PATH)

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            UPDATE cron
            SET name = ?, description = ?, cron_expression = ?, is_active = ?, max_runs = ?, run_count = ?
            WHERE id = ?
            """,
            (name, description, cron_expression, int(is_active), max_runs, run_count, id)
        )
        connection.commit()
    finally:
        connection.close()


def set_cron_active(cron_id: int, is_active: bool) -> None:
    """Atualiza apenas o status ativo de um cron."""
    init_db()
    connection = sqlite3.connect(DB_PATH)

    try:
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE cron SET is_active = ? WHERE id = ?",
            (int(is_active), cron_id)
        )
        connection.commit()
    finally:
        connection.close()

def delete_cron(cron_id: int) -> None:
    """
    Deletes a cron job from the 'cron' table.
    Args:
        cron_id (int): The id of the cron job to delete.
    """
    init_db()
    connection = sqlite3.connect(DB_PATH)

    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM cron WHERE id = ?", (cron_id,))
        connection.commit()
    finally:
        connection.close()

def get_cron(cron_id: int) -> dict | None:
    """
    Retrieves a single cron job by id.
    Returns:
        dict | None: The cron job, or None if not found.
    """
    init_db()
    connection = sqlite3.connect(DB_PATH)

    try:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT id, name, description, cron_expression, is_active, max_runs, run_count, created_at, updated_at, last_run_at FROM cron WHERE id = ?",
            (cron_id,)
        )
        row = cursor.fetchone()

        if row:
            return {"id": row[0], "name": row[1], "description": row[2], "cron_expression": row[3], "is_active": bool(row[4]), "max_runs": row[5], "run_count": row[6], "created_at": row[7], "updated_at": row[8], "last_run_at": row[9]}
        return None
    finally:
        connection.close()

def get_all_crons(only_active: bool = False) -> list[dict]:
    """
    Retrieves all cron jobs from the 'cron' table.
    Args:
        only_active (bool): If True, returns only active cron jobs.
    Returns:
        list[dict]: A list of cron job dicts.
    """
    init_db()
    connection = sqlite3.connect(DB_PATH)

    try:
        cursor = connection.cursor()
        query = "SELECT id, name, description, cron_expression, is_active, max_runs, run_count, created_at, updated_at, last_run_at FROM cron"
        if only_active:
            query += " WHERE is_active = 1"
        cursor.execute(query)
        rows = cursor.fetchall()

        return [
            {"id": row[0], "name": row[1], "description": row[2], "cron_expression": row[3], "is_active": bool(row[4]), "max_runs": row[5], "run_count": row[6], "created_at": row[7], "updated_at": row[8], "last_run_at": row[9]}
            for row in rows
        ]
    finally:
        connection.close()

def increment_cron_run_count(cron_id: int) -> None:
    """
    Increments the 'run_count' field of a cron job by 1.
    Args:
        cron_id (int): The id of the cron job to update.
    """
    init_db()
    connection = sqlite3.connect(DB_PATH)

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            UPDATE cron
            SET run_count = run_count + 1,
                last_run_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (cron_id,)
        )
        connection.commit()
    finally:
        connection.close()

if __name__ == "__main__":
    init_db()
    print(f"Table 'cron' initialized in {DB_PATH}")
