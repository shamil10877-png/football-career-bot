import asyncio
import json
import os
import random
from datetime import datetime

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher(storage=MemoryStorage())

SAVE_DIR = os.path.join(os.path.dirname(__file__), "players")
os.makedirs(SAVE_DIR, exist_ok=True)


# ── сохранение / загрузка ──────────────────────────────────────────────────

def save_file(user_id: int) -> str:
    return os.path.join(SAVE_DIR, f"{user_id}.json")

def save(user_id: int, player: dict):
    with open(save_file(user_id), "w", encoding="utf-8") as f:
        json.dump(player, f, ensure_ascii=False, indent=4)

def load(user_id: int) -> dict | None:
    path = save_file(user_id)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return migrate(json.load(f))
    return None

DEFAULTS = {
    "created": False, "name": "", "surname": "", "nation": "",
    "position": "", "age": 15, "height": 170, "weight": 65,
    "foot": "Right", "number": 9, "club": "Свободный агент",
    "club_level": 1,
    "rating": 60, "potential": 90,
    "matches": 0, "goals": 0, "assists": 0, "mvps": 0,
    "salary": 0, "money": 0, "market_value": 500000,
    "season": 1, "ucl": 0, "league_titles": 0, "worldcup": 0, "ballon": 0,
    "fitness": 100, "morale": 80, "injured": False, "injury_days": 0,
    "pace": 60, "shooting": 60, "passing": 60,
    "dribbling": 60, "defending": 30, "physical": 55,
    "agent": "Нет",
    "followers": 100, "popularity": 1,
    "professionalism": 50, "leadership": 50, "ambition": 50,
    "club_history": [],
    "trophies": [],
    "sponsors": [],
    "boots": "обычные",
    "equipment": "стандартная",
    "captain": False,
    "retired": False,
}

def migrate(p: dict) -> dict:
    for key, val in DEFAULTS.items():
        if key not in p:
            p[key] = val
    return p

def new_player() -> dict:
    return {
        "created": False,
        "name": "", "surname": "", "nation": "", "position": "",
        "age": 15, "height": 170, "weight": 65,
        "foot": "Right", "number": 9,
        "club": "Свободный агент", "club_level": 1,
        "rating": 60, "potential": 90,
        "matches": 0, "goals": 0, "assists": 0, "mvps": 0,
        "salary": 0, "money": 0, "market_value": 500000,
        "season": 1, "ucl": 0, "league_titles": 0, "worldcup": 0, "ballon": 0,
        "fitness": 100, "morale": 80, "injured": False, "injury_days": 0,
        "pace": 60, "shooting": 60, "passing": 60,
        "dribbling": 60, "defending": 30, "physical": 55,
        "agent": "Нет",
        "followers": 100, "popularity": 1,
        "professionalism": 50, "leadership": 50, "ambition": 50,
        "club_history": [],
        "trophies": [],
        "sponsors": [],
        "boots": "обычные",
        "equipment": "стандартная",
        "captain": False,
        "retired": False,
    }


# ── хелперы ──────────────────────────────────────────────────────────────

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
    clubs = []
    if rating >= 85:
        clubs = [("Реал Мадрид", 500000, 4), ("Барселона", 450000, 4), ("Манчестер Сити", 480000, 4)]
    elif rating >= 75:
        clubs = [("Ливерпуль", 300000, 3), ("Челси", 280000, 3), ("Ювентус", 250000, 3)]
    elif rating >= 65:
        clubs = [("Вест Хэм", 150000, 2), ("Валенсия", 140000, 2), ("Лацио", 130000, 2)]
    else:
        clubs = [("Кристал Пэлас", 60000, 1), ("Хоффенхайм", 55000, 1), ("Болонья", 50000, 1)]
    return random.sample(clubs, min(3, len(clubs)))


# ── /start ─────────────────────────────────────────────────────────────────

@dp.message(Command("start"))
async def cmd_start(message: Message):
    p = load(message.from_user.id)
    if p and p.get("created"):
        await message.answer(
            f"👋 С возвращением, <b>{p['name']} {p['surname']}</b>!\n\n"
            "/profile — профиль\n"
            "/train — тренировка\n"
            "/rest — отдых\n"
            "/match — сыграть матч\n"
            "/season — сезон\n"
            "/trophies — трофеи\n"
            "/agent — агент\n"
            "/social — социальные сети\n"
            "/personality — характер\n"
            "/stats — статистика\n"
            "/help — все команды"
        )
    else:
        await message.answer(
            "⚽ <b>Football Career</b>\n\n"
            "Создай карьеру командой:\n"
            "<code>/create Имя Фамилия Страна Позиция Возраст Рост Вес Нога Номер</code>\n\n"
            "Пример:\n"
            "<code>/create Alex Smith England ST 16 181 74 Right 9</code>"
        )


# ── /create ────────────────────────────────────────────────────────────────

@dp.message(Command("create"))
async def cmd_create(message: Message):
    args = message.text.split()
    if len(args) != 10:
        await message.answer(
            "❌ Неверный формат. Нужно 9 параметров:\n"
            "<code>/create Имя Фамилия Страна Позиция Возраст Рост Вес Нога Номер</code>\n\n"
            "Пример:\n"
            "<code>/create Alex Smith England ST 16 181 74 Right 9</code>"
        )
        return

    try:
        age = int(args[5])
        height = int(args[6])
        weight = int(args[7])
        number = int(args[9])
    except ValueError:
        await message.answer("❌ Возраст, рост, вес и номер должны быть числами.")
        return

    foot = args[8].capitalize()
    if foot not in ("Right", "Left", "Both"):
        await message.answer("❌ Нога: Right, Left или Both.")
        return

    potential = random.randint(75, 99)
    p = new_player()
    p.update({
        "created": True,
        "name": args[1],
        "surname": args[2],
        "nation": args[3],
        "position": args[4].upper(),
        "age": age,
        "height": height,
        "weight": weight,
        "foot": foot,
        "number": number,
        "potential": potential,
    })
    save(message.from_user.id, p)

    await message.answer(
        f"✅ <b>Карьера создана!</b>\n\n"
        f"👤 {p['name']} {p['surname']}\n"
        f"🌍 {p['nation']}\n"
        f"⚽ {p['position']}   🔢 #{p['number']}\n"
        f"🎂 {p['age']} лет\n"
        f"📏 {p['height']} см   ⚖ {p['weight']} кг   🦶 {p['foot']}\n\n"
        f"⭐ Рейтинг: {p['rating']}\n"
        f"💎 Потенциал: {p['potential']}\n"
        f"🏟 Клуб: {p['club']}\n\n"
        "Используй /profile, /train, /match, /season, /trophies"
    )


# ── /profile ───────────────────────────────────────────────────────────────

@dp.message(Command("profile"))
async def cmd_profile(message: Message):
    p = load(message.from_user.id)
    if not p or not p.get("created"):
        await message.answer("❌ Сначала создай карьеру через /create")
        return

    await message.answer(
f"""
👤 {p['name']} {p['surname']}
{'👑 Капитан' if p.get('captain') else ''}

🌍 Страна: {p['nation']}
⚽ Позиция: {p['position']}
🏟 Клуб: {p['club']} ({get_club_level(p['rating'])[1]})

⭐ Рейтинг: {p['rating']}
💎 Потенциал: {p['potential']}

🎂 Возраст: {p['age']}
📏 Рост: {p['height']} см
⚖ Вес: {p['weight']} кг
🦶 Нога: {p['foot']}
🔢 Номер: {p['number']}

💰 Деньги: {fmt_money(p['money'])}
💵 Зарплата: {fmt_money(p['salary'])}/неделя
💸 Стоимость: {fmt_money(p['market_value'])}

🏟 Матчи: {p['matches']}
⚽ Голы: {p['goals']}
🎯 Ассисты: {p['assists']}
⭐ MVP: {p['mvps']}

⚡ Форма: {p['fitness']}%
😊 Мораль: {p['morale']}%
🤕 Травма: {'Да' if p['injured'] else 'Нет'}
{'📅 Осталось: ' + str(p['injury_days']) + ' дней' if p['injured'] else ''}

👟 Бутсы: {p.get('boots', 'обычные')}
🎽 Экипировка: {p.get('equipment', 'стандартная')}
"""
    )


# ── /match ─────────────────────────────────────────────────────────────────

@dp.message(Command("match"))
async def cmd_match(message: Message):
    p = load(message.from_user.id)
    if not p or not p.get("created"):
        await message.answer("❌ Сначала создай карьеру: /create")
        return

    if p.get("retired"):
        await message.answer("❌ Ты завершил карьеру!")
        return

    if p["injured"]:
        await message.answer(f"🤕 Ты травмирован! Осталось {p['injury_days']} дней.")
        return

    if p["fitness"] < 15:
        await message.answer("😴 Ты слишком устал! Отдохни командой /rest")
        return

    rating_modifier = (p["rating"] - 60) / 20
    goals = max(0, int(random.gauss(0.5 + rating_modifier, 0.8)))
    assists = max(0, int(random.gauss(0.3 + rating_modifier * 0.5, 0.6)))
    is_mvp = random.random() < 0.1 + (p["rating"] - 60) / 100

    p["matches"] += 1
    p["goals"] += goals
    p["assists"] += assists
    if is_mvp:
        p["mvps"] += 1

    rating_change = goals * 0.5 + assists * 0.3 + (1.5 if is_mvp else 0) + random.uniform(-0.5, 0.5)
    p["rating"] = min(99, max(40, p["rating"] + rating_change))
    p["market_value"] = int(p["rating"] * 100000 + p["goals"] * 5000)

    injury_msg = ""
    if random.random() < 0.05:
        injury_days = random.randint(3, 14)
        p["injured"] = True
        p["injury_days"] = injury_days
        injury_msg = f"\n\n🤕 Ты получил травму! {injury_days} дней восстановления."

    p["fitness"] = max(0, p["fitness"] - random.randint(10, 25))
    bonus = goals * p["salary"] // 5 + (50000 if is_mvp else 0)
    p["money"] += bonus

    followers_gain = random.randint(10, 50) + goals * 10 + (100 if is_mvp else 0)
    p["followers"] += followers_gain
    p["popularity"] = min(100, p["popularity"] + random.randint(1, 3))

    save(message.from_user.id, p)

    mvp_text = "⭐ <b>Игрок матча!</b>\n" if is_mvp else ""

    await message.answer(
f"""
🏟 <b>Матч окончен!</b>

{mvp_text}
⚽ Голы: {goals}
🎯 Ассисты: {assists}
📈 Рейтинг: {p['rating']:.1f} ({'+' if rating_change > 0 else ''}{rating_change:.1f})

💵 Бонус: {fmt_money(bonus)}
👥 +{followers_gain} подписчиков
⚡ Форма: {p['fitness']}%
{injury_msg}
"""
    )


# ── /train ─────────────────────────────────────────────────────────────────

@dp.message(Command("train"))
async def cmd_train(message: Message):
    p = load(message.from_user.id)
    if not p or not p.get("created"):
        await message.answer("Сначала создай карьеру.")
        return

    if p.get("retired"):
        await message.answer("❌ Ты завершил карьеру!")
        return

    if p["injured"]:
        await message.answer("🤕 Ты травмирован и не можешь тренироваться.")
        return

    if p["fitness"] < 20:
        await message.answer("😴 Ты слишком устал.")
        return

    stat_names = {
        "pace": "Скорость", "shooting": "Удар", "passing": "Пас",
        "dribbling": "Дриблинг", "defending": "Защита", "physical": "Физика"
    }
    stat = random.choice(["pace", "shooting", "passing", "dribbling", "defending", "physical"])
    gain = random.randint(1, 3)
    old_value = p[stat]
    p[stat] = min(p[stat] + gain, 99)
    actual_gain = p[stat] - old_value

    p["rating"] = int((p["pace"] + p["shooting"] + p["passing"] + p["dribbling"] + p["defending"] + p["physical"]) / 6)
    p["fitness"] = max(0, p["fitness"] - random.randint(10, 20))
    p["morale"] = min(100, p["morale"] + random.randint(1, 4))

    injury_msg = ""
    if random.randint(1, 100) <= 5:
        days = random.randint(3, 7)
        p["injured"] = True
        p["injury_days"] = days
        injury_msg = f"\n\n🤕 Ты получил травму на тренировке! {days} дней восстановления."

    save(message.from_user.id, p)

    await message.answer(
f"""
🏋️ Тренировка завершена!

⬆️ {stat_names[stat]} +{actual_gain}

⭐ Рейтинг: {p["rating"]}
⚡ Форма: {p["fitness"]}%
😊 Мораль: {p["morale"]}%
{injury_msg}
"""
    )


# ── /rest ──────────────────────────────────────────────────────────────────

@dp.message(Command("rest"))
async def cmd_rest(message: Message):
    p = load(message.from_user.id)
    if not p or not p.get("created"):
        await message.answer("Сначала создай карьеру.")
        return

    p["fitness"] = min(p["fitness"] + 30, 100)
    p["morale"] = min(p["morale"] + 10, 100)

    recovery_msg = ""
    if p["injured"]:
        p["injury_days"] -= 1
        if p["injury_days"] <= 0:
            p["injured"] = False
            p["injury_days"] = 0
            recovery_msg = "✅ Ты полностью восстановился после травмы!"
        else:
            recovery_msg = f"🤕 Восстановление продолжается. Осталось {p['injury_days']} дней."

    save(message.from_user.id, p)

    await message.answer(
f"""
😴 Отдых завершён!

⚡ Форма: {p["fitness"]}%
😊 Мораль: {p["morale"]}%
{recovery_msg}
"""
    )


# ── /transfers ─────────────────────────────────────────────────────────────

def transfer_keyboard(offers: list) -> InlineKeyboardMarkup:
    buttons = []
    for club, salary, level in offers:
        level_names = {1: "⬇️", 2: "➡️", 3: "⬆️", 4: "💎"}
        buttons.append([
            InlineKeyboardButton(
                text=f"{level_names.get(level, '')} {club} — {fmt_money(salary)}/нед",
                callback_data=f"transfer:{club}:{salary}:{level}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="❌ Пропустить", callback_data="transfer:skip")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@dp.message(Command("transfers"))
async def cmd_transfers(message: Message):
    p = load(message.from_user.id)
    if not p or not p.get("created"):
        await message.answer("❌ Сначала создай карьеру!")
        return

    if p.get("retired"):
        await message.answer("❌ Ты завершил карьеру!")
        return

    if p.get("agent", "Нет") == "Нет":
        await message.answer("❌ Для трансферов нужен агент. Найми через /agent")
        return

    offers = get_club_offers(p["rating"])

    await message.answer(
f"""
✈️ <b>Трансферные предложения</b>

Текущий клуб: {p['club']}
⭐ Рейтинг: {p['rating']}
💰 Зарплата: {fmt_money(p['salary'])}/нед

Выбери новый клуб:
""",
        reply_markup=transfer_keyboard(offers)
    )

@dp.callback_query(F.data.startswith("transfer:"))
async def cb_transfer(call: CallbackQuery):
    uid = call.from_user.id
    p = load(uid)
    if not p or not p.get("created"):
        await call.answer("❌ Сначала создай карьеру!", show_alert=True)
        return

    data = call.data.split(":")
    if data[1] == "skip":
        await call.message.edit_text("❌ Ты отклонил все предложения.")
        return

    club, salary_str, level_str = data[1], data[2], data[3]
    salary = int(salary_str)
    level = int(level_str)

    old_club = p["club"]
    old_club_level = p.get("club_level", 1)

    p["club_history"].append({"club": old_club, "season": p["season"], "rating": p["rating"]})
    p["club"] = club
    p["club_level"] = level
    p["salary"] = salary
    p["market_value"] = int(p["rating"] * 100000)

    if level > old_club_level:
        p["money"] += 100000 * (level - old_club_level)

    save(uid, p)

    await call.message.edit_text(
f"""
✅ <b>Ты перешёл в {club}!</b>

🏟 Новый клуб: {club} ({get_club_level(p['rating'])[1]})
💵 Зарплата: {fmt_money(salary)}/нед
📈 Стоимость: {fmt_money(p['market_value'])}
💰 Бонус: +{fmt_money(100000 * max(0, level - old_club_level))}
"""
    )


# ── /season ────────────────────────────────────────────────────────────────

@dp.message(Command("season"))
async def cmd_season(message: Message):
    p = load(message.from_user.id)
    if not p or not p.get("created"):
        await message.answer("❌ Сначала создай карьеру: /create")
        return

    if p.get("retired"):
        await message.answer("❌ Ты завершил карьеру!")
        return

    ucl = 1 if random.random() < max(0, (p["rating"] - 70) / 30) else 0
    league = 1 if random.random() < max(0, (p["rating"] - 60) / 40) else 0
    wc = 1 if random.random() < (0.1 if p["rating"] < 80 else 0.3) else 0
    ballon_won = p["goals"] > 20 and p["rating"] >= 85 and random.random() < 0.3

    if ballon_won:
        p["ballon"] += 1
    if ucl:
        p["ucl"] += 1
        p["trophies"].append("Лига чемпионов")
    if league:
        p["league_titles"] += 1
        p["trophies"].append("Чемпионат")
    if wc:
        p["worldcup"] += 1
        p["trophies"].append("Чемпионат мира")

    p["rating"] = min(99, p["rating"] + random.uniform(1, 5))
    p["salary"] = int(p["rating"] * 2500 + p["goals"] * 500)
    p["market_value"] = int(p["rating"] * 120000 + p["goals"] * 10000)
    p["money"] += p["salary"] * 52
    p["followers"] += random.randint(100, 500)
    p["popularity"] = min(100, p["popularity"] + random.randint(1, 5))
    p["age"] += 1
    p["season"] += 1

    retirement_msg = ""
    if p["age"] > 35 and p["rating"] < 75:
        p["retired"] = True
        retirement_msg = "\n\n🔚 <b>Ты завершил карьеру!</b> Ты вошёл в историю!"

    p["goals"] = 0
    p["assists"] = 0
    p["matches"] = 0

    save(message.from_user.id, p)

    ballon_line = "🏅 <b>Ты выиграл Золотой мяч!</b>" if ballon_won else "❌ Золотой мяч не получен"

    await message.answer(
f"""
📅 <b>Сезон {p['season'] - 1} завершён!</b>

🏆 Лига чемпионов: {'✅ Да' if ucl else '❌ Нет'}
🥇 Чемпионат: {'✅ Да' if league else '❌ Нет'}
🌍 ЧМ: {'✅ Да' if wc else '❌ Нет'}
{ballon_line}

⭐ Рейтинг: {p['rating']:.1f}
💰 Зарплата: {fmt_money(p['salary'])}/нед
📈 Стоимость: {fmt_money(p['market_value'])}
👥 Подписчики: {p['followers']:,}

Тебе {p['age']} лет. Сезон {p['season']} начинается!
{retirement_msg}
"""
    )


# ── /trophies ──────────────────────────────────────────────────────────────

@dp.message(Command("trophies"))
async def cmd_trophies(message: Message):
    p = load(message.from_user.id)
    if not p or not p.get("created"):
        await message.answer("❌ Сначала создай карьеру: /create")
        return

    trophies_list = "\n".join([f"🏆 {t}" for t in p.get("trophies", [])[-10:]]) or "Пока нет трофеев"

    await message.answer(
f"""
🏆 <b>Трофеи {p['name']} {p['surname']}</b>

🏆 Лига чемпионов: {p['ucl']}
🥇 Чемпионаты: {p['league_titles']}
🌍 Чемпионаты мира: {p['worldcup']}
🏅 Золотой мяч: {p['ballon']}

📋 Список трофеев:
{trophies_list}
"""
    )


# ── /stats ─────────────────────────────────────────────────────────────────

@dp.message(Command("stats"))
async def cmd_stats(message: Message):
    p = load(message.from_user.id)
    if not p or not p.get("created"):
        await message.answer("❌ Сначала создай карьеру!")
        return

    await message.answer(
f"""
📊 Статистика {p['name']} {p['surname']}

⚽ Голы: {p['goals']}
🎯 Ассисты: {p['assists']}
🎮 Матчей: {p['matches']}
⭐ MVP: {p['mvps']}

🏃 Скорость: {p['pace']}
🎯 Удар: {p['shooting']}
🔄 Пас: {p['passing']}
🌀 Дриблинг: {p['dribbling']}
🛡 Защита: {p['defending']}
💪 Физика: {p['physical']}

⚡ Форма: {p['fitness']}%
😊 Мораль: {p['morale']}%
🤕 Травма: {"Да" if p["injured"] else "Нет"}

👥 Подписчики: {p['followers']:,}
⭐ Популярность: {p['popularity']}/100
"""
    )


# ── /agent ─────────────────────────────────────────────────────────────────

AGENTS = {
    "bad": ("Плохой агент", 25000),
    "medium": ("Средний агент", 55000),
    "good": ("Хороший агент", 90000),
}

def agent_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="😐 Плохой агент — €25,000", callback_data="hire_agent:bad")],
        [InlineKeyboardButton(text="🙂 Средний агент — €55,000", callback_data="hire_agent:medium")],
        [InlineKeyboardButton(text="😎 Хороший агент — €90,000", callback_data="hire_agent:good")],
    ])

@dp.message(Command("agent"))
async def cmd_agent(message: Message):
    p = load(message.from_user.id)
    if not p or not p.get("created"):
        await message.answer("❌ Сначала создай карьеру!")
        return

    current = p.get("agent", "Нет")
    if current != "Нет":
        await message.answer(
            f"🧑‍💼 Твой агент: <b>{current}</b>\n\n"
            f"💰 Деньги: {fmt_money(p['money'])}"
        )
        return

    await message.answer(
        f"🧑‍💼 <b>Выбери агента</b>\n\n"
        f"💰 Твои деньги: {fmt_money(p['money'])}\n\n"
        "Агент помогает искать новые клубы.",
        reply_markup=agent_keyboard()
    )

@dp.callback_query(F.data.startswith("hire_agent:"))
async def cb_hire_agent(call: CallbackQuery):
    uid = call.from_user.id
    p = load(uid)
    if not p or not p.get("created"):
        await call.answer("❌ Сначала создай карьеру!", show_alert=True)
        return

    if p.get("agent", "Нет") != "Нет":
        await call.answer("У тебя уже есть агент.", show_alert=True)
        return

    key = call.data.split(":")[1]
    name, cost = AGENTS[key]

    if p["money"] < cost:
        await call.answer(f"❌ Недостаточно денег. Нужно {fmt_money(cost)}", show_alert=True)
        return

    p["money"] -= cost
    p["agent"] = name
    save(uid, p)

    await call.message.edit_text(
        f"✅ Ты нанял <b>{name}</b>!\n\n"
        f"Агент будет искать для тебя новые клубы.\n\n"
        f"💰 Осталось: {fmt_money(p['money'])}"
    )


# ── /social ────────────────────────────────────────────────────────────────

@dp.message(Command("social"))
async def cmd_social(message: Message):
    p = load(message.from_user.id)
    if not p or not p.get("created"):
        await message.answer("❌ Сначала создай карьеру!")
        return

    await message.answer(
f"""
📱 Социальные сети

👥 Подписчики: {p.get('followers', 100):,}
⭐ Популярность: {p.get('popularity', 1)}/100

📊 Статистика:
📈 Рост за сезон: +{random.randint(50, 200)}
💬 Вовлечение: {random.randint(1, 10)}%
"""
    )


# ── /personality ───────────────────────────────────────────────────────────

@dp.message(Command("personality"))
async def cmd_personality(message: Message):
    p = load(message.from_user.id)
    if not p or not p.get("created"):
        await message.answer("❌ Сначала создай карьеру!")
        return

    traits = []
    for key, name in [("professionalism", "Профессионализм"), ("leadership", "Лидерство"), ("ambition", "Амбиции")]:
        value = p.get(key, 50)
        emoji = "🔵" if value < 40 else "🟢" if value < 70 else "🔴"
        traits.append(f"{emoji} {name}: {value}/100")

    await message.answer(
f"""
🧠 Характер игрока

{chr(10).join(traits)}

💡 Совет:
{"Высокий профессионализм помогает в карьере!" if p.get('professionalism', 50) > 70 else "Работай над профессионализмом!"}
"""
    )


# ── /contract ──────────────────────────────────────────────────────────────

@dp.message(Command("contract"))
async def cmd_contract(message: Message):
    p = load(message.from_user.id)
    if not p or not p.get("created"):
        await message.answer("❌ Сначала создай карьеру!")
        return

    contract_years = random.randint(1, 5)

    await message.answer(
f"""
📄 <b>Контракт</b>

🏟 Клуб: {p['club']}
💵 Зарплата: {fmt_money(p['salary'])}/неделя
📈 Стоимость: {fmt_money(p['market_value'])}
⌛ Осталось: {contract_years} года(лет)

💰 Деньги: {fmt_money(p['money'])}
🧑‍💼 Агент: {p.get('agent', 'Нет')}
"""
    )


# ── /table ─────────────────────────────────────────────────────────────────

CLUBS_POOL = [
    "Манчестер Сити", "Реал Мадрид", "Барселона", "Бавария",
    "ПСЖ", "Ливерпуль", "Ювентус", "Атлетико", "Челси", "Арсенал",
]

@dp.message(Command("table"))
async def cmd_table(message: Message):
    p = load(message.from_user.id)
    if not p or not p.get("created"):
        await message.answer("❌ Сначала создай карьеру!")
        return

    others = [c for c in CLUBS_POOL if c != p["club"]]
    random.shuffle(others)
    teams = [p["club"]] + others[:9]
    table = sorted(teams, key=lambda _: random.randint(0, 100), reverse=True)

    lines = ["🏆 <b>Таблица лиги</b>\n"]
    medals = {0: "🥇", 1: "🥈", 2: "🥉"}
    for i, team in enumerate(table):
        pts = random.randint(20, 90)
        medal = medals.get(i, f"{i+1}.")
        mark = " ← ты" if team == p["club"] else ""
        lines.append(f"{medal} {team} — {pts} очков{mark}")

    await message.answer("\n".join(lines))


# ── /shop ──────────────────────────────────────────────────────────────────

@dp.message(Command("shop"))
async def cmd_shop(message: Message):
    p = load(message.from_user.id)
    if not p or not p.get("created"):
        await message.answer("❌ Сначала создай карьеру!")
        return

    items = {
        "boots": {"name": "👟 Профессиональные бутсы", "cost": 50000, "stat": "+2 к скорости"},
        "equipment": {"name": "🎽 Профессиональная экипировка", "cost": 30000, "stat": "+1 к физике"},
        "fitness": {"name": "💪 Тренажёрный зал", "cost": 10000, "stat": "+10 к форме"},
        "recovery": {"name": "🏥 Восстановительный центр", "cost": 20000, "stat": "+15 к форме"},
    }

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{item['name']} — {fmt_money(item['cost'])}", callback_data=f"shop:{key}")]
        for key, item in items.items()
    ])

    await message.answer(
f"""
🛒 <b>Магазин</b>

💰 Деньги: {fmt_money(p['money'])}

Выбери товар:
""",
        reply_markup=keyboard
    )

@dp.callback_query(F.data.startswith("shop:"))
async def cb_shop(call: CallbackQuery):
    uid = call.from_user.id
    p = load(uid)
    if not p or not p.get("created"):
        await call.answer("❌ Сначала создай карьеру!", show_alert=True)
        return

    item_key = call.data.split(":")[1]
    items = {
        "boots": {"name": "👟 Профессиональные бутсы", "cost": 50000, "stat": "+2 к скорости"},
        "equipment": {"name": "🎽 Профессиональная экипировка", "cost": 30000, "stat": "+1 к физике"},
        "fitness": {"name": "💪 Тренажёрный зал", "cost": 10000, "stat": "+10 к форме"},
        "recovery": {"name": "🏥 Восстановительный центр", "cost": 20000, "stat": "+15 к форме"},
    }

    item = items[item_key]

    if p["money"] < item["cost"]:
        await call.answer(f"❌ Недостаточно денег! Нужно {fmt_money(item['cost'])}", show_alert=True)
        return

    p["money"] -= item["cost"]

    if item_key == "boots":
        p["boots"] = "профессиональные"
        p["pace"] = min(99, p["pace"] + 2)
    elif item_key == "equipment":
        p["equipment"] = "профессиональная"
        p["physical"] = min(99, p["physical"] + 1)
    elif item_key == "fitness":
        p["fitness"] = min(100, p["fitness"] + 10)
    elif item_key == "recovery":
        p["fitness"] = min(100, p["fitness"] + 15)

    save(uid, p)

    await call.message.edit_text(
f"""
✅ <b>Покупка совершена!</b>

{item['name']}
💰 Осталось: {fmt_money(p['money'])}

{item['stat']}
"""
    )


# ── /boots ─────────────────────────────────────────────────────────────────

@dp.message(Command("boots"))
async def cmd_boots(message: Message):
    p = load(message.from_user.id)
    if not p or not p.get("created"):
        await message.answer("❌ Сначала создай карьеру!")
        return

    await message.answer(
f"""
👟 <b>Твои бутсы</b>

👟 Текущие: {p.get('boots', 'обычные')}
⚡ Эффект: {'+2 к скорости' if p.get('boots') == 'профессиональные' else 'без бонуса'}

🏃 Скорость: {p['pace']}

💡 Используй /shop чтобы купить новые бутсы!
"""
    )


# ── /equipment ─────────────────────────────────────────────────────────────

@dp.message(Command("equipment"))
async def cmd_equipment(message: Message):
    p = load(message.from_user.id)
    if not p or not p.get("created"):
        await message.answer("❌ Сначала создай карьеру!")
        return

    await message.answer(
f"""
🎽 <b>Твоя экипировка</b>

🎽 Текущая: {p.get('equipment', 'стандартная')}
💪 Эффект: {'+1 к физике' if p.get('equipment') == 'профессиональная' else 'без бонуса'}

💪 Физика: {p['physical']}

💡 Используй /shop чтобы купить новую экипировку!
"""
    )


# ── /news ──────────────────────────────────────────────────────────────────

@dp.message(Command("news"))
async def cmd_news(message: Message):
    p = load(message.from_user.id)
    if not p or not p.get("created"):
        await message.answer("❌ Сначала создай карьеру!")
        return

    news_items = [
        f"📰 <b>{p['name']} {p['surname']}</b> показал отличную игру в последнем матче!",
        f"🏟 Болельщики требуют повышения зарплаты для {p['name']}!",
        f"⚽ {p['name']} тренируется с повышенной нагрузкой.",
        f"📊 Рейтинг {p['name']} растёт с каждым матчем!",
        f"👥 Количество подписчиков {p['name']} достигло {p['followers']:,}!",
        f"🏆 {p['name']} мечтает выиграть Лигу чемпионов.",
        f"💪 {p['name']} стал лидером команды.",
        f"⭐ Эксперты называют {p['name']} будущим футбола.",
    ]

    await message.answer(random.choice(news_items))


# ── /leaderboard ───────────────────────────────────────────────────────────

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


# ── /sponsor ──────────────────────────────────────────────────────────────

@dp.message(Command("sponsor"))
async def cmd_sponsor(message: Message):
    p = load(message.from_user.id)
    if not p or not p.get("created"):
        await message.answer("❌ Сначала создай карьеру!")
        return

    if p["rating"] >= 85:
        sponsors = [{"name": "Nike", "money": 500000, "popularity": 10}]
    elif p["rating"] >= 75:
        sponsors = [{"name": "Gatorade", "money": 200000, "popularity": 5}]
    else:
        sponsors = [{"name": "Local brand", "money": 50000, "popularity": 1}]

    sponsor = random.choice(sponsors)
    p["money"] += sponsor["money"]
    p["popularity"] = min(100, p["popularity"] + sponsor["popularity"])
    p["sponsors"].append(sponsor["name"])

    save(message.from_user.id, p)

    await message.answer(
f"""
💎 <b>Новый спонсор!</b>

🏢 {sponsor['name']}
💰 Контракт: {fmt_money(sponsor['money'])}
⭐ Популярность +{sponsor['popularity']}

Ты заключил спонсорское соглашение!
"""
    )


# ── /help ──────────────────────────────────────────────────────────────────

@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer("""
⚽ <b>Все команды бота</b>

📋 Основные:
/start — Запуск
/create — Создать карьеру
/profile — Профиль
/help — Все команды

⚽ Игровой процесс:
/train — Тренировка
/rest — Отдых
/match — Сыграть матч
/season — Перейти в новый сезон

📊 Статистика:
/stats — Характеристики
/trophies — Трофеи
/table — Таблица лиги
/leaderboard — Топ игроков

🔄 Карьера:
/transfers — Трансферы
/agent — Агент
/contract — Контракт
/sponsor — Спонсоры

👤 Социальное:
/social — Социальные сети
/news — Новости
/personality — Характер

🛒 Магазин:
/shop — Купить экипировку
/boots — Бутсы
/equipment — Экипировка
""")


# ── / ── неизвестные команды ─────────────────────────────────────────────

@dp.message(F.text.startswith("/"))
async def show_commands(message: Message):
    p = load(message.from_user.id)

    if not p or not p.get("created"):
        await message.answer(
            "⚽ <b>Доступные команды</b>\n\n"
            "📋 Основные:\n"
            "/start — Запуск бота\n"
            "/create — Создать карьеру\n"
            "/help — Все команды\n\n"
            "💡 Создай карьеру через /create!"
        )
        return

    await message.answer(
        "⚽ <b>Все команды бота</b>\n\n"
        "📋 Основные:\n"
        "/start — Запуск\n"
        "/create — Создать карьеру\n"
        "/profile — Профиль\n"
        "/help — Все команды\n\n"
        "⚽ Игровой процесс:\n"
        "/train — Тренировка\n"
        "/rest — Отдых\n"
        "/match — Сыграть матч\n"
        "/season — Перейти в новый сезон\n\n"
        "📊 Статистика:\n"
        "/stats — Характеристики\n"
        "/trophies — Трофеи\n"
        "/table — Таблица лиги\n"
        "/leaderboard — Топ игроков\n\n"
        "🔄 Карьера:\n"
        "/transfers — Трансферы\n"
        "/agent — Агент\n"
        "/contract — Контракт\n"
        "/sponsor — Спонсоры\n\n"
        "👤 Социальное:\n"
        "/social — Социальные сети\n"
        "/news — Новости\n"
        "/personality — Характер\n\n"
        "🛒 Магазин:\n"
        "/shop — Купить экипировку\n"
        "/boots — Бутсы\n"
        "/equipment — Экипировка\n\n"
        "💡 Используй /help для подробностей"
    )


# ── запуск ─────────────────────────────────────────────────────────────────

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
