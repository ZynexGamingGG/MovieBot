from aiogram.types import InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


def user_menu():
    kb = ReplyKeyboardBuilder()
    kb.button(text="🎬 Kino Qidirish")
    kb.button(text="📊 Statistika")
    kb.button(text="📖 Qo'llanma")
    kb.adjust(1, 2)
    return kb.as_markup(resize_keyboard=True)


def admin_menu():
    kb = ReplyKeyboardBuilder()
    kb.button(text="➕ Kino Qo'shish")
    kb.button(text="🗑 Kino O'chirish")
    kb.button(text="📋 Kinolar Ro'yxati")
    kb.button(text="📊 Statistika")
    kb.button(text="📣 Hammaga Xabar")
    kb.adjust(2, 2, 1)
    return kb.as_markup(resize_keyboard=True)


def cancel_kb():
    kb = ReplyKeyboardBuilder()
    kb.button(text="❌ Bekor qilish")
    return kb.as_markup(resize_keyboard=True, one_time_keyboard=True)


def movie_found_kb(code: str):
    b = InlineKeyboardBuilder()
    b.button(text="📤 Do'stga Ulashish", switch_inline_query=str(code))
    return b.as_markup()


def movies_nav_kb(offset: int, total: int):
    b = InlineKeyboardBuilder()
    nav = []
    if offset > 0:
        nav.append(InlineKeyboardButton(text="◀️", callback_data=f"page_{offset-10}"))
    if offset + 10 < total:
        nav.append(InlineKeyboardButton(text="▶️", callback_data=f"page_{offset+10}"))
    if nav:
        b.row(*nav)
    return b.as_markup()


def movie_detail_kb(code: str):
    b = InlineKeyboardBuilder()
    b.button(text="🗑 O'chirish", callback_data=f"del_{code}")
    b.button(text="◀️ Ro'yxat", callback_data="page_0")
    b.adjust(2)
    return b.as_markup()


def confirm_del_kb(code: str):
    b = InlineKeyboardBuilder()
    b.button(text="✅ Ha, o'chir", callback_data=f"confirmed_del_{code}")
    b.button(text="❌ Yo'q", callback_data="cancel_del")
    b.adjust(2)
    return b.as_markup()
