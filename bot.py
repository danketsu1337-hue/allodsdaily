import os
import asyncio
import aiohttp
import time
from bs4 import BeautifulSoup
from aiogram import Bot, Dispatcher, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode
from aiogram.types import Message

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

CACHE = {
    "servers": None,
    "crystals": None,
    "orders": None,
    "timestamp": 0
}

CACHE_TTL = 60  # кэш 60 сек


async def fetch_page(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.text()


async def fetch_allods_data():
    # Проверяем кэш
    if CACHE["servers"] and (time.time() - CACHE["timestamp"] < CACHE_TTL):
        return CACHE["servers"]

    html = await fetch_page("https://alloder.pro/monitoring/")
    soup = BeautifulSoup(html, "html.parser")

    servers = []
    table = soup.select_one("table.table")
    if table:
        for row in table.select("tbody tr"):
            cells = [c.text.strip() for c in row.select("td")]
            if len(cells) >= 5:
                servers.append({
                    "server": cells[0],
                    "online": cells[2],
                    "faction": cells[3]
                })

    CACHE["servers"] = servers
    CACHE["timestamp"] = time.time()
    return servers


async def fetch_crystals():
    if CACHE["crystals"] and (time.time() - CACHE["timestamp"] < CACHE_TTL):
        return CACHE["crystals"]

    html = await fetch_page("https://alloder.pro/monitoring/")
    soup = BeautifulSoup(html, "html.parser")

    spans = soup.select("div.total-price span")
    buy = spans[0].text.strip() if len(spans) >= 1 else "?"
    sell = spans[1].text.strip() if len(spans) >= 2 else "?"

    result = {"buy": buy, "sell": sell}
    CACHE["crystals"] = result
    return result


async def fetch_orders():
    if CACHE["orders"] and (time.time() - CACHE["timestamp"] < CACHE_TTL):
        return CACHE["orders"]

    html = await fetch_page("https://alloder.pro/monitoring/")
    soup = BeautifulSoup(html, "html.parser")

    orders = []
    rows = soup.select("div.order-bonuses .bonus-item")
    for row in rows:
        name = row.select_one(".bonus-title").text.strip()
        pct = row.select_one(".bonus-value").text.strip()
        color = row.get("style", "").replace("background:", "").strip()
        orders.append({"name": name, "bonus": pct, "color": color})

    CACHE["orders"] = orders
    return orders


def main_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="📊 Онлайн серверов", callback_data="servers")
    kb.button(text="💎 Курсы кристаллов", callback_data="crystals")
    kb.button(text="🎖 Бонусы орденов", callback_data="orders")
    kb.adjust(1)
    return kb.as_markup()


@dp.message(commands=["start"])
async def cmd_start(message: Message):
    await message.answer(
        "Привет! Я бот по игре **Аллоды Онлайн** ⚔\nВыбирай категорию👇",
        reply_markup=main_menu(),
        parse_mode=ParseMode.MARKDOWN
    )


@dp.callback_query(lambda c: c.data == "servers")
async def show_servers(callback: types.CallbackQuery):
    data = await fetch_allods_data()
    text = "📊 <b>Онлайн серверов</b>\n\n"
    for item in data:
        text += f"• <b>{item['server']}</b> — {item['online']} игроков\n"
    await callback.message.edit_text(text, reply_markup=main_menu(), parse_mode="HTML")


@dp.callback_query(lambda c: c.data == "crystals")
async def show_crystals(callback: types.CallbackQuery):
    data = await fetch_crystals()
    text = (
        "💎 <b>Курс кристаллов</b>\n\n"
        f"🔹 Покупка: <b>{data['buy']}</b>\n"
        f"🔸 Продажа: <b>{data['sell']}</b>\n"
    )
    await callback.message.edit_text(text, reply_markup=main_menu(), parse_mode="HTML")


@dp.callback_query(lambda c: c.data == "orders")
async def show_orders(callback: types.CallbackQuery):
    data = await fetch_orders()
    text = "🎖 <b>Бонусы орденов</b>\n\n"
    for o in data:
        text += f"• <b>{o['name']}</b> — {o['bonus']} ({o['color']})\n"
    await callback.message.edit_text(text, reply_markup=main_menu(), parse_mode="HTML")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
