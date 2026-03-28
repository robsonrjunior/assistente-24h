import sqlite3
from pathlib import Path

from database_utils.assistant_database_utils import (
    ASSISTANT_DB_PATH,
    ensure_assistant_database,
    initialize_assistant_database,
)


DB_PATH = ASSISTANT_DB_PATH

def init_db(db_path: Path = DB_PATH) -> None:
    ensure_assistant_database(db_path)
    initialize_assistant_database(db_path)

def initialize_assistant() -> None:
    initialize_assistant_database(DB_PATH)

def update_assistant(
    name="Assistente 24h",
    personality="Calmo, prestativo e eficiente",
    user_name="Usuário",
    user_preferred_name="Usuário",
    language="Portuguese (Brazil)", 
    time_zone="UTC -3",
    current_mood="Neutral"
):
    """
    Updates the assistant's information in the 'assistant' table of the database.
    Args:
        name (str): The assistant's name.
        personality (str): The assistant's personality.
        user_name (str): The user's name.
        user_preferred_name (str): The user's preferred name.
        language (str): The user's preferred language.
        time_zone (str): The user's time zone.
        current_mood (str): The assistant's current mood.
    """
    init_db()
    connnection = sqlite3.connect(DB_PATH)

    try:
        cursor = connnection.cursor()
        cursor.execute(
            """
            UPDATE assistant
            SET name = ?, personality = ?, user_name = ?, user_preferred_name = ?, language = ?, time_zone = ?, current_mood = ?, last_interaction_at = CURRENT_TIMESTAMP
            WHERE rowid = 1
            """,
            (name, personality, user_name, user_preferred_name, language, time_zone, current_mood)
        )
        connnection.commit()
    finally:
        connnection.close()

def get_assistant_info():
    """
    Retrieves the assistant's information from the 'assistant' table in the database.
    Returns:
        dict: A dictionary containing the assistant's information.
    """
    init_db()
    connection = sqlite3.connect(DB_PATH)

    try:
        cursor = connection.cursor()
        cursor.execute("SELECT name, personality, user_name, user_preferred_name, language, time_zone, current_mood FROM assistant WHERE rowid = 1")
        row = cursor.fetchone()

        if row:
            return {
                "name": row[0],
                "personality": row[1],
                "user_name": row[2],
                "user_preferred_name": row[3],
                "language": row[4],
                "time_zone": row[5],
                "current_mood": row[6]
            }
        else:
            return {}
    finally:
        connection.close()

if __name__ == "__main__":
    init_db()
    print(f"Table 'assistant' initialized in {DB_PATH}")
