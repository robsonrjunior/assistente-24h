from database_utils.chat_database_utils import get_last_messages


def get_history(limit: int = 5):
    """
    Returns the last `limit` chat messages as a list of dicts.
    Each dict contains: user, message, created_at.
    """
    rows = get_last_messages(limit=limit)
    # Reverse to chronological order (oldest first)
    rows = list(reversed(rows))
    return [
        {"user": user, "message": message, "created_at": created_at}
        for user, message, created_at in rows
    ]
