import aiosqlite
from config import DB_PATH


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS movies (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                code      TEXT UNIQUE NOT NULL,   -- '037', '109', '913'
                title     TEXT NOT NULL,
                caption   TEXT DEFAULT '',         -- tavsif / izoh
                file_id   TEXT DEFAULT '',         -- Telegram file_id (video)
                file_type TEXT DEFAULT 'video',    -- video | document
                views     INTEGER DEFAULT 0,
                added_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id   INTEGER PRIMARY KEY,
                username  TEXT,
                full_name TEXT,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Indekslar — tezroq qidirish uchun
        await db.execute("CREATE INDEX IF NOT EXISTS idx_movies_code ON movies(code)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_movies_views ON movies(views DESC)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_movies_title ON movies(title)")
        await db.commit()


# ─── KINO ────────────────────────────────────────────────────────

async def add_movie(code: str, title: str, caption: str,
                    file_id: str, file_type: str = "video"):
    """Kino qo'shish yoki yangilash"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO movies (code, title, caption, file_id, file_type)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(code) DO UPDATE SET
                title=excluded.title,
                caption=excluded.caption,
                file_id=excluded.file_id,
                file_type=excluded.file_type
        """, (code, title, caption, file_id, file_type))
        await db.commit()


async def get_movie(code: str):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM movies WHERE code = ?", (code,)
        ) as cur:
            return await cur.fetchone()


async def delete_movie(code: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM movies WHERE code = ?", (code,))
        await db.commit()


async def all_movies(limit=10, offset=0):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """SELECT * FROM movies
               ORDER BY CAST(code AS INTEGER) ASC
               LIMIT ? OFFSET ?""",
            (limit, offset)
        ) as cur:
            return await cur.fetchall()


async def movies_count():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM movies") as cur:
            return (await cur.fetchone())[0]


async def increment_views(code: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE movies SET views = views + 1 WHERE code = ?", (code,)
        )
        await db.commit()


async def top_movies(limit=5):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM movies ORDER BY views DESC LIMIT ?", (limit,)
        ) as cur:
            return await cur.fetchall()


async def search_movies(query: str, limit=10):
    """Nom yoki kod bo'yicha kino qidirish"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        pattern = f"%{query}%"
        async with db.execute(
            """SELECT * FROM movies
               WHERE title LIKE ? OR code LIKE ?
               ORDER BY views DESC
               LIMIT ?""",
            (pattern, pattern, limit)
        ) as cur:
            return await cur.fetchall()


# ─── USER ─────────────────────────────────────────────────────────

async def register_user(user_id: int, username: str, full_name: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR IGNORE INTO users (user_id, username, full_name)
            VALUES (?, ?, ?)
        """, (user_id, username or "", full_name or ""))
        await db.commit()


async def users_count():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as cur:
            return (await cur.fetchone())[0]


async def all_user_ids():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT user_id FROM users") as cur:
            rows = await cur.fetchall()
            return [r[0] for r in rows]
