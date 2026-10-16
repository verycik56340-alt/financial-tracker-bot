# main.py
import os
import asyncio
from aiogram import Bot, Dispatcher
from handlers import user
from database import init_db
from dotenv import load_dotenv

async def main():
    load_dotenv()
    init_db()
    bot = Bot(token=os.environ["BOT_TOKEN"])
    dp = Dispatcher()
    dp.include_router(user)
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass