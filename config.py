import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN   = os.getenv("BOT_TOKEN", "8623572936:AAG1jIKftv_l9Cgq8tz9wSmh-VI1nlRHCW8")
ADMIN_IDS   = list(map(int, os.getenv("ADMIN_IDS", "8968585930").split(",")))
DB_PATH     = "kinobot.db"
CHANNEL_URL = os.getenv("CHANNEL_URL", "https://www.instagram.com/loftmovies.uz/")
