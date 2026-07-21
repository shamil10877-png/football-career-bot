import asyncio
import json
import os
import random

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

# ⚠️ ТОКЕН - вставь свой!
TOKEN = "8849485512:AAEhvLOhm7rLwmXoalUx1Wnp5QKCSbFw7O4"

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher(storage=MemoryStorage())

# Папка для сохранений
SAVE_DIR = "players"
os.makedirs(SAVE_DIR, exist_ok=True)

# ── СОХРАНЕНИЕ ──────────────────────────────────────────

def save_file(user_id: int) -> str:
    return os.path.join(SAVE_DIR, f"{user_id}.json")

def save(user_id: int, data: dict):
    with open(save_file(user_id), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load(user_id: int) -> dict | None:
    path = save_file(user_id)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

# ── /start ──────────────────────────────────────────────────

@dp.message(Command("start"))
async def start(message: Message):
    await message.answer("✅ Бот РАБОТАЕТ!\n\nНапиши /create чтобы начать.")

# ── /create ──────────────────────────────────────────────────

@dp.message(Command("create"))
async def create(message: Message):
    args = message.text.split()
    if len(args) < 2:
        await message.answer("❌ Напиши: /create Имя")
        return
    
    name = " ".join(args[1:])
    
    data = {
        "name": name,
        "rating": 60,
        "money": 0,
        "created": True
    }
    
    save(message.from_user.id, data)
    await message.answer(f"✅ Создан игрок: {name}\n⭐ Рейтинг: 60")

# ── /profile ──────────────────────────────────────────────────

@dp.message(Command("profile"))
async def profile(message: Message):
    data = load(message.from_user.id)
    if not data or not data.get("created"):
        await message.answer("❌ Сначала создай игрока через /create")
        return
    
    await message.answer(
        f"👤 Игрок: {data['name']}\n"
        f"⭐ Рейтинг: {data['rating']}\n"
        f"💰 Денег: {data['money']}"
    )

# ── /train ──────────────────────────────────────────────────

@dp.message(Command("train"))
async def train(message: Message):
    data = load(message.from_user.id)
    if not data or not data.get("created"):
        await message.answer("❌ Сначала создай игрока через /create")
        return
    
    gain = random.randint(1, 3)
    data['rating'] = min(99, data['rating'] + gain)
    save(message.from_user.id, data)
    
    await message.answer(f"🏋️ Тренировка!\n⭐ Рейтинг +{gain}\n📈 Теперь: {data['rating']}")

# ── /match ──────────────────────────────────────────────────

@dp.message(Command("match"))
async def match(message: Message):
    data = load(message.from_user.id)
    if not data or not data.get("created"):
        await message.answer("❌ Сначала создай игрока через /create")
        return
    
    goals = random.randint(0, 2)
    money = goals * 1000
    
    data['money'] += money
    save(message.from_user.id, data)
    
    await message.answer(f"⚽ Матч!\nГолы: {goals}\n💰 Заработано: {money}")

# ── /help ──────────────────────────────────────────────────

@dp.message(Command("help"))
async def help(message: Message):
    await message.answer(
        "📋 Команды:\n"
        "/start — запуск\n"
        "/create Имя — создать игрока\n"
        "/profile — профиль\n"
        "/train — тренировка\n"
        "/match — матч\n"
        "/help — помощь"
    )

# ── НЕИЗВЕСТНЫЕ КОМАНДЫ ──────────────────────────────────

@dp.message(F.text.startswith("/"))
async def unknown(message: Message):
    await message.answer("❌ Неизвестная команда. Напиши /help")

# ── ЗАПУСК ──────────────────────────────────────────────────

async def main():
    print("🚀 Бот запущен!")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
