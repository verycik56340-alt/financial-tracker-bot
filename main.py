# main.py
import asyncio
import logging
import os
import sys
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.types import ErrorEvent, Message
from dotenv import load_dotenv

from handlers import user
from database import init_db

BASE_DIR = Path(__file__).resolve().parent


async def on_error(event: ErrorEvent):
    logging.error(
        "Unhandled exception while processing update #%s",
        event.update.update_id,
        exc_info=event.exception,
    )

    message = None
    if isinstance(event.update.message, Message):
        message = event.update.message
    elif isinstance(getattr(event.update.callback_query, "message", None), Message):
        message = event.update.callback_query.message

    if message is not None:
        try:
            await message.answer("Something went wrong, try again")
        except Exception:
            logging.exception("Failed to notify the user about the error")


async def main():
    logging.basicConfig(level=logging.INFO)
    load_dotenv(BASE_DIR / ".env")
    token = os.environ.get("BOT_TOKEN")
    if not token:
        sys.exit(
            "BOT_TOKEN is not set. "
            "Add it to the .env file next to main.py (see .env.example)."
        )
    init_db()
    bot = Bot(token=token)
    dp = Dispatcher()
    dp.errors.register(on_error)
    dp.include_router(user)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
