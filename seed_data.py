"""
Автоматическое добавление базовых данных при старте бота
"""
import logging
from database import Database

logger = logging.getLogger(__name__)

def seed_ani_menu(db, restaurant_id):
    """Добавить меню для ресторана Ани (с фото и бейджами)"""
    
    # Placeholder фото по категориям
    photos = {
        'Салаты': 'https://picsum.photos/800/600?random=salad',
        'Супы': 'https://picsum.photos/800/600?random=soup',
        'Холодные закуски': 'https://picsum.photos/800/600?random=appetizer',
        'Горячие закуски': 'https://picsum.photos/800/600?random=hot',
        'Шашлыки': 'https://picsum.photos/800/600?random=kebab',
        'Горячие блюда': 'https://picsum.photos/800/600?random=main',
        'Гарниры': 'https://picsum.photos/800/600?random=side',
        'Десерты': 'https://picsum.photos/800/600?random=dessert',
        'Напитки': 'https://picsum.photos/800/600?random=drink',
    }
    
    menu_items = [
        # Холодные закуски
        {"category": "Холодные закуски", "name": "Ассорти мясное", "price": 2900, "photo_url": photos['Холодные закуски']},
        {"category": "Холодные закуски", "name": "Ассорти рыбное", "price": 2900, "photo_url": photos['Холодные закуски']},
        {"category": "Холодные закуски", "name": "Долма", "price": 1800, "photo_url": photos['Холодные закуски'], "badges": "new"},
        {"category": "Холодные закуски", "name": "Язык отварной", "price": 1800, "photo_url": photos['Холодные закуски']},
        {"category": "Холодные закуски", "name": "Овощи свежие", "price": 900, "photo_url": photos['Холодные закуски']},
        {"category": "Холодные закуски", "name": "Сыр-тесто-зелень", "price": 800, "photo_url": photos['Холодные закуски']},
        
        # Горячие закуски
        {"category": "Горячие закуски", "name": "Хинкали (5 шт)", "price": 700, "photo_url": photos['Горячие закуски'], "badges": "hit"},
        {"category": "Горячие закуски", "name": "Хачапури по-аджарски", "price": 1200, "photo_url": photos['Горячие закуски'], "badges": "new,hit"},
        {"category": "Горячие закуски", "name": "Хачапури по-мегрельски", "price": 1000, "photo_url": photos['Горячие закуски']},
        {"category": "Горячие закуски", "name": "Люля-кебаб", "price": 600, "photo_url": photos['Горячие закуски']},
        
        # Салаты
        {"category": "Салаты", "name": "Греческий салат", "price": 800, "photo_url": photos['Салаты'], "badges": "hit"},
        {"category": "Салаты", "name": "Цезарь с курицей", "price": 900, "photo_url": photos['Салаты']},
        {"category": "Салаты", "name": "Цезарь с креветками", "price": 1200, "photo_url": photos['Салаты']},
        {"category": "Салаты", "name": "Оливье", "price": 600, "photo_url": photos['Салаты']},
        {"category": "Салаты", "name": "Крабовый салат", "price": 700, "photo_url": photos['Салаты']},
        {"category": "Салаты", "name": "Винегрет", "price": 500, "photo_url": photos['Салаты']},
        
        # Супы
        {"category": "Супы", "name": "Харчо", "price": 600, "photo_url": photos['Супы'], "badges": "spicy,hit"},
        {"category": "Супы", "name": "Бульон куриный", "price": 400, "photo_url": photos['Супы']},
        {"category": "Супы", "name": "Суп-лапша", "price": 500, "photo_url": photos['Супы']},
        {"category": "Супы", "name": "Окрошка", "price": 600, "photo_url": photos['Супы']},
        
        # Шашлыки
        {"category": "Шашлыки", "name": "Шашлык из свинины", "price": 1800, "photo_url": photos['Шашлыки']},
        {"category": "Шашлыки", "name": "Шашлык из курицы", "price": 1500, "photo_url": photos['Шашлыки']},
        {"category": "Шашлыки", "name": "Шашлык из баранины", "price": 2200, "photo_url": photos['Шашлыки']},
        {"category": "Шашлыки", "name": "Шашлык из говядины", "price": 2000, "photo_url": photos['Шашлыки']},
        {"category": "Шашлыки", "name": "Люля-кебаб из баранины", "price": 1600, "photo_url": photos['Шашлыки']},
        {"category": "Шашлыки", "name": "Крылышки куриные", "price": 1200, "photo_url": photos['Шашлыки']},
        
        # Горячие блюда
        {"category": "Горячие блюда", "name": "Стейк из свинины", "price": 1800, "photo_url": photos['Горячие блюда']},
        {"category": "Горячие блюда", "name": "Стейк из говядины", "price": 2200, "photo_url": photos['Горячие блюда']},
        {"category": "Горячие блюда", "name": "Куриное филе", "price": 1300, "photo_url": photos['Горячие блюда']},
        {"category": "Горячие блюда", "name": "Рыба на гриле", "price": 1600, "photo_url": photos['Горячие блюда']},
        {"category": "Горячие блюда", "name": "Картофель фри", "price": 400, "photo_url": photos['Горячие блюда']},
        {"category": "Горячие блюда", "name": "Овощи гриль", "price": 600, "photo_url": photos['Горячие блюда']},
        
        # Гарниры
        {"category": "Гарниры", "name": "Картофель по-деревенски", "price": 400, "photo_url": photos['Гарниры']},
        {"category": "Гарниры", "name": "Рис отварной", "price": 300, "photo_url": photos['Гарниры']},
        {"category": "Гарниры", "name": "Пюре картофельное", "price": 300, "photo_url": photos['Гарниры']},
        {"category": "Гарниры", "name": "Гречка", "price": 300, "photo_url": photos['Гарниры']},
        
        # Десерты
        {"category": "Десерты", "name": "Чизкейк", "price": 600, "photo_url": photos['Десерты']},
        {"category": "Десерты", "name": "Тирамису", "price": 700, "photo_url": photos['Десерты'], "badges": "new"},
        {"category": "Десерты", "name": "Наполеон", "price": 500, "photo_url": photos['Десерты']},
        {"category": "Десерты", "name": "Мороженое", "price": 400, "photo_url": photos['Десерты']},
        
        # Напитки
        {"category": "Напитки", "name": "Чай черный/зеленый", "price": 200, "photo_url": photos['Напитки']},
        {"category": "Напитки", "name": "Кофе американо", "price": 300, "photo_url": photos['Напитки']},
        {"category": "Напитки", "name": "Кофе капучино", "price": 400, "photo_url": photos['Напитки']},
        {"category": "Напитки", "name": "Сок", "price": 300, "photo_url": photos['Напитки']},
        {"category": "Напитки", "name": "Вода минеральная", "price": 200, "photo_url": photos['Напитки']},
        {"category": "Напитки", "name": "Лимонад", "price": 300, "photo_url": photos['Напитки']},
    ]
    
    added = 0
    for item in menu_items:
        try:
            db.add_menu_item(
                restaurant_id=restaurant_id,
                name=item['name'],
                category=item['category'],
                price=item['price'],
                photo_url=item.get('photo_url'),
                badges=item.get('badges')
            )
            added += 1
        except Exception as e:
            logger.error(f"❌ Ошибка при добавлении {item['name']}: {e}")
    
    logger.info(f"   📋 Добавлено {added} блюд в меню")


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
            "phone": None,
            "has_menu": True  # Для этого ресторана добавим полное меню
        },
        {
            "name": "Итальянская кухня",
            "description": "Пицца, паста, ризотто",
            "emoji": "🍝",
            "address": None,
            "phone": None,
            "has_menu": False
        },
        {
            "name": "Бургерная",
            "description": "Сочные бургеры и картофель фри",
            "emoji": "🍔",
            "address": None,
            "phone": None,
            "has_menu": False
        },
        {
            "name": "Суши бар",
            "description": "Роллы, суши, сашими",
            "emoji": "🍣",
            "address": None,
            "phone": None,
            "has_menu": False
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
            
            # Добавляем меню для Ани
            if rest.get("has_menu"):
                seed_ani_menu(db, rest_id)
            
            added_count += 1
        except Exception as e:
            logger.error(f"❌ Ошибка при добавлении {rest['name']}: {e}")
    
    logger.info(f"🎉 Добавлено {added_count} ресторан(ов)!")

if __name__ == "__main__":
    # Для тестирования
    logging.basicConfig(level=logging.INFO)
    seed_restaurants()

