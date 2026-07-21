import asyncio
import json
import os
import random
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import web

TOKEN = "8849485512:AAEhvLOhm7rLwmXoalUx1Wnp5QKCSbFw7O4"

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher(storage=MemoryStorage())

SAVE_DIR = "players"
os.makedirs(SAVE_DIR, exist_ok=True)

HISTORY_DIR = "history"
os.makedirs(HISTORY_DIR, exist_ok=True)


def save_file(user_id):
    return os.path.join(SAVE_DIR, f"{user_id}.json")


def save(user_id, data):
    with open(save_file(user_id), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def load(user_id):
    path = save_file(user_id)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def save_history(user_id, data):
    path = os.path.join(HISTORY_DIR, f"{user_id}.json")
    history = []
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            history = json.load(f)
    history.append(data)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=4)


def load_history(user_id):
    path = os.path.join(HISTORY_DIR, f"{user_id}.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def money(x):
    if x >= 1000000:
        return f"{x//1000000}M €"
    if x >= 1000:
        return f"{x//1000}K €"
    return f"{x} €"


def get_clubs_by_rating(rating):
    if rating >= 85:
        return [
            ("Реал Мадрид", 300000, 95),
            ("Барселона", 280000, 93),
            ("Манчестер Сити", 290000, 94),
            ("Бавария", 270000, 92),
            ("ПСЖ", 260000, 91),
            ("Ливерпуль", 250000, 90),
        ]
    elif rating >= 75:
        return [
            ("Челси", 180000, 85),
            ("Ювентус", 170000, 84),
            ("Атлетико", 160000, 83),
            ("Арсенал", 150000, 82),
            ("Боруссия Дортмунд", 140000, 80),
        ]
    elif rating >= 65:
        return [
            ("Вест Хэм", 100000, 75),
            ("Валенсия", 90000, 73),
            ("Лацио", 85000, 72),
            ("Лилль", 80000, 70),
            ("Севилья", 95000, 74),
        ]
    else:
        return [
            ("Кристал Пэлас", 40000, 65),
            ("Хоффенхайм", 35000, 62),
            ("Болонья", 30000, 60),
            ("Ренн", 25000, 58),
            ("Эспаньол", 20000, 55),
        ]


def get_all_clubs():
    return [
        ("Реал Мадрид", 95),
        ("Барселона", 93),
        ("Манчестер Сити", 94),
        ("Бавария", 92),
        ("ПСЖ", 91),
        ("Ливерпуль", 90),
        ("Челси", 85),
        ("Ювентус", 84),
        ("Атлетико", 83),
        ("Арсенал", 82),
        ("Боруссия Дортмунд", 80),
        ("Вест Хэм", 75),
        ("Валенсия", 73),
        ("Лацио", 72),
        ("Лилль", 70),
        ("Севилья", 74),
        ("Кристал Пэлас", 65),
        ("Хоффенхайм", 62),
        ("Болонья", 60),
        ("Ренн", 58),
        ("Эспаньол", 55),
    ]


def new_player(name):
    now = datetime.now()
    return {
        "created": True,
        "name": name,
        "club": "Свободный агент",
        "rating": 60,
        "potential": 90,
        "age": 16,
        "season": 1,
        "week": 1,
        "matches": 0,
        "goals": 0,
        "assists": 0,
        "mvps": 0,
        "salary": 0,
        "money": 50000,
        "market_value": 500000,
        "fitness": 100,
        "morale": 100,
        "pace": 60,
        "shooting": 60,
        "passing": 60,
        "dribbling": 60,
        "defending": 35,
        "physical": 55,
        "followers": 100,
        "popularity": 1,
        "ucl": 0,
        "league_titles": 0,
        "worldcup": 0,
        "ballon": 0,
        "agent": "Нет",
        "boots": "Обычные",
        "equipment": "Стандартная",
        "trophies": [],
        "club_history": [],
        "retired": False,
        "injured": False,
        "injury_days": 0,
        "sponsors": [],
        "reputation": 50,
        "house": "Нет",
        "houses": [],
        "rental_income": 0,
        "car": "Нет",
        "cars": [],
        "business": False,
        "business_type": "Нет",
        "business_income": 0,
        "wife": None,
        "children": 0,
        "relationship_days": 0,
        "last_daily": now.isoformat(),
        "goals_career": 0,
        "assists_career": 0,
        "matches_career": 0,
        "mvps_career": 0,
        "ucl_career": 0,
        "league_titles_career": 0,
        "worldcup_career": 0,
        "ballon_career": 0,
        "league_points": 0,
        "ucl_points": 0,
        "league_matches": 0,
        "ucl_matches": 0,
        "last_ucl_week": 0,
        "worldcup_year": 0,
        "euro_year": 0,
        "club_teams": [],
    }


def add_history(player, user_id):
    history_data = {
        "name": player["name"],
        "rating": player["rating"],
        "goals": player["goals_career"],
        "assists": player["assists_career"],
        "matches": player["matches_career"],
        "mvps": player["mvps_career"],
        "ucl": player["ucl_career"],
        "league_titles": player["league_titles_career"],
        "worldcup": player["worldcup_career"],
        "ballon": player["ballon_career"],
        "trophies": player["trophies"],
        "age": player["age"],
        "season": player["season"],
    }
    save_history(user_id, history_data)


@dp.message(Command("start"))
async def start(message: Message):
    p = load(message.from_user.id)
    if p:
        await message.answer(
            f"👋 Добро пожаловать обратно, <b>{p['name']}</b>!\n\n"
            "📅 Неделя: " + str(p.get("week", 1)) + "\n"
            "🏆 Сезон: " + str(p.get("season", 1)) + "\n\n"
            "Используй /help чтобы посмотреть команды."
        )
    else:
        await message.answer(
            "⚽ <b>Football Career</b>\n\n"
            "Создай карьеру:\n"
            "<code>/create Имя</code>\n\n"
            "Пример:\n"
            "<code>/create Alex</code>"
        )


@dp.message(Command("help"))
async def help_cmd(message: Message):
    await message.answer(
        "📖 <b>Команды</b>\n\n"
        "/profile — профиль\n"
        "/train — тренировка\n"
        "/match — матч\n"
        "/rest — отдых\n"
        "/calendar — календарь\n"
        "/transfers — трансферы\n"
        "/agent — агент\n"
        "/shop — магазин\n"
        "/stats — статистика\n"
        "/trophies — трофеи\n"
        "/news — новости\n"
        "/table — таблица\n"
        "/ucl — лига чемпионов\n"
        "/contract — контракт\n"
        "/sponsor — спонсоры\n"
        "/daily — ежедневный бонус\n"
        "/national — сборная\n"
        "/goldenboot — золотая бутса\n"
        "/cars — купить машину\n"
        "/house — купить/сдать дом\n"
        "/family — семья\n"
        "/business — бизнес\n"
        "/history — предыдущие карьеры\n"
        "/ping — проверка бота\n"
        "/help — помощь"
    )


@dp.message(Command("ping"))
async def ping(message: Message):
    await message.answer("🏓 Pong! Бот работает!")


@dp.message(Command("create"))
async def create(message: Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("❌ Используй: /create Имя")
        return

    name = args[1]
    player = new_player(name)
    save(message.from_user.id, player)

    await message.answer(
        f"✅ Карьера создана!\n\n"
        f"👤 Игрок: <b>{name}</b>\n"
        f"⭐ Рейтинг: 60\n"
        f"🏟 Клуб: Свободный агент"
    )


@dp.message(Command("profile"))
async def profile(message: Message):
    p = load(message.from_user.id)
    if not p:
        await message.answer("❌ Сначала создай карьеру: /create")
        return

    await message.answer(
        f"""👤 <b>{p['name']}</b>

⭐ Рейтинг: {p['rating']}
🌟 Потенциал: {p['potential']}

🏟 Клуб: {p['club']}
🎂 Возраст: {p['age']}

💰 Деньги: {money(p['money'])}
💵 Зарплата: {money(p['salary'])}/нед
📈 Стоимость: {money(p['market_value'])}

⚽ Матчи: {p['matches']}
🥅 Голы: {p['goals']}
🎯 Ассисты: {p['assists']}
🏅 MVP: {p['mvps']}

🏃 Скорость: {p['pace']}
🎯 Удар: {p['shooting']}
🎨 Пас: {p['passing']}
🪄 Дриблинг: {p['dribbling']}
🛡 Защита: {p['defending']}
💪 Физика: {p['physical']}

⚡ Форма: {p['fitness']}%
😊 Мораль: {p['morale']}%

👥 Подписчики: {p['followers']}
🔥 Популярность: {p['popularity']}

👟 Бутсы: {p['boots']}
🎽 Экипировка: {p['equipment']}
🏠 Дом: {p.get('house', 'Нет')}
💰 Аренда: {money(p.get('rental_income', 0))}/нед
🚗 Машина: {p.get('car', 'Нет')}
❤️ Семья: {p.get('wife', 'Нет')}, {p.get('children', 0)} детей
"""
    )


@dp.message(Command("train"))
async def train(message: Message):
    p = load(message.from_user.id)
    if not p:
        await message.answer("❌ Сначала создай карьеру.")
        return

    if p.get("retired"):
        await message.answer("❌ Ты завершил карьеру!")
        return

    if p["fitness"] < 20:
        await message.answer("😴 Ты устал. Используй /rest")
        return

    stat = random.choice(["pace", "shooting", "passing", "dribbling", "defending", "physical"])
    stat_names = {
        "pace": "Скорость", "shooting": "Удар", "passing": "Пас",
        "dribbling": "Дриблинг", "defending": "Защита", "physical": "Физика"
    }

    plus = random.randint(1, 3)
    p[stat] = min(99, p[stat] + plus)
    p["fitness"] -= random.randint(10, 20)
    p["morale"] = min(100, p["morale"] + 2)

    p["rating"] = int((p["pace"] + p["shooting"] + p["passing"] + p["dribbling"] + p["defending"] + p["physical"]) / 6)

    save(message.from_user.id, p)

    await message.answer(
        f"""🏋️ Тренировка завершена!

⬆️ +{plus} к {stat_names[stat]}
⭐ Рейтинг: {p['rating']}
⚡ Форма: {p['fitness']}%
"""
    )


@dp.message(Command("match"))
async def match_cmd(message: Message):
    p = load(message.from_user.id)
    if not p:
        await message.answer("❌ Сначала создай карьеру.")
        return

    if p.get("retired"):
        await message.answer("❌ Ты завершил карьеру!")
        return

    if p.get("injured"):
        await message.answer(f"🤕 Ты травмирован! Осталось {p['injury_days']} дней.")
        return

    if p["fitness"] < 15:
        await message.answer("😴 Ты слишком устал. Используй /rest")
        return

    # Симуляция матча
    goals = random.randint(0, max(1, p["rating"] // 35))
    assists = random.randint(0, max(1, p["rating"] // 45))
    mvp = random.randint(1, 100) <= p["rating"] - 40

    # Результат матча (победа/ничья/поражение) — +3/+1/0
    result_num = random.randint(1, 100)
    if result_num <= 40 + (p["rating"] - 60) // 2:
        result = "win"
        points = 3
    elif result_num <= 60 + (p["rating"] - 60) // 2:
        result = "draw"
        points = 1
    else:
        result = "lose"
        points = 0

    # Обновление статистики
    p["matches"] += 1
    p["goals"] += goals
    p["assists"] += assists
    p["matches_career"] += 1
    p["goals_career"] += goals
    p["assists_career"] += assists
    p["league_matches"] = p.get("league_matches", 0) + 1
    p["league_points"] = p.get("league_points", 0) + points

    if mvp:
        p["mvps"] += 1
        p["mvps_career"] += 1

    # Рейтинг от голов + ассистов
    gain = goals * 0.35 + assists * 0.20 + (0.50 if mvp else 0)
    if result == "win":
        gain += 0.30
    elif result == "draw":
        gain += 0.10
    p["rating"] = round(min(99, p["rating"] + gain), 1)

    # Доходы (уменьшены)
    reward = goals * 8000 + assists * 5000 + (15000 if mvp else 0)
    if result == "win":
        reward += 5000
    p["money"] += reward
    p["market_value"] = int(p["rating"] * 120000)
    p["fitness"] = max(0, p["fitness"] - random.randint(10, 20))

    followers_gain = random.randint(50, 300) + goals * 80 + assists * 40
    if mvp:
        followers_gain += 300
    if result == "win":
        followers_gain += 200
    p["followers"] += followers_gain

    p["week"] += 1

    # Лига чемпионов (каждые 2 недели)
    ucl_text = ""
    if p.get("last_ucl_week", 0) == 0 or p["week"] - p["last_ucl_week"] >= 2:
        ucl_goals = random.randint(0, max(1, p["rating"] // 35))
        ucl_assists = random.randint(0, max(1, p["rating"] // 45))
        ucl_mvp = random.randint(1, 100) <= p["rating"] - 40

        ucl_result_num = random.randint(1, 100)
        if ucl_result_num <= 40 + (p["rating"] - 60) // 2:
            ucl_result = "win"
            ucl_points = 3
        elif ucl_result_num <= 60 + (p["rating"] - 60) // 2:
            ucl_result = "draw"
            ucl_points = 1
        else:
            ucl_result = "lose"
            ucl_points = 0

        p["ucl_matches"] = p.get("ucl_matches", 0) + 1
        p["ucl_points"] = p.get("ucl_points", 0) + ucl_points
        p["goals"] += ucl_goals
        p["assists"] += ucl_assists
        p["goals_career"] += ucl_goals
        p["assists_career"] += ucl_assists

        if ucl_mvp:
            p["mvps"] += 1
            p["mvps_career"] += 1

        p["last_ucl_week"] = p["week"]

        ucl_reward = ucl_goals * 10000 + ucl_assists * 6000 + (20000 if ucl_mvp else 0)
        p["money"] += ucl_reward

        ucl_text = f"""
⭐ <b>Лига чемпионов!</b>
⚽ Голы: {ucl_goals}
🎯 Ассисты: {ucl_assists}
📊 Результат: {ucl_result}
📊 Очков: +{ucl_points}
💰 Бонус: {money(ucl_reward)}"""

    # Чемпионат мира (каждые 4 года)
    wc_text = ""
    if p["season"] % 4 == 0 and p["season"] != p.get("worldcup_year", 0):
        p["worldcup_year"] = p["season"]
        wc_goals = random.randint(0, 2)
        wc_assists = random.randint(0, 1)
        wc_win = random.choice([True, False])

        p["goals"] += wc_goals
        p["assists"] += wc_assists
        p["goals_career"] += wc_goals
        p["assists_career"] += wc_assists

        if wc_win:
            p["worldcup"] += 1
            p["worldcup_career"] += 1
            p["trophies"].append("🌍 Чемпионат мира")
            p["followers"] += 15000
            p["money"] += 100000

        wc_text = f"""
🌍 <b>Чемпионат мира!</b>
⚽ Голы: {wc_goals}
🎯 Ассисты: {wc_assists}
🏆 {'Победа! 🏆' if wc_win else 'Поражение'}"""

    # Евро (каждые 4 года, со сдвигом)
    euro_text = ""
    if p["season"] % 4 == 2 and p["season"] != p.get("euro_year", 0):
        p["euro_year"] = p["season"]
        euro_goals = random.randint(0, 2)
        euro_assists = random.randint(0, 1)
        euro_win = random.choice([True, False])

        p["goals"] += euro_goals
        p["assists"] += euro_assists
        p["goals_career"] += euro_goals
        p["assists_career"] += euro_assists

        if euro_win:
            p["trophies"].append("🏆 Евро")
            p["followers"] += 10000
            p["money"] += 80000

        euro_text = f"""
🏆 <b>Евро!</b>
⚽ Голы: {euro_goals}
🎯 Ассисты: {euro_assists}
🏆 {'Победа! 🏆' if euro_win else 'Поражение'}"""

    # Проверка завершения сезона (38 матчей в лиге)
    season_text = ""
    if p["league_matches"] >= 38:
        p["season"] += 1
        p["age"] += 1
        p["week"] = 1
        p["league_matches"] = 0
        p["league_points"] = 0
        p["ucl_matches"] = 0
        p["ucl_points"] = 0
        p["goals"] = 0
        p["assists"] = 0
        p["matches"] = 0

        # Трофеи по итогам сезона
        if p.get("league_points", 0) >= 80:
            p["league_titles"] += 1
            p["league_titles_career"] += 1
            p["trophies"].append("🏆 Чемпионат")
            p["followers"] += 5000

        if p.get("ucl_points", 0) >= 15:
            p["ucl"] += 1
            p["ucl_career"] += 1
            p["trophies"].append("⭐ Лига чемпионов")
            p["followers"] += 10000

        # Рост рейтинга с возрастом
        if p["age"] < 30:
            p["rating"] = min(99, p["rating"] + random.uniform(1, 3))

        p["salary"] = int(p["rating"] * 5000)
        p["market_value"] = int(p["rating"] * 150000)
        p["money"] += p["salary"] * 52

        # Проверка завершения карьеры (41 год)
        if p["age"] >= 41:
            p["retired"] = True
            add_history(p, message.from_user.id)
            save(message.from_user.id, p)
            await message.answer(
                f"🔚 <b>Ты завершил карьеру в возрасте {p['age']} лет!</b>\n\n"
                f"👤 {p['name']}\n"
                f"⭐ Итоговый рейтинг: {p['rating']}\n"
                f"🏆 Трофеев: {p['ucl_career'] + p['league_titles_career'] + p['worldcup_career'] + p['ballon_career']}\n"
                f"⚽ Голов: {p['goals_career']}\n"
                f"🎯 Ассистов: {p['assists_career']}"
            )
            return

        season_text = f"\n📅 <b>Сезон завершён!</b> Начинается сезон {p['season']}"

    save(message.from_user.id, p)

    result_text = "🏆 Победа!" if result == "win" else "🤝 Ничья" if result == "draw" else "❌ Поражение"

    await message.answer(
        f"""🏟 Матч окончен!

📊 Результат: {result_text} (+{points} очков)
⚽ Голы: {goals}
🎯 Ассисты: {assists}
⭐ MVP: {"Да" if mvp else "Нет"}

📈 Рейтинг: {p['rating']}
💰 Получено: {money(reward)}
💎 Стоимость: {money(p['market_value'])}

⚡ Форма: {p['fitness']}%
👥 +{followers_gain} подписчиков
📊 Очков в лиге: {p.get('league_points', 0)}
📊 Матчей в лиге: {p.get('league_matches', 0)}/38
{ucl_text}
{wc_text}
{euro_text}
{season_text}
"""
    )


@dp.message(Command("rest"))
async def rest_cmd(message: Message):
    p = load(message.from_user.id)
    if not p:
        await message.answer("❌ Сначала создай карьеру.")
        return

    p["fitness"] = min(100, p["fitness"] + 30)
    p["morale"] = min(100, p["morale"] + 10)

    if p.get("injured"):
        p["injury_days"] -= 1
        if p["injury_days"] <= 0:
            p["injured"] = False
            p["injury_days"] = 0
            recovery_msg = "✅ Ты полностью восстановился!"
        else:
            recovery_msg = f"🤕 Осталось {p['injury_days']} дней."
    else:
        recovery_msg = ""

    save(message.from_user.id, p)

    await message.answer(
        f"""😴 Отдых завершён!

⚡ Форма: {p['fitness']}%
😊 Мораль: {p['morale']}%
{recovery_msg}
"""
    )


@dp.message(Command("calendar"))
async def calendar_cmd(message: Message):
    p = load(message.from_user.id)
    if not p:
        await message.answer("❌ Сначала создай карьеру.")
        return

    next_ucl = "Следующая неделя" if p.get("last_ucl_week", 0) == 0 or p["week"] - p["last_ucl_week"] >= 1 else f"Через {2 - (p['week'] - p['last_ucl_week'])} недели"

    await message.answer(
        f"""📅 <b>Календарь</b>

🏆 Сезон: {p['season']}
📆 Неделя: {p.get('week', 1)} из 38

📊 Статистика сезона:
⚽ Голов: {p['goals']}
🎯 Ассистов: {p['assists']}
🎮 Матчей: {p['matches']}
📊 Очков: {p.get('league_points', 0)}
🏟 Лига: {p.get('league_matches', 0)}/38 матчей

⭐ Лига чемпионов: {next_ucl}
"""
    )


@dp.message(Command("daily"))
async def daily(message: Message):
    p = load(message.from_user.id)
    if not p:
        await message.answer("❌ Сначала создай карьеру.")
        return

    now = datetime.now()
    last_daily = datetime.fromisoformat(p.get("last_daily", now.isoformat()))

    if (now - last_daily).days < 1:
        await message.answer("⏳ Бонус уже получен! Приходи через 24 часа.")
        return

    reward = random.randint(10000, 50000)
    p["money"] += reward
    p["last_daily"] = now.isoformat()

    save(message.from_user.id, p)

    await message.answer(f"🎁 <b>Ежедневный бонус!</b>\n\n💰 +{money(reward)}")


@dp.message(Command("national"))
async def national(message: Message):
    p = load(message.from_user.id)
    if not p:
        await message.answer("❌ Сначала создай карьеру.")
        return

    if not p.get("national_team"):
        if p["rating"] < 75:
            await message.answer(
                f"""🇦🇿 <b>Сборная</b>

Тренер пока не вызывает тебя.
⭐ Нужно минимум 75 рейтинга.
Твой рейтинг: {p['rating']}
"""
            )
            return

        p["national_team"] = True
        save(message.from_user.id, p)
        await message.answer("🇦🇿 Поздравляем! Ты вызван в сборную!")
        return

    goals = random.randint(0, 2)
    assists = random.randint(0, 1)
    result = random.choice(["Победа", "Ничья", "Поражение"])

    p["national_matches"] += 1
    p["national_goals"] += goals
    p["matches"] += 1
    p["goals"] += goals
    p["assists"] += assists

    save(message.from_user.id, p)

    await message.answer(
        f"""🇦🇿 <b>Матч за сборную</b>

📊 Результат: {result}
⚽ Голы: {goals}
🎯 Ассисты: {assists}
📈 Всего матчей: {p['national_matches']}
🥅 Всего голов: {p['national_goals']}
"""
    )


@dp.message(Command("sponsor"))
async def sponsor(message: Message):
    p = load(message.from_user.id)
    if not p:
        await message.answer("❌ Сначала создай карьеру.")
        return

    sponsors = [
        ("Nike", 500000),
        ("Adidas", 450000),
        ("Puma", 300000),
        ("EA Sports", 700000),
        ("Red Bull", 400000),
        ("Coca-Cola", 350000),
        ("Pepsi", 320000)
    ]

    if p["followers"] < 10000:
        await message.answer("❌ Нужно минимум 10 000 подписчиков.")
        return

    name, reward = random.choice(sponsors)
    p["money"] += reward
    if name not in p["sponsors"]:
        p["sponsors"].append(name)

    save(message.from_user.id, p)

    await message.answer(
        f"""🤝 <b>Новый спонсор!</b>

🏢 Компания: {name}
💰 Контракт: {money(reward)}
"""
    )


@dp.message(Command("goldenboot"))
async def goldenboot(message: Message):
    p = load(message.from_user.id)
    if not p:
        await message.answer("❌ Сначала создай карьеру.")
        return

    if p["goals"] < 25:
        await message.answer(
            f"""👟 <b>Золотая бутса</b>

❌ Пока недостаточно голов.
⚽ Голов: {p['goals']}
🎯 Нужно минимум: 25
"""
        )
        return

    prize = 500000
    p["money"] += prize
    p["rating"] += 2

    if "Золотая бутса" not in p["trophies"]:
        p["trophies"].append("Золотая бутса")

    save(message.from_user.id, p)

    await message.answer(
        f"""👟🏆 <b>Ты выиграл Золотую бутсу!</b>

💰 Призовые: {money(prize)}
⭐ Рейтинг +2
"""
    )


@dp.message(Command("cars"))
async def cars(message: Message):
    p = load(message.from_user.id)
    if not p:
        await message.answer("❌ Сначала создай карьеру.")
        return

    if "cars" not in p:
        p["cars"] = []

    cars_list = [
        ("Lada Granta", 2000),
        ("Kia Rio", 8000),
        ("Hyundai Solaris", 12000),
        ("Toyota Camry", 25000),
        ("BMW X5", 60000),
        ("Mercedes S-Class", 120000),
        ("Porsche 911", 250000),
        ("Lamborghini Huracan", 500000),
        ("Bugatti Chiron", 3000000),
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{car} — {money(price)}", callback_data=f"car:{car}:{price}")]
        for car, price in cars_list
    ])

    await message.answer(
        f"""🚗 <b>Автосалон</b>

💰 Деньги: {money(p['money'])}
🚘 Твоя машина: {p.get('car', 'Нет')}

Выбери машину:
""",
        reply_markup=keyboard
    )


@dp.callback_query(F.data.startswith("car:"))
async def car_cb(call: CallbackQuery):
    uid = call.from_user.id
    p = load(uid)
    if not p:
        await call.answer("❌ Сначала создай карьеру!", show_alert=True)
        return

    parts = call.data.split(":")
    car = parts[1]
    price = int(parts[2])

    if p["money"] < price:
        await call.answer(f"❌ Нужно {money(price)}", show_alert=True)
        return

    p["money"] -= price
    p["cars"].append(car)
    p["car"] = car

    save(uid, p)

    await call.message.edit_text(
        f"""🚗 <b>Покупка завершена!</b>

🚘 Машина: {car}
💰 Цена: {money(price)}
💵 Осталось: {money(p['money'])}
"""
    )


@dp.message(Command("house"))
async def house(message: Message):
    p = load(message.from_user.id)
    if not p:
        await message.answer("❌ Сначала создай карьеру.")
        return

    if "houses" not in p:
        p["houses"] = []

    houses_list = [
        ("Квартира", 150000, 5000),
        ("Дом", 500000, 15000),
        ("Вилла", 1500000, 50000),
        ("Особняк", 5000000, 150000),
        ("Замок", 15000000, 500000),
    ]

    if p.get("house") != "Нет":
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Сдать в аренду", callback_data="rent:house")]
        ])
        await message.answer(
            f"""🏠 <b>Твой дом</b>

🏡 Дом: {p['house']}
💰 Доход от аренды: {money(p.get('rental_income', 0))}/нед

Используй /house чтобы сдать в аренду или посмотреть другие дома.
""",
            reply_markup=keyboard
        )
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{home} — {money(price)} (аренда {money(rent)}/нед)", callback_data=f"house:{home}:{price}:{rent}")]
        for home, price, rent in houses_list
    ])

    await message.answer(
        f"""🏠 <b>Недвижимость</b>

💰 Деньги: {money(p['money'])}
🏠 Твой дом: {p.get('house', 'Нет')}

Выбери дом:
""",
        reply_markup=keyboard
    )


@dp.callback_query(F.data.startswith("house:"))
async def house_cb(call: CallbackQuery):
    uid = call.from_user.id
    p = load(uid)
    if not p:
        await call.answer("❌ Сначала создай карьеру!", show_alert=True)
        return

    parts = call.data.split(":")
    home = parts[1]
    price = int(parts[2])
    rent = int(parts[3])

    if p["money"] < price:
        await call.answer(f"❌ Нужно {money(price)}", show_alert=True)
        return

    p["money"] -= price
    p["houses"].append(home)
    p["house"] = home
    p["rental_income"] = rent

    save(uid, p)

    await call.message.edit_text(
        f"""🏠 <b>Поздравляем!</b>

🏡 Ты купил: {home}
💰 Цена: {money(price)}
💵 Аренда: {money(rent)}/нед
💵 Осталось: {money(p['money'])}
"""
    )


@dp.callback_query(F.data.startswith("rent:"))
async def rent_cb(call: CallbackQuery):
    uid = call.from_user.id
    p = load(uid)
    if not p:
        await call.answer("❌ Сначала создай карьеру!", show_alert=True)
        return

    if p.get("house") == "Нет":
        await call.answer("У тебя нет дома!", show_alert=True)
        return

    rent = p.get("rental_income", 0)
    if rent > 0:
        p["money"] += rent * 4  # доход за месяц
        await call.answer(f"🏠 Сдано в аренду!\n💰 Получено: {money(rent * 4)}", show_alert=True)
        save(uid, p)
        await call.message.edit_text(
            f"""🏠 <b>Дом сдан в аренду!</b>

🏡 Дом: {p['house']}
💰 Доход: {money(rent * 4)}
💵 Всего денег: {money(p['money'])}
"""
        )
    else:
        await call.answer("Этот дом не приносит дохода.", show_alert=True)


@dp.message(Command("family"))
async def family(message: Message):
    p = load(message.from_user.id)
    if not p:
        await message.answer("❌ Сначала создай карьеру.")
        return

    if p.get("retired"):
        await message.answer("❌ Ты завершил карьеру!")
        return

    if p.get("wife") is None:
        girls = ["Анна", "София", "Виктория", "Мария", "Эмилия", "Диана", "Алина"]
        girl = random.choice(girls)
        p["wife"] = girl
        save(message.from_user.id, p)
        await message.answer(f"💍 <b>Ты начал отношения!</b>\n\n❤️ Девушка: {girl}")
        return

    p["relationship_days"] = p.get("relationship_days", 0) + 1

    if p["relationship_days"] >= 30 and random.randint(1, 100) <= 20:
        p["children"] += 1
        p["relationship_days"] = 0
        save(message.from_user.id, p)
        await message.answer(
            f"""👶 Поздравляем!

У вас с {p['wife']} родился ребёнок!
👨‍👩‍👧 Детей: {p['children']}

💡 Попробуй ещё через месяц."""
        )
    else:
        await message.answer(
            f"""👨‍👩‍👧 <b>Семья</b>

❤️ Жена: {p['wife']}
👶 Детей: {p['children']}
📅 Вместе: {p['relationship_days']} дней

💡 Дети появятся через некоторое время."""
        )


@dp.message(Command("records"))
async def records(message: Message):
    p = load(message.from_user.id)
    if not p:
        await message.answer("❌ Сначала создай карьеру.")
        return

    await message.answer(
        f"""📜 <b>Рекорды</b>

⚽ Голов за карьеру: {p['goals_career']}
🎯 Ассистов: {p['assists_career']}
🎮 Матчей: {p['matches_career']}
⭐ MVP: {p['mvps_career']}

🏆 Лиги: {p['league_titles_career']}
🏆 ЛЧ: {p['ucl_career']}
🌍 ЧМ: {p['worldcup_career']}
🥇 Золотых мячей: {p['ballon_career']}
"""
    )


@dp.message(Command("awards"))
async def awards(message: Message):
    p = load(message.from_user.id)
    if not p:
        await message.answer("❌ Сначала создай карьеру.")
        return

    total = p["league_titles_career"] + p["ucl_career"] + p["worldcup_career"] + p["ballon_career"]

    await message.answer(
        f"""🏅 <b>Достижения</b>

🥇 Всего крупных трофеев: {total}

🏆 Чемпионаты: {p['league_titles_career']}
🏆 Лига чемпионов: {p['ucl_career']}
🌍 Чемпионаты мира: {p['worldcup_career']}
⭐ Золотые мячи: {p['ballon_career']}
"""
    )


@dp.message(Command("business"))
async def business(message: Message):
    p = load(message.from_user.id)
    if not p:
        await message.answer("❌ Сначала создай карьеру.")
        return

    if p.get("business"):
        await message.answer(
            f"""🏢 <b>Твой бизнес</b>

🏢 Тип: {p.get('business_type', 'Нет')}
💰 Доход: {money(p.get('business_income', 0))}/нед
💵 Всего денег: {money(p['money'])}
"""
        )
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏪 Магазин — 30,000", callback_data="business:small")],
        [InlineKeyboardButton(text="🛍️ Торговый центр — 200,000", callback_data="business:medium")],
        [InlineKeyboardButton(text="🏗️ Строительная компания — 500,000", callback_data="business:large")],
    ])

    await message.answer(
        f"""🏢 <b>Бизнес</b>

💰 Деньги: {money(p['money'])}

Выбери бизнес:
""",
        reply_markup=keyboard
    )


@dp.callback_query(F.data.startswith("business:"))
async def business_cb(call: CallbackQuery):
    uid = call.from_user.id
    p = load(uid)
    if not p:
        await call.answer("❌ Сначала создай карьеру!", show_alert=True)
        return

    if p.get("business"):
        await call.answer("У тебя уже есть бизнес!", show_alert=True)
        return

    types = {
        "small": ("🏪 Магазин", 30000, 5000),
        "medium": ("🛍️ Торговый центр", 200000, 25000),
        "large": ("🏗️ Строительная компания", 500000, 60000),
    }

    key = call.data.split(":")[1]
    name, cost, income = types[key]

    if p["money"] < cost:
        await call.answer(f"❌ Нужно {money(cost)}", show_alert=True)
        return

    p["money"] -= cost
    p["business"] = True
    p["business_type"] = name
    p["business_income"] = income

    save(uid, p)

    await call.message.edit_text(
        f"""✅ <b>Бизнес открыт!</b>

🏢 {name}
💰 Доход: {money(income)}/нед
"""
    )


@dp.message(Command("agent"))
async def agent(message: Message):
    p = load(message.from_user.id)
    if not p:
        await message.answer("❌ Сначала создай карьеру.")
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="😐 Плохой агент — €10,000", callback_data="agent:bad:10000")],
        [InlineKeyboardButton(text="🙂 Средний агент — €30,000", callback_data="agent:medium:30000")],
        [InlineKeyboardButton(text="😎 Хороший агент — €70,000", callback_data="agent:good:70000")],
        [InlineKeyboardButton(text="🌟 Топ-агент — €150,000", callback_data="agent:top:150000")],
    ])

    current = p.get("agent", "Нет")
    if current != "Нет":
        await message.answer(
            f"""🧑‍💼 <b>Твой агент</b>

🧑‍💼 Агент: {current}
💰 Деньги: {money(p['money'])}

Хочешь сменить агента? Выбери нового:
""",
            reply_markup=keyboard
        )
        return

    await message.answer(
        f"""🧑‍💼 <b>Выбери агента</b>

💰 Деньги: {money(p['money'])}

Агент помогает с трансферами.
""",
        reply_markup=keyboard
    )


@dp.callback_query(F.data.startswith("agent:"))
async def agent_cb(call: CallbackQuery):
    uid = call.from_user.id
    p = load(uid)
    if not p:
        await call.answer("❌ Сначала создай карьеру!", show_alert=True)
        return

    parts = call.data.split(":")
    agent_type = parts[1]
    cost = int(parts[2])

    agent_names = {
        "bad": "😐 Плохой агент",
        "medium": "🙂 Средний агент",
        "good": "😎 Хороший агент",
        "top": "🌟 Топ-агент"
    }

    name = agent_names[agent_type]

    if p["money"] < cost:
        await call.answer(f"❌ Нужно {money(cost)}", show_alert=True)
        return

    p["money"] -= cost
    p["agent"] = name
    save(uid, p)

    await call.message.edit_text(
        f"""✅ Ты нанял <b>{name}</b>!

💰 Осталось: {money(p['money'])}
"""
    )


@dp.message(Command("transfers"))
async def transfers(message: Message):
    p = load(message.from_user.id)
    if not p:
        await message.answer("❌ Сначала создай карьеру.")
        return

    if p.get("retired"):
        await message.answer("❌ Ты завершил карьеру!")
        return

    if p.get("agent") == "Нет":
        await message.answer("❌ Для трансферов нужен агент. Найми через /agent")
        return

    clubs = get_clubs_by_rating(p["rating"])
    offers = random.sample(clubs, min(3, len(clubs)))

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"🏟 {club} — {money(sal)}/нед",
            callback_data=f"transfer:{club}:{sal}"
        )] for club, sal, _ in offers
    ])

    await message.answer(
        f"""✈️ <b>Трансферные предложения</b>

Текущий клуб: {p['club']}
⭐ Рейтинг: {p['rating']}

Выбери новый клуб:
""",
        reply_markup=keyboard
    )


@dp.callback_query(F.data.startswith("transfer:"))
async def transfer_cb(call: CallbackQuery):
    uid = call.from_user.id
    p = load(uid)
    if not p:
        await call.answer("❌ Сначала создай карьеру!", show_alert=True)
        return

    parts = call.data.split(":")
    club = parts[1]
    salary = int(parts[2])

    old_club = p["club"]
    p["club"] = club
    p["salary"] = salary
    p["club_history"].append(old_club)

    save(uid, p)

    await call.message.edit_text(
        f"""✅ <b>Трансфер совершён!</b>

Ты покинул <b>{old_club}</b>
и перешёл в <b>{club}</b>!

💵 Новая зарплата: {money(salary)}/нед
"""
    )


@dp.message(Command("shop"))
async def shop(message: Message):
    p = load(message.from_user.id)
    if not p:
        await message.answer("❌ Сначала создай карьеру.")
        return

    items = {
        "boots": {"name": "👟 Профессиональные бутсы", "cost": 50000, "stat": "+2 к скорости"},
        "equipment": {"name": "🎽 Профессиональная экипировка", "cost": 30000, "stat": "+1 к физике"},
        "fitness": {"name": "💪 Тренажёрный зал", "cost": 10000, "stat": "+10 к форме"},
    }

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"{item['name']} — {money(item['cost'])}",
            callback_data=f"shop:{key}"
        )] for key, item in items.items()
    ])

    await message.answer(
        f"""🛒 <b>Магазин</b>

💰 Деньги: {money(p['money'])}

Выбери товар:
""",
        reply_markup=keyboard
    )


@dp.callback_query(F.data.startswith("shop:"))
async def shop_cb(call: CallbackQuery):
    uid = call.from_user.id
    p = load(uid)
    if not p:
        await call.answer("❌ Сначала создай карьеру!", show_alert=True)
        return

    item_key = call.data.split(":")[1]
    items = {
        "boots": {"name": "👟 Профессиональные бутсы", "cost": 50000, "stat": "+2 к скорости"},
        "equipment": {"name": "🎽 Профессиональная экипировка", "cost": 30000, "stat": "+1 к физике"},
        "fitness": {"name": "💪 Тренажёрный зал", "cost": 10000, "stat": "+10 к форме"},
    }

    item = items[item_key]

    if p["money"] < item["cost"]:
        await call.answer(f"❌ Нужно {money(item['cost'])}", show_alert=True)
        return

    p["money"] -= item["cost"]

    if item_key == "boots":
        p["boots"] = "Профессиональные"
        p["pace"] = min(99, p["pace"] + 2)
    elif item_key == "equipment":
        p["equipment"] = "Профессиональная"
        p["physical"] = min(99, p["physical"] + 1)
    elif item_key == "fitness":
        p["fitness"] = min(100, p["fitness"] + 10)

    save(uid, p)

    await call.message.edit_text(
        f"""✅ <b>Покупка совершена!</b>

{item['name']}
💰 Осталось: {money(p['money'])}
{item['stat']}
"""
    )


@dp.message(Command("stats"))
async def stats(message: Message):
    p = load(message.from_user.id)
    if not p:
        await message.answer("❌ Сначала создай карьеру.")
        return

    await message.answer(
        f"""📊 <b>Статистика {p['name']}</b>

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
"""
    )


@dp.message(Command("trophies"))
async def trophies(message: Message):
    p = load(message.from_user.id)
    if not p:
        await message.answer("❌ Сначала создай карьеру.")
        return

    trophies_list = "\n".join(p.get("trophies", [])) if p.get("trophies") else "Пока нет трофеев 🏆"

    await message.answer(
        f"""🏆 <b>Трофеи</b>

{trophies_list}
"""
    )


@dp.message(Command("table"))
async def table(message: Message):
    p = load(message.from_user.id)
    if not p:
        await message.answer("❌ Сначала создай карьеру.")
        return

    all_clubs = get_all_clubs()
    clubs = [c[0] for c in all_clubs]

    if p["club"] in clubs:
        clubs.remove(p["club"])
    random.shuffle(clubs)
    table_list = [p["club"]] + clubs[:9]
    random.shuffle(table_list)

    lines = ["🏆 <b>Таблица лиги</b>\n"]
    medals = {0: "🥇", 1: "🥈", 2: "🥉"}

    # Создаём нормальные очки (не рандомные)
    points = []
    for i, club in enumerate(table_list):
        if club == p["club"]:
            pts = p.get("league_points", 0)
        else:
            pts = random.randint(30, 85)
        points.append(pts)

    sorted_table = sorted(zip(table_list, points), key=lambda x: x[1], reverse=True)

    for i, (club, pts) in enumerate(sorted_table):
        medal = medals.get(i, f"{i+1}.")
        mark = " ← ты" if club == p["club"] else ""
        lines.append(f"{medal} {club} — {pts} очков{mark}")

    await message.answer("\n".join(lines))


@dp.message(Command("ucl"))
async def ucl(message: Message):
    p = load(message.from_user.id)
    if not p:
        await message.answer("❌ Сначала создай карьеру.")
        return

    clubs = get_all_clubs()[:8]
    random.shuffle(clubs)

    lines = ["⭐ <b>Лига чемпионов</b>\n\n" + "🏆 <b>Плей-офф</b>\n"]

    for i in range(0, len(clubs), 2):
        if i + 1 < len(clubs):
            lines.append(f"⚔️ {clubs[i][0]} vs {clubs[i+1][0]}")

    await message.answer("\n".join(lines))


@dp.message(Command("contract"))
async def contract(message: Message):
    p = load(message.from_user.id)
    if not p:
        await message.answer("❌ Сначала создай карьеру.")
        return

    await message.answer(
        f"""📄 <b>Контракт</b>

🏟 Клуб: {p['club']}
💰 Зарплата: {money(p['salary'])}/нед
📈 Стоимость: {money(p['market_value'])}
💵 Денег: {money(p['money'])}
🧑‍💼 Агент: {p.get('agent', 'Нет')}
"""
    )


@dp.message(Command("news"))
async def news(message: Message):
    p = load(message.from_user.id)
    if not p:
        await message.answer("❌ Сначала создай карьеру.")
        return

    news_list = [
        f"📰 {p['name']} оформил дубль в последнем матче!",
        f"📰 {p['club']} рассчитывает на {p['name']} в новом сезоне.",
        f"📰 Болельщики признали {p['name']} лучшим игроком недели.",
        f"📰 Стоимость {p['name']} продолжает расти.",
        f"📰 {p['name']} дал интервью после матча.",
    ]

    await message.answer(random.choice(news_list))


@dp.message(Command("history"))
async def history_cmd(message: Message):
    history = load_history(message.from_user.id)
    if not history:
        await message.answer("📭 У тебя пока нет завершённых карьер.")
        return

    text = "📜 <b>Твои предыдущие карьеры:</b>\n\n"
    for i, career in enumerate(history[-5:], 1):
        text += f"""{i}. 👤 {career['name']}
   ⭐ Рейтинг: {career['rating']}
   ⚽ Голов: {career['goals']}
   🎯 Ассистов: {career['assists']}
   🏆 Трофеев: {len(career['trophies'])}
   🎂 Возраст: {career['age']}
   📅 Сезонов: {career['season']}
\n"""

    await message.answer(text)


@dp.message(F.text.startswith("/"))
async def unknown(message: Message):
    await message.answer("❌ Неизвестная команда. Напиши /help")


# ── HEALTH CHECK ДЛЯ CRON-JOB ─────────────────────────────────────────────

async def health_check(request):
    return web.Response(text="OK", status=200)

async def start_web():
    app = web.Application()
    app.router.add_get('/', health_check)
    app.router.add_get('/ping', health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    print("🌐 Web-сервер запущен на порту 8080")


# ── ЗАПУСК ─────────────────────────────────────────────────────────────────

async def main():
    print("🚀 Бот запущен!")
    asyncio.create_task(start_web())
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
