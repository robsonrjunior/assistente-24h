import asyncio
import os

from dotenv import load_dotenv

from assistant.assistant import answer_question
from assistant.on_first_run import setup_assistant_on_first_run
from database_utils.assistant_database_utils import (
    ensure_assistant_database,
    initialize_assistant_database,
)
from database_utils.calories_database_utils import ensure_calories_database, initialize_calories_database
from database_utils.cron_database_utils import ensure_cron_database, initialize_cron_database
from services import cron
from services import evolution_webhook
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
    setup_assistant_on_first_run()
    ensure_cron_database()
    initialize_cron_database()
    ensure_calories_database()
    initialize_calories_database()

    if _get_assistant_mode() == "TERMINAL_CHAT":
        start_terminal_chat()
        return

    webhook_service = webhook.start
    if _get_assistant_mode() == "WHATSAPP":
        webhook_service = evolution_webhook.start

    await asyncio.gather(
        asyncio.to_thread(cron.start),
        asyncio.to_thread(webhook_service),
    )

if __name__ == "__main__":
    asyncio.run(main())