import sqlite3

from apscheduler.triggers.cron import CronTrigger

from database_utils.cron_database_utils import CRON_DB_PATH, ensure_cron_database, initialize_cron_database


def _connect() -> sqlite3.Connection:
    ensure_cron_database(CRON_DB_PATH)
    initialize_cron_database(CRON_DB_PATH)
    return sqlite3.connect(CRON_DB_PATH)


def get_cron_record(cron_id: int) -> dict | None:
    connection = _connect()

    try:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT id, name, description, cron_expression, is_active, max_runs, run_count, created_at, updated_at, last_run_at FROM cron WHERE id = ?",
            (cron_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return {"id": row[0], "name": row[1], "description": row[2], "cron_expression": row[3], "is_active": bool(row[4]), "max_runs": row[5], "run_count": row[6], "created_at": row[7], "updated_at": row[8], "last_run_at": row[9]}
    finally:
        connection.close()


def get_all_cron_records(only_active: bool = False) -> list[dict]:
    connection = _connect()

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


def set_cron_active_status(cron_id: int, is_active: bool) -> None:
    connection = _connect()

    try:
        cursor = connection.cursor()
        cursor.execute("UPDATE cron SET is_active = ? WHERE id = ?", (int(is_active), cron_id))
        connection.commit()
    finally:
        connection.close()


def increment_cron_run_count(cron_id: int) -> None:
    connection = _connect()

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            UPDATE cron
            SET run_count = run_count + 1,
                last_run_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (cron_id,),
        )
        connection.commit()
    finally:
        connection.close()


def add_cron(
    name: str,
    cron_expression: str,
    description: str = "",
    is_active: bool = True,
    max_runs: int | None = None,
) -> dict:
    """Adds a new scheduled task."""
    if not name or not name.strip():
        raise ValueError("name não pode estar vazio")
    CronTrigger.from_crontab(cron_expression)

    connection = _connect()

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO cron (name, description, cron_expression, is_active, max_runs, run_count)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (name.strip(), description, cron_expression, int(is_active), max_runs, 0),
        )
        connection.commit()
        cron_id = cursor.lastrowid
    finally:
        connection.close()

    return {
        "message": "Cron criado com sucesso",
        "id": cron_id,
        "name": name.strip(),
        "cron_expression": cron_expression,
        "is_active": is_active,
    }


def remove_cron(cron_id: int) -> dict:
    """Removes a scheduled task by id."""
    existing = get_cron_record(cron_id)
    if not existing:
        raise ValueError(f"Cron {cron_id} não encontrado")

    connection = _connect()

    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM cron WHERE id = ?", (cron_id,))
        connection.commit()
    finally:
        connection.close()

    return {
        "message": "Cron removido com sucesso",
        "id": cron_id,
        "name": existing["name"],
    }


def update_cron(
    cron_id: int,
    name: str | None = None,
    cron_expression: str | None = None,
    description: str | None = None,
    is_active: bool | None = None,
    max_runs: int | None = None,
    run_count: int | None = None,
) -> dict:
    """Updates an existing scheduled task."""
    existing = get_cron_record(cron_id)
    if not existing:
        raise ValueError(f"Cron {cron_id} não encontrado")

    updated_name = existing["name"] if name is None else name.strip()
    updated_description = existing["description"] if description is None else description
    updated_expression = existing["cron_expression"] if cron_expression is None else cron_expression
    updated_is_active = existing["is_active"] if is_active is None else is_active
    updated_max_runs = existing["max_runs"] if max_runs is None else max_runs
    updated_run_count = existing["run_count"] if run_count is None else run_count

    if not updated_name:
        raise ValueError("name não pode estar vazio")
    CronTrigger.from_crontab(updated_expression)

    connection = _connect()

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            UPDATE cron
            SET name = ?, description = ?, cron_expression = ?, is_active = ?, max_runs = ?, run_count = ?
            WHERE id = ?
            """,
            (updated_name, updated_description, updated_expression, int(updated_is_active), updated_max_runs, updated_run_count, cron_id),
        )
        connection.commit()
    finally:
        connection.close()

    return {
        "message": "Cron atualizado com sucesso",
        "id": cron_id,
        "name": updated_name,
        "cron_expression": updated_expression,
        "is_active": updated_is_active,
        "max_runs": updated_max_runs,
        "run_count": updated_run_count,
    }


tools = [
    add_cron,
    remove_cron,
    update_cron,
]