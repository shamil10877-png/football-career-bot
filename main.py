import os
import asyncio
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, LabeledPrice, PreCheckoutQuery
from aiogram.filters import Command, CommandObject
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Загрузка конфигурации
load_dotenv()
BOT_TOKEN = os.getenv("8849485512:AAEhvLOhm7rLwmXoalUx1Wnp5QKCSbFw7O4")
OWNER_ID = int(os.getenv("OWNER_ID", 0))
CHANNEL_ID = os.getenv("CHANNEL_ID", "") # Канал для проверки подписки

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Глобальная БД в памяти (на GitHub лучше показать структуру, затем заменить на SQLite/PostgreSQL)
db = {
    "players": {},       # Данные игроков
    "coaches": {},       # Данные режима тренера
    "referrals": {}      # Система рефералов {кто_пригласил: [список_id_приглашенных]}
}

# --- КЛАВИАТУРЫ ---
def get_main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⚽ Сыграть матч"), KeyboardButton(text="🏋️ Тренировка")],
            [KeyboardButton(text="📊 Мой профиль"), KeyboardButton(text="🏢 Сменить клуб")],
            [KeyboardButton(text="💼 Меню Тренера"), KeyboardButton(text="🎰 Развлечения")]
        ],
        resize_keyboard=True
    )

def get_coach_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🏃 Команда"), KeyboardButton(text="🏋️‍♂️ Тренировка команды")],
            [KeyboardButton(text="🏟️ Матч команды"), KeyboardButton(text="📋 Тактика")],
            [KeyboardButton(text="🏆 Мои Трофеи"), KeyboardButton(text="🔙 Главное меню")]
        ],
        resize_keyboard=True
    )

def get_casino_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎰 Слоты"), KeyboardButton(text="🪙 Орел/Решка")],
            [KeyboardButton(text="🎡 Рулетка"), KeyboardButton(text="🥅 Пенальти")],
            [KeyboardButton(text="🔙 Главное меню")]
        ],
        resize_keyboard=True
    )

# Инициализация профилей
def init_user(user_id, name):
    if user_id not in db["players"]:
        db["players"][user_id] = {
            "name": name, "rating": 10, "money": 5000, "club": "Дворовый ФК",
            "goals": 0, "matches": 0, "last_daily": None, "bonus_claimed": False
        }
    if user_id not in db["coaches"]:
        db["coaches"][user_id] = {
            "team_name": "Без названия", "rating": 10, "trophies": 0,
            "tactics": "4-4-2", "staff_level": 1, "history": ["Начало карьеры менеджера"]
        }

# --- БАЗОВЫЕ И ТЕХНИЧЕСКИЕ КОМАНДЫ ---

@dp.message(Command("start"))
async def cmd_start(message: Message, command: CommandObject):
    user_id = message.from_user.id
    init_user(user_id, message.from_user.first_name)
    
    # Обработка реферального кода /start <inviter_id>
    args = command.args
    if args and args.isdigit():
        inviter_id = int(args)
        if inviter_id != user_id and inviter_id in db["players"]:
            if inviter_id not in db["referrals"]:
                db["referrals"][inviter_id] = []
            if user_id not in db["referrals"][inviter_id]:
                db["referrals"][inviter_id].append(user_id)
                db["players"][inviter_id]["money"] += 15000  # Бонус пригласившему
                await bot.send_message(inviter_id, f"🎉 По вашей ссылке зарегистрировался новый игрок! Вам начислено +15,000 €")

    await message.answer("⚽ Добро пожаловать в симулятор футбола! Выберите действие:", reply_markup=get_main_menu())

@dp.message(Command("ping"))
async def cmd_ping(message: Message):
    start_time = datetime.now()
    msg = await message.answer("🏓 Понг! Измеряю задержку...")
    end_time = datetime.now()
    ping = (end_time - start_time).microseconds // 1000
    await msg.edit_text(f"🏓 Понг!\n⏱ Скорость ответа бота: `{ping} мс`", parse_mode="Markdown")

@dp.message(Command("myid"))
async def cmd_myid(message: Message):
    await message.answer(f"🆔 Ваш Telegram ID: `{message.from_user.id}`", parse_mode="Markdown")

@dp.message(Command("help"))
async def cmd_help(message: Message):
    help_text = (
        "📜 **Список доступных команд:**\n\n"
        "⚽ **Игрок:** /stats, /daily, /bonus, /tasks, /referral, /reminder\n"
        "💼 **Тренер:** /coach_profile, /team, /train_team, /match_team, /tactics, /coach_trophies, /coach_leaderboard, /staff, /coach_history\n"
        "🎰 **Мини-игры:** /casino, /penalty\n"
        "🤝 **Экономика:** /give, /donate\n"
        "🔧 **Система:** /ping, /myid, /help, /start"
    )
    await message.answer(help_text, parse_mode="Markdown")

@dp.message(Command("stats"))
@dp.message(F.text == "📊 Мой профиль")
async def cmd_stats(message: Message):
    user_id = message.from_user.id
    init_user(user_id, message.from_user.first_name)
    p = db["players"][user_id]
    
    text = (
        f"📊 **СТАТИСТИКА ИГРОКА {p['name']}**\n\n"
        f"🏢 Клуб: {p['club']}\n"
        f"⭐ Скилл (Рейтинг): `{p['rating']}`\n"
        f"💰 Баланс: `{p['money']:,} €`\n"
        f"🏟️ Сыграно матчей: {p['matches']}\n"
        f"⚽ Забито голов: {p['goals']}"
    )
    await message.answer(text, parse_mode="Markdown")

# Навигация через текст
@dp.message(F.text == "💼 Меню Тренера")
async def go_coach_menu(message: Message):
    await message.answer("📋 Вы перешли в панель управления тренера:", reply_markup=get_coach_menu())

@dp.message(F.text == "🎰 Развлечения")
async def go_casino_menu(message: Message):
    await message.answer("🎲 Добро пожаловать в зону отдыха и казино! Выберите игру:", reply_markup=get_casino_menu())

@dp.message(F.text == "🔙 Главное меню")
async def go_main_menu(message: Message):
    await message.answer("🔙 Вы вернулись в главное меню игрока:", reply_markup=get_main_menu())


# --- РЕЖИМ ТРЕНЕРА ---

@dp.message(Command("coach_profile"))
async def cmd_coach_profile(message: Message):
    user_id = message.from_user.id
    init_user(user_id, message.from_user.first_name)
    c = db["coaches"][user_id]
    
    text = (
        f"👔 **ПРОФИЛЬ ТРЕНЕРА**\n\n"
        f"🏃 Команда: *{c['team_name']}*\n"
        f"⭐ Рейтинг состава: `{c['rating']}`\n"
        f"📋 Тактическая схема: `{c['tactics']}`\n"
        f"🎓 Уровень штаба: `{c['staff_level']}`\n"
        f"🏆 Завоевано трофеев: `{c['trophies']}`"
    )
    await message.answer(text, parse_mode="Markdown")

@dp.message(Command("team"))
@dp.message(F.text == "🏃 Команда")
async def cmd_team(message: Message):
    user_id = message.from_user.id
    init_user(user_id, message.from_user.first_name)
    c = db["coaches"][user_id]
    await message.answer(f"📋 Ваша команда: *{c['team_name']}*\n⭐ Общая сыгранность и рейтинг: {c['rating']} PTS.", parse_mode="Markdown")

@dp.message(Command("train_team"))
@dp.message(F.text == "🏋️‍♂️ Тренировка команды")
async def cmd_train_team(message: Message):
    user_id = message.from_user.id
    init_user(user_id, message.from_user.first_name)
    c = db["coaches"][user_id]
    
    gain = random.randint(2, 5) * c["staff_level"]
    c["rating"] += gain
    await message.answer(f"🏋️‍♂️ Вы провели командную тренировку. Рейтинг состава вырос на +{gain}! Текущий рейтинг: {c['rating']}.")

@dp.message(Command("match_team"))
@dp.message(F.text == "🏟️ Матч команды")
async def cmd_match_team(message: Message):
    user_id = message.from_user.id
    init_user(user_id, message.from_user.first_name)
    c = db["coaches"][user_id]
    p = db["players"][user_id]
    
    opponent_power = random.randint(10, 150)
    await message.answer(f"🏟️ Начинается матч против ФК 'Соперник' (Сила: {opponent_power})...")
    await asyncio.sleep(1)
    
    # Шанс выигрыша зависит от силы состава
    if c["rating"] > opponent_power:
        c["trophies"] += 1
        p["money"] += 50000
        c["history"].append(f"Победа над ФК Соперник ({datetime.now().strftime('%d.%m %H:%M')})")
        await message.answer(f"🏆 Победа! Ваша тактика сработала. Вы выиграли кубок и заработали +50,000 €!")
    else:
        c["history"].append(f"Поражение от ФК Соперник ({datetime.now().strftime('%d.%m %H:%M')})")
        await message.answer("❌ Ваша команда проиграла. Составу не хватило рейтинга или правильной тактики.")

@dp.message(Command("tactics"))
@dp.message(F.text == "📋 Тактика")
async def cmd_tactics(message: Message, command: CommandObject):
    user_id = message.from_user.id
    init_user(user_id, message.from_user.first_name)
    c = db["coaches"][user_id]
    
    args = command.args if command else None
    if not args:
        await message.answer(f"📋 Текущая тактика: `{c['tactics']}`\nЧтобы изменить её, напишите команду с параметром, например: `/tactics 4-3-3`", parse_mode="Markdown")
        return
        
    c["tactics"] = args
    await message.answer(f"✅ Вы успешно изменили тактическую схему на: `{args}`", parse_mode="Markdown")

@dp.message(Command("coach_trophies"))
@dp.message(F.text == "🏆 Мои Трофеи")
async def cmd_coach_trophies(message: Message):
    user_id = message.from_user.id
    init_user(user_id, message.from_user.first_name)
    c = db["coaches"][user_id]
    await message.answer(f"🏆 На вашей полке наград: `{c['trophies']}` кубков.", parse_mode="Markdown")

@dp.message(Command("coach_leaderboard"))
async def cmd_coach_leaderboard(message: Message):
    # Сортировка тренеров по количеству кубков
    top = sorted(db["coaches"].items(), key=lambda x: x[1]["trophies"], reverse=True)[:10]
    if not top:
        return await message.answer("🏆 Таблица лидеров пока пуста.")
        
    text = "🏆 **ТОП-10 ЛУЧШИХ ТРЕНЕРОВ:**\n\n"
    for i, (uid, data) in enumerate(top, start=1):
        player_name = db["players"].get(uid, {}).get("name", "Неизвестно")
        text += f"{i}. {player_name} — {data['trophies']} 🏆 (Команда: {data['team_name']})\n"
    await message.answer(text, parse_mode="Markdown")

@dp.message(Command("staff"))
          Режим ИИ
Все
Картинки
Видео
Новости
Книги
Авиабилеты
Финансы

3 сайта
Да, я могу создать полноценный код для текстовой игры-симулятора «Карьера футболиста» на Python.
Ниже представлен готовый код на базе современной библиотеки aiogram 3.x. Бот имитирует карьеру: игрок может тренироваться, повышать навыки, играть матчи за клуб, зарабатывать деньги и переходить в более сильные команды.
Подготовка к запуску
Создайте бота в Telegram через @BotFather и скопируйте полученный API-токен.
Установите библиотеку aiogram через терминал: 

Cloud.ru
 +1
bash
pip install aiogram
Используйте код с осторожностью.
Замените в коде значение BOT_TOKEN на ваш реальный токен.
Исходный код бота (bot.py)
python
import asyncio
import random
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command

# Вставьте сюда ваш токен от BotFather
BOT_TOKEN = "ВАШ_ТЕЛЕГРАМ_ТОКЕН"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Временная база данных в оперативной памяти (после перезапуска сбросится)
players_db = {}

# Главная клавиатура
def get_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⚽ Сыграть матч"), KeyboardButton(text="🏋️ Тренировка")],
            [KeyboardButton(text="📊 Мой профиль"), KeyboardButton(text="🏢 Сменить клуб")]
        ],
        resize_keyboard=True
    )

# Клубы, доступные по достижении определенного рейтинга
CLUBS = [
    {"name": "Дворовый ФК", "req_rating": 0, "salary": 100},
    {"name": "Шинник", "req_rating": 20, "salary": 500},
    {"name": "ФК Краснодар", "req_rating": 50, "salary": 2000},
    {"name": "Зенит", "req_rating": 100, "salary": 5000},
    {"name": "Реал Мадрид", "req_rating": 200, "salary": 25000},
]

@dp.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    if user_id not in players_db:
        players_db[user_id] = {
            "name": message.from_user.first_name,
            "rating": 10,
            "money": 0,
            "club": "Дворовый ФК",
            "goals": 0,
            "matches": 0
        }
    
    await message.answer(
        f"Привет, {message.from_user.first_name}! Добро пожаловать в симулятор карьеры футболиста.\n"
        "Тренируйся, забивай голы и пробейся в Реал Мадрид!",
        reply_markup=get_main_keyboard()
    )

@dp.message(F.text == "📊 Мой профиль")
async def view_profile(message: Message):
    user_id = message.from_user.id
    p = players_db.get(user_id)
    
    if not p:
        return await message.answer("Введите /start, чтобы начать карьеру.")
        
    profile_text = (
        f"👤 Игрок: *{p['name']}*\n"
        f"🏢 Клуб: *{p['club']}*\n"
        f"⭐ Рейтинг (Скилл): `{p['rating']}`\n"
        f"💰 Баланс: `{p['money']} €`\n\n"
        f"📊 Статистика:\n"
        f"🏟️ Матчи: {p['matches']}\n"
        f"⚽ Голы: {p['goals']}"
    )
    await message.answer(profile_text, parse_mode="Markdown")

@dp.message(F.text == "🏋️ Тренировка")
async def do_train(message: Message):
    user_id = message.from_user.id
    p = players_db.get(user_id)
    
    if not p: return
    
    rating_gain = random.randint(1, 3)
    p["rating"] += rating_gain
    
    await message.answer(f"💪 Отличная тренировка! Твой рейтинг вырос на +{rating_gain}. Текущий рейтинг: {p['rating']}")

@dp.message(F.text == "⚽ Сыграть матч")
async def play_match(message: Message):
    user_id = message.from_user.id
    p = players_db.get(user_id)
    
    if not p: return

    p["matches"] += 1
    # Шанс забить зависит от текущего рейтинга игрока
    success_chance = min(30 + p["rating"] // 2, 90) 
    
    # Ищем зарплату текущего клуба
    current_club_stats = next((c for c in CLUBS if c["name"] == p["club"]), CLUBS[0])
    salary = current_club_stats["salary"]
    
    if random.randint(1, 100) <= success_chance:
        goals_scored = random.randint(1, 3)
        p["goals"] += goals_scored
        p["money"] += salary
        p["rating"] += 1
        
        await message.answer(
            f"🔥 Победа! Твой клуб {p['club']} выиграл матч!\n"
            f"⚽ Ты забил голы: {goals_scored}\n"
            f"💰 Получена зарплата: +{salary} €\n"
            f"⭐ Рейтинг повышен на +1"
        )
    else:
        # Проигрыш, но минимальную выплату за матч всё равно дают
        p["money"] += salary // 2
        await message.answer(
            f"❌ Обидное поражение! Матч сыгран неудачно.\n"
            f"💰 Выплачено утешительное вознаграждение: +{salary // 2} €"
        )

@dp.message(F.text == "🏢 Сменить клуб")
async def change_club(message: Message):
    user_id = message.from_user.id
    p = players_db.get(user_id)
    
    if not p: return
    
    available_clubs = [c for c in CLUBS if p["rating"] >= c["req_rating"]]
    next_club = available_clubs[-1] # Выбираем самый лучший доступный по рейтингу клуб
    
    if next_club["name"] == p["club"]:
        # Ищем, какой клуб идет следующим, чтобы сказать игроку, сколько рейтинга не хватает
        current_index = CLUBS.index(next_club)
        if current_index + 1 < len(CLUBS):
            future_club = CLUBS[current_index + 1]
            req = future_club["req_rating"] - p["rating"]
            await message.answer(
                f"Твой текущий клуб: *{p['club']}*.\n"
                f"Скауты из других команд пока не заинтересованы. "
                f"До перехода в *{future_club['name']}* не хватает {req} ед. рейтинга.",
                parse_mode="Markdown"
            )
        else:
            await message.answer("🏆 Ты уже в самом лучшем клубе мира — Реал Мадрид!")
    else:
        p["club"] = next_club["name"]
        await message.answer(
            f"🎉 Трансфер состоялся! Тебя подписал новый клуб: *{p['club']}*!\n"
            f"💶 Новая базовая зарплата за матч: {next_club['salary']} €",
            parse_mode="Markdown"
        )

async def main():
    print("Бот успешно запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
Используйте код с осторожностью.
Архитектура и механики игры
Хранение данных: Использован простой словарь players_db. При перезапуске скрипта прогресс обнулится. Для сохранения прогресса в будущем можно подключить базу данных SQLite или PostgreSQL.
Рейтинг (Скилл): Влияет на успешность матчей и открывает трансферы. Прокачивается на тренировках.
Экономика: Матчи приносят валюту в зависимости от престижности клуба.
Если вам интересно, я могу расширить этот код: добавить базу данных для сохранения прогресса, механику энергии (чтобы нельзя было кликать бесконечно) или трансферный рынок снаряжения (бутсы, форма), повышающий характеристики. С чего начнем?
ИИ может ошибаться. Проверяйте его ответы.






В текущей базовой версии кода для бота реализованы четыре основные игровые механики. Игрок управляет процессом с помощью кнопок в меню:
1. Профиль игрока (📊 Мой профиль)
Это визитная карточка футболиста, где отображается его текущий статус:
Имя и Клуб: Название команды, за которую сейчас выступает игрок.
Рейтинг: Уровень мастерства (скилл), который определяет силу футболиста.
Баланс: Количество заработанных евро (€).
Статистика: Общее число сыгранных матчей и забитых за карьеру голов.
2. Система тренировок (🏋️ Тренировка)
Главный способ развития футболиста:
Каждое нажатие кнопки симулирует тренировочный процесс.
Случайным образом увеличивает рейтинг игрока на +1, +2 или +3 единицы.
Повышение рейтинга напрямую открывает доступ к более сильным лигам.
3. Проведение матчей (⚽ Сыграть матч)
Основной источник дохода и футбольной статистики:
Расчет шансов: Бот рассчитывает вероятность успеха на основе рейтинга (чем выше скилл, тем больше шансов победить и забить).
При победе: Игрок забивает от 1 до 3 голов, получает 100% зарплаты от своего клуба и дополнительно +1 к рейтингу.
При поражении: Голы не забиваются, игрок получает лишь 50% утешительного гонорара, а рейтинг не растет.
4. Трансферная система (🏢 Сменить клуб)
Механика карьерного роста. В коде заложена лестница из 5 клубов:
Дворовый ФК (Доступен сразу, зарплата: 100 €)
Шинник (Нужен рейтинг 20+, зарплата: 500 €)
ФК Краснодар (Нужен рейтинг 50+, зарплата: 2000 €)
Зенит (Нужен рейтинг 100+, зарплата: 5000 €)
Реал Мадрид (Нужен рейтинг 200+, зарплата: 25000 €)
Бот автоматически проверяет текущий рейтинг и переводит игрока в максимально доступный для него клуб, увеличивая его доход за каждый матч.
Если вы хотите развить этот проект, мы можем добавить механику выносливости (чтобы игрок не мог кликать бесконечно), магазин бутс и агентов или базу данных, чтобы прогресс пользователей не стирался после перезапуска бота. Какую функцию добавим первой?






Отлично! Размещение проекта на GitHub — правильный шаг. Это позволит не только сохранить код, но и красиво оформить портфолио.
Чтобы проект выглядел профессионально и работал правильно у других пользователей, структуру кода нужно немного изменить: вынести токен в безопасное место и добавить файл зависимостей.
Вот готовая структура и файлы, которые нужно загрузить в ваш репозиторий:
1. Файл .gitignore
Этот файл обязателен. Он указывает Git, какие файлы нельзя загружать в публичный репозиторий. Туда мы прячем файл с конфиденциальным токеном бота.
Создайте файл с именем .gitignore и текстом:
text
.env
__pycache__/
*.pyc
Используйте код с осторожностью.
2. Файл .env (Файл конфигурации)
Создайте этот файл на своем компьютере для тестирования, но не загружайте на GitHub (благодаря правилу выше).
text
BOT_TOKEN=ваш_реальный_токен_от_botfather
Используйте код с осторожностью.
3. Файл requirements.txt (Зависимости)
Пользователи (или хостинг) будут использовать этот файл для быстрой установки библиотек.
text
aiogram==3.13.1
python-dotenv==1.0.1
Используйте код с осторожностью.
4. Обновленный код главного файла bot.py
Этот вариант кода безопасен для GitHub, так как он не содержит жестко прописанного токена, а считывает его из окружения с помощью библиотеки python-dotenv.
python
import os
import asyncio
import random
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from dotenv import load_dotenv

# Загружаем переменные из файла .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    exit("Ошибка: Токен бота не найден. Создайте файл .env и укажите BOT_TOKEN.")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Временная база данных
players_db = {}

def get_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⚽ Сыграть матч"), KeyboardButton(text="🏋️ Тренировка")],
            [KeyboardButton(text="📊 Мой профиль"), KeyboardButton(text="🏢 Сменить клуб")]
        ],
        resize_keyboard=True
    )

CLUBS = [
    {"name": "Дворовый ФК", "req_rating": 0, "salary": 100},
    {"name": "Шинник", "req_rating": 20, "salary": 500},
    {"name": "ФК Краснодар", "req_rating": 50, "salary": 2000},
    {"name": "Зенит", "req_rating": 100, "salary": 5000},
    {"name": "Реал Мадрид", "req_rating": 200, "salary": 25000},
]

@dp.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    if user_id not in players_db:
        players_db[user_id] = {
            "name": message.from_user.first_name,
            "rating": 10,
            "money": 0,
            "club": "Дворовый ФК",
            "goals": 0,
            "matches": 0
        }
    await message.answer(
        f"Привет, {message.from_user.first_name}! Добро пожаловать в симулятор карьеры футболиста.\n"
        "Тренируйся, забивай голы и пробейся в Реал Мадрид!",
        reply_markup=get_main_keyboard()
    )

@dp.message(F.text == "📊 Мой профиль")
async def view_profile(message: Message):
    user_id = message.from_user.id
    p = players_db.get(user_id)
    if not p: return
        
    profile_text = (
        f"👤 Игрок: *{p['name']}*\n"
        f"🏢 Клуб: *{p['club']}*\n"
        f"⭐ Рейтинг (Скилл): `{p['rating']}`\n"
        f"💰 Баланс: `{p['money']} €`\n\n"
        f"📊 Статистика:\n"
        f"🏟️ Матчи: {p['matches']}\n"
        f"⚽ Голы: {p['goals']}"
    )
    await message.answer(profile_text, parse_mode="Markdown")

@dp.message(F.text == "🏋️ Тренировка")
async def do_train(message: Message):
    user_id = message.from_user.id
    p = players_db.get(user_id)
    if not p: return
    
    rating_gain = random.randint(1, 3)
    p["rating"] += rating_gain
    await message.answer(f"💪 Отличная тренировка! Твой рейтинг вырос на +{rating_gain}. Текущий рейтинг: {p['rating']}")

@dp.message(F.text == "⚽ Сыграть матч")
async def play_match(message: Message):
    user_id = message.from_user.id
    p = players_db.get(user_id)
    if not p: return

    p["matches"] += 1
    success_chance = min(30 + p["rating"] // 2, 90) 
    current_club_stats = next((c for c in CLUBS if c["name"] == p["club"]), CLUBS[0])
    salary = current_club_stats["salary"]
    
    if random.randint(1, 100) <= success_chance:
        goals_scored = random.randint(1, 3)
        p["goals"] += goals_scored
        p["money"] += salary
        p["rating"] += 1
        await message.answer(
            f"🔥 Победа! Твой клуб {p['club']} выиграл матч!\n"
            f"⚽ Ты забил голы: {goals_scored}\n"
            f"💰 Получена зарплата: +{salary} €\n"
            f"⭐ Рейтинг повышен на +1"
        )
    else:
        p["money"] += salary // 2
        await message.answer(
            f"❌ Обидное поражение! Матч сыгран неудачно.\n"
            f"💰 Выплачено утешительное вознаграждение: +{salary // 2} €"
        )

@dp.message(F.text == "🏢 Сменить клуб")
async def change_club(message: Message):
    user_id = message.from_user.id
    p = players_db.get(user_id)
    if not p: return
    
    available_clubs = [c for c in CLUBS if p["rating"] >= c["req_rating"]]
    next_club = available_clubs[-1]
    
    if next_club["name"] == p["club"]:
        current_index = CLUBS.index(next_club)
        if current_index + 1 < len(CLUBS):
            future_club = CLUBS[current_index + 1]
            req = future_club["req_rating"] - p["rating"]
            await message.answer(
                f"Твой текущий клуб: *{p['club']}*.\n"
                f"До перехода в *{future_club['name']}* не хватает {req} ед. рейтинга.",
                parse_mode="Markdown"
            )
        else:
            await message.answer("🏆 Ты уже в самом лучшем клубе мира — Реал Мадрид!")
    else:
        p["club"] = next_club["name"]
        await message.answer(
            f"🎉 Трансфер состоялся! Тебя подписал новый клуб: *{p['club']}*!\n"
            f"💶 Новая базовая зарплата за матч: {next_club['salary']} €",
            parse_mode="Markdown"
        )

async def main():
    print("Бот успешно запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
Используйте код с осторожностью.
5. Файл README.md
Это лицо вашего репозитория. Напишите красивое описание, чтобы проект привлекал внимание работодателей или других разработчиков. Вот шаблон:
markdown
# ⚽ Telegram Bot: Карьера Футболиста

Текстовая игра-симулятор футбольной карьеры внутри Telegram на базе библиотеки `aiogram 3`.

## 🎮 Механики игры
- **Профиль**: Просмотр клуба, рейтинга, баланса и статистики голов.
- **Тренировки**: Прокачка скилла игрока.
- **Матчи**: Симуляция игр, генерация голов и заработок валюты.
- **Трансферы**: Переход в топовые клубы по мере роста рейтинга.

## 🛠️ Инструкция по запуску
1. Склонируйте репозиторий.
2. Установите зависимости: `pip install -r requirements.txt`
3. Создайте файл `.env` в корневой папке и добавьте свой токен: `BOT_TOKEN=ваш_токен`
4. Запустите бота: `python bot.py`
Используйте код с осторожностью.
Вам помочь составить Git-команды для отправки проекта на GitHub или, может, сразу напишем код для сохранения прогресса в базу данных SQLite (чтобы прогресс игроков не пропадал)?






Отлично, внимательно слушаю! Выкладывайте все свои идеи — будь то новые игровые фичи, экономика или технические улучшения.
Пока вы формулируете, вот несколько популярных механик, которые обычно круто заходят в таких симуляторах для GitHub-портфолио:
🔋 Выносливость/Энергия: Чтобы игроки не могли бесконечно кликать «Матч», а тратили энергию, которая восстанавливается со временем.
🛒 Магазин снаряжения: Покупка бутс, формы или услуг персонального тренера, которые дают постоянный буст к рейтингу или доходу.
🏟️ Стадион и Агенты: Возможность нанять лучшего агента для поиска жирных контрактов или улучшать личную базу.
🎲 Случайные события (Ивенты): Например: "Вас поймали на вечеринке перед матчем. Штраф 500 €" или "Вы дали крутое интервью. Рейтинг +5".
Жду ваш список задумок! Что именно добавим в игру?






Вот масштабное обновление кода бота. Проект разделен на логические модули, что идеально подходит для GitHub-репозитория и демонстрирует профессиональную структуру кода на aiogram 3.x.
В коде реализованы все запрошенные вами команды (базовые, административные, тренерские, азартные игры и бонусы), включая интеграцию Telegram Stars для донатов.
Архитектура проекта на GitHub
Для удобства создайте в папке проекта следующие файлы:
.env — токен бота, ID владельца и ID канала.
requirements.txt — список библиотек.
bot.py — главный файл запуска.
1. Файл .env
text
BOT_TOKEN=ваш_токен_от_botfather
OWNER_ID=ваш_числовой_телеграм_id
CHANNEL_ID=@ссылка_на_ваш_канал_или_его_id
Используйте код с осторожностью.
2. Файл requirements.txt
text
aiogram==3.13.1
python-dotenv==1.0.1
Используйте код с осторожностью.
3. Главный файл bot.py
python
import os
import asyncio
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, LabeledPrice, PreCheckoutQuery
from aiogram.filters import Command, CommandObject
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Загрузка конфигурации
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", 0))
CHANNEL_ID = os.getenv("CHANNEL_ID", "") # Канал для проверки подписки

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Глобальная БД в памяти (на GitHub лучше показать структуру, затем заменить на SQLite/PostgreSQL)
db = {
    "players": {},       # Данные игроков
    "coaches": {},       # Данные режима тренера
    "referrals": {}      # Система рефералов {кто_пригласил: [список_id_приглашенных]}
}

# --- КЛАВИАТУРЫ ---
def get_main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⚽ Сыграть матч"), KeyboardButton(text="🏋️ Тренировка")],
            [KeyboardButton(text="📊 Мой профиль"), KeyboardButton(text="🏢 Сменить клуб")],
            [KeyboardButton(text="💼 Меню Тренера"), KeyboardButton(text="🎰 Развлечения")]
        ],
        resize_keyboard=True
    )

def get_coach_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🏃 Команда"), KeyboardButton(text="🏋️‍♂️ Тренировка команды")],
            [KeyboardButton(text="🏟️ Матч команды"), KeyboardButton(text="📋 Тактика")],
            [KeyboardButton(text="🏆 Мои Трофеи"), KeyboardButton(text="🔙 Главное меню")]
        ],
        resize_keyboard=True
    )

def get_casino_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎰 Слоты"), KeyboardButton(text="🪙 Орел/Решка")],
            [KeyboardButton(text="🎡 Рулетка"), KeyboardButton(text="🥅 Пенальти")],
            [KeyboardButton(text="🔙 Главное меню")]
        ],
        resize_keyboard=True
    )

# Инициализация профилей
def init_user(user_id, name):
    if user_id not in db["players"]:
        db["players"][user_id] = {
            "name": name, "rating": 10, "money": 5000, "club": "Дворовый ФК",
            "goals": 0, "matches": 0, "last_daily": None, "bonus_claimed": False
        }
    if user_id not in db["coaches"]:
        db["coaches"][us
