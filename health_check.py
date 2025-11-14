#!/usr/bin/env python3
"""
Проверка работоспособности бота
"""
import asyncio
import sys
from telegram import Bot
import config

async def check_bot():
    """Проверить что бот может подключиться к API"""
    try:
        bot = Bot(token=config.BOT_TOKEN)
        me = await bot.get_me()
        print(f"✅ Бот подключен: @{me.username}")
        print(f"✅ Bot ID: {me.id}")
        print(f"✅ Admin ID: {config.ADMIN_ID}")
        return True
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(check_bot())
    sys.exit(0 if result else 1)

