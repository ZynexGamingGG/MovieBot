import asyncio
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import database as db
from config import ADMIN_IDS
from keyboards import (admin_menu, user_menu, cancel_kb,
                       movies_nav_kb, movie_detail_kb, confirm_del_kb)

router = Router()


def is_admin(uid: int) -> bool:
    return uid in ADMIN_IDS


# ─── FSM ─────────────────────────────────────────────────────────
class AddMovie(StatesGroup):
    code    = State()   # '037'
    title   = State()   # 'Avengers: Endgame'
    caption = State()   # tavsif (ixtiyoriy)
    file    = State()   # video yoki document yuborish


class DeleteMovie(StatesGroup):
    code = State()


class Broadcast(StatesGroup):
    text = State()


# ─── /admin ──────────────────────────────────────────────────────
@router.message(Command("admin"))
async def cmd_admin(msg: Message):
    if not is_admin(msg.from_user.id):
        return
    await msg.answer("🎛 <b>Admin Panel</b>", reply_markup=admin_menu())


# ─────────────────────────────────────────────────────────────────
# KINO QO'SHISH
# ─────────────────────────────────────────────────────────────────
@router.message(F.text == "➕ Kino Qo'shish")
async def add_start(msg: Message, state: FSMContext):
    if not is_admin(msg.from_user.id): return
    await state.clear()
    await state.set_state(AddMovie.code)
    await msg.answer(
        "🔢 <b>Kino kodini</b> kiriting:\n\n"
        "Masalan: <code>037</code>",
        reply_markup=cancel_kb()
    )


@router.message(AddMovie.code)
async def add_code(msg: Message, state: FSMContext):
    if msg.text == "❌ Bekor qilish":
        await state.clear()
        await msg.answer("❌ Bekor qilindi.", reply_markup=admin_menu())
        return

    code = msg.text.strip()
    if not code.isdigit():
        await msg.answer("⚠️ Faqat raqam kiriting! Masalan: <code>037</code>")
        return

    code = code.zfill(3)   # '37' → '037'

    # mavjudligini tekshir
    existing = await db.get_movie(code)
    if existing:
        await msg.answer(
            f"⚠️ <b>{code}</b> kodi allaqachon mavjud!\n"
            f"Film: {existing['title']}\n\n"
            "Yangi kod kiriting yoki bekor qiling."
        )
        return

    await state.update_data(code=code)
    await state.set_state(AddMovie.title)
    await msg.answer(f"✅ Kod: <code>{code}</code>\n\n🎬 Endi <b>kino nomini</b> kiriting:")


@router.message(AddMovie.title)
async def add_title(msg: Message, state: FSMContext):
    if msg.text == "❌ Bekor qilish":
        await state.clear()
        await msg.answer("❌ Bekor qilindi.", reply_markup=admin_menu())
        return

    await state.update_data(title=msg.text.strip())
    await state.set_state(AddMovie.caption)
    await msg.answer(
        "📝 <b>Tavsif</b> kiriting (ixtiyoriy):\n\n"
        "Janr, yil, til haqida yozishingiz mumkin.\n"
        "O'tkazib yuborish uchun: <code>-</code>"
    )


@router.message(AddMovie.caption)
async def add_caption(msg: Message, state: FSMContext):
    if msg.text == "❌ Bekor qilish":
        await state.clear()
        await msg.answer("❌ Bekor qilindi.", reply_markup=admin_menu())
        return

    caption = "" if msg.text.strip() == "-" else msg.text.strip()
    await state.update_data(caption=caption)
    await state.set_state(AddMovie.file)

    data = await state.get_data()
    await msg.answer(
        f"📦 Endi <b>kino faylini</b> yuboring:\n\n"
        f"• Video yoki Document ko'rinishida yuboring\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"Kod: <code>{data['code']}</code>\n"
        f"Nomi: {data['title']}\n"
        f"Tavsif: {caption or '—'}"
    )


@router.message(AddMovie.file, F.video | F.document)
async def add_file(msg: Message, state: FSMContext):
    data = await state.get_data()

    if msg.video:
        file_id   = msg.video.file_id
        file_type = "video"
    else:
        file_id   = msg.document.file_id
        file_type = "document"

    await db.add_movie(
        code      = data["code"],
        title     = data["title"],
        caption   = data.get("caption", ""),
        file_id   = file_id,
        file_type = file_type
    )

    await state.clear()
    await msg.answer(
        f"✅ <b>Kino qo'shildi!</b>\n\n"
        f"🔢 Kod: <code>{data['code']}</code>\n"
        f"🎬 Nomi: {data['title']}\n"
        f"📁 Turi: {file_type}",
        reply_markup=admin_menu()
    )


@router.message(AddMovie.file)
async def add_file_wrong(msg: Message):
    if msg.text == "❌ Bekor qilish":
        return
    await msg.answer("⚠️ Iltimos video yoki document (fayl) yuboring!")


# ─────────────────────────────────────────────────────────────────
# KINO O'CHIRISH
# ─────────────────────────────────────────────────────────────────
@router.message(F.text == "🗑 Kino O'chirish")
async def delete_start(msg: Message, state: FSMContext):
    if not is_admin(msg.from_user.id): return
    await state.set_state(DeleteMovie.code)
    await msg.answer(
        "🔢 O'chirmoqchi bo'lgan <b>kino kodini</b> kiriting:\n\nMasalan: <code>037</code>",
        reply_markup=cancel_kb()
    )


@router.message(DeleteMovie.code)
async def delete_by_code(msg: Message, state: FSMContext):
    if msg.text == "❌ Bekor qilish":
        await state.clear()
        await msg.answer("❌ Bekor qilindi.", reply_markup=admin_menu())
        return

    code = msg.text.strip().zfill(3)
    movie = await db.get_movie(code)
    if not movie:
        await msg.answer(f"❌ <code>{code}</code> kodi topilmadi.")
        return

    await state.clear()
    await msg.answer(
        f"🗑 <b>O'chirishni tasdiqlang:</b>\n\n"
        f"🔢 Kod: <code>{movie['code']}</code>\n"
        f"🎬 Nomi: {movie['title']}",
        reply_markup=confirm_del_kb(code)
    )


@router.callback_query(F.data.startswith("confirmed_del_"))
async def confirm_delete(cb: CallbackQuery):
    code = cb.data.split("confirmed_del_")[1]
    await db.delete_movie(code)
    await cb.message.edit_text(f"✅ <code>{code}</code> o'chirildi.", reply_markup=None)
    await cb.answer("O'chirildi!")


@router.callback_query(F.data == "cancel_del")
async def cancel_delete(cb: CallbackQuery):
    await cb.message.edit_text("❌ Bekor qilindi.")
    await cb.answer()


# ─────────────────────────────────────────────────────────────────
# KINOLAR RO'YXATI
# ─────────────────────────────────────────────────────────────────
@router.message(F.text == "📋 Kinolar Ro'yxati")
async def movies_list(msg: Message):
    if not is_admin(msg.from_user.id): return
    await show_page(msg, 0)


async def show_page(msg: Message, offset: int):
    total  = await db.movies_count()
    movies = await db.all_movies(limit=10, offset=offset)

    if not movies:
        await msg.answer("📭 Hali kino yo'q.")
        return

    text = f"📋 <b>Kinolar ro'yxati</b> ({total} ta)\n\n"
    for m in movies:
        text += f"🔢 <code>{m['code']}</code> — {m['title']}  👁 {m['views']}\n"

    await msg.answer(text, reply_markup=movies_nav_kb(offset, total))


@router.callback_query(F.data.startswith("page_"))
async def page_nav(cb: CallbackQuery):
    offset = int(cb.data.split("page_")[1])
    total  = await db.movies_count()
    movies = await db.all_movies(limit=10, offset=offset)

    text = f"📋 <b>Kinolar ro'yxati</b> ({total} ta)\n\n"
    for m in movies:
        text += f"🔢 <code>{m['code']}</code> — {m['title']}  👁 {m['views']}\n"

    await cb.message.edit_text(text, reply_markup=movies_nav_kb(offset, total))
    await cb.answer()


# ─────────────────────────────────────────────────────────────────
# STATISTIKA
# ─────────────────────────────────────────────────────────────────
@router.message(F.text == "📊 Statistika")
async def admin_stats(msg: Message):
    if not is_admin(msg.from_user.id): return
    movies = await db.movies_count()
    users  = await db.users_count()
    tops   = await db.top_movies(5)

    top_text = ""
    for i, m in enumerate(tops, 1):
        top_text += f"  {i}. <code>{m['code']}</code> {m['title']} — {m['views']} marta\n"

    await msg.answer(
        f"📊 <b>Statistika</b>\n\n"
        f"🎬 Kinolar: <b>{movies}</b> ta\n"
        f"👥 Foydalanuvchilar: <b>{users}</b> ta\n\n"
        f"🏆 <b>Top 5 kino:</b>\n{top_text or '  Hali yoq'}"
    )


# ─────────────────────────────────────────────────────────────────
# HAMMAGA XABAR (broadcast)
# ─────────────────────────────────────────────────────────────────
@router.message(F.text == "📣 Hammaga Xabar")
async def broadcast_start(msg: Message, state: FSMContext):
    if not is_admin(msg.from_user.id): return
    await state.set_state(Broadcast.text)
    await msg.answer(
        "📣 Barcha foydalanuvchilarga yuboriladigan xabarni yozing:\n\n"
        "(Bekor qilish uchun: ❌ Bekor qilish)",
        reply_markup=cancel_kb()
    )


@router.message(Broadcast.text)
async def broadcast_send(msg: Message, state: FSMContext):
    if msg.text == "❌ Bekor qilish":
        await state.clear()
        await msg.answer("❌ Bekor qilindi.", reply_markup=admin_menu())
        return

    await state.clear()
    user_ids = await db.all_user_ids()
    sent = 0
    failed = 0

    progress = await msg.answer(f"📤 Yuborilmoqda... 0/{len(user_ids)}")

    for uid in user_ids:
        try:
            await msg.bot.send_message(uid, msg.text)
            sent += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.05)   # flood limit

    await progress.edit_text(
        f"✅ <b>Xabar yuborildi!</b>\n\n"
        f"✔️ Muvaffaqiyatli: {sent}\n"
        f"❌ Yuborilmadi: {failed}"
    )
    await msg.answer(".", reply_markup=admin_menu())
