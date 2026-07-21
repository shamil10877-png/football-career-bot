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


LEAGUES = {
    "АПЛ": ["Манчестер Сити", "Ливерпуль", "Челси", "Арсенал", "Тоттенхэм", "Манчестер Юнайтед", "Ньюкасл", "Астон Вилла", "Брайтон", "Вулверхэмптон"],
    "Ла Лига": ["Реал Мадрид", "Барселона", "Атлетико", "Севилья", "Вильярреал", "Реал Сосьедад", "Бетис", "Атлетик", "Валенсия", "Осасуна"],
    "Бундеслига": ["Бавария", "Боруссия Дортмунд", "Лейпциг", "Байер", "Фрайбург", "Айнтрахт", "Вольфсбург", "Менхенгладбах", "Штутгарт", "Хоффенхайм"],
    "Серия А": ["Ювентус", "Милан", "Интер", "Рома", "Наполи", "Лацио", "Аталанта", "Фиорентина", "Торино", "Болонья"],
    "Лига 1": ["ПСЖ", "Марсель", "Монако", "Лион", "Лилль", "Ренн", "Ницца", "Страсбург", "Ланс", "Нант"],
}

UCL_CLUBS = ["Реал Мадрид", "Барселона", "Манчестер Сити", "Бавария", "ПСЖ", "Ливерпуль", "Ювентус", "Атлетико"]


def get_league_for_club(club):
    for league, clubs in LEAGUES.items():
        if club in clubs:
            return league
    return "АПЛ"


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


def new_player(name, referrer=None):
    now = datetime.now()
    league = random.choice(list(LEAGUES.keys()))
    club = random.choice(LEAGUES[league])
    return {
        "created": True,
        "name": name,
        "club": club,
        "league": league,
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
        "money": 50000 + (REFERRED_BONUS if referrer else 0),
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
        "golden_boot": 0,
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
        "golden_boot_career": 0,
        "league_points": 0,
        "ucl_points": 0,
        "league_matches": 0,
        "ucl_matches": 0,
        "last_ucl_week": 0,
        "worldcup_year": 0,
        "euro_year": 0,
        "winter_transfer": False,
        "season_goals": 0,
        "season_assists": 0,
        "season_matches": 0,
        "best_rating": 60,
        "hospital_count": 0,
        "bonus_received": False,
        "referrer": referrer,
        "referrals": [],
        "achievements": [],
        "last_reminder": now.isoformat(),
        "daily_tasks": {"goals": 0, "matches": 0, "points": 0, "completed": False},
        "casino_total": 0,
    }


def check_achievements(p, user_id):
    unlocked = []
    achievements = p.get("achievements", [])

    if p["goals_career"] >= 1 and "first_goal" not in achievements:
        achievements.append("first_goal")
        p["money"] += ACHIEVEMENTS["first_goal"]["reward"]
        unlocked.append("🥇 Первый гол")

    if p.get("season_goals", 0) >= 3 and "hat_trick" not in achievements:
        achievements.append("hat_trick")
        p["money"] += ACHIEVEMENTS["hat_trick"]["reward"]
        unlocked.append("🎯 Хет-трик")

    if p["matches_career"] >= 100 and "100_matches" not in achievements:
        achievements.append("100_matches")
        p["money"] += ACHIEVEMENTS["100_matches"]["reward"]
        unlocked.append("🏃 100 матчей")

    if p["rating"] >= 80 and "rating_80" not in achievements:
        achievements.append("rating_80")
        p["money"] += ACHIEVEMENTS["rating_80"]["reward"]
        unlocked.append("⭐ Рейтинг 80")

    if p["rating"] >= 90 and "rating_90" not in achievements:
        achievements.append("rating_90")
        p["money"] += ACHIEVEMENTS["rating_90"]["reward"]
        unlocked.append("🌟 Рейтинг 90")

    if p["money"] >= 1000000 and "millionaire" not in achievements:
        achievements.append("millionaire")
        p["money"] += ACHIEVEMENTS["millionaire"]["reward"]
        unlocked.append("💰 Миллионер")

    if p["league_titles_career"] >= 1 and "champion" not in achievements:
        achievements.append("champion")
        p["money"] += ACHIEVEMENTS["champion"]["reward"]
        unlocked.append("🏆 Чемпион лиги")

    if p["ucl_career"] >= 1 and "ucl_winner" not in achievements:
        achievements.append("ucl_winner")
        p["money"] += ACHIEVEMENTS["ucl_winner"]["reward"]
        unlocked.append("⭐ Победитель ЛЧ")

    if p["golden_boot_career"] >= 1 and "golden_boot" not in achievements:
        achievements.append("golden_boot")
        p["money"] += ACHIEVEMENTS["golden_boot"]["reward"]
        unlocked.append("👟 Золотая бутса")

    if p["ballon_career"] >= 1 and "ballon_dor" not in achievements:
        achievements.append("ballon_dor")
        p["money"] += ACHIEVEMENTS["ballon_dor"]["reward"]
        unlocked.append("🏅 Золотой мяч")

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


@dp.message(Command("start"))
async def start(message: Message):
    args = message.text.split()
    referrer = args[1] if len(args) > 1 else None

    p = load(message.from_user.id)
    if p:
        await message.answer(
            f"👋 Добро пожаловать обратно, <b>{p['name']}</b>!\n\n"
            f"🏆 Лига: {p.get('league', 'АПЛ')}\n"
            f"📅 Неделя: {p.get('week', 1)}\n"
            f"🏆 Сезон: {p.get('season', 1)}\n\n"
            "Используй /help чтобы посмотреть команды."
        )
    else:
        await message.answer(
            "⚽ <b>Football Career</b>\n\n"
            "Создай карьеру:\n"
            "<code>/create Имя</code>\n\n"
            "Пример:\n"
            "<code>/create Alex</code>\n\n"
            "Если тебя пригласили, используй:\n"
            "<code>/create Имя @username</code>"
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
        "/cars — купить машину\n"
        "/house — купить/сдать дом\n"
        "/family — семья\n"
        "/business — бизнес\n"
        "/history — предыдущие карьеры\n"
        "/donate — поддержать бота\n"
        "/bonus — бонус за подписку\n"
        "/achievements — достижения\n"
        "/leaderboard — топ игроков\n"
        "/penalty — пенальти\n"
        "/casino — казино\n"
        "/tasks — ежедневные задания\n"
        "/referral — реферальная ссылка\n"
        "/reminder — напоминания\n"
        "/ping — проверка\n"
        "/myid — показать ID\n"
        "/give @username сумма — передать деньги"
    )


@dp.message(Command("ping"))
async def ping(message: Message):
    await message.answer("🏓 Pong! Бот работает!")


@dp.message(Command("myid"))
async def my_id(message: Message):
    await message.answer(f"🆔 Твой ID: <code>{message.from_user.id}</code>")


@dp.message(Command("bonus"))
async def bonus_cmd(message: Message):
    p = load(message.from_user.id)
    if not p:
        await message.answer("❌ Сначала создай карьеру через /create")
        return

    if p.get("bonus_received", False):
        await message.answer("❌ Ты уже получил бонус за подписку!")
        return

    try:
        member = await bot.get_chat_member(chat_id="@GoalTimeNews_bot", user_id=message.from_user.id)
        if member.status in ["member", "administrator", "creator"]:
            p["money"] += 50000
            p["bonus_received"] = True
            save(message.from_user.id, p)
            await message.answer(f"✅ <b>Бонус за подписку получен!</b>\n\n💰 +50,000 €\n💵 Твой баланс: {money(p['money'])}")
        else:
            await message.answer(f"📢 <b>Бонус за подписку!</b>\n\nПодпишись на наш канал и получи 50,000 €!\n\n👉 {CHANNEL_URL}\n\nПосле подписки нажми /bonus снова.")
    except:
        await message.answer(f"📢 <b>Бонус за подписку!</b>\n\nПодпишись на наш канал и получи 50,000 €!\n\n👉 {CHANNEL_URL}\n\nПосле подписки нажми /bonus снова.")


@dp.message(Command("achievements"))
async def achievements_cmd(message: Message):
    p = load(message.from_user.id)
    if not p:
        await message.answer("❌ Сначала создай карьеру через /create")
        return

    unlocked = p.get("achievements", [])
    if not unlocked:
        await message.answer("🏆 <b>Достижения</b>\n\nПока нет достижений. Играй и открывай новые!")
        return

    text = "🏆 <b>Твои достижения:</b>\n\n"
    for ach in unlocked:
        if ach in ACHIEVEMENTS:
            text += f"✅ {ACHIEVEMENTS[ach]['name']} — +{money(ACHIEVEMENTS[ach]['reward'])}\n"

    await message.answer(text)


@dp.message(Command("leaderboard"))
async def leaderboard(message: Message):
    players = get_all_players()
    if not players:
        await message.answer("📭 Нет зарегистрированных игроков")
        return

    sorted_players = sorted(players, key=lambda x: x.get("rating", 0), reverse=True)[:10]

    text = "🏆 <b>Топ-10 игроков</b>\n\n"
    medals = {0: "🥇", 1: "🥈", 2: "🥉"}

    for i, p in enumerate(sorted_players):
        medal = medals.get(i, f"{i+1}.")
        text += f"{medal} {p['name']} — ⭐{p['rating']} — 💰{money(p['money'])} — 🏟{p['club']}\n"

    await message.answer(text)


@dp.message(Command("penalty"))
async def penalty(message: Message):
    p = load(message.from_user.id)
    if not p:
        await message.answer("❌ Сначала создай карьеру!")
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Влево", callback_data="penalty:left"),
         InlineKeyboardButton(text="➡️ Вправо", callback_data="penalty:right")],
        [InlineKeyboardButton(text="⬆️ Вверх", callback_data="penalty:up"),
         InlineKeyboardButton(text="⬇️ Вниз", callback_data="penalty:down")]
    ])

    await message.answer("⚽ <b>Пенальти!</b>\n\nВыбери направление удара:", reply_markup=keyboard)


@dp.callback_query(F.data.startswith("penalty:"))
async def penalty_cb(call: CallbackQuery):
    uid = call.from_user.id
    p = load(uid)
    if not p:
        await call.answer("❌ Сначала создай карьеру!", show_alert=True)
        return

    user_choice = call.data.split(":")[1]
    bot_choice = random.choice(["left", "right", "up", "down"])

    if user_choice == bot_choice:
        reward = 10000
        p["money"] += reward
        save(uid, p)
        await call.message.edit_text(
            f"⚽ <b>Пенальти!</b>\n\n"
            f"Ты ударил: {user_choice}\n"
            f"Вратарь прыгнул: {bot_choice}\n\n"
            f"🥅 <b>ГОЛ!</b> 🎉\n"
            f"💰 +{money(reward)}"
        )
    else:
        await call.message.edit_text(
            f"⚽ <b>Пенальти!</b>\n\n"
            f"Ты ударил: {user_choice}\n"
            f"Вратарь прыгнул: {bot_choice}\n\n"
            f"❌ <b>МИМО!</b> Попробуй ещё раз."
        )


@dp.message(Command("casino"))
async def casino(message: Message):
    p = load(message.from_user.id)
    if not p:
        await message.answer("❌ Сначала создай карьеру!")
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎰 Слоты", callback_data="casino:slots")],
        [InlineKeyboardButton(text="🪙 Орёл/Решка", callback_data="casino:coin")],
        [InlineKeyboardButton(text="♠️ Рулетка", callback_data="casino:roulette")],
    ])

    await message.answer(
        f"🎰 <b>Казино</b>\n\n"
        f"💰 Твой баланс: {money(p['money'])}\n"
        f"🎯 Выбери игру:",
        reply_markup=keyboard
    )


@dp.callback_query(F.data.startswith("casino:slots"))
async def casino_slots(call: CallbackQuery):
    uid = call.from_user.id
    p = load(uid)
    if not p:
        await call.answer("❌ Сначала создай карьеру!", show_alert=True)
        return

    bet = 5000
    if p["money"] < bet:
        await call.answer("❌ Недостаточно денег!", show_alert=True)
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
    p["casino_total"] = p.get("casino_total", 0) + win - bet
    save(uid, p)

    await call.message.edit_text(
        f"🎰 <b>Слоты</b>\n\n"
        f"Результат: {' '.join(result)}\n"
        f"💰 Ставка: {money(bet)}\n"
        f"🏆 Выигрыш: {money(win)}\n"
        f"💵 Баланс: {money(p['money'])}"
    )


@dp.callback_query(F.data.startswith("casino:coin"))
async def casino_coin(call: CallbackQuery):
    uid = call.from_user.id
    p = load(uid)
    if not p:
        await call.answer("❌ Сначала создай карьеру!", show_alert=True)
        return

    bet = 10000
    if p["money"] < bet:
        await call.answer("❌ Недостаточно денег!", show_alert=True)
        return

    user_choice = "Орёл" if random.random() > 0.5 else "Решка"
    bot_choice = "Орёл" if random.random() > 0.5 else "Решка"

    win = bet if user_choice == bot_choice else 0

    p["money"] -= bet
    p["money"] += win
    p["casino_total"] = p.get("casino_total", 0) + win - bet
    save(uid, p)

    await call.message.edit_text(
        f"🪙 <b>Орёл/Решка</b>\n\n"
        f"Ты выбрал: {user_choice}\n"
        f"Выпало: {bot_choice}\n"
        f"💰 Ставка: {money(bet)}\n"
        f"🏆 Выигрыш: {money(win)}\n"
        f"💵 Баланс: {money(p['money'])}"
    )


@dp.callback_query(F.data.startswith("casino:roulette"))
async def casino_roulette(call: CallbackQuery):
    uid = call.from_user.id
    p = load(uid)
    if not p:
        await call.answer("❌ Сначала создай карьеру!", show_alert=True)
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔴 Красное", callback_data="roulette:red")],
        [InlineKeyboardButton(text="⚫ Чёрное", callback_data="roulette:black")],
        [InlineKeyboardButton(text="🟢 Зелёное", callback_data="roulette:green")],
    ])

    await call.message.edit_text(
        f"♠️ <b>Рулетка</b>\n\n"
        f"💰 Твой баланс: {money(p['money'])}\n"
        f"Ставка: 20,000 €\n\n"
        f"Выбери цвет:",
        reply_markup=keyboard
    )


@dp.callback_query(F.data.startswith("roulette:"))
async def roulette_cb(call: CallbackQuery):
    uid = call.from_user.id
    p = load(uid)
    if not p:
        await call.answer("❌ Сначала создай карьеру!", show_alert=True)
        return

    bet = 20000
    if p["money"] < bet:
        await call.answer("❌ Недостаточно денег!", show_alert=True)
        return

    user_choice = call.data.split(":")[1]
    colors = ["red", "black", "green"]
    weights = [0.48, 0.48, 0.04]
    bot_choice = random.choices(colors, weights=weights)[0]

    win = 0
    if user_choice == bot_choice:
        if bot_choice == "green":
            win = bet * 14
        else:
            win = bet * 2

    p["money"] -= bet
    p["money"] += win
    p["casino_total"] = p.get("casino_total", 0) + win - bet
    save(uid, p)

    colors_dict = {"red": "🔴 Красное", "black": "⚫ Чёрное", "green": "🟢 Зелёное"}

    await call.message.edit_text(
        f"♠️ <b>Рулетка</b>\n\n"
        f"Ты выбрал: {colors_dict[user_choice]}\n"
        f"Выпало: {colors_dict[bot_choice]}\n"
        f"💰 Ставка: {money(bet)}\n"
        f"🏆 Выигрыш: {money(win)}\n"
        f"💵 Баланс: {money(p['money'])}"
    )


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
        await message.answer("✅ <b>Ежедневные задания выполнены!</b>\n\nТы уже получил 50,000 € за сегодня. Возвращайся завтра!")
        return

    await message.answer(
        f"📋 <b>Ежедневные задания</b>\n\n"
        f"⚽ Забей {required['goals']} голов: {current.get('goals', 0)}/{required['goals']}\n"
        f"🎮 Сыграй {required['matches']} матчей: {current.get('matches', 0)}/{required['matches']}\n"
        f"📊 Набери {required['points']} очков в лиге: {current.get('points', 0)}/{required['points']}\n\n"
        f"🏆 Награда: 50,000 €"
    )


@dp.message(Command("referral"))
async def referral(message: Message):
    p = load(message.from_user.id)
    if not p:
        await message.answer("❌ Сначала создай карьеру через /create")
        return

    refs = p.get("referrals", [])
    text = f"🔗 <b>Реферальная система</b>\n\n"
    text += f"📋 Твоя ссылка: <code>https://t.me/GoalTimeNews_bot?start={message.from_user.id}</code>\n\n"
    text += f"👥 Приглашённых: {len(refs)}\n"
    if refs:
        text += f"📋 Список: {', '.join(refs[:5])}\n"

    await message.answer(text)


@dp.message(Command("reminder"))
async def reminder(message: Message):
    p = load(message.from_user.id)
    if not p:
        await message.answer("❌ Сначала создай карьеру! ")
        return

    now = datetime.now()
    last = datetime.fromisoformat(p.get("last_reminder", now.isoformat()))

    if (now - last).days >= 1:
        p["money"] += 10000
        p["last_reminder"] = now.isoformat()
        save(message.from_user.id, p)
        await message.answer("⏰ <b>Напоминание!</b>\n\nТы зашёл в игру! +10,000 € за активность! 🎉")
    else:
        await message.answer("⏰ <b>Напоминание</b>\n\nТы уже получал бонус сегодня. Возвращайся завтра!")


@dp.message(Command("create"))
async def create(message: Message):
    args = message.text.split()
    if len(args) < 2:
        await message.answer("❌ Используй: /create Имя")
        return

    name = args[1]
    referrer = args[2] if len(args) > 2 else None

    if referrer:
        ref_user = load(int(referrer))
        if ref_user:
            ref_user["money"] += REFERRAL_BONUS
            ref_user["referrals"].append(name)
            save(int(referrer), ref_user)

    player = new_player(name, referrer)
    save(message.from_user.id, player)

    await message.answer(
        f"✅ Карьера создана!\n\n"
        f"👤 Игрок: <b>{name}</b>\n"
        f"⭐ Рейтинг: 60\n"
        f"🏟 Клуб: {player['club']}\n"
        f"🏆 Лига: {player['league']}\n"
        f"{'💰 +50,000 € за рефералку!' if referrer else ''}"
    )


@dp.message(Command("profile"))
async def profile(message: Message):
    p = load(message.from_user.id)
    if not p:
        await message.answer("❌ Сначала создай карьеру: /create")
        return

    await message.answer(
        f"👤 <b>{p['name']}</b>\n"
        f"⭐ Рейтинг: {p['rating']}\n"
        f"🏟 Клуб: {p['club']}\n"
        f"🏆 Лига: {p.get('league', 'АПЛ')}\n"
        f"🎂 Возраст: {p['age']}\n"
        f"💰 Деньги: {money(p['money'])}\n"
        f"💵 Зарплата: {money(p['salary'])}/нед\n"
        f"📈 Стоимость: {money(p['market_value'])}\n"
        f"⚽ Матчи: {p['matches']}\n"
        f"🥅 Голы: {p['goals']}\n"
        f"🎯 Ассисты: {p['assists']}\n"
        f"🏅 MVP: {p['mvps']}\n"
        f"👥 Подписчики: {p['followers']}\n"
        f"🏠 Дом: {p.get('house', 'Нет')}\n"
        f"🚗 Машина: {p.get('car', 'Нет')}"
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
        f"🏋️ Тренировка завершена!\n\n"
        f"⬆️ +{plus} к {stat_names[stat]}\n"
        f"⭐ Рейтинг: {p['rating']}\n"
        f"⚡ Форма: {p['fitness']}%"
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

    goals = random.randint(0, max(1, p["rating"] // 35))
    assists = random.randint(0, max(1, p["rating"] // 45))
    mvp = random.randint(1, 100) <= p["rating"] - 40

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

    p["matches"] += 1
    p["goals"] += goals
    p["assists"] += assists
    p["season_goals"] = p.get("season_goals", 0) + goals
    p["season_assists"] = p.get("season_assists", 0) + assists
    p["season_matches"] = p.get("season_matches", 0) + 1
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

    # Обновление ежедневных заданий
    tasks = p.get("daily_tasks", {})
    if not tasks.get("completed", False):
        if "required" not in tasks:
            tasks["required"] = {"goals": random.randint(2,5), "matches": random.randint(3,7), "points": random.randint(10,20)}
        tasks["current"] = tasks.get("current", {"goals": 0, "matches": 0, "points": 0})
        tasks["current"]["goals"] += goals
        tasks["current"]["matches"] += 1
        tasks["current"]["points"] += points
        p["daily_tasks"] = tasks
        check_daily_tasks(p, message.from_user.id)

    # Достижения
    unlocked = check_achievements(p, message.from_user.id)

    # Зимнее трансферное окно
    winter_text = ""
    if p["week"] == 19 and not p.get("winter_transfer", False):
        p["winter_transfer"] = True
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Перейти в другой клуб", callback_data="winter:yes")],
            [InlineKeyboardButton(text="❌ Остаться", callback_data="winter:no")],
        ])
        winter_text = "\n\n❄️ <b>Зимнее трансферное окно!</b>\nХочешь перейти в другой клуб?"

    # Лига чемпионов
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
        p["season_goals"] = p.get("season_goals", 0) + ucl_goals

        if ucl_mvp:
            p["mvps"] += 1
            p["mvps_career"] += 1

        p["last_ucl_week"] = p["week"]

        ucl_reward = ucl_goals * 10000 + ucl_assists * 6000 + (20000 if ucl_mvp else 0)
        p["money"] += ucl_reward

        ucl_text = f"\n\n⭐ <b>Лига чемпионов!</b>\n⚽ Голы: {ucl_goals}\n🎯 Ассисты: {ucl_assists}\n📊 Результат: {ucl_result}\n📊 Очков: +{ucl_points}\n💰 Бонус: {money(ucl_reward)}"

    # ЧМ
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
        p["season_goals"] = p.get("season_goals", 0) + wc_goals

        if wc_win:
            p["worldcup"] += 1
            p["worldcup_career"] += 1
            p["trophies"].append("🌍 Чемпионат мира")
            p["followers"] += 15000
            p["money"] += 100000

        wc_text = f"\n\n🌍 <b>Чемпионат мира!</b>\n⚽ Голы: {wc_goals}\n🎯 Ассисты: {wc_assists}\n🏆 {'Победа! 🏆' if wc_win else 'Поражение'}"

    # Евро
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
        p["season_goals"] = p.get("season_goals", 0) + euro_goals

        if euro_win:
            p["trophies"].append("🏆 Евро")
            p["followers"] += 10000
            p["money"] += 80000

        euro_text = f"\n\n🏆 <b>Евро!</b>\n⚽ Голы: {euro_goals}\n🎯 Ассисты: {euro_assists}\n🏆 {'Победа! 🏆' if euro_win else 'Поражение'}"

    # Завершение сезона
    season_text = ""
    if p["league_matches"] >= 38:
        season_goals = p.get("season_goals", 0)
        season_assists = p.get("season_assists", 0)

        if season_goals >= 20:
            p["golden_boot"] += 1
            p["golden_boot_career"] += 1
            p["trophies"].append("👟 Золотая бутса")
            p["money"] += 300000
            p["followers"] += 8000

        if p["rating"] >= 85 and season_goals + season_assists >= 25:
            p["ballon"] += 1
            p["ballon_career"] += 1
            p["trophies"].append("🏅 Золотой мяч")
            p["money"] += 500000
            p["followers"] += 15000

        season_bonus = 0
        if p["league_points"] >= 80:
            season_bonus += 3
            p["league_titles"] += 1
            p["league_titles_career"] += 1
            p["trophies"].append("🏆 Чемпионат")
            p["followers"] += 5000
        elif p["league_points"] >= 60:
            season_bonus += 1

        if p.get("ucl_points", 0) >= 15:
            season_bonus += 2
            p["ucl"] += 1
            p["ucl_career"] += 1
            p["trophies"].append("⭐ Лига чемпионов")
            p["followers"] += 10000

        p["rating"] = min(99, p["rating"] + season_bonus)

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
        p["season_goals"] = 0
        p["season_assists"] = 0
        p["season_matches"] = 0
        p["winter_transfer"] = False

        if p["age"] < 30:
            p["rating"] = min(99, p["rating"] + random.uniform(1, 3))

        p["salary"] = int(p["rating"] * 5000)
        p["market_value"] = int(p["rating"] * 150000)
        p["money"] += p["salary"] * 52

        if p["age"] >= 41:
            p["retired"] = True
            save(message.from_user.id, p)
            await message.answer(f"🔚 <b>Ты завершил карьеру в возрасте {p['age']} лет!</b>\n\n⭐ Итоговый рейтинг: {p['rating']}\n⚽ Голов: {p['goals_career']}\n🎯 Ассистов: {p['assists_career']}")
            return

        season_text = f"\n\n📅 <b>Сезон завершён!</b>\n⭐ Бонус к рейтингу: +{season_bonus}\n📈 Новый рейтинг: {p['rating']}"

    save(message.from_user.id, p)

    result_text = "🏆 Победа!" if result == "win" else "🤝 Ничья" if result == "draw" else "❌ Поражение"
    unlocked_text = f"\n\n🏆 <b>Новые достижения!</b>\n{' '.join(unlocked)}" if unlocked else ""

    await message.answer(
        f"🏟 Матч окончен!\n\n"
        f"📊 Результат: {result_text} (+{points} очков)\n"
        f"⚽ Голы: {goals}\n"
        f"🎯 Ассисты: {assists}\n"
        f"⭐ MVP: {'Да' if mvp else 'Нет'}\n"
        f"📈 Рейтинг: {p['rating']}\n"
        f"💰 Получено: {money(reward)}\n"
        f"⚡ Форма: {p['fitness']}%\n"
        f"👥 +{followers_gain} подписчиков\n"
        f"📊 Очков в лиге: {p.get('league_points', 0)}\n"
        f"📊 Матчей в лиге: {p.get('league_matches', 0)}/38"
        f"{ucl_text}{wc_text}{euro_text}{winter_text}{season_text}{unlocked_text}"
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
        f"😴 Отдых завершён!\n\n"
        f"⚡ Форма: {p['fitness']}%\n"
        f"😊 Мораль: {p['morale']}%\n"
        f"{recovery_msg}"
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
        f"✈️ <b>Трансферные предложения</b>\n\n"
        f"Текущий клуб: {p['club']}\n"
        f"⭐ Рейтинг: {p['rating']}\n\n"
        f"Выбери новый клуб:",
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
    p["league"] = get_league_for_club(club)
    p["salary"] = salary
    p["club_history"].append(old_club)

    save(uid, p)

    await call.message.edit_text(
        f"✅ <b>Трансфер совершён!</b>\n\n"
        f"Ты покинул <b>{old_club}</b>\n"
        f"и перешёл в <b>{club}</b>!\n\n"
        f"🏆 Новая лига: {p['league']}\n"
        f"💵 Новая зарплата: {money(salary)}/нед"
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
            f"🧑‍💼 <b>Твой агент</b>\n\n"
            f"🧑‍💼 Агент: {current}\n"
            f"💰 Деньги: {money(p['money'])}\n\n"
            f"Хочешь сменить агента? Выбери нового:",
            reply_markup=keyboard
        )
        return

    await message.answer(
        f"🧑‍💼 <b>Выбери агента</b>\n\n"
        f"💰 Деньги: {money(p['money'])}\n\n"
        f"Агент помогает с трансферами.",
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
        f"✅ Ты нанял <b>{name}</b>!\n\n"
        f"💰 Осталось: {money(p['money'])}"
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
        "recovery": {"name": "🧊 Восстановительный центр", "cost": 25000, "stat": "+15 к форме + лечение"},
        "nutrition": {"name": "🥗 Персональный диетолог", "cost": 15000, "stat": "+5 к форме каждую неделю"},
        "psychologist": {"name": "🧠 Спортивный психолог", "cost": 20000, "stat": "+10 к морали"},
    }

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"{item['name']} — {money(item['cost'])}",
            callback_data=f"shop:{key}"
        )] for key, item in items.items()
    ])

    await message.answer(
        f"🛒 <b>Магазин</b>\n\n"
        f"💰 Деньги: {money(p['money'])}\n\n"
        f"Выбери товар:",
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
        "recovery": {"name": "🧊 Восстановительный центр", "cost": 25000, "stat": "+15 к форме + лечение"},
        "nutrition": {"name": "🥗 Персональный диетолог", "cost": 15000, "stat": "+5 к форме каждую неделю"},
        "psychologist": {"name": "🧠 Спортивный психолог", "cost": 20000, "stat": "+10 к морали"},
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
    elif item_key == "recovery":
        p["fitness"] = min(100, p["fitness"] + 15)
        if p.get("injured"):
            p["injured"] = False
            p["injury_days"] = 0
    elif item_key == "nutrition":
        p["fitness"] = min(100, p["fitness"] + 5)
    elif item_key == "psychologist":
        p["morale"] = min(100, p["morale"] + 10)

    save(uid, p)

    await call.message.edit_text(
        f"✅ <b>Покупка совершена!</b>\n\n"
        f"{item['name']}\n"
        f"💰 Осталось: {money(p['money'])}\n"
        f"{item['stat']}"
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
        f"🚗 <b>Автосалон</b>\n\n"
        f"💰 Деньги: {money(p['money'])}\n"
        f"🚘 Твоя машина: {p.get('car', 'Нет')}\n\n"
        f"Выбери машину:",
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
        f"🚗 <b>Покупка завершена!</b>\n\n"
        f"🚘 Машина: {car}\n"
        f"💰 Цена: {money(price)}\n"
        f"💵 Осталось: {money(p['money'])}"
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
            f"🏠 <b>Твой дом</b>\n\n"
            f"🏡 Дом: {p['house']}\n"
            f"💰 Доход от аренды: {money(p.get('rental_income', 0))}/нед\n\n"
            f"Используй /house чтобы сдать в аренду или посмотреть другие дома.",
            reply_markup=keyboard
        )
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{home} — {money(price)} (аренда {money(rent)}/нед)", callback_data=f"house:{home}:{price}:{rent}")]
        for home, price, rent in houses_list
    ])

    await message.answer(
        f"🏠 <b>Недвижимость</b>\n\n"
        f"💰 Деньги: {money(p['money'])}\n"
        f"🏠 Твой дом: {p.get('house', 'Нет')}\n\n"
        f"Выбери дом:",
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
        f"🏠 <b>Поздравляем!</b>\n\n"
        f"🏡 Ты купил: {home}\n"
        f"💰 Цена: {money(price)}\n"
        f"💵 Аренда: {money(rent)}/нед\n"
        f"💵 Осталось: {money(p['money'])}"
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
        p["money"] += rent * 4
        await call.answer(f"🏠 Сдано в аренду!\n💰 Получено: {money(rent * 4)}", show_alert=True)
        save(uid, p)
        await call.message.edit_text(
            f"🏠 <b>Дом сдан в аренду!</b>\n\n"
            f"🏡 Дом: {p['house']}\n"
            f"💰 Доход: {money(rent * 4)}\n"
            f"💵 Всего денег: {money(p['money'])}"
        )
    else:
        await call.answer("Этот дом не приносит дохода.", show_alert=True)


@dp.message(Command("business"))
async def business(message: Message):
    p = load(message.from_user.id)
    if not p:
        await message.answer("❌ Сначала создай карьеру.")
        return

    if p.get("business"):
        await message.answer(
            f"🏢 <b>Твой бизнес</b>\n\n"
            f"🏢 Тип: {p.get('business_type', 'Нет')}\n"
            f"💰 Доход: {money(p.get('business_income', 0))}/нед\n"
            f"💵 Всего денег: {money(p['money'])}"
        )
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏪 Магазин — 30,000", callback_data="business:small")],
        [InlineKeyboardButton(text="🛍️ Торговый центр — 200,000", callback_data="business:medium")],
        [InlineKeyboardButton(text="🏗️ Строительная компания — 500,000", callback_data="business:large")],
        [InlineKeyboardButton(text="🏥 Больница — 1,000,000", callback_data="business:hospital")],
    ])

    await message.answer(
        f"🏢 <b>Бизнес</b>\n\n"
        f"💰 Деньги: {money(p['money'])}\n\n"
        f"Выбери бизнес:",
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
        "hospital": ("🏥 Больница", 1000000, 100000),
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
        f"✅ <b>Бизнес открыт!</b>\n\n"
        f"🏢 {name}\n"
        f"💰 Доход: {money(income)}/нед"
    )


@dp.message(Command("stats"))
async def stats(message: Message):
    p = load(message.from_user.id)
    if not p:
        await message.answer("❌ Сначала создай карьеру.")
        return

    await message.answer(
        f"📊 <b>Статистика {p['name']}</b>\n\n"
        f"⚽ Голы: {p['goals']}\n"
        f"🎯 Ассисты: {p['assists']}\n"
        f"🎮 Матчей: {p['matches']}\n"
        f"⭐ MVP: {p['mvps']}\n"
        f"🏃 Скорость: {p['pace']}\n"
        f"🎯 Удар: {p['shooting']}\n"
        f"🔄 Пас: {p['passing']}\n"
        f"🌀 Дриблинг: {p['dribbling']}\n"
        f"🛡 Защита: {p['defending']}\n"
        f"💪 Физика: {p['physical']}\n"
        f"⚡ Форма: {p['fitness']}%\n"
        f"😊 Мораль: {p['morale']}%"
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
            matches = p.get("league_matches", 0)
        else:
            matches = random.randint(20, 38)
            pts = random.randint(20, 85)
            if matches < 38:
                pts = int(pts * (matches / 38))
        table_data.append((club, pts, matches))

    sorted_table = sorted(table_data, key=lambda x: x[1], reverse=True)

    lines = [f"🏆 <b>{league}</b>\n"]
    medals = {0: "🥇", 1: "🥈", 2: "🥉"}

    for i, (club, pts, matches) in enumerate(sorted_table[:10]):
        medal = medals.get(i, f"{i+1}.")
        mark = " ← ты" if club == p["club"] else ""
        lines.append(f"{medal} {club} — {pts} очков ({matches} матчей){mark}")

    await message.answer("\n".join(lines))


@dp.message(Command("ucl"))
async def ucl(message: Message):
    p = load(message.from_user.id)
    if not p:
        await message.answer("❌ Сначала создай карьеру.")
        return

    clubs = UCL_CLUBS.copy()
    random.shuffle(clubs)

    lines = ["⭐ <b>Лига чемпионов</b>\n\n🏆 <b>Плей-офф</b>\n"]

    for i in range(0, len(clubs), 2):
        if i + 1 < len(clubs):
            lines.append(f"⚔️ {clubs[i]} vs {clubs[i+1]}")

    await message.answer("\n".join(lines))


@dp.message(Command("trophies"))
async def trophies(message: Message):
    p = load(message.from_user.id)
    if not p:
        await message.answer("❌ Сначала создай карьеру.")
        return

    trophies_list = "\n".join(p.get("trophies", [])) if p.get("trophies") else "Пока нет трофеев 🏆"

    await message.answer(f"🏆 <b>Трофеи</b>\n\n{trophies_list}")


@dp.message(Command("contract"))
async def contract(message: Message):
    p = load(message.from_user.id)
    if not p:
        await message.answer("❌ Сначала создай карьеру.")
        return

    await message.answer(
        f"📄 <b>Контракт</b>\n\n"
        f"🏟 Клуб: {p['club']}\n"
        f"🏆 Лига: {p.get('league', 'АПЛ')}\n"
        f"💰 Зарплата: {money(p['salary'])}/нед\n"
        f"📈 Стоимость: {money(p['market_value'])}\n"
        f"💵 Денег: {money(p['money'])}\n"
        f"🧑‍💼 Агент: {p.get('agent', 'Нет')}"
    )


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
            f"👶 Поздравляем!\n\n"
            f"У вас с {p['wife']} родился ребёнок!\n"
            f"👨‍👩‍👧 Детей: {p['children']}\n\n"
            f"💡 Попробуй ещё через месяц."
        )
    else:
        await message.answer(
            f"👨‍👩‍👧 <b>Семья</b>\n\n"
            f"❤️ Жена: {p['wife']}\n"
            f"👶 Детей: {p['children']}\n"
            f"📅 Вместе: {p['relationship_days']} дней\n\n"
            f"💡 Дети появятся через некоторое время."
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
        text += f"{i}. 👤 {career['name']}\n   ⭐ Рейтинг: {career['rating']}\n   ⚽ Голов: {career['goals']}\n   🎯 Ассистов: {career['assists']}\n   🏆 Трофеев: {len(career['trophies'])}\n   🎂 Возраст: {career['age']}\n   📅 Сезонов: {career['season']}\n\n"

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

    await message.answer(f"✅ Ты перевёл {money(amount)} игроку <b>{username}</b>\n💰 У тебя осталось: {money(p['money'])}")


@dp.message(Command("addmoney"))
async def add_money(message: Message):
    if message.from_user.id != OWNER_ID:
        await message.answer("❌ У тебя нет прав!")
        return

    args = message.text.split()
    if len(args) < 3:
        await message.answer("❌ Используй: /addmoney @username сумма")
        return

    username = args[1].replace("@", "")
    amount = int(args[2])

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
                await message.answer(f"✅ Игроку <b>{username}</b> добавлено {money(amount)}")
                break

    if not found:
        await message.answer(f"❌ Игрок {username} не найден")


@dp.message(Command("setmoney"))
async def set_money(message: Message):
    if message.from_user.id != OWNER_ID:
        await message.answer("❌ У тебя нет прав!")
        return

    args = message.text.split()
    if len(args) < 3:
        await message.answer("❌ Используй: /setmoney @username сумма")
        return

    username = args[1].replace("@", "")
    amount = int(args[2])

    found = False
    for file in os.listdir(SAVE_DIR):
        if file.endswith(".json"):
            with open(os.path.join(SAVE_DIR, file), "r", encoding="utf-8") as f:
                data = json.load(f)
            if data.get("name", "").lower() == username.lower():
                data["money"] = amount
                with open(os.path.join(SAVE_DIR, file), "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                found = True
                await message.answer(f"✅ У игрока <b>{username}</b> теперь {money(amount)}")
                break

    if not found:
        await message.answer(f"❌ Игрок {username} не найден")


@dp.message(Command("allplayers"))
async def all_players(message: Message):
    if message.from_user.id != OWNER_ID:
        await message.answer("❌ У тебя нет прав!")
        return

    players = []
    for file in os.listdir(SAVE_DIR):
        if file.endswith(".json"):
            with open(os.path.join(SAVE_DIR, file), "r", encoding="utf-8") as f:
                data = json.load(f)
            if data.get("created"):
                players.append(f"👤 {data['name']} — ⭐{data['rating']} — 💰{money(data['money'])} — 🏟{data['club']}")

    if not players:
        await message.answer("📭 Нет зарегистрированных игроков")
        return

    await message.answer("📋 <b>Все игроки:</b>\n\n" + "\n".join(players[:20]))


@dp.message(Command("donate"))
async def donate_cmd(message: Message):
    await message.answer(
        "⭐ <b>Поддержать бота</b>\n\n"
        "Отправь Telegram Stars, чтобы получить бонус в игре!\n\n"
        "💰 5 ⭐ → 50,000 €\n"
        "💰 10 ⭐ → 120,000 €\n"
        "💰 25 ⭐ → 350,000 €\n"
        "💰 50 ⭐ → 800,000 €\n"
        "💰 100 ⭐ → 2,000,000 €\n\n"
        "Все донаты идут на развитие бота! ❤️",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⭐ 5 звёзд", callback_data="donate:5")],
            [InlineKeyboardButton(text="⭐ 10 звёзд", callback_data="donate:10")],
            [InlineKeyboardButton(text="⭐ 25 звёзд", callback_data="donate:25")],
            [InlineKeyboardButton(text="⭐ 50 звёзд", callback_data="donate:50")],
            [InlineKeyboardButton(text="⭐ 100 звёзд", callback_data="donate:100")],
        ])
    )


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
    print("🌐 Web-сервер запущен на порту 8080")


async def main():
    print("🚀 Бот запущен!")
    asyncio.create_task(start_web())
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
