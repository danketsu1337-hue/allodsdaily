import os
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from aiogram import Bot, Dispatcher, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode
from aiogram.types import Message

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
APP_URL = os.getenv("RENDER_EXTERNAL_URL")  # Render задаёт автоматически

bot = Bot(token=TOKEN)
dp = Dispatcher()


# --- Получение данных с сайта ---
async def fetch_allods_data():
    url = "https://alloder.pro/monitoring/"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            html = await resp.text()
    soup = BeautifulSoup(html, "html.parser")

    servers = []
    table = soup.select_one("table.table")  # первая таблица мониторинга
    if table:
        for row in table.select("tbody tr"):
            cells = [c.text.strip() for c in row.select("td")]
            if len(cells) >= 5:
                servers.append({
                    "server": cells[0],
                    "online": cells[2],
                    "faction": cells[3]
                })

    return servers


# --- Главное меню ---
def main_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="📊 Мониторинг серваров", callback_data="servers")
    kb.button(text="💎 Курсы кристаллов", callback_data="crystals")
    kb.button(text="🎖 Бонусы орденов", callback_data="orders")
    kb.adjust(1)
    return kb.as_markup()


# --- Команды ---
@dp.message(commands=["start"])
async def cmd_start(message: Message):
    await message.answer(
        "Привет! Я бот игры **Аллоды Онлайн** ⚔\nВыбери действие:",
        reply_markup=main_menu(),
        parse_mode=ParseMode.MARKDOWN
    )


# --- Обработчики меню ---
@dp.callback_query(lambda c: c.data == "servers")
async def show_servers(callback: types.CallbackQuery):
    data = await fetch_allods_data()
    text = "📊 <b>Онлайн серверов:</b>\n\n"
    for item in data:
        text += f"{item['server']} — <b>{item['online']}</b> онлайн\n"
    await callback.message.edit_text(text, reply_markup=main_menu(), parse_mode="HTML")


@dp.callback_query(lambda c: c.data == "crystals")
async def show_crystals(callback: types.CallbackQuery):
    # TODO: спарсить курс (аналогично fetch_allods_data)
    await callback.message.edit_text("💎 Курсы кристаллов\nSoon…", reply_markup=main_menu())


@dp.callback_query(lambda c: c.data == "orders")
async def show_orders(callback: types.CallbackQuery):
    # TODO: спарсить бонусы + цвета орденов
    await callback.message.edit_text("🎖 Бонусы орденов\nSoon…", reply_markup=main_menu())


# --- Запуск ---
async def main():
    await dp.start_polling(bot)  # polling — бесплатно и просто на Render


if __name__ == "__main__":
    asyncio.run(main())
