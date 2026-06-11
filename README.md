# 🎬 KinoBot — Telegram Kino Boti

Instagram postlarga raqamli kod qo'yasiz → foydalanuvchi kodni botga yozadi → kino yuboriladi!

---

## 📁 Fayl tuzilmasi

```
kinobot/
├── bot.py              ← Asosiy fayl
├── config.py           ← Sozlamalar
├── database.py         ← SQLite bazasi
├── keyboards.py        ← Tugmalar
├── handlers/
│   ├── user.py         ← Foydalanuvchi handlerlari
│   └── admin.py        ← Admin handlerlari
├── .env                ← Token va sozlamalar
└── requirements.txt
```

---

## ⚙️ O'rnatish

### 1. Kutubxonalarni o'rnatish
```bash
pip install -r requirements.txt
```

### 2. .env faylini yaratish
```bash
cp .env.example .env
```

`.env` faylini oching va to'ldiring:
```
BOT_TOKEN=7123456789:AAF_...   ← @BotFather dan olingan token
ADMIN_IDS=123456789            ← Sizning Telegram ID (bir nechta bo'lsa vergul bilan)
CHANNEL_URL=https://instagram.com/sizning_sahifa
```

> Telegram ID ni bilish uchun: @userinfobot ga `/start` yuboring

### 3. Botni ishga tushirish
```bash
python bot.py
```

---

## 🎮 Qanday ishlaydi?

### Foydalanuvchi uchun:
1. Instagram postdagi kino kodini ko'radi (masalan: `037`)
2. Botga `037` deb yozadi
3. Bot kinoni darhol yuboradi ✅

### Siz (admin) uchun:
1. `/admin` buyrug'ini yuboring
2. **"➕ Kino Qo'shish"** tugmasini bosing
3. Kod kiriting: `037`
4. Kino nomini kiriting
5. Tavsif kiriting (yoki `-` o'tkazib yuborish)
6. Video yoki faylni yuboring
7. Tayyor! ✅

---

## 🛠 Admin imkoniyatlari

| Tugma | Vazifa |
|-------|--------|
| ➕ Kino Qo'shish | Yangi kino + kod qo'shish |
| 🗑 Kino O'chirish | Kod orqali o'chirish |
| 📋 Kinolar Ro'yxati | Barcha kinolar (sahifalangan) |
| 📊 Statistika | Kinolar, userlar, top 5 |
| 📣 Hammaga Xabar | Broadcast xabar |

---

## 📌 Kod formati

- Faqat raqam: `037`, `109`, `913`, `1`, `42`
- Bot avtomatik 3 xonali qiladi: `37` → `037`
- Deep link: `t.me/YourBot?start=037` — Instagram bio ga qo'shsa bo'ladi

---

## 🚀 Server (VPS) da ishga tushirish

```bash
# screen bilan
screen -S kinobot
python bot.py
# Ctrl+A, D — fon rejimiga o'tish

# yoki systemd service sifatida
```
