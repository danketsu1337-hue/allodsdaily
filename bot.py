import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from config import BOT_TOKEN, WEBHOOK_URL, WEBHOOK_PATH
from utils import fetch_monitoring


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Привет! Я Аллоды мониторинг бот\n\n"
        "Команды:\n"
        "/servers — статус серверов"
    )


@dp.message(Command("servers"))
async def cmd_servers(message: types.Message):
    data = await fetch_monitoring()
    await message.answer(f"🛡 Серверы:\n\n{data}")


async def on_startup(bot: Bot):
    await bot.set_webhook(WEBHOOK_URL)


async def on_shutdown(bot: Bot):
    await bot.delete_webhook()


def main():
    app = web.Application()

    SimpleRequestHandler(
        dispatcher=dp,
        bot=bot
    ).register(app, path=WEBHOOK_PATH)

    setup_application(app, dp, bot=bot)

    return app


if __name__ == "__main__":
    web.run_app(
        main(),
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8080))
    )
