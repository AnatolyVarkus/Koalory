import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message

from bot.services.analytics_service import gather_analytics
from bot.db import AsyncSessionLocal
from bot.core import settings

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # make sure this is set
bot = Bot(token=settings.TG_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

@dp.message(CommandStart())
async def handle_start(message: Message):
    if message.from_user.id in settings.ALLOWED_USER_IDS:
        async with AsyncSessionLocal() as session:
            report = await gather_analytics(session)
        await message.answer(report)
    else:
        await message.answer("You are not authorized to use this command. \n\nContact @AnatolyVarkus")

def run():
    logging.basicConfig(level=logging.INFO)
    asyncio.run(dp.start_polling(bot))