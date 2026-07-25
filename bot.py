import asyncio
import random
import aiosqlite
from datetime import datetime
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.enums import ParseMode

# ===================== CONFIG =====================
BOT_TOKEN = "8849485512:AAEhvLOhm7rLwmXoalUx1Wnp5QKCSbFw7O4"
DB_PATH = "football_manager.db"
MAX_ENERGY = 100

POSITIONS = {
    "GK": {"name": "🧤 Вратарь", "main": "goalkeeping"},
    "DEF": {"name": "🛡 Защитник", "main": "defense"},
    "MID": {"name": "⚡ Полузащитник", "main": "passing"},
    "FWD": {"name": "🔥 Нападающий", "main": "shooting"},
}

SKILLS = {
    "speed": "⚡ Скорость", "shooting": "🎯 Удар", "passing": "🎨 Пас",
    "defense": "🛡 Защита", "physical": "💪 Физика", "goalkeeping": "🧤 Вратарь",
}

CLUBS = {
    1: [{"name": "⚪ FC Grassroots", "salary": 500, "bonus": 200, "req_rating": 0},
        {"name": "🔵 Blue Collar FC", "salary": 600, "bonus": 250, "req_rating": 0},
        {"name": "🟢 Green Valley", "salary": 550, "bonus": 220, "req_rating": 0}],
    2: [{"name": "🟡 Golden Lions", "salary": 2000, "bonus": 800, "req_rating": 68},
        {"name": "🔴 Red Devils II", "salary": 2500, "bonus": 1000, "req_rating": 70},
        {"name": "⚫ Iron Warriors", "salary": 2200, "bonus": 900, "req_rating": 69}],
    3: [{"name": "🌟 Star City FC", "salary": 8000, "bonus": 3000, "req_rating": 78},
        {"name": "🏆 Royal FC", "salary": 10000, "bonus": 4000, "req_rating": 82},
        {"name": "💎 Diamond United", "salary": 12000, "bonus": 5000, "req_rating": 85}],
    4: [{"name": "👑 Legend FC", "salary": 50000, "bonus": 20000, "req_rating": 90},
        {"name": "🔱 Titan SC", "salary": 60000, "bonus": 25000, "req_rating": 92},
        {"name": "🌍 World XI", "salary": 80000, "bonus": 35000, "req_rating": 95}],
}

# ===================== DATABASE =====================
async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""CREATE TABLE IF NOT EXISTS players (
            user_id INTEGER PRIMARY KEY, name TEXT, position TEXT, age INTEGER DEFAULT 17,
            rating INTEGER DEFAULT 65, energy INTEGER DEFAULT 100, money INTEGER DEFAULT 5000,
            club TEXT DEFAULT "Без клуба", club_level INTEGER DEFAULT 1, salary INTEGER DEFAULT 0,
            matches_played INTEGER DEFAULT 0, goals INTEGER DEFAULT 0, assists INTEGER DEFAULT 0,
            wins INTEGER DEFAULT 0, draws INTEGER DEFAULT 0, losses INTEGER DEFAULT 0,
            season INTEGER DEFAULT 1, speed INTEGER DEFAULT 50, shooting INTEGER DEFAULT 50,
            passing INTEGER DEFAULT 50, defense INTEGER DEFAULT 50, physical INTEGER DEFAULT 50,
            goalkeeping INTEGER DEFAULT 50, created_at TEXT, last_training TEXT, last_match TEXT)""")
        await db.execute("""CREATE TABLE IF NOT EXISTS match_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, opponent TEXT, result TEXT,
            score TEXT, goals INTEGER, assists INTEGER, rating_change INTEGER,
            money_earned INTEGER, date TEXT)""")
        await db.execute("""CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, achievement TEXT, date TEXT)""")
        await db.execute("""CREATE TABLE IF NOT EXISTS scheduler_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT, job_name TEXT, ran_at TEXT)""")
        await db.commit()

async def get_player(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM players WHERE user_id = ?", (user_id,)) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None

async def get_all_players():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM players") as cur:
            return [dict(r) for r in await cur.fetchall()]

async def create_player(user_id: int, name: str, position: str):
    now = datetime.now().isoformat()
    main_skill = POSITIONS[position]["main"]
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""INSERT INTO players (user_id, name, position, age, rating, energy, money,
            speed, shooting, passing, defense, physical, goalkeeping, created_at)
            VALUES (?, ?, ?, 17, 65, 100, 5000, 50, 50, 50, 50, 50, 50, ?)""", (user_id, name, position, now))
        await db.execute(f"UPDATE players SET {main_skill} = 55 WHERE user_id = ?", (user_id,))
        await db.commit()

async def update_player(user_id: int, **kwargs):
    async with aiosqlite.connect(DB_PATH) as db:
        for k, v in kwargs.items():
            await db.execute(f"UPDATE players SET {k} = ? WHERE user_id = ?", (v, user_id))
        await db.commit()

async def add_match_history(user_id, opponent, result, score, goals, assists, rating_change, money_earned):
    now = datetime.now().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""INSERT INTO match_history
            (user_id, opponent, result, score, goals, assists, rating_change, money_earned, date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, opponent, result, score, goals, assists, rating_change, money_earned, now))
        await db.commit()

async def get_match_history(user_id: int, limit: int = 10):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM match_history WHERE user_id = ? ORDER BY id DESC LIMIT ?", (user_id, limit)) as cur:
            return [dict(r) for r in await cur.fetchall()]

async def add_achievement(user_id: int, achievement: str):
    now = datetime.now().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO achievements (user_id, achievement, date) VALUES (?, ?, ?)", (user_id, achievement, now))
        await db.commit()

async def get_achievements(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM achievements WHERE user_id = ? ORDER BY id DESC", (user_id,)) as cur:
            return [dict(r) for r in await cur.fetchall()]

# ===================== KEYBOARDS =====================
def main_menu_kb():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="👤 Профиль"), KeyboardButton(text="📊 Статистика")],
        [KeyboardButton(text="⚽ Матч"), KeyboardButton(text="🏋️ Тренировка")],
        [KeyboardButton(text="🔄 Трансфер"), KeyboardButton(text="📜 История матчей")],
        [KeyboardButton(text="🏆 Достижения"), KeyboardButton(text="💤 Отдых")],
    ], resize_keyboard=True)

def position_kb():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🧤 Вратарь")], [KeyboardButton(text="🛡 Защитник")],
        [KeyboardButton(text="⚡ Полузащитник")], [KeyboardButton(text="🔥 Нападающий")],
    ], resize_keyboard=True, one_time_keyboard=True)

def training_kb():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="⚡ Скорость"), KeyboardButton(text="🎯 Удар")],
        [KeyboardButton(text="🎨 Пас"), KeyboardButton(text="🛡 Защита")],
        [KeyboardButton(text="💪 Физика"), KeyboardButton(text="🧤 Вратарь")],
        [KeyboardButton(text="⬅️ Назад")],
    ], resize_keyboard=True)

def confirm_kb():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="✅ Да"), KeyboardButton(text="❌ Нет")],
    ], resize_keyboard=True)

def transfer_clubs_kb(clubs: list):
    buttons = [[KeyboardButton(text=f"{c['name']} (💰{c['salary']}/мес)")] for c in clubs]
    buttons.append([KeyboardButton(text="⬅️ Назад")])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

# ===================== GAME LOGIC =====================
def calculate_overall(skills: dict) -> int:
    return min(99, max(1, sum(skills.values()) // 6))

def get_skill_key_by_name(name: str) -> str:
    mapping = {"⚡ Скорость": "speed", "🎯 Удар": "shooting", "🎨 Пас": "passing",
               "🛡 Защита": "defense", "💪 Физика": "physical", "🧤 Вратарь": "goalkeeping"}
    return mapping.get(name, "")

def simulate_match(player: dict) -> dict:
    rating, position, energy = player["rating"], player["position"], player["energy"]
    team_strength = rating * (energy / 100) * random.uniform(0.85, 1.15)
    opponent_strength = random.uniform(50, 95) * random.uniform(0.8, 1.2)
    if team_strength > opponent_strength + 15:
        result, our_goals, their_goals = "win", random.randint(2, 5), random.randint(0, 1)
    elif team_strength > opponent_strength:
        result, our_goals, their_goals = "win", random.randint(1, 3), random.randint(0, 2)
    elif abs(team_strength - opponent_strength) < 10:
        result, our_goals = "draw", random.randint(1, 2)
        their_goals = our_goals
    else:
        result, our_goals, their_goals = "loss", random.randint(0, 2), random.randint(2, 4)
    base_chance = rating / 100
    goals = assists = 0
    if position == "FWD":
        goals = random.choices([0,1,2,3], weights=[30,40,20,10])[0] if random.random() < base_chance else 0
        assists = random.choices([0,1,2], weights=[50,35,15])[0] if random.random() < base_chance*0.7 else 0
    elif position == "MID":
        goals = random.choices([0,1,2], weights=[60,30,10])[0] if random.random() < base_chance*0.6 else 0
        assists = random.choices([0,1,2], weights=[40,40,20])[0] if random.random() < base_chance*0.8 else 0
    elif position == "DEF":
        goals = random.choices([0,1], weights=[85,15])[0] if random.random() < base_chance*0.3 else 0
        assists = random.choices([0,1], weights=[70,30])[0] if random.random() < base_chance*0.5 else 0
    elif position == "GK":
        goals = 0
        assists = random.choices([0,1], weights=[90,10])[0]
    rating_change = 0
    if result == "win":
        rating_change = random.randint(1, 3)
        if goals > 0: rating_change += 1
        if position == "GK" and their_goals == 0: rating_change += 2
    elif result == "draw":
        rating_change = random.randint(-1, 1)
    else:
        rating_change = random.randint(-2, 0)
    base_earnings = 100 + rating * 2
    if result == "win": money_earned = base_earnings + player.get("salary", 0)//10 + random.randint(50, 200)
    elif result == "draw": money_earned = base_earnings//2 + random.randint(20, 100)
    else: money_earned = base_earnings//4 + random.randint(10, 50)
    energy_cost = random.randint(15, 30)
    opponent_name = random.choice(["Rival FC", "City United", "Sporting Lions", "Metro Stars",
                                    "Coastal FC", "Northern Wolves", "Eastern Eagles", "Western Bulls"])
    return {"result": result, "score": f"{our_goals}:{their_goals}", "opponent": opponent_name,
            "goals": goals, "assists": assists, "rating_change": rating_change,
            "money_earned": money_earned, "energy_cost": energy_cost}

def get_available_transfers(player: dict) -> list:
    rating, current_level = player["rating"], player.get("club_level", 1)
    available = []
    for level, clubs in CLUBS.items():
        if level <= current_level + 1:
            for club in clubs:
                if rating >= club["req_rating"] - 3:
                    available.append({**club, "level": level})
    return [c for c in available if c["name"] != player.get("club", "")][:5]

# ===================== FSM =====================
class CreatePlayer(StatesGroup):
    name = State()
    position = State()
    confirm = State()

class Training(StatesGroup):
    select_skill = State()

class Transfer(StatesGroup):
    select_club = State()
    confirm = State()

# ===================== HANDLERS =====================
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    player = await get_player(user_id)
    if player:
        await message.answer(f"👋 С возвращением, <b>{player['name']}</b>!\n\nТвой клуб: {player['club']}\nРейтинг: {player['rating']} | Энергия: {player['energy']}/100\n\nИспользуй меню ниже!", parse_mode=ParseMode.HTML, reply_markup=main_menu_kb())
    else:
        await message.answer("⚽ <b>Добро пожаловать в Football Career Manager!</b>\n\nЗдесь ты создашь своего футболиста и пройдёшь путь от юниора до легенды!\n\nДавай начнём. Как зовут твоего игрока?", parse_mode=ParseMode.HTML)
        await state.set_state(CreatePlayer.name)

@dp.message(CreatePlayer.name)
async def process_name(message: types.Message, state: FSMContext):
    name = message.text.strip()
    if len(name) < 2 or len(name) > 30:
        await message.answer("❌ Имя должно быть от 2 до 30 символов. Попробуй ещё раз:")
        return
    await state.update_data(name=name)
    await message.answer(f"Отлично, <b>{name}</b>! Теперь выбери позицию:", parse_mode=ParseMode.HTML, reply_markup=position_kb())
    await state.set_state(CreatePlayer.position)

@dp.message(CreatePlayer.position)
async def process_position(message: types.Message, state: FSMContext):
    pos_map = {"🧤 Вратарь": "GK", "🛡 Защитник": "DEF", "⚡ Полузащитник": "MID", "🔥 Нападающий": "FWD"}
    if message.text not in pos_map:
        await message.answer("❌ Выбери позицию из списка:", reply_markup=position_kb())
        return
    position = pos_map[message.text]
    await state.update_data(position=position)
    data = await state.get_data()
    pos_info = POSITIONS[position]
    await message.answer(f"📋 <b>Проверь данные:</b>\n\n👤 Имя: {data['name']}\n⚽ Позиция: {pos_info['name']}\n⭐ Главный навык: {SKILLS[pos_info['main']]} (+5 бонус)\n🎂 Возраст: 17 лет\n💰 Стартовый бюджет: 5,000$\n\nВсё верно?", parse_mode=ParseMode.HTML, reply_markup=confirm_kb())
    await state.set_state(CreatePlayer.confirm)

@dp.message(CreatePlayer.confirm)
async def process_confirm(message: types.Message, state: FSMContext):
    if message.text == "✅ Да":
        data = await state.get_data()
        user_id = message.from_user.id
        await create_player(user_id, data["name"], data["position"])
        start_club = CLUBS[1][0]
        await update_player(user_id, club=start_club["name"], club_level=1, salary=start_club["salary"])
        await message.answer(f"🎉 <b>Игрок создан!</b>\n\nТы подписал контракт с <b>{start_club['name']}</b>!\nЗарплата: {start_club['salary']}$/месяц\n\nТвоя карьера начинается! Удачи на поле! ⚽", parse_mode=ParseMode.HTML, reply_markup=main_menu_kb())
        await state.clear()
    elif message.text == "❌ Нет":
        await message.answer("Хорошо, давай заново. Как зовут твоего игрока?", reply_markup=ReplyKeyboardRemove())
        await state.set_state(CreatePlayer.name)
    else:
        await message.answer("Выбери Да или Нет:", reply_markup=confirm_kb())

@dp.message(F.text == "👤 Профиль")
async def show_profile(message: types.Message):
    user_id = message.from_user.id
    player = await get_player(user_id)
    if not player: return await message.answer("Сначала создай игрока: /start")
    pos_name = POSITIONS.get(player["position"], {}).get("name", player["position"])
    text = (f"👤 <b>{player['name']}</b> | {pos_name}\n"
            f"------------------------------\n"
            f"🏟 Клуб: <b>{player['club']}</b>\n"
            f"⭐ Рейтинг: <b>{player['rating']}</b>/99\n"
            f"🎂 Возраст: <b>{player['age']}</b> лет | Сезон: <b>{player['season']}</b>\n"
            f"⚡ Энергия: <b>{player['energy']}</b>/100\n"
            f"💰 Баланс: <b>{player['money']:,}</b>$ | Зарплата: <b>{player['salary']:,}</b>$/мес\n"
            f"------------------------------\n"
            f"📊 <b>Навыки:</b>\n"
            f"  ⚡ Скорость: {player['speed']}\n"
            f"  🎯 Удар: {player['shooting']}\n"
            f"  🎨 Пас: {player['passing']}\n"
            f"  🛡 Защита: {player['defense']}\n"
            f"  💪 Физика: {player['physical']}\n"
            f"  🧤 Вратарь: {player['goalkeeping']}\n")
    await message.answer(text, parse_mode=ParseMode.HTML)

@dp.message(F.text == "📊 Статистика")
async def show_stats(message: types.Message):
    user_id = message.from_user.id
    player = await get_player(user_id)
    if not player: return await message.answer("Сначала создай игрока: /start")
    total = player["wins"] + player["draws"] + player["losses"]
    winrate = (player["wins"] / total * 100) if total > 0 else 0
    text = (f"📊 <b>Карьерная статистика {player['name']}</b>\n"
            f"------------------------------\n"
            f"⚽ Матчей: <b>{total}</b> | ✅ Побед: <b>{player['wins']}</b> | 🤝 Ничьих: <b>{player['draws']}</b> | ❌ Поражений: <b>{player['losses']}</b>\n"
            f"📈 Винрейт: <b>{winrate:.1f}%</b>\n"
            f"------------------------------\n"
            f"⚽ Голов: <b>{player['goals']}</b> | 🎯 Пасов: <b>{player['assists']}</b>\n"
            f"💰 Баланс: <b>{player['money']:,}</b>$\n")
    await message.answer(text, parse_mode=ParseMode.HTML)

@dp.message(F.text == "🏋️ Тренировка")
async def start_training(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    player = await get_player(user_id)
    if not player: return await message.answer("Сначала создай игрока: /start")
    if player["energy"] < 20:
        return await message.answer(f"😴 <b>Мало энергии!</b>\n\nТекущая: {player['energy']}/100\nОтдохни.", parse_mode=ParseMode.HTML)
    await message.answer(f"🏋️ <b>Тренировка</b>\n\nВыбери навык (стоимость: 20 энергии):\n\n⚡ Скорость: {player['speed']}\n🎯 Удар: {player['shooting']}\n🎨 Пас: {player['passing']}\n🛡 Защита: {player['defense']}\n💪 Физика: {player['physical']}\n🧤 Вратарь: {player['goalkeeping']}", parse_mode=ParseMode.HTML, reply_markup=training_kb())
    await state.set_state(Training.select_skill)

@dp.message(Training.select_skill)
async def process_training(message: types.Message, state: FSMContext):
    if message.text == "⬅️ Назад": await message.answer("Главное меню:", reply_markup=main_menu_kb()); await state.clear(); return
    skill_key = get_skill_key_by_name(message.text)
    if not skill_key: return await message.answer("❌ Выбери навык:", reply_markup=training_kb())
    user_id = message.from_user.id
    player = await get_player(user_id)
    if player["energy"] < 20: await message.answer("😴 Недостаточно энергии!", reply_markup=main_menu_kb()); await state.clear(); return
    current = player[skill_key]
    if current >= 99: await message.answer(f"🏆 Максимум! {message.text} уже 99.", reply_markup=main_menu_kb()); await state.clear(); return
    gain = random.randint(2, 4) if current < 70 else (random.randint(1, 3) if current < 85 else random.randint(0, 2))
    gain = min(gain, 99 - current)
    new_value = current + gain
    new_energy = player["energy"] - 20
    skills = {"speed": player["speed"], "shooting": player["shooting"], "passing": player["passing"],
              "defense": player["defense"], "physical": player["physical"], "goalkeeping": player["goalkeeping"]}
    skills[skill_key] = new_value
    new_rating = calculate_overall(skills)
    await update_player(user_id, **{skill_key: new_value, "energy": new_energy, "rating": new_rating})
    if player["matches_played"] == 0 and player.get("last_training") is None:
        await add_achievement(user_id, "🌱 Первые шаги — первая тренировка")
    await update_player(user_id, last_training=datetime.now().isoformat())
    await message.answer(f"🏋️ <b>Тренировка завершена!</b>\n\n{message.text}: <b>{current}</b> → <b>{new_value}</b> (+{gain})\n⭐ Рейтинг: {player['rating']} → <b>{new_rating}</b>\n⚡ Энергия: {player['energy']} → <b>{new_energy}</b>", parse_mode=ParseMode.HTML, reply_markup=main_menu_kb())
    await state.clear()

@dp.message(F.text == "⚽ Матч")
async def play_match(message: types.Message):
    user_id = message.from_user.id
    player = await get_player(user_id)
    if not player: return await message.answer("Сначала создай игрока: /start")
    if player["energy"] < 15:
        return await message.answer(f"😴 <b>Мало энергии для матча!</b>\n\nТекущая: {player['energy']}/100\nОтдохни.", parse_mode=ParseMode.HTML)
    result = simulate_match(player)
    new_energy = max(0, player["energy"] - result["energy_cost"])
    new_money = player["money"] + result["money_earned"]
    new_goals = player["goals"] + result["goals"]
    new_assists = player["assists"] + result["assists"]
    new_rating = min(99, max(1, player["rating"] + result["rating_change"]))
    new_matches = player["matches_played"] + 1
    wins = player["wins"] + (1 if result["result"] == "win" else 0)
    draws = player["draws"] + (1 if result["result"] == "draw" else 0)
    losses = player["losses"] + (1 if result["result"] == "loss" else 0)
    await update_player(user_id, energy=new_energy, money=new_money, goals=new_goals, assists=new_assists,
                        rating=new_rating, matches_played=new_matches, wins=wins, draws=draws, losses=losses,
                        last_match=datetime.now().isoformat())
    await add_match_history(user_id, result["opponent"], result["result"], result["score"],
                            result["goals"], result["assists"], result["rating_change"], result["money_earned"])
    if new_matches == 1: await add_achievement(user_id, "⚽ Дебют — первый матч")
    if new_goals >= 10:
        achs = await get_achievements(user_id)
        if not any("10 голов" in a["achievement"] for a in achs): await add_achievement(user_id, "🔥 Снайпер — 10 голов")
    if new_rating >= 80:
        achs = await get_achievements(user_id)
        if not any("80+" in a["achievement"] for a in achs): await add_achievement(user_id, "⭐ Звезда — рейтинг 80+")
    emoji = "🎉" if result["result"] == "win" else ("🤝" if result["result"] == "draw" else "😔")
    res_text = "ПОБЕДА" if result["result"] == "win" else ("НИЧЬЯ" if result["result"] == "draw" else "ПОРАЖЕНИЕ")
    rc = result["rating_change"]
    text = (f"{emoji} <b>{res_text}!</b>\n\n"
            f"🏟 <b>{player['club']}</b> {result['score']} <b>{result['opponent']}</b>\n"
            f"------------------------------\n"
            f"⚽ Твои голы: <b>{result['goals']}</b>\n"
            f"🎯 Голевые передачи: <b>{result['assists']}</b>\n"
            f"------------------------------\n"
            f"⭐ Рейтинг: {player['rating']} → <b>{new_rating}</b> ({'+' if rc >= 0 else ''}{rc})\n"
            f"💰 Заработано: <b>+{result['money_earned']:,}</b>$\n"
            f"⚡ Энергия: {player['energy']} → <b>{new_energy}</b>\n")
    if new_matches % 10 == 0:
        new_season = player["season"] + 1
        new_age = player["age"] + 1
        age_bonus = 1 if new_age <= 25 else (-1 if new_age > 32 else 0)
        await update_player(user_id, season=new_season, age=new_age)
        if age_bonus != 0:
            skill = random.choice(list(SKILLS.keys()))
            old_val = player[skill]
            new_val = max(1, min(99, old_val + age_bonus))
            await update_player(user_id, **{skill: new_val})
        text += f"\n🎊 <b>КОНЕЦ СЕЗОНА {player['season']}!</b>\n🎂 Теперь тебе {new_age} лет\n"
        if age_bonus > 0: text += "📈 Возрастной бонус: +1 к навыку\n"
        elif age_bonus < 0: text += "📉 Возрастной штраф: -1 к навыку\n"
        text += "Новый сезон начался! 🏆"
    await message.answer(text, parse_mode=ParseMode.HTML, reply_markup=main_menu_kb())

@dp.message(F.text == "🔄 Трансфер")
async def start_transfer(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    player = await get_player(user_id)
    if not player: return await message.answer("Сначала создай игрока: /start")
    if player["matches_played"] < 5:
        return await message.answer(f"🚫 <b>Слишком рано!</b>\n\nСыграй минимум 5 матчей.\nПрогресс: {player['matches_played']}/5", parse_mode=ParseMode.HTML)
    clubs = get_available_transfers(player)
    if not clubs:
        return await message.answer("😕 <b>Пока нет предложений.</b>\n\nПрокачай рейтинг.", parse_mode=ParseMode.HTML)
    await state.update_data(clubs=clubs)
    text = f"🔄 <b>Трансферное окно</b>\n\nТекущий клуб: {player['club']}\nТвой рейтинг: {player['rating']}\n\nДоступные предложения:\n"
    for i, club in enumerate(clubs, 1):
        text += f"{i}. {club['name']} — Зарплата: {club['salary']:,}$/мес, Бонус: {club['bonus']:,}$\n"
    text += "\nВыбери клуб:"
    await message.answer(text, parse_mode=ParseMode.HTML, reply_markup=transfer_clubs_kb(clubs))
    await state.set_state(Transfer.select_club)

@dp.message(Transfer.select_club)
async def process_transfer_select(message: types.Message, state: FSMContext):
    if message.text == "⬅️ Назад": await message.answer("Главное меню:", reply_markup=main_menu_kb()); await state.clear(); return
    data = await state.get_data()
    clubs = data.get("clubs", [])
    selected = None
    for club in clubs:
        if club["name"] in message.text: selected = club; break
    if not selected: return await message.answer("❌ Выбери клуб:", reply_markup=transfer_clubs_kb(clubs))
    await state.update_data(selected_club=selected)
    await message.answer(f"📝 <b>Подтверди переход:</b>\n\nКлуб: {selected['name']}\nУровень: {selected['level']}\nЗарплата: {selected['salary']:,}$/мес\nБонус: {selected['bonus']:,}$\n\nПереходим?", parse_mode=ParseMode.HTML, reply_markup=confirm_kb())
    await state.set_state(Transfer.confirm)

@dp.message(Transfer.confirm)
async def process_transfer_confirm(message: types.Message, state: FSMContext):
    if message.text == "✅ Да":
        data = await state.get_data()
        club = data["selected_club"]
        user_id = message.from_user.id
        player = await get_player(user_id)
        new_money = player["money"] + club["bonus"]
        await update_player(user_id, club=club["name"], club_level=club["level"], salary=club["salary"], money=new_money, matches_played=0)
        if club["level"] >= 3: await add_achievement(user_id, f"🚀 Большой переход — {club['name']}")
        await message.answer(f"🎉 <b>Трансфер состоялся!</b>\n\nТы перешёл в <b>{club['name']}</b>!\n💰 Бонус: +{club['bonus']:,}$\n💵 Зарплата: {club['salary']:,}$/мес\n\nУдачи! ⚽", parse_mode=ParseMode.HTML, reply_markup=main_menu_kb())
        await state.clear()
    elif message.text == "❌ Нет": await message.answer("Трансфер отменён.", reply_markup=main_menu_kb()); await state.clear()
    else: await message.answer("Выбери Да или Нет:", reply_markup=confirm_kb())

@dp.message(F.text == "📜 История матчей")
async def show_history(message: types.Message):
    user_id = message.from_user.id
    history = await get_match_history(user_id, 10)
    if not history: return await message.answer("📭 Пока нет матчей.")
    text = "📜 <b>Последние матчи:</b>\n\n"
    for match in history:
        emoji = "🟢" if match["result"] == "win" else ("🟡" if match["result"] == "draw" else "🔴")
        rc = match["rating_change"]
        text += f"{emoji} {match['opponent']} {match['score']} | {'+' if rc >= 0 else ''}{rc}⭐ | +{match['money_earned']}$\n"
    await message.answer(text, parse_mode=ParseMode.HTML)

@dp.message(F.text == "🏆 Достижения")
async def show_achievements(message: types.Message):
    user_id = message.from_user.id
    achievements = await get_achievements(user_id)
    if not achievements: return await message.answer("🏆 <b>Достижения</b>\n\nПока нет. Играй и зарабатывай!")
    text = "🏆 <b>Твои достижения:</b>\n\n"
    for ach in achievements:
        date = ach["date"][:10] if ach["date"] else ""
        text += f"• {ach['achievement']} ({date})\n"
    await message.answer(text, parse_mode=ParseMode.HTML)

@dp.message(F.text == "💤 Отдых")
async def rest(message: types.Message):
    user_id = message.from_user.id
    player = await get_player(user_id)
    if not player: return await message.answer("Сначала создай игрока: /start")
    if player["energy"] >= MAX_ENERGY: return await message.answer("😎 Полная энергия! Время играть!")
    restore = random.randint(25, 45)
    new_energy = min(MAX_ENERGY, player["energy"] + restore)
    await update_player(user_id, energy=new_energy)
    await message.answer(f"💤 <b>Отдых завершён!</b>\n\n⚡ Энергия: {player['energy']} → <b>{new_energy}</b> (+{new_energy - player['energy']})\n\nТы готов! ⚽", parse_mode=ParseMode.HTML)

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer("📖 <b>Как играть:</b>\n\n⚽ <b>Матч</b> — играй за клуб (тратит энергию).\n🏋️ <b>Тренировка</b> — прокачивай навыки.\n🔄 <b>Трансфер</b> — переходи в сильный клуб (после 5 матчей).\n💤 <b>Отдых</b> — восстанавливай энергию.\n📊 <b>Статистика</b> — следи за карьерой.\n🏆 <b>Достижения</b> — награды за успехи!\n\nКаждые 10 матчей — конец сезона. До 25 лет рост, после 32 — спад.", parse_mode=ParseMode.HTML)

@dp.message(Command("reset"))
async def cmd_reset(message: types.Message):
    user_id = message.from_user.id
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM players WHERE user_id = ?", (user_id,))
        await db.execute("DELETE FROM match_history WHERE user_id = ?", (user_id,))
        await db.execute("DELETE FROM achievements WHERE user_id = ?", (user_id,))
        await db.commit()
    await message.answer("🗑 <b>Карьера сброшена!</b>\n\nНачни заново: /start", parse_mode=ParseMode.HTML, reply_markup=ReplyKeyboardRemove())

# ===================== SCHEDULER (CRON) =====================
async def scheduler_task():
    """Фоновая задача: начисление зарплаты каждые 24ч, энергия каждые 6ч"""
    await asyncio.sleep(30)  # Подождём запуска бота
    while True:
        try:
            now = datetime.now()
            # Восстановление энергии каждые 6 часов (+15 всем)
            players = await get_all_players()
            for p in players:
                new_energy = min(MAX_ENERGY, p["energy"] + 15)
                await update_player(p["user_id"], energy=new_energy)
            # Начисление зарплаты каждые 24 часа
            async with aiosqlite.connect(DB_PATH) as db:
                async with db.execute("SELECT ran_at FROM scheduler_log WHERE job_name = 'salary' ORDER BY id DESC LIMIT 1") as cur:
                    row = await cur.fetchone()
                    last_salary = datetime.fromisoformat(row[0]) if row else None
                if not last_salary or (now - last_salary).total_seconds() >= 86400:
                    for p in players:
                        if p["salary"] > 0:
                            new_money = p["money"] + p["salary"]
                            await update_player(p["user_id"], money=new_money)
                    await db.execute("INSERT INTO scheduler_log (job_name, ran_at) VALUES (?, ?)", ("salary", now.isoformat()))
                    await db.commit()
            await asyncio.sleep(21600)  # 6 часов
        except Exception as e:
            print(f"[SCHEDULER ERROR] {e}")
            await asyncio.sleep(300)

# ===================== MAIN =====================
async def main():
    await init_db()
    asyncio.create_task(scheduler_task())
    print("⚽ Football Career Manager Bot запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
