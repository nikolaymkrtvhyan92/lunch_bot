#!/usr/bin/env python3
"""Добавление ресторана Ани"""
from database import Database

db = Database()

# Добавляем ресторан Ани (армянская кухня)
try:
    rest_id = db.add_restaurant(
        name="Ани",
        description="Армянская кухня: хинкали, хачапури, шашлык",
        emoji="🥘",
        address=None,
        phone=None
    )
    print(f"✅ 🥘 Ресторан 'Ани' добавлен (ID: {rest_id})")
    print("\nТеперь нужно добавить его на Railway!")
except Exception as e:
    print(f"❌ Ошибка: {e}")
