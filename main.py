import asyncio
import json
import os
import random

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8849485512:AAEhvLOhm7rLwmXoalUx1Wnp5QKCSbFw7O4"

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher(storage=MemoryStorage())

SAVE_DIR = "players"
os.makedirs(SAVE_DIR, exist_ok=True)

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

def new_player(name: str) -> dict:
    return {
        "created": True,
        "name": name,
        "rating": 60,
        "money": 0,
        "goals": 0,
        "assists": 0,
        "matches": 0,
        "fitness": 100,
        "morale": 80,
        "injured": False,
        "injury_days": 0,
        "pace": 60,
        "shooting": 60,
        "passing": 60,
        "dribbling": 60,
        "defending": 30,
        "physical": 55,
        "club": "Свободный агент",
        "agent": "Нет",
        "followers": 100,
        "popularity": 1,
        "boots": "обычные",
        "equipment": "стандартная",
        "trophies": [],
        "season": 1,
        "age": 16,
        "mvps": 0,
    }

def fmt_money(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M €"
    if n >= 1_000:
        return f"{n / 1_000:.0f}K €"
    return f"{n} €"

@dp.message(Command("start"))
async def cmd_start(message: Message):
    data = load(message.from_user.id)
    if data and data.get("created"):
        await message.answer(
            f"👋 С возвращением, <b>{data['name']}</b>!\n\n"
            "/profile — профиль\n"
            "/train — тренировка\n"
            "/match — матч\n"
            "/rest — отдых\n"
            "/shop — магазин\n"
            "/help — все команды"
        )
    else:
        await message.answer(
            "⚽ <b>Football Career</b>\n\n"
            "Создай карьеру:\n"
            "<code>/create Имя</code>\n\n"
            "Пример:\n"
            "<code>/create Alex</code>"
        )

@dp.message(Command("create"))
async def cmd_create(message: Message):
    args = message.text.split()
    if len(args) < 2:
        await message.answer("❌ Напиши: /create Имя")
        return

    name = " ".join(args[1:])
    data = new_player(name)
    save(message.from_user.id, data)

    await message.answer(
        f"✅ <b>Карьера создана!</b>\n\n"
        f"👤 Игрок: {data['name']}\n"
        f"⭐ Рейтинг: {data['rating']}\n"
        f"🏟 Клуб: {data['club']}\n\n"
        "Используй /help для всех команд"
    )

@dp.message(Command("profile"))
async def cmd_profile(message: Message):
    data = load(message.from_user.id)
    if not data or not data.get("created"):
        await message.answer("❌ Сначала создай игрока через /create")
        return

    await message.answer(
f"""
👤 <b>{data['name']}</b>

⭐ Рейтинг: {data['rating']}
🏟 Клуб: {data['club']}
💰 Деньги: {fmt_money(data['money'])}
⚽ Голы: {data['goals']}
🎯 Ассисты: {data['assists']}
🎮 Матчей: {data['matches']}
⭐ MVP: {data['mvps']}

🏃 Скорость: {data['pace']}
🎯 Удар: {data['shooting']}
🔄 Пас: {data['passing']}
🌀 Дриблинг: {data['dribbling']}
🛡 Защита: {data['defending']}
💪 Физика: {data['physical']}

⚡ Форма: {data['fitness']}%
😊 Мораль: {data['morale']}%
🤕 Травма: {'Да' if data['injured'] else 'Нет'}
👟 Бутсы: {data.get('boots', 'обычные')}
👥 Подписчики: {data['followers']}
"""
    )

@dp.message(Command("train"))
async def cmd_train(message: Message):
    data = load(message.from_user.id)
    if not data or not data.get("created"):
        await message.answer("❌ Сначала создай игрока через /create")
        return

    if data.get("injured"):
        await message.answer("🤕 Ты травмирован! Отдохни.")
        return

    if data["fitness"] < 20:
        await message.answer("😴 Ты слишком устал! Используй /rest")
        return

    stats = ["pace", "shooting", "passing", "dribbling", "defending", "physical"]
    stat_names = {
        "pace": "Скорость", "shooting": "Удар", "passing": "Пас",
        "dribbling": "Дриблинг", "defending": "Защита", "physical": "Физика"
    }

    stat = random.choice(stats)
    gain = random.randint(1, 3)
    data[stat] = min(99, data[stat] + gain)

    data["rating"] = int((
        data["pace"] + data["shooting"] + data["passing"] +
        data["dribbling"] + data["defending"] + data["physical"]
    ) / 6)

    data["fitness"] = max(0, data["fitness"] - random.randint(10, 20))
    data["morale"] = min(100, data["morale"] + random.randint(1, 4))

    injury_msg = ""
    if random.randint(1, 100) <= 5:
        days = random.randint(3, 7)
        data["injured"] = True
        data["injury_days"] = days
        injury_msg = f"\n\n🤕 Ты получил травму! {days} дней."

    save(message.from_user.id, data)

    await message.answer(
f"""
🏋️ <b>Тренировка завершена!</b>

⬆️ {stat_names[stat]} +{gain}
⭐ Рейтинг: {data['rating']}
⚡ Форма: {data['fitness']}%
😊 Мораль: {data['morale']}%
{injury_msg}
"""
    )

@dp.message(Command("match"))
async def cmd_match(message: Message):
    data = load(message.from_user.id)
    if not data or not data.get("created"):
        await message.answer("❌ Сначала создай игрока через /create")
        return

    if data.get("injured"):
        await message.answer(f"🤕 Ты травмирован! Осталось {data['injury_days']} дней.")
        return

    if data["fitness"] < 15:
        await message.answer("😴 Ты слишком устал! Отдохни /rest")
        return

    goals = max(0, int(random.gauss(0.5, 0.8)))
    assists = max(0, int(random.gauss(0.3, 0.6)))
    is_mvp = random.random() < 0.15

    data["matches"] += 1
    data["goals"] += goals
    data["assists"] += assists
    if is_mvp:
        data["mvps"] += 1

    rating_change = goals * 0.5 + assists * 0.3 + (1.5 if is_mvp else 0) + random.uniform(-0.5, 0.5)
    data["rating"] = min(99, max(40, data["rating"] + rating_change))

    bonus = goals * 1000 + (5000 if is_mvp else 0)
    data["money"] += bonus

    data["fitness"] = max(0, data["fitness"] - random.randint(10, 25))

    followers_gain = random.randint(10, 50) + goals * 10
    data["followers"] += followers_gain
    data["popularity"] = min(100, data["popularity"] + random.randint(1, 3))

    injury_msg = ""
    if random.random() < 0.05:
        days = random.randint(3, 7)
        data["injured"] = True
        data["injury_days"] = days
        injury_msg = f"\n\n🤕 Ты получил травму! {days} дней."

    save(message.from_user.id, data)

    mvp_text = "⭐ <b>Игрок матча!</b>\n" if is_mvp else ""

    await message.answer(
f"""
🏟 <b>Матч окончен!</b>

{mvp_text}
⚽ Голы: {goals}
🎯 Ассисты: {assists}
📈 Рейтинг: {data['rating']:.1f}

💵 Бонус: {fmt_money(bonus)}
👥 +{followers_gain} подписчиков
⚡ Форма: {data['fitness']}%
{injury_msg}
"""
    )

@dp.message(Command("rest"))
async def cmd_rest(message: Message):
    data = load(message.from_user.id)
    if not data or not data.get("created"):
        await message.answer("❌ Сначала создай игрока через /create")
        return

    data["fitness"] = min(100, data["fitness"] + 30)
    data["morale"] = min(100, data["morale"] + 10)

    recovery_msg = ""
    if data.get("injured"):
        data["injury_days"] -= 1
        if data["injury_days"] <= 0:
            data["injured"] = False
            data["injury_days"] = 0
            recovery_msg = "✅ Ты полностью восстановился!"
        else:
            recovery_msg = f"🤕 Осталось {data['injury_days']} дней."

    save(message.from_user.id, data)

    await message.answer(
f"""
😴 <b>Отдых завершён!</b>

⚡ Форма: {data['fitness']}%
😊 Мораль: {data['morale']}%
{recovery_msg}
"""
    )

@dp.message(Command("shop"))
async def cmd_shop(message: Message):
    data = load(message.from_user.id)
    if not data or not data.get("created"):
        await message.answer("❌ Сначала создай игрока через /create")
        return

    items = {
        "boots": {"name": "👟 Профессиональные бутсы", "cost": 50000, "stat": "+2 к скорости"},
        "equipment": {"name": "🎽 Профессиональная экипировка", "cost": 30000, "stat": "+1 к физике"},
        "fitness": {"name": "💪 Тренажёрный зал", "cost": 10000, "stat": "+10 к форме"},
        "recovery": {"name": "🏥 Восстановительный центр", "cost": 20000, "stat": "+15 к форме"},
    }

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"{item['name']} — {fmt_money(item['cost'])}",
            callback_data=f"shop:{key}"
        )] for key, item in items.items()
    ])

    await message.answer(
f"""
🛒 <b>Магазин</b>

💰 Деньги: {fmt_money(data['money'])}

Выбери товар:
""",
        reply_markup=keyboard
    )

@dp.callback_query(F.data.startswith("shop:"))
async def cb_shop(call: CallbackQuery):
    uid = call.from_user.id
    data = load(uid)
    if not data or not data.get("created"):
        await call.answer("❌ Сначала создай игрока!", show_alert=True)
        return

    item_key = call.data.split(":")[1]
    items = {
        "boots": {"name": "👟 Профессиональные бутсы", "cost": 50000, "stat": "+2 к скорости"},
        "equipment": {"name": "🎽 Профессиональная экипировка", "cost": 30000, "stat": "+1 к физике"},
        "fitness": {"name": "💪 Тренажёрный зал", "cost": 10000, "stat": "+10 к форме"},
        "recovery": {"name": "🏥 Восстановительный центр", "cost": 20000, "stat": "+15 к форме"},
    }

    item = items[item_key]

    if data["money"] < item["cost"]:
        await call.answer(f"❌ Нужно {fmt_money(item['cost'])}", show_alert=True)
        return

    data["money"] -= item["cost"]

    if item_key == "boots":
        data["boots"] = "профессиональные"
        data["pace"] = min(99, data["pace"] + 2)
    elif item_key == "equipment":
        data["equipment"] = "профессиональная"
        data["physical"] = min(99, data["physical"] + 1)
    elif item_key == "fitness":
        data["fitness"] = min(100, data["fitness"] + 10)
    elif item_key == "recovery":
        data["fitness"] = min(100, data["fitness"] + 15)

    save(uid, data)

    await call.message.edit_text(
f"""
✅ <b>Покупка совершена!</b>

{item['name']}
💰 Осталось: {fmt_money(data['money'])}
{item['stat']}
"""
    )

@dp.message(Command("boots"))
async def cmd_boots(message: Message):
    data = load(message.from_user.id)
    if not data or not data.get("created"):
        await message.answer("❌ Сначала создай игрока через /create")
        return

    await message.answer(
f"""
👟 <b>Твои бутсы</b>

👟 Текущие: {data.get('boots', 'обычные')}
⚡ Эффект: {'+2 к скорости' if data.get('boots') == 'профессиональные' else 'без бонуса'}

🏃 Скорость: {data['pace']}

💡 Используй /shop чтобы купить новые!
"""
    )

@dp.message(Command("equipment"))
async def cmd_equipment(message: Message):
    data = load(message.from_user.id)
    if not data or not data.get("created"):
        await message.answer("❌ Сначала создай игрока через /create")
        return

    await message.answer(
f"""
🎽 <b>Твоя экипировка</b>

🎽 Текущая: {data.get('equipment', 'стандартная')}
💪 Эффект: {'+1 к физике' if data.get('equipment') == 'профессиональная' else 'без бонуса'}

💪 Физика: {data['physical']}

💡 Используй /shop чтобы купить новую!
"""
    )

@dp.message(Command("trophies"))
async def cmd_trophies(message: Message):
    data = load(message.from_user.id)
    if not data or not data.get("created"):
        await message.answer("❌ Сначала создай игрока через /create")
        return

    trophies = data.get("trophies", [])
    if not trophies:
        trophies_text = "Пока нет трофеев 🏆"
    else:
        trophies_text = "\n".join([f"🏆 {t}" for t in trophies])

    await message.answer(
f"""
🏆 <b>Трофеи {data['name']}</b>

{trophies_text}
"""
    )

@dp.message(Command("stats"))
async def cmd_stats(message: Message):
    data = load(message.from_user.id)
    if not data or not data.get("created"):
        await message.answer("❌ Сначала создай игрока через /create")
        return

    await message.answer(
f"""
📊 <b>Статистика {data['name']}</b>

⚽ Голы: {data['goals']}
🎯 Ассисты: {data['assists']}
🎮 Матчей: {data['matches']}
⭐ MVP: {data['mvps']}

🏃 Скорость: {data['pace']}
🎯 Удар: {data['shooting']}
🔄 Пас: {data['passing']}
🌀 Дриблинг: {data['dribbling']}
🛡 Защита: {data['defending']}
💪 Физика: {data['physical']}

⚡ Форма: {data['fitness']}%
😊 Мораль: {data['morale']}%
🤕 Травма: {'Да' if data['injured'] else 'Нет'}

👥 Подписчики: {data['followers']}
⭐ Популярность: {data['popularity']}/100
"""
    )

@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "⚽ <b>Все команды бота</b>\n\n"
        "📋 Основные:\n"
        "/start — Запуск\n"
        "/create Имя — Создать игрока\n"
        "/profile — Профиль\n"
        "/help — Помощь\n\n"
        "⚽ Игровой процесс:\n"
        "/train — Тренировка\n"
        "/rest — Отдых\n"
        "/match — Сыграть матч\n\n"
        "📊 Статистика:\n"
        "/stats — Характеристики\n"
        "/trophies — Трофеи\n\n"
        "🛒 Магазин:\n"
        "/shop — Купить экипировку\n"
        "/boots — Бутсы\n"
        "/equipment — Экипировка"
    )

@dp.message(F.text.startswith("/"))
async def unknown(message: Message):
    await message.answer("❌ Неизвестная команда. Напиши /help")

async def main():
    print("🚀 Бот запущен!")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
