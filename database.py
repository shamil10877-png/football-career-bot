import aiosqlite

DB = "players.db"

async def init_db():
    async with aiosqlite.connect(DB) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS players(
            user_id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            age INTEGER,
            nation TEXT,
            position TEXT,
            club TEXT,
            rating INTEGER,
            potential INTEGER,
            money INTEGER,
            salary INTEGER,
            matches INTEGER,
            goals INTEGER,
            assists INTEGER,
            trophies INTEGER,
            energy INTEGER,
            morale INTEGER
        )
        """)
        await db.commit()

async def player_exists(user_id):
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute(
            "SELECT user_id FROM players WHERE user_id=?",
            (user_id,)
        )
        return await cur.fetchone()

async def create_player(user_id):
    async with aiosqlite.connect(DB) as db:
        await db.execute("""
        INSERT INTO players
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """,(
            user_id,
            "",
            "",
            15,
            "",
            "ST",
            "Без клуба",
            55,
            90,
            1000,
            0,
            0,
            0,
            0,
            0,
            100,
            100
        ))
        await db.commit()
