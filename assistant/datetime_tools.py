from datetime import datetime


def check_current_date() -> dict:
    """Returns the current date and time information."""
    now = datetime.now()
    return {
        "iso": now.isoformat(timespec="seconds"),
        "day": now.day,
        "month": now.month,
        "year": now.year,
        "hour": now.hour,
        "minute": now.minute,
        "weekday": now.strftime("%A"),
    }


tools = [
    check_current_date,
]