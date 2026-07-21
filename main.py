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
        "surname": "",
        "nation": "Россия",
        "position": "Нападающий",
        "age": 16,
        "height": 175,
        "weight": 70,
        "foot": "Right",
        "number": 9,
        "club": "Свободный агент",
        "club_level": 1,
        "rating": 60,
        "potential": 90,
        "matches": 0,
        "goals": 0,
        "assists": 0,
        "mvps": 0,
        "salary": 0,
        "money": 0,
        "market_value": 500000,
        "season": 1,
        "ucl": 0,
        "league_titles": 0,
        "worldcup": 0,
        "ballon": 0,
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
        "agent": "Нет",
        "followers": 100,
        "popularity": 1,
        "professionalism": 50,
        "leadership": 50,
        "ambition": 50,
        "club_history": [],
        "trophies": [],
        "sponsors": [],
        "boots": "обычные",
        "equipment": "стандартная",
        "captain": False,
        "retired": False,
    }


def fmt_money(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M €"
    if n >= 1_000:
        return f"{n / 1_000:.0f}K €"
    return f"{n} €"

def get_club_level(rating: int) -> tuple:
    if rating >= 85:
        return 4, "Топ-клуб"
    elif rating >= 75:
        return 3, "Сильный клуб"
    elif rating >= 65:
        return 2, "Средний клуб"
    else:
        return 1, "Слабый клуб"

def get_club_offers(rating: int) -> list:
    if rating >= 85:
        return [("Реал Мадрид", 500000, 4), ("Барселона", 450000, 4), ("Манчестер Сити", 480000, 4)]
    elif rating >= 75:
        return [("Ливерпуль", 300000, 3), ("Челси", 280000, 3), ("Ювентус", 250000, 3)]
    elif rating >= 65:
        return [("Вест Хэм", 150000, 2), ("Валенсия", 140000, 2), ("Лацио", 130000, 2)]
    else:
        return [("Кристал Пэлас", 60000, 1), ("Хоффенхайм", 55000, 1), ("Болонья", 50000, 1)]


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
            "/season — сезон\n"
            "/transfers — трансферы\n"
            "/agent — агент\n"
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
🏟 Клуб: {data['club']} ({get_club_level(data['rating'])[1]})
💰 Деньги: {fmt_money(data['money'])}
💵 Зарплата: {fmt_money(data['salary'])}/нед
📈 Стоимость: {fmt_money(data['market_value'])}

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
{'📅 Осталось: ' + str(data['injury_days']) + ' дней' if data['injured'] else ''}

👟 Бутсы: {data.get('boots', 'обычные')}
👥 Подписчики: {data['followers']:,}
⭐ Популярность: {data['popularity']}/100
"""
    )


@dp.message(Command("train"))
async def cmd_train(message: Message):
    data = load(message.from_user.id)
    if not data or not data.get("created"):
        await message.answer("❌ Сначала создай игрока через /create")
        return

    if data.get("retired"):
        await message.answer("❌ Ты завершил карьеру!")
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

    if data.get("retired"):
        await message.answer("❌ Ты завершил карьеру!")
        return

    if data.get("injured"):
        await message.answer(f"🤕 Ты травмирован! Осталось {data['injury_days']} дней.")
        return

    if data["fitness"] < 15:
        await message.answer("😴 Ты слишком устал! Отдохни /rest")
        return

    rating_modifier = (data["rating"] - 60) / 20
    goals = max(0, int(random.gauss(0.5 + rating_modifier, 0.8)))
    assists = max(0, int(random.gauss(0.3 + rating_modifier * 0.5, 0.6)))
    is_mvp = random.random() < 0.1 + (data["rating"] - 60) / 100

    data["matches"] += 1
    data["goals"] += goals
    data["assists"] += assists
    if is_mvp:
        data["mvps"] += 1

    rating_change = goals * 0.5 + assists * 0.3 + (1.5 if is_mvp else 0) + random.uniform(-0.5, 0.5)
    data["rating"] = min(99, max(40, data["rating"] + rating_change))
    data["market_value"] = int(data["rating"] * 100000 + data["goals"] * 5000)

    bonus = goals * data["salary"] // 5 + (50000 if is_mvp else 0)
    data["money"] += bonus

    data["fitness"] = max(0, data["fitness"] - random.randint(10, 25))

    followers_gain = random.randint(10, 50) + goals * 10 + (100 if is_mvp else 0)
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
📈 Рейтинг: {data['rating']:.1f} ({'+' if rating_change > 0 else ''}{rating_change:.1f})

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


@dp.message(Command("season"))
async def cmd_season(message: Message):
    data = load(message.from_user.id)
    if not data or not data.get("created"):
        await message.answer("❌ Сначала создай игрока через /create")
        return

    if data.get("retired"):
        await message.answer("❌ Ты завершил карьеру!")
        return

    ucl = 1 if random.random() < max(0, (data["rating"] - 70) / 30) else 0
    league = 1 if random.random() < max(0, (data["rating"] - 60) / 40) else 0
    wc = 1 if random.random() < (0.1 if data["rating"] < 80 else 0.3) else 0
    ballon_won = data["goals"] > 20 and data["rating"] >= 85 and random.random() < 0.3

    if ballon_won:
        data["ballon"] += 1
    if ucl:
        data["ucl"] += 1
        data["trophies"].append("Лига чемпионов")
    if league:
        data["league_titles"] += 1
        data["trophies"].append("Чемпионат")
    if wc:
        data["worldcup"] += 1
        data["trophies"].append("Чемпионат мира")

    data["rating"] = min(99, data["rating"] + random.uniform(1, 5))
    data["salary"] = int(data["rating"] * 2500 + data["goals"] * 500)
    data["market_value"] = int(data["rating"] * 120000 + data["goals"] * 10000)
    data["money"] += data["salary"] * 52
    data["followers"] += random.randint(100, 500)
    data["popularity"] = min(100, data["popularity"] + random.randint(1, 5))
    data["age"] += 1
    data["season"] += 1

    retirement_msg = ""
    if data["age"] > 35 and data["rating"] < 75:
        data["retired"] = True
        retirement_msg = "\n\n🔚 <b>Ты завершил карьеру!</b> Ты вошёл в историю!"

    data["goals"] = 0
    data["assists"] = 0
    data["matches"] = 0

    save(message.from_user.id, data)

    ballon_line = "🏅 <b>Ты выиграл Золотой мяч!</b>" if ballon_won else "❌ Золотой мяч не получен"

    await message.answer(
f"""
📅 <b>Сезон {data['season'] - 1} завершён!</b>

🏆 Лига чемпионов: {'✅ Да' if ucl else '❌ Нет'}
🥇 Чемпионат: {'✅ Да' if league else '❌ Нет'}
🌍 Чемпионат мира: {'✅ Да' if wc else '❌ Нет'}
{ballon_line}

⭐ Рейтинг: {data['rating']:.1f}
💰 Зарплата: {fmt_money(data['salary'])}/нед
📈 Стоимость: {fmt_money(data['market_value'])}
👥 Подписчики: {data['followers']:,}
🎂 Возраст: {data['age']}
{retirement_msg}
"""
    )


@dp.message(Command("transfers"))
async def cmd_transfers(message: Message):
    data = load(message.from_user.id)
    if not data or not data.get("created"):
        await message.answer("❌ Сначала создай игрока через /create")
        return

    if data.get("retired"):
        await message.answer("❌ Ты завершил карьеру!")
        return

    if data.get("agent") == "Нет":
        await message.answer("❌ Для трансферов нужен агент. Найми через /agent")
        return

    offers = get_club_offers(data["rating"])

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"{club} — {fmt_money(salary)}/нед",
            callback_data=f"transfer:{club}:{salary}:{level}"
        )] for club, salary, level in offers
    ] + [[InlineKeyboardButton(text="❌ Пропустить", callback_data="transfer:skip")]])

    await message.answer(
f"""
✈️ <b>Трансферные предложения</b>

Текущий клуб: {data['club']}
⭐ Рейтинг: {data['rating']}
💰 Зарплата: {fmt_money(data['salary'])}/нед

Выбери новый клуб:
""",
        reply_markup=keyboard
    )


@dp.callback_query(F.data.startswith("transfer:"))
async def cb_transfer(call: CallbackQuery):
    uid = call.from_user.id
    data = load(uid)
    if not data or not data.get("created"):
        await call.answer("❌ Сначала создай карьеру!", show_alert=True)
        return

    parts = call.data.split(":")
    if parts[1] == "skip":
        await call.message.edit_text("❌ Ты отклонил все предложения.")
        return

    club, salary, level = parts[1], int(parts[2]), int(parts[3])
    old_club = data["club"]
    old_level = data.get("club_level", 1)

    data["club_history"].append({"club": old_club, "season": data["season"], "rating": data["rating"]})
    data["club"] = club
    data["club_level"] = level
    data["salary"] = salary
    data["market_value"] = int(data["rating"] * 100000)

    if level > old_level:
        data["money"] += 100000 * (level - old_level)

    save(uid, data)

    await call.message.edit_text(
f"""
✅ <b>Ты перешёл в {club}!</b>

🏟 Новый клуб: {club} ({get_club_level(data['rating'])[1]})
💵 Зарплата: {fmt_money(salary)}/нед
📈 Стоимость: {fmt_money(data['market_value'])}
"""
    )


@dp.message(Command("agent"))
async def cmd_agent(message: Message):
    data = load(message.from_user.id)
    if not data or not data.get("created"):
        await message.answer("❌ Сначала создай игрока через /create")
        return

    current = data.get("agent", "Нет")
    if current != "Нет":
        await message.answer(f"🧑‍💼 Твой агент: <b>{current}</b>\n💰 Деньги: {fmt_money(data['money'])}")
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="😐 Плохой агент — €25,000", callback_data="hire_agent:bad")],
        [InlineKeyboardButton(text="🙂 Средний агент — €55,000", callback_data="hire_agent:medium")],
        [InlineKeyboardButton(text="😎 Хороший агент — €90,000", callback_data="hire_agent:good")],
    ])

    await message.answer(
        f"🧑‍💼 <b>Выбери агента</b>\n\n💰 Деньги: {fmt_money(data['money'])}",
        reply_markup=keyboard
    )


@dp.callback_query(F.data.startswith("hire_agent:"))
async def cb_hire_agent(call: CallbackQuery):
    uid = call.from_user.id
    data = load(uid)
    if not data or not data.get("created"):
        await call.answer("❌ Сначала создай карьеру!", show_alert=True)
        return

    if data.get("agent", "Нет") != "Нет":
        await call.answer("У тебя уже есть агент.", show_alert=True)
        return

    agents = {"bad": ("Плохой агент", 25000), "medium": ("Средний агент", 55000), "good": ("Хороший агент", 90000)}
    key = call.data.split(":")[1]
    name, cost = agents[key]

    if data["money"] < cost:
        await call.answer(f"❌ Нужно {fmt_money(cost)}", show_alert=True)
        return

    data["money"] -= cost
    data["agent"] = name
    save(uid, data)

    await call.message.edit_text(f"✅ Ты нанял <b>{name}</b>!\n💰 Осталось: {fmt_money(data['money'])}")


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
    trophies_text = "\n".join([f"🏆 {t}" for t in trophies]) if trophies else "Пока нет трофеев 🏆"

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

👥 Подписчики: {data['followers']:,}
⭐ Популярность: {data['popularity']}/100
"""
    )


@dp.message(Command("social"))
async def cmd_social(message: Message):
    data = load(message.from_user.id)
    if not data or not data.get("created"):
        await message.answer("❌ Сначала создай игрока через /create")
        return

    await message.answer(
f"""
📱 <b>Социальные сети</b>

👥 Подписчики: {data.get('followers', 100):,}
⭐ Популярность: {data.get('popularity', 1)}/100
📈 Рост за сезон: +{random.randint(50, 200)}
"""
    )


@dp.message(Command("personality"))
async def cmd_personality(message: Message):
    data = load(message.from_user.id)
    if not data or not data.get("created"):
        await message.answer("❌ Сначала создай игрока через /create")
        return

    await message.answer(
f"""
🧠 <b>Характер игрока</b>

💼 Профессионализм: {data.get('professionalism', 50)}/100
👑 Лидерство: {data.get('leadership', 50)}/100
🔥 Амбиции: {data.get('ambition', 50)}/100
"""
    )


@dp.message(Command("contract"))
async def cmd_contract(message: Message):
    data = load(message.from_user.id)
    if not data or not data.get("created"):
        await message.answer("❌ Сначала создай игрока через /create")
        return

    await message.answer(
f"""
📄 <b>Контракт</b>

🏟 Клуб: {data['club']}
💰 Зарплата: {fmt_money(data['salary'])}/нед
📈 Стоимость: {fmt_money(data['market_value'])}
💵 Денег: {fmt_money(data['money'])}
🧑‍💼 Агент: {data.get('agent', 'Нет')}
"""
    )


@dp.message(Command("table"))
async def cmd_table(message: Message):
    data = load(message.from_user.id)
    if not data or not data.get("created"):
        await message.answer("❌ Сначала создай игрока через /create")
        return

    clubs = [
        "Манчестер Сити", "Реал Мадрид", "Барселона", "Бавария",
        "ПСЖ", "Ливерпуль", "Ювентус", "Атлетико", "Челси", "Арсенал"
    ]

    if data["club"] in clubs:
        clubs.remove(data["club"])
    random.shuffle(clubs)
    table = [data["club"]] + clubs[:9]
    random.shuffle(table)

    lines = ["🏆 <b>Таблица лиги</b>\n"]
    medals = {0: "🥇", 1: "🥈", 2: "🥉"}

    for i, club in enumerate(table):
        pts = random.randint(20, 90)
        medal = medals.get(i, f"{i+1}.")
        mark = " ← ты" if club == data["club"] else ""
        lines.append(f"{medal} {club} — {pts} очков{mark}")

    await message.answer("\n".join(lines))


@dp.message(Command("news"))
async def cmd_news(message: Message):
    data = load(message.from_user.id)
    if not data or not data.get("created"):
        await message.answer("❌ Сначала создай игрока через /create")
        return

    news_items = [
        f"📰 <b>{data['name']}</b> показал отличную игру в последнем матче!",
        f"🏟 Болельщики требуют повышения зарплаты для {data['name']}!",
        f"⚽ {data['name']} тренируется с повышенной нагрузкой.",
        f"📊 Рейтинг {data['name']} растёт с каждым матчем!",
        f"👥 Подписчики {data['name']} достигли {data['followers']:,}!",
        f"🏆 {data['name']} мечтает выиграть Лигу чемпионов.",
        f"⭐ Эксперты называют {data['name']} будущим футбола.",
    ]

    await message.answer(random.choice(news_items))


@dp.message(Command("leaderboard"))
async def cmd_leaderboard(message: Message):
    top_players = [
        {"name": "Лионель Месси", "rating": 94, "club": "Интер Майами"},
        {"name": "Криштиану Роналду", "rating": 93, "club": "Аль-Наср"},
        {"name": "Килиан Мбаппе", "rating": 92, "club": "ПСЖ"},
        {"name": "Эрлинг Холанд", "rating": 91, "club": "Манчестер Сити"},
        {"name": "Винисиус Жуниор", "rating": 90, "club": "Реал Мадрид"},
        {"name": "Хави Эрнандес", "rating": 89, "club": "Барселона"},
        {"name": "Андре Иньеста", "rating": 88, "club": "Висел Кобе"},
        {"name": "Златан Ибрагимович", "rating": 87, "club": "Милан"},
        {"name": "Неймар", "rating": 86, "club": "Аль-Хиляль"},
        {"name": "Тиаго Силва", "rating": 85, "club": "Челси"},
    ]

    lines = ["🏆 <b>Топ-10 игроков мира</b>\n"]
    medals = {0: "🥇", 1: "🥈", 2: "🥉"}

    for i, player in enumerate(top_players):
        medal = medals.get(i, f"{i+1}.")
        lines.append(f"{medal} {player['name']} — {player['rating']}⭐ ({player['club']})")

    await message.answer("\n".join(lines))


@dp.message(Command("sponsor"))
async def cmd_sponsor(message: Message):
    data = load(message.from_user.id)
    if not data or not data.get("created"):
        await message.answer("❌ Сначала создай игрока через /create")
        return

    if data["rating"] >= 85:
        sponsors = [{"name": "Nike", "money": 500000, "popularity": 10}]
    elif data["rating"] >= 75:
        sponsors = [{"name": "Gatorade", "money": 200000, "popularity": 5}]
    else:
        sponsors = [{"name": "Local brand", "money": 50000, "popularity": 1}]

    sponsor = random.choice(sponsors)
    data["money"] += sponsor["money"]
    data["popularity"] = min(100, data["popularity"] + sponsor["popularity"])
    data["sponsors"].append(sponsor["name"])

    save(message.from_user.id, data)

    await message.answer(
f"""
💎 <b>Новый спонсор!</b>

🏢 {sponsor['name']}
💰 Контракт: {fmt_money(sponsor['money'])}
⭐ Популярность +{sponsor['popularity']}
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
        "/match — Матч\n"
        "/season — Новый сезон\n\n"
        "🔄 Карьера:\n"
        "/transfers — Трансферы\n"
        "/agent — Агент\n"
        "/contract — Контракт\n"
        "/sponsor — Спонсоры\n\n"
        "📊 Статистика:\n"
        "/stats — Характеристики\n"
        "/trophies — Трофеи\n"
        "/table — Таблица\n"
        "/leaderboard — Топ игроков\n\n"
        "👤 Социальное:\n"
        "/social — Соцсети\n"
        "/news — Новости\n"
        "/personality — Характер\n\n"
        "🛒 Магазин:\n"
        "/shop — Купить\n"
        "/boots — Бутсы\n"
        "/equipment — Экипировка"
    )


@dp.message(F.text.startswith("/"))
async def unknown(message: Message):
    data = load(message.from_user.id)
    if not data or not data.get("created"):
        await message.answer("❌ Неизвестная команда. Напиши /help")
        return

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
        "/match — Матч\n"
        "/season — Новый сезон\n\n"
        "🔄 Карьера:\n"
        "/transfers — Трансферы\n"
        "/agent — Агент\n"
        "/contract — Контракт\n"
        "/sponsor — Спонсоры\n\n"
        "📊 Статистика:\n"
        "/stats — Характеристики\n"
        "/trophies — Трофеи\n"
        "/table — Таблица\n"
        "/leaderboard — Топ игроков\n\n"
        "👤 Социальное:\n"
        "/social — Соцсети\n"
        "/news — Новости\n"
        "/personality — Характер\n\n"
        "🛒 Магазин:\n"
        "/shop — Купить\n"
        "/boots — Бутсы\n"
        "/equipment — Экипировка"
    )


async def main():
    print("🚀 Бот запущен!")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
