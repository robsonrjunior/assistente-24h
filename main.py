import asyncio
import os

from dotenv import load_dotenv

from assistant.assistant import answer_question
from database_utils.assistant_database_utils import ensure_assistant_database, initialize_assistant_database
from database_utils.calories_database_utils import ensure_calories_database, initialize_calories_database
from database_utils.cron_database_utils import ensure_cron_database, initialize_cron_database
from services import cron
from services import webhook


load_dotenv()


def _get_assistant_mode() -> str:
    return os.getenv("ASSISTANT_MODE", "").strip().upper()


def start_terminal_chat() -> None:
    print("Terminal chat mode enabled. Type 'exit' to quit.")

    while True:
        try:
            user_message = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting terminal chat.")
            break

        if not user_message:
            continue
        if user_message.lower() in {"exit", "quit", "sair"}:
            print("Exiting terminal chat.")
            break

        answer = answer_question(user_message)
        print(f"Assistant: {answer}")

async def main():
    ensure_assistant_database()
    initialize_assistant_database()
    ensure_cron_database()
    initialize_cron_database()
    ensure_calories_database()
    initialize_calories_database()

    if _get_assistant_mode() == "TERMINAL_CHAT":
        start_terminal_chat()
        return

    await asyncio.gather(
        asyncio.to_thread(cron.start),
        asyncio.to_thread(webhook.start),
    )

if __name__ == "__main__":
    asyncio.run(main())