#!/usr/bin/env python3
"""Быстрая проверка что бот запущен"""
import asyncio
from telegram import Bot
import config

async def check():
    bot = Bot(token=config.BOT_TOKEN)
    try:
        # Пробуем отправить сообщение админу
        await bot.send_message(
            chat_id=config.ADMIN_ID,
            text="🔵 Тест: бот работает локально!\n\nЕсли видите это - значит токен правильный."
        )
        print("✅ Тест успешен!")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(check())
