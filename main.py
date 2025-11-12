import os

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from dotenv import load_dotenv
from telethon import TelegramClient

from tg_bot import main

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_ID = int(os.getenv("API_ID")) # Ваш API ID из my.telegram.org
API_HASH = os.getenv("API_HASH")  # Ваш API Hash
SESSION_NAME = f'session/session_name.session'

proxy = "http://qWD41r:JdCPrA@196.19.121.132:8000"
session = AiohttpSession(
    proxy=proxy
)
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    session=session
)

# Инициализация Telethon клиента
client = TelegramClient(SESSION_NAME, API_ID, API_HASH, system_version="4.16.30-vxCUSTOM")


if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(main(client_bot=client, bot=bot))