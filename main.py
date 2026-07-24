import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message

from config import TOKEN
from keyboards import menu
from database import *

from aiogram.fsm.context import FSMContext
from states import CreatePlayer
from database import update_player

bot = Bot(TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):

    if not await player_exists(message.from_user.id):
        await create_player(message.from_user.id)

        await message.answer(
            "⚽ Добро пожаловать!\n\n"
            "Напиши имя своего футболиста."
        )

        await state.set_state(CreatePlayer.first_name)
        return

    await message.answer(
        "С возвращением!",
        reply_markup=menu
    )


@dp.message(CreatePlayer.first_name)
async def first_name(message: Message, state: FSMContext):

    await update_player(message.from_user.id, "first_name", message.text)

    await message.answer("Теперь фамилия.")

    await state.set_state(CreatePlayer.last_name)


@dp.message(CreatePlayer.last_name)
async def last_name(message: Message, state: FSMContext):

    await update_player(message.from_user.id, "last_name", message.text)

    await message.answer("Страна?")

    await state.set_state(CreatePlayer.nation)


@dp.message(CreatePlayer.nation)
async def nation(message: Message, state: FSMContext):

    await update_player(message.from_user.id, "nation", message.text)

    await message.answer(
        "Позиция?\n\nGK\nCB\nLB\nRB\nCDM\nCM\nCAM\nLW\nRW\nST"
    )

    await state.set_state(CreatePlayer.position)


@dp.message(CreatePlayer.position)
async def position(message: Message, state: FSMContext):

    await update_player(message.from_user.id, "position", message.text.upper())

    await state.clear()

    await message.answer(
        "✅ Игрок создан!",
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
