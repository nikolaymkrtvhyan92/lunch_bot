"""
Автоматическое добавление базовых данных при старте бота
"""
import logging
from database import Database

logger = logging.getLogger(__name__)

def seed_restaurants():
    """Добавить базовые рестораны если БД пустая"""
    db = Database()
    
    # Проверяем есть ли уже рестораны
    existing = db.get_all_restaurants(active_only=False)
    if existing:
        logger.info(f"✅ База данных уже содержит {len(existing)} ресторан(ов)")
        return
    
    logger.info("🌱 Инициализация базовых ресторанов...")
    
    # Базовые рестораны
    restaurants = [
        {
            "name": "Ани",
            "description": "Армянская кухня: хинкали, долма, шашлык",
            "emoji": "🥘",
            "address": None,
            "phone": None
        },
        {
            "name": "Итальянская кухня",
            "description": "Пицца, паста, ризотто",
            "emoji": "🍝",
            "address": None,
            "phone": None
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
        }
    ]
    
    added_count = 0
    for rest in restaurants:
        try:
            rest_id = db.add_restaurant(
                name=rest["name"],
                description=rest["description"],
                emoji=rest["emoji"],
                address=rest["address"],
                phone=rest["phone"]
            )
            logger.info(f"✅ {rest['emoji']} {rest['name']} (ID: {rest_id})")
            added_count += 1
        except Exception as e:
            logger.error(f"❌ Ошибка при добавлении {rest['name']}: {e}")
    
    logger.info(f"🎉 Добавлено {added_count} ресторан(ов)!")

if __name__ == "__main__":
    # Для тестирования
    logging.basicConfig(level=logging.INFO)
    seed_restaurants()

