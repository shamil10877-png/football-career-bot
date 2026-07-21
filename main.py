import asyncio
import json
import os
import random

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv(8849485512:AAEhvLOhm7rLwmXoalUx1Wnp5QKCSbFw7O4)

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
    "rating": 60, "potential": 90,
    "matches": 0, "goals": 0, "assists": 0,
    "salary": 0, "money": 0, "market_value": 500000,
    "season": 1, "ucl": 0, "league_titles": 0, "worldcup": 0, "ballon": 0,
    "fitness": 100, "morale": 80, "injured": False,
    "pace": 60, "shooting": 60, "passing": 60,
    "dribbling": 60, "defending": 30, "physical": 55,
    "agent": "Нет",
    "followers": 100, "popularity": 1,
    "professionalism": 50, "leadership": 50, "ambition": 50,
}

def migrate(p: dict) -> dict:
    """Добавляет недостающие поля в старые сохранения."""
    for key, val in DEFAULTS.items():
        if key not in p:
            p[key] = val
    return p

def new_player() -> dict:
    return {
        "created": False,
        "name": "",
        "surname": "",
        "nation": "",
        "position": "",
        "age": 15,
        "height": 170,
        "weight": 65,
        "foot": "Right",
        "number": 9,
        "club": "Свободный агент",
        "rating": 60,
        "potential": 90,
        "matches": 0,
        "goals": 0,
        "assists": 0,
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
    }


# ── хелпер ────────────────────────────────────────────────────────────────

def fmt_money(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M €"
    if n >= 1_000:
        return f"{n / 1_000:.0f}K €"
    return f"{n} €"


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
        age    = int(args[5])
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
        "name":     args[1],
        "surname":  args[2],
        "nation":   args[3],
        "position": args[4].upper(),
        "age":      age,
        "height":   height,
        "weight":   weight,
        "foot":     foot,
        "number":   number,
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

🌍 Страна: {p['nation']}
⚽ Позиция: {p['position']}
🏟 Клуб: {p['club']}

⭐ Рейтинг: {p['rating']}
💎 Потенциал: {p['potential']}

🎂 Возраст: {p['age']}
📏 Рост: {p['height']} см
⚖ Вес: {p['weight']} кг
🦶 Нога: {p['foot']}
🔢 Номер: {p['number']}

💰 Деньги: €{p['money']:,}
💵 Зарплата: €{p['salary']:,}/неделя
💸 Стоимость: €{p['market_value']:,}

🏟 Матчи: {p['matches']}
⚽ Голы: {p['goals']}
🎯 Ассисты: {p['assists']}
"""
)


# ── /save ──────────────────────────────────────────────────────────────────

@dp.message(Command("save"))
async def cmd_save(message: Message):
    p = load(message.from_user.id)
    if not p or not p.get("created"):
        await message.answer("❌ Сначала создай карьеру через /create")
        return
    save(message.from_user.id, p)
    await message.answer("💾 Прогресс сохранён.")


# ── /load ──────────────────────────────────────────────────────────────────

@dp.message(Command("load"))
async def cmd_load(message: Message):
    p = load(message.from_user.id)
    if not p or not p.get("created"):
        await message.answer("❌ Сохранённой карьеры нет.")
        return
    await message.answer("📂 Прогресс загружен.")


# ── /help ──────────────────────────────────────────────────────────────────

@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer("""
⚽ Команды бота

/start — Запуск
/create — Создать карьеру
/profile — Профиль
/train — Тренировка
/rest — Отдых
/match — Сыграть матч
/season — Сезон
/table — Таблица
/contract — Контракты
/transfers — Трансферы
/agent — Агент
/social — Социальные сети
/personality — Характер
/stats — Статистика
/help — Все команды
""")


# ── /train ─────────────────────────────────────────────────────────────────

@dp.message(Command("train"))
async def cmd_train(message: Message):
    p = load(message.from_user.id)
    if not p or not p.get("created"):
        await message.answer("Сначала создай карьеру.")
        return

    if p["injured"]:
        await message.answer("🤕 Ты травмирован и не можешь тренироваться.")
        return

    if p["fitness"] < 20:
        await message.answer("😴 Ты слишком устал.")
        return

    stat = random.choice(["pace", "shooting", "passing", "dribbling", "defending", "physical"])
    gain = random.randint(1, 2)

    p[stat] = min(p[stat] + gain, 99)
    p["fitness"] -= random.randint(8, 15)
    p["morale"] = min(p["morale"] + random.randint(1, 3), 100)
    p["rating"] = int((
        p["pace"] + p["shooting"] + p["passing"] +
        p["dribbling"] + p["defending"] + p["physical"]
    ) / 6)

    injury_msg = ""
    if random.randint(1, 100) <= 5:
        p["injured"] = True
        injury_msg = "\n🤕 На тренировке ты получил травму!"

    save(message.from_user.id, p)

    await message.answer(
f"""
🏋️ Тренировка завершена!

⬆️ Улучшено: {stat}
+{gain}

⭐ Рейтинг: {p["rating"]}
⚡ Форма: {p["fitness"]}%
😊 Мораль: {p["morale"]}%{injury_msg}
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

    if p["injured"]:
        if random.randint(1, 100) <= 40:
            p["injured"] = False
            text = "✅ Ты восстановился после травмы."
        else:
            text = "🤕 Травма ещё не прошла."
    else:
        text = "😴 Ты хорошо отдохнул."

    save(message.from_user.id, p)

    await message.answer(
f"""
{text}

⚡ Форма: {p["fitness"]}%
"""
)



# ── /personality ───────────────────────────────────────────────────────────

@dp.message(Command("personality"))
async def cmd_personality(message: Message):
    p = load(message.from_user.id)
    if not p or not p.get("created"):
        await message.answer("❌ Сначала создай карьеру!")
        return

    await message.answer(
f"""🧠 Характер игрока

💼 Профессионализм: {p.get("professionalism", 50)}/100
👑 Лидерство: {p.get("leadership", 50)}/100
🔥 Амбиции: {p.get("ambition", 50)}/100
"""
    )


# ── /social ────────────────────────────────────────────────────────────────

@dp.message(Command("social"))
async def cmd_social(message: Message):
    p = load(message.from_user.id)
    if not p or not p.get("created"):
        await message.answer("❌ Сначала создай карьеру!")
        return

    await message.answer(
f"""📱 Социальные сети

👥 Подписчики: {p.get("followers", 100):,}
⭐ Популярность: {p.get("popularity", 1)}/100
"""
    )


# ── /agent ─────────────────────────────────────────────────────────────────

AGENTS = {
    "bad":    ("Плохой агент",   25_000),
    "medium": ("Средний агент",  55_000),
    "good":   ("Хороший агент",  90_000),
}

def agent_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="😐 Плохой агент — €25,000",  callback_data="hire_agent:bad")],
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
            f"💰 Деньги: €{p['money']:,}"
        )
        return

    await message.answer(
        f"🧑‍💼 <b>Выбери агента</b>\n\n"
        f"💰 Твои деньги: €{p['money']:,}\n\n"
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
        await call.answer(f"❌ Недостаточно денег. Нужно €{cost:,}", show_alert=True)
        return

    p["money"] -= cost
    p["agent"] = name
    save(uid, p)

    await call.message.edit_text(
        f"✅ Ты нанял <b>{name}</b>!\n\n"
        f"Агент будет искать для тебя новые клубы.\n\n"
        f"💰 Осталось денег: €{p['money']:,}"
    )


# ── /match ─────────────────────────────────────────────────────────────────

@dp.message(Command("match"))
async def cmd_match(message: Message):
    p = load(message.from_user.id)
    if not p or not p.get("created"):
        await message.answer("❌ Сначала создай карьеру: /create")
        return

    goals   = random.randint(0, 3)
    assists = random.randint(0, 2)
    score   = random.randint(5, 10)
    bonus   = goals * p["salary"] // 10

    p["matches"] += 1
    p["goals"]   += goals
    p["assists"] += assists
    p["money"]   += bonus
    save(message.from_user.id, p)

    bonus_line = f"\n💵 Бонус: +{fmt_money(bonus)}" if bonus > 0 else ""
    await message.answer(
        f"🏟 <b>Матч окончен!</b>\n\n"
        f"⚽ Голы: {goals}\n"
        f"🎯 Ассисты: {assists}\n"
        f"⭐ Оценка: {score}/10"
        f"{bonus_line}"
    )


# ── /season ────────────────────────────────────────────────────────────────

@dp.message(Command("season"))
async def cmd_season(message: Message):
    p = load(message.from_user.id)
    if not p or not p.get("created"):
        await message.answer("❌ Сначала создай карьеру: /create")
        return

    ucl    = random.randint(0, 1)
    league = random.randint(0, 1)
    wc     = random.randint(0, 1) if p["nation"] in ("Brazil", "France", "Germany", "England", "Spain", "Argentina", "Portugal") else 0

    ballon_won = p["goals"] > 30 and p["rating"] >= 90
    if ballon_won:
        p["ballon"] += 1

    # рост зарплаты и стоимости
    salary_raise = int(p["rating"] * 1000)
    p["salary"] = salary_raise
    p["market_value"] = int(p["rating"] * 100_000)
    p["money"] += p["salary"] * 12

    p["ucl"]          += ucl
    p["league_titles"] += league
    p["worldcup"]     += wc
    p["season"]       += 1
    p["age"]          += 1
    p["goals"]         = 0
    p["assists"]       = 0
    p["matches"]       = 0
    save(message.from_user.id, p)

    ballon_line = "🏅 <b>Ты выиграл Золотой мяч!</b>" if ballon_won else "❌ Золотой мяч не получен"
    await message.answer(
        f"📅 <b>Сезон завершён!</b>\n\n"
        f"🏆 Лига чемпионов: {'✅ Да' if ucl else '❌ Нет'}\n"
        f"🥇 Чемпионат: {'✅ Да' if league else '❌ Нет'}\n"
        f"🌍 ЧМ: {'✅ Да' if wc else '❌ Нет'}\n"
        f"{ballon_line}\n\n"
        f"💰 Зарплата: {fmt_money(p['salary'])}/мес\n"
        f"📈 Рыночная стоимость: {fmt_money(p['market_value'])}\n\n"
        f"Начинается сезон {p['season']}. Тебе {p['age']} лет."
    )


# ── /trophies ──────────────────────────────────────────────────────────────

@dp.message(Command("trophies"))
async def cmd_trophies(message: Message):
    p = load(message.from_user.id)
    if not p or not p.get("created"):
        await message.answer("❌ Сначала создай карьеру: /create")
        return

    await message.answer(
        f"🏆 <b>Трофеи {p['name']} {p['surname']}</b>\n\n"
        f"🏆 Лига чемпионов: {p['ucl']}\n"
        f"🥇 Чемпионаты: {p['league_titles']}\n"
        f"🌍 Чемпионаты мира: {p['worldcup']}\n"
        f"🏅 Золотой мяч: {p['ballon']}"
    )


# ── /stats ─────────────────────────────────────────────────────────────────

@dp.message(Command("stats"))
async def cmd_stats(message: Message):
    p = load(message.from_user.id)
    if not p or not p.get("created"):
        await message.answer("❌ Сначала создай карьеру!")
        return

    await message.answer(
f"""📊 Статистика {p["name"]} {p["surname"]}

⚽ Голы: {p["goals"]}
🎯 Ассисты: {p["assists"]}
🎮 Матчей: {p["matches"]}

🏃 Скорость: {p["pace"]}
🎯 Удар: {p["shooting"]}
🔄 Пас: {p["passing"]}
🌀 Дриблинг: {p["dribbling"]}
🛡 Защита: {p["defending"]}
💪 Физика: {p["physical"]}

⚡ Форма: {p["fitness"]}%
😊 Мораль: {p["morale"]}%
🤕 Травма: {"Да" if p["injured"] else "Нет"}
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
        lines.append(f"{medal} {team} — {pts} оч{mark}")

    await message.answer("\n".join(lines))


# ── /contract ──────────────────────────────────────────────────────────────

@dp.message(Command("contract"))
async def cmd_contract(message: Message):
    p = load(message.from_user.id)
    if not p or not p.get("created"):
        await message.answer("❌ Сначала создай карьеру!")
        return

    await message.answer(
f"""📄 <b>Контракт</b>

🏟 Клуб: {p["club"]}
💵 Зарплата: €{p["salary"]:,}/неделя
📈 Рыночная стоимость: €{p["market_value"]:,}

💰 Деньги: €{p["money"]:,}
🧑‍💼 Агент: {p["agent"]}
"""
    )


# ── /transfers ─────────────────────────────────────────────────────────────

TRANSFER_CLUBS = [
    ("Манчестер Сити", 200_000),
    ("Реал Мадрид",    250_000),
    ("Барселона",      220_000),
    ("Бавария",        190_000),
    ("ПСЖ",            230_000),
    ("Ливерпуль",      180_000),
    ("Ювентус",        170_000),
    ("Челси",          160_000),
]

def transfer_keyboard() -> InlineKeyboardMarkup:
    offers = random.sample(TRANSFER_CLUBS, 3)
    buttons = [
        [InlineKeyboardButton(
            text=f"🏟 {club} — €{sal:,}/нед",
            callback_data=f"transfer:{club}:{sal}"
        )]
        for club, sal in offers
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@dp.message(Command("transfers"))
async def cmd_transfers(message: Message):
    p = load(message.from_user.id)
    if not p or not p.get("created"):
        await message.answer("❌ Сначала создай карьеру!")
        return

    if p.get("agent", "Нет") == "Нет":
        await message.answer("❌ Для трансферов нужен агент. Найми через /agent")
        return

    await message.answer(
        f"✈️ <b>Трансферные предложения</b>\n\n"
        f"Сейчас ты в: <b>{p['club']}</b>\n"
        f"Выбери новый клуб:",
        reply_markup=transfer_keyboard()
    )

@dp.callback_query(F.data.startswith("transfer:"))
async def cb_transfer(call: CallbackQuery):
    uid = call.from_user.id
    p = load(uid)
    if not p or not p.get("created"):
        await call.answer("❌ Сначала создай карьеру!", show_alert=True)
        return

    parts = ca
