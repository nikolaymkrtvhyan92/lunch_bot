"""
Автоматическое добавление базовых данных при старте бота
"""
import logging
from database import Database

logger = logging.getLogger(__name__)

def seed_ani_menu(db, restaurant_id):
    """Добавить меню для ресторана Ани (с реальными фото блюд)"""
    
    # Качественные фото армянской и кавказской кухни
    photos = {
        # Холодные закуски - армянские традиционные блюда
        'Ассорти мясное': 'https://images.pexels.com/photos/1639562/pexels-photo-1639562.jpeg?auto=compress&w=800',
        'Ассорти рыбное': 'https://images.pexels.com/photos/262959/pexels-photo-262959.jpeg?auto=compress&w=800',
        'Долма': 'https://images.pexels.com/photos/6275169/pexels-photo-6275169.jpeg?auto=compress&w=800',
        'Язык отварной': 'https://images.pexels.com/photos/1640772/pexels-photo-1640772.jpeg?auto=compress&w=800',
        'Овощи свежие': 'https://images.pexels.com/photos/1300972/pexels-photo-1300972.jpeg?auto=compress&w=800',
        'Сыр-тесто-зелень': 'https://images.pexels.com/photos/821365/pexels-photo-821365.jpeg?auto=compress&w=800',
        
        # Горячие закуски - грузинская/армянская кухня
        'Хинкали (5 шт)': 'https://images.pexels.com/photos/5175524/pexels-photo-5175524.jpeg?auto=compress&w=800',
        'Хачапури по-аджарски': 'https://images.pexels.com/photos/4394298/pexels-photo-4394298.jpeg?auto=compress&w=800',
        'Хачапури по-мегрельски': 'https://images.pexels.com/photos/4518586/pexels-photo-4518586.jpeg?auto=compress&w=800',
        'Люля-кебаб': 'https://images.pexels.com/photos/3186654/pexels-photo-3186654.jpeg?auto=compress&w=800',
        
        # Салаты
        'Греческий салат': 'https://images.pexels.com/photos/1059905/pexels-photo-1059905.jpeg?auto=compress&w=800',
        'Цезарь с курицей': 'https://images.pexels.com/photos/2702674/pexels-photo-2702674.jpeg?auto=compress&w=800',
        'Цезарь с креветками': 'https://images.pexels.com/photos/262047/pexels-photo-262047.jpeg?auto=compress&w=800',
        'Оливье': 'https://images.pexels.com/photos/3026808/pexels-photo-3026808.jpeg?auto=compress&w=800',
        'Крабовый салат': 'https://images.pexels.com/photos/1833349/pexels-photo-1833349.jpeg?auto=compress&w=800',
        'Винегрет': 'https://images.pexels.com/photos/1640777/pexels-photo-1640777.jpeg?auto=compress&w=800',
        
        # Супы - традиционные кавказские
        'Харчо': 'https://images.pexels.com/photos/539451/pexels-photo-539451.jpeg?auto=compress&w=800',
        'Бульон куриный': 'https://images.pexels.com/photos/1640775/pexels-photo-1640775.jpeg?auto=compress&w=800',
        'Суп-лапша': 'https://images.pexels.com/photos/1703272/pexels-photo-1703272.jpeg?auto=compress&w=800',
        'Окрошка': 'https://images.pexels.com/photos/8478104/pexels-photo-8478104.jpeg?auto=compress&w=800',
        
        # Шашлыки - кавказская традиция
        'Шашлык из свинины': 'https://images.pexels.com/photos/8697347/pexels-photo-8697347.jpeg?auto=compress&w=800',
        'Шашлык из курицы': 'https://images.pexels.com/photos/8697427/pexels-photo-8697427.jpeg?auto=compress&w=800',
        'Шашлык из баранины': 'https://images.pexels.com/photos/5175519/pexels-photo-5175519.jpeg?auto=compress&w=800',
        'Шашлык из говядины': 'https://images.pexels.com/photos/3186654/pexels-photo-3186654.jpeg?auto=compress&w=800',
        'Люля-кебаб из баранины': 'https://images.pexels.com/photos/5175521/pexels-photo-5175521.jpeg?auto=compress&w=800',
        'Крылышки куриные': 'https://images.pexels.com/photos/60616/fried-chicken-chicken-fried-crunchy-60616.jpeg?auto=compress&w=800',
        
        # Горячие блюда
        'Стейк из свинины': 'https://images.pexels.com/photos/769289/pexels-photo-769289.jpeg?auto=compress&w=800',
        'Стейк из говядины': 'https://images.pexels.com/photos/1639557/pexels-photo-1639557.jpeg?auto=compress&w=800',
        'Куриное филе': 'https://images.pexels.com/photos/2338407/pexels-photo-2338407.jpeg?auto=compress&w=800',
        'Рыба на гриле': 'https://images.pexels.com/photos/725997/pexels-photo-725997.jpeg?auto=compress&w=800',
        'Картофель фри': 'https://images.pexels.com/photos/1893556/pexels-photo-1893556.jpeg?auto=compress&w=800',
        'Овощи гриль': 'https://images.pexels.com/photos/1640770/pexels-photo-1640770.jpeg?auto=compress&w=800',
        
        # Гарниры
        'Картофель по-деревенски': 'https://images.pexels.com/photos/2802527/pexels-photo-2802527.jpeg?auto=compress&w=800',
        'Рис отварной': 'https://images.pexels.com/photos/803963/pexels-photo-803963.jpeg?auto=compress&w=800',
        'Пюре картофельное': 'https://images.pexels.com/photos/5949888/pexels-photo-5949888.jpeg?auto=compress&w=800',
        'Гречка': 'https://images.pexels.com/photos/3338497/pexels-photo-3338497.jpeg?auto=compress&w=800',
        
        # Десерты
        'Чизкейк': 'https://images.pexels.com/photos/273773/pexels-photo-273773.jpeg?auto=compress&w=800',
        'Тирамису': 'https://images.pexels.com/photos/4109998/pexels-photo-4109998.jpeg?auto=compress&w=800',
        'Наполеон': 'https://images.pexels.com/photos/1055270/pexels-photo-1055270.jpeg?auto=compress&w=800',
        'Мороженое': 'https://images.pexels.com/photos/1352278/pexels-photo-1352278.jpeg?auto=compress&w=800',
        
        # Напитки
        'Чай черный/зеленый': 'https://images.pexels.com/photos/230477/pexels-photo-230477.jpeg?auto=compress&w=800',
        'Кофе американо': 'https://images.pexels.com/photos/312418/pexels-photo-312418.jpeg?auto=compress&w=800',
        'Кофе капучино': 'https://images.pexels.com/photos/302899/pexels-photo-302899.jpeg?auto=compress&w=800',
        'Сок': 'https://images.pexels.com/photos/96974/pexels-photo-96974.jpeg?auto=compress&w=800',
        'Вода минеральная': 'https://images.pexels.com/photos/327090/pexels-photo-327090.jpeg?auto=compress&w=800',
        'Лимонад': 'https://images.pexels.com/photos/1233319/pexels-photo-1233319.jpeg?auto=compress&w=800',
    }
    
    menu_items = [
        # Холодные закуски
        {"category": "Холодные закуски", "name": "Ассорти мясное", "price": 2900, "photo_url": photos['Ассорти мясное']},
        {"category": "Холодные закуски", "name": "Ассорти рыбное", "price": 2900, "photo_url": photos['Ассорти рыбное']},
        {"category": "Холодные закуски", "name": "Долма", "price": 1800, "photo_url": photos['Долма'], "badges": "new"},
        {"category": "Холодные закуски", "name": "Язык отварной", "price": 1800, "photo_url": photos['Язык отварной']},
        {"category": "Холодные закуски", "name": "Овощи свежие", "price": 900, "photo_url": photos['Овощи свежие']},
        {"category": "Холодные закуски", "name": "Сыр-тесто-зелень", "price": 800, "photo_url": photos['Сыр-тесто-зелень']},
        
        # Горячие закуски
        {"category": "Горячие закуски", "name": "Хинкали (5 шт)", "price": 700, "photo_url": photos['Хинкали (5 шт)'], "badges": "hit"},
        {"category": "Горячие закуски", "name": "Хачапури по-аджарски", "price": 1200, "photo_url": photos['Хачапури по-аджарски'], "badges": "new,hit"},
        {"category": "Горячие закуски", "name": "Хачапури по-мегрельски", "price": 1000, "photo_url": photos['Хачапури по-мегрельски']},
        {"category": "Горячие закуски", "name": "Люля-кебаб", "price": 600, "photo_url": photos['Люля-кебаб']},
        
        # Салаты
        {"category": "Салаты", "name": "Греческий салат", "price": 800, "photo_url": photos['Греческий салат'], "badges": "hit"},
        {"category": "Салаты", "name": "Цезарь с курицей", "price": 900, "photo_url": photos['Цезарь с курицей']},
        {"category": "Салаты", "name": "Цезарь с креветками", "price": 1200, "photo_url": photos['Цезарь с креветками']},
        {"category": "Салаты", "name": "Оливье", "price": 600, "photo_url": photos['Оливье']},
        {"category": "Салаты", "name": "Крабовый салат", "price": 700, "photo_url": photos['Крабовый салат']},
        {"category": "Салаты", "name": "Винегрет", "price": 500, "photo_url": photos['Винегрет']},
        
        # Супы
        {"category": "Супы", "name": "Харчо", "price": 600, "photo_url": photos['Харчо'], "badges": "spicy,hit"},
        {"category": "Супы", "name": "Бульон куриный", "price": 400, "photo_url": photos['Бульон куриный']},
        {"category": "Супы", "name": "Суп-лапша", "price": 500, "photo_url": photos['Суп-лапша']},
        {"category": "Супы", "name": "Окрошка", "price": 600, "photo_url": photos['Окрошка']},
        
        # Шашлыки
        {"category": "Шашлыки", "name": "Шашлык из свинины", "price": 1800, "photo_url": photos['Шашлык из свинины']},
        {"category": "Шашлыки", "name": "Шашлык из курицы", "price": 1500, "photo_url": photos['Шашлык из курицы']},
        {"category": "Шашлыки", "name": "Шашлык из баранины", "price": 2200, "photo_url": photos['Шашлык из баранины']},
        {"category": "Шашлыки", "name": "Шашлык из говядины", "price": 2000, "photo_url": photos['Шашлык из говядины']},
        {"category": "Шашлыки", "name": "Люля-кебаб из баранины", "price": 1600, "photo_url": photos['Люля-кебаб из баранины']},
        {"category": "Шашлыки", "name": "Крылышки куриные", "price": 1200, "photo_url": photos['Крылышки куриные']},
        
        # Горячие блюда
        {"category": "Горячие блюда", "name": "Стейк из свинины", "price": 1800, "photo_url": photos['Стейк из свинины']},
        {"category": "Горячие блюда", "name": "Стейк из говядины", "price": 2200, "photo_url": photos['Стейк из говядины']},
        {"category": "Горячие блюда", "name": "Куриное филе", "price": 1300, "photo_url": photos['Куриное филе']},
        {"category": "Горячие блюда", "name": "Рыба на гриле", "price": 1600, "photo_url": photos['Рыба на гриле']},
        {"category": "Горячие блюда", "name": "Картофель фри", "price": 400, "photo_url": photos['Картофель фри']},
        {"category": "Горячие блюда", "name": "Овощи гриль", "price": 600, "photo_url": photos['Овощи гриль']},
        
        # Гарниры
        {"category": "Гарниры", "name": "Картофель по-деревенски", "price": 400, "photo_url": photos['Картофель по-деревенски']},
        {"category": "Гарниры", "name": "Рис отварной", "price": 300, "photo_url": photos['Рис отварной']},
        {"category": "Гарниры", "name": "Пюре картофельное", "price": 300, "photo_url": photos['Пюре картофельное']},
        {"category": "Гарниры", "name": "Гречка", "price": 300, "photo_url": photos['Гречка']},
        
        # Десерты
        {"category": "Десерты", "name": "Чизкейк", "price": 600, "photo_url": photos['Чизкейк']},
        {"category": "Десерты", "name": "Тирамису", "price": 700, "photo_url": photos['Тирамису'], "badges": "new"},
        {"category": "Десерты", "name": "Наполеон", "price": 500, "photo_url": photos['Наполеон']},
        {"category": "Десерты", "name": "Мороженое", "price": 400, "photo_url": photos['Мороженое']},
        
        # Напитки
        {"category": "Напитки", "name": "Чай черный/зеленый", "price": 200, "photo_url": photos['Чай черный/зеленый']},
        {"category": "Напитки", "name": "Кофе американо", "price": 300, "photo_url": photos['Кофе американо']},
        {"category": "Напитки", "name": "Кофе капучино", "price": 400, "photo_url": photos['Кофе капучино']},
        {"category": "Напитки", "name": "Сок", "price": 300, "photo_url": photos['Сок']},
        {"category": "Напитки", "name": "Вода минеральная", "price": 200, "photo_url": photos['Вода минеральная']},
        {"category": "Напитки", "name": "Лимонад", "price": 300, "photo_url": photos['Лимонад']},
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

