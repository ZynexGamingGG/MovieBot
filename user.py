import re
import uuid
import asyncio

from aiogram import Router, F
from aiogram.types import (Message, CallbackQuery,
                            InlineQuery, InlineQueryResultArticle,
                            InputTextMessageContent)
from aiogram.filters import CommandStart

import database as db
from config import CHANNEL_URL
from keyboards import user_menu, movie_found_kb

router = Router()


def normalize_code(text: str) -> str:
    """'037', ' 37 ', '37' -> '037' (3 xonali, oldida 0)"""
    text = text.strip()
    if text.isdigit():
        return text.zfill(3)
    return text


# ─── /start ──────────────────────────────────────────────────────
@router.message(CommandStart())
async def cmd_start(msg: Message):
    await db.register_user(
        msg.from_user.id,
        msg.from_user.username,
        msg.from_user.full_name
    )

    # /start 037  →  deep link orqali to'g'ridan kino yuborish
    args = msg.text.split(maxsplit=1)
    if len(args) > 1:
        code = normalize_code(args[1])
        await send_movie(msg, code)
        return

    await msg.answer(
        f"👋 Assalomu alaykum, <b>{msg.from_user.first_name}</b>!\n\n"
        "🎬 <b>Kino Bot</b>ga xush kelibsiz!\n\n"
        "📌 Instagramdagi postlarda kino kodi yoziladi.\n"
        "Masalan: <code>037</code>, <code>109</code>, <code>913</code>\n\n"
        "🔽 Kino kodini yuboring va filmni oling!",
        reply_markup=user_menu()
    )


# ─── Qo'llanma ───────────────────────────────────────────────────
@router.message(F.text == "📖 Qo'llanma")
async def guide(msg: Message):
    await msg.answer(
        "📖 <b>Qo'llanma</b>\n\n"
        "1️⃣ Instagramdagi kino postni toping\n"
        "2️⃣ Post tagidagi <b>raqamli kodni</b> nusxa oling\n"
        "   Masalan: <code>037</code>\n"
        "3️⃣ Shu kodni botga yuboring\n"
        "4️⃣ Kino darhol yuboriladi! 🎉\n\n"
        f"📸 Instagram: {CHANNEL_URL}"
    )


# ─── Statistika ──────────────────────────────────────────────────
@router.message(F.text == "📊 Statistika")
async def stats(msg: Message):
    movies = await db.movies_count()
    users  = await db.users_count()
    tops   = await db.top_movies(3)

    top_text = ""
    for i, m in enumerate(tops, 1):
        top_text += f"  {i}. <code>{m['code']}</code> — {m['title']} ({m['views']} marta)\n"

    await msg.answer(
        f"📊 <b>Statistika</b>\n\n"
        f"🎬 Jami kinolar: <b>{movies}</b> ta\n"
        f"👥 Foydalanuvchilar: <b>{users}</b> ta\n\n"
        f"🏆 <b>Top 3 kino:</b>\n{top_text or '  Hali yoq'}"
    )


# ─── Kino Qidirish tugmasi ───────────────────────────────────────
@router.message(F.text == "🎬 Kino Qidirish")
async def search_prompt(msg: Message):
    await msg.answer(
        "🔢 Kino kodini yoki <b>nomini</b> yuboring:\n\n"
        "Masalan: <code>037</code> yoki <code>Avengers</code>"
    )


# ─── ASOSIY: Raqamli kod yuborilganda ───────────────────────────
@router.message(F.text.regexp(r"^\d{1,4}$"))
async def handle_code(msg: Message):
    await db.register_user(
        msg.from_user.id,
        msg.from_user.username,
        msg.from_user.full_name
    )
    code = normalize_code(msg.text)
    await send_movie(msg, code)


# ─── Nom bo'yicha qidirish ───────────────────────────────────────
@router.message(F.text & ~F.text.startswith("/"))
async def handle_search(msg: Message):
    """Matn yuborilsa — nom bo'yicha qidiradi"""
    query = msg.text.strip()
    # Tugma matni bo'lsa — o'tkazib yuborish
    if query in ("📖 Qo'llanma", "📊 Statistika", "🎬 Kino Qidirish",
                 "➕ Kino Qo'shish", "🗑 Kino O'chirish",
                 "📋 Kinolar Ro'yxati", "📣 Hammaga Xabar",
                 "❌ Bekor qilish"):
        return

    results = await db.search_movies(query, limit=5)
    if not results:
        await msg.answer(
            f"❌ <b>'{query}'</b> bo'yicha hech narsa topilmadi.\n\n"
            "🔍 Kodni to'g'ri yozdingizmi?\n"
            f"📸 Kodlarni Instagram sahifamizdan toping:\n{CHANNEL_URL}"
        )
        return

    if len(results) == 1:
        # Bitta natija — to'g'ri yuborish
        await send_movie_obj(msg, results[0])
        return

    # Bir nechta natija — ro'yxat ko'rsatish
    text = f"🔍 <b>'{query}'</b> bo'yicha {len(results)} ta natija:\n\n"
    for m in results:
        text += f"🔢 <code>{m['code']}</code> — {m['title']} 👁 {m['views']}\n"
    text += "\n📌 Kodni yuboring va filmni oling!"
    await msg.answer(text)


async def send_movie(msg: Message, code: str):
    movie = await db.get_movie(code)
    if not movie:
        await msg.answer(
            f"❌ <b>{code}</b> kodli kino topilmadi.\n\n"
            "🔍 Kodni to'g'ri yozdingizmi?\n"
            f"📸 Kodlarni Instagram sahifamizdan toping:\n{CHANNEL_URL}"
        )
        return
    await send_movie_obj(msg, movie)


async def send_movie_obj(msg: Message, movie):
    await db.increment_views(movie["code"])

    caption = (
        f"🎬 <b>{movie['title']}</b>\n"
        f"🔢 Kod: <code>{movie['code']}</code>\n"
    )
    if movie["caption"]:
        caption += f"\n📝 {movie['caption']}"

    kb = movie_found_kb(movie["code"])

    if movie["file_type"] == "video":
        await msg.answer_video(video=movie["file_id"], caption=caption, reply_markup=kb)
    elif movie["file_type"] == "document":
        await msg.answer_document(document=movie["file_id"], caption=caption, reply_markup=kb)
    else:
        await msg.answer(caption, reply_markup=kb)


# ─── Inline mode: '@bot 037' ─────────────────────────────────────
@router.inline_query()
async def inline_search(query: InlineQuery):
    q = query.query.strip()
    if not q:
        await query.answer([], cache_time=1)
        return

    # Raqam bo'lsa — kod bo'yicha qidirish
    if q.isdigit():
        code = normalize_code(q)
        movie = await db.get_movie(code)
        movies = [movie] if movie else []
    else:
        movies = await db.search_movies(q, limit=5)

    if not movies:
        result = InlineQueryResultArticle(
            id=str(uuid.uuid4()),
            title=f"❌ '{q}' — topilmadi",
            input_message_content=InputTextMessageContent(
                message_text=f"❌ Kino topilmadi. So'rov: <code>{q}</code>",
                parse_mode="HTML"
            )
        )
        await query.answer([result], cache_time=5)
        return

    results = []
    for movie in movies:
        results.append(InlineQueryResultArticle(
            id=str(uuid.uuid4()),
            title=f"🎬 {movie['title']}  (#{movie['code']})",
            description=movie["caption"][:100] if movie["caption"] else f"👁 {movie['views']} marta ko'rilgan",
            input_message_content=InputTextMessageContent(
                message_text=(
                    f"🎬 <b>{movie['title']}</b>\n"
                    f"🔢 Kod: <code>{movie['code']}</code>\n\n"
                    f"🤖 Botdan yuklab oling!"
                ),
                parse_mode="HTML"
            )
        ))
    await query.answer(results, cache_time=10)
