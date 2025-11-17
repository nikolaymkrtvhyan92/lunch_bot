"""
Конфигурация бота
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Токен бота
BOT_TOKEN = os.getenv('BOT_TOKEN')

# ID администратора
ADMIN_ID = int(os.getenv('ADMIN_ID', 0))

# Время уведомления о обеде
LUNCH_TIME = os.getenv('LUNCH_TIME', '12:00')

# Часовой пояс
TIMEZONE = os.getenv('TIMEZONE', 'Europe/Moscow')

# База данных
# Если есть DATABASE_URL (PostgreSQL на Railway), используем его
# Иначе используем SQLite локально
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL:
    # Railway PostgreSQL
    DATABASE_TYPE = 'postgresql'
else:
    # SQLite локально
    DATABASE_TYPE = 'sqlite'
    DATABASE_NAME = 'lunch_bot.db'

