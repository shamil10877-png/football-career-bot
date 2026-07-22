```python
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

OWNER_ID = 123456789
CHANNEL_URL = "https://t.me/+MHTPcaFy2j5lOWMy"

REFERRAL_BONUS = 25000
REFERRED_BONUS = 50000

ACHIEVEMENTS = {
    "first_goal": {"name": "🥇 Первый гол", "reward": 5000},
    "hat_trick": {"name": "🎯 Хет-трик", "reward": 20000},
    "100_matches": {"name": "🏃 100 матчей", "reward": 50000},
    "rating_80": {"name": "⭐ Рейтинг 80", "reward": 30000},
    "rating_90": {"name": "🌟 Рейтинг 90", "reward": 100000},
    "millionaire": {"name": "💰 Миллионер", "reward": 100000},
    "champion": {"name": "🏆 Чемпион лиги", "reward": 150000},
    "ucl_winner": {"name": "⭐ Победитель ЛЧ", "reward": 200000},
    "golden_boot": {"name": "👟 Золотая бутса", "reward": 50000},
    "ballon_dor": {"name": "🏅 Золотой мяч", "reward": 100000},
}

RANKS = {
    0: {"name": "🟢 Новичок", "min_rating": 0, "min_trophies": 0, "bonus": 0},
    1: {"name": "🔵 Профессионал", "min_rating": 70, "min_trophies": 2, "bonus": 5},
    2: {"name": "🟣 Звезда", "min_rating": 80, "min_trophies": 5, "bonus": 10},
    3: {"name": "🟠 Легенда", "min_rating": 88, "min_trophies": 10, "bonus": 20},
    4: {"name": "🔴 GOAT", "min_rating": 95, "min_trophies": 15, "bonus": 30},
}

LEAGUES = {
    "АПЛ": ["Манчестер Сити", "Ливерпуль", "Челси", "Арсенал", "Тоттенхэм", "Манчестер Юнайтед", "Ньюкасл", "Астон Вилла", "Брайтон", "Вулверхэмптон"],
    "Ла Лига": ["Реал Мадрид", "Барселона", "Атлетико", "Севилья", "Вильярреал", "Реал Сосьедад", "Бетис", "Атлетик", "Валенсия", "Осасуна"],
    "Бундеслига": ["Бавария", "Боруссия Дортмунд", "Лейпциг", "Байер", "Фрайбург", "Айнтрахт", "Вольфсбург", "Менхенгладбах", "Штутгарт", "Хоффенхайм"],
    "Серия А": ["Ювентус", "Милан", "Интер", "Рома", "Наполи", "Лацио", "Аталанта", "Фиорентина", "Торино", "Болонья"],
    "Лига 1": ["ПСЖ", "Марсель", "Монако", "Лион", "Лилль", "Ренн", "Ницца", "Страсбург", "Ланс", "Нант"],
}

UCL_CLUBS = ["Реал Мадрид", "Барселона", "Манчестер Сити", "Бавария", "ПСЖ", "Ливерпуль", "Ювентус", "Атлетико"]

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

def get_all_players():
    players = []
    for file in os.listdir(SAVE_DIR):
        if file.endswith(".json"):
            with open(os.path.join(SAVE_DIR, file), "r", encoding="utf-8") as f:
                data = json.load(f)
            if data.get("created"):
                players.append(data)
    return players

def get_rank(rating, trophies):
    for i in range(len(RANKS)-1, -1, -1):
        if rating >= RANKS[i]["min_rating"] and trophies >= RANKS[i]["min_trophies"]:
            return RANKS[i]
    return RANKS[0]

def get_league_for_club(club):
    for league, clubs in LEAGUES.items():
        if club in clubs:
            return league
    return "АПЛ"

def get_clubs_by_rating(rating):
    if rating >= 85:
        return [("Реал Мадрид", 300000), ("Барселона", 280000), ("Манчестер Сити", 290000), ("Бавария", 270000)]
    elif rating >= 75:
        return [("Челси", 180000), ("Ювентус", 170000), ("Атлетико", 160000), ("Арсенал", 150000)]
    elif rating >= 65:
        return [("Вест Хэм", 100000), ("Валенсия", 90000), ("Лацио", 85000), ("Лилль", 80000)]
    else:
        return [("Кристал Пэлас", 40000), ("Хоффенхайм", 35000), ("Болонья", 30000), ("Ренн", 25000)]

def new_player(name, referrer=None):
    league = random.choice(list(LEAGUES.keys()))
    club = random.choice(LEAGUES[league])
    now = datetime.now()
    return {
        "created": True, "name": name, "club": club, "league": league,
        "rating": 60, "potential": 90, "age": 16, "season": 1, "week": 1,
        "matches": 0, "goals": 0, "assists": 0, "mvps": 0,
        "salary": 0, "money": 50000 + (REFERRED_BONUS if referrer else 0),
        "market_value": 500000,
        "fitness": 100, "morale": 100,
        "pace": 60, "shooting": 60, "passing": 60, "dribbling": 60, "defending": 35, "physical": 55,
        "followers": 100, "popularity": 1,
        "ucl": 0, "league_titles": 0, "worldcup": 0, "ballon": 0, "golden_boot": 0,
        "agent": "Нет", "boots": "Обычные", "equipment": "Стандартная",
        "trophies": [], "club_history": [],
        "retired": False, "injured": False, "injury_days": 0,
        "sponsors": [], "reputation": 50,
        "house": "Нет", "houses": [], "rental_income": 0,
        "car": "Нет", "cars": [],
        "business": False, "business_type": "Нет", "business_income": 0,
        "wife": None, "children": 0, "relationship_days": 0,
        "last_daily": now.isoformat(),
        "goals_career": 0, "assists_career": 0, "matches_career": 0, "mvps_career": 0,
        "ucl_career": 0, "league_titles_career": 0, "worldcup_career": 0, "ballon_career": 0, "golden_boot_career": 0,
        "league_points": 0, "ucl_points": 0, "league_matches": 0, "ucl_matches": 0,
        "last_ucl_week": 0, "worldcup_year": 0, "euro_year": 0,
        "winter_transfer": False,
        "season_goals": 0, "season_assists": 0, "season_matches": 0,
        "best_rating": 60,
        "bonus_received": False,
        "referrer": referrer, "referrals": [],
        "achievements": [],
        "last_reminder": now.isoformat(),
        "daily_tasks": {"goals": 0, "matches": 0, "points": 0, "completed": False},
        "casino_total": 0,
        "is_coach": False,
        "coach_team": None,
        "coach_rating": 50,
        "coach_trophies": [],
        "coach_matches": 0,
        "coach_wins": 0,
        "coach_draws": 0,
        "coach_losses": 0,
        "coach_tactics": "Сбалансированная",
        "coach_players": [],
        "coach_staff": 0,
        "coach_money": 0,
        "coach_history": [],
        "emoji": "⚽",
        "season_stats": [],
        "stadium_level": 0,
        "merch_items": [],
        "friends": [],
        "cases_opened": 0,
        "stocks": [],
    }

def check_achievements(p, user_id):
    unlocked = []
    achievements = p.get("achievements", [])
    if p["goals_career"] >= 1 and "first_goal" not in achievements:
        achievements.append("first_goal"); p["money"] += ACHIEVEMENTS["first_goal"]["reward"]; unlocked.append("🥇 Первый гол")
    if p.get("season_goals", 0) >= 3 and "hat_trick" not in achievements:
        achievements.append("hat_trick"); p["money"] += ACHIEVEMENTS["hat_trick"]["reward"]; unlocked.append("🎯 Хет-трик")
    if p["matches_career"] >= 100 and "100_matches" not in achievements:
        achievements.append("100_matches"); p["money"] += ACHIEVEMENTS["100_matches"]["reward"]; unlocked.append("🏃 100 матчей")
    if p["rating"] >= 80 and "rating_80" not in achievements:
        achievements.append("rating_80"); p["money"] += ACHIEVEMENTS["rating_80"]["reward"]; unlocked.append("⭐ Рейтинг 80")
    if p["rating"] >= 90 and "rating_90" not in achievements:
        achievements.append("rating_90"); p["money"] += ACHIEVEMENTS["rating_90"]["reward"]; unlocked.append("🌟 Рейтинг 90")
    if p["money"] >= 1000000 and "millionaire" not in achievements:
        achievements.append("millionaire"); p["money"] += ACHIEVEMENTS["millionaire"]["reward"]; unlocked.append("💰 Миллионер")
    if p["league_titles_career"] >= 1 and "champion" not in achievements:
        achievements.append("champion"); p["money"] += ACHIEVEMENTS["champion"]["reward"]; unlocked.append("🏆 Чемпион лиги")
    if p["ucl_career"] >= 1 and "ucl_winner" not in achievements:
        achievements.append("ucl_winner"); p["money"] += ACHIEVEMENTS["ucl_winner"]["reward"]; unlocked.append("⭐ Победитель ЛЧ")
    if p["golden_boot_career"] >= 1 and "golden_boot" not in achievements:
        achievements.append("golden_boot"); p["money"] += ACHIEVEMENTS["golden_boot"]["reward"]; unlocked.append("👟 Золотая бутса")
    if p["ballon_career"] >= 1 and "ballon_dor" not in achievements:
        achievements.append("ballon_dor"); p["money"] += ACHIEVEMENTS["ballon_dor"]["reward"]; unlocked.append("🏅 Золотой мяч")
    p["achievements"] = achievements
    save(user_id, p)
    return unlocked

def check_daily_tasks(p, user_id):
    tasks = p.get("daily_tasks", {})
    if tasks.get("completed", False):
        return None
    required = tasks.get("required", {"goals": random.randint(2,5), "matches": random.randint(3,7), "points": random.randint(10,20)})
    current = tasks.get("current", {"goals": 0, "matches": 0, "points": 0})
    if current.get("goals", 0) >= required.get("goals", 0) and current.get("matches", 0) >= required.get("matches", 0) and current.get("points", 0) >= required.get("points", 0):
        tasks["completed"] = True
        p["daily_tasks"] = tasks
        p["money"] += 50000
        save(user_id, p)
        return required
    return None

def main_menu_keyboard(is_coach=False):
    keyboard = [
        [InlineKeyboardButton(text="⚽ Профиль", callback_data="menu:profile"), InlineKeyboardButton(text="🏆 Игровой процесс", callback_data="menu:game")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="menu:stats"), InlineKeyboardButton(text="🔄 Карьера", callback_data="menu:career")],
        [InlineKeyboardButton(text="🛒 Магазин", callback_data="menu:shop"), InlineKeyboardButton(text="👤 Социальное", callback_data="menu:social")],
        [InlineKeyboardButton(text="⭐ Бонусы", callback_data="menu:bonus"), InlineKeyboardButton(text="🎰 Казино", callback_data="menu:casino")],
        [InlineKeyboardButton(text="🏅 Достижения", callback_data="menu:achievements")],
    ]
    if is_coach:
        keyboard.insert(2, [InlineKeyboardButton(text="🧑‍🏫 Тренерские", callback_data="menu:coach")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

@dp.message(Command("start"))
async def start(message: Message):
    p = load(message.from_user.id)
    if p:
        await message.answer(
            f"👋 С возвращением, <b>{p['name']}</b> {p.get('emoji', '⚽')}!\n"
            f"🏆 Лига: {p.get('league', 'АПЛ')}\n"
            f"📅 Неделя: {p.get('week', 1)}\n"
            f"🏆 Сезон: {p.get('season', 1)}",
            reply_markup=main_menu_keyboard(p.get("is_coach", False))
        )
    else:
        await message.answer("⚽ <b>Football Career</b>\n\nСоздай карьеру:\n<code>/create Имя</code>")

@dp.message(Command("help"))
async def help_cmd(message: Message):
    p = load(message.from_user.id)
    is_coach = p.get("is_coach", False) if p else False
    text = "📖 <b>Команды</b>\n\n⚽ ОСНОВНЫЕ:\n/profile, /train, /match, /rest, /season, /calendar, /transfers, /agent, /shop, /stats, /trophies, /news, /table, /ucl, /contract, /sponsor, /daily, /national, /cars, /house, /family, /business, /history, /donate, /bonus, /achievements, /leaderboard, /penalty, /casino, /tasks, /referral, /reminder, /ping, /myid, /give\n"
    text += "\n🆕 НОВЫЕ:\n/rename, /setemoji, /seasons, /cup, /stadium, /merch, /cases, /friends, /club_world_cup, /predict, /stocks"
    if is_coach:
        text += "\n\n🧑‍🏫 ТРЕНЕРСКИЕ:\n/coach_profile, /team, /train_team, /match_team, /tactics, /transfer_players, /squad, /coach_trophies, /coach_history, /staff, /coach_leaderboard"
    await message.answer(text)

@dp.message(Command("ping"))
async def ping(message: Message):
    await message.answer("🏓 Pong! Бот работает!")

@dp.message(Command("myid"))
async def my_id(message: Message):
    await message.answer(f"🆔 Твой ID: <code>{message.from_user.id}</code>")

@dp.message(Command("create"))
async def create(message: Message):
    args = message.text.split()
    if len(args) < 2:
        await message.answer("❌ Используй: /create Имя")
        return
    name = args[1]
    player = new_player(name)
    save(message.from_user.id, player)
    await message.answer(f"✅ Карьера создана!\n👤 Игрок: <b>{name}</b>\n⭐ Рейтинг: 60\n🏟 Клуб: {player['club']}")

@dp.message(Command("profile"))
async def profile(message: Message):
    p = load(message.from_user.id)
    if not p:
        await message.answer("❌ Сначала создай карьеру: /create")
        return
    rank = get_rank(p["rating"], len(p.get("trophies", [])))
    text = f"👤 <b>{p['name']}</b> {p.get('emoji', '⚽')}\n⭐ Рейтинг: {p['rating']}\n🏅 Звание: {rank['name']}\n🏟 Клуб: {p['club']}\n🏆 Лига: {p.get('league', 'АПЛ')}\n🎂 Возраст: {p['age']}\n💰 Деньги: {money(p['money'])}\n💵 Зарплата: {money(p['salary'])}/нед\n📈 Стоимость: {money(p['market_value'])}\n⚽ Матчи: {p['matches']}\n🥅 Голы: {p['goals']}\n🎯 Ассисты: {p['assists']}\n🏅 MVP: {p['mvps']}\n👥 Подписчики: {p['followers']}"
    await message.answer(text)

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
    stat_names = {"pace": "Скорость", "shooting": "Удар", "passing": "Пас", "dribbling": "Дриблинг", "defending": "Защита", "physical": "Физика"}
    plus = random.randint(1, 3)
    p[stat] = min(99, p[stat] + plus)
    p["fitness"] -= random.randint(10, 20)
    p["rating"] = int((p["pace"] + p["shooting"] + p["passing"] + p["dribbling"] + p["defending"] + p["physical"]) / 6)
    save(message.from_user.id, p)
    await message.answer(f"🏋️ Тренировка!\n⬆️ +{plus} к {stat_names[stat]}\n⭐ Рейтинг: {p['rating']}")

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
        await message.answer("😴 Ты устал. Используй /rest")
        return
    goals = random.randint(0, 2)
    assists = random.randint(0, 1)
    mvp = random.randint(1, 100) <= p["rating"] - 40
    result_num = random.randint(1, 100)
    if result_num <= 40 + (p["rating"] - 60) // 2:
        result, points = "win", 3
    elif result_num <= 60 + (p["rating"] - 60) // 2:
        result, points = "draw", 1
    else:
        result, points = "lose", 0
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
    gain = goals * 0.35 + assists * 0.20 + (0.50 if mvp else 0)
    if result == "win":
        gain += 0.30
    elif result == "draw":
        gain += 0.10
    p["rating"] = round(min(99, p["rating"] + gain), 1)
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
    unlocked = check_achievements(p, message.from_user.id)
    if p["week"] >= 38:
        p["season"] += 1
        p["age"] += 1
        p["week"] = 1
        p["goals"] = 0
        p["assists"] = 0
        p["matches"] = 0
        p["league_matches"] = 0
        p["league_points"] = 0
        if p["age"] >= 41:
            p["retired"] = True
            save(message.from_user.id, p)
            await message.answer("🔚 <b>Ты завершил карьеру!</b>")
            return
    save(message.from_user.id, p)
    result_text = "🏆 Победа!" if result == "win" else "🤝 Ничья" if result == "draw" else "❌ Поражение"
    await message.answer(f"🏟 Матч!\n📊 {result_text} (+{points})\n⚽ Голы: {goals}\n🎯 Ассисты: {assists}\n⭐ {'MVP!' if mvp else ''}\n💰 +{money(reward)}\n📈 Рейтинг: {p['rating']}")

@dp.message(Command("rest"))
async def rest_cmd(message: Message):
    p = load(message.from_user.id)
    if not p:
        await message.answer("❌ Сначала создай карьеру.")
        return
    p["fitness"] = min(100, p["fitness"] + 30)
    save(message.from_user.id, p)
    await message.answer(f"😴 Отдых!\n⚡ Форма: {p['fitness']}%")

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
    await message.answer(f"🎁 Ежедневный бонус!\n💰 +{money(reward)}")

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
        await message.answer("❌ Нужен агент. Найми через /agent")
        return
    clubs = get_clubs_by_rating(p["rating"])
    offers = random.sample(clubs, min(3, len(clubs)))
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"🏟 {club} — {money(sal)}/нед", callback_data=f"transfer:{club}:{sal}")] for club, sal in offers
    ])
    await message.answer(f"✈️ Трансферы\nТекущий клуб: {p['club']}", reply_markup=keyboard)

@dp.callback_query(F.data.startswith("transfer:"))
async def transfer_cb(call: CallbackQuery):
    uid = call.from_user.id
    p = load(uid)
    if not p:
        await call.answer("❌ Ошибка!", show_alert=True)
        return
    parts = call.data.split(":")
    club = parts[1]
    salary = int(parts[2])
    old_club = p["club"]
    p["club"] = club
    p["league"] = get_league_for_club(club)
    p["salary"] = salary
    p["club_history"].append(old_club)
    save(uid, p)
    await call.message.edit_text(f"✅ Трансфер!\nТы перешёл в {club}!\n💵 Зарплата: {money(salary)}/нед")

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
    if p.get("agent") != "Нет":
        await message.answer(f"🧑‍💼 Агент: {p['agent']}\n💰 Деньги: {money(p['money'])}", reply_markup=keyboard)
        return
    await message.answer(f"🧑‍💼 Выбери агента\n💰 Деньги: {money(p['money'])}", reply_markup=keyboard)

@dp.callback_query(F.data.startswith("agent:"))
async def agent_cb(call: CallbackQuery):
    uid = call.from_user.id
    p = load(uid)
    if not p:
        await call.answer("❌ Ошибка!", show_alert=True)
        return
    parts = call.data.split(":")
    agent_type = parts[1]
    cost = int(parts[2])
    agent_names = {"bad": "😐 Плохой агент", "medium": "🙂 Средний агент", "good": "😎 Хороший агент", "top": "🌟 Топ-агент"}
    name = agent_names[agent_type]
    if p["money"] < cost:
        await call.answer(f"❌ Нужно {money(cost)}", show_alert=True)
        return
    p["money"] -= cost
    p["agent"] = name
    save(uid, p)
    await call.message.edit_text(f"✅ Ты нанял <b>{name}</b>!\n💰 Осталось: {money(p['money'])}")

@dp.message(Command("shop"))
async def shop(message: Message):
    p = load(message.from_user.id)
    if not p:
        await message.answer("❌ Сначала создай карьеру.")
        return
    items = {
        "boots": {"name": "👟 Бутсы", "cost": 50000, "stat": "+2 скорость"},
        "equipment": {"name": "🎽 Экипировка", "cost": 30000, "stat": "+1 физика"},
        "fitness": {"name": "💪 Тренажёрка", "cost": 10000, "stat": "+10 форма"},
    }
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{item['name']} — {money(item['cost'])}", callback_data=f"shop:{key}")] for key, item in items.items()
    ])
    await message.answer(f"🛒 Магазин\n💰 Деньги: {money(p['money'])}", reply_markup=keyboard)

@dp.callback_query(F.data.startswith("shop:"))
async def shop_cb(call: CallbackQuery):
    uid = call.from_user.id
    p = load(uid)
    if not p:
        await call.answer("❌ Ошибка!", show_alert=True)
        return
    item_key = call.data.split(":")[1]
    items = {
        "boots": {"name": "👟 Бутсы", "cost": 50000, "stat": "+2 скорость"},
        "equipment": {"name": "🎽 Экипировка", "cost": 30000, "stat": "+1 физика"},
        "fitness": {"name": "💪 Тренажёрка", "cost": 10000, "stat": "+10 форма"},
    }
    item = items[item_key]
    if p["money"] < item["cost"]:
        await call.answer(f"❌ Нужно {money(item['cost'])}", show_alert=True)
        return
    p["money"] -= item["cost"]
    if item_key == "boots":
        p["boots"] = "Профессиональные"; p["pace"] = min(99, p["pace"] + 2)
    elif item_key == "equipment":
        p["equipment"] = "Профессиональная"; p["physical"] = min(99, p["physical"] + 1)
    elif item_key == "fitness":
        p["fitness"] = min(100, p["fitness"] + 10)
    save(uid, p)
    await call.message.edit_text(f"✅ Куплено: {item['name']}\n💰 Осталось: {money(p['money'])}")

@dp.message(Command("stats"))
async def stats(message: Message):
    p = load(message.from_user.id)
    if not p:
        await message.answer("❌ Сначала создай карьеру.")
        return
    await message.answer(
        f"📊 Статистика {p['name']}\n⚽ Голы: {p['goals']}\n🎯 Ассисты: {p['assists']}\n🎮 Матчей: {p['matches']}\n⭐ MVP: {p['mvps']}\n🏃 Скорость: {p['pace']}\n🎯 Удар: {p['shooting']}\n🔄 Пас: {p['passing']}\n🌀 Дриблинг: {p['dribbling']}\n🛡 Защита: {p['defending']}\n💪 Физика: {p['physical']}\n⚡ Форма: {p['fitness']}%"
    )

@dp.message(Command("table"))
async def table(message: Message):
    p = load(message.from_user.id)
    if not p:
        await message.answer("❌ Сначала создай карьеру.")
        return
    league = p.get("league", "АПЛ")
    clubs = LEAGUES.get(league, LEAGUES["АПЛ"])
    table_data = []
    for club in clubs:
        if club == p["club"]:
            pts = p.get("league_points", 0)
        else:
            pts = random.randint(20, 85)
        table_data.append((club, pts))
    sorted_table = sorted(table_data, key=lambda x: x[1], reverse=True)
    lines = [f"🏆 <b>{league}</b>\n"]
    medals = {0: "🥇", 1: "🥈", 2: "🥉"}
    for i, (club, pts) in enumerate(sorted_table[:10]):
        medal = medals.get(i, f"{i+1}.")
        mark = " ← ты" if club == p["club"] else ""
        lines.append(f"{medal} {club} — {pts} очков{mark}")
    await message.answer("\n".join(lines))

@dp.message(Command("trophies"))
async def trophies(message: Message):
    p = load(message.from_user.id)
    if not p:
        await message.answer("❌ Сначала создай карьеру.")
        return
    trophies_list = "\n".join(p.get("trophies", [])) if p.get("trophies") else "Пока нет трофеев 🏆"
    await message.answer(f"🏆 Трофеи\n{trophies_list}")

@dp.message(Command("contract"))
async def contract(message: Message):
    p = load(message.from_user.id)
    if not p:
        await message.answer("❌ Сначала создай карьеру.")
        return
    await message.answer(
        f"📄 Контракт\n🏟 Клуб: {p['club']}\n🏆 Лига: {p.get('league', 'АПЛ')}\n💰 Зарплата: {money(p['salary'])}/нед\n📈 Стоимость: {money(p['market_value'])}\n💵 Денег: {money(p['money'])}"
    )

@dp.message(Command("cars"))
async def cars(message: Message):
    p = load(message.from_user.id)
    if not p:
        await message.answer("❌ Сначала создай карьеру.")
        return
    cars_list = [("Lada Granta", 2000), ("Kia Rio", 8000), ("Toyota Camry", 25000), ("BMW X5", 60000), ("Porsche 911", 250000), ("Lamborghini", 500000)]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{car} — {money(price)}", callback_data=f"car:{car}:{price}")] for car, price in cars_list
    ])
    await message.answer(f"🚗 Автосалон\n💰 Деньги: {money(p['money'])}", reply_markup=keyboard)

@dp.callback_query(F.data.startswith("car:"))
async def car_cb(call: CallbackQuery):
    uid = call.from_user.id
    p = load(uid)
    if not p:
        await call.answer("❌ Ошибка!", show_alert=True)
        return
    parts = call.data.split(":")
    car = parts[1]
    price = int(parts[2])
    if p["money"] < price:
        await call.answer(f"❌ Нужно {money(price)}", show_alert=True)
        return
    p["money"] -= price
    p["car"] = car
    save(uid, p)
    await call.message.edit_text(f"🚗 Куплена {car}!\n💰 Осталось: {money(p['money'])}")

@dp.message(Command("house"))
async def house(message: Message):
    p = load(message.from_user.id)
    if not p:
        await message.answer("❌ Сначала создай карьеру.")
        return
    houses_list = [("Квартира", 150000), ("Дом", 500000), ("Вилла", 1500000)]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{home} — {money(price)}", callback_data=f"house:{home}:{price}")] for home, price in houses_list
    ])
    await message.answer(f"🏠 Недвижимость\n💰 Деньги: {money(p['money'])}", reply_markup=keyboard)

@dp.callback_query(F.data.startswith("house:"))
async def house_cb(call: CallbackQuery):
    uid = call.from_user.id
    p = load(uid)
    if not p:
        await call.answer("❌ Ошибка!", show_alert=True)
        return
    parts = call.data.split(":")
    home = parts[1]
    price = int(parts[2])
    if p["money"] < price:
        await call.answer(f"❌ Нужно {money(price)}", show_alert=True)
        return
    p["money"] -= price
    p["house"] = home
    save(uid, p)
    await call.message.edit_text(f"🏠 Куплен {home}!\n💰 Осталось: {money(p['money'])}")

@dp.message(Command("business"))
async def business(message: Message):
    p = load(message.from_user.id)
    if not p:
        await message.answer("❌ Сначала создай карьеру.")
        return
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏪 Магазин — 30,000", callback_data="business:small")],
        [InlineKeyboardButton(text="🛍️ ТЦ — 200,000", callback_data="business:medium")],
    ])
    await message.answer(f"🏢 Бизнес\n💰 Деньги: {money(p['money'])}", reply_markup=keyboard)

@dp.callback_query(F.data.startswith("business:"))
async def business_cb(call: CallbackQuery):
    uid = call.from_user.id
    p = load(uid)
    if not p:
        await call.answer("❌ Ошибка!", show_alert=True)
        return
    types = {"small": ("🏪 Магазин", 30000, 5000), "medium": ("🛍️ ТЦ", 200000, 25000)}
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
    await call.message.edit_text(f"✅ Бизнес открыт!\n🏢 {name}\n💰 Доход: {money(income)}/нед")

@dp.message(Command("news"))
async def news(message: Message):
    p = load(message.from_user.id)
    if not p:
        await message.answer("❌ Сначала создай карьеру.")
        return
    news_list = [
        f"📰 {p['name']} оформил дубль!",
        f"📰 {p['club']} рассчитывает на {p['name']}",
        f"📰 Стоимость {p['name']} растёт",
    ]
    await message.answer(random.choice(news_list))

@dp.message(Command("history"))
async def history_cmd(message: Message):
    history = load_history(message.from_user.id)
    if not history:
        await message.answer("📭 Нет завершённых карьер.")
        return
    text = "📜 Твои предыдущие карьеры:\n"
    for i, career in enumerate(history[-5:], 1):
        text += f"{i}. {career['name']} — ⭐{career['rating']}\n"
    await message.answer(text)

@dp.message(Command("give"))
async def give_money(message: Message):
    p = load(message.from_user.id)
    if not p:
        await message.answer("❌ Сначала создай карьеру!")
        return
    args = message.text.split()
    if len(args) < 3:
        await message.answer("❌ Используй: /give @username сумма")
        return
    username = args[1].replace("@", "")
    amount = int(args[2])
    if p["money"] < amount:
        await message.answer(f"❌ У тебя только {money(p['money'])}")
        return
    found = False
    for file in os.listdir(SAVE_DIR):
        if file.endswith(".json"):
            with open(os.path.join(SAVE_DIR, file), "r", encoding="utf-8") as f:
                data = json.load(f)
            if data.get("name", "").lower() == username.lower():
                data["money"] += amount
                with open(os.path.join(SAVE_DIR, file), "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                found = True
                break
    if not found:
        await message.answer(f"❌ Игрок {username} не найден")
        return
    p["money"] -= amount
    save(message.from_user.id, p)
    await message.answer(f"✅ Переведено {money(amount)} игроку <b>{username}</b>")

@dp.message(Command("bonus"))
async def bonus_cmd(message: Message):
    p = load(message.from_user.id)
    if not p:
        await message.answer("❌ Сначала создай карьеру!")
        return
    if p.get("bonus_received", False):
        await message.answer("❌ Бонус уже получен!")
        return
    p["money"] += 50000
    p["bonus_received"] = True
    save(message.from_user.id, p)
    await message.answer(f"✅ Бонус получен!\n💰 +50,000 €")

@dp.message(Command("achievements"))
async def achievements_cmd(message: Message):
    p = load(message.from_user.id)
    if not p:
        await message.answer("❌ Сначала создай карьеру!")
        return
    unlocked = p.get("achievements", [])
    if not unlocked:
        await message.answer("🏆 Нет достижений.")
        return
    text = "🏆 Твои достижения:\n"
    for ach in unlocked:
        if ach in ACHIEVEMENTS:
            text += f"✅ {ACHIEVEMENTS[ach]['name']}\n"
    await message.answer(text)

@dp.message(Command("leaderboard"))
async def leaderboard(message: Message):
    players = get_all_players()
    if not players:
        await message.answer("📭 Нет игроков")
        return
    sorted_players = sorted(players, key=lambda x: x.get("rating", 0), reverse=True)[:10]
    text = "🏆 Топ-10 игроков\n"
    for i, p in enumerate(sorted_players):
        text += f"{i+1}. {p['name']} — ⭐{p['rating']}\n"
    await message.answer(text)

@dp.message(Command("penalty"))
async def penalty(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Влево", callback_data="penalty:left"), InlineKeyboardButton(text="➡️ Вправо", callback_data="penalty:right")],
        [InlineKeyboardButton(text="⬆️ Вверх", callback_data="penalty:up"), InlineKeyboardButton(text="⬇️ Вниз", callback_data="penalty:down")]
    ])
    await message.answer("⚽ Пенальти!\nВыбери направление:", reply_markup=keyboard)

@dp.callback_query(F.data.startswith("penalty:"))
async def penalty_cb(call: CallbackQuery):
    uid = call.from_user.id
    p = load(uid)
    if not p:
        await call.answer("❌ Ошибка!", show_alert=True)
        return
    user_choice = call.data.split(":")[1]
    bot_choice = random.choice(["left", "right", "up", "down"])
    if user_choice == bot_choice:
        reward = 10000
        p["money"] += reward
        save(uid, p)
        await call.message.edit_text(f"⚽ ГОЛ! 🎉\n💰 +{money(reward)}")
    else:
        await call.message.edit_text("⚽ МИМО! ❌")

@dp.message(Command("casino"))
async def casino(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎰 Слоты", callback_data="casino:slots")],
        [InlineKeyboardButton(text="🪙 Орёл/Решка", callback_data="casino:coin")],
    ])
    await message.answer(f"🎰 Казино\n💰 Баланс: {money(p.get('money', 0))}", reply_markup=keyboard)

@dp.callback_query(F.data.startswith("casino:slots"))
async def casino_slots(call: CallbackQuery):
    uid = call.from_user.id
    p = load(uid)
    if not p:
        await call.answer("❌ Ошибка!", show_alert=True)
        return
    bet = 5000
    if p["money"] < bet:
        await call.answer("❌ Недостаточно!", show_alert=True)
        return
    symbols = ["🍒", "🍋", "🍊", "🍇", "💎", "7️⃣"]
    result = [random.choice(symbols) for _ in range(3)]
    win = 0
    if result[0] == result[1] == result[2]:
        win = bet * 10
    elif result[0] == result[1] or result[0] == result[2] or result[1] == result[2]:
        win = bet * 2
    p["money"] -= bet
    p["money"] += win
    save(uid, p)
    await call.message.edit_text(f"🎰 Слоты\n{' '.join(result)}\n🏆 Выигрыш: {money(win)}\n💵 Баланс: {money(p['money'])}")

@dp.callback_query(F.data.startswith("casino:coin"))
async def casino_coin(call: CallbackQuery):
    uid = call.from_user.id
    p = load(uid)
    if not p:
        await call.answer("❌ Ошибка!", show_alert=True)
        return
    bet = 10000
    if p["money"] < bet:
        await call.answer("❌ Недостаточно!", show_alert=True)
        return
    user_choice = random.choice(["Орёл", "Решка"])
    bot_choice = random.choice(["Орёл", "Решка"])
    win = bet if user_choice == bot_choice else 0
    p["money"] -= bet
    p["money"] += win
    save(uid, p)
    await call.message.edit_text(f"🪙 Орёл/Решка\nВыпало: {bot_choice}\n🏆 Выигрыш: {money(win)}\n💵 Баланс: {money(p['money'])}")

@dp.message(Command("tasks"))
async def tasks(message: Message):
    p = load(message.from_user.id)
    if not p:
        await message.answer("❌ Сначала создай карьеру!")
        return
    tasks = p.get("daily_tasks", {})
    required = tasks.get("required", {"goals": random.randint(2,5), "matches": random.randint(3,7), "points": random.randint(10,20)})
    current = tasks.get("current", {"goals": 0, "matches": 0, "points": 0})
    if tasks.get("completed", False):
        await message.answer("✅ Задания выполнены! +50,000 € получены!")
        return
    await message.answer(
        f"📋 Ежедневные задания\n⚽ Голов: {current.get('goals', 0)}/{required['goals']}\n🎮 Матчей: {current.get('matches', 0)}/{required['matches']}\n📊 Очков: {current.get('points', 0)}/{required['points']}\n🏆 Награда: 50,000 €"
    )

@dp.message(Command("referral"))
async def referral(message: Message):
    p = load(message.from_user.id)
    if not p:
        await message.answer("❌ Сначала создай карьеру!")
        return
    text = f"🔗 Твоя ссылка: <code>https://t.me/GoalTimeNews_bot?start={message.from_user.id}</code>"
    await message.answer(text)

@dp.message(Command("reminder"))
async def reminder(message: Message):
    p = load(message.from_user.id)
    if not p:
        await message.answer("❌ Сначала создай карьеру!")
        return
    now = datetime.now()
    last = datetime.fromisoformat(p.get("last_reminder", now.isoformat()))
    if (now - last).days >= 1:
        p["money"] += 10000
        p["last_reminder"] = now.isoformat()
        save(message.from_user.id, p)
        await message.answer("⏰ +10,000 € за активность!")
    else:
        await message.answer("⏰ Бонус уже получен сегодня.")

# ============ ТРЕНЕРСКИЕ КОМАНДЫ ============

@dp.message(Command("coach_profile"))
async def coach_profile(message: Message):
    p = load(message.from_user.id)
    if not p or not p.get("is_coach"):
        await message.answer("❌ Ты не тренер!")
        return
    await message.answer(
        f"🧑‍🏫 Профиль тренера\n👤 {p['name']}\n⭐ Рейтинг: {p['coach_rating']}\n🏟 Команда: {p.get('coach_team', 'Нет')}\n📊 {p.get('coach_wins', 0)}-{p.get('coach_draws', 0)}-{p.get('coach_losses', 0)}\n🏆 Трофеев: {len(p.get('coach_trophies', []))}\n💰 Денег: {money(p.get('coach_money', 0))}"
    )

@dp.message(Command("team"))
async def team(message: Message):
    p = load(message.from_user.id)
    if not p or not p.get("is_coach"):
        await message.answer("❌ Ты не тренер!")
        return
    await message.answer(f"🏟 Команда: {p.get('coach_team', 'Нет')}\n👥 Игроков: {len(p.get('coach_players', []))}")

@dp.message(Command("train_team"))
async def train_team(message: Message):
    p = load(message.from_user.id)
    if not p or not p.get("is_coach"):
        await message.answer("❌ Ты не тренер!")
        return
    p["coach_rating"] = min(100, p.get("coach_rating", 50) + random.randint(1, 3))
    save(message.from_user.id, p)
    await message.answer(f"🧑‍🏫 Тренировка команды!\n⭐ Рейтинг тренера: {p['coach_rating']}")

@dp.message(Command("match_team"))
async def match_team(message: Message):
    p = load(message.from_user.id)
    if not p or not p.get("is_coach"):
        await message.answer("❌ Ты не тренер!")
        return
    opp = random.choice(["Реал Мадрид", "Барселона", "Бавария"])
    result = random.choice(["win", "draw", "lose"])
    p["coach_matches"] = p.get("coach_matches", 0) + 1
    if result == "win":
        p["coach_wins"] = p.get("coach_wins", 0) + 1
        p["coach_money"] = p.get("coach_money", 0) + 10000
        p["coach_rating"] = min(100, p.get("coach_rating", 50) + 2)
    elif result == "draw":
        p["coach_draws"] = p.get("coach_draws", 0) + 1
        p["coach_money"] = p.get("coach_money", 0) + 3000
        p["coach_rating"] = min(100, p.get("coach_rating", 50) + 1)
    else:
        p["coach_losses"] = p.get("coach_losses", 0) + 1
        p["coach_rating"] = max(0, p.get("coach_rating", 50) - 1)
    save(message.from_user.id, p)
    result_text = "🏆 Победа!" if result == "win" else "🤝 Ничья" if result == "draw" else "❌ Поражение"
    await message.answer(f"🏟 Матч!\n📊 {result_text}\n⚔️ Соперник: {opp}\n⭐ Рейтинг: {p['coach_rating']}")

@dp.message(Command("tactics"))
async def tactics(message: Message):
    p = load(message.from_user.id)
    if not p or not p.get("is_coach"):
        await message.answer("❌ Ты не тренер!")
        return
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚔️ Атакующая", callback_data="tactics:attack")],
        [InlineKeyboardButton(text="🛡️ Защитная", callback_data="tactics:defense")],
        [InlineKeyboardButton(text="⚖️ Сбалансированная", callback_data="tactics:balanced")],
    ])
    await message.answer(f"🧠 Тактика\nТекущая: {p.get('coach_tactics', 'Сбалансированная')}", reply_markup=keyboard)

@dp.callback_query(F.data.startswith("tactics:"))
async def tactics_cb(call: CallbackQuery):
    uid = call.from_user.id
    p = load(uid)
    if not p:
        await call.answer("❌ Ошибка!", show_alert=True)
        return
    names = {"attack": "⚔️ Атакующая", "defense": "🛡️ Защитная", "balanced": "⚖️ Сбалансированная"}
    p["coach_tactics"] = names[call.data.split(":")[1]]
    save(uid, p)
    await call.message.edit_text(f"✅ Тактика изменена!")

@dp.message(Command("coach_trophies"))
async def coach_trophies(message: Message):
    p = load(message.from_user.id)
    if not p or not p.get("is_coach"):
        await message.answer("❌ Ты не тренер!")
        return
    trophies = p.get("coach_trophies", [])
    await message.answer(f"🏆 Трофеи тренера\n{'\n'.join(trophies) if trophies else 'Пока нет'}")

@dp.message(Command("coach_leaderboard"))
async def coach_leaderboard(message: Message):
    players = get_all_players()
    coaches = [p for p in players if p.get("is_coach", False)]
    if not coaches:
        await message.answer("📭 Нет тренеров")
        return
    sorted_coaches = sorted(coaches, key=lambda x: x.get("coach_rating", 0), reverse=True)[:10]
    text = "🧑‍🏫 Топ-10 тренеров\n"
    for i, p in enumerate(sorted_coaches):
        text += f"{i+1}. {p['name']} — ⭐{p.get('coach_rating', 50)}\n"
    await message.answer(text)

@dp.message(Command("staff"))
async def staff(message: Message):
    p = load(message.from_user.id)
    if not p or not p.get("is_coach"):
        await message.answer("❌ Ты не тренер!")
        return
    level = p.get("coach_staff", 0)
    await message.answer(f"🏠 Тренерский штаб\nУровень: {level+1}")

@dp.message(Command("coach_history"))
async def coach_history(message: Message):
    p = load(message.from_user.id)
    if not p or not p.get("is_coach"):
        await message.answer("❌ Ты не тренер!")
        return
    history = p.get("coach_history", [])
    await message.answer(f"📜 История\n{'\n'.join(history[-5:]) if history else 'Пока нет'}")

# ============ НОВЫЕ КОМАНДЫ ============

@dp.message(Command("rename"))
async def rename(message: Message):
    p = load(message.from_user.id)
    if not p:
        await message.answer("❌ Сначала создай карьеру!")
        return
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("❌ Используй: /rename Новое имя")
        return
    new_name = args[1]
    if p["money"] < 50000:
        await message.answer("❌ Нужно 50,000 €")
        return
    p["money"] -= 50000
    p["name"] = new_name
    save(message.from_user.id, p)
    await message.answer(f"✅ Имя изменено на <b>{new_name}</b>!")

@dp.message(Command("setemoji"))
async def setemoji(message: Message):
    p = load(message.from_user.id)
    if not p:
        await message.answer("❌ Сначала создай карьеру!")
        return
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("❌ Используй: /setemoji ⚽")
        return
    emoji = args[1]
    p["emoji"] = emoji
    save(message.from_user.id, p)
    await message.answer(f"✅ Эмодзи установлен: {emoji}")

@dp.message(Command("seasons"))
async def seasons(message: Message):
    p = load(message.from_user.id)
    if not p:
        await message.answer("❌ Сначала создай карьеру!")
        return
    stats = p.get("season_stats", [])
    if not stats:
        await message.answer("📭 Нет завершённых сезонов.")
        return
    text = "📊 История сезонов\n"
    for i, s in enumerate(stats[-5:], 1):
        text += f"{i}. Сезон {s.get('season', 0)}: ⭐{s.get('rating', 0)}\n"
    await message.answer(text)

@dp.message(Command("cup"))
async def cup(message: Message):
    p = load(message.from_user.id)
    if not p or p.get("retired") or p.get("injured") or p["fitness"] < 15:
        await message.answer("❌ Ты не можешь играть!")
        return
    goals = random.randint(0, 2)
    opp_goals = random.randint(0, 1)
    win = goals > opp_goals
    p["fitness"] = max(0, p["fitness"] - random.randint(10, 20))
    if win:
        p["money"] += 50000
        p["followers"] += 1000
        p["trophies"].append("🏆 Кубок страны")
        text = f"🏆 Кубок страны!\nПобеда!\n💰 +50,000 €"
    else:
        p["money"] += 10000
        text = f"🏆 Кубок страны!\nПоражение\n💰 +10,000 €"
    save(message.from_user.id, p)
    await message.answer(text)

@dp.message(Command("stadium"))
async def stadium(message: Message):
    p = load(message.from_user.id)
    if not p:
        await message.answer("❌ Сначала создай карьеру!")
        return
    level = p.get("stadium_level", 0)
    await message.answer(f"🏟️ Стадион\nУровень: {level+1}")

@dp.message(Command("merch"))
async def merch(message: Message):
    p = load(message.from_user.id)
    if not p:
        await message.answer("❌ Сначала создай карьеру!")
        return
    await message.answer("👕 Мерч\nСкоро будет доступно!")

@dp.message(Command("cases"))
async def cases(message: Message):
    p = load(message.from_user.id)
    if not p:
        await message.answer("❌ Сначала создай карьеру!")
        return
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎁 Обычный кейс — 10,000", callback_data="case:normal:10000")],
    ])
    await message.answer(f"🎁 Кейсы\n💰 Деньги: {money(p['money'])}", reply_markup=keyboard)

@dp.callback_query(F.data.startswith("case:"))
async def case_cb(call: CallbackQuery):
    uid = call.from_user.id
    p = load(uid)
    if not p:
        await call.answer("❌ Ошибка!", show_alert=True)
        return
    cost = int(call.data.split(":")[2])
    if p["money"] < cost:
        await call.answer(f"❌ Нужно {money(cost)}", show_alert=True)
        return
    p["money"] -= cost
    reward = random.choice(["5000 €", "10000 €", "20000 €"])
    if "€" in reward:
        amount = int(reward.replace(" €", "").replace(" ", ""))
        p["money"] += amount
    save(uid, p)
    await call.message.edit_text(f"🎁 Кейс открыт!\nВыпало: {reward}")

@dp.message(Command("friends"))
async def friends(message: Message):
    p = load(message.from_user.id)
    if not p:
        await message.answer("❌ Сначала создай карьеру!")
        return
    await message.answer("👥 Друзья\nПриглашай игроков через реферальную ссылку!")

@dp.message(Command("club_world_cup"))
async def club_world_cup(message: Message):
    p = load(message.from_user.id)
    if not p or p.get("retired") or p.get("injured") or p["fitness"] < 15:
        await message.answer("❌ Ты не можешь играть!")
        return
    goals = random.randint(0, 2)
    opp_goals = random.randint(0, 1)
    win = goals > opp_goals
    p["fitness"] = max(0, p["fitness"] - random.randint(10, 20))
    if win:
        p["money"] += 100000
        p["trophies"].append("🌍 Клубный ЧМ")
        text = f"🌍 Клубный ЧМ!\nПобеда!\n💰 +100,000 €"
    else:
        p["money"] += 20000
        text = f"🌍 Клубный ЧМ!\nПоражение\n💰 +20,000 €"
    save(message.from_user.id, p)
    await message.answer(text)

@dp.message(Command("predict"))
async def predict(message: Message):
    p = load(message.from_user.id)
    if not p:
        await message.answer("❌ Сначала создай карьеру!")
        return
    await message.answer("🔮 Прогнозы\nСкоро будет доступно!")

@dp.message(Command("stocks"))
async def stocks(message: Message):
    p = load(message.from_user.id)
    if not p:
        await message.answer("❌ Сначала создай карьеру!")
        return
    await message.answer("📈 Акции\nСкоро будет доступно!")

# ============ МЕНЮ ============

@dp.callback_query(F.data.startswith("menu:"))
async def menu_cb(call: CallbackQuery):
    p = load(call.from_user.id)
    if not p:
        await call.answer("❌ Сначала создай карьеру!", show_alert=True)
        return
    action = call.data.split(":")[1]
    menus = {
        "profile": "👤 <b>Профиль</b>\n/profile",
        "game": "⚽ <b>Игровой процесс</b>\n/train, /match, /rest",
        "stats": "📊 <b>Статистика</b>\n/stats, /trophies, /table",
        "career": "🔄 <b>Карьера</b>\n/transfers, /agent, /contract",
        "shop": "🛒 <b>Магазин</b>\n/shop, /cars, /house, /business",
        "social": "👤 <b>Социальное</b>\n/news, /family",
        "bonus": "⭐ <b>Бонусы</b>\n/daily, /bonus, /tasks, /referral, /reminder",
        "casino": "🎰 <b>Казино</b>\n/casino, /penalty",
        "achievements": "🏅 <b>Достижения</b>\n/achievements",
        "coach": "🧑‍🏫 <b>Тренерские</b>\n/coach_profile, /team, /train_team, /match_team, /tactics, /coach_trophies, /coach_leaderboard, /staff, /coach_history",
    }
    await call.message.edit_text(menus.get(action, "❌ Неизвестно"), reply_markup=main_menu_keyboard(p.get("is_coach", False)))

@dp.message(Command("donate"))
async def donate_cmd(message: Message):
    await message.answer(
        "⭐ <b>Поддержать бота</b>\n\n"
        "💰 5 ⭐ → 50,000 €\n"
        "💰 10 ⭐ → 120,000 €\n"
        "💰 25 ⭐ → 350,000 €\n"
        "💰 50 ⭐ → 800,000 €\n"
        "💰 100 ⭐ → 2,000,000 €",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⭐ 5", callback_data="donate:5")],
            [InlineKeyboardButton(text="⭐ 10", callback_data="donate:10")],
            [InlineKeyboardButton(text="⭐ 25", callback_data="donate:25")],
            [InlineKeyboardButton(text="⭐ 50", callback_data="donate:50")],
            [InlineKeyboardButton(text="⭐ 100", callback_data="donate:100")],
        ])
    )

@dp.callback_query(F.data.startswith("donate:"))
async def donate_cb(call: CallbackQuery):
    uid = call.from_user.id
    p = load(uid)
    if not p:
        await call.answer("❌ Сначала создай карьеру!", show_alert=True)
        return
    stars = int(call.data.split(":")[1])
    amounts = {"5": 50000, "10": 120000, "25": 350000, "50": 800000, "100": 2000000}
    amount = amounts.get(str(stars), 0)
    try:
        await bot.send_invoice(
            chat_id=uid,
            title="Поддержка бота",
            description=f"Донат {stars} ⭐ → {money(amount)}",
            payload=f"donate_{uid}_{stars}",
            provider_token="",
            currency="XTR",
            prices=[{"label": f"{stars} ⭐", "amount": stars}],
        )
        await call.answer("💰 Счёт отправлен!", show_alert=True)
    except Exception as e:
        await call.answer(f"❌ Ошибка: {e}", show_alert=True)

@dp.pre_checkout_query()
async def pre_checkout_query(pre_checkout_query):
    await pre_checkout_query.answer(ok=True)

@dp.message(F.successful_payment)
async def successful_payment(message: Message):
    payment = message.successful_payment
    payload = payment.invoice_payload
    stars = int(payload.split("_")[2])
    amounts = {"5": 50000, "10": 120000, "25": 350000, "50": 800000, "100": 2000000}
    amount = amounts.get(str(stars), 0)
    p = load(message.from_user.id)
    if p:
        p["money"] += amount
        save(message.from_user.id, p)
        await message.answer(f"✅ Спасибо!\n⭐ {stars} звёзд\n💰 +{money(amount)}")

# ============ ЗАПУСК ============

@dp.message(F.text.startswith("/"))
async def unknown(message: Message):
    await message.answer("❌ Неизвестная команда. Напиши /help")

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
    print("🌐 Web-сервер запущен")

async def main():
    print("🚀 Бот запущен!")
    asyncio.create_task(start_web())
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
```
