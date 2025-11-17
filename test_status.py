#!/usr/bin/env python3
"""Быстрая проверка статуса бота"""
import asyncio
from telegram import Bot
import config

async def test():
    bot = Bot(token=config.BOT_TOKEN)
    try:
        me = await bot.get_me()
        print(f"✅ Бот активен: @{me.username}")
        print(f"✅ Bot ID: {me.id}")
        
        # Пробуем отправить тестовое сообщение
        await bot.send_message(
            chat_id=config.ADMIN_ID,
            text="🔵 Быстрая проверка: бот доступен!\n\nОтправьте /start чтобы протестировать."
        )
        print("✅ Тестовое сообщение отправлено!")
        return True
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test())
