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
CUP_CLUBS = ["Реал Мадрид", "Барселона", "Манчестер Сити", "Бавария", "ПСЖ", "Ливерпуль", "Челси", "Арсенал"]
CASES = [
    {"name": "Обычный кейс", "cost": 10000, "items": ["5000 €", "10000 €", "Обычные бутсы"]},
    {"name": "Серебряный кейс", "cost": 25000, "items": ["20000 €", "50000 €", "Профессиональные бутсы"]},
    {"name": "Золотой кейс", "cost": 50000, "items": ["100000 €", "200000 €", "Вилла", "Lamborghini"]},
]
CARS_LIST = [("Lada Granta", 2000), ("Kia Rio", 8000), ("Hyundai Solaris", 12000), ("Toyota Camry", 25000), ("BMW X5", 60000), ("Mercedes S-Class", 120000), ("Porsche 911", 250000), ("Lamborghini Huracan", 500000), ("Bugatti Chiron", 3000000)]
HOUSES_LIST = [("Квартира", 150000, 5000), ("Дом", 500000, 15000), ("Вилла", 1500000, 50000), ("Особняк", 5000000, 150000), ("Замок", 15000000, 500000)]
MERCH_ITEMS = [{"name": "👕 Футболка", "cost": 25000, "income": 5000}, {"name": "🧢 Кепка", "cost": 10000, "income": 2000}]
STADIUM_UPGRADES = [{"name": "Маленький стадион", "cost": 0, "income": 0}, {"name": "Средний стадион", "cost": 200000, "income": 10000}, {"name": "Большой стадион", "cost": 500000, "income": 25000}, {"name": "Супер стадион", "cost": 1500000, "income": 50000}]
PREDICTIONS = [{"match": "Реал Мадрид vs Барселона", "odds": {"1": 2.5, "X": 3.0, "2": 2.8}}, {"match": "Манчестер Сити vs Ливерпуль", "odds": {"1": 2.2, "X": 3.2, "2": 3.0}}]
STOCKS = [{"name": "Nike", "price": 100}, {"name": "Adidas", "price": 80}, {"name": "Puma", "price": 60}]

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
        achievements.append("champion"); p["money"] += ACHIEVEMENTS["champion"]["reward"]; unlocked.append("🏆 Чемпион")
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
            f"👋 С возвращением, <b>{p['name']}</b>!\n"
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
    text = "📖 <b>Команды</b>\n\n/profile, /train, /match, /rest, /season, /calendar, /transfers, /agent, /shop, /stats, /trophies, /news, /table, /ucl, /contract, /sponsor, /daily, /national, /cars, /house, /family, /business, /history, /donate, /bonus, /achievements, /leaderboard, /penalty, /casino, /tasks, /referral, /reminder, /ping, /myid, /give\n🆕 /rename, /setemoji, /seasons, /cup, /stadium, /merch, /cases, /friends, /club_world_cup, /predict, /stocks"
    if is_coach:
        text += "\n🧑‍🏫 /coach_profile, /team, /train_team, /match_team, /tactics, /transfer_players, /squad, /coach_trophies, /coach_history, /staff, /coach_leaderboard"
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
        await message.answer("❌ /create Имя")
        return
    player = new_player(args[1])
    save(message.from_user.id, player)
    await message.answer(f"✅ Создан {args[1]}!\n⭐ 60\n🏟 {player['club']}\n🏆 {player['league']}")

@dp.message(Command("profile"))
async def profile(message: Message):
    p = load(message.from_user.id)
    if not p:
        await message.answer("❌ /create")
        return
    rank = get_rank(p["rating"], len(p.get("trophies", [])))
    text = f"👤 {p['name']} {p.get('emoji', '⚽')}\n⭐ {p['rating']}\n🏅 {rank['name']}\n🏟 {p['club']}\n🏆 {p.get('league', 'АПЛ')}\n🎂 {p['age']}\n💰 {money(p['money'])}\n💵 {money(p['salary'])}\n📈 {money(p['market_value'])}\n⚽ {p['matches']} 🥅 {p['goals']} 🎯 {p['assists']} 🏅 {p['mvps']}\n👥 {p['followers']}\n🏠 {p.get('house', 'Нет')} 🚗 {p.get('car', 'Нет')}"
    await message.answer(text)

@dp.message(Command("train"))
async def train(message: Message):
    p = load(message.from_user.id)
    if not p:
        return await message.answer("❌ /create")
    if p.get("retired") or p["fitness"] < 20:
        return await message.answer("❌")
    stat = random.choice(["pace", "shooting", "passing", "dribbling", "defending", "physical"])
    names = {"pace": "Скорость", "shooting": "Удар", "passing": "Пас", "dribbling": "Дриблинг", "defending": "Защита", "physical": "Физика"}
    plus = random.randint(1, 3)
    p[stat] = min(99, p[stat] + plus)
    p["fitness"] = max(0, p["fitness"] - random.randint(10, 20))
    p["rating"] = int((p["pace"] + p["shooting"] + p["passing"] + p["dribbling"] + p["defending"] + p["physical"]) / 6)
    save(message.from_user.id, p)
    await message.answer(f"🏋️ +{plus} {names[stat]}\n⭐ {p['rating']}")

@dp.message(Command("match"))
async def match_cmd(message: Message):
    p = load(message.from_user.id)
    if not p or p.get("retired") or p.get("injured") or p["fitness"] < 15:
        return await message.answer("❌")
    goals = random.randint(0, 2)
    assists = random.randint(0, 1)
    mvp = random.randint(1, 100) <= p["rating"] - 40
    result_num = random.randint(1, 100)
    if result_num <= 40 + (p["rating"] - 60) // 2:
        result, points = "Победа", 3
    elif result_num <= 60 + (p["rating"] - 60) // 2:
        result, points = "Ничья", 1
    else:
        result, points = "Поражение", 0
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
    gain = goals * 0.35 + assists * 0.20 + (0.50 if mvp else 0) + (0.30 if result == "Победа" else 0.10 if result == "Ничья" else 0)
    p["rating"] = round(min(99, p["rating"] + gain), 1)
    reward = goals * 8000 + assists * 5000 + (15000 if mvp else 0) + (5000 if result == "Победа" else 0)
    p["money"] += reward
    p["fitness"] = max(0, p["fitness"] - random.randint(10, 20))
    p["followers"] += random.randint(50, 300) + goals * 80 + assists * 40 + (300 if mvp else 0) + (200 if result == "Победа" else 0)
    p["week"] += 1
    check_achievements(p, message.from_user.id)
    if p["week"] >= 38:
        if p.get("season_goals", 0) >= 20:
            p["golden_boot"] += 1
            p["trophies"].append("👟 Золотая бутса")
            p["money"] += 300000
        if p["rating"] >= 85 and p.get("season_goals", 0) + p.get("season_assists", 0) >= 25:
            p["ballon"] += 1
            p["trophies"].append("🏅 Золотой мяч")
            p["money"] += 500000
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
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ Стать тренером", callback_data="become_coach:yes")],
                [InlineKeyboardButton(text="❌ Завершить", callback_data="become_coach:no")],
            ])
            return await message.answer(f"🔚 Карьера завершена!\nХочешь стать тренером?", reply_markup=keyboard)
    save(message.from_user.id, p)
    await message.answer(f"🏟 {result} (+{points})\n⚽ {goals} 🎯 {assists}\n⭐ {'MVP' if mvp else ''}\n💰 +{money(reward)}\n⭐ {p['rating']}")

@dp.message(Command("rest"))
async def rest_cmd(message: Message):
    p = load(message.from_user.id)
    if not p:
        return await message.answer("❌ /create")
    p["fitness"] = min(100, p["fitness"] + 30)
    save(message.from_user.id, p)
    await message.answer(f"😴 {p['fitness']}%")

@dp.message(Command("daily"))
async def daily(message: Message):
    p = load(message.from_user.id)
    if not p:
        return await message.answer("❌ /create")
    now = datetime.now()
    last_daily = datetime.fromisoformat(p.get("last_daily", now.isoformat()))
    if (now - last_daily).days < 1:
        return await message.answer("⏳ 24 часа")
    reward = random.randint(10000, 50000)
    p["money"] += reward
    p["last_daily"] = now.isoformat()
    save(message.from_user.id, p)
    await message.answer(f"🎁 +{money(reward)}")

@dp.message(Command("transfers"))
async def transfers(message: Message):
    p = load(message.from_user.id)
    if not p or p.get("retired") or p.get("agent") == "Нет":
        return await message.answer("❌")
    clubs = get_clubs_by_rating(p["rating"])
    offers = random.sample(clubs, min(3, len(clubs)))
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"🏟 {club} — {money(sal)}", callback_data=f"transfer:{club}:{sal}")] for club, sal in offers
    ])
    await message.answer(f"✈️ {p['club']}", reply_markup=keyboard)

@dp.callback_query(F.data.startswith("transfer:"))
async def transfer_cb(call: CallbackQuery):
    uid = call.from_user.id
    p = load(uid)
    if not p:
        return await call.answer("❌", show_alert=True)
    parts = call.data.split(":")
    club, salary = parts[1], int(parts[2])
    p["club"] = club
    p["league"] = get_league_for_club(club)
    p["salary"] = salary
    save(uid, p)
    await call.message.edit_text(f"✅ {club}!\n💵 {money(salary)}")

@dp.message(Command("agent"))
async def agent(message: Message):
    p = load(message.from_user.id)
    if not p:
        return await message.answer("❌ /create")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="😐 10,000", callback_data="agent:bad:10000")],
        [InlineKeyboardButton(text="🙂 30,000", callback_data="agent:medium:30000")],
        [InlineKeyboardButton(text="😎 70,000", callback_data="agent:good:70000")],
        [InlineKeyboardButton(text="🌟 150,000", callback_data="agent:top:150000")],
    ])
    await message.answer(f"🧑‍💼 {p.get('agent', 'Нет')}\n💰 {money(p['money'])}", reply_markup=keyboard)

@dp.callback_query(F.data.startswith("agent:"))
async def agent_cb(call: CallbackQuery):
    uid = call.from_user.id
    p = load(uid)
    if not p:
        return await call.answer("❌", show_alert=True)
    parts = call.data.split(":")
    name = {"bad": "Плохой", "medium": "Средний", "good": "Хороший", "top": "Топ"}[parts[1]]
    cost = int(parts[2])
    if p["money"] < cost:
        return await call.answer(f"❌ {money(cost)}", show_alert=True)
    p["money"] -= cost
    p["agent"] = name
    save(uid, p)
    await call.message.edit_text(f"✅ {name}!\n💰 {money(p['money'])}")

@dp.message(Command("shop"))
async def shop(message: Message):
    p = load(message.from_user.id)
    if not p:
        return await message.answer("❌ /create")
    items = {
        "boots": {"name": "👟 Бутсы", "cost": 50000, "stat": "+2 скорость"},
        "equipment": {"name": "🎽 Экипировка", "cost": 30000, "stat": "+1 физика"},
        "fitness": {"name": "💪 Тренажёрка", "cost": 10000, "stat": "+10 форма"},
        "recovery": {"name": "🧊 Восстановление", "cost": 25000, "stat": "+15 форма + лечение"},
        "nutrition": {"name": "🥗 Диетолог", "cost": 15000, "stat": "+5 форма"},
        "psychologist": {"name": "🧠 Психолог", "cost": 20000, "stat": "+10 мораль"},
    }
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{item['name']} — {money(item['cost'])}", callback_data=f"shop:{key}")] for key, item in items.items()
    ])
    await message.answer(f"🛒 {money(p['money'])}", reply_markup=keyboard)

@dp.callback_query(F.data.startswith("shop:"))
async def shop_cb(call: CallbackQuery):
    uid = call.from_user.id
    p = load(uid)
    if not p:
        return await call.answer("❌", show_alert=True)
    items = {
        "boots": {"name": "👟 Бутсы", "cost": 50000, "stat": "+2 скорость"},
        "equipment": {"name": "🎽 Экипировка", "cost": 30000, "stat": "+1 физика"},
        "fitness": {"name": "💪 Тренажёрка", "cost": 10000, "stat": "+10 форма"},
        "recovery": {"name": "🧊 Восстановление", "cost": 25000, "stat": "+15 форма + лечение"},
        "nutrition": {"name": "🥗 Диетолог", "cost": 15000, "stat": "+5 форма"},
        "psychologist": {"name": "🧠 Психолог", "cost": 20000, "stat": "+10 мораль"},
    }
    item = items[call.data.split(":")[1]]
    if p["money"] < item["cost"]:
        return await call.answer(f"❌ {money(item['cost'])}", show_alert=True)
    p["money"] -= item["cost"]
    key = call.data.split(":")[1]
    if key == "boots":
        p["pace"] = min(99, p["pace"] + 2)
    elif key == "equipment":
        p["physical"] = min(99, p["physical"] + 1)
    elif key == "fitness":
        p["fitness"] = min(100, p["fitness"] + 10)
    elif key == "recovery":
        p["fitness"] = min(100, p["fitness"] + 15)
        if p.get("injured"): p["injured"] = False; p["injury_days"] = 0
    elif key == "nutrition":
        p["fitness"] = min(100, p["fitness"] + 5)
    elif key == "psychologist":
        p["morale"] = min(100, p["morale"] + 10)
    save(uid, p)
    await call.message.edit_text(f"✅ {item['name']}\n💰 {money(p['money'])}")

@dp.message(Command("cars"))
async def cars(message: Message):
    p = load(message.from_user.id)
    if not p:
        return await message.answer("❌ /create")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{car} — {money(price)}", callback_data=f"car:{car}:{price}")] for car, price in CARS_LIST
    ])
    await message.answer(f"🚗 {money(p['money'])}\n🚘 {p.get('car', 'Нет')}", reply_markup=keyboard)

@dp.callback_query(F.data.startswith("car:"))
async def car_cb(call: CallbackQuery):
    uid = call.from_user.id
    p = load(uid)
    if not p:
        return await call.answer("❌", show_alert=True)
    parts = call.data.split(":")
    car, price = parts[1], int(parts[2])
    if p["money"] < price:
        return await call.answer(f"❌ {money(price)}", show_alert=True)
    p["money"] -= price
    p["car"] = car
    save(uid, p)
    await call.message.edit_text(f"🚗 {car}\n💰 {money(p['money'])}")

@dp.message(Command("house"))
async def house(message: Message):
    p = load(message.from_user.id)
    if not p:
        return await message.answer("❌ /create")
    if p.get("house") != "Нет":
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🏠 Сдать в аренду", callback_data="rent:house")]])
        return await message.answer(f"🏠 {p['house']}\n💰 {money(p.get('rental_income', 0))}/нед", reply_markup=keyboard)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{home} — {money(price)} (аренда {money(rent)}/нед)", callback_data=f"house:{home}:{price}:{rent}")] for home, price, rent in HOUSES_LIST
    ])
    await message.answer(f"🏠 {money(p['money'])}", reply_markup=keyboard)

@dp.callback_query(F.data.startswith("house:"))
async def house_cb(call: CallbackQuery):
    uid = call.from_user.id
    p = load(uid)
    if not p:
        return await call.answer("❌", show_alert=True)
    parts = call.data.split(":")
    home, price, rent = parts[1], int(parts[2]), int(parts[3])
    if p["money"] < price:
        return await call.answer(f"❌ {money(price)}", show_alert=True)
    p["money"] -= price
    p["house"] = home
    p["rental_income"] = rent
    save(uid, p)
    await call.message.edit_text(f"🏠 {home}\n💰 {money(p['money'])}")

@dp.callback_query(F.data.startswith("rent:"))
async def rent_cb(call: CallbackQuery):
    uid = call.from_user.id
    p = load(uid)
    if not p or p.get("house") == "Нет":
        return await call.answer("❌", show_alert=True)
    rent = p.get("rental_income", 0)
    if rent > 0:
        p["money"] += rent * 4
        save(uid, p)
        await call.message.edit_text(f"🏠 {p['house']}\n💰 +{money(rent * 4)}")
    else:
        await call.answer("❌")

@dp.message(Command("business"))
async def business(message: Message):
    p = load(message.from_user.id)
    if not p:
        return await message.answer("❌ /create")
    if p.get("business"):
        return await message.answer(f"🏢 {p.get('business_type', 'Нет')}\n💰 {money(p.get('business_income', 0))}/нед")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏪 Магазин 30,000", callback_data="business:small:30000")],
        [InlineKeyboardButton(text="🛍️ ТЦ 200,000", callback_data="business:medium:200000")],
        [InlineKeyboardButton(text="🏗️ Стройка 500,000", callback_data="business:large:500000")],
        [InlineKeyboardButton(text="🏥 Больница 1,000,000", callback_data="business:hospital:1000000")],
    ])
    await message.answer(f"🏢 {money(p['money'])}", reply_markup=keyboard)

@dp.callback_query(F.data.startswith("business:"))
async def business_cb(call: CallbackQuery):
    uid = call.from_user.id
    p = load(uid)
    if not p:
        return await call.answer("❌", show_alert=True)
    parts = call.data.split(":")
    types = {"small": ("🏪 Магазин", 5000), "medium": ("🛍️ ТЦ", 25000), "large": ("🏗️ Стройка", 60000), "hospital": ("🏥 Больница", 100000)}
    name, income = types[parts[1]]
    cost = int(parts[2])
    if p["money"] < cost:
        return await call.answer(f"❌ {money(cost)}", show_alert=True)
    p["money"] -= cost
    p["business"] = True
    p["business_type"] = name
    p["business_income"] = income
    save(uid, p)
    await call.message.edit_text(f"✅ {name}\n💰 {money(income)}/нед")

@dp.message(Command("stats"))
async def stats(message: Message):
    p = load(message.from_user.id)
    if not p:
        return await message.answer("❌ /create")
    await message.answer(f"📊 {p['name']}\n⚽ {p['goals']}\n🎯 {p['assists']}\n🎮 {p['matches']}\n⭐ {p['mvps']}\n🏃 {p['pace']}\n🎯 {p['shooting']}\n🔄 {p['passing']}\n🌀 {p['dribbling']}\n🛡 {p['defending']}\n💪 {p['physical']}\n⚡ {p['fitness']}%")

@dp.message(Command("table"))
async def table(message: Message):
    p = load(message.from_user.id)
    if not p:
        return await message.answer("❌ /create")
    clubs = LEAGUES.get(p.get("league", "АПЛ"), LEAGUES["АПЛ"])
    table_data = []
    for club in clubs:
        if club == p["club"]:
            pts = p.get("league_points", 0)
        else:
            pts = random.randint(20, 85)
        table_data.append((club, pts))
    sorted_table = sorted(table_data, key=lambda x: x[1], reverse=True)
    lines = [f"🏆 {p.get('league', 'АПЛ')}"]
    for i, (club, pts) in enumerate(sorted_table[:10]):
        lines.append(f"{i+1}. {club} — {pts} {'← ты' if club == p['club'] else ''}")
    await message.answer("\n".join(lines))

@dp.message(Command("ucl"))
async def ucl(message: Message):
    p = load(message.from_user.id)
    if not p:
        return await message.answer("❌ /create")
    clubs = UCL_CLUBS.copy()
    random.shuffle(clubs)
    lines = ["⭐ Лига чемпионов"]
    for i in range(0, len(clubs), 2):
        if i + 1 < len(clubs):
            lines.append(f"⚔️ {clubs[i]} vs {clubs[i+1]}")
    await message.answer("\n".join(lines))

@dp.message(Command("trophies"))
async def trophies(message: Message):
    p = load(message.from_user.id)
    if not p:
        return await message.answer("❌ /create")
    t = "\n".join(p.get("trophies", [])) or "Нет"
    await message.answer(f"🏆\n{t}")

@dp.message(Command("contract"))
async def contract(message: Message):
    p = load(message.from_user.id)
    if not p:
        return await message.answer("❌ /create")
    await message.answer(f"📄 {p['club']}\n🏆 {p.get('league', 'АПЛ')}\n💰 {money(p['salary'])}\n📈 {money(p['market_value'])}\n💵 {money(p['money'])}")

@dp.message(Command("sponsor"))
async def sponsor(message: Message):
    p = load(message.from_user.id)
    if not p:
        return await message.answer("❌ /create")
    sponsors = [("Nike", 500000), ("Adidas", 450000), ("Puma", 300000), ("EA Sports", 700000)]
    if p["followers"] < 10000:
        return await message.answer("❌ 10,000 подписчиков")
    name, reward = random.choice(sponsors)
    p["money"] += reward
    save(message.from_user.id, p)
    await message.answer(f"🤝 {name}\n💰 +{money(reward)}")

@dp.message(Command("national"))
async def national(message: Message):
    p = load(message.from_user.id)
    if not p:
        return await message.answer("❌ /create")
    if p["rating"] < 75:
        return await message.answer("❌ 75 рейтинг")
    goals = random.randint(0, 2)
    assists = random.randint(0, 1)
    result = random.choice(["Победа", "Ничья", "Поражение"])
    p["goals"] += goals
    p["assists"] += assists
    save(message.from_user.id, p)
    await message.answer(f"🇦🇿 {result}\n⚽ {goals} 🎯 {assists}")

@dp.message(Command("family"))
async def family(message: Message):
    p = load(message.from_user.id)
    if not p or p.get("retired"):
        return await message.answer("❌")
    if p.get("wife") is None:
        girls = ["Анна", "София", "Виктория", "Мария", "Эмилия", "Диана", "Алина"]
        p["wife"] = random.choice(girls)
        save(message.from_user.id, p)
        return await message.answer(f"💍 {p['wife']}")
    p["relationship_days"] = p.get("relationship_days", 0) + 1
    if p["relationship_days"] >= 30 and random.randint(1, 100) <= 20:
        p["children"] += 1
        p["relationship_days"] = 0
        save(message.from_user.id, p)
        await message.answer(f"👶 {p['wife']} родила!\n👨‍👩‍👧 {p['children']}")
    else:
        await message.answer(f"❤️ {p['wife']}\n👶 {p.get('children', 0)}\n📅 {p['relationship_days']}")

@dp.message(Command("news"))
async def news(message: Message):
    p = load(message.from_user.id)
    if not p:
        return await message.answer("❌ /create")
    await message.answer(random.choice([f"📰 {p['name']} оформил дубль!", f"📰 {p['club']} рассчитывает на {p['name']}"]))

@dp.message(Command("history"))
async def history_cmd(message: Message):
    history = load_history(message.from_user.id)
    if not history:
        return await message.answer("📭")
    text = "📜\n" + "\n".join([f"{i+1}. {c['name']} — ⭐{c['rating']}" for i, c in enumerate(history[-5:])])
    await message.answer(text)

@dp.message(Command("give"))
async def give_money(message: Message):
    p = load(message.from_user.id)
    if not p:
        return await message.answer("❌ /create")
    args = message.text.split()
    if len(args) < 3:
        return await message.answer("❌ /give @username сумма")
    username = args[1].replace("@", "")
    amount = int(args[2])
    if p["money"] < amount:
        return await message.answer(f"❌ {money(p['money'])}")
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
        return await message.answer("❌")
    p["money"] -= amount
    save(message.from_user.id, p)
    await message.answer(f"✅ {money(amount)} -> {username}")

@dp.message(Command("bonus"))
async def bonus_cmd(message: Message):
    p = load(message.from_user.id)
    if not p or p.get("bonus_received", False):
        return await message.answer("❌")
    p["money"] += 50000
    p["bonus_received"] = True
    save(message.from_user.id, p)
    await message.answer(f"✅ +50,000")

@dp.message(Command("achievements"))
async def achievements_cmd(message: Message):
    p = load(message.from_user.id)
    if not p:
        return await message.answer("❌ /create")
    unlocked = p.get("achievements", [])
    if not unlocked:
        return await message.answer("🏆 Нет")
    text = "🏆\n" + "\n".join([ACHIEVEMENTS[ach]["name"] for ach in unlocked if ach in ACHIEVEMENTS])
    await message.answer(text)

@dp.message(Command("leaderboard"))
async def leaderboard(message: Message):
    players = get_all_players()
    if not players:
        return await message.answer("📭")
    sorted_players = sorted(players, key=lambda x: x.get("rating", 0), reverse=True)[:10]
    text = "🏆\n" + "\n".join([f"{i+1}. {p['name']} — ⭐{p['rating']}" for i, p in enumerate(sorted_players)])
    await message.answer(text)

@dp.message(Command("penalty"))
async def penalty(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️", callback_data="penalty:left"), InlineKeyboardButton(text="➡️", callback_data="penalty:right")],
        [InlineKeyboardButton(text="⬆️", callback_data="penalty:up"), InlineKeyboardButton(text="⬇️", callback_data="penalty:down")]
    ])
    await message.answer("⚽", reply_markup=keyboard)

@dp.callback_query(F.data.startswith("penalty:"))
async def penalty_cb(call: CallbackQuery):
    uid = call.from_user.id
    p = load(uid)
    if not p:
        return await call.answer("❌", show_alert=True)
    user_choice = call.data.split(":")[1]
    bot_choice = random.choice(["left", "right", "up", "down"])
    if user_choice == bot_choice:
        p["money"] += 10000
        save(uid, p)
        await call.message.edit_text(f"⚽ ГОЛ!\n💰 +10,000")
    else:
        await call.message.edit_text("⚽ МИМО!")

@dp.message(Command("casino"))
async def casino(message: Message):
    p = load(message.from_user.id)
    if not p:
        return await message.answer("❌ /create")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎰 Слоты", callback_data="casino:slots")],
        [InlineKeyboardButton(text="🪙 Орёл/Решка", callback_data="casino:coin")],
        [InlineKeyboardButton(text="♠️ Рулетка", callback_data="casino:roulette")],
    ])
    await message.answer(f"🎰 {money(p['money'])}", reply_markup=keyboard)

@dp.callback_query(F.data.startswith("casino:slots"))
async def casino_slots(call: CallbackQuery):
    uid = call.from_user.id
    p = load(uid)
    if not p or p["money"] < 5000:
        return await call.answer("❌", show_alert=True)
    symbols = ["🍒", "🍋", "🍊", "🍇", "💎", "7️⃣"]
    result = [random.choice(symbols) for _ in range(3)]
    win = 0
    if result[0] == result[1] == result[2]:
        win = 50000
    elif result[0] == result[1] or result[0] == result[2] or result[1] == result[2]:
        win = 10000
    p["money"] -= 5000
    p["money"] += win
    save(uid, p)
    await call.message.edit_text(f"🎰 {' '.join(result)}\n🏆 {money(win)}\n💵 {money(p['money'])}")

@dp.callback_query(F.data.startswith("casino:coin"))
async def casino_coin(call: CallbackQuery):
    uid = call.from_user.id
    p = load(uid)
    if not p or p["money"] < 10000:
        return await call.answer("❌", show_alert=True)
    user_choice = random.choice(["Орёл", "Решка"])
    bot_choice = random.choice(["Орёл", "Решка"])
    win = 10000 if user_choice == bot_choice else 0
    p["money"] -= 10000
    p["money"] += win
    save(uid, p)
    await call.message.edit_text(f"🪙 {user_choice} vs {bot_choice}\n🏆 {money(win)}\n💵 {money(p['money'])}")

@dp.callback_query(F.data.startswith("casino:roulette"))
async def casino_roulette(call: CallbackQuery):
    uid = call.from_user.id
    p = load(uid)
    if not p or p["money"] < 20000:
        return await call.answer("❌", show_alert=True)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔴", callback_data="roulette:red")],
        [InlineKeyboardButton(text="⚫", callback_data="roulette:black")],
        [InlineKeyboardButton(text="🟢", callback_data="roulette:green")],
    ])
    await call.message.edit_text("♠️ 20,000", reply_markup=keyboard)

@dp.callback_query(F.data.startswith("roulette:"))
async def roulette_cb(call: CallbackQuery):
    uid = call.from_user.id
    p = load(uid)
    if not p:
        return await call.answer("❌", show_alert=True)
    colors = ["red", "black", "green"]
    weights = [0.48, 0.48, 0.04]
    bot_choice = random.choices(colors, weights=weights)[0]
    win = 0
    if call.data.split(":")[1] == bot_choice:
        win = 280000 if bot_choice == "green" else 40000
    p["money"] -= 20000
    p["money"] += win
    save(uid, p)
    await call.message.edit_text(f"♠️ {bot_choice}\n🏆 {money(win)}\n💵 {money(p['money'])}")

@dp.message(Command("tasks"))
async def tasks(message: Message):
    p = load(message.from_user.id)
    if not p:
        return await message.answer("❌ /create")
    tasks = p.get("daily_tasks", {})
    required = tasks.get("required", {"goals": random.randint(2,5), "matches": random.randint(3,7), "points": random.randint(10,20)})
    current = tasks.get("current", {"goals": 0, "matches": 0, "points": 0})
    if tasks.get("completed", False):
        return await message.answer("✅ +50,000")
    await message.answer(f"📋 ⚽ {current.get('goals', 0)}/{required['goals']}\n🎮 {current.get('matches', 0)}/{required['matches']}\n📊 {current.get('points', 0)}/{required['points']}\n🏆 50,000")

@dp.message(Command("referral"))
async def referral(message: Message):
    p = load(message.from_user.id)
    if not p:
        return await message.answer("❌ /create")
    await message.answer(f"🔗 https://t.me/GoalTimeNews_bot?start={message.from_user.id}\n👥 {len(p.get('referrals', []))}")

@dp.message(Command("reminder"))
async def reminder(message: Message):
    p = load(message.from_user.id)
    if not p:
        return await message.answer("❌ /create")
    now = datetime.now()
    last = datetime.fromisoformat(p.get("last_reminder", now.isoformat()))
    if (now - last).days >= 1:
        p["money"] += 10000
        p["last_reminder"] = now.isoformat()
        save(message.from_user.id, p)
        await message.answer("⏰ +10,000")
    else:
        await message.answer("⏰ Завтра")

@dp.message(Command("donate"))
async def donate_cmd(message: Message):
    await message.answer(
        "⭐\n5⭐ → 50,000\n10⭐ → 120,000\n25⭐ → 350,000\n50⭐ → 800,000\n100⭐ → 2,000,000",
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
        return await call.answer("❌ /create", show_alert=True)
    stars = int(call.data.split(":")[1])
    amounts = {"5": 50000, "10": 120000, "25": 350000, "50": 800000, "100": 2000000}
    try:
        await bot.send_invoice(
            chat_id=uid,
            title="Поддержка",
            description=f"{stars}⭐ → {money(amounts[str(stars)])}",
            payload=f"donate_{uid}_{stars}",
            provider_token="",
            currency="XTR",
            prices=[{"label": f"{stars}⭐", "amount": stars}],
        )
        await call.answer("💰", show_alert=True)
    except Exception as e:
        await call.answer(f"❌ {e}", show_alert=True)

@dp.pre_checkout_query()
async def pre_checkout_query(pre_checkout_query):
    await pre_checkout_query.answer(ok=True)

@dp.message(F.successful_payment)
async def successful_payment(message: Message):
    payment = message.successful_payment
    stars = int(payment.invoice_payload.split("_")[2])
    amounts = {"5": 50000, "10": 120000, "25": 350000, "50": 800000, "100": 2000000}
    p = load(message.from_user.id)
    if p:
        p["money"] += amounts[str(stars)]
        save(message.from_user.id, p)
        await message.answer(f"✅ {stars}⭐\n💰 +{money(amounts[str(stars)])}")

# ============ ТРЕНЕРСКИЕ ============

@dp.callback_query(F.data.startswith("become_coach:"))
async def become_coach_cb(call: CallbackQuery):
    uid = call.from_user.id
    p = load(uid)
    if not p:
        return await call.answer("❌", show_alert=True)
    if call.data.split(":")[1] == "yes":
        p["is_coach"] = True
        p["coach_team"] = random.choice(["Кристал Пэлас", "Ренн", "Болонья"])
        p["coach_rating"] = 50
        p["coach_money"] = 50000
        save(uid, p)
        await call.message.edit_text(f"🧑‍🏫 {p['coach_team']}\n⭐ {p['coach_rating']}\n💰 {money(p['coach_money'])}")
    else:
        await call.message.edit_text("🔚")

@dp.message(Command("coach_profile"))
async def coach_profile(message: Message):
    p = load(message.from_user.id)
    if not p or not p.get("is_coach"):
        return await message.answer("❌")
    await message.answer(f"🧑‍🏫 {p['name']}\n⭐ {p['coach_rating']}\n🏟 {p.get('coach_team', 'Нет')}\n📊 {p.get('coach_wins', 0)}-{p.get('coach_draws', 0)}-{p.get('coach_losses', 0)}\n🏆 {len(p.get('coach_trophies', []))}\n💰 {money(p.get('coach_money', 0))}")

@dp.message(Command("team"))
async def team(message: Message):
    p = load(message.from_user.id)
    if not p or not p.get("is_coach"):
        return await message.answer("❌")
    await message.answer(f"🏟 {p.get('coach_team', 'Нет')}\n👥 {len(p.get('coach_players', []))}")

@dp.message(Command("train_team"))
async def train_team(message: Message):
    p = load(message.from_user.id)
    if not p or not p.get("is_coach"):
        return await message.answer("❌")
    p["coach_rating"] = min(100, p.get("coach_rating", 50) + random.randint(1, 3))
    save(message.from_user.id, p)
    await message.answer(f"🧑‍🏫 ⭐ {p['coach_rating']}")

@dp.message(Command("match_team"))
async def match_team(message: Message):
    p = load(message.from_user.id)
    if not p or not p.get("is_coach"):
        return await message.answer("❌")
    opp = random.choice(["Реал", "Барса", "Бавария"])
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
    await message.answer(f"🏟 {result}\n⚔️ {opp}\n⭐ {p['coach_rating']}")

@dp.message(Command("tactics"))
async def tactics(message: Message):
    p = load(message.from_user.id)
    if not p or not p.get("is_coach"):
        return await message.answer("❌")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚔️ Атакующая", callback_data="tactics:attack")],
        [InlineKeyboardButton(text="🛡️ Защитная", callback_data="tactics:defense")],
        [InlineKeyboardButton(text="⚖️ Сбалансированная", callback_data="tactics:balanced")],
    ])
    await message.answer(f"🧠 {p.get('coach_tactics', 'Сбалансированная')}", reply_markup=keyboard)

@dp.callback_query(F.data.startswith("tactics:"))
async def tactics_cb(call: CallbackQuery):
    uid = call.from_user.id
    p = load(uid)
    if not p:
        return await call.answer("❌", show_alert=True)
    names = {"attack": "⚔️ Атакующая", "defense": "🛡️ Защитная", "balanced": "⚖️ Сбалансированная"}
    p["coach_tactics"] = names[call.data.split(":")[1]]
    save(uid, p)
    await call.message.edit_text(f"✅ {p['coach_tactics']}")

@dp.message(Command("coach_trophies"))
async def coach_trophies(message: Message):
    p = load(message.from_user.id)
    if not p or not p.get("is_coach"):
        return await message.answer("❌")
    t = "\n".join(p.get("coach_trophies", [])) or "Нет"
    await message.answer(f"🏆\n{t}")

@dp.message(Command("coach_leaderboard"))
async def coach_leaderboard(message: Message):
    players = get_all_players()
    coaches = [p for p in players if p.get("is_coach", False)]
    if not coaches:
        return await message.answer("📭")
    sorted_coaches = sorted(coaches, key=lambda x: x.get("coach_rating", 0), reverse=True)[:10]
    text = "🧑‍🏫\n" + "\n".join([f"{i+1}. {p['name']} — ⭐{p.get('coach_rating', 50)}" for i, p in enumerate(sorted_coaches)])
    await message.answer(text)

@dp.message(Command("staff"))
async def staff(message: Message):
    p = load(message.from_user.id)
    if not p or not p.get("is_coach"):
        return await message.answer("❌")
    level = p.get("coach_staff", 0)
    costs = [50000, 200000, 500000]
    if level >= 3:
        return await message.answer("🏠 Максимум")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"⬆️ {money(costs[level])}", callback_data="staff:upgrade")]
    ])
    await message.answer(f"🏠 Уровень {level+1}", reply_markup=keyboard)

@dp.callback_query(F.data.startswith("staff:"))
async def staff_cb(call: CallbackQuery):
    uid = call.from_user.id
    p = load(uid)
    if not p:
        return await call.answer("❌", show_alert=True)
    level = p.get("coach_staff", 0)
    costs = [50000, 200000, 500000]
    if level >= 3:
        return await call.answer("✅", show_alert=True)
    if p.get("coach_money", 0) < costs[level]:
        return await call.answer(f"❌ {money(costs[level])}", show_alert=True)
    p["coach_money"] -= costs[level]
    p["coach_staff"] = level + 1
    save(uid, p)
    await call.message.edit_text(f"✅ Уровень {level+2}")

@dp.message(Command("coach_history"))
async def coach_history(message: Message):
    p = load(message.from_user.id)
    if not p or not p.get("is_coach"):
        return await message.answer("❌")
    history = p.get("coach_history", [])
    await message.answer(f"📜\n{'\n'.join(history[-5:]) or 'Нет'}")

# ============ НОВЫЕ КОМАНДЫ ============

@dp.message(Command("rename"))
async def rename(message: Message):
    p = load(message.from_user.id)
    if not p or p["money"] < 50000:
        return await message.answer("❌")
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        return await message.answer("❌ /rename Имя")
    p["money"] -= 50000
    p["name"] = args[1]
    save(message.from_user.id, p)
    await message.answer(f"✅ {args[1]}")

@dp.message(Command("setemoji"))
async def setemoji(message: Message):
    p = load(message.from_user.id)
    if not p:
        return await message.answer("❌")
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        return await message.answer("❌ /setemoji ⚽")
    p["emoji"] = args[1]
    save(message.from_user.id, p)
    await message.answer(f"✅ {args[1]}")

@dp.message(Command("seasons"))
async def seasons(message: Message):
    p = load(message.from_user.id)
    if not p:
        return await message.answer("❌")
    stats = p.get("season_stats", [])
    if not stats:
        return await message.answer("📭")
    text = "📊\n" + "\n".join([f"{i+1}. Сезон {s.get('season', 0)} — ⭐{s.get('rating', 0)}" for i, s in enumerate(stats[-5:])])
    await message.answer(text)

@dp.message(Command("cup"))
async def cup(message: Message):
    p = load(message.from_user.id)
    if not p or p.get("retired") or p.get("injured") or p["fitness"] < 15:
        return await message.answer("❌")
    opp = random.choice(CUP_CLUBS)
    goals = random.randint(0, 2)
    opp_goals = random.randint(0, 1)
    win = goals > opp_goals
    p["fitness"] = max(0, p["fitness"] - random.randint(10, 20))
    if win:
        p["money"] += 50000
        p["trophies"].append("🏆 Кубок страны")
        text = f"🏆 {goals}-{opp_goals} vs {opp}\n💰 +50,000"
    else:
        p["money"] += 10000
        text = f"🏆 {goals}-{opp_goals} vs {opp}\n💰 +10,000"
    save(message.from_user.id, p)
    await message.answer(text)

@dp.message(Command("stadium"))
async def stadium(message: Message):
    p = load(message.from_user.id)
    if not p:
        return await message.answer("❌")
    level = p.get("stadium_level", 0)
    current = STADIUM_UPGRADES[level]
    if level >= len(STADIUM_UPGRADES)-1:
        return await message.answer(f"🏟️ {current['name']}\n💰 {money(current['income'])}")
    next_up = STADIUM_UPGRADES[level+1]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"⬆️ {next_up['name']} — {money(next_up['cost'])}", callback_data="stadium:upgrade")]
    ])
    await message.answer(f"🏟️ {current['name']} — {money(current['income'])}\n⬆️ {next_up['name']} — {money(next_up['cost'])}", reply_markup=keyboard)

@dp.callback_query(F.data.startswith("stadium:"))
async def stadium_cb(call: CallbackQuery):
    uid = call.from_user.id
    p = load(uid)
    if not p:
        return await call.answer("❌", show_alert=True)
    level = p.get("stadium_level", 0)
    if level >= len(STADIUM_UPGRADES)-1:
        return await call.answer("✅", show_alert=True)
    next_up = STADIUM_UPGRADES[level+1]
    if p["money"] < next_up["cost"]:
        return await call.answer(f"❌ {money(next_up['cost'])}", show_alert=True)
    p["money"] -= next_up["cost"]
    p["stadium_level"] = level + 1
    save(uid, p)
    await call.message.edit_text(f"✅ {next_up['name']}\n💰 {money(next_up['income'])}")

@dp.message(Command("merch"))
async def merch(message: Message):
    p = load(message.from_user.id)
    if not p:
        return await message.answer("❌")
    merch_items = p.get("merch_items", [])
    if merch_items:
        total = sum(item.get("income", 0) for item in merch_items)
        return await message.answer(f"👕\n{'\n'.join([f\"{item['name']} — {money(item['income'])}/нед\" for item in merch_items])}\n💰 {money(total)}")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{item['name']} — {money(item['cost'])}", callback_data=f"merch:{item['name']}:{item['cost']}:{item['income']}")] for item in MERCH_ITEMS
    ])
    await message.answer(f"👕 {money(p['money'])}", reply_markup=keyboard)

@dp.callback_query(F.data.startswith("merch:"))
async def merch_cb(call: CallbackQuery):
    uid = call.from_user.id
    p = load(uid)
    if not p:
        return await call.answer("❌", show_alert=True)
    parts = call.data.split(":")
    name, cost, income = parts[1], int(parts[2]), int(parts[3])
    if p["money"] < cost:
        return await call.answer(f"❌ {money(cost)}", show_alert=True)
    p["money"] -= cost
    if "merch_items" not in p:
        p["merch_items"] = []
    p["merch_items"].append({"name": name, "income": income})
    save(uid, p)
    await call.message.edit_text(f"✅ {name}\n💰 {money(income)}/нед")

@dp.message(Command("cases"))
async def cases(message: Message):
    p = load(message.from_user.id)
    if not p:
        return await message.answer("❌")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{case['name']} — {money(case['cost'])}", callback_data=f"case:{case['name']}:{case['cost']}")] for case in CASES
    ])
    await message.answer(f"🎁 {money(p['money'])}\n🔓 {p.get('cases_opened', 0)}", reply_markup=keyboard)

@dp.callback_query(F.data.startswith("case:"))
async def case_cb(call: CallbackQuery):
    uid = call.from_user.id
    p = load(uid)
    if not p:
        return await call.answer("❌", show_alert=True)
    parts = call.data.split(":")
    case_name = parts[1]
    cost = int(parts[2])
    if p["money"] < cost:
        return await call.answer(f"❌ {money(cost)}", show_alert=True)
    p["money"] -= cost
    p["cases_opened"] = p.get("cases_opened", 0) + 1
    for case in CASES:
        if case["name"] == case_name:
            prize = random.choice(case["items"])
            break
    if "€" in prize:
        amount = int(prize.replace(" €", ""))
        p["money"] += amount
        text = f"🎁 {prize}\n💰 {money(amount)}"
    else:
        text = f"🎁 {prize}"
    save(uid, p)
    await call.message.edit_text(text)

@dp.message(Command("friends"))
async def friends(message: Message):
    p = load(message.from_user.id)
    if not p:
        return await message.answer("❌")
    friends = p.get("friends", [])
    await message.answer(f"👥\n{'\n'.join(friends[:10]) or 'Нет'}")

@dp.message(Command("club_world_cup"))
async def club_world_cup(message: Message):
    p = load(message.from_user.id)
    if not p or p.get("retired") or p.get("injured") or p["fitness"] < 15:
        return await message.answer("❌")
    opp = random.choice(["Реал", "Барса", "МС", "Бавария"])
    goals = random.randint(0, 2)
    opp_goals = random.randint(0, 1)
    win = goals > opp_goals
    p["fitness"] = max(0, p["fitness"] - random.randint(10, 20))
    if win:
        p["money"] += 100000
        p["trophies"].append("🌍 Клубный ЧМ")
        text = f"🌍 {goals}-{opp_goals} vs {opp}\n💰 +100,000"
    else:
        p["money"] += 20000
        text = f"🌍 {goals}-{opp_goals} vs {opp}\n💰 +20,000"
    save(message.from_user.id, p)
    await message.answer(text)

@dp.message(Command("predict"))
async def predict(message: Message):
    p = load(message.from_user.id)
    if not p:
        return await message.answer("❌")
    match = random.choice(PREDICTIONS)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"1 — {match['odds']['1']}", callback_data=f"predict:{match['match']}:1:{match['odds']['1']}"),
         InlineKeyboardButton(text=f"X — {match['odds']['X']}", callback_data=f"predict:{match['match']}:X:{match['odds']['X']}"),
         InlineKeyboardButton(text=f"2 — {match['odds']['2']}", callback_data=f"predict:{match['match']}:2:{match['odds']['2']}")]
    ])
    await message.answer(f"🔮 {match['match']}\n💰 10,000", reply_markup=keyboard)

@dp.callback_query(F.data.startswith("predict:"))
async def predict_cb(call: CallbackQuery):
    uid = call.from_user.id
    p = load(uid)
    if not p or p["money"] < 10000:
        return await call.answer("❌", show_alert=True)
    parts = call.data.split(":")
    match, choice, odds = parts[1], parts[2], float(parts[3])
    p["money"] -= 10000
    result = random.choice(["1", "X", "2"])
    if choice == result:
        win = int(10000 * odds)
        p["money"] += win
        text = f"✅ {match}\n💰 {money(win)}"
    else:
        text = f"❌ {match}\nРезультат: {result}"
    save(uid, p)
    await call.message.edit_text(text)

@dp.message(Command("stocks"))
async def stocks(message: Message):
    p = load(message.from_user.id)
    if not p:
        return await message.answer("❌")
    stocks = p.get("stocks", [])
    if stocks:
        total = sum(s.get("price", 0) for s in stocks)
        return await message.answer(f"📈\n{'\n'.join([f\"{s['name']} — {money(s['price'])}\" for s in stocks])}\n💰 {money(total)}")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{s['name']} — {money(s['price'])}", callback_data=f"stock:buy:{s['name']}:{s['price']}")] for s in STOCKS
    ])
    await message.answer(f"📈 {money(p['money'])}", reply_markup=keyboard)

@dp.callback_query(F.data.startswith("stock:"))
async def stock_cb(call: CallbackQuery):
    uid = call.from_user.id
    p = load(uid)
    if not p:
        return await call.answer("❌", show_alert=True)
    parts = call.data.split(":")
    name, price = parts[2], int(parts[3])
    if p["money"] < price:
        return await call.answer(f"❌ {money(price)}", show_alert=True)
    p["money"] -= price
    if "stocks" not in p:
        p["stocks"] = []
    p["stocks"].append({"name": name, "price": price})
    save(uid, p)
    await call.message.edit_text(f"✅ {name}")

@dp.callback_query(F.data.startswith("menu:"))
async def menu_cb(call: CallbackQuery):
    p = load(call.from_user.id)
    if not p:
        return await call.answer("❌", show_alert=True)
    action = call.data.split(":")[1]
    menus = {
        "profile": "👤 /profile",
        "game": "⚽ /train, /match, /rest",
        "stats": "📊 /stats, /trophies, /table",
        "career": "🔄 /transfers, /agent, /contract",
        "shop": "🛒 /shop, /cars, /house, /business",
        "social": "👤 /news, /family",
        "bonus": "⭐ /daily, /bonus, /tasks, /referral, /reminder",
        "casino": "🎰 /casino, /penalty",
        "achievements": "🏅 /achievements",
        "coach": "🧑‍🏫 /coach_profile, /team, /train_team, /match_team, /tactics, /coach_trophies, /coach_leaderboard, /staff, /coach_history",
    }
    await call.message.edit_text(menus.get(action, "❌"), reply_markup=main_menu_keyboard(p.get("is_coach", False)))

@dp.message(F.text.startswith("/"))
async def unknown(message: Message):
    await message.answer("❌ /help")

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
