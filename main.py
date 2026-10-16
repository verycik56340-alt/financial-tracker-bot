# main.py
import os
import sys
import asyncio
from pathlib import Path

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from handlers import user
from database import init_db

BASE_DIR = Path(__file__).resolve().parent


async def main():
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
    dp.include_router(user)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
