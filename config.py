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
DATABASE_NAME = 'lunch_bot.db'

