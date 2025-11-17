#!/usr/bin/env python3
"""
Скрипт для быстрого добавления тестовых ресторанов
"""
from database import Database

db = Database()

# Список ресторанов для добавления
restaurants = [
    {
        "name": "Итальянская кухня",
        "description": "Пицца, паста, ризотто",
        "emoji": "🍝",
        "address": "ул. Ленина, 10",
        "phone": "+7 999 123-45-67"
    },
    {
        "name": "Бургерная",
        "description": "Сочные бургеры и картофель фри",
        "emoji": "🍔",
        "address": None,
        "phone": None
    },
    {
        "name": "Суши бар",
        "description": "Роллы, суши, сашими",
        "emoji": "🍣",
        "address": None,
        "phone": None
    },
    {
        "name": "Грузинская кухня",
        "description": "Хинкали, хачапури, шашлык",
        "emoji": "🫓",
        "address": None,
        "phone": None
    }
]

print("🍽️ Добавляю рестораны...\n")

for rest in restaurants:
    try:
        rest_id = db.add_restaurant(
            name=rest["name"],
            description=rest["description"],
            emoji=rest["emoji"],
            address=rest["address"],
            phone=rest["phone"]
        )
        print(f"✅ {rest['emoji']} {rest['name']} (ID: {rest_id})")
    except Exception as e:
        print(f"❌ Ошибка при добавлении {rest['name']}: {e}")

print("\n🎉 Готово! Рестораны добавлены!")
print("\nТеперь отправьте боту команду:")
print("  /lunch")
print("\nЧтобы увидеть список ресторанов для голосования!")

