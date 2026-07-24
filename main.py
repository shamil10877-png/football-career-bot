import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message

from config import TOKEN
from keyboards import menu
from database import *

bot = Bot(TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message):

    if not await player_exists(message.from_user.id):
        await create_player(message.from_user.id)

    await message.answer(
        "⚽ Добро пожаловать в Footballer Career!\n\n"
        "Твоя карьера начинается прямо сейчас.",
        reply_markup=menu
    )


@dp.message(F.text == "👤 Профиль")
async def profile(message: Message):

    import aiosqlite

    async with aiosqlite.connect(DB) as db:

        cur = await db.execute(
            "SELECT * FROM players WHERE user_id=?",
            (message.from_user.id,)
        )

        p = await cur.fetchone()

    await message.answer(
f"""
👤 Игрок

Имя: {p[1]} {p[2]}

Возраст: {p[3]}

🌍 Страна: {p[4]}

⚽ Позиция: {p[5]}

🏟 Клуб: {p[6]}

⭐ Рейтинг: {p[7]}
📈 Потенциал: {p[8]}

💰 Деньги: €{p[9]}
💵 Зарплата: €{p[10]}

⚽ Матчи: {p[11]}
🥅 Голы: {p[12]}
🎯 Ассисты: {p[13]}

🏆 Трофеи: {p[14]}

⚡ Энергия: {p[15]}%

😊 Мораль: {p[16]}%
"""
    )


async def main():
    await init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
